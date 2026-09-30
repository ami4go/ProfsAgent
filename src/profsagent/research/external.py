"""External comparable-course research across whitelisted top institutions.

Pipeline (docs/01 §7, S2):
  X1 plan  →  (a) Google-Search grounding per query (gemini-2.5-flash, free tier)
              (b) deterministic catalogue adapters (Stanford ExploreCourses XML, NUSMods JSON)
           →  candidate URLs filtered by whitelist + blocklist, de-duplicated, ranked by embedding similarity
           →  fetch → X2 page classification/extraction → evidence-quote check → ExternalCourse records
Blocklists (domains, course codes, title fragments) come from the run config so held-out test courses
(e.g. Stanford CS146S for the final evaluation) can never be retrieved.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import httpx
import numpy as np

from profsagent.config import institutions
from profsagent.llm.prompts import load_prompt
from profsagent.models.io import ExternalPage, SearchPlan
from profsagent.research.fetch import domain, domain_matches, fetch

URL_RE = re.compile(r"https?://[^\s\)\]\}>\"'`,]+")


@dataclass
class Blocklist:
    domains: list[str] = field(default_factory=list)
    course_codes: list[str] = field(default_factory=list)
    title_fragments: list[str] = field(default_factory=list)

    def blocks(self, url: str = "", code: str | None = None, title: str | None = None, text: str = "") -> str | None:
        if url and self.domains and domain_matches(url, self.domains):
            return f"domain {domain(url)}"
        norm = lambda s: re.sub(r"[\s\-_.]", "", (s or "").upper())  # noqa: E731
        for c in self.course_codes:
            if code and norm(code) == norm(c):
                return f"code {c}"
            if norm(c) and norm(c) in norm(url):
                return f"code {c} in url"
        for t in self.title_fragments:
            if t.lower() in (title or "").lower():
                return f"title '{t}'"
        return None


class ExternalResearch:
    def __init__(self, llm, log=print):
        self.llm = llm
        self.cfg = institutions()
        self.inst = {i["id"]: i for i in self.cfg["institutions"]}
        self.log = log

    # ------------------------------------------------------------------ helpers
    def institution_of(self, url: str) -> str | None:
        for i in self.cfg["institutions"]:
            if domain_matches(url, i["domains"]):
                return i["id"]
        return None

    def _grounded(self, q: dict) -> list[dict]:
        targets = [self.inst[t] for t in q.get("target_institutions", []) if t in self.inst]
        doms = sorted({d for t in (targets or self.cfg["institutions"]) for d in t["domains"]})
        instruction = (
            "You are helping find UNIVERSITY COURSE PAGES. Search the web and list pages that are the homepage, syllabus, "
            "schedule or official catalogue entry of ONE specific course. Only include pages hosted on these domains: "
            + ", ".join(doms) + ". Exclude degree-programme pages, course lists, people/faculty pages and news. "
            "Answer with one line per page in the form: URL | institution | course code | course title. Up to 6 lines. "
            "If you find nothing suitable, answer NONE."
        )
        try:
            res = self.llm.grounded_search(q["query"], instruction)
        except Exception as e:  # noqa: BLE001
            self.log(f"[research] search failed for {q['query']!r}: {e}")
            return []
        out = []
        for line in res["text"].splitlines():
            m = URL_RE.search(line)
            if not m:
                continue
            parts = [p.strip() for p in line.split("|")]
            out.append({"url": m.group(0).rstrip(".;"), "via": "search", "query": q["query"],
                        "code_hint": parts[2] if len(parts) > 2 else None, "title_hint": parts[3] if len(parts) > 3 else None})
        for s in res["sources"]:  # grounding redirect URLs — resolved at fetch time
            if s.get("uri"):
                out.append({"url": s["uri"], "via": "search-source", "query": q["query"], "title_hint": s.get("title")})
        return out

    def _stanford(self, kw: str) -> list[dict]:
        try:
            r = httpx.get("https://explorecourses.stanford.edu/search", timeout=40, follow_redirects=True,
                          params={"view": "xml-20200810", "filter-coursestatus-Active": "on", "q": kw, "academicYear": ""})
        except Exception as e:  # noqa: BLE001
            self.log(f"[research] stanford adapter failed: {e}")
            return []
        out = []
        for m in re.findall(r"<course>.*?</course>", r.text, re.S)[:25]:
            g = lambda tag: (re.search(rf"<{tag}>(.*?)</{tag}>", m, re.S) or [None, None])[1]  # noqa: E731
            subj, num, title, desc = g("subject"), g("code"), g("title"), g("description")
            if not (subj and num):
                continue
            out.append({"url": f"https://explorecourses.stanford.edu/search?q={subj}{num}", "via": "adapter:stanford",
                        "institution_id": "STANFORD", "code_hint": f"{subj} {num}", "title_hint": title,
                        "catalogue_text": f"{subj} {num}: {title}\n{re.sub(r'<[^>]+>', ' ', desc or '')}"})
        return out

    def _nusmods(self, kw: str, _cache={}) -> list[dict]:  # noqa: B006
        ay = "2025-2026"
        try:
            if ay not in _cache:
                _cache[ay] = httpx.get(f"https://api.nusmods.com/v2/{ay}/moduleList.json", timeout=40).json()
        except Exception as e:  # noqa: BLE001
            self.log(f"[research] nusmods adapter failed: {e}")
            return []
        words = [w for w in re.findall(r"[a-z]+", kw.lower()) if len(w) > 3]
        hits = [m for m in _cache[ay] if words and sum(w in m["title"].lower() for w in words) >= max(1, len(words) - 1)][:8]
        out = []
        for m in hits:
            try:
                d = httpx.get(f"https://api.nusmods.com/v2/{ay}/modules/{m['moduleCode']}.json", timeout=30).json()
            except Exception:  # noqa: BLE001
                continue
            out.append({"url": f"https://nusmods.com/courses/{m['moduleCode']}", "via": "adapter:nusmods", "institution_id": "NUS",
                        "code_hint": m["moduleCode"], "title_hint": m["title"],
                        "catalogue_text": f"{m['moduleCode']}: {m['title']}\n{d.get('description', '')}\nPrerequisite: {d.get('prerequisite', '')}\n"
                                          f"Workload (lec,tut,lab,proj,prep h/wk): {d.get('workload')}\nCredits: {d.get('moduleCredit')}"})
        return out

    # ------------------------------------------------------------------ main
    def run(self, cco_compact: dict, blocklist: Blocklist, run_id: str | None = None) -> dict:
        lim = self.cfg["search"]
        p1 = load_prompt("X1")
        sys_, usr = p1.render(cco=cco_compact, institutions=[{k: i[k] for k in ("id", "name", "country", "domains")}
                                                             for i in self.cfg["institutions"]], limits={"max_queries": lim["max_queries"]})
        plan, _ = self.llm.structured(system=sys_, user=usr, model_cls=SearchPlan, temperature=0.3, prompt_id="X1",
                                      prompt_version=p1.version, run_id=run_id)
        self.log(f"[research] plan: titles={plan.equivalent_course_titles[:5]} queries={len(plan.queries)}")

        cands: list[dict] = []
        for q in plan.queries[: lim["max_queries"]]:
            cands += self._grounded(q.model_dump())
        for kw in plan.catalogue_keywords[:4]:
            cands += self._stanford(kw) + self._nusmods(kw)

        # filter: whitelist, blocklist, de-dup (resolve redirect URLs by fetching lazily later)
        seen, kept, rejected = set(), [], []
        for c in cands:
            why = blocklist.blocks(url=c["url"], code=c.get("code_hint"), title=c.get("title_hint"))
            if why:
                rejected.append({**c, "reason": f"blocklist: {why}"})
                continue
            key = (c.get("code_hint") or c["url"]).upper().replace(" ", "")
            if key in seen:
                continue
            seen.add(key)
            kept.append(c)

        # rank by semantic similarity to the target course
        target_txt = f"{cco_compact.get('course_name')}: {cco_compact.get('description')} Topics: " + \
                     "; ".join(t for g in cco_compact.get("topic_groups", []) for t in [g.get("title", "")])
        texts = [f"{c.get('title_hint') or ''} {c.get('catalogue_text') or c['url']}" for c in kept]
        if kept:
            try:
                tv = self.llm.embed([target_txt], "RETRIEVAL_QUERY")[0]
                cv = self.llm.embed(texts, "RETRIEVAL_DOCUMENT")
                order = np.argsort(-(cv @ tv))
                kept = [kept[i] for i in order]
            except Exception as e:  # noqa: BLE001
                self.log(f"[research] ranking by embedding failed ({e}); keeping search order")

        p2 = load_prompt("X2")
        accepted, examined = [], []
        per_inst: dict[str, int] = {}
        for c in kept:
            if len(examined) >= lim["max_candidate_pages"] or len(accepted) >= lim["max_accepted"]:
                break
            inst_hint = c.get("institution_id") or self.institution_of(c["url"])
            if inst_hint and per_inst.get(inst_hint, 0) >= lim.get("max_per_institution", 2):
                continue
            if c.get("catalogue_text"):
                page = {"url": c["url"], "final_url": c["url"], "title": c.get("title_hint"), "text": c["catalogue_text"], "status": 200}
            else:
                page = fetch(c["url"])
                if page.get("status") != 200 or not page.get("text"):
                    rejected.append({**c, "reason": f"fetch: {page.get('status')} {page.get('error')}"})
                    continue
            final = page.get("final_url") or c["url"]
            inst = c.get("institution_id") or self.institution_of(final)
            if not inst:
                rejected.append({**c, "reason": f"not whitelisted: {domain(final)}"})
                continue
            why = blocklist.blocks(url=final, title=page.get("title"))
            if why:
                rejected.append({**c, "reason": f"blocklist after redirect: {why}"})
                continue
            text = page["text"][: lim["page_text_chars"]]
            sys_, usr = p2.render(page={"url": final, "institution_id": inst, "domain": domain(final), "title": page.get("title"), "text": text},
                                  target={k: cco_compact.get(k) for k in ("course_name", "level", "topic_groups")})
            try:
                ext, _ = self.llm.structured(system=sys_, user=usr, model_cls=ExternalPage, role="extract", temperature=0,
                                             prompt_id="X2", prompt_version=p2.version, run_id=run_id)
            except Exception as e:  # noqa: BLE001
                rejected.append({**c, "reason": f"X2 failed: {e}"[:200]})
                continue
            examined.append(final)
            quotes_ok = sum(1 for qt in ext.evidence_quotes if _norm(qt)[:60] and _norm(qt)[:60] in _norm(text))
            why = blocklist.blocks(url=final, code=ext.course_code, title=ext.course_title)
            verdict = None
            if why:
                verdict = f"blocklist: {why}"
            elif ext.page_type not in ("single_course_page", "course_catalogue_entry"):
                verdict = f"page_type={ext.page_type}"
            elif ext.relevance in ("low", "none"):
                verdict = f"relevance={ext.relevance}"
            elif ext.evidence_quotes and quotes_ok < min(2, len(ext.evidence_quotes)):
                verdict = f"evidence quotes not found on page ({quotes_ok}/{len(ext.evidence_quotes)})"
            rec = {"id": f"EXT:{inst}/{re.sub(r'[^A-Za-z0-9.]+', '', ext.course_code or 'NA')}", "institution_id": inst,
                   "institution": self.inst[inst]["name"], "url": final, "via": c["via"], **ext.model_dump(exclude={"concerns", "missing"}),
                   "quotes_verified": quotes_ok}
            if verdict:
                rejected.append({"url": final, "reason": verdict, "course_title": ext.course_title})
            else:
                accepted.append(rec)
                per_inst[inst] = per_inst.get(inst, 0) + 1
        reasons = {}
        for r in rejected:
            k = re.sub(r"[:(].*", "", str(r.get("reason")))[:40]
            reasons[k] = reasons.get(k, 0) + 1
        self.log(f"[research] candidates={len(cands)} kept={len(kept)} examined={len(examined)} accepted={len(accepted)} rejected-by={reasons}")
        return {"plan": plan.model_dump(), "accepted": accepted, "rejected": rejected[:60]}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower()).strip()
