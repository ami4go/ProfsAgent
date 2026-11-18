"""Outputs of a run (runs/<run>/delivery/ytlecture/):

  lectures/<id>.json   everything about one lecture: parts, chosen clips with scores and checks, alternates, gaps, status
  playlists.json/.js   the chosen clips per lecture in the player's format
  player.html          plays a lecture's clips back to back (YouTube IFrame API; serve the folder over http)
  PLAYLISTS.md         the readable version for the professor
  TRACE.md             this run's own methods log: every query per tool, what each agent decided, what was dropped and why
"""
from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path

from profsagent.delivery.common import now, read_json, write_json
from profsagent.ytlecture.evidence import ts

CHECK = {"captions": "transcript", "browser": "browser-tx", "notes": "notes", "chapters": "chapters"}
MODE_HINT = {"ready": "Deliver with YouTube clips (mode 2).",
             "usable_with_gaps": "Mode 2 works for most parts; teach the gap parts live (mode 1) or with an AI slide video (mode 3).",
             "not_enough_video": "Too little good video: use mode 1 (professor) or mode 3 (AI slide video) for this lecture."}


def _clip_out(k: dict, v: dict, part: dict) -> dict:
    chk = k.get("check") or {}
    return {"video": k["video"], "start": ts(k["a"]), "end": ts(k["b"]), "a": k["a"], "b": k["b"], "clip_s": k["b"] - k["a"],
            "title": v["title"], "channel": v["channel"], "published": (v.get("published") or "")[:10], "views": v.get("views"),
            "tier": v.get("tier"), "video_length": ts(v.get("duration_s") or 0), "check": CHECK.get(k["evidence"], k["evidence"]),
            "why": k["summary"], "covers": [part["must_cover"][i] for i in k["covers"] if i < len(part["must_cover"])],
            "rating": k["rating"], "score": k.get("score"), "score_notes": k.get("score_notes", []),
            "verifier": {x: chk.get(x) for x in ("coverage", "standalone", "accurate", "recommend", "issue", "checker")} if chk else None,
            "reader": k.get("reader"), "concerns": k.get("concerns") or "",
            "watch_url": f"https://www.youtube.com/watch?v={k['video']}&t={int(k['a'])}s",
            "embed_url": f"https://www.youtube.com/embed/{k['video']}?start={int(k['a'])}&end={int(k['b'])}"}


def lecture_json(run_id: str, topic: dict, lp: dict, brief: dict, lck: dict, cands: dict, evs: dict, fast: bool) -> dict:
    asm = lck["assembly"]
    parts = []
    used = {(k["video"], k["a"]) for pp in asm["plan"] for k in pp["clips"]}
    n = 0
    for pp in asm["plan"]:
        if pp["part"] >= 0:
            p = lp["parts"][pp["part"]]
            n = pp["part"] + 1
            label = f"{n}. {p['title']}"
        else:                                            # an extra section the readers found on the topic
            k0 = pp["clips"][0]
            p = {"title": pp["title"], "teaches": k0["summary"], "must_cover": [pp["title"]], "minutes": round((k0["b"] - k0["a"]) / 60),
                 "kind": "extra"}
            label = f"{n}+ {pp['title']} (extra)"
        same = (lambda k: k["part"] == pp["part"]) if pp["part"] >= 0 else (lambda k: False)
        alts = sorted([k for k in lck["clips"] if same(k) and (k["video"], k["a"]) not in used and not k.get("gate")],
                      key=lambda k: -(k.get("score") or 0))[:2]
        gated = [k for k in lck["clips"] if same(k) and k.get("gate")]
        parts.append({"part": label, "title": p["title"], "teaches": p["teaches"], "must_cover": p["must_cover"],
                      "minutes": p["minutes"], "kind": p["kind"], "partial": pp["partial"], "gap": not pp["clips"],
                      "second_explanation": pp.get("second_explanation"),
                      "clips": [_clip_out(k, cands[k["video"]], p) for k in pp["clips"]],
                      "alternates": [_clip_out(k, cands[k["video"]], p) for k in alts],
                      "rejected_clips": [{"video": k["video"], "title": cands[k["video"]]["title"][:80], "start": ts(k["a"]),
                                          "end": ts(k["b"]), "why": k["gate"]} for k in gated][:4],
                      "part_s": sum(k["b"] - k["a"] for k in pp["clips"])})
    return {"id": lp["lecture_id"], "lecture_id": lp["lecture_id"], "topic": topic["title"], "slot_min": lp["slot_minutes"],
            "lo": "; ".join(f"{lo['id']} (BL{lo.get('bloom_level')}): " + lo["statement"].replace("{n} of {m}", "most")
                    for lo in brief["learning_outcomes"]),
            "generated_at": now(), "status": asm["status"], "recommendation": MODE_HINT[asm["status"]], "fill": asm["fill"],
            "video_total_s": asm["total_s"], "warnings": asm["warnings"], "fast_moving": fast,
            "gaps": [lp["parts"][i]["title"] for i in asm["gaps"]], "parts": parts,
            "stats": {"videos_read": len(lck.get("read", [])), "clips_cut": len(lck.get("clips", [])),
                      "clips_gated": sum(1 for k in lck.get("clips", []) if k.get("gate")),
                      "evidence": dict(Counter(evs[v]["source"] for v in evs))}}


def write_all(run_id: str, d: Path, trace) -> dict:
    lecs = [read_json(p) for p in sorted((d / "lectures").glob("*.json"))]
    lecs = [x for x in lecs if x]
    pl = [{k: x[k] for k in ("id", "topic", "slot_min", "lo", "video_total_s", "status", "recommendation")} |
          {"parts": [{"part": p["part"], "clips": p["clips"], "part_s": p["part_s"], "gap": p["gap"]} for p in x["parts"]]} for x in lecs]
    write_json(d / "playlists.json", pl)
    (d / "playlists.js").write_text("window.PLAYLISTS = " + json.dumps(pl, ensure_ascii=False) + ";\n", encoding="utf-8")
    shutil.copyfile(Path(__file__).with_name("player.html"), d / "player.html")
    (d / "PLAYLISTS.md").write_text(playlists_md(lecs), encoding="utf-8")
    (d / "TRACE.md").write_text(trace_md(trace.rows, lecs), encoding="utf-8")
    write_json(d / "trace.jsonl.json", trace.rows)
    return {"dir": str(d), "lectures": {x["id"]: {"status": x["status"], "video_min": round(x["video_total_s"] / 60),
                                                    "slot_min": x["slot_min"], "gaps": x["gaps"]} for x in lecs}}


def playlists_md(lecs: list[dict]) -> str:
    md = ["# YouTube lecture playlists (delivery mode 2)", "",
          "Each lecture is taught by the clips below, in order. `check`: **transcript** / **browser-tx** = clip read in the "
          "captions; **notes** = read in AI notes of the video; **chapters** = placed from chapter titles only (preview it).", ""]
    for x in lecs:
        md += [f"## {x['id']}: {x['topic']}", f"*{x['lo']}*", "",
               f"Slot {x['slot_min']} min · video **{ts(x['video_total_s'])}** ({round(100 * x['fill'])}%) · status **{x['status']}** · {x['recommendation']}", ""]
        for w in x["warnings"]:
            md.append(f"> ⚠ {w}")
        for p in x["parts"]:
            md.append(f"**{p['part']}** ({p['minutes']} min planned, {ts(p['part_s'])} found){' · partly covered' if p['partial'] else ''}"
                      f"{' · includes a second explanation by another teacher' if p.get('second_explanation') else ''}")
            md.append("")
            if p["gap"]:
                md += ["*No clip passed the checks: teach this part another way.*", ""]
                continue
            md += ["| Clip | Video | Length | Check | Score | Why |", "|---|---|---|---|---|---|"]
            for c in p["clips"]:
                v = c["verifier"] or {}
                cov = f", covers {round(100 * v['coverage'])}%" if v.get("coverage") is not None else ""
                md.append(f"| [{c['start']}–{c['end']}]({c['watch_url']}) | {c['title'][:70]} ({c['channel']}, {c['published'][:4]}) | "
                          f"{ts(c['clip_s'])} | {c['check']} | {c['score']}{cov} | {c['why']} |")
            if p["alternates"]:
                md.append("")
                md.append("Alternates: " + "; ".join(f"[{a['title'][:50]} {a['start']}–{a['end']}]({a['watch_url']})" for a in p["alternates"]))
            md.append("")
    return "\n".join(md)


def trace_md(rows: list[dict], lecs: list[dict]) -> str:
    """The run's own methods log, in the order things happened (what METHODS.md was written by hand for)."""
    md = ["# How these playlists were found (trace of this run)", "",
          "Every tool call, AI decision and filter, in order. Numbers in brackets are results returned.", ""]
    tools = Counter(r["tool"] for r in rows if r["kind"] == "tool")
    ai = Counter((r["agent"], (r["endpoint"] or "").replace("cache(", "").split(":")[1] if ":" in (r["endpoint"] or "") else r["endpoint"])
                 for r in rows if r["kind"] == "ai")
    md += ["## Totals", "", "| Tool | Calls |", "|---|---|"] + [f"| {k} | {v} |" for k, v in tools.most_common()]
    md += ["", "| Agent | Model | Calls |", "|---|---|---|"] + [f"| {a} | {m} | {n} |" for (a, m), n in sorted(ai.items())]
    md += ["", "## Log", ""]
    scope = None
    for r in rows:
        if r.get("scope") != scope:
            scope = r.get("scope")
            md += ["", f"### {scope}", ""]
        if r["kind"] == "tool":
            md.append(f"- `{r['tool']}` {r['query']} → {r['results']}" + (f" ({r['note']})" if r.get("note") else ""))
        elif r["kind"] == "ai":
            md.append(f"- **{r['agent']}** via {r['endpoint']} · {r['tokens']} tokens" + (f" · {r['note']}" if r.get("note") else ""))
        else:
            extra = {k: v for k, v in r.items() if k not in ("t", "kind", "scope", "msg")}
            md.append(f"- {r['msg']}" + (f": `{json.dumps(extra, ensure_ascii=False)[:600]}`" if extra else ""))
    return "\n".join(md)
