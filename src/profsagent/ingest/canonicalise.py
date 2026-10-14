import json
import glob
import hashlib
import re
from pathlib import Path
import difflib

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_ENRICHED_DIR = BASE_DIR / "data" / "enriched"
DATA_CANONICAL_DIR = BASE_DIR / "data" / "canonical"
CUTOFF = 0.75


def topic_slug(name):
    """Same key as the design pipeline's topic links (T:<slug>, kg/stub.slug)."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:60]


def canonical_id(name):
    """Derived from the topic's name, so rerunning (or adding a course) does not renumber every other topic.
    The old TOPIC_<running number> ids depended on set iteration order, which changes with every Python process."""
    return "TOPIC_" + hashlib.sha1(topic_slug(name).encode("utf-8")).hexdigest()[:12].upper()


def cluster_topics(raw_topics, cutoff=CUTOFF):
    """Group topics that are at least `cutoff` similar (difflib). Deterministic: topics are taken in sorted order, and
    get_close_matches ranks (score, string) pairs, so the order of the candidate set does not matter."""
    remaining = sorted(set(raw_topics))
    unassigned = set(remaining)
    clusters = []
    for base in remaining:
        if base not in unassigned:
            continue
        unassigned.remove(base)
        matches = difflib.get_close_matches(base, unassigned, n=15, cutoff=cutoff)
        unassigned.difference_update(matches)
        clusters.append([base] + matches)
    return clusters


def build_mapping(raw_topics, cutoff=CUTOFF):
    """raw topic -> {canonical_id, canonical_name}. The shortest name in a cluster (then alphabetical) is its canonical
    name; clusters whose names differ only in case or punctuation ("Applications" / "applications") share one id."""
    by_id = {}
    for cluster in cluster_topics(raw_topics, cutoff):
        name = min(cluster, key=lambda s: (len(s), s))
        cid = canonical_id(name)
        if cid in by_id:
            prev_name, members = by_id[cid]
            by_id[cid] = (min(prev_name, name, key=lambda s: (len(s), s)), members + cluster)
        else:
            by_id[cid] = (name, cluster)
    return {raw: {"canonical_id": cid, "canonical_name": name}
            for cid, (name, members) in sorted(by_id.items()) for raw in sorted(members)}


def main():
    DATA_CANONICAL_DIR.mkdir(parents=True, exist_ok=True)
    enriched_files = sorted(glob.glob(str(DATA_ENRICHED_DIR / "*.json")))

    print("Step 1: Extracting all raw topics...")
    raw_topics = set()
    for ef in enriched_files:
        with open(ef, "r", encoding="utf-8") as f:
            data = json.load(f)

        for week in data.get("weekly_plan", []):
            for topic in week.get("lecture_topics", []):
                # Clean up the string slightly
                clean_topic = str(topic).strip()
                if clean_topic:
                    raw_topics.add(clean_topic)

    print(f"Found {len(raw_topics)} unique raw topics across {len(enriched_files)} courses.")

    print("Step 2: Clustering into Canonical Topics (Local string matching)...")
    # We use a simple local clustering approach to guarantee it works without API quota limits.
    # We will group topics that are at least 75% similar.
    canonical_mapping = build_mapping(raw_topics)
    print(f"Created {len({v['canonical_id'] for v in canonical_mapping.values()})} canonical topic clusters.")

    out_path = DATA_CANONICAL_DIR / "topic_mapping.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(canonical_mapping, f, indent=4)

    print(f"Done! Canonical mapping saved to {out_path.relative_to(BASE_DIR)}")
    print("The topic ids changed if this replaced an older mapping: reload the graph (load.py --wipe) and the design runs.")


if __name__ == "__main__":
    main()
