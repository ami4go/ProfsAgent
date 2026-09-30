import json
import glob
from pathlib import Path
import difflib

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_ENRICHED_DIR = BASE_DIR / "data" / "enriched"
DATA_CANONICAL_DIR = BASE_DIR / "data" / "canonical"

def main():
    DATA_CANONICAL_DIR.mkdir(parents=True, exist_ok=True)
    enriched_files = glob.glob(str(DATA_ENRICHED_DIR / "*.json"))
    
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
                    
    raw_topics = sorted(list(raw_topics))
    print(f"Found {len(raw_topics)} unique raw topics across {len(enriched_files)} courses.")
    
    print("Step 2: Clustering into Canonical Topics (Local string matching)...")
    # We use a simple local clustering approach to guarantee it works without API quota limits.
    # We will group topics that are at least 75% similar.
    
    clusters = []
    unassigned = set(raw_topics)
    
    while unassigned:
        base = unassigned.pop()
        # Find all close matches in the remaining unassigned topics
        matches = difflib.get_close_matches(base, unassigned, n=15, cutoff=0.75)
        
        cluster = [base] + matches
        for m in matches:
            if m in unassigned:
                unassigned.remove(m)
        clusters.append(cluster)
        
    print(f"Created {len(clusters)} canonical topic clusters.")
    
    print("Step 3: Generating Canonical Mapping...")
    canonical_mapping = {}
    for idx, cluster in enumerate(clusters):
        # The shortest string in the cluster is usually the best "canonical" name
        canonical_name = sorted(cluster, key=len)[0]
        canonical_id = f"TOPIC_{idx:04d}"
        
        for raw_topic in cluster:
            canonical_mapping[raw_topic] = {
                "canonical_id": canonical_id,
                "canonical_name": canonical_name
            }
            
    out_path = DATA_CANONICAL_DIR / "topic_mapping.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(canonical_mapping, f, indent=4)
        
    print(f"Done! Canonical mapping saved to {out_path.relative_to(BASE_DIR)}")

if __name__ == "__main__":
    main()
