"""Layer A audit: completeness and consistency of the institutional knowledge graph. Read-only, NO LLM.

The graph-backed checks (exemplar COs, level priors, topic links, prerequisites) are only as good as the graph, so the
graph is checked first. Two sources:
- audit_files(): data/enriched/*.json and data/canonical/topic_mapping.json, i.e. what load.py loads;
- audit_neo4j(): what is actually in Neo4j, compared with the files.

Findings use the validator record shape ({code, severity, course, message}). Errors are data that load.py turns into
a wrong graph (a week naming a CO that does not exist becomes an empty CourseOutcome node; two COs with the same label
merge into one node; a lecture topic missing from the mapping is silently not loaded). Warnings are gaps or doubts.

    python scripts/audit_kg.py            # files only
    python scripts/audit_kg.py --neo4j    # also compare with the loaded graph
"""
from __future__ import annotations

import glob
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

from profsagent.kg.quality import co_quality
from profsagent.kg.stub import slug

ROOT = Path(__file__).resolve().parents[3]
ENRICHED = ROOT / "data" / "enriched"
MAPPING = ROOT / "data" / "canonical" / "topic_mapping.json"

ERR, WARN = "error", "warning"
BLOOM_RANK = {"Remember": 1, "Understand": 2, "Apply": 3, "Analyze": 4, "Evaluate": 5, "Create": 6}
DUP_SHEET_JACCARD = 0.8   # two codes whose lecture topics overlap this much are copies of one sheet (cross-listing)

CHECKS = {   # code -> what it means; printed by the script, and the test pins that every emitted code is listed
    "KA-NO-COS": (WARN, "course has no course outcomes"),
    "KA-NO-WEEKS": (WARN, "course has no weekly plan"),
    "KA-NO-TOPICS": (WARN, "weekly plan lists no lecture topics"),
    "KA-NO-ASSESS": (WARN, "course has no assessment components"),
    "KA-WEIGHTS": (WARN, "assessment weights do not sum to 100 (the course is left out of the weight priors)"),
    "KA-LEVEL": (WARN, "course level missing"),
    "KA-CREDITS": (WARN, "credits missing"),
    "KA-CO-DUP": (ERR, "two COs share a label (load.py merges them into one node)"),
    "KA-CO-REF": (ERR, "a week names a CO the course does not have (load.py creates an empty CO node)"),
    "KA-CO-UNMET": (WARN, "a CO no week meets"),
    "KA-WEEK-DUP": (ERR, "two weeks share a number (load.py merges them into one node)"),
    "KA-BLOOM-UNCLASSIFIED": (WARN, "COs the ingest Bloom tagger could not classify"),
    "KA-BLOOM-DISAGREE": (WARN, "COs where the ingest tagger and the design pipeline's lexicon give different Bloom levels"),
    "KA-PREREQ-DANGLING": (ERR, "a prerequisite is not a course in the graph (load.py creates a code-only course node)"),
    "KA-PREREQ-SELF": (ERR, "a course lists itself as a prerequisite"),
    "KA-PREREQ-CYCLE": (ERR, "mandatory prerequisites form a cycle"),
    "KA-ANTI-DANGLING": (ERR, "an anti-requisite is not a course in the graph"),
    "KA-ALIAS": (ERR, "one alias is claimed by two courses"),
    "KA-DUP-SHEET": (WARN, "two course codes carry (nearly) the same weekly plan; corpus statistics count it twice"),
    "KA-TOPIC-UNMAPPED": (ERR, "a lecture topic is missing from the topic mapping (not loaded)"),
    "KA-TOPIC-SLUG": (ERR, "two canonical topics share a slug, so a design's T:<slug> link resolves to only one of them"),
    "KA-TOPIC-STALE": (WARN, "mapping entries for topics no course uses"),
    "KA-NEO-MISSING": (ERR, "a course in data/enriched is not in Neo4j"),
    "KA-NEO-EXTRA": (WARN, "a course node in Neo4j has no data file (a code-only node, or left over from an older load)"),
    "KA-NEO-EMPTY-CO": (ERR, "CourseOutcome nodes without text"),
    "KA-NEO-STALE-TOPIC": (WARN, "Topic nodes whose id is not in the current mapping (an older mapping, not wiped)"),
    "KA-NEO-ORPHAN-TOPIC": (WARN, "Topic nodes no week covers"),
}


def f(code: str, course: str | None, message: str, **extra) -> dict:
    return {"code": code, "severity": CHECKS[code][0], "course": course, "message": message, **extra}


def load_courses(enriched_dir: Path = ENRICHED) -> list[dict]:
    out = []
    for p in sorted(glob.glob(str(Path(enriched_dir) / "*.json"))):
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        if (d.get("header") or {}).get("course_code"):
            out.append(d)
    return out


def _topics(d: dict) -> list[str]:
    return [str(t).strip() for w in d.get("weekly_plan", []) for t in w.get("lecture_topics", []) if str(t).strip()]


def _course_findings(d: dict, codes: set[str]) -> list[dict]:
    h = d["header"]
    code = h["course_code"]
    out = []
    cos, weeks, assess = d.get("outcomes", []), d.get("weekly_plan", []), d.get("assessments", [])
    if not cos:
        out.append(f("KA-NO-COS", code, "no course outcomes"))
    if not weeks:
        out.append(f("KA-NO-WEEKS", code, "no weekly plan"))
    elif not _topics(d):
        out.append(f("KA-NO-TOPICS", code, f"{len(weeks)} weeks but no lecture topics"))
    if not assess:
        out.append(f("KA-NO-ASSESS", code, "no assessment components"))
    else:
        ws = [a.get("weight_pct") for a in assess]
        if None not in ws and abs(sum(ws) - 100) >= 1:
            out.append(f("KA-WEIGHTS", code, f"weights sum to {sum(ws)}"))
    if h.get("level") in (None, ""):
        out.append(f("KA-LEVEL", code, "no course level"))
    if h.get("credits") in (None, "") and (h.get("catalogue") or {}).get("credits") is None:
        out.append(f("KA-CREDITS", code, "no credits"))

    labels = Counter(c["label"] for c in cos)
    for lab, n in sorted(labels.items()):
        if n > 1:
            out.append(f("KA-CO-DUP", code, f"{n} COs labelled {lab}"))
    nums = Counter(str(w.get("week")) for w in weeks)
    for num, n in sorted(nums.items()):
        if n > 1:
            out.append(f("KA-WEEK-DUP", code, f"{n} weeks numbered {num}"))
    met = {lab for w in weeks for lab in w.get("cos_met", [])}
    bad = sorted(met - set(labels))
    if bad:
        out.append(f("KA-CO-REF", code, f"weeks name COs the course does not have: {bad}"))
    if met:   # only when the sheet maps weeks to COs at all
        unmet = [lab for lab in labels if lab not in met]
        if unmet:
            out.append(f("KA-CO-UNMET", code, f"no week meets {unmet}"))

    uncl = [c["label"] for c in cos if c.get("bloom_level") in (None, "", "Unclassified")]
    if uncl:
        out.append(f("KA-BLOOM-UNCLASSIFIED", code, f"{len(uncl)} of {len(cos)} COs unclassified: {uncl}", n=len(uncl)))
    dis = []
    for c in cos:
        a, b = BLOOM_RANK.get(c.get("bloom_level")), co_quality(c.get("raw_text") or "")[3]
        if a and b and a != b:
            dis.append(f"{c['label']} {a}≠{b}")
    if dis:
        out.append(f("KA-BLOOM-DISAGREE", code, f"ingest vs lexicon level: {dis}", n=len(dis)))

    for link in h.get("prerequisite_links", []):
        if link["code"] == code:
            out.append(f("KA-PREREQ-SELF", code, f"{code} requires itself"))
        elif link["code"] not in codes:
            out.append(f("KA-PREREQ-DANGLING", code, f"prerequisite {link['code']} ({link.get('kind')}) is not in the graph"))
    for a in h.get("anti_requisites_resolved", []):
        if a not in codes:
            out.append(f("KA-ANTI-DANGLING", code, f"anti-requisite {a} is not in the graph"))
    return out


def _prereq_cycles(courses: list[dict]) -> list[list[str]]:
    import networkx as nx
    g = nx.DiGraph()
    for d in courses:
        code = d["header"]["course_code"]
        for link in d["header"].get("prerequisite_links", []):
            if link.get("kind") == "mandatory" and link["code"] != code:
                g.add_edge(code, link["code"])
    return sorted(sorted(c) for c in nx.strongly_connected_components(g) if len(c) > 1)


def _duplicate_sheets(courses: list[dict]) -> list[tuple[str, str, float]]:
    sets = {d["header"]["course_code"]: {t.lower() for t in _topics(d)} for d in courses}
    inv = defaultdict(set)
    for code, ts in sets.items():
        for t in ts:
            inv[t].add(code)
    pairs = {tuple(sorted(p)) for cs in inv.values() for p in itertools.combinations(cs, 2)}
    out = []
    for a, b in sorted(pairs):
        j = len(sets[a] & sets[b]) / len(sets[a] | sets[b])
        if j >= DUP_SHEET_JACCARD:
            out.append((a, b, round(j, 3)))
    return out


def audit_files(enriched_dir: Path = ENRICHED, mapping_path: Path = MAPPING) -> dict:
    courses = load_courses(enriched_dir)
    mapping = json.loads(Path(mapping_path).read_text(encoding="utf-8"))
    codes = {d["header"]["course_code"] for d in courses}
    findings = [x for d in courses for x in _course_findings(d, codes)]

    for cyc in _prereq_cycles(courses):
        findings.append(f("KA-PREREQ-CYCLE", cyc[0], f"mandatory prerequisite cycle among {cyc}"))
    owner = defaultdict(set)
    for d in courses:
        for a in [d["header"]["course_code"], *(d["header"].get("aliases") or [])]:
            owner[a].add(d["header"]["course_code"])
    for a, cs in sorted(owner.items()):
        if len(cs) > 1:
            findings.append(f("KA-ALIAS", None, f"alias {a} is claimed by {sorted(cs)}"))
    for a, b, j in _duplicate_sheets(courses):
        findings.append(f("KA-DUP-SHEET", a, f"{a} and {b} share {j:.0%} of their lecture topics", other=b))

    used = set()
    for d in courses:
        missing = sorted({t for t in _topics(d) if t not in mapping})
        used |= set(_topics(d))
        if missing:
            findings.append(f("KA-TOPIC-UNMAPPED", d["header"]["course_code"], f"{len(missing)} topics not in the mapping: {missing[:5]}",
                              n=len(missing)))
    names = {v["canonical_id"]: v["canonical_name"] for v in mapping.values()}
    by_slug = defaultdict(set)
    for cid, name in names.items():
        by_slug[slug(name)].add(cid)
    for s, ids in sorted(by_slug.items()):
        if len(ids) > 1:
            findings.append(f("KA-TOPIC-SLUG", None, f"T:{s} names {sorted(ids)}: {sorted(names[i] for i in ids)}"))
    stale = sorted(set(mapping) - used)
    if stale:
        findings.append(f("KA-TOPIC-STALE", None, f"{len(stale)} mapping entries are used by no course: {stale[:5]}", n=len(stale)))

    n_cos = sum(len(d.get("outcomes", [])) for d in courses)
    df = Counter(cid for d in courses for cid in {mapping[t]["canonical_id"] for t in _topics(d) if t in mapping})
    cluster_size = Counter(v["canonical_id"] for v in mapping.values())
    stats = {
        "courses": len(courses),
        "with_cos": sum(1 for d in courses if d.get("outcomes")),
        "with_weeks": sum(1 for d in courses if d.get("weekly_plan")),
        "with_topics": sum(1 for d in courses if _topics(d)),
        "with_assessment": sum(1 for d in courses if d.get("assessments")),
        "cos": n_cos,
        "bloom_ingest": dict(Counter(c.get("bloom_level") for d in courses for c in d.get("outcomes", [])).most_common()),
        "bloom_unclassified_pct": _pct(sum(x.get("n", 0) for x in findings if x["code"] == "KA-BLOOM-UNCLASSIFIED"), n_cos),
        "bloom_disagree_pct": _pct(sum(x.get("n", 0) for x in findings if x["code"] == "KA-BLOOM-DISAGREE"), n_cos),
        "raw_topics": len(mapping),
        "canonical_topics": len(names),
        "canonical_singleton_pct": _pct(sum(1 for n in cluster_size.values() if n == 1), len(cluster_size)),
        "canonical_in_2plus_courses": sum(1 for n in df.values() if n >= 2),
    }
    return _report("files", findings, stats)


def _pct(a: int, b: int) -> float:
    return round(100 * a / b, 1) if b else 0.0


def _report(source: str, findings: list[dict], stats: dict) -> dict:
    by_code = Counter(x["code"] for x in findings)
    return {"source": source, "stats": stats,
            "summary": {"errors": sum(1 for x in findings if x["severity"] == ERR),
                        "warnings": sum(1 for x in findings if x["severity"] == WARN),
                        "by_code": dict(sorted(by_code.items())),
                        "courses_with_errors": len({x["course"] for x in findings if x["severity"] == ERR and x["course"]})},
            "findings": findings}


NEO_Q = {
    "courses": "MATCH (c:Course) RETURN c.code AS code, c.name AS name",
    "empty_cos": "MATCH (co:CourseOutcome) WHERE co.text IS NULL OR co.text = '' RETURN co.id AS id",
    "topics": "MATCH (t:Topic) OPTIONAL MATCH (t)<-[cv:COVERS]-() RETURN t.id AS id, count(cv) AS n",
}


def audit_neo4j(driver, enriched_dir: Path = ENRICHED, mapping_path: Path = MAPPING) -> dict:
    """Compare the loaded graph with the files it was loaded from. Read-only."""
    files = {d["header"]["course_code"] for d in load_courses(enriched_dir)}
    ids = {v["canonical_id"] for v in json.loads(Path(mapping_path).read_text(encoding="utf-8")).values()}
    with driver.session() as s:
        rows = {k: [r.data() for r in s.run(q)] for k, q in NEO_Q.items()}
    graph = {r["code"]: r["name"] for r in rows["courses"]}
    findings = [f("KA-NEO-MISSING", c, f"{c} is in data/enriched but not in Neo4j") for c in sorted(files - set(graph))]
    findings += [f("KA-NEO-EXTRA", c, f"{c} is in Neo4j" + (" (code only, no name)" if not graph[c] else "") + " but has no data file")
                 for c in sorted(set(graph) - files)]
    if rows["empty_cos"]:
        findings.append(f("KA-NEO-EMPTY-CO", None, f"{len(rows['empty_cos'])} CourseOutcome nodes have no text: "
                                                   f"{sorted(r['id'] for r in rows['empty_cos'])[:8]}", n=len(rows["empty_cos"])))
    stale = sorted(r["id"] for r in rows["topics"] if r["id"] not in ids)
    if stale:
        findings.append(f("KA-NEO-STALE-TOPIC", None, f"{len(stale)} Topic nodes are not in the mapping: {stale[:5]}", n=len(stale)))
    orphan = sorted(r["id"] for r in rows["topics"] if not r["n"])
    if orphan:
        findings.append(f("KA-NEO-ORPHAN-TOPIC", None, f"{len(orphan)} Topic nodes are covered by no week: {orphan[:5]}", n=len(orphan)))
    stats = {"courses_in_graph": len(graph), "courses_in_files": len(files), "topics_in_graph": len(rows["topics"]),
             "empty_cos": len(rows["empty_cos"])}
    return _report("neo4j", findings, stats)


def merge_reports(*reports: dict) -> dict:
    findings = [x for r in reports for x in r["findings"]]
    return _report("+".join(r["source"] for r in reports), findings, {k: v for r in reports for k, v in r["stats"].items()})


def table(report: dict) -> str:
    """One line per code: severity, count, meaning."""
    lines = [f"{'code':<22} {'severity':<8} {'count':>5}  meaning"]
    for code, n in sorted(report["summary"]["by_code"].items(), key=lambda kv: (CHECKS[kv[0]][0] != ERR, -kv[1])):
        lines.append(f"{code:<22} {CHECKS[code][0]:<8} {n:>5}  {CHECKS[code][1]}")
    return "\n".join(lines)

