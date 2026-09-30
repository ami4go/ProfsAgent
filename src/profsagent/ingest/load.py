import os
import json
import glob
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_ENRICHED_DIR = BASE_DIR / "data" / "enriched"
DATA_CANONICAL_DIR = BASE_DIR / "data" / "canonical"

class KGBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_db(self):
        print("Clearing existing database...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

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
                    
                # Create Course Node
                session.run(
                    """
                    MERGE (c:Course {code: $code})
                    SET c.name = $name,
                        c.credits = $credits,
                        c.description = $description
                    """,
                    code=course_code,
                    name=header.get("name", ""),
                    credits=str(header.get("credits", "")),
                    description=header.get("description", "")
                )
                
                # Create Prerequisites
                prereqs = header.get("prerequisites_mandatory_resolved", [])
                for prereq_code in prereqs:
                    session.run(
                        """
                        MERGE (c1:Course {code: $course_code})
                        MERGE (c2:Course {code: $prereq_code})
                        MERGE (c1)-[:REQUIRES]->(c2)
                        """,
                        course_code=course_code,
                        prereq_code=prereq_code
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
    load_dotenv(BASE_DIR / ".env")
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "neo4j") # Default test password
    
    print(f"Connecting to Neo4j at {uri}...")
    try:
        builder = KGBuilder(uri, user, password)
        # builder.clear_db() # Optional: Un-comment to wipe the DB first
        builder.build_graph()
        builder.close()
        print("Success! Graph construction is complete.")
    except Exception as e:
        print(f"\nERROR connecting to Neo4j: {e}")
        print("Make sure Neo4j Desktop or Docker is running locally!")

if __name__ == "__main__":
    main()
