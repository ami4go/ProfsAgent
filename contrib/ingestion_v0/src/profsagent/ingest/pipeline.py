"""
Master Ingestion Pipeline for ProfsAgent (Layer A).

Orchestrates:
1. Programme and PO/PEO loading
2. Raw course sheet discovery and deterministic segmentation
3. E1-E4 extraction and Pydantic validation
4. Cognitive enrichment (Bloom's taxonomy + BCD quality scoring)
5. Topic canonicalization against CS2023 backbone
6. Deterministic validation (V1-V24)
7. Neo4j graph loading & derived relationships
8. priors.json computation and export
"""

import json
from pathlib import Path
from typing import Any
from rich.console import Console
from rich.table import Table

from profsagent.config import settings
from profsagent.ingest.canonicalize import TopicCanonicalizer
from profsagent.ingest.derived import DerivedRelationshipEngine
from profsagent.ingest.enrichment import BloomEnricher, CourseOutcomeQualityScorer
from profsagent.ingest.neo4j_loader import Neo4jGraphLoader
from profsagent.ingest.priors import compute_institutional_priors, save_priors_json
from profsagent.ingest.programmes import load_programme_spec, ingest_programme_to_neo4j
from profsagent.llm.extractors import CourseSheetExtractors
from profsagent.models.schema import ParsedCourse, ValidationReport
from profsagent.validate.deterministic import DeterministicValidator

console = Console()

# Official held-out evaluation courses (isolated from Layer A retrieval)
HELD_OUT_COURSE_CODES = {"CSE600", "CSE601"}


class LayerAIngestionPipeline:
    """End-to-end institutional Knowledge Graph ingestion pipeline."""

    def __init__(
        self,
        raw_dir: Path | None = None,
        output_dir: Path | None = None,
        held_out_codes: set[str] | None = None,
    ) -> None:
        self.raw_dir = raw_dir or settings.RAW_SHEETS_DIR
        self.output_dir = output_dir or settings.PARSED_SHEETS_DIR
        self.held_out_codes = held_out_codes or HELD_OUT_COURSE_CODES

        self.extractors = CourseSheetExtractors()
        self.enricher = BloomEnricher()
        self.quality_scorer = CourseOutcomeQualityScorer(self.enricher)
        self.canonicalizer = TopicCanonicalizer()
        self.validator = DeterministicValidator(self.enricher)
        self.derived_engine = DerivedRelationshipEngine(self.canonicalizer)
        self.loader = Neo4jGraphLoader()

    def process_sheet_text(self, text: str, source_path: Path) -> tuple[ParsedCourse, ValidationReport]:
        """Processes a single raw course sheet through the entire pipeline."""
        # Check if held-out
        is_gold = any(code in source_path.name for code in self.held_out_codes)

        # 1. E1-E4 Extraction
        course = self.extractors.extract_full_course(text, is_gold_set=is_gold)

        # 2. Cognitive Enrichment on Course Outcomes
        for co in course.course_outcomes:
            self.quality_scorer.enrich_course_outcome(co)

        # 3. Canonicalize weekly topics
        for w in course.weekly_plans:
            canon = self.canonicalizer.canonicalize(w.topic_summary)
            # Annotate with canonical topic
            w.reading_references.append(f"Canonical Topic: {canon.canonical_topic} [{canon.category}]")

        # 4. Independent Deterministic Validation
        report = self.validator.validate_course(course, held_out_codes=self.held_out_codes)

        return course, report

    def run(self, connect_neo4j: bool = True) -> dict[str, Any]:
        """Executes batch ingestion over all course sheets in data/raw_sheets/."""
        console.rule("[bold blue]Starting ProfsAgent Layer A Ingestion[/bold blue]")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        parsed_courses: list[ParsedCourse] = []
        validation_reports: list[ValidationReport] = []

        # 1. Ingest Programme Regulations and POs to Neo4j if available
        neo4j_online = False
        if connect_neo4j:
            try:
                driver = self.loader.get_driver()
                self.loader.init_schema()
                prog_data = load_programme_spec()
                prog_counts = ingest_programme_to_neo4j(driver, prog_data)
                console.print(f"[green]✓[/green] Connected to Neo4j. Ingested Programme POs: {prog_counts}")
                neo4j_online = True
            except Exception as e:
                console.print(f"[yellow]![/yellow] Neo4j unavailable ({e}). Continuing with disk serialization.")

        # 2. Discover and parse course sheets
        sheet_files = list(self.raw_dir.glob("*.txt"))
        console.print(f"Found {len(sheet_files)} course sheets in {self.raw_dir}")

        for file_path in sheet_files:
            text = file_path.read_text(encoding="utf-8")
            course, report = self.process_sheet_text(text, file_path)

            parsed_courses.append(course)
            validation_reports.append(report)

            # Save parsed JSON to data/parsed/
            out_json = self.output_dir / f"{course.header.course_code}.json"
            out_json.write_text(course.model_dump_json(indent=2), encoding="utf-8")

            # Load into Neo4j if online
            if neo4j_online and not course.is_gold_set:
                self.loader.load_parsed_course(course)

        # 3. Compute derived relationships across courses
        active_courses = [c for c in parsed_courses if not c.is_gold_set]
        overlaps = self.derived_engine.compute_pairwise_course_overlaps(active_courses)
        console.print(f"[green]✓[/green] Computed {len(overlaps)} pairwise course overlap connections")

        if neo4j_online:
            derived_stats = self.derived_engine.sync_derived_edges_to_neo4j(self.loader.get_driver(), active_courses)
            console.print(f"[green]✓[/green] Synced derived edges to Neo4j: {derived_stats}")

        # 4. Compute and save empirical priors.json
        priors = compute_institutional_priors(active_courses)
        priors_path = save_priors_json(priors, settings.DATA_DIR / "priors.json")
        console.print(f"[green]✓[/green] Exported updated priors to {priors_path}")

        # Print summary audit table
        self._print_audit_summary(parsed_courses, validation_reports)

        return {
            "courses_processed": len(parsed_courses),
            "valid_courses": sum(1 for r in validation_reports if r.passed),
            "overlaps_found": len(overlaps),
            "neo4j_synced": neo4j_online,
            "priors_file": str(priors_path),
        }

    def _print_audit_summary(self, courses: list[ParsedCourse], reports: list[ValidationReport]) -> None:
        table = Table(title="Layer A Ingestion Audit Summary")
        table.add_column("Course", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("COs", justify="right")
        table.add_column("Weeks", justify="right")
        table.add_column("Assess %", justify="right")
        table.add_column("Status", justify="center")
        table.add_column("Violations / Warnings", style="yellow")

        for c, r in zip(courses, reports, strict=False):
            status_str = "[bold green]PASS[/bold green]" if r.passed else "[bold red]FAIL[/bold red]"
            issues = f"V:{len(r.violations)} | W:{len(r.warnings)}"
            table.add_row(
                c.header.course_code,
                c.header.course_title[:30],
                str(len(c.course_outcomes)),
                str(len(c.weekly_plans)),
                f"{c.total_assessment_weight:.0f}%",
                status_str,
                issues,
            )

        console.print(table)


if __name__ == "__main__":
    pipeline = LayerAIngestionPipeline()
    pipeline.run(connect_neo4j=False)
