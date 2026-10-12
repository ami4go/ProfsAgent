"""
Enrichers for extracted course data:
  1. Bloom Verb Tagger   — tags each CO with its Bloom's Taxonomy level
  2. CO Quality Scorer   — checks if a CO is well-formed (verb + object + context)
  3. Course Code Resolver — sets each course's code from TechTree (sheet codes become aliases) and maps
                            prerequisite text to the codes of courses in the corpus
  4. CO reference check  — moves week CO references that match no outcome into cos_met_unknown
  5. Assessment Typer    — tags each assessment component with a standard type (endsem, quiz, ...)
  6. Catalogue details   — adds TechTree's entry (credits, semester, cluster, catalogue link), the course
                            level, prerequisite links from the sheet and TechTree, and anti-requisites
"""

import json
import glob
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_EXTRACTED_DIR = BASE_DIR / "data" / "extracted"
DATA_ENRICHED_DIR = BASE_DIR / "data" / "enriched"
TECHTREE_INDEX_PATH = BASE_DIR / "data" / "techtree_index.json"  # written by crawl.py

# ---------------------------------------------------------------------------
# Bloom's Taxonomy verb mapping (Anderson & Krathwohl, 2001)
# ---------------------------------------------------------------------------
BLOOM_LEVELS = {
    "Remember": [
        "define", "list", "recall", "recognize", "identify", "name", "state",
        "describe", "label", "match", "memorize", "repeat", "select"
    ],
    "Understand": [
        "explain", "summarize", "paraphrase", "classify", "compare",
        "interpret", "discuss", "distinguish", "illustrate", "predict",
        "translate", "give examples", "infer", "contrast"
    ],
    "Apply": [
        "apply", "demonstrate", "implement", "solve", "use", "execute",
        "compute", "calculate", "carry out", "operate", "practice",
        "construct", "develop", "modify"
    ],
    "Analyze": [
        "analyze", "differentiate", "organize", "attribute", "deconstruct",
        "examine", "investigate", "categorize", "break down", "outline",
        "integrate", "structure", "relate"
    ],
    "Evaluate": [
        "evaluate", "judge", "justify", "critique", "assess", "defend",
        "argue", "support", "appraise", "recommend", "validate", "test",
        "monitor", "check", "review"
    ],
    "Create": [
        "create", "design", "generate", "produce", "plan", "compose",
        "formulate", "devise", "construct", "invent", "propose",
        "synthesize", "build", "develop"
    ]
}

def tag_bloom_level(co_text):
    """
    Returns the highest Bloom level found in the CO text.
    Bloom levels are ordered: Remember < Understand < Apply < Analyze < Evaluate < Create.
    We return the HIGHEST level verb found, since that represents the cognitive ceiling.
    """
    co_lower = co_text.lower()
    level_order = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
    
    found_level = None
    found_verb = None
    
    for level in level_order:
        for verb in BLOOM_LEVELS[level]:
            # Match verb at word boundaries
            pattern = r'\b' + re.escape(verb) + r'\b'
            if re.search(pattern, co_lower):
                found_level = level
                found_verb = verb
                # Don't break — keep scanning for higher levels
                
    return found_level or "Unclassified", found_verb or ""

def score_co_quality(co_text):
    """
    Scores a CO on a 0-3 scale:
      +1 if it starts with an action verb (Bloom verb detected)
      +1 if it has a clear object (> 5 words after the verb)
      +1 if it has context/condition (words like 'given', 'using', 'by', 'through')
    """
    score = 0
    reasons = []
    
    bloom_level, verb = tag_bloom_level(co_text)
    if bloom_level != "Unclassified":
        score += 1
        reasons.append(f"action_verb={verb}")
    else:
        reasons.append("no_bloom_verb")
    
    words = co_text.split()
    if len(words) > 8:
        score += 1
        reasons.append("has_object")
    else:
        reasons.append("too_short")
    
    context_markers = ["given", "using", "by", "through", "in the context", 
                       "for", "within", "based on", "including"]
    co_lower = co_text.lower()
    if any(marker in co_lower for marker in context_markers):
        score += 1
        reasons.append("has_context")
    else:
        reasons.append("no_context")
    
    return score, reasons

# ---------------------------------------------------------------------------
# Assessment types — the same rules, in the same order, as assess_type() in kg/stub.py,
# so assessment priors from the graph match what the design pipeline expects
# ---------------------------------------------------------------------------
ASSESSMENT_TYPES = [
    ("endsem", r"end[\s-]*sem|final exam|end[\s-]*term|final"), ("midsem", r"mid[\s-]*sem|mid[\s-]*term"),
    ("quiz", r"quiz"), ("lab", r"\blab"), ("project", r"project"), ("assignment", r"assignment|homework|problem set"),
    ("presentation", r"presentation|seminar"), ("report", r"report|paper|state of art"),
    ("participation", r"participation|attendance|in-?class|peer"),
]

def classify_assessment(type_label):
    """Standard type for a sheet's assessment label, e.g. "Midsem (theory+lab)" -> "midsem"."""
    for assessment_type, pattern in ASSESSMENT_TYPES:
        if re.search(pattern, type_label or "", re.I):
            return assessment_type
    return "other"

# "CSE 101", "MTH-101", "CSE343/543" (a bare number after "/" takes the previous prefix)
CODE_PATTERN = re.compile(r"\b([A-Za-z]{2,4})\s*-?\s*(\d{3}[A-Za-z]?)\b((?:\s*/\s*\d{3}[A-Za-z]?\b)*)")

def find_course_codes(text):
    """All course codes in free text, normalised.
    e.g., "ML (CSE343/543) or DL (CSE 641)" -> ["CSE343", "CSE543", "CSE641"]
    """
    codes = []
    for prefix, number, more in CODE_PATTERN.findall(text or ""):
        prefix = prefix.upper()
        for num in [number, *re.findall(r"\d{3}[A-Za-z]?", more)]:
            code = prefix + num.upper()
            if code not in codes:
                codes.append(code)
    return codes

def assign_course_codes(header, techtree_code):
    """
    Returns (primary code, aliases) for one course.
    TechTree's code wins: sheets carry typos, old numbers and placeholders (CSE601's sheet says
    "CSE 301", SOC101's says "SOC201"), so the sheet's codes are kept only as aliases. When TechTree
    has a placeholder (ENTxxx, SSH3PT) the sheet's code is used; when neither has a real code,
    TechTree's id is kept as-is (BIO5XX, CSE5GP).
    """
    official = find_course_codes(techtree_code)
    from_sheet = find_course_codes(header.get("course_code"))
    for alias in header.get("aliases") or []:
        from_sheet += find_course_codes(alias)
    techtree_id = re.sub(r"[\s\-_]", "", techtree_code).upper()

    if official:
        primary = official[0]
    elif from_sheet:
        primary = from_sheet[0]
        if "XX" not in techtree_id:
            official = [techtree_id]  # keep TechTree's own id (e.g. SSH3PT) findable as an alias
    else:
        primary = techtree_id

    aliases = []
    for code in official + from_sheet:
        if code != primary and code not in aliases:
            aliases.append(code)
    return primary, aliases

def build_code_index(course_codes, official_codes):
    """
    Maps every primary code and alias to its course's primary code.
    Raises if two courses share a primary code (load.py merges courses by code). An alias that is
    another course's primary code is dropped. An alias several courses claim stays only with the one
    course whose TechTree code lists it (official_codes), otherwise it is dropped from all of them.
    """
    primaries = {}
    for stem, (primary, _) in course_codes.items():
        if primary in primaries:
            raise ValueError(f"{stem} and {primaries[primary]} both resolve to course code {primary}")
        primaries[primary] = stem

    claims = {}
    for stem, (primary, aliases) in course_codes.items():
        for alias in aliases:
            claims.setdefault(alias, []).append(stem)
    keep = {}  # alias -> the only stem allowed to keep it
    for alias, stems in sorted(claims.items()):
        if alias in primaries:
            reason, owner = f"the code of {primaries[alias]}", None
        elif len(stems) > 1:
            official = [s for s in stems if alias in official_codes.get(s, ())]
            owner = official[0] if len(official) == 1 else None
            reason = f"kept on {owner}, its TechTree code" if owner else "claimed by several courses"
        else:
            continue
        keep[alias] = owner
        losers = [s for s in stems if s != owner]
        print(f"  Dropping alias {alias} from {', '.join(losers)} ({reason})")
    for stem, (primary, aliases) in course_codes.items():
        course_codes[stem] = (primary, [a for a in aliases if a not in keep or keep[a] == stem])

    index = {primary: primary for primary in primaries}
    for primary, aliases in course_codes.values():
        index.update({alias: primary for alias in aliases})
    return index

def resolve_prerequisites(raw_prereqs, code_index, own_code):
    """
    Codes of the corpus courses a list of prerequisite strings mentions (all alternatives in
    "X or Y" are kept, as in kg/stub.py). Codes of courses not in the corpus and plain-text
    prerequisites such as "Intro to Programming" are dropped; the raw text stays on the header.
    """
    resolved = []
    for raw in raw_prereqs or []:
        for code in find_course_codes(raw):
            primary = code_index.get(code)
            if primary and primary != own_code and primary not in resolved:
                resolved.append(primary)
    return resolved

def prerequisite_links(header, catalogue, code_index, own_code):
    """
    One entry per prerequisite course, merged from the sheet and TechTree's catalogue columns:
    {code, kind: "mandatory" | "desirable", sources: ["sheet", "techtree"]}.
    A course that any source lists as mandatory is mandatory.
    """
    links = {}
    def add(raw_prereqs, kind, source):
        for code in resolve_prerequisites(raw_prereqs, code_index, own_code):
            link = links.setdefault(code, {"code": code, "kind": kind, "sources": []})
            if kind == "mandatory":
                link["kind"] = "mandatory"
            if source not in link["sources"]:
                link["sources"].append(source)
    add(header.get("prerequisites_mandatory"), "mandatory", "sheet")
    add([catalogue.get("prerequisites")], "mandatory", "techtree")
    add(header.get("prerequisites_desirable"), "desirable", "sheet")
    add([catalogue.get("preferable_prerequisites")], "desirable", "techtree")
    for link in links.values():
        link["sources"].sort()
    return list(links.values())

def course_level(code):
    """First digit of the course code (CSE101 -> 1, CSE5GP -> 5), the rule scripts/build_stub_kg.py uses."""
    match = re.search(r"\d", code or "")
    return int(match.group()) if match else None

def enrich_course(extracted_data, primary, aliases, code_index, catalogue):
    """Enriches a single extracted course JSON with Bloom tags, quality scores, codes, resolved prereqs
    and its TechTree catalogue details."""
    enriched = extracted_data.copy()

    # Enrich Course Outcomes
    for co in enriched.get("outcomes", []):
        bloom_level, bloom_verb = tag_bloom_level(co["raw_text"])
        quality_score, quality_reasons = score_co_quality(co["raw_text"])
        co["bloom_level"] = bloom_level
        co["bloom_verb"] = bloom_verb
        co["quality_score"] = quality_score
        co["quality_reasons"] = quality_reasons

    # Week CO references must name an outcome (some sheets cite e.g. CO5 but list only four COs)
    labels = {co["label"] for co in enriched.get("outcomes", [])}
    for week in enriched.get("weekly_plan", []):
        unknown = [label for label in week.get("cos_met", []) if label not in labels]
        if unknown:
            week["cos_met"] = [label for label in week["cos_met"] if label in labels]
            week["cos_met_unknown"] = unknown

    # Assessment components keep the sheet's label and get a standard type
    for component in enriched.get("assessments", []):
        component["type"] = classify_assessment(component.get("type_label"))

    # Course codes and prerequisites
    header = enriched.get("header", {})
    header["course_code"] = primary
    header["aliases"] = aliases
    header["prerequisites_mandatory_resolved"] = resolve_prerequisites(
        header.get("prerequisites_mandatory"), code_index, primary)
    header["prerequisites_desirable_resolved"] = resolve_prerequisites(
        header.get("prerequisites_desirable"), code_index, primary)

    # Catalogue details from TechTree, plus links merged from the sheet and the catalogue
    header["level"] = course_level(primary)
    header["catalogue"] = {k: v for k, v in catalogue.items() if k not in ("code", "name")}
    header["prerequisite_links"] = prerequisite_links(header, catalogue, code_index, primary)
    header["anti_requisites_resolved"] = resolve_prerequisites([catalogue.get("antirequisites")], code_index, primary)

    return enriched

def main():
    DATA_ENRICHED_DIR.mkdir(parents=True, exist_ok=True)
    with open(TECHTREE_INDEX_PATH, "r", encoding="utf-8") as f:
        techtree = json.load(f)

    extracted_files = sorted(glob.glob(str(DATA_EXTRACTED_DIR / "*.json")))
    print(f"Found {len(extracted_files)} extracted files. Enriching...")

    # Codes first: resolving prerequisites needs every course's code and aliases
    courses = {}
    for ef in extracted_files:
        with open(ef, "r", encoding="utf-8") as f:
            courses[Path(ef).stem] = json.load(f)
    techtree_codes = {stem: techtree.get(stem, {}).get("code", stem) for stem in courses}
    course_codes = {stem: assign_course_codes(data["header"], techtree_codes[stem]) for stem, data in courses.items()}
    official_codes = {stem: set(find_course_codes(code)) for stem, code in techtree_codes.items()}
    code_index = build_code_index(course_codes, official_codes)

    success = 0
    for code, data in courses.items():
        try:
            primary, aliases = course_codes[code]
            enriched = enrich_course(data, primary, aliases, code_index, techtree.get(code, {}))
            out_path = DATA_ENRICHED_DIR / f"{code}.json"
            with open(out_path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(enriched, f, indent=4)
            success += 1
        except Exception as e:
            print(f"  Failed to enrich {code}: {e}")

    print(f"Enriched {success} / {len(extracted_files)} courses.")

if __name__ == "__main__":
    main()
