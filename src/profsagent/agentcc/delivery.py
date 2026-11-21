"""Lecture delivery for a `claude_code` run: the app's delivery jobs go to the Claude Code session, not to the API models.

The app's job runner (app/delivery_step.py) calls hand_off() and returns at once. The job stays "running" in the app
(app/delivery.py leaves a pending job's spinner on) while the session works, so other courses' jobs are not held up.
The session writes the delivery files where deliverables B and C write them (runs/<id>/delivery/..., same formats, so
the app shows them unchanged), then runs

    PYTHONPATH=src python -m profsagent.agentcc deliver <request>

which checks the files (finish()), marks the request done and the app's job done.

Request: runs/<id>/agentcc/NNN_D<job>.request.json
    {kind: "delivery", job: recommend|material|mix, lectures, args, choices, briefs, how_to, hidden, owner_pid: null}
owner_pid is null on purpose: the step process ends right after the handoff, and the request stays open until done.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from profsagent.agentcc import protocol as P
from profsagent.config import RUNS

JOBS = ("recommend", "material", "mix")

HOW_TO = """You are the delivery agent for this lecture (run marked agent: claude_code). Do the job yourself (search, read,
check, write) and write the files the app reads, in the formats deliverables B and C use:
- recommend: delivery/lectures/<lid>.json (components, resources for the wanted kinds, experts if a guest was asked
  for), delivery/mix/<lid>.json (valid LectureMix), optional delivery/guest_kits/<lid>.md, delivery/notebooklm/<lid>.md.
- material: delivery/material/<lid>/ material.json, deck.json (valid LectureDeck), slides.pptx, notes.md, quiz.json.
- mix: delivery/mix/<lid>.json (and delivery/quiz/<lid>.json when the plan is approved).
Never use or name the hidden courses or domains. When the files are written, run from the repo root:
  PYTHONPATH=src python -m profsagent.agentcc deliver <this request>"""


def _run_dir(rid: str, runs: Path | None) -> Path:
    return Path(runs or RUNS) / rid


def _rj(p: Path, default=None):
    try:
        return P.read_json(p) if p.exists() else default
    except Exception:  # noqa: BLE001
        return default


def run_cfg(rid: str, runs: Path | None = None) -> dict:
    d = _run_dir(rid, runs)
    cfg = (_rj(d / "state.json", {}) or {}).get("run_cfg") or {}
    if not cfg and (d / "input.yaml").exists():
        import yaml
        cfg = ((yaml.safe_load((d / "input.yaml").read_text(encoding="utf-8")) or {}).get("run") or {})
    return cfg


def is_agent(rid: str, runs: Path | None = None) -> bool:
    return P.is_agent_run(run_cfg(rid, runs))


def log(rid: str, msg: str, runs: Path | None = None) -> None:
    """A line in delivery.log, as delivery/pipeline.Log writes it (the lecture page shows lines that name the lecture)."""
    d = _run_dir(rid, runs) / "delivery"
    d.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with (d / "delivery.log").open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def lectures_of(job: str, args: dict) -> list[str]:
    return list(args.get("lectures") or []) if job == "recommend" else [args["lecture"]]


def _key(job: str, lectures: list[str], args: dict) -> str:
    return json.dumps([job, sorted(lectures), {k: v for k, v in sorted(args.items()) if k not in ("lectures", "lecture")}],
                      sort_keys=True, default=str)


def open_request(rid: str, key: str, runs: Path | None = None) -> Path | None:
    f = _run_dir(rid, runs) / P.FOLDER
    for p in sorted(f.glob("*.request.json")) if f.exists() else []:
        r = _rj(p, {}) or {}
        if r.get("kind") == "delivery" and r.get("key") == key and not P.sibling(p, "done.json").exists():
            return p
    return None


def hand_off(rid: str, job: str, args: dict, runs: Path | None = None) -> dict:
    """Write the request for one delivery job (or reuse the open one for the same job), log it, return at once."""
    lectures = lectures_of(job, args)
    key = _key(job, lectures, args)
    old = open_request(rid, key, runs)
    if old is not None:
        return {"request": old.name, "reused": True}
    d = _run_dir(rid, runs)
    survey = {}
    if (d / "delivery" / "survey.yaml").exists():
        import yaml
        survey = (yaml.safe_load((d / "delivery" / "survey.yaml").read_text(encoding="utf-8")) or {}).get("lectures") or {}
    briefs = {b.get("lecture_id"): b for b in (_rj(d / "delivery" / "briefs.json", []) or [])}
    cfg = run_cfg(rid, runs)
    req = P.next_request_path(d, f"D{job}")
    P.write_json(req, {
        "run_id": rid, "pid": f"D-{job}", "kind": "delivery", "job": job, "lectures": lectures, "args": args, "key": key,
        "choices": {lid: survey.get(lid) for lid in lectures}, "briefs": {lid: briefs.get(lid) for lid in lectures},
        "checks": ["delivery files"], "how_to": HOW_TO,
        "hidden": {"courses": cfg.get("exclude_courses") or [], "domains": cfg.get("blocklist") or []},
        "owner_pid": None, "created_at": time.time()})
    what = {"recommend": "resources, guest speakers and the lecture plan", "material": "the slides",
            "mix": f"the lecture plan ({args.get('action') or 'propose'})"}[job]
    for lid in lectures:
        log(rid, f"{lid}: {what} handed to Claude Code (request {req.name}); waiting for its answer", runs)
    return {"request": req.name, "reused": False}


# ------------------------------------------------------------------ the session's side: check the files, then mark done
def _hidden_named(texts: list[str], hidden: dict) -> list[str]:
    words = [w for w in (hidden.get("courses") or []) if w] + [w for w in (hidden.get("domains") or []) if w]
    blob = "\n".join(texts)
    return sorted({w for w in words if re.search(rf"(?<![A-Za-z0-9]){re.escape(w)}(?![A-Za-z0-9])", blob, re.I)})


def problems(rid: str, job: str, lectures: list[str], args: dict, hidden: dict | None = None,
             runs: Path | None = None) -> list[str]:
    """What is missing or malformed in the files this job must leave (empty = the app can show them)."""
    import yaml
    from profsagent.content.models import LectureDeck
    from profsagent.delivery.models import LectureMix
    dd = _run_dir(rid, runs) / "delivery"
    survey = ((yaml.safe_load((dd / "survey.yaml").read_text(encoding="utf-8")) or {}).get("lectures") or {}) \
        if (dd / "survey.yaml").exists() else {}
    out, texts = [], []

    def mix_ok(lid: str, need: bool) -> None:
        p = dd / "mix" / f"{lid}.json"
        if not p.exists():
            if need:
                out.append(f"{lid}: mix/{lid}.json is missing")
            return
        texts.append(p.read_text(encoding="utf-8"))
        try:
            LectureMix(**P.read_json(p))
        except Exception as e:  # noqa: BLE001
            out.append(f"{lid}: mix/{lid}.json is not a valid LectureMix: {str(e)[:300]}")

    for lid in lectures:
        ch = survey.get(lid) or {}
        if job == "recommend":
            p = dd / "lectures" / f"{lid}.json"
            if not p.exists():
                out.append(f"{lid}: lectures/{lid}.json is missing")
                continue
            texts.append(p.read_text(encoding="utf-8"))
            r = P.read_json(p)
            comps = r.get("components") or []
            if not comps:
                out.append(f"{lid}: no components")
            for c in comps:
                if not re.fullmatch(rf"{re.escape(lid)}\.C\d+", str(c.get("id", ""))):
                    out.append(f"{lid}: component id {c.get('id')!r} is not {lid}.C<n>")
            if r.get("partial"):
                out.append(f"{lid}: marked partial")
            if ch.get("assistance") == "yes":
                res = r.get("resources") or {}
                if not isinstance(res.get("items"), dict) or not isinstance(res.get("reserve"), dict):
                    out.append(f"{lid}: resources.items and resources.reserve must be dicts")
                for kind, want in (("video", "want_videos"), ("reading", "want_readings"), ("practice", "want_practice"),
                                   ("recorded_lecture", "want_recorded_lecture")):
                    if ch.get(want) == "yes" and not (res.get("items") or {}).get(kind):
                        out.append(f"{lid}: {kind} was asked for but resources.items.{kind} is empty")
                    for it in (res.get("items") or {}).get(kind) or []:
                        for k in ("url", "title", "rank", "total"):
                            if k not in it:
                                out.append(f"{lid}: a {kind} item has no {k}")
            if ch.get("guest_lecture") == "yes":
                ex = r.get("experts") or {}
                if not ex.get("experts") or not isinstance(ex.get("reserve"), list):
                    out.append(f"{lid}: a guest was asked for: experts.experts must be non-empty and experts.reserve a list")
                for person in ex.get("experts") or []:
                    for k in ("name", "kind", "rank", "total"):
                        if k not in person:
                            out.append(f"{lid}: an expert has no {k}")
            mix_ok(lid, need=False)
            for sub in ("guest_kits", "notebooklm"):
                q = dd / sub / f"{lid}.md"
                if q.exists():
                    texts.append(q.read_text(encoding="utf-8"))
        elif job == "material":
            m = dd / "material" / lid
            for f in ("material.json", "deck.json", "slides.pptx", "notes.md", "quiz.json"):
                if not (m / f).exists():
                    out.append(f"{lid}: material/{lid}/{f} is missing")
            if (m / "deck.json").exists():
                texts.append((m / "deck.json").read_text(encoding="utf-8"))
                try:
                    LectureDeck(**P.read_json(m / "deck.json"))
                except Exception as e:  # noqa: BLE001
                    out.append(f"{lid}: deck.json is not a valid LectureDeck: {str(e)[:300]}")
            if (m / "material.json").exists():
                mj = P.read_json(m / "material.json")
                for k in ("topic", "status", "slides", "generated_at", "sources"):
                    if k not in mj:
                        out.append(f"{lid}: material.json has no {k}")
            if (m / "notes.md").exists():
                texts.append((m / "notes.md").read_text(encoding="utf-8"))
        elif job == "mix":
            mix_ok(lid, need=True)
            if args.get("action") == "approve":
                p = dd / "mix" / f"{lid}.json"
                if p.exists() and P.read_json(p).get("status") != "approved":
                    out.append(f"{lid}: the plan was to be approved but its status is not 'approved'")
                if not (dd / "quiz" / f"{lid}.json").exists():
                    out.append(f"{lid}: quiz/{lid}.json is missing (made when the plan is approved)")
    named = _hidden_named(texts, hidden or {})
    if named:
        out.append("names a hidden course or domain: " + ", ".join(named))
    return out


def _set_job(rid: str, job: str, lectures: list[str], runs: Path | None = None, **kw) -> None:
    """The same entry app/delivery.py's DeliveryManager._set writes, so the app's spinner turns into the result."""
    p = _run_dir(rid, runs) / "delivery" / "app_jobs.json"
    j = _rj(p, None) or {"lectures": {}}
    j.setdefault("lectures", {})
    for lid in lectures:
        sect = j["lectures"] if job == "recommend" else j.setdefault("material" if job == "material" else "mix", {})
        sect[lid] = {**(sect.get(lid) or {}), **kw, "at": time.time()}
    P.write_json(p, j)


def finish(req: Path, runs: Path | None = None) -> list[str]:
    """Check the files of a handed-off job. Clean: done.json + app job done. Else: check.json listing the problems."""
    req = Path(req)
    r = P.read_json(req)
    rid, job, lectures, args = r["run_id"], r["job"], r["lectures"], r.get("args") or {}
    runs = runs or req.parents[2]
    probs = problems(rid, job, lectures, args, r.get("hidden"), runs)
    if probs:
        P.write_json(P.sibling(req, "check.json"), {"for": "answer", "rejected": True, "at": time.time(), "problems": probs})
        return probs
    secs = round(time.time() - float(r.get("created_at") or time.time()), 1)
    P.write_json(P.sibling(req, "done.json"), {"accepted_at": time.time(), "seconds": secs, "job": job, "lectures": lectures})
    _set_job(rid, job, lectures, runs, state="done", error=None)
    what = {"recommend": "resources, guest speakers and lecture plan", "material": "slides", "mix": "lecture plan"}[job]
    for lid in lectures:
        log(rid, f"{lid}: {what} delivered by Claude Code after {secs:.0f}s (request {req.name})", runs)
    return []
