"""Expert-speaker aid (new aid A9): who could deliver this lecture — researchers or industry practitioners, worldwide.

Candidates:  academics  — OpenAlex works on the lecture's research phrases, aggregated by author, plus the authors of
                          the Google Scholar results for the same phrase (through SerpApi) (+ DBLP, ORCID)
             IIIT-D     — faculty teaching the related IIIT-D courses (course directory)
             industry   — web search (names extracted by D3, then confirmed on their own pages) and
                          maintainers of widely used GitHub repositories on the topic
Verification (2026-11-01): the best academics are looked up on Google Scholar (affiliation, citations, h-index,
interests); Semantic Scholar is the fallback. OpenAlex's "last known institution" was wrong for several people in the
28 Oct run (e.g. a researcher at SMU listed at Heidelberg with h-index 0), so Scholar's profile wins when both exist.
Ranking (plan §4.3): topical fit · teaching evidence · practical relevance · standing · recency · feasibility,
then an AI check of fit and field against the evidence (D4), hard checks (incl. a minimum h-index for academics),
diversity rules (IIIT-D faculty first, one per institution, one per paper), and 5–7 per lecture.
The system never contacts anyone; it drafts an invitation for the professor to send.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import re
from collections import defaultdict

from profsagent.config import DATA
from profsagent.delivery import checks
from profsagent.delivery.common import embed, xcfg
from profsagent.delivery.models import ExpertNotes, Practitioners
from profsagent.delivery.resources import llm_call
from profsagent.delivery.sources import (OpenAlex, dblp_author, github_repos, github_user, grounded_text, page, s2_author,
                                        scholar_find, scholar_papers, scholar_profile, scholar_search_url, serpapi_left,
                                        short_name, web_search)

YEAR = dt.date.today().year


def _fit(evidence_titles: list[str], targets: list[dict]) -> float:
    """Mean of the 3 best similarities between evidence titles and the lecture's targets, mapped 0.25→0, 0.65→1."""
    if not evidence_titles:
        return 0.0
    ev = embed(evidence_titles[:30])
    tv = embed([t["text"] for t in targets])
    best = sorted((float(x) for x in (ev @ tv.T).max(axis=1)), reverse=True)[:3]
    m = 0.6 * best[0] + 0.4 * sum(best) / len(best)       # one paper squarely on the topic (e.g. the survey) counts most
    return round(min(max((m - 0.25) / 0.40, 0.0), 1.0), 3)


REPUTABLE = ("acm", "ieee", "springer", "elsevier", "arxiv", "usenix", "neurips", "icml", "iclr", "aaai", "ijcai", "nature",
             "science", "plos", "wiley", "taylor", "oxford university press", "cambridge university press", "informs", "ssrn",
             "management science", "techrxiv", "proceedings")


def venue_quality(src: dict | None, name: str | None) -> float:
    """0.3 (unknown / likely low-reputation) … 1.0 (established venue): OpenAlex venue h-index, or a known publisher."""
    n = (name or (src or {}).get("name") or "").lower()
    host = ((src or {}).get("host") or "").lower()
    if any(r in n or r in host for r in REPUTABLE):
        return 1.0
    h = (src or {}).get("h_index")
    if h is None:
        return 0.5 if n else 0.4
    return 1.0 if h >= 40 else 0.8 if h >= 15 else 0.5 if h >= 5 else 0.3


def _top_institutions() -> list[str]:
    from profsagent.config import institutions
    names = [i["name"] for i in institutions()["institutions"]]
    return [n.lower() for n in names + xcfg().get("top_institutions_extra", [])]


def _prestige(affiliation: str | None) -> float:
    a = (affiliation or "").lower()
    return 1.0 if a and any(t in a for t in _top_institutions()) else 0.4


COUNTRY_CODES = {"united states": "US", "usa": "US", "us": "US", "united kingdom": "GB", "uk": "GB", "england": "GB",
                 "india": "IN", "australia": "AU", "canada": "CA", "germany": "DE", "france": "FR", "switzerland": "CH",
                 "netherlands": "NL", "singapore": "SG", "china": "CN", "japan": "JP", "south korea": "KR", "korea": "KR",
                 "israel": "IL", "ireland": "IE", "sweden": "SE", "norway": "NO", "denmark": "DK", "finland": "FI",
                 "spain": "ES", "italy": "IT", "austria": "AT", "brazil": "BR", "new zealand": "NZ", "uae": "AE",
                 "united arab emirates": "AE", "hong kong": "HK"}


def country_code(c: str | None) -> str | None:
    if not c:
        return None
    c = c.strip()
    return c.upper() if len(c) == 2 else COUNTRY_CODES.get(c.lower())


def _feasibility(country: str | None, cfg: dict) -> float:
    country = country_code(country)
    if not country:
        return 0.6
    off = cfg["feasibility"]["country_utc_offset"].get(country.upper())
    if off is None:
        return 0.6
    overlap = max(0.0, 9 - abs(off - 5.5)) / 9          # shared hours of a 9-to-6 working day with IST
    return round(min(1.0, overlap + (cfg["feasibility"]["india_bonus"] if country.upper() == "IN" else 0)), 3)


# ------------------------------------------------------------------ candidate pools
def academics(b: dict, q: dict, log) -> list[dict]:
    cfg = xcfg()["openalex"]
    oa = OpenAlex()
    agg: dict[str, dict] = {}
    searches = [(phrase, None) for phrase in (q.get("research_queries") or [b["topic"]])[:2]]
    if cfg.get("india_query"):                     # IITs, IISc, IIITs ...: Indian researchers on the same topic
        searches.append(((q.get("research_queries") or [b["topic"]])[0], "IN"))
    for phrase, country in searches:
        for w in oa.works(phrase, n=cfg["works_per_query"], min_year=cfg["min_year"], country=country):
            for a in w["authors"][:6]:          # first authors and senior authors are usually in the first six
                if not a.get("id") or not a.get("name"):
                    continue
                d = agg.setdefault(a["id"], {"id": a["id"], "name": a["name"], "orcid": a.get("orcid"), "works": [], "insts": a["institutions"]})
                if all(x["id"] != w["id"] for x in d["works"]):
                    d["works"].append({"id": w["id"], "title": w["title"], "year": w["year"], "cited_by": w["cited_by"], "doi": w.get("doi"),
                                       "venue": w.get("venue"), "venue_id": w.get("venue_id")})
    # relevance first: a paper counts only if its title is about this lecture; citations only break ties
    titles = list({w["title"] for d in agg.values() for w in d["works"] if w["title"]})
    rel = {}
    if titles:
        sims = embed(titles) @ embed([t["text"] for t in b["targets"]]).T
        rel = {t: float(sims[i].max()) for i, t in enumerate(titles)}
    for d in agg.values():
        d["works"] = [w for w in d["works"] if rel.get(w["title"], 0) >= 0.35]
        d["_rel"] = sum(rel.get(w["title"], 0) * (1 + 0.15 * math.log1p(w["cited_by"])) for w in d["works"])
    ranked = sorted((d for d in agg.values() if d["works"]), key=lambda d: -d["_rel"])[: cfg["authors_to_profile"]]
    scholar = scholar_authors(b, (q.get("research_queries") or [b["topic"]])[0])
    out = []
    for d in ranked:
        prof = oa.author(d["id"]) or {}
        works = sorted(d["works"], key=lambda x: (-(x["year"] or 0), -x["cited_by"]))
        inst_type = prof.get("inst_type") or ((d["insts"] or [{}])[0].get("type"))
        ev = []
        for w in works[:5]:
            vq = venue_quality(oa.source(w.get("venue_id")), w.get("venue"))
            ev.append({"kind": "paper", "title": w["title"], "year": w["year"], "url": w.get("doi") or w["id"], "cited_by": w["cited_by"],
                       "venue": w.get("venue"), "venue_quality": vq})
        links = {"openalex": prof.get("id") or d["id"], "orcid": prof.get("orcid") or d.get("orcid"),
                 "scholar_search": scholar_search_url(d["name"], prof.get("institution"))}
        out.append({"name": d["name"], "kind": "industry" if inst_type == "company" else "academic", "inst_type": inst_type,
                    "affiliation": prof.get("institution"),
                    "country": prof.get("country") or ((d["insts"] or [{}])[0].get("country")), "evidence": ev, "links": links,
                    "metrics": {"cited_by": prof.get("cited_by"), "h_index": prof.get("h_index"), "works_count": prof.get("works_count"),
                                "matching_works": len(d["works"])},
                    "topics": prof.get("topics", []), "verified_identity": "OpenAlex author record" + (" + ORCID" if links["orcid"] else ""),
                    "latest_year": max((w["year"] or 0) for w in d["works"]) or None,
                    "_scholar_id": (scholar.pop(short_name(d["name"]), None) or {}).get("author_id")})
    for sn, s in list(scholar.items())[:6]:          # authors only Google Scholar found: named in full once their profile is read
        out.append({"name": s["name"], "kind": "academic", "inst_type": None, "affiliation": None, "country": None,
                    "evidence": [{"kind": "paper", "title": w["title"], "year": w["year"], "url": w["link"], "cited_by": w["cited_by"]}
                                 for w in s["works"][:5]],
                    "links": {}, "metrics": {}, "topics": [], "verified_identity": None, "_scholar_id": s["author_id"],
                    "_scholar_only": True, "latest_year": max((w["year"] or 0) for w in s["works"]) or None})
    log(f"  experts {b['lecture_id']}: {len(out)} academics (OpenAlex{' + Google Scholar' if scholar or any(e.get('_scholar_id') for e in out) else ''})")
    return out


def scholar_authors(b: dict, phrase: str) -> dict[str, dict]:
    """Authors (with Scholar profile ids) of the Google Scholar results for the lecture's research phrase whose paper
    titles are about the lecture: {short name: {name, author_id, works}}. One SerpApi search per lecture."""
    cfg = xcfg()["scholar"]
    if not (cfg.get("enabled") and cfg.get("search_per_lecture")):
        return {}
    papers = [p for p in scholar_papers(phrase, 20) if p["title"]]
    if not papers:
        return {}
    sims = embed([p["title"] for p in papers]) @ embed([t["text"] for t in b["targets"]]).T
    out: dict[str, dict] = {}
    for p, s in zip(papers, sims.max(axis=1)):
        if float(s) < 0.35:
            continue
        for a in p["authors"]:
            if a.get("author_id"):
                d = out.setdefault(short_name(a["name"]), {"name": a["name"], "author_id": a["author_id"], "works": []})
                d["works"].append(p)
    return dict(sorted(out.items(), key=lambda kv: -len(kv[1]["works"])))


def iiitd_faculty(b: dict, st: dict, q: dict | None = None) -> list[dict]:
    """Faculty teaching the IIIT-D courses the design found related (overlaps / prerequisites)."""
    p = DATA / "stub_kg" / "index.json"
    if not p.exists():
        return []
    rows = {r["uid"]: r for r in json.loads(p.read_text(encoding="utf-8"))}
    related = [o["course_uid"] for o in (st.get("positioning") or {}).get("overlaps", [])] + \
              [o["course_uid"] for o in st.get("overlap_computed", [])[:8]]
    people = defaultdict(lambda: {"courses": []})
    for code in dict.fromkeys(related):
        r = rows.get(code)
        if not r or not r.get("professor") or r["professor"].lower() in ("none", "tba", "-"):
            continue
        for name in re.split(r",|&| and ", r["professor"]):
            name = name.strip()
            if len(name) > 3:
                people[name]["courses"].append({"code": code, "name": r["name"], "url": r.get("catalogue_url")})
    out = []
    oa = OpenAlex()
    phrase = ((q or {}).get("research_queries") or [b["topic"]])[0]
    for name, d in people.items():
        ev = [{"kind": "course", "title": f"Teaches {c['code']} {c['name']} at IIIT-D", "year": YEAR, "url": c["url"]} for c in d["courses"]]
        links, metrics, latest = {"scholar_search": scholar_search_url(name, "IIIT Delhi")}, {}, YEAR
        prof = oa.find_author(name, "Indraprastha")          # their publication record, like any other researcher
        if prof:
            links.update(openalex=prof["id"], orcid=prof.get("orcid"))
            metrics = {"cited_by": prof.get("cited_by"), "h_index": prof.get("h_index"), "works_count": prof.get("works_count")}
            for w in oa.works_by(prof["id"], phrase, 5):
                ev.append({"kind": "paper", "title": w["title"], "year": w["year"], "url": w.get("doi") or w["id"], "cited_by": w["cited_by"],
                           "venue": w.get("venue"), "venue_quality": venue_quality(oa.source(w.get("venue_id")), w.get("venue"))})
        out.append({"name": name, "kind": "iiitd", "affiliation": "IIIT-Delhi", "country": "IN", "inst_type": "education",
                    "evidence": ev, "links": links, "metrics": metrics, "topics": [c["name"] for c in d["courses"]],
                    "verified_identity": "IIIT-D course directory" + (" + OpenAlex author record" if prof else ""), "latest_year": latest})
    return out


SOCIAL = ("linkedin.com", "x.com", "twitter.com", "facebook.com", "instagram.com")   # self-written profiles do not confirm expertise


def talk_speakers(llm, b: dict, videos: list[dict], run_id: str, log) -> list[dict]:
    """Fallback without web search: speakers named in the titles/descriptions of the talk videos already found.
    A name is kept only if it appears in that video's own title or description (the talk is the evidence)."""
    vids = [v for v in videos if v.get("description")][:12]
    if not vids:
        return []
    text = "\n\n".join(f"[{i + 1}] {v['title']} ({v.get('source')})\n{v['description'][:700]}" for i, v in enumerate(vids))
    try:
        people = llm_call(llm, "D3", {"topic": {"topic": b["topic"], "learning_outcomes": [x["statement"] for x in b["learning_outcomes"]]},
                                      "search_text": text, "sources": [{"url": v["url"], "title": v["title"]} for v in vids]},
                          Practitioners, run_id, log)
    except Exception as e:  # noqa: BLE001
        log(f"  talk-speaker extraction failed ({type(e).__name__})")
        return []
    out = []
    for pp in people.people:
        sur = pp.name.split()[-1].lower()
        v = next((v for v in vids if sur in (v["title"] + " " + v["description"]).lower()), None)
        if not v:
            continue
        out.append({"name": pp.name, "kind": "industry", "affiliation": pp.organisation, "country": country_code(pp.country),
                    "role": (pp.role or "speaker")[:90], "evidence": [{"kind": "talk", "title": v["title"], "year": int(v["published"][:4]) if v.get("published") else None, "url": v["url"]}],
                    "links": {"talk": v["url"]}, "metrics": {}, "topics": [pp.why] if pp.why else [],
                    "verified_identity": f"named in the talk video {v['url']}", "latest_year": int(v["published"][:4]) if v.get("published") else None})
    return out


def practitioners(llm, b: dict, q: dict, run_id: str, log, videos: list[dict] | None = None) -> list[dict]:
    out = []
    cfg = xcfg()
    searched = False
    if cfg["web_search"]["enabled"] and q.get("practitioner_query"):
        instruction = ("Find industry practitioners (engineers, architects, applied researchers at companies, open-source "
                       "maintainers, well-known instructors) who are recognised speakers or authors on this topic. For each, "
                       "give their name, role, organisation, country, and a public professional page about them (talk page, "
                       "company or personal site, conference speaker page). Public professional information only.")
        try:
            res = grounded_text(llm, q["practitioner_query"], instruction)
            if res is None:
                raise RuntimeError("web search unavailable (daily quota)")
            searched = True
            people = llm_call(llm, "D3", {"topic": {"topic": b["topic"], "learning_outcomes": [x["statement"] for x in b["learning_outcomes"]]},
                                          "search_text": res["text"][:6000], "sources": res.get("sources", [])[:15]}, Practitioners, run_id, log)
            for pp in people.people:
                ev_urls = [u for u in dict.fromkeys([pp.profile_url, *pp.evidence_urls]) if u]
                verified, pages = None, []
                surname = pp.name.split()[-1].lower()
                for u in ev_urls[:4]:      # resolve search redirects to the real page; the name must appear on it
                    pg = page(u)
                    if pg.get("status") != 200:
                        continue
                    real = pg.get("final_url") or u
                    if "grounding-api-redirect" in real:
                        continue
                    weak = any(x in real for x in xcfg().get("weak_identity_domains", []))   # e.g. a Scribd upload
                    named = surname in (pg.get("text") or "").lower() and not weak
                    pages.append({"url": real, "title": (pg.get("title") or "").strip()[:120], "named": named})
                    if named and not verified:
                        verified = f"named on {real}"
                if not verified:       # pages can block scraping: accept the name in a talk video or a search result
                    nm = pp.name.lower()
                    v = next((v for v in (videos or []) if nm in (v["title"] + " " + (v.get("description") or "")).lower()), None)
                    if v:
                        verified = f"named in the talk video {v['url']}"
                        pages.append({"url": v["url"], "title": v["title"], "named": True})
                    else:
                        hit = next((s for s in res.get("sources", []) if nm in ((s.get("title") or "") + " " + (s.get("snippet") or "")).lower()), None)
                        if hit and hit.get("uri") and "grounding-api-redirect" not in hit["uri"]:
                            verified = f"named in the search result {hit['uri']}"
                            pages.append({"url": hit["uri"], "title": (hit.get("title") or "")[:120], "named": True})
                        else:            # one targeted search for the person: a page that names them with the topic
                            for r in web_search(f'"{pp.name}" {pp.organisation or ""} {b["topic"]}', 5) or []:
                                if nm in (r["title"] + " " + r["content"]).lower() and not any(x in r["url"] for x in SOCIAL):
                                    verified = f"named on {r['url']}"
                                    pages.append({"url": r["url"], "title": r["title"][:120], "named": True})
                                    break
                if not pages:
                    continue
                prof = next((x for x in pages if x["named"]), pages[0])
                out.append({"name": pp.name, "kind": "industry", "affiliation": pp.organisation, "country": country_code(pp.country),
                            "role": (pp.role or "")[:90],
                            "evidence": [{"kind": "talk", "title": x["title"] or pp.why, "year": None, "url": x["url"]} for x in pages[:3]],
                            "links": {"page": prof["url"]}, "metrics": {}, "topics": [pp.why] if pp.why else [],
                            "verified_identity": verified, "latest_year": None})
        except Exception as e:  # noqa: BLE001
            log(f"  practitioner web search failed ({str(e)[:80]}); using speakers of the talks found instead")
    if not searched and videos:
        out += talk_speakers(llm, b, videos, run_id, log)
    if cfg["github"]["enabled"]:
        owners = defaultdict(list)
        phrase = (q.get("research_queries") or [b["topic"]])[0]
        for r in github_repos(f"{phrase} in:name,description,topics", cfg["github"]["repos_per_query"]):
            if r["owner_type"] == "User" and r["stars"] >= 200:
                owners[r["owner"]].append(r)
        for login, repos in list(owners.items())[:5]:
            u = github_user(login)
            if not u or len((u.get("name") or "").split()) < 2:      # a real name, not just a handle
                continue
            site = (u.get("blog") or "").split()[0].strip(" ;,") if u.get("blog") else ""
            site = site if site.startswith("http") else (f"https://{site}" if site and "." in site else None)
            company = (u.get("company") or "").lstrip("@").strip() or None
            if company and ("http" in company or company.endswith((".com", ".io", ".dev"))):
                company = None
            out.append({"name": u["name"], "kind": "industry", "affiliation": company, "country": None,
                        "role": "open-source maintainer", "evidence": [{"kind": "repo", "title": f"{r['name']} ({r['stars']:,} stars): {r['description'][:100]}",
                                                                         "year": int(r["updated"][:4]) if r.get("updated") else None, "url": r["url"]} for r in repos],
                        "links": {"github": u["url"], "website": site}, "metrics": {"followers": u.get("followers")},
                        "topics": [], "verified_identity": "GitHub account", "latest_year": max((int(r["updated"][:4]) for r in repos if r.get("updated")), default=None)})
    log(f"  experts {b['lecture_id']}: {len(out)} practitioners")
    return out


# ------------------------------------------------------------------ verification (Google Scholar, Semantic Scholar)
TLD_COUNTRY = {"in": "IN", "sg": "SG", "uk": "GB", "de": "DE", "fr": "FR", "ch": "CH", "nl": "NL", "se": "SE", "no": "NO",
               "dk": "DK", "fi": "FI", "it": "IT", "es": "ES", "at": "AT", "ie": "IE", "au": "AU", "nz": "NZ", "ca": "CA",
               "cn": "CN", "hk": "HK", "jp": "JP", "kr": "KR", "il": "IL", "br": "BR", "edu": "US", "ae": "AE"}


def _tkey(s: str | None) -> str:
    return re.sub(r"\W", "", (s or "").lower())[:60]


def _same_titles(a: list[str], b: list[str]) -> bool:
    """Same paper in both lists; Scholar shortens long titles, so a long enough prefix counts."""
    ka, kb = {_tkey(x) for x in a if x}, {_tkey(x) for x in b if x}
    return any(x == y or (min(len(x), len(y)) >= 25 and (x.startswith(y) or y.startswith(x))) for x in ka for y in kb)


def _split_affiliation(s: str | None) -> tuple[str | None, str | None]:
    """'Associate Professor of Computer Science, Singapore Management University' -> (role, institution)."""
    m = re.match(r"(.{3,80}?)\s+at\s+(.+)$", s or "")       # 'Assistant Professor at Harokopio University of Athens'
    if m and re.search(r"professor|lecturer|researcher|scientist|engineer|student|fellow|associate|director|head", m.group(1), re.I):
        return m.group(1).strip(), m.group(2).strip()
    parts = [p.strip() for p in (s or "").split(",") if p.strip()]
    if len(parts) >= 2 and re.search(r"professor|lecturer|researcher|scientist|engineer|student|fellow|director|head|dean|"
                                     r"founder|lead|architect|manager|postdoc", parts[0], re.I):
        return parts[0], ", ".join(parts[1:])
    return None, s or None


def verify(cands: list[dict], b: dict, log) -> None:
    """Google Scholar profile (affiliation, citations, h-index, interests) for the best academics, by the profile id
    found in a Scholar result or by a name search; Semantic Scholar when Scholar has nothing. A profile is used only
    when it is the same person: the id came from one of their own papers, or the profile lists one of their papers."""
    cfg = xcfg()["scholar"]
    if not cfg.get("enabled"):
        return
    left0, n = serpapi_left(), 0
    for e in cands:
        if e["kind"] == "iiitd" or not (e["kind"] == "academic" or e.get("links", {}).get("openalex") or e.get("_scholar_id")):
            continue                                       # IIIT-D faculty: affiliation known from the course directory
        titles = [x["title"] for x in e["evidence"] if x.get("kind") == "paper"]
        prof, how = None, None
        budget_ok = n < cfg["profiles_per_lecture"] and left0 - serpapi_left() < cfg["max_searches_per_lecture"]
        if budget_ok and e.get("_scholar_id"):
            prof, how = scholar_profile(e["_scholar_id"]), "id from their paper"
            n += 1
        elif budget_ok and not e.get("_scholar_only"):
            prof, how = scholar_find(e["name"], b["topic"]), "name search, papers matched"
            if prof and not _same_titles(titles, [prof.get("found_via")] + [a["title"] for a in prof["articles"]]):
                prof = None                               # a namesake: none of their papers is on the profile
            n += 1
        if prof:
            role, inst = _split_affiliation(prof["affiliation"])
            if e.get("affiliation") and inst and e["affiliation"].lower() not in inst.lower():
                e["affiliation_openalex"] = e["affiliation"]
            if e.get("_scholar_only"):
                e["name"] = prof["name"]
                e["verified_identity"] = f"Google Scholar profile ({how})"
            else:
                e["verified_identity"] = (e.get("verified_identity") or "") + " + Google Scholar profile"
            e["affiliation"] = inst or e.get("affiliation")
            if role and not e.get("role"):
                e["role"] = role[:90]
            tld = (prof.get("email_domain") or "").rsplit(".", 1)[-1]
            if TLD_COUNTRY.get(tld) and (e.get("affiliation_openalex") or not e.get("country")):
                e["country"] = TLD_COUNTRY[tld]
            m = e.setdefault("metrics", {})
            m.update(h_index=prof.get("h_index"), cited_by=prof.get("cited_by"), i10_index=prof.get("i10_index"), source="Google Scholar")
            e["interests"] = prof.get("interests", [])
            e["topics"] = list(dict.fromkeys((e.get("topics") or []) + e["interests"]))[:8]
            e["links"]["scholar"] = prof["url"]
            e["links"].pop("scholar_search", None)
            if e["kind"] == "academic" and re.search(r"\b(inc|ltd|llc|corp|corporation|technologies)\b", inst or "", re.I) and \
                    not re.search(r"universit|institut|college|school", inst or "", re.I):
                e["kind"] = "industry"
            continue
        if e.get("_scholar_only"):
            continue                                       # never confirmed: X-IDENTITY removes it
        if cfg.get("semantic_scholar_fallback"):
            s2 = s2_author(e["name"], titles)
            if s2 and s2.get("matched_paper"):
                m = e.setdefault("metrics", {})
                if (s2.get("h_index") or 0) > (m.get("h_index") or 0):   # OpenAlex splits some people into several records
                    m.update(h_index=s2["h_index"], cited_by=s2.get("cited_by"), source="Semantic Scholar")
                if s2.get("affiliation"):
                    if e.get("affiliation") and s2["affiliation"].lower() not in e["affiliation"].lower():
                        e["affiliation_openalex"] = e["affiliation"]
                    e["affiliation"] = s2["affiliation"]
                if s2.get("url"):
                    e["links"]["semantic_scholar"] = s2["url"]
                e["verified_identity"] = (e.get("verified_identity") or "") + " + Semantic Scholar"
    if n:
        log(f"  experts {b['lecture_id']}: {n} Google Scholar profile look-ups ({serpapi_left()} SerpApi searches left this month)")


# ------------------------------------------------------------------ ranking
def score(e: dict, b: dict, talk_titles: list[str]) -> None:
    cfg = xcfg()
    w = dict(cfg["weights"])
    if b.get("hands_on"):
        w["practical"] += cfg["hands_on_shift"]
        w["standing"] -= cfg["hands_on_shift"]
    titles = [x["title"] for x in e["evidence"] if x.get("title")] + e.get("topics", [])
    name_l = e["name"].lower()
    talks = [t for t in talk_titles if name_l in t.lower()]
    if talks:
        e["evidence"].append({"kind": "talk", "title": talks[0], "year": None, "url": None})
    kinds = {x["kind"] for x in e["evidence"]}
    # from evidence only (28 Oct run: 45 of 49 academics had the same 0.6 / 0.3, so these weights added only noise)
    university = e.get("inst_type") == "education" or bool(re.search(r"universit|institut|college|school|professor|lecturer",
                                                                     f"{e.get('affiliation') or ''} {e.get('role') or ''}", re.I))
    teaching = 1.0 if ("course" in kinds or e["kind"] == "iiitd") else 0.9 if "talk" in kinds else 0.8 if "book" in kinds else \
        0.5 if university else 0.2
    practical = 1.0 if e["kind"] == "industry" else 0.8 if "repo" in kinds else 0.2
    m = e.get("metrics", {})
    if m.get("cited_by") is not None:
        cites = 0.5 * min(math.log10((m.get("cited_by") or 0) + 1) / 4, 1) + 0.5 * min((m.get("h_index") or 0) / 40, 1)
        vqs = [x["venue_quality"] for x in e["evidence"] if x.get("venue_quality") is not None]
        venue = sum(vqs) / len(vqs) if vqs else 0.6
        e["venue_quality"] = round(venue, 2)
        # citations · top university (IITs, IISc, MIT, ETH, ...) · reputation of where the relevant work appeared
        standing = 0.4 * cites + 0.3 * _prestige(e.get("affiliation")) + 0.3 * venue
    elif m.get("followers") is not None:
        standing = min(1.0, math.log10(m["followers"] + 1) / 4)
    else:
        standing = 0.3 if len(e["evidence"]) <= 1 else 0.5      # one talk is thin evidence; several items, more
    ly = e.get("latest_year")
    recency = 0.6 if ly is None else 1.0 if ly >= YEAR - 2 else 0.6 if ly >= YEAR - 5 else 0.3
    depth = min(1.0, len([x for x in e["evidence"] if x.get("title")]) / 3)    # one video < several papers / talks
    s = {"topical_fit": round(_fit(titles, b["targets"]) * (0.7 + 0.3 * depth), 3), "teaching": teaching, "practical": practical,
         "standing": round(standing, 3),
         "recency": recency, "feasibility": _feasibility(e.get("country"), cfg)}
    e["scores"] = {k: round(float(v), 3) for k, v in s.items()}
    e["total"] = round(float(sum(w[k] * s[k] for k in w)), 3)


def select(cands: list[dict]) -> list[dict]:
    cfg = xcfg()
    hi, lo = cfg["top_n"]["max"], cfg["top_n"]["min"]
    d = cfg["diversity"]
    pool = sorted(cands, key=lambda e: -e["total"])
    picked: list[dict] = []

    def papers(e: dict) -> set[str]:
        return {_tkey(x["title"]) for x in e["evidence"] if x.get("kind") == "paper" and x.get("title")}

    def clash(e: dict) -> bool:
        aff = _inst_key(e.get("affiliation"))
        if aff and sum(1 for p in picked if _inst_key(p.get("affiliation")) == aff) >= d.get("max_same_affiliation", 99):
            return True                                   # one person per university / company
        if d.get("one_per_paper") and any(papers(e) & papers(p) for p in picked):
            return True                                   # co-authors of one paper share one slot
        return sum(1 for p in picked if (p.get("country") or "?") == (e.get("country") or "!")) >= d["max_same_country"]

    # the institute's own faculty first, when the AI check judged them a strong fit (a moderate one is ranked like anyone)
    for e in [e for e in pool if e["kind"] == "iiitd" and (e.get("note") or {}).get("fit") == "strong"][: d.get("iiitd_first", 0)]:
        picked.append(e)
    for need_kind, n in (("industry", d["min_industry"]), ("academic", d["min_academic"])):
        for e in pool:
            if sum(1 for p in picked if p["kind"] == need_kind) >= n:
                break
            if e["kind"] == need_kind and e not in picked and not clash(e):
                picked.append(e)
    for e in pool:
        if len(picked) >= hi:
            break
        if e not in picked and not clash(e):
            picked.append(e)
    for e in pool:              # still short of the minimum: people who passed every check but share an institution or paper
        if len(picked) >= lo:
            break
        if e not in picked:
            picked.append(e)
    first = [e for e in picked if e["kind"] == "iiitd" and (e.get("note") or {}).get("fit") == "strong"]
    return first + sorted((e for e in picked if e not in first), key=lambda e: -e["total"])


def _inst_key(a: str | None) -> str:
    return re.sub(r"\W", "", re.sub(r"\s*\(.*?\)", "", a or "").lower())


def recommend_experts(llm, st: dict, b: dict, q: dict, talk_titles: list[str], run_id: str, log, videos: list[dict] | None = None) -> dict:
    cands = academics(b, q, log) + iiitd_faculty(b, st, q) + practitioners(llm, b, q, run_id, log, videos=videos)
    seen, uniq = set(), []
    for e in cands:                                  # one entry per person
        k = re.sub(r"[^a-z]", "", e["name"].lower())
        if k and k not in seen:
            seen.add(k)
            uniq.append(e)
    for e in uniq:
        score(e, b, talk_titles)
    per_kind = {"academic": 6, "industry": 6, "iiitd": 3}
    top = []
    for kind, n in per_kind.items():           # researchers must reach the AI check even when presenters score higher
        top += sorted((e for e in uniq if e["kind"] == kind), key=lambda e: -e["total"])[:n]
    top = sorted(top, key=lambda e: -e["total"])
    verify(top, b, log)                             # Google Scholar / Semantic Scholar: affiliation, h-index, interests
    seen, kept = set(), []
    for e in top:                                   # a Scholar-only author may turn out to be someone already listed
        k = re.sub(r"[^a-z]", "", e["name"].lower())
        if k not in seen:
            seen.add(k)
            kept.append(e)
            score(e, b, [])                         # standing, teaching and country may have changed
    top = sorted(kept, key=lambda e: -e["total"])
    for i, e in enumerate(top):
        e["_id"] = f"x{i + 1}"
        for j, ev in enumerate(e["evidence"]):
            ev["id"] = f"{e['_id']}e{j + 1}"
    if top:
        ctx = {"lecture": {"lecture_id": b["lecture_id"], "topic": b["topic"], "learning_outcomes": [x["statement"] for x in b["learning_outcomes"]],
                           "hands_on": b["hands_on"], "course_level": st.get("level"), "today": dt.date.today().isoformat()},
               "candidates": [{"id": e["_id"], "name": e["name"], "affiliation": e.get("affiliation"), "role": e.get("role"), "kind": e["kind"],
                               "research_interests": e.get("interests") or None, "h_index": (e.get("metrics") or {}).get("h_index"),
                               "evidence": [{k: ev.get(k) for k in ("id", "kind", "title", "year", "venue_quality") if ev.get(k) is not None}
                                            for ev in e["evidence"][:5]]} for e in top]}
        rank_of = {"weak": 0, "moderate": 1, "strong": 2}
        runs = []
        for order in (ctx["candidates"], list(reversed(ctx["candidates"]))):   # two passes, different order
            try:
                runs.append({n.id: n.model_dump() for n in llm_call(llm, "D4", {**ctx, "candidates": order}, ExpertNotes, run_id, log).notes})
            except Exception as ex:  # noqa: BLE001
                log(f"  [D4] pass failed ({type(ex).__name__})")
        for e in top:
            got = [r[e["_id"]] for r in runs if e["_id"] in r]
            if got:                                   # the AI verdict varies run to run: keep the more cautious one
                e["note"] = min(got, key=lambda n: rank_of.get(n["fit"], 1))
                e["note"]["fit_votes"] = [n["fit"] for n in got]
        if not runs:
            log("  [D4] failed; experts shown without AI fit check")
    for e in top:
        if xcfg()["dblp"]["enabled"] and e["kind"] in ("academic", "iiitd"):
            dd = dblp_author(e["name"])
            if dd:
                e["links"]["dblp"] = dd["url"]
        e["findings"] = checks.expert(e)
        note = e.get("note") or {}
        if note and not note.get("same_field", True):
            e["findings"].append(checks.f("X-FIELD", "error", "AI check: the evidence is from another field that only shares words with this topic"))
        h, min_h = (e.get("metrics") or {}).get("h_index"), xcfg()["record"]["min_h_index"]
        if e["kind"] == "academic" and h is not None and h < min_h:
            e["findings"].append(checks.f("X-RECORD", "error", f"too little research record yet (h-index {h} on "
                                                              f"{(e.get('metrics') or {}).get('source', 'OpenAlex')}, below {min_h})"))
        elif e["kind"] == "academic" and h is None:
            e["findings"].append(checks.f("X-RECORD", "warning", "no citation record found; check their profile before inviting"))
        if e["scores"]["feasibility"] == 0 and note.get("suggested_format", "").startswith("live"):
            note["suggested_format"] = "recorded_talk"     # no shared working hours with IST: a live slot is unlikely
            note.setdefault("concerns", []).append("no shared working hours with India: a recorded talk or an evening (IST) session")
    for e in top:
        fit = (e.get("note") or {}).get("fit")
        if fit in ("strong", "moderate"):
            e["total"] = round(min(1.0, e["total"] * (1.1 if fit == "strong" else 0.9)), 3)
            e["fit_adjustment"] = fit
    el = xcfg().get("eligibility", {})
    for e in top:                                   # same bar for everyone, IIIT-D faculty included
        if e["scores"]["topical_fit"] < el.get("min_topical_fit", 0):
            e["findings"].append(checks.f("X-ELIGIBLE", "error", f"topical fit {e['scores']['topical_fit']:.2f} is below {el['min_topical_fit']}"))
        elif e["total"] < el.get("min_total", 0):
            e["findings"].append(checks.f("X-ELIGIBLE", "error", f"overall score {e['total']:.2f} is below {el['min_total']}"))
        elif e.get("note") and e["note"].get("fit") not in el.get("allowed_fit", ["strong", "moderate", "weak"]):
            e["findings"].append(checks.f("X-ELIGIBLE", "error", f"AI fit check: {e['note'].get('fit')}"))
    ok = [e for e in top if not any(f["severity"] == "error" for f in e["findings"])]
    chosen = select(ok)
    for i, e in enumerate(chosen, 1):
        e["rank"] = i
    return {"lecture_id": b["lecture_id"], "topic": b["topic"], "experts": [slim(e) for e in chosen],
            "reserve": [slim(e) for e in ok if e not in chosen][:4],
            "rejected": [{"name": e["name"], "why": [f["message"] for f in e["findings"] if f["severity"] == "error"]} for e in top if e not in ok],
            "counts": {"candidates": len(uniq), "assessed": len(top), "passed_checks": len(ok)}}


def clean_why(why: str) -> str:
    """Remove candidate / evidence ids (x3, x2e1, x6's) that must not reach the professor."""
    w = re.sub(r"\s*[\[(]\s*x\d+(?:e\d+)?(?:\s*,\s*x\d+(?:e\d+)?)*\s*[\])]", "", why)
    w = re.sub(r"\s*\b(?:mirrors|like|as|see|with)\s+x\d+(?:e\d+)?(?:['’]s)?(?:\s+contributions?)?", "", w)
    w = re.sub(r"\bx\d+(?:e\d+)?(?:['’]s)?\b", "", w)
    w = re.sub(r"\s{2,}", " ", w).strip(" ,;")
    w = re.sub(r"\s+([.,;])", r"\1", w)
    return w or why


def slim(e: dict) -> dict:
    keep = ("name", "kind", "role", "affiliation", "affiliation_openalex", "country", "links", "metrics", "scores", "total", "rank",
            "verified_identity", "latest_year", "findings", "interests")
    out = {k: e[k] for k in keep if e.get(k) is not None}
    if out.get("affiliation"):
        out["affiliation"] = re.sub(r"\s*\((United States|United Kingdom|India|Germany|China|Canada|Australia)\)", "", out["affiliation"]).strip()
    out["evidence"] = [{k: v for k, v in ev.items() if k != "id" and v is not None} for ev in e["evidence"][:5]]
    if e.get("note"):
        out["why"] = clean_why(e["note"]["why"])
        out["fit"] = e["note"]["fit"]
        out["suggested_format"] = e["note"]["suggested_format"]
        out["concerns"] = e["note"].get("concerns", [])
    out["links"] = {k: v for k, v in (out.get("links") or {}).items() if v}
    return out


# ------------------------------------------------------------------ guest-lecture kit
FORMAT_TEXT = {"live_remote_60": "a 60-minute live session over video call", "live_in_person": "a 60–90-minute in-person lecture",
               "recorded_talk": "a recorded talk students watch before class", "panel": "a short panel with other speakers",
               "qa_after_recorded": "a Q&A after students watch your recorded talk"}


def guest_kit(st: dict, b: dict, experts: list[dict]) -> str:
    cc = st["cco_compact"]
    L = [f"# Guest-lecture kit · {b['lecture_id']} · {b['topic']}", "",
         f"**Course:** {cc['course_name']} · level {st.get('level')}xx · week {b['week']} · {b['hours']:g} h", "",
         "## Brief for the speaker", "", b["summary"], "", "**Learning outcomes for this session**"]
    from profsagent.delivery.brief import clean
    L += [f"- {clean(x['statement'])}." for x in b["learning_outcomes"]]
    if b["builds_on"]:
        L += ["", "**Students will already have seen**"] + [f"- {x['topic']} (week {x['week']})" for x in b["builds_on"]]
    if b["leads_to"] or b["assessed_in"]:
        L += ["", "**What follows this session**"] + [f"- {x['topic']} (week {x['week']})" for x in b["leads_to"]] + \
             [f"- {x['id']} ({x['type']}, week {x['due_week']})" for x in b["assessed_in"]]
    L += ["", "## Suggested speakers (ranked)", ""]
    for e in experts:
        L.append(f"{e['rank']}. **{e['name']}** — {e.get('role') or e['kind']}, {e.get('affiliation') or 'affiliation unknown'}"
                 f"{' (' + e['country'] + ')' if e.get('country') else ''} · score {e['total']:.2f}")
        if e.get("why"):
            L.append(f"   {e['why']}")
    if experts:
        e = experts[0]
        fmt = FORMAT_TEXT.get(e.get("suggested_format", "live_remote_60"), "a guest session")
        L += ["", f"## Invitation draft (edit and send yourself; the system never contacts anyone)", "",
              f"Subject: Invitation to give a guest lecture on {b['topic']} at IIIT-Delhi", "",
              f"Dear {e['name']},", "",
              f"I teach {cc['course_name']} at IIIT-Delhi, a course for {('/'.join(str(y) for y in (cc.get('target_students') or {}).get('years') or []) or 'senior')}-year "
              f"B.Tech students. In week {b['week']} we cover {b['topic']}, and your work"
              f"{' on ' + e['evidence'][0]['title'][:80] if e.get('evidence') else ''} is exactly what our students should see.",
              "", f"Would you be willing to deliver {fmt}? The session aims for students to be able to:"]
        L += [f"- {clean(x['statement'])}." for x in b["learning_outcomes"][:3]]
        L += ["", "I can share the course plan, what students have covered before the session, and a date and time that suits you.", "",
              "With best regards,", "<your name>", "Department of Computer Science and Engineering, IIIT-Delhi"]
    return "\n".join(L)
