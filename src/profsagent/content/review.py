"""The professor's decision on each generated deck, in the same shape as C's review (delivery/review.py).

material/review.yaml lists every generated lecture with `decision: pending`. The professor sets
    approve   the slides are final as they are now in slides.pptx (edits made in PowerPoint included)
    redo      generate again; the reason is passed to B1 as the professor's instructions (one AI call, on request)
    reject    do not use generated slides for this lecture
(a reason is required for redo and reject) and runs `run_content.py review --apply`. The decision is written to the
lecture's material.json as `status` (draft | approved | redo | rejected), which is what the UI shows; an approved deck is
never overwritten by a new generation unless forced.
"""
from __future__ import annotations

import yaml

from profsagent.delivery.common import now, out_dir, read_json, write_json

DECISIONS = ("pending", "approve", "redo", "reject")
STATUS = {"approve": "approved", "redo": "redo", "reject": "rejected"}
HEADER = ("# Decide each lecture's generated slides: decision: approve | redo | reject   (reason: required for redo / reject)\n"
          "#   approve  the slides are final as they are now in slides.pptx (your PowerPoint edits included)\n"
          "#   redo     generate them again; write in `reason` what to change (one AI call when you run generate --redo)\n"
          "#   reject   do not use generated slides for this lecture\n"
          "# Then run: python scripts/run_content.py review --run-id <id> --apply\n")


def _path(run_id: str):
    return out_dir(run_id) / "material" / "review.yaml"


def manifests(run_id: str) -> dict[str, dict]:
    root = out_dir(run_id) / "material"
    return {p.parent.name: read_json(p) for p in sorted(root.glob("*/material.json"))} if root.exists() else {}


def write(run_id: str) -> dict:
    """review.yaml for every generated lecture; decisions already written are kept."""
    p = _path(run_id)
    old = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("lectures", {}) if p.exists() else {}
    rows = {}
    for lid, m in manifests(run_id).items():
        o = old.get(lid) or {}
        rows[lid] = {"topic": m["topic"], "slides": m["slides"], "errors": m["errors"], "warnings": m["warnings"],
                     "status": m.get("status", "draft"), "decision": o.get("decision") or "pending", "reason": o.get("reason") or ""}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(HEADER + yaml.safe_dump({"lectures": rows}, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    return rows


def apply(run_id: str) -> dict:
    """Write each decision to its lecture's material.json. Returns counts and the refused rows (no reason given)."""
    p = _path(run_id)
    rows = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("lectures", {}) if p.exists() else {}
    stats = {"approved": 0, "redo": 0, "rejected": 0, "pending": 0, "refused": []}
    for lid, row in rows.items():
        dec = str(row.get("decision") or "pending").lower()
        mp = out_dir(run_id) / "material" / lid / "material.json"
        m = read_json(mp)
        if m is None or dec not in DECISIONS:
            stats["refused"].append({"lecture": lid, "why": "no generated material" if m is None else f"unknown decision {dec!r}"})
            continue
        if dec == "pending":
            stats["pending"] += 1
            continue
        reason = str(row.get("reason") or "").strip()
        if dec in ("redo", "reject") and not reason:
            stats["refused"].append({"lecture": lid, "why": f"{dec} needs a reason"})
            continue
        m["status"] = STATUS[dec]
        m["review"] = {"decision": dec, "reason": reason, "at": now()}
        m.setdefault("review_history", []).append(m["review"])
        write_json(mp, m)
        stats[STATUS[dec]] += 1
    write(run_id)                                   # refresh the status column
    return stats


def redo_requests(run_id: str) -> dict[str, str]:
    """Lecture -> the professor's instructions, for every deck waiting to be generated again."""
    return {lid: m["review"]["reason"] for lid, m in manifests(run_id).items() if m.get("status") == "redo"}
