"""Audit the Layer A knowledge graph (completeness and consistency). Read-only, no LLM calls.

  python scripts/audit_kg.py                 # data/enriched + topic mapping; writes data/audit/kg_audit.json
  python scripts/audit_kg.py --neo4j         # also compare with what is loaded in Neo4j
  python scripts/audit_kg.py --code KA-WEEK-DUP   # print every finding with that code
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(ROOT / "src"))

from profsagent.kg import audit  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--neo4j", action="store_true", help="also audit the loaded graph")
    ap.add_argument("--code", help="list the findings with this code")
    ap.add_argument("--out", default=str(ROOT / "data" / "audit" / "kg_audit.json"))
    a = ap.parse_args()

    reports = [audit.audit_files()]
    if a.neo4j:
        from dotenv import load_dotenv
        from neo4j import GraphDatabase
        load_dotenv(ROOT / ".env")
        drv = GraphDatabase.driver(os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                                   auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "")))
        try:
            reports.append(audit.audit_neo4j(drv))
        finally:
            drv.close()
    rep = audit.merge_reports(*reports)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
    st, sm = rep["stats"], rep["summary"]
    print(f"courses {st['courses']} (COs {st['with_cos']}, weeks {st['with_weeks']}, topics {st['with_topics']}, "
          f"assessment {st['with_assessment']}) | COs {st['cos']}: Bloom unclassified {st['bloom_unclassified_pct']}%, "
          f"taggers disagree {st['bloom_disagree_pct']}%")
    print(f"topics: {st['raw_topics']} raw -> {st['canonical_topics']} canonical ({st['canonical_singleton_pct']}% singletons, "
          f"{st['canonical_in_2plus_courses']} shared by 2+ courses)")
    if a.neo4j:
        print(f"neo4j: {st['courses_in_graph']} courses, {st['topics_in_graph']} topics")
    print(f"\n{sm['errors']} errors in {sm['courses_with_errors']} courses, {sm['warnings']} warnings\n")
    print(audit.table(rep))
    if a.code:
        print()
        for x in rep["findings"]:
            if x["code"] == a.code:
                print(f"{x['course'] or '-':<10} {x['message']}")
    print(f"\nreport: {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")


if __name__ == "__main__":
    main()
