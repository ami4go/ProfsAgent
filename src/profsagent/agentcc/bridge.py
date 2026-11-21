"""The stand-in for LLMClient in a run with `run.agent: claude_code`.

The pipeline keeps calling what it always calls (LLMClient.structured, agents.loop.generate, ExternalResearch.run);
for such a run each of those writes one request and waits until the Claude Code session hands back a finished answer.
Generation, checking and fixing happen in the session: while it works it may send drafts, which this process checks
with the pipeline's own validators and fixers (the same `engine.check` + `apply_fixers` that generate() uses), so the
answer usually arrives with no open error and no repair call (R1) is ever made.
"""
from __future__ import annotations

import copy
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from pydantic import BaseModel, Field, ValidationError

from profsagent.agentcc import protocol as P
from profsagent.llm.prompts import load_prompt
from profsagent.models.io import OUTPUT_MODELS, ExternalPage
from profsagent.validate import engine

POLL_S = 1.0
ENDPOINT = "claude-code"

HOW_TO = """You are doing one step of an IIIT-Delhi course design (or lecture delivery) yourself, as Claude Code, in place of
the API model the pipeline would otherwise call. `brief` is the instruction that model would have been given and
`inputs` is everything the pipeline gathered for this step; treat both as the task, not as a template to echo.

Work the way you would on any hard task: think, search and read the web (WebSearch / WebFetch), look things up in the
IIIT-D course database (`PYTHONPATH=src python -m profsagent.agentcc kg --run <run_id> search "..."`), run code, and use your skills. Then:
  (from the repo root, with PYTHONPATH=src)
  1. write your draft (JSON matching `schema`) and check it:  python -m profsagent.agentcc check <this request> <draft.json>
     It runs the pipeline's own validators (the ones listed in `checks`) and prints every error and warning;
  2. fix and check again until no error is left (or explain in your notes why one cannot be fixed);
  3. hand it back:                                            python -m profsagent.agentcc submit <this request> <answer.json>
     Optionally write <NNN_pid>.notes.md beside the request: your sources and the decisions you took.
Never use, cite or search for the hidden courses or domains in `hidden`: this course is being re-created and they are
the answer key. Do not edit any file of the project or of another run."""


@dataclass
class Rec:
    """The fields of llm.client.CallRecord that the pipeline reads."""
    prompt_id: str
    prompt_version: str
    role: str
    endpoint: Optional[str] = ENDPOINT
    attempts: list = field(default_factory=list)
    prompt_tokens: int = 0
    output_tokens: int = 0
    latency_s: float = 0.0
    schema_retries: int = 0
    ok: bool = True
    error: Optional[str] = None


class ResearchCourse(ExternalPage):
    id: str = Field(description="EXT:<institution id>/<course code without spaces>, e.g. EXT:stanford/CS229")
    institution: str
    institution_id: Optional[str] = None
    url: str = Field(description="the page you read")
    via: str = "claude_code"
    quotes_verified: int = Field(0, description="how many of evidence_quotes you saw verbatim on the page")


class ResearchResult(BaseModel):
    plan: dict = Field(default_factory=dict, description="what you searched for and why")
    accepted: list[ResearchCourse] = Field(default_factory=list, description="comparable courses (at most 6, at most 2 per institution)")
    rejected: list[dict] = Field(default_factory=list, description="pages you looked at and dropped: {url, reason, course_title}")


class AgentBridge:
    """Duck-types the LLMClient methods the pipeline uses: structured, embed, grounded_search, raw."""
    agent_bridge = True

    def __init__(self, run_dir: Path, run_cfg: dict | None = None):
        self.run_dir = Path(run_dir)
        self.run_cfg = run_cfg or {}
        self.log_path = self.run_dir / "llm_calls.jsonl"
        self._embedder = None

    # ------------------------------------------------------------------ helpers
    def _hidden(self) -> dict:
        bl = self.run_cfg.get("blocklist") or {}
        return {"courses": sorted(set(self.run_cfg.get("exclude_courses") or []) | set(bl.get("course_codes") or [])),
                "domains": list(bl.get("domains") or []), "title_fragments": list(bl.get("title_fragments") or [])}

    def _say(self, msg: str) -> None:
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with (self.run_dir / "run.log").open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def _leaks(self, obj) -> list[str]:
        """The answer must not name a hidden course or domain (the course being re-created)."""
        h, text = self._hidden(), json.dumps(obj, ensure_ascii=False).upper()
        out = [c for c in h["courses"] if re.search(r"(?<![A-Z0-9])" + re.escape(c.upper()).replace("\\ ", r"\s?") + r"(?![0-9])", text)]
        out += [d for d in h["domains"] if d.upper() in text]
        return out

    def _request(self, pid: str, version: str, kind: str, brief: str, inputs: str, schema: dict, checks: list[str] | None,
                 role: str = "generate", extra: dict | None = None) -> Path:
        req = P.next_request_path(self.run_dir, pid)
        P.write_json(req, {"id": P.stem(req), "run_id": self.run_dir.name, "pid": pid, "prompt_version": version, "kind": kind,
                           "role": role, "created_at": time.time(), "owner_pid": os.getpid(), "how_to": HOW_TO, "hidden": self._hidden(),
                           "checks": checks or [], "brief": brief, "inputs": inputs, "schema": schema, **(extra or {})})
        self._say(f"  [{pid}] handed to Claude Code (request {req.name}); waiting for its answer")
        return req

    def _wait(self, req: Path, evaluate: Callable[[dict], dict], parse: Callable[[dict], object]):
        """Serve draft checks until an answer parses; returns (parsed answer, drafts checked, seconds)."""
        t0, drafts, k = time.time(), 0, 0
        draft, answer, check = P.sibling(req, "draft.json"), P.sibling(req, "answer.json"), P.sibling(req, "check.json")
        while True:
            if draft.exists():
                drafts += 1
                obj = P.read_json(draft)
                rep = {"for": "draft", "n": drafts, "at": time.time(), **evaluate(obj)}
                draft.replace(draft.with_name(f"{P.stem(req)}.draft{drafts:02d}.json"))
                P.write_json(check, rep)
            if answer.exists():
                k += 1
                obj = P.read_json(answer)
                rep = evaluate(obj)
                if rep.get("schema_errors") or rep.get("hidden_named"):
                    answer.replace(answer.with_name(f"{P.stem(req)}.answer-rejected{k:02d}.json"))
                    P.write_json(check, {"for": "answer", "rejected": True, "at": time.time(), **rep})
                else:
                    secs = round(time.time() - t0, 1)
                    P.write_json(P.sibling(req, "done.json"), {"accepted_at": time.time(), "seconds": secs, "drafts": drafts,
                                                             "errors": rep.get("errors", []), "warnings": len(rep.get("warnings", []))})
                    return parse(obj), drafts, secs
            time.sleep(POLL_S)

    def _schema_check(self, model_cls: type[BaseModel], obj) -> tuple[BaseModel | None, list[str]]:
        try:
            return model_cls.model_validate(obj), []
        except ValidationError as e:
            return None, [f"{'.'.join(str(x) for x in er['loc'])}: {er['msg']}" for er in e.errors()[:40]]

    def _logcall(self, pid: str, version: str, role: str, secs: float, drafts: int, req: Path) -> None:
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.time(), "prompt_id": pid, "prompt_version": version, "role": role, "endpoint": ENDPOINT,
                                "ok": True, "latency_s": secs, "drafts_checked": drafts, "request": req.name}) + "\n")

    # ------------------------------------------------------------------ LLMClient.structured: one step, schema only
    def structured(self, *, system: str, user: str, model_cls: type[BaseModel], role: str = "generate", temperature: float = 0.2,
                   prompt_id: str = "?", prompt_version: str = "?", run_id: str | None = None, **_kw):
        req = self._request(prompt_id, prompt_version, "structured", system, user, model_cls.model_json_schema(), None, role)

        def evaluate(obj):
            m, errs = self._schema_check(model_cls, obj)
            return {"schema_errors": errs, "hidden_named": self._leaks(obj) if m else [], "errors": [], "warnings": []}
        obj, drafts, secs = self._wait(req, evaluate, lambda o: model_cls.model_validate(o))
        self._logcall(prompt_id, prompt_version, role, secs, drafts, req)
        self._say(f"  [{prompt_id}] answer accepted from Claude Code after {secs:.0f}s ({drafts} draft check{'s' if drafts != 1 else ''})")
        return obj, Rec(prompt_id, prompt_version, role, latency_s=secs)

    # ------------------------------------------------------------------ agents.loop.generate: one step, with the stage's validators
    def generate(self, rt, pid: str, ctx: dict, *, apply: Callable[[dict, dict], dict], stages: list[str],
                 frozen: set[str] | None = None, role: str = "generate", **_kw) -> tuple[dict, list[dict], dict]:
        p = load_prompt(pid)
        system, user = p.render(**ctx)
        model_cls = OUTPUT_MODELS[pid]
        req = self._request(pid, p.version, "generate", system, user, model_cls.model_json_schema(), stages, role)

        def run_checks(comp: dict):
            vs = engine.check(apply(copy.deepcopy(rt.state), comp), stages)
            comp2, vs2, fixes = engine.apply_fixers(rt.state, comp, apply, stages, vs)
            return comp2, vs, vs2, fixes

        def evaluate(obj):
            m, errs = self._schema_check(model_cls, obj)
            if not m:
                return {"schema_errors": errs, "hidden_named": [], "errors": [], "warnings": []}
            _, _, vs2, fixes = run_checks(m.model_dump())
            errors = engine.errors(vs2)
            return {"schema_errors": [], "hidden_named": self._leaks(obj), "errors": engine.strip_v2(errors),
                    "warnings": engine.strip_v2([x for x in vs2 if x not in errors]),
                    "fixers_applied": [f["fixer"] for f in fixes if f["accepted"]]}
        obj, drafts, secs = self._wait(req, evaluate, lambda o: model_cls.model_validate(o))
        comp0 = obj.model_dump()
        comp, vs0, vs, fixes = run_checks(comp0)
        for f in fixes:
            rt.log(f"  [fixer {f['fixer']}] errors {f['errors_before']} → {f['errors_after']} {'ACCEPT' if f['accepted'] else 'REJECT'}")
        self._logcall(pid, p.version, role, secs, drafts, req)
        trace = {"generator": {"prompt_id": pid, "prompt_version": p.version, "endpoint": ENDPOINT, "tokens": 0},
                 "initial_errors": len(engine.errors(vs0)), "initial_warnings": len(vs0) - len(engine.errors(vs0)),
                 "initial_error_codes": engine.error_codes(vs0), "repairs": [], "fixes": fixes, "regenerations": [],
                 "final_errors": len(engine.errors(vs)), "final_warnings": len(vs) - len(engine.errors(vs)),
                 "final_error_codes": engine.error_codes(vs), "open": engine.open_items(vs),
                 "agent": {"request": req.name, "seconds": secs, "drafts_checked": drafts}}
        rt.log(f"  [{pid}] answer accepted from Claude Code after {secs:.0f}s ({drafts} draft checks): "
               f"{trace['final_errors']} errors, {trace['final_warnings']} warnings")
        return comp, vs, trace

    # ------------------------------------------------------------------ ExternalResearch.run: comparable courses elsewhere
    def research(self, cco_compact: dict, blocklist, run_id: str | None = None) -> dict:
        from profsagent.config import load_yaml
        inst = load_yaml("config/institutions.yaml")
        brief = ("Find comparable courses at other universities for the course below, read their pages and extract each one "
                 "(schema `accepted[]`, the same fields the pipeline's X2 extractor fills). Prefer the institutions listed in "
                 "inputs.institutions; single course pages or catalogue entries only; at most 6 accepted and at most 2 per "
                 "institution; quote 2-4 short sentences from each page in evidence_quotes. Put every page you dropped in "
                 "`rejected` with its reason.")
        inputs = json.dumps({"course": cco_compact, "institutions": inst.get("institutions"),
                             "limits": {k: v for k, v in inst.items() if k != "institutions"}}, indent=1, ensure_ascii=False, default=str)
        req = self._request("X2", "agentcc", "research", brief, inputs, ResearchResult.model_json_schema(), None, "extract")

        def evaluate(obj):
            m, errs = self._schema_check(ResearchResult, obj)
            if not m:
                return {"schema_errors": errs, "hidden_named": [], "errors": [], "warnings": []}
            blocked = [f"{c.url}: {why}" for c in m.accepted if (why := blocklist.blocks(url=c.url, code=c.course_code, title=c.course_title))]
            return {"schema_errors": [], "hidden_named": self._leaks(obj) + blocked, "errors": [], "warnings": []}
        res, drafts, secs = self._wait(req, evaluate, lambda o: ResearchResult.model_validate(o))
        self._logcall("X2", "agentcc", "extract", secs, drafts, req)
        out = res.model_dump()
        self._say(f"[research] Claude Code accepted {len(out['accepted'])} comparable courses after {secs:.0f}s")
        return {"plan": out["plan"], "accepted": out["accepted"], "rejected": out["rejected"][:60]}

    # ------------------------------------------------------------------ the rest of LLMClient
    def embed(self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT"):
        if self._embedder is None:                       # local MiniLM, as the course database uses: no API, no Gemini
            from profsagent.kg.neo4j_kg import LocalEmbedder
            self._embedder = LocalEmbedder()
        return self._embedder.embed(texts, task_type)

    def grounded_search(self, query: str, instruction: str) -> dict:
        raise RuntimeError("no grounded search in a claude_code run: the session searches the web itself")

    def raw(self, *a, **kw):
        raise RuntimeError("a claude_code run makes no raw API calls")


def llm_for(run_dir: Path, run_cfg: dict | None):
    """The client a run uses: the bridge for `run.agent: claude_code`, else the ordinary LLMClient."""
    if P.is_agent_run(run_cfg):
        return AgentBridge(run_dir, run_cfg)
    from profsagent.llm.client import LLMClient
    return LLMClient(Path(run_dir) / "llm_calls.jsonl")
