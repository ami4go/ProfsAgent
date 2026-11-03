"""Deliverable C orchestration for one approved course run (scripts/run_delivery.py).

  briefs   → runs/<id>/delivery/briefs.json + briefs.md
  survey   → runs/<id>/delivery/survey.yaml (professor's answers; nothing is searched without them)
  recommend→ per lecture runs/<id>/delivery/lectures/<lecture>.json (resources, clips, experts), guest_kits/<lecture>.md,
             and the proposed delivery mix mix/<lecture>.json (mix.py) with the NotebookLM pack for its NotebookLM parts
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
    """Per topic: plan its components over all its lectures (D5), find the video segments that teach them (D6), then
    per lecture the readings and practice, the NotebookLM pack for what no video teaches, and guest speakers."""
    from profsagent.delivery.components import plan_topic, topic_groups
    from profsagent.delivery.experts import guest_kit, recommend_experts
    from profsagent.delivery.notebooklm import pack
    from profsagent.delivery.resources import plan_queries, recommend_lecture
    from profsagent.delivery.videos import deliver_topic
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
    def done(k):   # a lecture saved as partial (transcripts were blocked) or before component plans is redone
        lec = read_json(d / "lectures" / f"{k}.json") or {}
        return bool(lec) and not lec.get("partial") and "components" in lec
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
    ppath = d / "components.json"
    plans = read_json(ppath, {})
    groups = topic_groups(briefs)
    warned = False
    for tid in dict.fromkeys(briefs[lid]["topic_id"] for lid in sorted(todo)):
        group = groups[tid]
        lids = [b["lecture_id"] for b in group if b["lecture_id"] in todo]
        log(f"topic {tid} · {group[0]['topic']} · lectures {', '.join(b['lecture_id'] for b in group)} (doing {', '.join(lids)})")
        plan = plans.get(tid)
        if refresh or not plan or [x["lecture_id"] for x in plan["lectures"]] != [b["lecture_id"] for b in group]:
            plan = plan_topic(llm, st, group, run_id, log)
            plans[tid] = plan
            write_json(ppath, plans)
        vlids = [lid for lid in lids if todo[lid].get("want_videos") or todo[lid].get("want_clips")]
        vres = deliver_topic(llm, st, plan, briefs, vlids, queries, run_id, log) if vlids else {}
        shown: set[str] = set()                   # readings / practice already given to an earlier lecture of the topic
        guests = None                             # the lecture whose guest list this topic uses
        for b in group:
            lid = b["lecture_id"]
            if lid not in lids:
                prev = read_json(d / "lectures" / f"{lid}.json") or {}
                shown |= _links(prev)
                if (prev.get("experts") or {}).get("experts") and guests is None:
                    guests = lid
                continue
            want = todo[lid]
            log(f"{lid} · {b['topic']} · wants: {', '.join(k[5:] for k, v in want.items() if k.startswith('want_') and v)}")
            comps = [c for c in plan["components"] if c["lecture_id"] == lid]
            earlier = [c for c in plan["components"] if c["lecture_id"] < lid]
            v = vres.get(lid) or {}
            res = {"lecture_id": lid, "topic": b["topic"], "generated_at": now(), "components": comps}
            if earlier:
                res["continues"] = earlier[-1]["lecture_id"]
            if any(val for k, val in want.items() if k.startswith("want_") and k != "want_guest"):
                q = dict(queries[lid])
                if earlier and comps:             # a later lecture on the topic searches for its own parts
                    q["reading_queries"] = [f"{comps[0]['title']} {b['topic']}"]
                    q["practice_queries"] = [f"{comps[0]['title']} hands-on tutorial"]
                r = recommend_lecture(llm, st, b, want, q, run_id, log, components=comps, videos=v.get("videos", []), exclude=shown)
                if v:
                    if v["videos"]:
                        r["items"] = {"video": v["videos"], **{k: x for k, x in r["items"].items() if k != "video"}}
                    r["reserve"]["video"] = v["reserve"]
                    r["clips"], r["timeline"] = v["clips"], v["timeline"]
                    r["rejected"] = (r.get("rejected") or []) + v["rejected"]
                    r["counts"]["videos_used"] = len(v["videos"])
                    if v.get("partial"):
                        r["partial"] = v["partial"]
                r["components"] = comps
                srcs = {k: r["items"].get(k, []) for k in ("video", "reading", "practice")}
                md, summary = pack(st, b, comps, earlier, v.get("timeline") or [], srcs)
                (d / "notebooklm").mkdir(exist_ok=True)
                (d / "notebooklm" / f"{lid}.md").write_text(md, encoding="utf-8")
                r["notebooklm"] = summary
                res["resources"] = r
                shown |= _links(res)
            if want.get("want_guest"):
                if guests is None:
                    talk_titles = [c["title"] for blk in ("items", "reserve") for kind in ((res.get("resources") or {}).get(blk) or {}).values() for c in kind]
                    vids = [c for k in ("video", "recorded_lecture") for blk in ("items", "reserve")
                            for c in ((res.get("resources") or {}).get(blk) or {}).get(k, [])]
                    res["experts"] = recommend_experts(llm, st, b, queries[lid], talk_titles, run_id, log, videos=vids)
                    kit = guest_kit(st, b, res["experts"]["experts"])
                    (d / "guest_kits").mkdir(exist_ok=True)
                    (d / "guest_kits" / f"{lid}.md").write_text(kit, encoding="utf-8")
                    guests = lid
                else:                             # same topic: one guest list, kept with its first lecture
                    res["experts"] = {"same_as": guests, "experts": [], "reserve": [], "rejected": [], "counts": {}}
            if (res.get("resources") or {}).get("partial"):
                res["partial"] = res["resources"]["partial"]
            write_json(d / "lectures" / f"{lid}.json", res)
            if res.get("resources") and comps:
                try:                              # the proposed mix; an approved one with the same parts is kept
                    from profsagent.delivery import mix
                    mix.propose(run_id, lid, log=log, keep_approved=True)
                except Exception as e:  # noqa: BLE001 — the lecture's results stay; the mix can be made later (run_delivery.py mix)
                    log(f"  mix {lid}: not made ({type(e).__name__}: {str(e)[:120]})")
            if transcripts_blocked() and not warned:
                warned = True
                log(f"  ! YouTube is blocking transcript requests from this IP (since {transcripts_blocked()}). No more are sent "
                    "this run; components of the affected lectures go to the NotebookLM pack, and those lectures are saved "
                    "as partial. Run the same recommend command later (no --refresh needed) to redo only the partial lectures.")
            log(f"  saved {lid} · YouTube units used today: {YouTube().quota.used()}")
    part = [k for k in sorted(todo) if (read_json(d / "lectures" / f"{k}.json") or {}).get("partial")]
    if part:
        log(f"partial lectures ({len(part)}), redone by the next run: {', '.join(part)}")
    log(f"AI calls this session: {llm.totals['calls']}")
    return render(run_id)


def _links(lec: dict) -> set[str]:
    r = lec.get("resources") or {}
    return {c["url"].split("#")[0].rstrip("/") for blk in ("items", "reserve") for k in ("reading", "practice")
            for c in (r.get(blk) or {}).get(k, []) if c.get("url")}


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
        if r.get("components"):
            tl = {x["component"]: x for x in res.get("timeline") or []}
            L.append("**Lecture plan** (what each part teaches, for how long, and how it is delivered)\n")
            L.append("| # | Part | Min | Delivered by |")
            L.append("|---|---|---|---|")
            for c in r["components"]:
                row = tl.get(c["id"]) or {}
                how = row.get("delivery") or ("in class" if c.get("in_class") else "—")
                if how == "video":
                    how = " + ".join(f"[{s['video'][:45]}]({s['url']}) {s['start']}–{s['end']} "
                                     f"({'fully' if s['verdict'] == 'teaches_fully' else 'partly'})" for s in row["segments"])
                    if row.get("gap"):
                        how += " + NotebookLM" + (f" for: {'; '.join(row['gap']['missing'][:3])}" if row["gap"].get("missing") else "")
                elif how == "notebooklm":
                    how = f"NotebookLM video (`notebooklm/{lid}.md`)"
                elif how == "in_class":
                    how = f"in class ({c.get('kind', '').replace('_', ' ')})"
                L.append(f"| {c['id'].split('.')[-1]} | **{c['title']}** — {c['teaches'][:160]} | {c['minutes']} | {how} |")
            L.append("")
            if res.get("notebooklm"):
                L.append(f"NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `{res['notebooklm']['pack']}`\n")
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
        if res.get("clips") and not r.get("components"):    # with a plan, the clips are in the lecture plan above
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
