"""Phase 2, lecture delivery, in the app: the screens of docs/04_phase2_UI_integration_guide.md over Vihan's
deliverable C backend (profsagent.delivery). His files under runs/<id>/delivery/ stay the source of truth
(briefs.json, survey.yaml, lectures/*.json, review.yaml, guest_kits/, health.json, feedback.yaml). The app adds:

  app_jobs.json          background work per lecture (queued / running / done / error) and the link check
  app_own_links.json     links the professor pinned (shown as approved; C has no store for them yet, guide S5)
  app_actions.json       what the professor approved / replaced / rejected, with titles, for display
  app_health_dismissed.json   link-health alerts the professor dismissed
  app_feedback_log.yaml  every rating, each sent to review.record_feedback exactly once
  attachments/<lecture>/ files the professor attached for B (Parth's material generator, not connected yet)

Only the app's own courses (runs/app-*) are changed; Vihan's committed example run is copied, never edited.
"""
from __future__ import annotations

import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import yaml

from profsagent.config import ROOT, RUNS

CHOICES = ["own_material", "attach_material", "generate_material", "assistance", "guest_lecture"]
WANTS = ["want_videos", "want_readings", "want_practice", "want_recorded_lecture", "want_clips"]
C_KEYS = ["assistance", "guest_lecture"] + WANTS          # what C's search depends on (a change re-runs it)
ATTACH_TASKS = ["slides", "summary", "quiz", "gap_check", "enrich"]
KEEP = CHOICES + ["attachments", "attach_tasks"] + WANTS + ["confidence", "note"]
KINDS = ["video", "recorded_lecture", "reading", "practice"]
BLOOM = {1: "remember", 2: "understand", 3: "apply", 4: "analyse", 5: "evaluate", 6: "create"}
EXAMPLE_SOURCE = "cs601-02"      # Vihan's run with real resource and speaker results (W01.L1, W01.L2, W02.L1)


def _d(rid: str, runs: Path | None = None) -> Path:
    return (runs or RUNS) / rid / "delivery"      # RUNS read at call time (tests point it elsewhere)


def _rj(p: Path, default=None):
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
    except (OSError, ValueError):
        return default


def _wj(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    os.replace(tmp, p)


def _yes(v) -> bool:
    return str(v).lower() in ("yes", "y", "true", "1")


# ------------------------------------------------------------------ which courses can be delivered
def approved(run_dir: Path) -> bool:
    st = _rj(run_dir / "state.json") or {}
    return any(a.get("gate") == "gate3_proposal" and a.get("decision") == "approve" for a in st.get("approvals", []))


def courses(runs: Path | None = None) -> list[dict]:
    runs = runs or RUNS
    out = []
    for d in sorted(runs.glob("app-*")):
        m = _rj(d / "app.json") or {}
        if m.get("status") != "done" or not approved(d):
            continue
        sv = (yaml.safe_load((d / "delivery" / "survey.yaml").read_text(encoding="utf-8")) or {}) if (d / "delivery" / "survey.yaml").exists() else {}
        lecs = (sv.get("lectures") or {})
        code = (d / "course_code.txt").read_text().strip() if (d / "course_code.txt").exists() else None
        out.append({"run_id": d.name, "title": m.get("title"), "code": code, "created_at": m.get("created_at"), "example": bool(m.get("example_of")),
                    "lectures": len(lecs) or None, "decided": sum(1 for a in lecs.values() if any(a.get(k) is not None for k in CHOICES)),
                    "with_results": len(list((d / "delivery" / "lectures").glob("*.json"))) if (d / "delivery" / "lectures").exists() else 0})
    return sorted(out, key=lambda c: c.get("created_at") or 0, reverse=True)


def copy_example(runs: Path | None = None, source: str = EXAMPLE_SOURCE) -> str:
    """A private copy of Vihan's CS-601 run (with its real results for three lectures) to try delivery on."""
    from profsagent.app.runner import new_run_id, write_meta
    runs = runs or RUNS
    src = runs / source
    if not (src / "state.json").exists():
        raise FileNotFoundError(f"runs/{source} is not here")
    rid = new_run_id("cs601 example", runs)
    shutil.copytree(src, runs / rid, ignore=shutil.ignore_patterns("checkpoint.sqlite*", "*.tmp"))
    st = _rj(src / "state.json") or {}
    write_meta(runs / rid, {"run_id": rid, "title": (st.get("cco_compact") or {}).get("course_name", "CS-601") + " (CS-601 example)",
                            "by": "Professor", "created_at": time.time(), "status": "done", "phase": "design", "gate": "gate3_proposal",
                            "example_of": source, "history": [{"at": time.time(), "event": f"copied from runs/{source} to try lecture delivery"}]})
    return rid


# ------------------------------------------------------------------ data for the screens (same shapes as the prototype)
def _fill(text: str) -> str:
    return (text or "").replace("{n} of {m}", "most")     # a placeholder C's brief writer sometimes leaves in LO text


def _lecture(b: dict) -> dict:
    return {
        "id": b["lecture_id"], "week": b["week"], "slot": b.get("slot"), "hours": b.get("hours"), "topic": b["topic"], "module": b.get("module"),
        "continues": bool(b.get("continues")), "novel": bool(b.get("novel")), "match": b.get("iiitd_match") or None, "summary": b.get("summary"),
        "los": [{"id": x["id"], "text": _fill(x["statement"]), "bloom": BLOOM.get(x.get("bloom_level"), ""), "co": x.get("co")} for x in b.get("learning_outcomes", [])],
        "cos": [{"id": x["id"], "text": x["statement"]} for x in b.get("course_outcomes", [])],
        "builds_on": b.get("builds_on", []), "prereq": b.get("prerequisite_courses", []), "leads_to": b.get("leads_to", []),
        "assessed": b.get("assessed_in", []), "labs": b.get("labs", []), "hands_on": b.get("hands_on"), "outside": b.get("outside_load_hours"),
    }


def _resource(c: dict, topic_id: str | None) -> dict:
    cov = []
    for tgt, v in ((c.get("coverage") or {}).get("per_target") or {}).items():
        if v.get("covered"):
            cov.append({"label": "the topic" if tgt == topic_id else "outcome " + tgt,
                        "segs": [[round(s["start"]), round(s["end"])] for s in v.get("segments", [])]})
    rv = c.get("review") or {}
    return {
        "key": c.get("url") or c.get("title"), "url": c.get("url"), "title": c.get("title"), "source": c.get("source"), "tier": c.get("tier"),
        "dur": c.get("duration_s"), "year": (c.get("published") or str(c.get("year") or ""))[:4] or None,
        "captions": c.get("captions"), "licence": c.get("licence"), "embeddable": c.get("embeddable", True),
        "yt": c.get("id") if "youtube.com" in (c.get("url") or "") else None,
        "total": c.get("total"), "scores": c.get("scores"), "rationale": c.get("rationale"), "rank": c.get("rank"),
        "warnings": [f["message"] for f in c.get("findings", []) if f.get("severity") == "warning"],
        "review": {"text": rv.get("review"), "use_as": rv.get("use_as"), "issues": rv.get("issues", [])},
        "cover": cov, "evidence": (c.get("coverage") or {}).get("evidence"), "approved": c.get("status_decision") == "approve",
    }


def _expert(x: dict) -> dict:
    return {
        "key": x["name"], "name": x["name"], "kind": x.get("kind"), "role": x.get("role"), "affiliation": x.get("affiliation"), "country": x.get("country"),
        "links": x.get("links", {}), "total": x.get("total"), "scores": x.get("scores"), "fit": x.get("fit"), "why": x.get("why"), "rank": x.get("rank"),
        "evidence": [{"kind": e.get("kind"), "title": e.get("title"), "year": e.get("year"), "url": e.get("url"), "venue": e.get("venue")} for e in x.get("evidence", [])[:3]],
        "format": x.get("suggested_format"), "verified": x.get("verified_identity"), "approved": x.get("status_decision") == "approve",
        "warnings": [f["message"] for f in x.get("findings", []) if f.get("severity") == "warning"] + list(x.get("concerns") or []),
    }


def _result(lec: dict, topic_id: str | None) -> dict:
    r = lec.get("resources") or {}
    e = lec.get("experts")
    out = {"generated_at": lec.get("generated_at"), "continuation_of": lec.get("continuation_of"), "note": r.get("note"), "counts": r.get("counts"),
           "has_resources": bool(lec.get("resources")),
           "items": {k: [_resource(c, topic_id) for c in v] for k, v in (r.get("items") or {}).items()},
           "reserve": {k: [_resource(c, topic_id) for c in v] for k, v in (r.get("reserve") or {}).items()},
           "rejected": [{"title": x.get("title"), "url": x.get("url"), "why": x.get("why", [])} for x in r.get("rejected", [])],
           "clips": r.get("clips", []), "experts": None}
    if e and e.get("same_as"):
        out["experts"] = {"same_as": e["same_as"]}
    elif e:
        out["experts"] = {"experts": [_expert(x) for x in e.get("experts", [])], "reserve": [_expert(x) for x in e.get("reserve", [])],
                          "rejected": [{"name": x["name"], "why": x.get("why", [])} for x in e.get("rejected", [])], "counts": e.get("counts")}
    return out


def ensure(rid: str) -> None:
    """Briefs (no AI, fast) and an empty survey the first time a course is opened for delivery."""
    from profsagent.delivery import pipeline, survey as sv
    d = _d(rid)
    if not (d / "briefs.json").exists():
        pipeline.make_briefs(rid)
    if sv.load(rid) is None:
        sv.init(rid, _rj(d / "briefs.json", []))


def view(rid: str, runs: Path | None = None) -> dict:
    from profsagent.app.runner import read_meta
    from profsagent.delivery import survey as sv
    runs = runs or RUNS
    ensure(rid)
    d = _d(rid, runs)
    briefs = _rj(d / "briefs.json", [])
    topic_of = {b["lecture_id"]: b.get("topic_id") for b in briefs}
    s = (sv.load(rid) or {}).get("lectures") or {}
    survey = {}
    for b in briefs:
        a = sv._migrate(s.get(b["lecture_id"]) or {})
        decided = any(a.get(k) is not None for k in CHOICES)
        survey[b["lecture_id"]] = ({k: a.get(k) for k in KEEP} if decided else None)
    results = {p.stem: _result(_rj(p, {}), topic_of.get(p.stem)) for p in sorted((d / "lectures").glob("*.json"))} if (d / "lectures").exists() else {}
    kits = sorted(p.stem for p in (d / "guest_kits").glob("*.md")) if (d / "guest_kits").exists() else []
    logs: dict[str, list[str]] = {}
    if (d / "delivery.log").exists():
        for line in (d / "delivery.log").read_text(encoding="utf-8", errors="replace").splitlines()[-400:]:
            m = re.search(r"\b(W\d\d\.L\d)\b", line)
            if m:
                logs.setdefault(m.group(1), []).append(line[:200])
    health = (_rj(d / "health.json") or {})
    dismissed = set(_rj(d / "app_health_dismissed.json", []))
    meta = read_meta(runs / rid)
    st = _rj(runs / rid / "state.json") or {}
    return {
        "run": {"id": rid, "course": (st.get("cco_compact") or {}).get("course_name") or meta.get("title"), "title": meta.get("title"),
                "code": (runs / rid / "course_code.txt").read_text().strip() if (runs / rid / "course_code.txt").exists() else None,
                "example_of": meta.get("example_of")},
        "lectures": [_lecture(b) for b in briefs], "survey": survey, "results": results, "kits": kits,
        "log": {k: v[-8:] for k, v in logs.items()}, "jobs": _rj(d / "app_jobs.json", {"lectures": {}}),
        "own": _rj(d / "app_own_links.json", {}), "actions": _rj(d / "app_actions.json", {}),
        "ratings": _ratings(d), "health": {"checked_at": health.get("checked_at"),
                                           "dead": [x for x in health.get("dead", []) if x.get("url") not in dismissed]},
        "keys": {"youtube": bool(os.environ.get("YOUTUBE_API_KEY")), "openalex": bool(os.environ.get("OPENALEX_API_KEY")),
                 "tavily": bool(os.environ.get("TAVILY_API_KEY"))},
        "material_connected": False,      # B (Parth): attach / generate calls are not defined yet (guide §4)
    }


# ------------------------------------------------------------------ S2: choices
def validate_choices(a: dict) -> dict[str, str]:
    e = {}
    if not any(a.get(k) == "yes" for k in CHOICES):
        e["none"] = "Pick at least one way to deliver this lecture."
    if a.get("attach_material") == "yes" and not a.get("attachments"):
        e["attach"] = "Add at least one file or link."
    if a.get("attach_material") == "yes" and not a.get("attach_tasks"):
        e["tasks"] = "Pick at least one thing to do with your material."
    if a.get("assistance") == "yes" and not any(a.get(w) == "yes" for w in WANTS):
        e["wants"] = "Pick at least one kind of resource."
    if a.get("confidence") not in (None, 1, 2, 3, 4, 5):
        e["confidence"] = "Confidence goes from 1 to 5."
    return e


def _clean(a: dict) -> dict:
    out = {}
    for k in CHOICES:
        out[k] = "yes" if a.get(k) == "yes" else "no"
    for k in WANTS:
        out[k] = ("yes" if a.get(k) == "yes" else "no") if out["assistance"] == "yes" else (a.get(k) if a.get(k) in ("yes", "no") else "no")
    out["attachments"] = [str(x)[:500] for x in (a.get("attachments") or [])][:20] if out["attach_material"] == "yes" else []
    out["attach_tasks"] = [t for t in (a.get("attach_tasks") or []) if t in ATTACH_TASKS] if out["attach_material"] == "yes" else []
    out["confidence"] = a.get("confidence") if a.get("confidence") in (1, 2, 3, 4, 5) else None
    out["note"] = str(a.get("note") or "")[:1000]
    return out


def save_choices(rid: str, lid: str, answers: dict) -> dict:
    """Write one lecture's answers to survey.yaml. Returns {errors} or {saved, start_c, refresh}: C's search starts only
    when resources or a guest were asked for, and re-runs (refresh) only when what C searches for has changed."""
    from profsagent.delivery import survey as sv
    errs = validate_choices(answers)
    if errs:
        return {"errors": errs}
    ensure(rid)
    s = sv.load(rid)
    if lid not in (s.get("lectures") or {}):
        return {"errors": {"none": "Unknown lecture"}}
    old = sv._migrate(s["lectures"][lid])
    new = _clean(answers)
    has_results = (_d(rid) / "lectures" / f"{lid}.json").exists()
    changed_c = any(str(old.get(k)) != str(new.get(k)) for k in C_KEYS)
    s["lectures"][lid].update(new)
    sv.save(rid, s)
    wants_c = _yes(new["assistance"]) or _yes(new["guest_lecture"])
    jobs = _rj(_d(rid) / "app_jobs.json", {"lectures": {}})
    never_ran = (jobs["lectures"].get(lid) or {}).get("state") is None and not has_results
    start = wants_c and (changed_c or never_ran or not has_results)
    return {"saved": True, "start_c": start, "refresh": start and has_results}


def bulk(rid: str, lid: str, scope: str) -> dict:
    """Copy one lecture's saved choices to the lectures of its week or module that have no choices yet."""
    from profsagent.delivery import survey as sv
    s = sv.load(rid)
    briefs = {b["lecture_id"]: b for b in _rj(_d(rid) / "briefs.json", [])}
    src = sv._migrate(s["lectures"][lid])
    if not any(src.get(k) is not None for k in CHOICES):
        return {"applied": [], "problem": "Save this lecture's choices first."}
    key = "week" if scope == "week" else "module"
    done = []
    for other, a in s["lectures"].items():
        if other == lid or briefs.get(other, {}).get(key) != briefs[lid].get(key) or any(sv._migrate(a).get(k) is not None for k in CHOICES):
            continue
        a.update({k: src.get(k) for k in KEEP if k not in ("attachments", "note")} | {"attachments": [], "note": ""})
        if a.get("attach_material") == "yes":
            a["attach_material"], a["attach_tasks"] = "no", []      # files belong to one lecture: not copied
        done.append(other)
    sv.save(rid, s)
    return {"applied": done}


def same_as_previous(rid: str, lid: str) -> dict:
    from profsagent.delivery import survey as sv
    s = sv.load(rid)
    ids = list((s.get("lectures") or {}).keys())
    i = ids.index(lid)
    if i == 0:
        return {"problem": "This is the first lecture."}
    prev = sv._migrate(s["lectures"][ids[i - 1]])
    if not any(prev.get(k) is not None for k in CHOICES):
        return {"problem": "The previous lecture has no saved choices yet."}
    return {"answers": {k: prev.get(k) for k in KEEP if k not in ("attachments",)} | {"attachments": []}}


def save_attachment(rid: str, lid: str, filename: str, data: bytes) -> str:
    """Store a file for B (guide question c): runs/<id>/delivery/attachments/<lecture>/<file>. Returns the relative path."""
    name = re.sub(r"[^\w.\- ]+", "_", Path(filename).name)[:120] or "file"
    d = _d(rid) / "attachments" / lid
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    n = 1
    while p.exists():
        p = d / f"{Path(name).stem}-{n}{Path(name).suffix}"
        n += 1
    p.write_bytes(data)
    return str(p.relative_to(d.parent.parent.parent)).replace("\\", "/")   # relative to the course folder: delivery/attachments/<lecture>/<file>


# ------------------------------------------------------------------ S5: review (approve / replace / reject)
def _review_rows(d: Path) -> dict:
    p = d / "review.yaml"
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}


def review(rid: str, lid: str, kind: str, key: str, decision: str, reason: str, title: str = "") -> dict:
    """One decision, written to review.yaml and applied at once with review.apply (C's own rules: a reason is required
    for replace and reject; replace takes the next-best reserve item)."""
    from profsagent.delivery import pipeline, review as rv
    if decision not in ("approve", "replace", "reject"):
        return {"problem": "Unknown decision"}
    reason = (reason or "").strip()
    if decision in ("replace", "reject") and not reason:
        return {"problem": f"Write a short reason to {decision} this."}
    d = _d(rid)
    rows = _review_rows(d)
    if lid not in (rows.get("lectures") or {}):
        pipeline.render(rid)                       # brings review.yaml in sync with the latest results
        rows = _review_rows(d)
    kinds = (rows.get("lectures") or {}).get(lid) or {}
    row = next((r for r in kinds.get(kind, []) if r.get("key") == key), None)
    if row is None:
        return {"problem": "This item is no longer in the list. Reload the page."}
    row["decision"], row["reason"] = decision, reason
    hdr = "# Decide each item: decision: approve | reject | replace   (reason: required for reject / replace)\n"
    (d / "review.yaml").write_text(hdr + yaml.safe_dump(rows, sort_keys=False, allow_unicode=True, width=140), encoding="utf-8")
    stats = rv.apply(rid)
    acts = _rj(d / "app_actions.json", {})
    acts.setdefault(lid, []).append({"kind": kind, "key": key, "title": title or row.get("title"), "decision": decision, "reason": reason, "at": time.time()})
    _wj(d / "app_actions.json", acts)
    return {"ok": True, "stats": stats}


def undo_approve(rid: str, lid: str, kind: str, key: str) -> dict:
    """Back to pending (C's apply only ever sets approve, so the app clears it in the lecture file and in review.yaml)."""
    from profsagent.delivery import pipeline
    d = _d(rid)
    p = d / "lectures" / f"{lid}.json"
    lec = _rj(p) or {}
    block = (lec.get("experts") or {}).get("experts", []) if kind == "experts" else ((lec.get("resources") or {}).get("items") or {}).get(kind, [])
    for x in block:
        if (x.get("url") or x.get("name") or x.get("title")) == key:
            x.pop("status_decision", None)
            x.pop("approved_at", None)
    _wj(p, lec)
    rows = _review_rows(d)
    for r in ((rows.get("lectures") or {}).get(lid) or {}).get(kind, []):
        if r.get("key") == key:
            r["decision"] = "pending"
    (d / "review.yaml").write_text(yaml.safe_dump(rows, sort_keys=False, allow_unicode=True, width=140), encoding="utf-8")
    pipeline.render(rid)
    return {"ok": True}


def own_link(rid: str, lid: str, title: str, url: str, kind: str, remove: int | None = None) -> dict:
    d = _d(rid)
    own = _rj(d / "app_own_links.json", {})
    if remove is not None:
        lst = own.get(lid, [])
        if 0 <= remove < len(lst):
            lst.pop(remove)
    else:
        if not title.strip() or not re.match(r"^https?://\S+$", url.strip()):
            return {"problem": "Give a title and a link that starts with http"}
        own.setdefault(lid, []).append({"title": title.strip()[:200], "url": url.strip(), "kind": kind if kind in KINDS else "reading", "at": time.time()})
    _wj(d / "app_own_links.json", own)
    return {"ok": True, "own": own.get(lid, [])}


def dismiss_dead(rid: str, url: str) -> None:
    d = _d(rid)
    lst = _rj(d / "app_health_dismissed.json", [])
    if url not in lst:
        lst.append(url)
    _wj(d / "app_health_dismissed.json", lst)


# ------------------------------------------------------------------ S8: ratings (each sent to C once)
def _ratings(d: Path) -> dict:
    p = d / "app_feedback_log.yaml"
    out: dict = {}
    for r in ((yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("ratings") or []) if p.exists() else []:
        out.setdefault(r["lecture"], {})[r["key"]] = {"r": r["rating"], "c": r.get("comment", "")}
    return out


def rate(rid: str, lid: str, key: str, title: str, rating: int, comment: str = "") -> dict:
    """review.record_feedback adds up every row of feedback.yaml each time it runs, so the app writes a feedback.yaml with
    just this rating, records it, and keeps it in app_feedback_log.yaml instead."""
    from profsagent.delivery import review as rv
    if rating not in (1, 2, 3, 4, 5):
        return {"problem": "Ratings go from 1 to 5"}
    d = _d(rid)
    fb = d / "feedback.yaml"
    fb.write_text(yaml.safe_dump({"lectures": {lid: [{"key": key, "title": title, "rating": rating, "comment": comment}]}},
                                 sort_keys=False, allow_unicode=True), encoding="utf-8")
    try:
        res = rv.record_feedback(rid)
    finally:
        fb.unlink(missing_ok=True)
    log = d / "app_feedback_log.yaml"
    data = (yaml.safe_load(log.read_text(encoding="utf-8")) or {}) if log.exists() else {}
    data.setdefault("ratings", []).append({"lecture": lid, "key": key, "title": title, "rating": rating, "comment": comment,
                                           "at": time.strftime("%Y-%m-%d %H:%M:%S")})
    log.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return {"ok": True, "recorded": res}


# ------------------------------------------------------------------ background work: C's search, link check, Neo4j records
class DeliveryManager:
    """One delivery job at a time, each in its own process (app/delivery_step.py) so it can be cancelled.
    Jobs: ("recommend", rid, {lectures, refresh}), ("health", rid, {})."""

    def __init__(self, runs: Path | None = None, step_cmd=None):
        self.runs = runs or RUNS
        self.q: queue.Queue = queue.Queue()
        self.lock = threading.RLock()
        self.current: str | None = None
        self.proc: subprocess.Popen | None = None
        self.cancelled: set[str] = set()
        self._stop = threading.Event()
        self.step_cmd = step_cmd or (lambda rid, kind, af: [sys.executable, "-m", "profsagent.app.delivery_step", rid, kind, str(af)])

    def start(self) -> None:
        self.recover()
        threading.Thread(target=self._worker, daemon=True, name="profsagent-delivery").start()

    def stop(self) -> None:
        self._stop.set()
        self.q.put(None)

    def _jobs(self, rid: str) -> dict:
        return _rj(_d(rid, self.runs) / "app_jobs.json", {"lectures": {}})

    def _set(self, rid: str, lids: list[str] | None, **kw) -> None:
        with self.lock:
            j = self._jobs(rid)
            if lids is None:
                j["health"] = {**(j.get("health") or {}), **kw, "at": time.time()}
            for lid in lids or []:
                j["lectures"][lid] = {**(j["lectures"].get(lid) or {}), **kw, "at": time.time()}
            _wj(_d(rid, self.runs) / "app_jobs.json", j)

    def recover(self) -> None:
        for d in sorted(self.runs.glob("app-*")):
            j = _rj(d / "delivery" / "app_jobs.json")
            if not j:
                continue
            lids = [lid for lid, x in j.get("lectures", {}).items() if x.get("state") in ("queued", "running")]
            if lids:
                self.queue_recommend(d.name, lids, refresh=any(j["lectures"][x].get("refresh") for x in lids))

    def queue_recommend(self, rid: str, lectures: list[str], refresh: bool = False) -> None:
        self.cancelled.discard(rid)
        self._set(rid, lectures, state="queued", refresh=refresh, error=None)
        self.q.put(("recommend", rid, {"lectures": lectures, "refresh": refresh}))

    def queue_health(self, rid: str) -> None:
        self.cancelled.discard(rid)
        self._set(rid, None, state="queued", error=None)
        self.q.put(("health", rid, {}))

    def cancel(self, rid: str) -> None:
        """Stop work for a course (it is being deleted): queued jobs are skipped, a running one is ended."""
        with self.lock:
            self.cancelled.add(rid)
            proc = self.proc if self.current == rid else None
        if proc is not None:
            proc.kill()

    def _worker(self) -> None:
        while not self._stop.is_set():
            job = self.q.get()
            if job is None:
                return
            kind, rid, args = job
            if rid in self.cancelled or not (self.runs / rid / "delivery").exists():
                continue
            lids = args.get("lectures") if kind == "recommend" else None
            self._set(rid, lids, state="running")
            d = _d(rid, self.runs)
            af, rf = d / "app_step_args.json", d / "app_step_result.json"
            _wj(af, args)
            rf.unlink(missing_ok=True)
            env = {**os.environ, "PYTHONPATH": str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""), "PYTHONIOENCODING": "utf-8"}
            with self.lock:
                self.current = rid
                self.proc = subprocess.Popen(self.step_cmd(rid, kind, af), cwd=str(ROOT), env=env)
            try:
                self.proc.wait()
            finally:
                with self.lock:
                    self.proc, self.current = None, None
            if rid in self.cancelled or not d.exists():
                continue
            res = _rj(rf) or {"error": {"message": "the job's process ended without a result", "type": "StepCrashed"}}
            if "ok" in res:
                self._set(rid, lids, state="done", error=None)
            else:
                self._set(rid, lids, state="error", error=_plain_error(res["error"]))


def _plain_error(err: dict) -> str:
    t, msg = err.get("type", ""), err.get("message", "")
    if err.get("quota"):
        return "The free AI quota is used up for today; try again after about 1:30 pm IST."
    if t == "SystemExit" or "No lecture asked for anything" in msg:
        return "Nothing to search: no lecture asked for resources or a guest."
    return f"The search stopped ({t}). Press Try again; lectures already finished are kept."
