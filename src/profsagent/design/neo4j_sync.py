"""Load a run's course design graph (Layer B, runs/<id>/design_graph.json) into Neo4j next to Layer A.

Design nodes get the labels `DesignNode` and `D_<label>` (D_CO, D_LO, D_CourseTopic, D_Assessment, ...) so they never
mix with Layer A's own labels (Course, Topic, Resource, ...). Every node carries `run_id`, so several runs of the same
course can coexist; reloading a run replaces it. Links that leave the design point at real Layer A / shared nodes:

  course codes   (REQUIRES, OVERLAPS, ...)  -> (:Course {code})            matched on code or alias
  canonical ids  (SAME_AS TOPIC_xxxx)       -> (:Topic {id})
  programme ids  (MAPS_TO BTECH-COMMON/PO3) -> (:ProgrammeOutcome {uid})   created from data/programmes/*.yaml
  anything else                              -> (:ExternalRef {ref})       so nothing is silently dropped

A (:DesignRun {run_id}) node holds the run summary and points at the new course: (DesignRun)-[:DESIGNS]->(D_NewCourse).

Reading it in Neo4j Browser:
- every generated node also has the label `Generated` (Layer A nodes and programme outcomes have `Institutional`);
- each run gets a course code of its own, the department prefix + a number from 1001 (CSE1001, CSE1002, ...; real
  IIIT-D codes have 3 digits, so these never clash). It is stored as `course_code` on every node of the run, as `code`
  on the D_NewCourse node, and in runs/<id>/course_code.txt so reloading the run keeps its number;
- every node has a readable `name` (the caption Neo4j shows): "CSE1001 · <title>", "Week 3", "W3 Lecture 2", "CO2",
  "CO2.LO1", "Quiz1 (W3)", topic and book titles;
- the course node is the hub: HAS_CO, HAS_MODULE, HAS_WEEK, HAS_ASSESSMENT, USES_RESOURCE, ... link it to every part.

check_run() compares a loaded run with its design_graph.json (every node and link) and checks the course is complete
(every CO has LOs, every LO is taught and assessed, every topic scheduled, weeks 1..N, ...):

    python scripts/load_design_to_neo4j.py --run-id cs601-01 --check

    python scripts/load_design_to_neo4j.py --run-id cs601-01           # load / reload
    python scripts/load_design_to_neo4j.py --run-id cs601-01 --delete  # remove it from the graph
"""
from __future__ import annotations

import json
import os
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

from profsagent.config import RUNS, pedagogy, programme
from profsagent.kg.stub import slug

META = ("uid", "local_id", "label", "version", "status", "created_by", "prompt_id", "prompt_version", "model")
CODE_FILE = "course_code.txt"
FIRST_GENERATED_NUMBER = 1001
# The course node is the hub of its design, as (:Course) is in Layer A: it links to every part of the course
HUB_LINKS = {"CO": "HAS_CO", "Module": "HAS_MODULE", "Week": "HAS_WEEK", "Assessment": "HAS_ASSESSMENT",
             "Resource": "USES_RESOURCE", "TopicGroup": "HAS_TOPIC_GROUP", "Constraint": "HAS_CONSTRAINT",
             "Assumption": "HAS_ASSUMPTION", "ContextField": "HAS_FORM_FIELD", "Approval": "HAS_APPROVAL"}


def _scalar(v):
    """Neo4j properties must be primitives or lists of primitives; anything else is stored as JSON text."""
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    if isinstance(v, list) and all(isinstance(x, (str, int, float, bool)) for x in v):
        return v
    return json.dumps(v, ensure_ascii=False, default=str)


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


def course_code(run_dir: Path, st: dict, drv) -> str:
    """The run's generated course code: kept in runs/<id>/course_code.txt, else the next free number for the department
    (looking at every run folder and every run already in Neo4j), from FIRST_GENERATED_NUMBER."""
    f = Path(run_dir) / CODE_FILE
    if f.exists() and f.read_text(encoding="utf-8").strip():
        return f.read_text(encoding="utf-8").strip()
    dept = re.sub(r"[^A-Z]", "", str(st.get("department") or (st.get("run_cfg") or {}).get("department") or "CSE").upper()) or "CSE"
    used = {p.read_text(encoding="utf-8").strip() for p in RUNS.glob(f"*/{CODE_FILE}")}
    with drv.session() as s:
        used |= {r["c"] for r in s.run("MATCH (d:DesignRun) WHERE d.course_code IS NOT NULL RETURN d.course_code AS c")}
    nums = [int(c[len(dept):]) for c in used if c.startswith(dept) and c[len(dept):].isdigit()]
    code = f"{dept}{max(nums + [FIRST_GENERATED_NUMBER - 1]) + 1}"
    f.write_text(code + "\n", encoding="utf-8")
    return code


def caption(label: str, local_id: str, props: dict, code: str) -> str:
    """Short readable name for a design node (Neo4j shows `name` as the node's caption)."""
    p, lid = props or {}, str(local_id or "")
    wk = re.match(r"W(\d+)", lid)
    w = f"W{int(wk.group(1))}" if wk else ""
    if label == "NewCourse":
        return f"{code} · {p.get('title') or ''}".rstrip(" ·")
    if label == "Week":
        return f"Week {p.get('n') or (int(wk.group(1)) if wk else lid)}"
    if label == "Lecture":
        return f"{w} Lecture {p.get('slot') or lid.rsplit('L', 1)[-1]}".strip()
    if label == "Tutorial":
        return f"{w} Tutorial".strip()
    if label == "LabSession":
        return f"{w} Lab".strip()
    if label == "Assessment":
        name, week = lid.split(":", 1)[-1], p.get("release_week")
        return f"{name} (W{week})" if week not in (None, "") else name
    if label in ("Module", "TopicGroup"):
        return f"{lid} {p.get('title') or ''}".strip()
    if label in ("CourseTopic", "Resource"):
        return str(p.get("title") or lid)
    if label == "ExternalCourse":
        return f"{p.get('institution') or ''} {p.get('course_code') or ''}".strip() or lid
    if label == "Constraint":
        return f"{lid} {p.get('target') or ''}".strip()
    if label == "Assumption":
        return f"{lid} {p.get('what') or ''}".strip()
    if label == "ContextField":
        return "Form: " + lid.removeprefix("CCO.")
    if label == "Approval":
        return f"{p.get('gate') or lid}: {p.get('decision') or ''}".rstrip(": ")
    return lid   # CO1, CO1.LO1, ...


def driver():
    from neo4j import GraphDatabase
    return GraphDatabase.driver(os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
                                auth=(os.environ.get("NEO4J_USER", "neo4j"), os.environ.get("NEO4J_PASSWORD", "")))


def delete_run(run_id: str, drv=None) -> int:
    own = drv is None
    drv = drv or driver()
    try:
        with drv.session() as s:
            n = s.run("MATCH (n:DesignNode {run_id: $r}) RETURN count(n) AS n", r=run_id).single()["n"]
            s.run("MATCH (n:DesignNode {run_id: $r}) DETACH DELETE n", r=run_id)
            s.run("MATCH (d:DesignRun {run_id: $r}) DETACH DELETE d", r=run_id)
            s.run("MATCH (x:ExternalRef) WHERE NOT (x)--() DELETE x")
        return n
    finally:
        if own:
            drv.close()


def _split_edges(g: dict) -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    """Design-graph edges by relationship type: (links between design nodes, links to anything else)."""
    pid, nodes = g["project_id"], g["nodes"]

    def resolve(x: str) -> tuple[str, str]:   # (kind, id); repairs links saved by older runs (missing/extra project prefix)
        if x in nodes:
            return "d", x
        if f"{pid}/{x}" in nodes:
            return "d", f"{pid}/{x}"
        if x.startswith(pid + "/"):
            x = x[len(pid) + 1:]
        return "x", x

    internal: dict[str, list[dict]] = defaultdict(list)
    external: dict[str, list[dict]] = defaultdict(list)
    for e in g["edges"]:
        (ks, s_), (kd, d_) = resolve(e["src"]), resolve(e["dst"])
        props = {k: _scalar(v) for k, v in (e.get("props") or {}).items()}
        if ks != "d":
            continue   # every link starts at a design node; nothing else is expected
        (internal if kd == "d" else external)[_safe(e["rel"])].append({"s": s_, "d": d_, "p": props})
    return internal, external


def _read_run(run_dir: Path) -> tuple[dict, dict]:
    g = json.loads((run_dir / "design_graph.json").read_text(encoding="utf-8"))
    st = json.loads((run_dir / "state.json").read_text(encoding="utf-8")) if (run_dir / "state.json").exists() else {}
    return g, st


def load_run(run_dir: Path, drv=None) -> dict:
    run_dir = Path(run_dir)
    run_id = run_dir.name
    g, st = _read_run(run_dir)
    pid, nodes = g["project_id"], g["nodes"]

    by_label: dict[str, list[dict]] = defaultdict(list)
    rows_with_nodes: list[tuple[dict, dict]] = []
    for u, n in nodes.items():
        row = {k: _scalar(n.get(k)) for k in META}
        row.update(run_id=run_id, project_id=pid, sources=_scalar(n.get("sources")), ts=n.get("ts"))
        for k, v in (n.get("props") or {}).items():
            row[k if k not in row else f"p_{k}"] = _scalar(v)
        if "name" in row:   # `name` is the caption set below; keep any design property of that name
            row["p_name"] = row.pop("name")
        by_label[_safe(n["label"])].append(row)
        rows_with_nodes.append((row, n))

    internal, external = _split_edges(g)

    vs = [x for v in (st.get("violations") or {}).values() for x in v]
    summary = {"run_id": run_id, "project_id": pid, "course_name": (st.get("cco_compact") or {}).get("course_name"),
               "kg_backend": (st.get("run_cfg") or {}).get("kg_backend"), "loaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
               "open_errors": sum(1 for x in vs if x.get("severity") == "error"),
               "open_warnings": sum(1 for x in vs if x.get("severity") == "warning"),
               "approvals": json.dumps(st.get("approvals", []), default=str)}
    own = drv is None
    drv = drv or driver()
    code = course_code(run_dir, st, drv)
    summary.update(course_code=code, name=f"{code} · run summary ({run_id})")
    for row, n in rows_with_nodes:
        row["name"] = caption(n["label"], n.get("local_id"), n.get("props"), code)
        row["course_code"] = code
        if n["label"] == "NewCourse":
            row["code"] = code
    with drv.session() as s:   # KG topic candidates are named T:<slug of the topic name>; Layer A topics have TOPIC_xxxx ids
        slug_to_id = {}
        for r in s.run("MATCH (t:Topic) RETURN t.id AS id, t.name AS name"):
            slug_to_id.setdefault("T:" + slug(r["name"] or ""), r["id"])
    for rows in external.values():
        for r in rows:
            if r["d"].startswith("T:") and r["d"] in slug_to_id:
                r["p"] = {**r["p"], "kg_ref": r["d"]}
                r["d"] = slug_to_id[r["d"]]
    stats = {"nodes": 0, "internal_links": 0, "hub_links": 0, "links_to_course": 0, "links_to_topic": 0, "links_to_programme": 0,
             "unresolved_refs": 0}
    try:
        with drv.session() as s:
            s.run("CREATE INDEX design_node IF NOT EXISTS FOR (n:DesignNode) ON (n.run_id, n.uid)")
            s.run("CREATE CONSTRAINT programme_outcome_uid IF NOT EXISTS FOR (p:ProgrammeOutcome) REQUIRE p.uid IS UNIQUE")
            for prog in pedagogy().get("copo_programmes", []):   # shared programme outcome nodes (template text, verbatim)
                rows = [{"uid": x["id"], "programme": prog, "label": x.get("label"), "kind": x.get("kind"), "text": x["text"],
                         "name": f"{x.get('label') or x['id'].split('/')[-1]} ({prog})"}
                        for x in programme(prog)["po"]]
                s.run("UNWIND $rows AS r MERGE (p:ProgrammeOutcome {uid: r.uid}) SET p += r, p:Institutional", rows=rows)
            delete_run(run_id, drv)
            s.run("CREATE (d:DesignRun:Generated) SET d = $p", p=summary)
            for label, rows in by_label.items():
                s.run(f"UNWIND $rows AS r CREATE (n:DesignNode:Generated:D_{label}) SET n = r", rows=rows)
                stats["nodes"] += len(rows)
            s.run("MATCH (d:DesignRun {run_id: $r}), (n:D_NewCourse {run_id: $r}) CREATE (d)-[:DESIGNS]->(n)", r=run_id)
            for label, rel in HUB_LINKS.items():
                stats["hub_links"] += s.run(f"MATCH (c:D_NewCourse {{run_id: $r}}), (n:D_{label} {{run_id: $r}}) "
                                            f"CREATE (c)-[:{rel}]->(n) RETURN count(*) AS n", r=run_id).single()["n"]
            for rel, rows in internal.items():
                s.run(f"UNWIND $rows AS r MATCH (a:DesignNode {{run_id: $run, uid: r.s}}), (b:DesignNode {{run_id: $run, uid: r.d}}) "
                      f"CREATE (a)-[x:{rel}]->(b) SET x = r.p", rows=rows, run=run_id)
                stats["internal_links"] += len(rows)
            for rel, rows in external.items():
                res = s.run(f"""UNWIND $rows AS r
                    MATCH (a:DesignNode {{run_id: $run, uid: r.s}})
                    OPTIONAL MATCH (c:Course) WHERE c.code = r.d OR r.d IN coalesce(c.aliases, [])
                    OPTIONAL MATCH (t:Topic {{id: r.d}})
                    OPTIONAL MATCH (p:ProgrammeOutcome {{uid: r.d}})
                    WITH a, r, head(collect(DISTINCT c)) AS c, head(collect(DISTINCT t)) AS t, head(collect(DISTINCT p)) AS p
                    CALL (a, r, c, t, p) {{
                        WITH a, r, coalesce(c, t, p) AS target WHERE target IS NOT NULL
                        CREATE (a)-[x:{rel}]->(target) SET x = r.p
                        RETURN 1 AS ok
                      UNION
                        WITH a, r, c, t, p WHERE c IS NULL AND t IS NULL AND p IS NULL
                        MERGE (e:ExternalRef {{ref: r.d}})
                        CREATE (a)-[x:{rel}]->(e) SET x = r.p
                        RETURN 0 AS ok
                    }}
                    RETURN c IS NOT NULL AS course, t IS NOT NULL AS topic, p IS NOT NULL AS prog, ok""", rows=rows, run=run_id).data()
                for x in res:
                    stats["links_to_course"] += x["course"]
                    stats["links_to_topic"] += x["topic"] and not x["course"]
                    stats["links_to_programme"] += x["prog"]
                    stats["unresolved_refs"] += not x["ok"]
    finally:
        if own:
            drv.close()
    return stats


def check_run(run_dir: Path, drv=None) -> list[dict]:
    """Is the run in Neo4j an exact copy of its design_graph.json, and is the course complete? -> [{check, ok, detail}]"""
    run_dir = Path(run_dir)
    run_id = run_dir.name
    g, st = _read_run(run_dir)
    internal, external = _split_edges(g)
    want_nodes = Counter(n["label"] for n in g["nodes"].values())
    want_internal = Counter({rel: len(rows) for rel, rows in internal.items()})
    want_external = sum(len(rows) for rows in external.values())
    own = drv is None
    drv = drv or driver()
    out: list[dict] = []

    def add(check: str, ok: bool, detail: str) -> None:
        out.append({"check": check, "ok": bool(ok), "detail": detail})

    try:
        with drv.session() as s:
            def ids(q: str, **params) -> list:
                return [r[0] for r in s.run(q, r=run_id, **params)]

            got_nodes = Counter({r["l"]: r["n"] for r in s.run(
                "MATCH (n:DesignNode {run_id: $r}) RETURN n.label AS l, count(*) AS n", r=run_id)})
            add("nodes match design_graph.json", got_nodes == want_nodes,
                f"{sum(got_nodes.values())} nodes in {len(got_nodes)} types" if got_nodes == want_nodes
                else f"differences: {dict((got_nodes - want_nodes) + (want_nodes - got_nodes))}")
            hub = set(HUB_LINKS.values())
            got_internal = Counter({r["t"]: r["n"] for r in s.run(
                "MATCH (:DesignNode {run_id: $r})-[x]->(:DesignNode {run_id: $r}) RETURN type(x) AS t, count(*) AS n", r=run_id)
                if r["t"] not in hub})
            add("links inside the course match", got_internal == want_internal,
                f"{sum(got_internal.values())} links in {len(got_internal)} types" if got_internal == want_internal
                else f"differences: {dict((got_internal - want_internal) + (want_internal - got_internal))}")
            got_external = ids("MATCH (:DesignNode {run_id: $r})-[x]->(b) WHERE NOT b:DesignNode RETURN count(x)")[0]
            add("links to the IIIT-D graph match", got_external == want_external, f"{got_external} of {want_external}")
            unresolved = ids("MATCH (:DesignNode {run_id: $r})-[x]->(e:ExternalRef) RETURN DISTINCT e.ref")
            add("every reference found in the IIIT-D graph", not unresolved,
                "all found" if not unresolved else f"not found: {unresolved}")
            hubs = ids("MATCH (c:D_NewCourse {run_id: $r}) RETURN c.name")
            loose = ids("MATCH (n:DesignNode {run_id: $r}) WHERE n.label IN $labels AND NOT (:D_NewCourse)-->(n) RETURN n.name",
                        labels=list(HUB_LINKS))
            add("one course node, linked to every part", len(hubs) == 1 and not loose,
                f"{hubs[0] if hubs else 'no course node'}" + (f"; not linked: {loose}" if loose else ""))
            for check, q in [
                ("every CO has LOs", "MATCH (n:D_CO {run_id: $r}) WHERE NOT (n)-[:DECOMPOSES_INTO]->(:D_LO) RETURN n.name"),
                ("every LO belongs to a CO", "MATCH (n:D_LO {run_id: $r}) WHERE NOT (:D_CO)-[:DECOMPOSES_INTO]->(n) RETURN n.name"),
                ("every LO is taught by a topic", "MATCH (n:D_LO {run_id: $r}) WHERE NOT (n)-[:TAUGHT_VIA]->(:D_CourseTopic) RETURN n.name"),
                ("every LO is assessed", "MATCH (n:D_LO {run_id: $r}) WHERE NOT (:D_Assessment)-[:ASSESSES]->(n) RETURN n.name"),
                ("every topic is in a lecture", "MATCH (n:D_CourseTopic {run_id: $r}) WHERE NOT (n)-[:DELIVERED_IN]->(:D_Lecture) RETURN n.name"),
                ("every lecture, lab and tutorial is in a week",
                 "MATCH (n:DesignNode {run_id: $r}) WHERE n.label IN ['Lecture', 'LabSession', 'Tutorial'] "
                 "AND NOT (n)-[:IN_WEEK]->(:D_Week) RETURN n.name"),
                ("every assessment has release and due weeks",
                 "MATCH (n:D_Assessment {run_id: $r}) WHERE NOT (n)-[:RELEASED_IN]->(:D_Week) OR NOT (n)-[:DUE_IN]->(:D_Week) RETURN n.name"),
            ]:
                bad = ids(q)
                add(check, not bad, "yes" if not bad else f"missing for: {bad}")
            weeks = sorted(int(w) for w in ids("MATCH (n:D_Week {run_id: $r}) RETURN n.n") if w is not None)
            n_weeks = int(st.get("weeks") or len(weeks))
            add("weeks 1..N, none missing", weeks == list(range(1, n_weeks + 1)), f"{len(weeks)} weeks (expected {n_weeks})")
    finally:
        if own:
            drv.close()
    vs = [x for v in (st.get("violations") or {}).values() for x in v if x.get("severity") == "error"]
    add("design passed the validators (no open errors)", not vs,
        "no open errors" if not vs else f"{len(vs)} open: " + "; ".join(f"[{x.get('code')}] {x.get('message', '')[:90]}" for x in vs))
    return out
