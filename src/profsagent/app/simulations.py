"""Simulations in the professor app (docs/09_phase2_A_simulation_catalogue.md §7, plan stage A2; docs/decisions.md 26).

The catalogue is simulations/ (profsagent.sims.catalogue): each entry has a manifest, one offline page and its checks.
The app shows it in three places:
  - the Simulations page: every entry by kind and course, a preview, and requests for new ones;
  - each lecture page in Lecture delivery: the entries whose topics match the lecture, which the professor approves,
    replaces or rejects, and the setup students should start from (the "class example"); and simulations on trusted
    sites (PhET, Falstad, VisuAlgo…, profsagent.sims.external) as links only, which the professor opens and judges;
  - the student view: the approved simulations, opened at the class example.

Stored per course run, in runs/<id>/delivery/simulations/ (Vihan's delivery files stay untouched):
  suggestions.json  per lecture: matching entries (local embedding model, no AI calls) and the kind of simulation the
                    topic suits (the catalogue's topic -> type classifier). Remade when the lectures or the catalogue change.
  decisions.json    per lecture: entries the professor added, approve / replace / reject (with reason and version),
                    class examples; and a history of every change.
For all courses: runs/_simulation_requests.json, simulations professors asked for (not committed: their course ideas).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qsl

from profsagent.config import DATA, RUNS
from profsagent.sims import autobuild as AB
from profsagent.sims import catalogue as C
from profsagent.sims import external as X

MATCH = 0.60        # topic similarity for a suggestion; on IIIT-D's 9,784 weekly topics (3 Nov) matches below it were mostly unrelated
STRONG = 0.75       # shown as a close match
TOP = 4             # suggestions kept per lecture
EXT_MATCH = 0.65    # links to other sites: on the same 9,784 topics, matches below it were often wrong (e.g. "TCP/IP networks" -> network flow)
EXT_TOP = 3         # links kept per lecture
SID = re.compile(r"^[a-z0-9][a-z0-9_.-]{2,80}$")
EXT = re.compile(r"^ext:[a-z0-9]+:[a-z0-9_.-]{1,80}$")
LID = re.compile(r"^W\d\d\.L\d+$")
REQUESTS = "_simulation_requests.json"

_LOCK = threading.Lock()          # one suggestion job at a time (the embedding cache file is shared)
_BUILD_LOCK = threading.Lock()
_JOBS: dict[str, dict] = {}       # run id -> {"state": "running" | "error", "error": str}


# ------------------------------------------------------------------ small helpers
def _rj(p: Path, default=None):
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
    except (OSError, ValueError):
        return default


def _wj(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, p)


def _dir(rid: str, runs: Path | None = None) -> Path:
    return (runs or RUNS) / rid / "delivery" / "simulations"


def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


_cat = {"key": None, "entries": []}


def entries() -> list[dict]:
    """The catalogue's entries (retired ones too: an approval stays visible), re-read when a manifest changes."""
    key = tuple((str(f), f.stat().st_mtime) for f in sorted(C.SIMS.glob("*/sim.yaml")))
    if key != _cat["key"]:
        _cat.update(key=key, entries=[e for e in C.entries() if not C.problems(e)])
    return _cat["entries"]


def entry(sim_id: str) -> dict | None:
    return next((e for e in entries() if e["id"] == sim_id), None)


@lru_cache(maxsize=1)
def _course_names() -> dict[str, str]:
    try:
        idx = json.loads((DATA / "techtree_index.json").read_text(encoding="utf-8"))
    except OSError:
        return {}
    out = {}
    for v in idx.values():
        for c in re.split(r"[/,]", v.get("code") or ""):
            c = re.sub(r"\s+", "", c).upper()
            if c:
                out.setdefault(c, v.get("name") or "")
    return out


def _qa() -> dict:
    return _rj(C.BUILD / "qa_report.json", {}) or {}


def card(e: dict, qa: dict | None = None) -> dict:
    """What the screens show about one entry."""
    ty = C.types()
    names = {t["id"]: t["name"] for t in ty["types"]}
    ts = e["type"] if isinstance(e["type"], list) else [e["type"]]
    q = (qa if qa is not None else _qa()).get(e["id"])
    return {"id": e["id"], "title": e["title"], "summary": e["summary"], "version": str(e["version"]), "status": e["status"],
            "types": [{"id": t, "name": names.get(t, t)} for t in ts],
            "level": {"id": e["interactivity"], "text": ty["levels"].get(e["interactivity"], "")},
            "courses": [{"code": str(c).upper(), "name": _course_names().get(str(c).upper(), "")} for c in e["courses"]],
            "topics": list(e["topics"]), "engine": (e.get("engine") or {}).get("name"), "class_example": bool(e.get("class_example")),
            "built_by": e.get("built_by"), "request": e.get("request"),
            "independent": (e.get("checks") or {}).get("independent"),
            "checked": ({"ok": bool(q.get("ok")), "at": q.get("at"), "version": q.get("version"),
                         "current": str(q.get("version")) == str(e["version"])} if q else None)}


# ------------------------------------------------------------------ pages
def _sources(e: dict) -> list[Path]:
    d, files = e["_dir"], e["files"]
    if files.get("page"):
        return [d / files["page"]]
    src = d / files["page_src"]
    html = src.read_text(encoding="utf-8")
    out = [src] + [C.SIMS / root / x for root, x in C.ASSET_JS.findall(html) + C.ASSET_CSS.findall(html)]
    return out + ([C.LIB / "LICENSES.txt"] if (C.LIB / "LICENSES.txt").exists() else [])


def page(sim_id: str) -> Path:
    """The single-file page, rebuilt when its source, a library or an engine changed since the last build."""
    e = entry(sim_id) if SID.match(sim_id or "") else None
    if e is None:
        raise KeyError(sim_id)
    out = C.BUILD / f"{e['id']}.html"
    with _BUILD_LOCK:
        newest = max(p.stat().st_mtime for p in _sources(e) if p.exists())
        if not out.exists() or out.stat().st_mtime < newest:
            C.build(e)
    return out


# ------------------------------------------------------------------ suggestions (background; the embedding model takes ~10 s to load once)
def _briefs(rid: str, runs: Path | None) -> list[dict]:
    return _rj((runs or RUNS) / rid / "delivery" / "briefs.json", []) or []


def _course_name(rid: str, runs: Path | None) -> str:
    st = _rj((runs or RUNS) / rid / "state.json", {}) or {}
    return (st.get("cco_compact") or {}).get("course_name") or ""


def _lecture_full(b: dict) -> str:
    return (b.get("topic") or "") + ". " + (b.get("summary") or "")[:600]


def _key(briefs: list[dict], es: list[dict]) -> str:
    raw = json.dumps([[(b["lecture_id"], b.get("topic"), _lecture_full(b)) for b in briefs],
                      [(e["id"], str(e["version"]), e["title"], list(e["topics"]), e.get("status")) for e in es],
                      _rj(C.SIMS / "classifier" / "params.json", {}), MATCH, TOP,
                      [e["id"] for e in X.entries()], EXT_MATCH, EXT_TOP], ensure_ascii=False)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _short_title(e: dict) -> str:
    return re.split(r"\s+·\s+|,\s+step by step$", e["title"])[0].strip()


def compute(briefs: list[dict], course: str, es: list[dict]) -> dict:
    """Per lecture: catalogue entries whose title or topics are close to the lecture topic (or its summary), and the kind
    of simulation the topic suits. Only the local model; no AI calls."""
    import numpy as np
    from profsagent.sims import classify as K
    live = [e for e in es if e.get("status") != "retired"]
    out: dict[str, dict] = {}
    if not briefs:
        return out
    texts, owner = [], []
    for i, e in enumerate(live):
        for t in [_short_title(e)] + list(e["topics"]):
            texts.append(t)
            owner.append(i)
    owner_a = np.array(owner)
    T = K.embed([b.get("topic") or "" for b in briefs])
    if live:
        E = K.embed(texts)
        F = K.embed([_short_title(e) + ": " + ", ".join(e["topics"]) for e in live])
        Lf = K.embed([_lecture_full(b) for b in briefs])
        S, SF = T @ E.T, Lf @ F.T
    params = _rj(C.SIMS / "classifier" / "params.json", {}) or {}
    clf = K.Classifier(params.get("threshold", 0.35), params.get("margin", 0.0), params.get("topk", 2))
    kt = [f"{b.get('topic')} ({course})" if params.get("with_course") and course else (b.get("topic") or "") for b in briefs]
    kinds = clf.decide(clf.scores(K.embed(kt)))
    xs = X.entries()
    xtexts, xowner = [], []
    for i, x in enumerate(xs):
        for t in X.text_for_matching(x):
            xtexts.append(t)
            xowner.append(i)
    XS = T @ K.embed(xtexts).T if xs else None
    for k, b in enumerate(briefs):
        matches = []
        for i, e in enumerate(live):
            cols = np.where(owner_a == i)[0]
            j = int(cols[S[k, cols].argmax()])
            s_topic, s_full = float(S[k, j]), float(SF[k, i])
            score = max(s_topic, s_full)
            if score >= MATCH:
                matches.append({"id": e["id"], "score": round(score, 3), "close": score >= STRONG, "matched": texts[j] if s_topic >= s_full else None,
                                "via": "topic" if s_topic >= s_full else "summary"})
        matches.sort(key=lambda m: -m["score"])
        links: dict[str, dict] = {}
        if XS is not None:
            for j in np.argsort(-XS[k])[:60]:
                sc = float(XS[k, j])
                if sc < EXT_MATCH:
                    break
                x = xs[xowner[j]]
                if x["id"] not in links:
                    links[x["id"]] = {"id": x["id"], "score": round(sc, 3), "matched": xtexts[j].split(": ")[0]}
        kind, _score, also = kinds[k]
        out[b["lecture_id"]] = {"topic": b.get("topic"), "matches": matches[:TOP], "external": list(links.values())[:EXT_TOP],
                                "kind": {"type": kind, "also": also if kind != K.NONE else None}}
    return out


def _prepare(rid: str, runs: Path | None, key: str) -> None:
    try:
        with _LOCK:
            res = compute(_briefs(rid, runs), _course_name(rid, runs), entries())
            _wj(_dir(rid, runs) / "suggestions.json", {"key": key, "made_at": _now(), "lectures": res})
        _JOBS.pop(rid, None)
    except Exception as ex:  # noqa: BLE001 - shown on the lecture page; delivery itself keeps working
        _JOBS[rid] = {"state": "error", "error": f"{type(ex).__name__}: {ex}"[:300], "key": key, "at": time.time()}


def suggestions(rid: str, runs: Path | None = None, wait: bool = False, start: bool = True) -> tuple[str, dict]:
    """("ready", lectures) or ("preparing" | "error" | "not started", {}). With start, a stored result that is out of date
    is remade in the background (wait: in this thread)."""
    briefs = _briefs(rid, runs)
    key = _key(briefs, entries())
    cur = _rj(_dir(rid, runs) / "suggestions.json", {}) or {}
    if cur.get("key") == key:
        return "ready", cur.get("lectures") or {}
    job = _JOBS.get(rid)
    if job and job["state"] == "running":
        return "preparing", {}
    if job and job["state"] == "error" and job.get("key") == key and time.time() - job.get("at", 0) < 300:
        return "error", {"error": job["error"]}       # tried again after 5 minutes
    if not start:
        return "not started", {}
    _JOBS[rid] = {"state": "running", "key": key}
    if wait:
        _prepare(rid, runs, key)
        return suggestions(rid, runs) if rid not in _JOBS else ("error", {"error": _JOBS[rid]["error"]})
    threading.Thread(target=_prepare, args=(rid, runs, key), daemon=True, name=f"sims-{rid}").start()
    return "preparing", {}


# ------------------------------------------------------------------ the professor's decisions
def _decisions(rid: str, runs: Path | None) -> dict:
    return _rj(_dir(rid, runs) / "decisions.json", None) or {"lectures": {}, "history": []}


def ext_card(x: dict) -> dict:
    """What the screens show about a link to another site (not ours, not checked by us)."""
    return {"id": x["id"], "external": True, "title": x["title"], "summary": x["summary"], "url": x["url"], "site": x["site"],
            "site_name": x["site_name"], "topics": x["topics"][:8], "class_example": False, "version": None, "checked": None}


def _lecture_items(lid: str, sug: dict, dec: dict, qa: dict) -> list[dict]:
    """Added by the professor (newest first), then the suggestions by score; each with its decision and class example."""
    d = dec.get("lectures", {}).get(lid, {})
    order: list[tuple[str, dict]] = [(s, {"source": "added", "added_by": (d.get("added_by") or {}).get(s, "Professor")}) for s in reversed(d.get("added", []))]
    order += [(m["id"], {"source": "suggested", "score": m["score"], "close": m.get("close"), "matched": m.get("matched"), "via": m.get("via")})
              for m in (sug.get(lid) or {}).get("matches", [])]
    order += [(m["id"], {"source": "external", "score": m["score"], "matched": m.get("matched")}) for m in (sug.get(lid) or {}).get("external", [])]
    order += [(s, {"source": "decided"}) for s in d.get("decisions", {})]     # e.g. approved, then no longer suggested
    out, seen = [], set()
    for sid, extra in order:
        if sid in seen:
            continue
        seen.add(sid)
        if EXT.match(sid):
            x = X.get(sid)
            if x is None:
                continue
            c = {**ext_card(x), **extra}
            c["decision"], c["retired"], c["example"] = d.get("decisions", {}).get(sid), False, None
            out.append(c)
            continue
        e = entry(sid)
        if e is None:
            continue
        c = {**card(e, qa), **extra}
        x = d.get("decisions", {}).get(sid)
        c["decision"] = ({**x, "outdated": x.get("decision") == "approve" and str(x.get("version")) != c["version"]} if x else None)
        c["retired"] = e.get("status") == "retired"
        c["example"] = d.get("class_example", {}).get(sid)
        out.append(c)
    return out


def course_view(rid: str, runs: Path | None = None) -> dict:
    """For delivery.view(): per lecture, the simulation items and the kind the topic suits. Never starts the suggestion job
    (the server does, when a professor opens the course: sims.suggestions)."""
    state, sug = suggestions(rid, runs, start=False)
    dec, qa = _decisions(rid, runs), _qa()
    names = {t["id"]: t for t in C.types()["types"]}
    lectures = {}
    for b in _briefs(rid, runs):
        lid = b["lecture_id"]
        items = _lecture_items(lid, sug if state == "ready" else {}, dec, qa)
        k = (sug.get(lid) or {}).get("kind") if state == "ready" else None
        kind = None
        if k:
            t = names.get(k["type"])
            kind = ({"id": "none"} if t is None else {"id": t["id"], "name": t["name"], "does": t["does"]})
            if k.get("also") in names:
                kind["also"] = {"id": k["also"], "name": names[k["also"]]["name"]}
        if items or kind:
            lectures[lid] = {"items": items, "kind": kind}
    return {"state": state, "error": sug.get("error") if state == "error" else None, "lectures": lectures}


def decide(rid: str, lid: str, sim_id: str, decision: str, reason: str = "", by: str = "Professor", runs: Path | None = None) -> dict:
    if decision not in ("add", "approve", "replace", "reject", "undo"):
        return {"problem": "Unknown decision"}
    if not any(b["lecture_id"] == lid for b in _briefs(rid, runs)):
        return {"problem": "No such lecture"}
    if EXT.match(sim_id or ""):
        x = X.get(sim_id)
        if x is None:
            return {"problem": "No such link"}
        if decision not in ("approve", "reject", "undo"):
            return {"problem": "A link can only be approved, rejected or undone"}
        e = {"version": "", "status": "external"}
    else:
        e = entry(sim_id) if SID.match(sim_id or "") else None
    if e is None:
        return {"problem": "No such simulation in the catalogue"}
    if decision in ("add", "approve") and e.get("status") == "retired":
        return {"problem": "This simulation was retired from the catalogue"}
    reason = (reason or "").strip()
    if decision == "reject" and len(reason) < 3:
        return {"problem": "Write a short reason first"}
    data = _decisions(rid, runs)
    d = data["lectures"].setdefault(lid, {"added": [], "decisions": {}, "class_example": {}})
    if decision == "add":
        d["added"] = [s for s in d["added"] if s != sim_id] + [sim_id]
        d.setdefault("added_by", {})[sim_id] = by
        d["decisions"].pop(sim_id, None)
    elif decision == "undo":
        d["decisions"].pop(sim_id, None)
    else:
        d["decisions"][sim_id] = {"decision": decision, "version": str(e["version"]), "reason": reason[:1000], "by": by, "at": _now()}
    data["history"].append({"at": _now(), "lecture": lid, "simulation": sim_id, "version": str(e["version"]), "decision": decision,
                            "reason": reason[:1000], "by": by})
    _wj(_dir(rid, runs) / "decisions.json", data)
    return {"ok": True}


def class_example(rid: str, lid: str, sim_id: str, state: str, summary: str = "", clear: bool = False, by: str = "Professor",
                  runs: Path | None = None) -> dict:
    """The setup students start from: the page's own link state (key=value&...), as the page reported it."""
    if not any(b["lecture_id"] == lid for b in _briefs(rid, runs)):
        return {"problem": "No such lecture"}
    e = entry(sim_id) if SID.match(sim_id or "") else None
    if e is None:
        return {"problem": "No such simulation in the catalogue"}
    if not e.get("class_example"):
        return {"problem": "This simulation cannot keep a class example yet"}
    state = (state or "").strip().lstrip("#")
    if not clear:
        if not state or len(state) > 6000 or not parse_qsl(state, keep_blank_values=True):
            return {"problem": "Change something in the simulation first, then save it as the class example"}
    data = _decisions(rid, runs)
    d = data["lectures"].setdefault(lid, {"added": [], "decisions": {}, "class_example": {}})
    if clear:
        d["class_example"].pop(sim_id, None)
    else:
        d["class_example"][sim_id] = {"state": state, "summary": (summary or "").strip()[:300], "version": str(e["version"]), "at": _now()}
    data["history"].append({"at": _now(), "lecture": lid, "simulation": sim_id, "version": str(e["version"]),
                            "decision": "class example cleared" if clear else "class example set", "summary": (summary or "")[:300], "by": by})
    _wj(_dir(rid, runs) / "decisions.json", data)
    return {"ok": True}


# ------------------------------------------------------------------ the Simulations page
def _used(runs: Path | None) -> dict[str, list[dict]]:
    """Where each simulation is approved, across the app's courses."""
    runs = runs or RUNS
    out: dict[str, list[dict]] = {}
    for f in sorted(runs.glob("app-*/delivery/simulations/decisions.json")):
        rid = f.parents[2].name
        meta = _rj(runs / rid / "app.json", {}) or {}
        topics = {b["lecture_id"]: b.get("topic") for b in _briefs(rid, runs)}
        for lid, d in (_rj(f, {}) or {}).get("lectures", {}).items():
            for sid, x in d.get("decisions", {}).items():
                if x.get("decision") == "approve":
                    out.setdefault(sid, []).append({"run_id": rid, "course": meta.get("title") or rid, "lecture": lid, "topic": topics.get(lid)})
    return out


def catalogue_view(runs: Path | None = None) -> dict:
    qa, used = _qa(), _used(runs)
    es = [e for e in entries() if e.get("status") != "retired"]
    cards = [{**card(e, qa), "used": used.get(e["id"], [])} for e in es]
    count: dict[str, int] = {}
    for c in cards:
        for t in c["types"]:
            count[t["id"]] = count.get(t["id"], 0) + 1
    ty = C.types()
    xs = X.entries()
    return {"entries": cards, "types": [{"id": t["id"], "name": t["name"], "does": t["does"], "count": count.get(t["id"], 0)} for t in ty["types"]],
            "levels": ty["levels"], "requests": requests(runs),
            "external": {"sites": sorted({x["site_name"] for x in xs}, key=lambda n: -sum(1 for y in xs if y["site_name"] == n)),
                         "entries": [{"id": x["id"], "site_name": x["site_name"], "title": x["title"], "url": x["url"], "summary": x["summary"][:200],
                                      "text": " ".join([x["title"], x["site_name"], x["summary"], " ".join(x["topics"])]).lower()} for x in xs]}}


def requests(runs: Path | None = None) -> list[dict]:
    return sorted(AB.read_requests(runs), key=lambda r: r.get("at") or "", reverse=True)


def add_request(body: dict, runs: Path | None = None) -> dict:
    """A professor asks the team for a simulation (the team builds it into the catalogue; see simulations/README.md)."""
    runs = runs or RUNS
    topic, what = str(body.get("topic") or "").strip(), str(body.get("what") or "").strip()
    errors = {}
    if len(topic) < 3:
        errors["topic"] = "Name the topic"
    if len(what) < 10:
        errors["what"] = "Say in a sentence what students should see or try"
    kind = str(body.get("kind") or "")
    if kind and kind not in C.type_ids():
        errors["kind"] = "Unknown kind"
    rid, lid = str(body.get("run_id") or ""), str(body.get("lecture") or "")
    if rid and not (re.fullmatch(r"app-[a-z0-9-]+", rid) and (runs / rid / "app.json").exists()):
        errors["run_id"] = "Unknown course"
    if lid and not LID.match(lid):
        errors["lecture"] = "Unknown lecture"
    if errors:
        return {"errors": errors}
    course = ((_rj(runs / rid / "app.json", {}) or {}).get("title") if rid else None) or str(body.get("course") or "").strip()[:120]
    row = {"at": _now(), "by": str(body.get("by") or "Professor")[:80], "topic": topic[:200], "what": what[:1500],
           "kind": kind or None, "course": course or None, "run_id": rid or None, "lecture": lid or None, "status": "queued"}

    def add(rows):
        n = max([int(r["id"][1:]) for r in rows if re.fullmatch(r"R\d+", r.get("id", ""))] + [0])
        row["id"] = f"R{n + 1:03d}"
        rows.append(row)
    AB.update_requests(runs, add)
    return {"ok": True, "request": row}


def build_again(req_id: str, runs: Path | None = None, note: str = "") -> dict:
    """Requested (old): look for existing ones first. Reviewed and none fit, sent to the team, or paused: build one."""
    out: dict = {}

    def fn(rows):
        for r in rows:
            if r.get("id") != req_id:
                continue
            if r.get("status") == "requested":
                r.update(status="queued", reason=None, detail=None)
            elif r.get("status") in ("review", "needs_team", "paused"):
                r.update(status="build_queued", reason=None, detail=None, **({"note": note.strip()[:600]} if note.strip() else {}))
            else:
                return
            out.update(r)
    AB.update_requests(runs or RUNS, fn)
    return {"ok": True, "request": out} if out else {"problem": "This request cannot be built again now"}


def review_found(req_id: str, n: int, decision: str, runs: Path | None = None, by: str = "Professor") -> dict:
    """The professor's decision on one simulation the search found: approve (the request is done; a lecture request puts it
    on the lecture, approved) or reject (when every one is rejected, the machine builds one). Returns start_build."""
    runs = runs or RUNS
    if decision not in ("approve", "reject", "undo"):
        return {"problem": "Unknown decision"}
    out: dict = {}

    def fn(rows):
        r = next((x for x in rows if x.get("id") == req_id), None)
        if r is None or r.get("status") not in ("review", "chosen"):
            return
        c = next((x for x in r.get("found") or [] if x.get("n") == n), None)
        if c is None:
            return
        if decision == "approve":
            if c["kind"] == "link":
                c["ext_id"] = c.get("ext_id") or X.add_found(c["url"], c["title"], c.get("summary") or "", c.get("site") or "", r.get("topic") or "", req_id, by)
            c["decision"] = "approve"
            r.update(status="chosen", chosen={k: c.get(k) for k in ("n", "kind", "id", "ext_id", "url", "title", "site")}, chosen_at=_now())
        elif decision == "reject":
            c["decision"] = "reject"
            if all(x.get("decision") == "reject" for x in r["found"]):
                r.update(status="build_queued", note=r.get("note") or "")
                out["start_build"] = True
        else:
            c["decision"] = None
            if r.get("status") == "chosen" and (r.get("chosen") or {}).get("n") == n:
                r.update(status="review", chosen=None)
        out["request"] = dict(r)
    AB.update_requests(runs, fn)
    if not out:
        return {"problem": "This request is not waiting for a review"}
    req = out["request"]
    if decision == "approve" and req.get("run_id") and req.get("lecture"):        # a request from a lecture page: it lands there, approved
        ch = req["chosen"]
        decide(req["run_id"], req["lecture"], ch.get("ext_id") or ch.get("id"), "approve", by=by, runs=runs)
    return {"ok": True, "request": req, "start_build": bool(out.get("start_build"))}
