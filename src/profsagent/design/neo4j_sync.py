"""Load a run's course design graph (Layer B, runs/<id>/design_graph.json) into Neo4j next to Layer A.

Design nodes get the labels `DesignNode` and `D_<label>` (D_CO, D_LO, D_CourseTopic, D_Assessment, ...) so they never
mix with Layer A's own labels (Course, Topic, Resource, ...). Every node carries `run_id`, so several runs of the same
course can coexist; reloading a run replaces it. Links that leave the design point at real Layer A / shared nodes:

  course codes   (REQUIRES, OVERLAPS, ...)  -> (:Course {code})            matched on code or alias
  canonical ids  (SAME_AS TOPIC_xxxx)       -> (:Topic {id})
  programme ids  (MAPS_TO BTECH-COMMON/PO3) -> (:ProgrammeOutcome {uid})   created from data/programmes/*.yaml
  anything else                              -> (:ExternalRef {ref})       so nothing is silently dropped

A (:DesignRun {run_id}) node holds the run summary and points at the new course: (DesignRun)-[:DESIGNS]->(D_NewCourse).

    python scripts/load_design_to_neo4j.py --run-id cs601-01           # load / reload
    python scripts/load_design_to_neo4j.py --run-id cs601-01 --delete  # remove it from the graph
"""
from __future__ import annotations

import json
import os
import re
import time
from collections import defaultdict
from pathlib import Path

from profsagent.config import pedagogy, programme
from profsagent.kg.stub import slug

META = ("uid", "local_id", "label", "version", "status", "created_by", "prompt_id", "prompt_version", "model")


def _scalar(v):
    """Neo4j properties must be primitives or lists of primitives; anything else is stored as JSON text."""
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    if isinstance(v, list) and all(isinstance(x, (str, int, float, bool)) for x in v):
        return v
    return json.dumps(v, ensure_ascii=False, default=str)


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


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


def load_run(run_dir: Path, drv=None) -> dict:
    run_dir = Path(run_dir)
    run_id = run_dir.name
    g = json.loads((run_dir / "design_graph.json").read_text(encoding="utf-8"))
    st = json.loads((run_dir / "state.json").read_text(encoding="utf-8")) if (run_dir / "state.json").exists() else {}
    pid, nodes = g["project_id"], g["nodes"]

    def resolve(x: str) -> tuple[str, str]:   # (kind, id); repairs links saved by older runs (missing/extra project prefix)
        if x in nodes:
            return "d", x
        if f"{pid}/{x}" in nodes:
            return "d", f"{pid}/{x}"
        if x.startswith(pid + "/"):
            x = x[len(pid) + 1:]
        return "x", x

    by_label: dict[str, list[dict]] = defaultdict(list)
    for u, n in nodes.items():
        row = {k: _scalar(n.get(k)) for k in META}
        row.update(run_id=run_id, project_id=pid, sources=_scalar(n.get("sources")), ts=n.get("ts"))
        for k, v in (n.get("props") or {}).items():
            row[k if k not in row else f"p_{k}"] = _scalar(v)
        by_label[_safe(n["label"])].append(row)

    internal: dict[str, list[dict]] = defaultdict(list)
    external: dict[str, list[dict]] = defaultdict(list)
    for e in g["edges"]:
        (ks, s_), (kd, d_) = resolve(e["src"]), resolve(e["dst"])
        props = {k: _scalar(v) for k, v in (e.get("props") or {}).items()}
        if ks != "d":
            continue   # every link starts at a design node; nothing else is expected
        (internal if kd == "d" else external)[_safe(e["rel"])].append({"s": s_, "d": d_, "p": props})

    vs = [x for v in (st.get("violations") or {}).values() for x in v]
    summary = {"run_id": run_id, "project_id": pid, "course_name": (st.get("cco_compact") or {}).get("course_name"),
               "kg_backend": (st.get("run_cfg") or {}).get("kg_backend"), "loaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
               "open_errors": sum(1 for x in vs if x.get("severity") == "error"),
               "open_warnings": sum(1 for x in vs if x.get("severity") == "warning"),
               "approvals": json.dumps(st.get("approvals", []), default=str)}
    own = drv is None
    drv = drv or driver()
    with drv.session() as s:   # KG topic candidates are named T:<slug of the topic name>; Layer A topics have TOPIC_xxxx ids
        slug_to_id = {}
        for r in s.run("MATCH (t:Topic) RETURN t.id AS id, t.name AS name"):
            slug_to_id.setdefault("T:" + slug(r["name"] or ""), r["id"])
    for rows in external.values():
        for r in rows:
            if r["d"].startswith("T:") and r["d"] in slug_to_id:
                r["p"] = {**r["p"], "kg_ref": r["d"]}
                r["d"] = slug_to_id[r["d"]]
    stats = {"nodes": 0, "internal_links": 0, "links_to_course": 0, "links_to_topic": 0, "links_to_programme": 0, "unresolved_refs": 0}
    try:
        with drv.session() as s:
            s.run("CREATE INDEX design_node IF NOT EXISTS FOR (n:DesignNode) ON (n.run_id, n.uid)")
            s.run("CREATE CONSTRAINT programme_outcome_uid IF NOT EXISTS FOR (p:ProgrammeOutcome) REQUIRE p.uid IS UNIQUE")
            for prog in pedagogy().get("copo_programmes", []):   # shared programme outcome nodes (template text, verbatim)
                rows = [{"uid": x["id"], "programme": prog, "label": x.get("label"), "kind": x.get("kind"), "text": x["text"]}
                        for x in programme(prog)["po"]]
                s.run("UNWIND $rows AS r MERGE (p:ProgrammeOutcome {uid: r.uid}) SET p += r", rows=rows)
            delete_run(run_id, drv)
            s.run("CREATE (d:DesignRun) SET d = $p", p=summary)
            for label, rows in by_label.items():
                s.run(f"UNWIND $rows AS r CREATE (n:DesignNode:D_{label}) SET n = r", rows=rows)
                stats["nodes"] += len(rows)
            s.run("MATCH (d:DesignRun {run_id: $r}), (n:D_NewCourse {run_id: $r}) CREATE (d)-[:DESIGNS]->(n)", r=run_id)
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
