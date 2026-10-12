import os
import re
import sys
import json
import glob
import hashlib
import argparse
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_ENRICHED_DIR = BASE_DIR / "data" / "enriched"
DATA_CANONICAL_DIR = BASE_DIR / "data" / "canonical"

# One uniqueness constraint per node key: keeps MERGE from creating duplicates and makes lookups fast
CONSTRAINTS = [
    ("Course", "code"), ("CourseOutcome", "id"), ("WeekPlan", "id"), ("Topic", "id"),
    ("AssessmentComponent", "id"), ("Resource", "id"),
]

def resource_id(title):
    """Shared id for a textbook/reference title, so courses citing the same book share one node."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return "R:hash:" + hashlib.sha1(slug.encode("utf-8")).hexdigest()[:16] if slug else None

def course_credits(header):
    """TechTree's credits when listed, else the number on the sheet."""
    credits = (header.get("catalogue") or {}).get("credits")
    if credits is None:
        match = re.search(r"\d+", str(header.get("credits") or ""))
        credits = int(match.group()) if match else None
    return credits

class KGBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_db(self):
        print("Clearing existing database...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def create_constraints(self):
        with self.driver.session() as session:
            for label, prop in CONSTRAINTS:
                session.run(f"CREATE CONSTRAINT {label.lower()}_{prop} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE")

    def build_graph(self):
        # 1. Load Topic Mapping
        topic_mapping_path = DATA_CANONICAL_DIR / "topic_mapping.json"
        if not topic_mapping_path.exists():
            print(f"ERROR: Cannot find {topic_mapping_path}")
            return
            
        with open(topic_mapping_path, "r", encoding="utf-8") as f:
            topic_mapping = json.load(f)
            
        # Create Canonical Topic Nodes First
        print("Creating Canonical Topic nodes...")
        unique_canonical = {}
        for raw, mapping in topic_mapping.items():
            cid = mapping["canonical_id"]
            if cid not in unique_canonical:
                unique_canonical[cid] = mapping["canonical_name"]
                
        with self.driver.session() as session:
            for cid, cname in unique_canonical.items():
                session.run(
                    "MERGE (t:Topic {id: $id}) "
                    "SET t.name = $name",
                    id=cid, name=cname
                )
        
        # 2. Load Courses
        enriched_files = glob.glob(str(DATA_ENRICHED_DIR / "*.json"))
        print(f"Loading {len(enriched_files)} enriched courses into Neo4j...")
        
        with self.driver.session() as session:
            for ef in enriched_files:
                with open(ef, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                header = data.get("header", {})
                course_code = header.get("course_code")
                if not course_code:
                    continue
                    
                # Create Course Node (catalogue details come from TechTree via enrich.py)
                catalogue = header.get("catalogue") or {}
                session.run(
                    """
                    MERGE (c:Course {code: $code})
                    SET c.name = $name,
                        c.aliases = $aliases,
                        c.credits = $credits,
                        c.level = $level,
                        c.semester = $semester,
                        c.cluster = $cluster,
                        c.department = $department,
                        c.offered_to = $offered_to,
                        c.catalogue_url = $catalogue_url,
                        c.description = $description
                    """,
                    code=course_code,
                    aliases=header.get("aliases") or [],
                    name=header.get("name", ""),
                    credits=course_credits(header),
                    level=header.get("level"),
                    semester=catalogue.get("semester"),
                    cluster=catalogue.get("cluster"),
                    department=header.get("department"),
                    offered_to=header.get("offered_to") or [],
                    catalogue_url=catalogue.get("catalogue_url"),
                    description=header.get("description", "")
                )

                # Create Prerequisites (merged from the sheet and TechTree; kind = mandatory | desirable)
                for link in header.get("prerequisite_links", []):
                    session.run(
                        """
                        MERGE (c1:Course {code: $course_code})
                        MERGE (c2:Course {code: $prereq_code})
                        MERGE (c1)-[r:REQUIRES]->(c2)
                        SET r.kind = $kind,
                            r.sources = $sources
                        """,
                        course_code=course_code,
                        prereq_code=link["code"],
                        kind=link["kind"],
                        sources=link["sources"]
                    )

                # Create Anti-requisites (from TechTree)
                for anti_code in header.get("anti_requisites_resolved", []):
                    session.run(
                        """
                        MERGE (c1:Course {code: $course_code})
                        MERGE (c2:Course {code: $anti_code})
                        MERGE (c1)-[:ANTI_REQUISITE]->(c2)
                        """,
                        course_code=course_code,
                        anti_code=anti_code
                    )

                # Create Resources (one node per distinct title, shared by every course that cites it)
                for resource in data.get("resources", []):
                    title = " ".join(str(resource.get("title") or "").split())
                    r_id = resource_id(title)
                    if not r_id:
                        continue
                    session.run(
                        """
                        MERGE (c:Course {code: $course_code})
                        MERGE (r:Resource {id: $r_id})
                        ON CREATE SET r.title = $title
                        MERGE (c)-[u:USES_RESOURCE]->(r)
                        SET u.type = $type
                        """,
                        course_code=course_code,
                        r_id=r_id,
                        title=title,
                        type=resource.get("type_label")
                    )

                # Create Course Outcomes (COs)
                outcomes = data.get("outcomes", [])
                for co in outcomes:
                    co_id = f"{course_code}_{co['label']}"
                    session.run(
                        """
                        MERGE (c:Course {code: $course_code})
                        MERGE (co:CourseOutcome {id: $co_id})
                        SET co.label = $label,
                            co.text = $text,
                            co.bloom_level = $bloom_level,
                            co.bloom_verb = $bloom_verb
                        MERGE (c)-[:HAS_CO]->(co)
                        """,
                        course_code=course_code,
                        co_id=co_id,
                        label=co["label"],
                        text=co["raw_text"],
                        bloom_level=co.get("bloom_level", ""),
                        bloom_verb=co.get("bloom_verb", "")
                    )
                    
                # Create Assessment Components (type is the standard type set by enrich.py)
                for order, component in enumerate(data.get("assessments", []), start=1):
                    session.run(
                        """
                        MERGE (c:Course {code: $course_code})
                        MERGE (a:AssessmentComponent {id: $a_id})
                        SET a.name = $name,
                            a.type = $type,
                            a.weight_pct = $weight_pct,
                            a.order = $order
                        MERGE (c)-[:HAS_ASSESSMENT]->(a)
                        """,
                        course_code=course_code,
                        a_id=f"{course_code}_A{order}",
                        name=component.get("type_label", ""),
                        type=component.get("type", "other"),
                        weight_pct=component.get("weight_pct"),
                        order=order
                    )

                # Create Weekly Plan & Map Topics
                weekly_plan = data.get("weekly_plan", [])
                for week in weekly_plan:
                    week_num = week.get("week")
                    week_id = f"{course_code}_W{week_num}"
                    
                    session.run(
                        """
                        MERGE (c:Course {code: $course_code})
                        MERGE (w:WeekPlan {id: $week_id})
                        SET w.week_number = $week_num
                        MERGE (c)-[:HAS_WEEK]->(w)
                        """,
                        course_code=course_code,
                        week_id=week_id,
                        week_num=week_num
                    )
                    
                    # Link Week -> Topics
                    for raw_topic in week.get("lecture_topics", []):
                        clean_topic = str(raw_topic).strip()
                        if clean_topic in topic_mapping:
                            canonical_id = topic_mapping[clean_topic]["canonical_id"]
                            session.run(
                                """
                                MERGE (w:WeekPlan {id: $week_id})
                                MERGE (t:Topic {id: $canonical_id})
                                MERGE (w)-[:COVERS {raw_text: $raw_topic}]->(t)
                                """,
                                week_id=week_id,
                                canonical_id=canonical_id,
                                raw_topic=raw_topic
                            )
                            
                    # Link Week -> COs
                    for co_label in week.get("cos_met", []):
                        co_id = f"{course_code}_{co_label}"
                        session.run(
                            """
                            MERGE (w:WeekPlan {id: $week_id})
                            MERGE (co:CourseOutcome {id: $co_id})
                            MERGE (w)-[:MEETS]->(co)
                            """,
                            week_id=week_id,
                            co_id=co_id
                        )

def main():
    parser = argparse.ArgumentParser(description="Load data/enriched + data/canonical into Neo4j.")
    parser.add_argument("--wipe", action="store_true", help="delete everything in the database before loading")
    args = parser.parse_args()

    load_dotenv(BASE_DIR / ".env")
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "neo4j") # Default test password

    print(f"Connecting to Neo4j at {uri}...")
    try:
        builder = KGBuilder(uri, user, password)
        if args.wipe:
            builder.clear_db()
        builder.create_constraints()
        builder.build_graph()
        builder.close()
        print("Success! Graph construction is complete.")
    except Exception as e:
        print(f"\nERROR connecting to Neo4j: {e}")
        print("Make sure Neo4j Desktop or Docker is running locally!")
        sys.exit(1)

if __name__ == "__main__":
    main()
