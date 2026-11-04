"""One background delivery job in its own process (so the app can cancel it), over Vihan's deliverable C backend.

    python -m profsagent.app.delivery_step <run_id> recommend|material|health <args.json>

recommend: profsagent.delivery.pipeline.recommend(run_id, lectures, refresh), then graph.write (skipped if Neo4j is down)
material:  profsagent.content.generate.generate_material(run_id, lecture, options) (Parth's deliverable B: slides)
health:    profsagent.delivery.review.health(run_id)
Result: runs/<id>/delivery/app_step_result.json = {"ok": ...} or {"error": {type, message, quota}}. C's log lines go to
stdout (the app's terminal) and to runs/<id>/delivery/delivery.log, which the lecture pages show.
"""
from __future__ import annotations

import json
import os
import sys
import traceback


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8", errors="replace")
    rid, kind, af = argv[1], argv[2], argv[3]
    import profsagent.config  # noqa: F401  (loads .env)
    from profsagent.delivery.common import out_dir
    if not os.environ.get("GROQ_API_KEYS") and os.environ.get("GROQ_API_KEY"):
        os.environ["GROQ_API_KEYS"] = os.environ["GROQ_API_KEY"]
    args = json.loads(open(af, encoding="utf-8").read())
    try:
        if kind == "recommend":
            from profsagent.delivery import pipeline
            out = {"ok": pipeline.recommend(rid, lectures=args.get("lectures"), refresh=bool(args.get("refresh")))}
            try:
                from profsagent.delivery.graph import write
                out["graph"] = write(rid)
            except Exception as e:  # noqa: BLE001 — the files are complete; Neo4j records can be written later
                out["graph"] = f"skipped ({type(e).__name__})"
        elif kind == "mix":                 # C's delivery mix for one lecture (D7 reasons; D8 quiz on approval)
            from profsagent.delivery import mix
            from profsagent.delivery.pipeline import Log
            lid, act, log = args["lecture"], args.get("action") or "propose", Log(rid)
            if act == "approve":
                r = mix.approve(rid, lid, by=args.get("by") or "Professor", log=log)
            elif act == "preset":
                r = mix.save(rid, lid, preset=args.get("preset"), by=args.get("by") or "Professor", log=log)
            else:
                r = {"mix": mix.propose(rid, lid, note=args.get("note") or "", log=log)}
            if r.get("errors"):
                raise ValueError("; ".join(str(v) for v in r["errors"].values()))
            out = {"ok": {"lecture": lid, "status": r["mix"]["status"]}}
        elif kind == "material":
            from profsagent.content.generate import generate_material
            from profsagent.delivery.pipeline import Log
            m = generate_material(rid, args["lecture"], args.get("options") or {}, log=Log(rid))
            out = {"ok": {"lecture": args["lecture"], "slides": m.get("slides"), "errors": m.get("errors"), "status": m.get("status")}}
        elif kind == "health":
            from profsagent.delivery import review
            out = {"ok": {"dead": review.health(rid)}}
        else:
            out = {"error": {"type": "ValueError", "message": f"unknown job {kind}"}}
    except BaseException as e:  # noqa: BLE001 — recommend raises SystemExit when no lecture asked for anything
        if isinstance(e, KeyboardInterrupt):
            raise
        from profsagent.llm.client import AllEndpointsFailed
        out = {"error": {"type": type(e).__name__, "message": str(e)[:2000], "quota": isinstance(e, AllEndpointsFailed),
                         "traceback": traceback.format_exc()}}
    (out_dir(rid) / "app_step_result.json").write_text(json.dumps(out, ensure_ascii=False, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
