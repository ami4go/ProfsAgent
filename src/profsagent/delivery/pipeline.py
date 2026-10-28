"""Deliverable C orchestration for one approved course run (scripts/run_delivery.py).

  briefs   → runs/<id>/delivery/briefs.json + briefs.md
  survey   → runs/<id>/delivery/survey.yaml (professor's answers; nothing is searched without them)
  recommend→ per lecture runs/<id>/delivery/lectures/<lecture>.json (resources, clips, experts), guest_kits/<lecture>.md
  report   → runs/<id>/delivery/report.md (what the professor reads) + review.yaml (what the professor decides)
Each lecture is saved as soon as it is done, so a run that stops (quota, network) continues where it left off.
"""
from __future__ import annotations

import time

from profsagent.delivery import survey as sv
from profsagent.delivery.brief import briefs_markdown, build_briefs
from profsagent.delivery.common import hms, load_state, now, out_dir, read_json, write_json
from profsagent.delivery.sources import YouTube, transcripts_blocked


class Log:
    def __init__(self, run_id: str):
        self.path = out_dir(run_id) / "delivery.log"

    def __call__(self, msg: str) -> None:
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def make_briefs(run_id: str) -> list[dict]:
    st = load_state(run_id)
    briefs = build_briefs(st)
    d = out_dir(run_id)
    write_json(d / "briefs.json", briefs)
    (d / "briefs.md").write_text(briefs_markdown(st, briefs), encoding="utf-8")
    return briefs


def recommend(run_id: str, lectures: list[str] | None = None, refresh: bool = False, limit: int | None = None) -> dict:
    from profsagent.delivery.experts import guest_kit, recommend_experts
    from profsagent.delivery.resources import plan_queries, recommend_lecture
    from profsagent.llm.client import LLMClient

    log = Log(run_id)
    st = load_state(run_id)
    d = out_dir(run_id)
    briefs = {b["lecture_id"]: b for b in (read_json(d / "briefs.json") or make_briefs(run_id))}
    s = sv.load(run_id)
    reqs = sv.requests(s)
    if not reqs:
        raise SystemExit("No lecture asked for anything yet: fill runs/<id>/delivery/survey.yaml "
                         "(python scripts/run_delivery.py survey --run-id <id> --ask), or use --defaults for a test run.")
    if lectures:
        reqs = {k: v for k, v in reqs.items() if k in lectures}
    if limit:
        reqs = dict(list(reqs.items())[:limit])
    def done(k):   # a lecture saved as partial (transcripts were blocked) is redone by a plain re-run
        f = d / "lectures" / f"{k}.json"
        return f.exists() and not (read_json(f) or {}).get("partial")
    todo = {k: v for k, v in reqs.items() if refresh or not done(k)}
    log(f"delivery for {run_id}: {len(reqs)} lectures asked for help, {len(todo)} to do · YouTube units used today: {YouTube().quota.used()}")
    if not todo:
        return render(run_id)
    llm = LLMClient(d / "llm_calls.jsonl")
    qpath = d / "queries.json"
    queries = read_json(qpath, {})
    missing = {k: v for k, v in todo.items() if k not in queries or refresh}
    if missing:
        queries.update(plan_queries(llm, st, briefs, missing, run_id, log))
        write_json(qpath, queries)
    # a topic split over several lectures: later parts get the next-best, different items (not repeats)
    by_topic = {}
    for lid in sorted(reqs):
        f = d / "lectures" / f"{lid}.json"
        if f.exists() and lid not in todo:
            prev = read_json(f)
            if not prev.get("continuation_of"):
                by_topic.setdefault(briefs[lid]["topic_id"], (lid, prev, reqs[lid]))
    warned = False
    for lid, want in sorted(todo.items()):
        b = briefs[lid]
        log(f"{lid} · {b['topic']} · wants: {', '.join(k[5:] for k, v in want.items() if k.startswith('want_') and v)}")
        first = by_topic.get(b["topic_id"])
        if first and first[0] < lid and all(first[2].get(k) for k, v in want.items() if k.startswith("want_") and v):
            res = continuation(first[1], first[0], b, want)
            if first[1].get("partial"):
                res["partial"] = {"reason": f"continues {first[0]}, which is partial"}
            write_json(d / "lectures" / f"{lid}.json", res)
            log(f"  {lid} continues {first[0]} (same topic): next-best items, no repeats")
            continue
        res = {"lecture_id": lid, "topic": b["topic"], "generated_at": now()}
        talk_titles = []
        if any(v for k, v in want.items() if k.startswith("want_") and k != "want_guest"):
            res["resources"] = recommend_lecture(llm, st, b, want, queries[lid], run_id, log)
            talk_titles = [c["title"] for kind in res["resources"]["items"].values() for c in kind] + \
                          [c["title"] for kind in res["resources"]["reserve"].values() for c in kind]
        if want.get("want_guest"):
            vids = [c for k in ("video", "recorded_lecture") for blk in ("items", "reserve")
                    for c in ((res.get("resources") or {}).get(blk) or {}).get(k, [])]
            res["experts"] = recommend_experts(llm, st, b, queries[lid], talk_titles, run_id, log, videos=vids)
            kit = guest_kit(st, b, res["experts"]["experts"])
            (d / "guest_kits").mkdir(exist_ok=True)
            (d / "guest_kits" / f"{lid}.md").write_text(kit, encoding="utf-8")
        if (res.get("resources") or {}).get("partial"):
            res["partial"] = res["resources"]["partial"]
        write_json(d / "lectures" / f"{lid}.json", res)
        by_topic.setdefault(b["topic_id"], (lid, res, want))
        if transcripts_blocked() and not warned:
            warned = True
            log(f"  ! YouTube is blocking transcript requests from this IP (since {transcripts_blocked()}). No more are sent "
                "this run; videos are judged from title and description, and those lectures are saved as partial. "
                "Run the same recommend command later (no --refresh needed) to redo only the partial lectures.")
        log(f"  saved {lid} · YouTube units used today: {YouTube().quota.used()}")
    part = [k for k in sorted(todo) if (read_json(d / "lectures" / f"{k}.json") or {}).get("partial")]
    if part:
        log(f"partial lectures ({len(part)}), redone by the next run: {', '.join(part)}")
    log(f"AI calls this session: {llm.totals['calls']}")
    return render(run_id)


def continuation(prev: dict, prev_lid: str, b: dict, want: dict) -> dict:
    """Recommendations for a later lecture on the same topic: the next-best items of the first lecture's ranking
    (its reserve), so students get new material; the guest list stays with the first lecture."""
    import copy

    from profsagent.delivery.common import rcfg
    from profsagent.delivery.resources import KIND_CAP, clip_playlist, site
    out = {"lecture_id": b["lecture_id"], "topic": b["topic"], "generated_at": now(), "continuation_of": prev_lid}
    pr = prev.get("resources")
    if pr:
        r = copy.deepcopy(pr)
        items, reserve = {}, {}
        caps = rcfg()["caps"]
        bar = caps.get("min_continuation_score", caps.get("min_show_score", 0))
        for kind in pr["items"]:
            cap = caps[KIND_CAP[kind]]
            # a second lecture on the topic needs items about the topic itself, above a higher bar, not from a site
            # already shown for it (a mirror of the spec), and not ones the AI review says only mention it
            seen = {site(c) for c in pr["items"][kind]} if kind in ("reading", "practice") else set()
            fresh = []
            for c in copy.deepcopy(pr["reserve"].get(kind, [])):
                topic_ok = ((c.get("coverage") or {}).get("per_target", {}).get(b["topic_id"]) or {}).get("covered")
                teaches = (c.get("review") or {}).get("explains") == "explains"     # unreviewed items are not carried over
                if c.get("total", 0) < bar or not topic_ok or not teaches or (seen and site(c) in seen):
                    continue
                fresh.append(c)
                if kind in ("reading", "practice"):
                    seen.add(site(c))
            for i, c in enumerate(fresh[:cap], 1):
                c["rank"], c["status"] = i, "proposed"
            items[kind], reserve[kind] = fresh[:cap], fresh[cap:]
        r.update(items=items, reserve=reserve, lecture_id=b["lecture_id"],
                 note=f"Same topic as {prev_lid}: its recommendations still apply. These are the next-best, different items.")
        if want.get("want_clips"):
            r["clips"] = clip_playlist([c for k in ("video", "recorded_lecture") for c in items.get(k, [])], b)
        out["resources"] = r
    if want.get("want_guest") and prev.get("experts"):
        out["experts"] = {"same_as": prev_lid, "experts": [], "reserve": [], "rejected": [], "counts": {}}
    return out


# ------------------------------------------------------------------ report + review file
KIND_TITLE = {"video": "Videos", "recorded_lecture": "Recorded lecture (flipped class)", "reading": "Readings", "practice": "Practice"}
USE = {"professor_prep": "your preparation", "pre_class": "before class", "in_class_clip": "in-class clip", "after_class": "after class",
       "flipped_class": "flipped class", "lab": "lab", "practice": "practice"}


def render(run_id: str) -> dict:
    from profsagent.delivery import review as rv
    st = load_state(run_id)
    d = out_dir(run_id)
    briefs = {b["lecture_id"]: b for b in read_json(d / "briefs.json", [])}
    lecs = {p.stem: read_json(p) for p in sorted((d / "lectures").glob("*.json"))} if (d / "lectures").exists() else {}
    L = [f"# Delivery support — {st['cco_compact']['course_name']}", "",
         f"Run `{run_id}` · generated {now()} · {len(lecs)} lectures with recommendations. Every link was checked to exist; "
         "items are ranked by how well they cover the lecture's topic and learning outcomes, then quality (AI review), "
         "source, level, reception and practicality. Decide in `review.yaml` (approve / replace / reject + reason).", ""]
    for lid in sorted(lecs):
        r = lecs[lid]
        b = briefs.get(lid, {})
        L.append(f"## {lid} · Week {b.get('week')} · {r['topic']}{' ★ new at IIIT-D' if b.get('novel') else ''}")
        L.append(f"*{b.get('summary', '')}*\n")
        if r.get("partial"):
            L.append(f"> ⚠ **Partial:** {r['partial']['reason']}. Videos were judged from their title and description "
                     "only and no clips could be made; the next `recommend` run redoes this lecture.\n")
        res = r.get("resources") or {}
        if res.get("note"):
            L.append(f"> {res['note']}\n")
        for kind, items in (res.get("items") or {}).items():
            L.append(f"**{KIND_TITLE.get(kind, kind)}**\n")
            for c in items:
                rv_ = c.get("review") or {}
                head = f"{c['rank']}. [{c['title']}]({c['url']}) — score {c['total']:.2f}"
                L.append(head)
                L.append(f"   {c.get('rationale', '')}")
                if rv_.get("review"):
                    L.append(f"   *Review:* {rv_['review']}" + (f" Use: {USE.get(rv_.get('use_as'), rv_.get('use_as'))}." if rv_.get("use_as") else ""))
                warns = [x["message"] for x in c.get("findings", []) if x["severity"] == "warning"]
                if warns:
                    L.append(f"   ⚠ {'; '.join(warns)}")
            L.append("")
        if res.get("clips"):
            L.append("**Clip playlist** (only the minutes that teach each part)\n")
            for k in res["clips"]:
                L.append(f"- {k['target'][:90]} → [{k['video'][:60]}]({k['url']}) {k['start']}–{k['end']} ({k['minutes']} min)")
            L.append("")
        ex = r.get("experts")
        if ex and ex.get("same_as"):
            L.append(f"**Possible guest speakers:** same topic as {ex['same_as']}; see its list and guest kit.\n")
        elif ex:
            L.append(f"**Possible guest speakers** (guest kit: `guest_kits/{lid}.md`)\n")
            for e in ex["experts"]:
                kind = {"iiitd": "IIIT-D faculty", "academic": "researcher", "industry": "industry"}.get(e["kind"], e["kind"])
                L.append(f"{e['rank']}. **{e['name']}** — {e.get('role') or kind}, {e.get('affiliation') or '—'}"
                         f"{' (' + e['country'] + ')' if e.get('country') else ''} · score {e['total']:.2f}"
                         f"{' · fit: ' + e['fit'] if e.get('fit') else ''}")
                if e.get("why"):
                    L.append(f"   {e['why']}")
                ev = [x for x in e.get("evidence", []) if x.get("url")][:2]
                if ev:
                    L.append("   Evidence: " + " · ".join(f"[{(x.get('title') or x['kind'])[:70]}]({x['url']})" + (f" ({x['year']})" if x.get("year") else "") for x in ev))
                links = " · ".join(f"[{k.replace('_', ' ')}]({v})" for k, v in (e.get("links") or {}).items())
                if links:
                    L.append(f"   {links}")
                warns = [x["message"] for x in e.get("findings", []) if x["severity"] == "warning"]
                if warns:
                    L.append(f"   ⚠ {'; '.join(warns)}")
            if not ex["experts"]:
                L.append("No candidate passed the checks for this lecture.")
            L.append("")
        n = res.get("counts")
        if n:
            L.append(f"<sub>{n['candidates']} candidates found · {n['passed_checks']} passed the checks · {n['rejected']} removed</sub>\n")
    (d / "report.md").write_text("\n".join(L), encoding="utf-8")
    rv.sync_review_file(run_id, lecs)
    return {"lectures": len(lecs), "report": str(d / "report.md")}
