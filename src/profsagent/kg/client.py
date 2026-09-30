"""KGClient — the contract between the design pipeline (ours) and Layer A (KG teammate).

Everything the design pipeline reads from the institutional graph goes through this interface. The stub
(kg/stub.py) implements it from parsed course sheets; the production implementation will run Cypher against
Neo4j. Every method takes `exclude` (a set of course uids/aliases) so a run can hide its own target course
(e.g. the CSE201 dev run must not see CSE201's sheet).

Return shapes are plain JSON-able dicts so they can be dropped straight into prompt contexts.
"""
from __future__ import annotations

from typing import Protocol


class KGClient(Protocol):
    # --- courses -------------------------------------------------------------------------------------
    def course(self, uid: str, exclude: set[str] = frozenset()) -> dict | None:
        """{uid, aliases, name, level, credits, cluster, semester, description, prereqs:[uid], anti:[uid],
            cos:[{uid,label,text,quality_score,bloom_lexicon,leading_verb}], topics:[str], weeks:[{week,topics,co_refs}],
            assessment:[{type,weight_pct,raw_label}], resources:[{type,title}], catalogue_url}"""

    def index(self, exclude: set[str] = frozenset()) -> list[dict]:
        """Compact rows for every course: {uid, aliases, name, level, credits, cluster}."""

    def search_courses(self, text: str, k: int = 15, exclude: set[str] = frozenset()) -> list[dict]:
        """Hybrid retrieval over course descriptions/COs/weekly topics → [{uid, score, hits:[doc snippets]}]."""

    def topic_overlap(self, new_topics: list[str], uid: str) -> dict:
        """{weighted_jaccard, shared_topics:[str], method} between the new course's topics and course uid."""

    def topic_candidates(self, phrases: list[str], k: int = 5, exclude: set[str] = frozenset()) -> list[dict]:
        """For each phrase, nearest canonical topics: [{phrase, candidates:[{topic_uid, canonical_name, sim, courses}]}]."""

    # --- outcomes ------------------------------------------------------------------------------------
    def programme_pos(self, programme_uid: str) -> list[dict]:
        """[{uid, text, short_label}] verbatim."""

    def exemplar_cos(self, text: str, level: int | None, k: int = 8, exclude: set[str] = frozenset(),
                     min_quality: float = 0.7) -> list[dict]:
        """Quality-filtered corpus COs similar to `text`: [{uid, course, statement, bloom_lexicon, quality_score}]."""

    # --- priors & resources --------------------------------------------------------------------------
    def priors(self, level: int | None = None, exclude: set[str] = frozenset()) -> dict:
        """{co_count:{median,n}, weights:{type:{median,iqr:[lo,hi],n}}, component_count:{median,n}, n_courses}"""

    def corpus_resources(self, uids: list[str]) -> list[dict]:
        """[{resource_uid, title, type, used_by_courses:[uid], verified:false}]"""

    def topic_precedence(self, topic_uids: list[str]) -> list[dict]:
        """[{from, to, support}] among the given canonical topics (may be empty in the stub)."""
