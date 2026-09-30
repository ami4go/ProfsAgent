"""
Programme, PEO, and PO Curator for ProfsAgent.

Loads official institutional curriculum regulations and NBA-accredited
Programme Outcomes (POs) and Programme Educational Objectives (PEOs),
inserting them into Layer A with full provenance.
"""

import json
from pathlib import Path
from typing import Any
from neo4j import Driver
from profsagent.config import settings


def load_programme_spec(file_path: Path | None = None) -> dict[str, Any]:
    """Loads programme definition JSON from disk."""
    path = file_path or (settings.DATA_DIR / "programmes" / "btech_cse.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def ingest_programme_to_neo4j(driver: Driver, prog_data: dict[str, Any]) -> dict[str, int]:
    """Ingests Institution, Programme, PEOs, POs, and PSOs into Neo4j."""
    counts = {"peos": 0, "pos": 0, "psos": 0}

    with driver.session(database=settings.NEO4J_DATABASE) as session:
        # 1. Institution and Programme
        session.run(
            """
            MERGE (inst:Institution {institution_id: $inst_id})
            SET inst.name = $inst_name
            MERGE (prog:Programme {programme_code: $prog_code})
            SET prog.name = $prog_name,
                prog.curriculum_version = $version,
                prog.accreditation = $accreditation
            MERGE (inst)-[:OFFERS_PROGRAMME]->(prog)
            """,
            inst_id=prog_data.get("institution_id", "IIITD"),
            inst_name=prog_data.get("institution_name", "IIIT-Delhi"),
            prog_code=prog_data.get("programme_code", "BTECH_CSE"),
            prog_name=prog_data.get("programme_name", "B.Tech Computer Science and Engineering"),
            version=prog_data.get("curriculum_version", "2024-2028"),
            accreditation=prog_data.get("accreditation", "NBA Tier-1"),
        )

        # 2. Programme Educational Objectives (PEOs)
        for peo in prog_data.get("peos", []):
            session.run(
                """
                MERGE (p:PEO {peo_id: $peo_id})
                SET p.title = $title,
                    p.description = $desc
                WITH p
                MATCH (prog:Programme {programme_code: $prog_code})
                MERGE (prog)-[:HAS_PEO]->(p)
                """,
                peo_id=peo["peo_id"],
                title=peo["title"],
                desc=peo["description"],
                prog_code=prog_data.get("programme_code", "BTECH_CSE"),
            )
            counts["peos"] += 1

        # 3. Programme Outcomes (POs)
        for po in prog_data.get("pos", []):
            session.run(
                """
                MERGE (p:PO {po_id: $po_id})
                SET p.title = $title,
                    p.description = $desc
                WITH p
                MATCH (prog:Programme {programme_code: $prog_code})
                MERGE (prog)-[:HAS_PO]->(p)
                """,
                po_id=po["po_id"],
                title=po["title"],
                desc=po["description"],
                prog_code=prog_data.get("programme_code", "BTECH_CSE"),
            )
            counts["pos"] += 1

        # 4. Programme Specific Outcomes (PSOs)
        for pso in prog_data.get("psos", []):
            session.run(
                """
                MERGE (p:PO {po_id: $pso_id})
                SET p.title = $title,
                    p.description = $desc,
                    p.is_pso = true
                WITH p
                MATCH (prog:Programme {programme_code: $prog_code})
                MERGE (prog)-[:HAS_PSO]->(p)
                """,
                pso_id=pso["pso_id"],
                title=pso["title"],
                desc=pso["description"],
                prog_code=prog_data.get("programme_code", "BTECH_CSE"),
            )
            counts["psos"] += 1

    return counts
