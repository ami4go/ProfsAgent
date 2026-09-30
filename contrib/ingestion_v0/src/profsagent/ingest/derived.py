"""
Derived Graph Relationships for ProfsAgent (Layer A).

Computes:
1. Topic Precedence (temporal sequence of topics across weeks and prerequisites)
2. Course Overlap & Similarity (Jaccard similarity on canonical topics)
3. Derived Cypher edge generators
"""

from typing import Any
from neo4j import Driver
from profsagent.config import settings
from profsagent.ingest.canonicalize import TopicCanonicalizer
from profsagent.models.schema import ParsedCourse


class DerivedRelationshipEngine:
    """Calculates higher-order topological relationships between course graph entities."""

    def __init__(self, canonicalizer: TopicCanonicalizer | None = None) -> None:
        self.canonicalizer = canonicalizer or TopicCanonicalizer()

    def compute_course_topics(self, course: ParsedCourse) -> set[str]:
        """Extracts unique canonical topics covered across all weeks of a course."""
        topics = set()
        for w in course.weekly_plans:
            # Canonicalize summary and subtopics
            summary_match = self.canonicalizer.canonicalize(w.topic_summary)
            topics.add(summary_match.canonical_topic)
            for sub in w.subtopics:
                sub_match = self.canonicalizer.canonicalize(sub)
                topics.add(sub_match.canonical_topic)
        return topics

    def compute_pairwise_course_overlaps(
        self,
        courses: list[ParsedCourse],
        threshold: float = 0.15,
    ) -> list[dict[str, Any]]:
        """Computes Jaccard topic similarity between all pairs of courses."""
        course_topic_map = {
            c.header.course_code: self.compute_course_topics(c)
            for c in courses if not c.is_gold_set
        }

        overlaps: list[dict[str, Any]] = []
        codes = list(course_topic_map.keys())

        for i in range(len(codes)):
            for j in range(i + 1, len(codes)):
                c1, c2 = codes[i], codes[j]
                t1, t2 = course_topic_map[c1], course_topic_map[c2]

                if not t1 or not t2:
                    continue

                common = t1 & t2
                union = t1 | t2
                jaccard = len(common) / len(union) if union else 0.0

                if jaccard >= threshold:
                    overlaps.append({
                        "course1": c1,
                        "course2": c2,
                        "jaccard_similarity": round(jaccard, 3),
                        "common_topics": sorted(list(common)),
                    })

        return overlaps

    def compute_intra_course_topic_precedence(
        self,
        course: ParsedCourse,
    ) -> list[tuple[str, str, int, int]]:
        """
        Derives topic precedence pairs (TopicA PRECEDES TopicB) based on weekly order.
        Returns: list of (topic_a, topic_b, week_a, week_b)
        """
        precedence_pairs = []
        week_topics = []

        for w in sorted(course.weekly_plans, key=lambda x: x.week_number):
            match = self.canonicalizer.canonicalize(w.topic_summary)
            week_topics.append((w.week_number, match.canonical_topic))

        for i in range(len(week_topics)):
            w_i, t_i = week_topics[i]
            for j in range(i + 1, len(week_topics)):
                w_j, t_j = week_topics[j]
                if t_i != t_j:
                    precedence_pairs.append((t_i, t_j, w_i, w_j))

        return precedence_pairs

    def sync_derived_edges_to_neo4j(
        self,
        driver: Driver,
        courses: list[ParsedCourse],
    ) -> dict[str, int]:
        """Applies derived OVERLAPS_WITH and PRECEDES edges directly to Neo4j."""
        overlaps = self.compute_pairwise_course_overlaps(courses)
        overlap_count = 0
        precedence_count = 0

        with driver.session(database=settings.NEO4J_DATABASE) as session:
            # 1. Sync OVERLAPS_WITH edges
            for ov in overlaps:
                session.run(
                    """
                    MATCH (c1:Course {course_code: $c1})
                    MATCH (c2:Course {course_code: $c2})
                    MERGE (c1)-[r:OVERLAPS_WITH]->(c2)
                    SET r.jaccard_similarity = $sim,
                        r.common_topics = $topics
                    """,
                    c1=ov["course1"],
                    c2=ov["course2"],
                    sim=ov["jaccard_similarity"],
                    topics=ov["common_topics"],
                )
                overlap_count += 1

            # 2. Sync TOPIC PRECEDES edges
            for c in courses:
                if c.is_gold_set:
                    continue
                pairs = self.compute_intra_course_topic_precedence(c)
                for t1, t2, w1, w2 in pairs:
                    session.run(
                        """
                        MERGE (top1:Topic {canonical_name: $t1})
                        MERGE (top2:Topic {canonical_name: $t2})
                        MERGE (top1)-[p:PRECEDES]->(top2)
                        ON CREATE SET p.evidence_courses = [$course_code]
                        ON MATCH SET p.evidence_courses = CASE
                            WHEN $course_code IN p.evidence_courses THEN p.evidence_courses
                            ELSE p.evidence_courses + $course_code
                        END
                        """,
                        t1=t1,
                        t2=t2,
                        course_code=c.header.course_code,
                    )
                    precedence_count += 1

        return {
            "overlaps_created": overlap_count,
            "precedence_created": precedence_count,
        }
