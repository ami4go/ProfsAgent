"""Background runs of the real design pipeline (orchestrator/graph.py), one at a time, with the three professor gates.

Each app run is runs/app-<slug>-<n>/ with
  input.yaml      the pipeline form + run config (same shape as eval/inputs/*.yaml) and the app's own form
  app.json        what the app shows: status, the waiting gate, errors, the pause-until time, a history of events
  …               everything the pipeline writes (state.json, run.log, checkpoint.sqlite, proposal.md, course_template.xlsx)

Phases: "details" (ProfsAgent fills in the fields left blank → the professor checks the complete form at
gate0_details), then "design" (the pipeline with gate1_context, gate2_outcomes, gate3_proposal).
Statuses: queued → running → waiting (at a gate) → … → done | stopped (professor stopped it at a gate)
          paused (free AI quota used up; continues by itself at resume_at) | error (needs "Try again").
"""
from __future__ import annotations

import json
import os
import queue
import re
import threading
import time
import traceback
from pathlib import Path

import yaml

from profsagent.app import formmap
from profsagent.config import CACHE, RUNS, keys, models_cfg

GATES = ["gate0_details", "gate1_context", "gate2_outcomes", "gate3_proposal"]
PREFIX = "app-"


# ------------------------------------------------------------------ files (OneDrive can briefly lock a file just written)
def _write(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    for i in range(8):
        try:
            tmp.write_text(text, encoding="utf-8")
            os.replace(tmp, path)
            return
        except OSError:
            if i == 7:
                raise
            time.sleep(0.25 * (i + 1))


def read_meta(run_dir: Path) -> dict:
    p = run_dir / "app.json"
    for i in range(5):
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            if i == 4:
                raise
            time.sleep(0.2)
    return {}


def write_meta(run_dir: Path, meta: dict) -> None:
    _write(run_dir / "app.json", json.dumps(meta, indent=1, ensure_ascii=False, default=str))


def new_run_id(name: str, runs: Path = RUNS) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:32] or "course"
    n = 1
    while (runs / f"{PREFIX}{slug}-{n:02d}").exists():
        n += 1
    return f"{PREFIX}{slug}-{n:02d}"


# ------------------------------------------------------------------ free-tier quota
def quota_resume_at(now: float | None = None) -> float | None:
    """When the soonest AI model slot for the large 'generate' calls comes off its cooldown (data/cache/llm_state.json).
    None = no usable key at all (every key rejected)."""
    from profsagent.llm.client import _fp
    now = now or time.time()
    try:
        st = json.loads((CACHE / "llm_state.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        st = {}
    kmap = {"gemini": keys("GEMINI_API_KEYS"), "groq": keys("GROQ_API_KEYS")}
    untils, usable = [], False
    for ep in models_cfg()["roles"]["generate"]:
        for k in kmap.get(ep["provider"], []):
            if st.get(f"key:{ep['provider']}:{_fp(k)}", {}).get("until", 0) > now:   # key rejected (401/403)
                continue
            usable = True
            u = st.get(f"{ep['provider']}:{ep['model']}:{_fp(k)}", {}).get("until", 0)
            if u > now:
                untils.append(u)
    if not usable:
        return None
    return min(untils) if untils else now


# ------------------------------------------------------------------ the pipeline driver
class PipelineDriver:
    """Runs one step of the LangGraph pipeline: start, resume a gate with a decision, or continue after an error."""

    def step(self, run_id: str, kind: str, payload: dict | None = None) -> dict:
        from langgraph.types import Command
        from profsagent.agents.pipeline import make_runtime
        from profsagent.orchestrator import graph as G

        run_dir = RUNS / run_id
        app = G.build(str(run_dir / "checkpoint.sqlite"))
        cfg = {"configurable": {"thread_id": run_id}}
        try:
            snap = app.get_state(cfg)
            waiting = any(t.interrupts for t in snap.tasks)
            if kind == "resume" and not waiting:
                kind = "continue"
            if kind == "continue" and not snap.values:
                kind = "start"
            if kind == "start" and snap.values:
                kind = "continue"
            if kind == "start":
                spec = yaml.safe_load((run_dir / "input.yaml").read_text(encoding="utf-8"))
                rt = make_runtime(run_id, spec["form"], spec["run"])
                rt.save()
                G.register(rt)
                res = app.invoke({"run_id": run_id, "auto_approve": False, "done": []}, cfg)
            elif kind == "resume":
                res = app.invoke(Command(resume=payload), cfg)
            else:
                G._RT.pop(run_id, None)   # re-read state.json: a stage that failed half-way may have changed the in-memory copy
                res = app.invoke(None, cfg)
        finally:
            try:
                app.checkpointer.conn.close()
            except Exception:  # noqa: BLE001
                pass
        intr = res.get("__interrupt__") if isinstance(res, dict) else None
        if intr:
            return {"status": "waiting", "gate": intr[0].value.get("gate"), "payload": intr[0].value}
        if isinstance(res, dict) and res.get("rejected_at"):
            return {"status": "stopped", "gate": res["rejected_at"]}
        return {"status": "done"}


def classify(e: BaseException) -> tuple[str, str]:
    """(status, plain message) for an exception that stopped a run."""
    from profsagent.llm.client import AllEndpointsFailed
    name, text = type(e).__name__, str(e)
    if isinstance(e, AllEndpointsFailed):
        return "paused", "The free AI quota is used up for now."
    if name in ("ServiceUnavailable", "SessionExpired") or "Couldn't connect" in text or "7687" in text:
        return "error", "The course database (Neo4j) isn't running. Start it in Neo4j Desktop, then press Try again."
    if name in ("AuthError", "Neo4jError") and "auth" in text.lower():
        return "error", "Neo4j refused the password in .env. Check NEO4J_PASSWORD, then press Try again."
    return "error", f"Something went wrong ({name}). Your progress is saved; press Try again."


# ------------------------------------------------------------------ the manager
class RunManager:
    def __init__(self, runs: Path = RUNS, driver: PipelineDriver | None = None, tick_s: float = 20.0, filler=None):
        from profsagent.app.filler import DetailsFiller
        self.runs = runs
        self.driver = driver or PipelineDriver()
        self.filler = filler or DetailsFiller()
        self.q: queue.Queue = queue.Queue()
        self.lock = threading.RLock()
        self.current: str | None = None
        self.tick_s = tick_s
        self._stop = threading.Event()
        self.threads: list[threading.Thread] = []

    # ---- lifecycle
    def start(self) -> None:
        self.recover()
        for target in (self._worker, self._scheduler):
            t = threading.Thread(target=target, daemon=True, name=f"profsagent-{target.__name__}")
            t.start()
            self.threads.append(t)

    def stop(self) -> None:
        self._stop.set()
        self.q.put(None)

    def recover(self) -> None:
        """After a restart: runs that were queued or running continue; a decision that was sent is sent again."""
        for d in sorted(self.runs.glob(f"{PREFIX}*")):
            if not (d / "app.json").exists():
                continue
            m = read_meta(d)
            if m.get("status") in ("queued", "running"):
                job = m.get("pending") or {"kind": "continue"}
                self._log(d, m, "restarted: the app was closed while this run was working; continuing")
                m["status"] = "queued"
                write_meta(d, m)
                self.q.put((d.name, job["kind"], job.get("payload")))

    # ---- actions
    def create(self, ui_form: dict) -> tuple[str | None, dict]:
        """Save the professor's form and queue step 1: filling in what they left blank. Nothing is designed yet."""
        errs = formmap.validate(ui_form)
        if errs:
            return None, errs
        with self.lock:
            rid = new_run_id(ui_form["name"], self.runs)
            d = self.runs / rid
            d.mkdir(parents=True)
        _write(d / "input.yaml", yaml.safe_dump({"app_form": {k: v for k, v in ui_form.items() if k != "consent"}},
                                                allow_unicode=True, sort_keys=False, width=120))
        meta = {"run_id": rid, "title": formmap._s(ui_form["name"]), "by": formmap._s(ui_form["by"]), "created_at": time.time(),
                "consent": {"given": True, "at": time.time(), "text": formmap.CONSENT_TEXT},
                "status": "queued", "phase": "details", "pending": {"kind": "fill"}, "history": []}
        self._log(d, meta, f"created by {meta['by']}")
        write_meta(d, meta)
        self.q.put((rid, "fill", None))
        return rid, {}

    def _confirm_details(self, d: Path, m: dict, values: dict, by: str, comment: str) -> dict | None:
        """gate0_details approved: the complete, checked form becomes the pipeline's input. Returns field errors, or None."""
        spec = yaml.safe_load((d / "input.yaml").read_text(encoding="utf-8"))
        original = spec["app_form"]
        final = {**original, **{k: v for k, v in (values or {}).items() if k in ("name", "description", "topics_flexible", "external_research", *formmap.FILLABLE)}}
        errs = formmap.validate_complete(final)
        if errs:
            return errs
        fill = json.loads((d / "fill.json").read_text(encoding="utf-8")) if (d / "fill.json").exists() else {"fields": {}}
        suggested = fill.get("fields", {})
        same = lambda a, b: (sorted(a) if isinstance(a, list) else formmap._s(a)) == (sorted(b) if isinstance(b, list) else formmap._s(b))  # noqa: E731
        form, run_cfg = formmap.to_pipeline(final)
        _write(d / "input.yaml", yaml.safe_dump({"run": run_cfg, "form": form, "app_form": final, "app_form_original": original},
                                                allow_unicode=True, sort_keys=False, width=120))
        review = {"gate": "gate0_details", "decision": "approve", "by": by, "comment": comment, "at": time.time(),
                  "suggested_by_profsagent": sorted(suggested),
                  "accepted": sorted(k for k in suggested if same(final.get(k), suggested[k]["value"])),
                  "changed_by_professor": sorted(k for k in formmap.FILLABLE if not same(final.get(k), suggested[k]["value"] if k in suggested else original.get(k))),
                  "left_blank": sorted(k for k in formmap.FILLABLE if formmap.blank(final, k))}
        _write(d / "details_review.json", json.dumps(review, indent=1, ensure_ascii=False))
        return None

    def decide(self, rid: str, gate: str, decision: str, by: str, comment: str, values: dict | None = None) -> str | dict | None:
        """Queue the professor's answer to the waiting gate. Returns a problem to show (or field errors at gate0), or None."""
        d = self.runs / rid
        with self.lock:
            m = read_meta(d)
            if m.get("status") != "waiting" or m.get("gate") != gate:
                return "This step is no longer waiting for a decision. Reload the page."
            if decision not in ("approve", "reject"):
                return "Unknown decision"
            comment = (comment or "").strip()
            by = (by or m.get("by") or "professor").strip()
            if gate == "gate0_details":
                if decision == "reject":
                    if not comment:
                        return "Say briefly why you are stopping; it helps us improve the system."
                    _write(d / "details_review.json", json.dumps({"gate": gate, "decision": "reject", "by": by, "comment": comment, "at": time.time()}))
                    m.update(status="stopped", pending=None, payload=None)
                    self._log(d, m, f"{gate}: reject by {by} — {comment}")
                    write_meta(d, m)
                    return None
                errs = self._confirm_details(d, m, values or {}, by, comment)
                if errs:
                    return errs
                m.update(status="queued", phase="design", pending={"kind": "start"}, payload=None)
                self._log(d, m, f"{gate}: details confirmed by {by}" + (f" — {comment}" if comment else ""))
                write_meta(d, m)
                self.q.put((rid, "start", None))
                return None
            blocked = bool((m.get("payload") or {}).get("blocked"))
            if decision == "reject" and not comment:
                return "Say briefly why you are stopping; it helps us improve the system."
            if decision == "approve" and blocked and not comment:
                return "There are open problems. Give a reason for continuing anyway; it is recorded on the course sheet."
            payload = {"decision": decision, "by": by, "comment": comment}
            if decision == "approve" and blocked:
                payload["reason"] = comment
            m.update(status="queued", pending={"kind": "resume", "payload": payload})
            self._log(d, m, f"{gate}: {decision} by {payload['by']}" + (f" — {comment}" if comment else ""))
            write_meta(d, m)
        self.q.put((rid, "resume", payload))
        return None

    def retry(self, rid: str) -> str | None:
        d = self.runs / rid
        with self.lock:
            m = read_meta(d)
            if m.get("status") not in ("paused", "error"):
                return "This run isn't stopped."
            kind = self._resume_kind(m)
            m.update(status="queued", pending={"kind": kind}, resume_at=None)
            self._log(d, m, "try again")
            write_meta(d, m)
        self.q.put((rid, kind, None))
        return None

    @staticmethod
    def _resume_kind(m: dict) -> str:
        """What 'try again' or the quota timer restarts: filling in the details, or the design pipeline."""
        return "fill" if m.get("phase") == "details" else "continue"

    # ---- threads
    def _worker(self) -> None:
        while not self._stop.is_set():
            job = self.q.get()
            if job is None:
                return
            rid, kind, payload = job
            d = self.runs / rid
            with self.lock:
                m = read_meta(d)
                if m.get("status") != "queued":
                    continue
                m["status"] = "running"
                m["started_at"] = time.time()
                write_meta(d, m)
                self.current = rid
            try:
                out = self.filler.fill(d) if kind == "fill" else self.driver.step(rid, kind, payload)
                with self.lock:
                    m = read_meta(d)
                    m.update(out, pending=None, error=None, resume_at=None, pause_count=0)
                    m.setdefault("payload", None)
                    if out["status"] != "waiting":
                        m["payload"] = None
                    self._log(d, m, {"waiting": f"waiting at {out.get('gate')}", "done": "finished", "stopped": f"stopped at {out.get('gate')}"}[out["status"]])
                    if kind == "fill":
                        m["filled"] = out.get("payload", {}).get("filled")
                    write_meta(d, m)
            except Exception as e:  # noqa: BLE001 — the run's files and checkpoint stay; the professor or the scheduler continues it
                status, msg = classify(e)
                with (d / "app_error.log").open("a", encoding="utf-8") as f:
                    f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + traceback.format_exc() + "\n")
                with self.lock:
                    m = read_meta(d)
                    m.update(status=status, error={"message": msg, "detail": f"{type(e).__name__}: {str(e)[:300]}"}, pending=None)
                    if status == "paused":
                        at = quota_resume_at()
                        if at is None:
                            m.update(status="error", error={"message": "No AI key works any more (all were rejected). Check the keys in .env.",
                                                            "detail": m["error"]["detail"]})
                        else:   # back off when the quota fails again right after a pause, so the KG isn't reloaded every minute
                            n = m.get("pause_count", 0)
                            m["resume_at"] = max(at, time.time() + min(120 * 2 ** n, 3600)) + 30
                            m["pause_count"] = n + 1
                    self._log(d, m, f"{m['status']}: {m['error']['detail']}")
                    write_meta(d, m)
            finally:
                self.current = None

    def _scheduler(self) -> None:
        while not self._stop.wait(self.tick_s):
            for d in sorted(self.runs.glob(f"{PREFIX}*")):
                try:
                    if not (d / "app.json").exists():
                        continue
                    with self.lock:
                        m = read_meta(d)
                        if m.get("status") == "paused" and (m.get("resume_at") or 0) <= time.time():
                            kind = self._resume_kind(m)
                            m.update(status="queued", pending={"kind": kind})
                            self._log(d, m, "quota should be back: continuing")
                            write_meta(d, m)
                            self.q.put((d.name, kind, None))
                except Exception:  # noqa: BLE001 — one unreadable folder must not stop the scheduler
                    continue

    @staticmethod
    def _log(d: Path, m: dict, event: str) -> None:
        m.setdefault("history", []).append({"at": time.time(), "event": event})

    # ---- reading
    def list(self) -> list[dict]:
        out = []
        for d in self.runs.glob(f"{PREFIX}*"):
            if (d / "app.json").exists():
                try:
                    m = read_meta(d)
                except Exception:  # noqa: BLE001
                    continue
                out.append({k: m.get(k) for k in ("run_id", "title", "by", "created_at", "status", "gate", "resume_at")})
        return sorted(out, key=lambda r: r.get("created_at") or 0, reverse=True)

    def queue_position(self, rid: str) -> int:
        with self.q.mutex:
            ids = [j[0] for j in list(self.q.queue) if j]
        return ids.index(rid) + 1 if rid in ids else 0
