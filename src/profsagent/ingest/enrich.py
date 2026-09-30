"""
Enrichers for extracted course data:
  1. Bloom Verb Tagger   — tags each CO with its Bloom's Taxonomy level
  2. CO Quality Scorer   — checks if a CO is well-formed (verb + object + context)
  3. Course Code Resolver — normalises prerequisite strings into clean course codes
"""

import json
import glob
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_EXTRACTED_DIR = BASE_DIR / "data" / "extracted"
DATA_ENRICHED_DIR = BASE_DIR / "data" / "enriched"

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

def resolve_course_code(raw_prereq):
    """
    Normalises a prerequisite string into a clean course code.
    e.g., "CSE 101" -> "CSE101", "cse101" -> "CSE101", "None" -> None
    """
    if not raw_prereq:
        return None
    raw = raw_prereq.strip()
    if raw.lower() in ("none", "nil", "na", "n/a", "-", ""):
        return None
    
    # Try to extract a pattern like CSE101, CSE 101, cse-101
    match = re.match(r'([A-Za-z]{2,5})\s*[-]?\s*(\d{3,4}[A-Za-z]?)', raw)
    if match:
        dept = match.group(1).upper()
        num = match.group(2).upper()
        return f"{dept}{num}"
    
    return raw  # Return as-is if we can't parse it

def enrich_course(extracted_data):
    """Enriches a single extracted course JSON with Bloom tags, quality scores, and resolved prereqs."""
    enriched = extracted_data.copy()
    
    # Enrich Course Outcomes
    for co in enriched.get("outcomes", []):
        bloom_level, bloom_verb = tag_bloom_level(co["raw_text"])
        quality_score, quality_reasons = score_co_quality(co["raw_text"])
        co["bloom_level"] = bloom_level
        co["bloom_verb"] = bloom_verb
        co["quality_score"] = quality_score
        co["quality_reasons"] = quality_reasons
    
    # Resolve prerequisite codes
    header = enriched.get("header", {})
    header["prerequisites_mandatory_resolved"] = [
        resolved for raw in header.get("prerequisites_mandatory", [])
        if (resolved := resolve_course_code(raw)) is not None
    ]
    header["prerequisites_desirable_resolved"] = [
        resolved for raw in header.get("prerequisites_desirable", [])
        if (resolved := resolve_course_code(raw)) is not None
    ]
    
    return enriched

def main():
    DATA_ENRICHED_DIR.mkdir(parents=True, exist_ok=True)
    
    extracted_files = sorted(glob.glob(str(DATA_EXTRACTED_DIR / "*.json")))
    print(f"Found {len(extracted_files)} extracted files. Enriching...")
    
    success = 0
    for ef in extracted_files:
        code = Path(ef).stem
        try:
            with open(ef, "r", encoding="utf-8") as f:
                data = json.load(f)
            enriched = enrich_course(data)
            out_path = DATA_ENRICHED_DIR / f"{code}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(enriched, f, indent=4)
            success += 1
        except Exception as e:
            print(f"  Failed to enrich {code}: {e}")
    
    print(f"Enriched {success} / {len(extracted_files)} courses.")

if __name__ == "__main__":
    main()
