"""Delivery records in Neo4j, next to the course's design graph (architecture §8.6: Recommendation, Feedback nodes).

  (:Delivery:LectureBrief {run_id, lecture_id, novel, summary})-[:BRIEF_OF]->(:D_Lecture)
  (:Delivery:CoverageDecision {choices, resources, guest, attachments, attach_tasks, confidence, note})-[:DECISION_FOR]->(:D_Lecture)
  (:Delivery:Recommendation {kind, title, url, source, tier, rank, total, status, rationale, review})-[:FOR_LECTURE]->(:D_Lecture)
        -[:COVERS {covered, sim, start, end}]->(:D_CourseTopic | :D_LO)
  (:Delivery:Expert {name, kind, affiliation, country, ...})-[:CANDIDATE_FOR {rank, total, fit, why, format, status}]->(:D_Lecture)
        -[:EVIDENCED_BY]->(:Delivery:Evidence {kind, title, year, url})
Reloading a run replaces its delivery nodes. Design nodes are matched by run_id + local_id (W02.L1, M1.T2, CO1.LO1).
"""
from __future__ import annotations

import json

from profsagent.delivery import survey as sv
from profsagent.delivery.common import out_dir, read_json


def _j(v):
    return json.dumps(v, ensure_ascii=False, default=str) if isinstance(v, (dict, list)) else v


def write(run_id: str) -> dict:
    from profsagent.design.neo4j_sync import driver
    d = out_dir(run_id)
    briefs = read_json(d / "briefs.json", [])
    s = sv.load(run_id) or {}
    lecs = {p.stem: read_json(p) for p in (d / "lectures").glob("*.json")} if (d / "lectures").exists() else {}
    stats = {"briefs": 0, "decisions": 0, "recommendations": 0, "experts": 0, "linked_lectures": 0}
    drv = driver()
    try:
        with drv.session() as ses:
            ses.run("MATCH (n:Delivery {run_id: $r}) DETACH DELETE n", r=run_id)
            stats["linked_lectures"] = ses.run("MATCH (l:D_Lecture {run_id: $r}) RETURN count(l) AS n", r=run_id).single()["n"]
            ses.run("""UNWIND $rows AS r CREATE (b:Delivery:LectureBrief) SET b = r, b.name = r.lecture_id + ' brief'
                       WITH b, r OPTIONAL MATCH (l:D_Lecture {run_id: r.run_id, local_id: r.lecture_id})
                       FOREACH (_ IN CASE WHEN l IS NULL THEN [] ELSE [1] END | CREATE (b)-[:BRIEF_OF]->(l))""",
                    rows=[{"run_id": run_id, "lecture_id": b["lecture_id"], "topic": b["topic"], "week": b["week"], "novel": b["novel"],
                           "summary": b["summary"]} for b in briefs])
            stats["briefs"] = len(briefs)
            dec = [{"run_id": run_id, "lecture_id": lid, "choices": t["choices"], "resources": t["resources"], "guest": t["guest"],
                    "attachments": t["attachments"], "attach_tasks": t["attach_tasks"],
                    "confidence": t["confidence"], "note": t["note"]} for lid, t in sv.tasks(s).items()]
            ses.run("""UNWIND $rows AS r CREATE (c:Delivery:CoverageDecision) SET c = r, c.name = r.lecture_id + ' decision'
                       WITH c, r OPTIONAL MATCH (l:D_Lecture {run_id: r.run_id, local_id: r.lecture_id})
                       FOREACH (_ IN CASE WHEN l IS NULL THEN [] ELSE [1] END | CREATE (c)-[:DECISION_FOR]->(l))""", rows=dec)
            stats["decisions"] = len(dec)
            recs, covers, experts, evid = [], [], [], []
            for lid, r in lecs.items():
                for kind, items in ((r.get("resources") or {}).get("items") or {}).items():
                    for c in items:
                        rid = f"{run_id}|{lid}|{c.get('url')}"
                        recs.append({"rid": rid, "run_id": run_id, "lecture_id": lid, "kind": kind, "title": c.get("title"), "url": c.get("url"),
                                     "source": c.get("source"), "tier": c.get("tier"), "rank": c.get("rank"), "total": c.get("total"),
                                     "status": c.get("status_decision") or "proposed", "rationale": c.get("rationale"),
                                     "review": (c.get("review") or {}).get("review"), "use_as": (c.get("review") or {}).get("use_as"),
                                     "scores": _j(c.get("scores")), "licence": c.get("licence"), "duration_s": c.get("duration_s"),
                                     "name": f"{kind}: {(c.get('title') or '')[:50]}"})
                        for tid, v in (c.get("coverage") or {}).get("per_target", {}).items():
                            seg = (v.get("segments") or [{}])[0]
                            covers.append({"rid": rid, "run_id": run_id, "target": tid, "covered": v["covered"], "sim": v["sim"],
                                           "start": seg.get("start"), "end": seg.get("end")})
                for e in ((r.get("experts") or {}).get("experts") or []):
                    xid = f"{run_id}|{e['name']}"
                    experts.append({"xid": xid, "run_id": run_id, "lecture_id": lid, "name": e["name"], "kind": e["kind"],
                                    "affiliation": e.get("affiliation"), "country": e.get("country"), "role": e.get("role"),
                                    "links": _j(e.get("links")), "verified_identity": e.get("verified_identity"),
                                    "rank": e.get("rank"), "total": e.get("total"), "fit": e.get("fit"), "why": e.get("why"),
                                    "format": e.get("suggested_format"), "status": e.get("status_decision") or "proposed"})
                    evid += [{"xid": xid, "run_id": run_id, **{k: ev.get(k) for k in ("kind", "title", "year", "url")}} for ev in e.get("evidence", [])]
            ses.run("""UNWIND $rows AS r CREATE (m:Delivery:Recommendation) SET m = r
                       WITH m, r OPTIONAL MATCH (l:D_Lecture {run_id: r.run_id, local_id: r.lecture_id})
                       FOREACH (_ IN CASE WHEN l IS NULL THEN [] ELSE [1] END | CREATE (m)-[:FOR_LECTURE {rank: r.rank, status: r.status}]->(l))""", rows=recs)
            ses.run("""UNWIND $rows AS r MATCH (m:Recommendation {rid: r.rid})
                       MATCH (t:DesignNode {run_id: r.run_id, local_id: r.target})
                       CREATE (m)-[:COVERS {covered: r.covered, sim: r.sim, start: r.start, end: r.end}]->(t)""", rows=covers)
            ses.run("""UNWIND $rows AS r MERGE (x:Delivery:Expert {xid: r.xid})
                       SET x.run_id = r.run_id, x.name = r.name, x.kind = r.kind, x.affiliation = r.affiliation, x.country = r.country,
                           x.role = r.role, x.links = r.links, x.verified_identity = r.verified_identity
                       WITH x, r OPTIONAL MATCH (l:D_Lecture {run_id: r.run_id, local_id: r.lecture_id})
                       FOREACH (_ IN CASE WHEN l IS NULL THEN [] ELSE [1] END |
                         CREATE (x)-[:CANDIDATE_FOR {rank: r.rank, total: r.total, fit: r.fit, why: r.why, format: r.format, status: r.status}]->(l))""",
                    rows=experts)
            ses.run("""UNWIND $rows AS r MATCH (x:Expert {xid: r.xid})
                       CREATE (x)-[:EVIDENCED_BY]->(e:Delivery:Evidence {run_id: r.run_id, kind: r.kind, title: r.title, year: r.year, url: r.url,
                                                                         name: r.kind + ': ' + left(coalesce(r.title, ''), 40)})""", rows=evid)
            stats["recommendations"], stats["experts"] = len(recs), len({e["xid"] for e in experts})
    finally:
        drv.close()
    return stats
