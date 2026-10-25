"""The professor's decisions, feedback and link health (plan §7).

review.yaml lists every proposed item per lecture with `decision: pending`. The professor sets
  approve | reject | replace   (+ `reason`, required for reject and replace)
and runs `run_delivery.py review --apply`: approved items are frozen, rejected ones dropped, and `replace` swaps in
the next-ranked reserve item of the same kind (which then appears as pending). Decisions survive re-rendering.
feedback.yaml collects 1–5 ratings for approved items; per-source averages adjust future rankings.
"""
from __future__ import annotations

import yaml

from profsagent.config import DATA
from profsagent.delivery.common import now, out_dir, read_json, write_json
from profsagent.delivery.sources import url_alive

FEEDBACK = DATA / "delivery_feedback.json"


def _key(item: dict) -> str:
    return item.get("url") or item.get("name") or item.get("title")


def sync_review_file(run_id: str, lecs: dict) -> None:
    p = out_dir(run_id) / "review.yaml"
    old = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
    prev = {(lid, it["key"]): it for lid, kinds in (old.get("lectures") or {}).items() for items in kinds.values() for it in items}
    out = {}
    for lid, r in lecs.items():
        kinds = {}
        for kind, items in ((r.get("resources") or {}).get("items") or {}).items():
            kinds[kind] = [_row(lid, c, prev) for c in items]
        if r.get("experts"):
            kinds["experts"] = [_row(lid, e, prev) for e in r["experts"]["experts"]]
        out[lid] = kinds
    hdr = ("# Decide each item: decision: approve | reject | replace   (reason: required for reject / replace)\n"
           "# Then run: python scripts/run_delivery.py review --run-id <id> --apply\n")
    p.write_text(hdr + yaml.safe_dump({"lectures": out}, sort_keys=False, allow_unicode=True, width=140), encoding="utf-8")


def _row(lid: str, item: dict, prev: dict) -> dict:
    k = _key(item)
    old = prev.get((lid, k), {})
    return {"key": k, "rank": item.get("rank"), "title": item.get("title") or item.get("name"),
            "decision": old.get("decision") or item.get("status_decision") or "pending", "reason": old.get("reason") or ""}


def apply(run_id: str) -> dict:
    d = out_dir(run_id)
    rv = yaml.safe_load((d / "review.yaml").read_text(encoding="utf-8")) or {}
    stats = {"approved": 0, "rejected": 0, "replaced": 0, "pending": 0, "refused": []}
    for lid, kinds in (rv.get("lectures") or {}).items():
        p = d / "lectures" / f"{lid}.json"
        lec = read_json(p)
        if not lec:
            continue
        for kind, rows in kinds.items():
            if kind == "experts":
                block, reserve = lec["experts"]["experts"], lec["experts"]["reserve"]
            else:
                block, reserve = lec["resources"]["items"].get(kind, []), lec["resources"]["reserve"].get(kind, [])
            for row in rows:
                dec = (row.get("decision") or "pending").lower()
                item = next((x for x in block if _key(x) == row["key"]), None)
                if item is None:
                    continue
                if dec in ("reject", "replace") and not (row.get("reason") or "").strip():
                    stats["refused"].append(f"{lid} {row['title'][:40]}: a reason is required to {dec}")
                    continue
                if dec == "approve":
                    item["status_decision"], item["approved_at"] = "approve", now()
                    stats["approved"] += 1
                elif dec in ("reject", "replace"):
                    item["status_decision"], item["reason"] = dec, row["reason"]
                    block.remove(item)
                    lec.setdefault("decisions", []).append({"item": _key(item), "decision": dec, "reason": row["reason"], "at": now()})
                    stats["rejected" if dec == "reject" else "replaced"] += 1
                    if dec == "replace" and reserve:
                        nxt = reserve.pop(0)
                        nxt["rank"] = item.get("rank")
                        block.append(nxt)
                        block.sort(key=lambda x: x.get("rank") or 99)
                else:
                    stats["pending"] += 1
        write_json(p, lec)
    from profsagent.delivery.pipeline import render
    render(run_id)
    return stats


def record_feedback(run_id: str) -> dict:
    """feedback.yaml: {lectures: {lid: [{key, rating 1-5, comment}]}} → per-source running averages."""
    d = out_dir(run_id)
    p = d / "feedback.yaml"
    if not p.exists():
        lecs = {q.stem: read_json(q) for q in (d / "lectures").glob("*.json")}
        tmpl = {"lectures": {lid: [{"key": _key(c), "title": c.get("title"), "rating": None, "comment": ""}
                                   for items in ((r.get("resources") or {}).get("items") or {}).values() for c in items
                                   if c.get("status_decision") == "approve"] for lid, r in lecs.items()}}
        p.write_text("# Rate approved items 1-5 after use (students or professor), then run feedback again.\n" +
                     yaml.safe_dump(tmpl, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return {"created": str(p)}
    fb = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    agg = read_json(FEEDBACK, {})
    n = 0
    for lid, rows in (fb.get("lectures") or {}).items():
        lec = read_json(d / "lectures" / f"{lid}.json") or {}
        items = {(_key(c)): c for items in ((lec.get("resources") or {}).get("items") or {}).values() for c in items}
        for row in rows:
            if not row.get("rating"):
                continue
            src = (items.get(row["key"]) or {}).get("source") or "unknown"
            a = agg.setdefault(src, {"n": 0, "sum": 0})
            a["n"] += 1
            a["sum"] += int(row["rating"])
            n += 1
    write_json(FEEDBACK, agg)
    return {"ratings_recorded": n, "sources": len(agg)}


def source_multiplier(source: str | None) -> float:
    """0.6–1.2 from professors' and students' average rating of a source (neutral without ratings)."""
    a = read_json(FEEDBACK, {}).get(source or "")
    if not a or a["n"] < 3:
        return 1.0
    return max(0.6, min(1.2, 1.0 + 0.1 * (a["sum"] / a["n"] - 3)))


def health(run_id: str) -> list[dict]:
    """Re-check every approved link; report the dead ones (with a replacement available from the reserve)."""
    d = out_dir(run_id)
    dead = []
    for p in (d / "lectures").glob("*.json"):
        lec = read_json(p)
        for kind, items in ((lec.get("resources") or {}).get("items") or {}).items():
            for c in items:
                if c.get("status_decision") == "approve" and c.get("url"):
                    ok, code = url_alive(c["url"])
                    if not ok:
                        dead.append({"lecture": p.stem, "kind": kind, "title": c["title"], "url": c["url"], "status": code,
                                     "replacement_available": bool(lec["resources"]["reserve"].get(kind))})
    write_json(d / "health.json", {"checked_at": now(), "dead": dead})
    return dead
