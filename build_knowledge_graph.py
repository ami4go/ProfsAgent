"""
ProfsAgent Knowledge Graph Builder
===================================
Builds a Knowledge Graph for CSE222: Algorithm Design & Analysis
using NetworkX and visualizes it with matplotlib.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import os

# ============================================================
# 1. CREATE THE KNOWLEDGE GRAPH
# ============================================================

G = nx.DiGraph()

# ---- COURSE NODE ----
G.add_node("COURSE", 
    type="Course", 
    label="CSE222: Algorithm\nDesign & Analysis",
    title="Algorithm Design & Analysis",
    code="CSE222",
    credits=4,
    prereqs="DSA, IP",
    textbook="Kleinberg & Tardos, Algorithm Design, 2006"
)

# ---- COURSE OBJECTIVES (COs) ----
cos = {
    "CO1": "Design algorithms using greedy, divide & conquer, dynamic programming",
    "CO2": "Analyze correctness and complexity of algorithms",
    "CO3": "Design, analyze, and apply graph algorithms",
    "CO4": "Implement algorithms for solving problems",
    "CO5": "Explain NP-hardness, NP-completeness, and reductions",
}
for co_id, desc in cos.items():
    G.add_node(co_id, type="CO", label=co_id, description=desc)
    G.add_edge("COURSE", co_id, relation="HAS_OBJECTIVE")

# ---- LEARNING OUTCOMES (LOs) ----
los = {
    "LO1": {"desc": "Apply divide & conquer to design recursive algorithms", "bloom": "Apply", "co": "CO1"},
    "LO2": {"desc": "Apply dynamic programming to optimization problems", "bloom": "Apply", "co": "CO1"},
    "LO3": {"desc": "Apply greedy strategy to scheduling & MST problems", "bloom": "Apply", "co": "CO1"},
    "LO4": {"desc": "Prove correctness of algorithms using loop invariants", "bloom": "Analyze", "co": "CO2"},
    "LO5": {"desc": "Analyze time complexity using recurrences & asymptotic notation", "bloom": "Analyze", "co": "CO2"},
    "LO6": {"desc": "Apply BFS, DFS, shortest path, and MST algorithms", "bloom": "Apply", "co": "CO3"},
    "LO7": {"desc": "Implement algorithms in a programming language", "bloom": "Apply", "co": "CO4"},
    "LO8": {"desc": "Explain P vs NP and perform polynomial reductions", "bloom": "Understand", "co": "CO5"},
}
for lo_id, data in los.items():
    G.add_node(lo_id, type="LO", label=lo_id, description=data["desc"], bloom_level=data["bloom"])
    G.add_edge(data["co"], lo_id, relation="DECOMPOSES_INTO")

# ---- MODULES (Weeks) ----
modules = {
    "MOD1": {"title": "Introduction & Asymptotic Analysis", "weeks": "Week 1"},
    "MOD2": {"title": "Divide and Conquer", "weeks": "Weeks 2-3"},
    "MOD3": {"title": "Dynamic Programming", "weeks": "Weeks 4-5"},
    "MOD4": {"title": "Greedy Algorithms", "weeks": "Weeks 6-7"},
    "MOD5": {"title": "Graph Algorithms", "weeks": "Weeks 8-11"},
    "MOD6": {"title": "NP-Completeness", "weeks": "Weeks 12-13"},
}
for mod_id, data in modules.items():
    G.add_node(mod_id, type="Module", label=f"{mod_id}\n{data['weeks']}", title=data["title"], weeks=data["weeks"])

# LO -> Module mappings (TAUGHT_IN)
lo_module_map = {
    "LO5": ["MOD1"],
    "LO1": ["MOD2"],
    "LO2": ["MOD3"],
    "LO3": ["MOD4"],
    "LO4": ["MOD1", "MOD2", "MOD3"],
    "LO6": ["MOD5"],
    "LO7": ["MOD1", "MOD2", "MOD3", "MOD4", "MOD5"],
    "LO8": ["MOD6"],
}
for lo_id, mod_ids in lo_module_map.items():
    for mod_id in mod_ids:
        G.add_edge(lo_id, mod_id, relation="TAUGHT_IN")

# ---- TOPICS ----
topics = {
    # Module 1 Topics
    "T1": {"title": "Asymptotic Notation (Big-O, Ω, Θ)", "hours": 2, "module": "MOD1"},
    "T2": {"title": "Runtime Analysis", "hours": 1, "module": "MOD1"},
    # Module 2 Topics
    "T3": {"title": "Merge Sort", "hours": 2, "module": "MOD2"},
    "T4": {"title": "Binary Search", "hours": 1, "module": "MOD2"},
    "T5": {"title": "Counting Inversions", "hours": 2, "module": "MOD2"},
    "T6": {"title": "Master Theorem", "hours": 2, "module": "MOD2"},
    # Module 3 Topics
    "T7": {"title": "Fibonacci (DP)", "hours": 1, "module": "MOD3"},
    "T8": {"title": "Chain Matrix Multiplication", "hours": 2, "module": "MOD3"},
    "T9": {"title": "0/1 Knapsack Problem", "hours": 2, "module": "MOD3"},
    "T10": {"title": "Sequence Alignment", "hours": 2, "module": "MOD3"},
    "T11": {"title": "Bellman-Ford Algorithm", "hours": 2, "module": "MOD3"},
    # Module 4 Topics
    "T12": {"title": "Interval Scheduling", "hours": 2, "module": "MOD4"},
    "T13": {"title": "Prim's Algorithm (MST)", "hours": 2, "module": "MOD4"},
    "T14": {"title": "Kruskal's Algorithm (MST)", "hours": 2, "module": "MOD4"},
    "T15": {"title": "Huffman Coding", "hours": 2, "module": "MOD4"},
    # Module 5 Topics
    "T16": {"title": "BFS & DFS", "hours": 3, "module": "MOD5"},
    "T17": {"title": "Dijkstra's Shortest Path", "hours": 2, "module": "MOD5"},
    "T18": {"title": "Topological Sort", "hours": 2, "module": "MOD5"},
    "T19": {"title": "Strongly Connected Components", "hours": 2, "module": "MOD5"},
    # Module 6 Topics
    "T20": {"title": "P vs NP", "hours": 2, "module": "MOD6"},
    "T21": {"title": "NP-Completeness Proofs", "hours": 3, "module": "MOD6"},
    "T22": {"title": "Polynomial Reductions", "hours": 3, "module": "MOD6"},
}
for t_id, data in topics.items():
    G.add_node(t_id, type="Topic", label=t_id, title=data["title"], estimated_hours=data["hours"])
    G.add_edge(data["module"], t_id, relation="CONTAINS")

# Topic Prerequisites (PREREQUISITE_OF)
prereq_edges = [
    ("T1", "T6"),   # Asymptotic Notation -> Master Theorem
    ("T3", "T5"),   # Merge Sort -> Counting Inversions
    ("T7", "T9"),   # Fibonacci DP -> Knapsack
    ("T16", "T17"), # BFS/DFS -> Dijkstra
    ("T16", "T18"), # BFS/DFS -> Topological Sort
    ("T18", "T19"), # Topological Sort -> SCC
    ("T20", "T21"), # P vs NP -> NP-Completeness Proofs
    ("T21", "T22"), # NP-Completeness -> Reductions
]
for src, dst in prereq_edges:
    G.add_edge(src, dst, relation="PREREQUISITE_OF")

# ---- MATERIALS ----
materials = {
    "MAT1": {"title": "Kleinberg & Tardos Ch. 2", "type": "Textbook"},
    "MAT2": {"title": "Kleinberg & Tardos Ch. 5", "type": "Textbook"},
    "MAT3": {"title": "Kleinberg & Tardos Ch. 6", "type": "Textbook"},
    "MAT4": {"title": "Kleinberg & Tardos Ch. 4", "type": "Textbook"},
    "MAT5": {"title": "Kleinberg & Tardos Ch. 3", "type": "Textbook"},
    "MAT6": {"title": "Kleinberg & Tardos Ch. 8", "type": "Textbook"},
}
mat_topic_map = {
    "MAT1": ["T1", "T2"],
    "MAT2": ["T3", "T4", "T5", "T6"],
    "MAT3": ["T7", "T8", "T9", "T10", "T11"],
    "MAT4": ["T12", "T13", "T14", "T15"],
    "MAT5": ["T16", "T17", "T18", "T19"],
    "MAT6": ["T20", "T21", "T22"],
}
for mat_id, data in materials.items():
    G.add_node(mat_id, type="Material", label=mat_id, title=data["title"], material_type=data["type"])
    for t_id in mat_topic_map[mat_id]:
        G.add_edge(t_id, mat_id, relation="SUPPORTED_BY")

# ---- ASSESSMENTS ----
assessments = {
    "ASS1": {"title": "Programming Assignment 1", "type": "Assignment", "weight": 5},
    "ASS2": {"title": "Programming Assignment 2", "type": "Assignment", "weight": 5},
    "ASS3": {"title": "Programming Assignment 3", "type": "Assignment", "weight": 5},
    "ASS4": {"title": "Quiz 1", "type": "Quiz", "weight": 12.5},
    "ASS5": {"title": "Quiz 2", "type": "Quiz", "weight": 12.5},
    "ASS6": {"title": "Mid-Semester Exam", "type": "Exam", "weight": 30},
    "ASS7": {"title": "End-Semester Exam", "type": "Exam", "weight": 30},
}
for ass_id, data in assessments.items():
    G.add_node(ass_id, type="Assessment", label=f"{ass_id}\n{data['type']}", 
               title=data["title"], assessment_type=data["type"], weight=data["weight"])

# LO -> Assessment mappings (ASSESSED_BY)
lo_assessment_map = {
    "LO1": ["ASS1", "ASS4", "ASS6"],
    "LO2": ["ASS2", "ASS5", "ASS6", "ASS7"],
    "LO3": ["ASS2", "ASS5", "ASS6"],
    "LO4": ["ASS4", "ASS6", "ASS7"],
    "LO5": ["ASS4", "ASS6", "ASS7"],
    "LO6": ["ASS3", "ASS5", "ASS7"],
    "LO7": ["ASS1", "ASS2", "ASS3"],
    "LO8": ["ASS7"],
}
for lo_id, ass_ids in lo_assessment_map.items():
    for ass_id in ass_ids:
        G.add_edge(lo_id, ass_id, relation="ASSESSED_BY")


# ============================================================
# 2. VALIDATION QUERIES (The Superpower)
# ============================================================

print("=" * 60)
print("  PROFSAGENT KNOWLEDGE GRAPH — VALIDATION REPORT")
print("  Course: CSE222 Algorithm Design & Analysis")
print("=" * 60)

# Check 1: Orphan LOs (LOs not assessed)
print("\n✅ CHECK 1: Orphan Learning Outcomes (LOs with no assessment)")
lo_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "LO"]
orphan_los = []
for lo in lo_nodes:
    assessed = any(G[lo][nbr].get("relation") == "ASSESSED_BY" for nbr in G.successors(lo) if G.has_edge(lo, nbr))
    if not assessed:
        orphan_los.append(lo)
if orphan_los:
    print(f"   ❌ FAIL: {orphan_los} have no assessments!")
else:
    print("   ✅ PASS: All LOs are assessed.")

# Check 2: Orphan LOs (LOs not taught)
print("\n✅ CHECK 2: Orphan Learning Outcomes (LOs not taught in any module)")
untaught_los = []
for lo in lo_nodes:
    taught = any(G[lo][nbr].get("relation") == "TAUGHT_IN" for nbr in G.successors(lo) if G.has_edge(lo, nbr))
    if not taught:
        untaught_los.append(lo)
if untaught_los:
    print(f"   ❌ FAIL: {untaught_los} are never taught!")
else:
    print("   ✅ PASS: All LOs are taught in at least one module.")

# Check 3: Assessment Weight Sum
print("\n✅ CHECK 3: Assessment Weights Sum to 100%")
ass_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "Assessment"]
total_weight = sum(G.nodes[a].get("weight", 0) for a in ass_nodes)
if abs(total_weight - 100) < 0.01:
    print(f"   ✅ PASS: Total weight = {total_weight}%")
else:
    print(f"   ⚠️ WARNING: Total weight = {total_weight}% (expected 100%)")

# Check 4: Workload per module
print("\n✅ CHECK 4: Workload Balance (estimated hours per module)")
mod_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "Module"]
for mod in sorted(mod_nodes):
    topic_children = [nbr for nbr in G.successors(mod) if G.nodes[nbr].get("type") == "Topic"]
    total_hours = sum(G.nodes[t].get("estimated_hours", 0) for t in topic_children)
    weeks_str = G.nodes[mod].get("weeks", "")
    print(f"   {mod} ({weeks_str}): {total_hours} hours across {len(topic_children)} topics")

# Check 5: CO Coverage
print("\n✅ CHECK 5: CO → LO Coverage (Every CO has at least one LO)")
co_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "CO"]
for co in sorted(co_nodes):
    lo_children = [nbr for nbr in G.successors(co) if G.nodes[nbr].get("type") == "LO"]
    status = "✅" if lo_children else "❌"
    print(f"   {status} {co}: {len(lo_children)} LOs")

# Graph Stats
print("\n" + "=" * 60)
print(f"  GRAPH STATS: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
node_types = {}
for _, d in G.nodes(data=True):
    t = d.get("type", "Unknown")
    node_types[t] = node_types.get(t, 0) + 1
for t, c in sorted(node_types.items()):
    print(f"    {t}: {c}")
print("=" * 60)


# ============================================================
# 3. VISUALIZE THE KNOWLEDGE GRAPH
# ============================================================

# Color map by node type
color_map = {
    "Course": "#1565C0",
    "CO": "#2E7D32",
    "LO": "#66BB6A",
    "Module": "#E65100",
    "Topic": "#FFB74D",
    "Material": "#7E57C2",
    "Assessment": "#C62828",
}

node_colors = [color_map.get(G.nodes[n].get("type", ""), "#999999") for n in G.nodes()]
node_sizes = []
for n in G.nodes():
    t = G.nodes[n].get("type", "")
    if t == "Course":
        node_sizes.append(1200)
    elif t in ("CO", "Module"):
        node_sizes.append(800)
    elif t in ("LO", "Assessment"):
        node_sizes.append(600)
    else:
        node_sizes.append(400)

labels = {n: G.nodes[n].get("label", n) for n in G.nodes()}

fig, ax = plt.subplots(1, 1, figsize=(24, 16))
fig.patch.set_facecolor("#FAFAFA")
ax.set_facecolor("#FAFAFA")

# Use spring layout for a clear spread
pos = nx.spring_layout(G, k=2.5, iterations=80, seed=42)

# Draw edges
nx.draw_networkx_edges(G, pos, ax=ax, 
                       edge_color="#BBBBBB", 
                       arrows=True, 
                       arrowsize=12, 
                       width=0.8,
                       alpha=0.6,
                       connectionstyle="arc3,rad=0.05")

# Draw nodes
nx.draw_networkx_nodes(G, pos, ax=ax,
                       node_color=node_colors,
                       node_size=node_sizes,
                       edgecolors="white",
                       linewidths=1.5)

# Draw labels
nx.draw_networkx_labels(G, pos, labels, ax=ax,
                        font_size=6, 
                        font_weight="bold",
                        font_color="white")

# Legend
legend_handles = [mpatches.Patch(color=c, label=t) for t, c in color_map.items()]
ax.legend(handles=legend_handles, loc="upper left", fontsize=10, 
          framealpha=0.9, edgecolor="#CCCCCC", title="Node Types", title_fontsize=11)

ax.set_title("ProfsAgent Knowledge Graph — CSE222: Algorithm Design & Analysis", 
             fontsize=16, fontweight="bold", pad=20)
ax.axis("off")

plt.tight_layout()

# Save
output_dir = r"C:\Users\amitk\OneDrive\Desktop\ProfsAgent"
output_path = os.path.join(output_dir, "cse222_knowledge_graph.png")
plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#FAFAFA")
print(f"\n📊 Knowledge Graph saved to: {output_path}")

# Also save as JSON for future use
graph_data = {
    "nodes": [],
    "edges": []
}
for n, d in G.nodes(data=True):
    node_data = {"id": n}
    node_data.update({k: v for k, v in d.items() if k != "label"})
    graph_data["nodes"].append(node_data)
for u, v, d in G.edges(data=True):
    graph_data["edges"].append({"source": u, "target": v, "relation": d.get("relation", "")})

json_path = os.path.join(output_dir, "cse222_knowledge_graph.json")
with open(json_path, "w") as f:
    json.dump(graph_data, f, indent=2)
print(f"📄 Graph data saved to: {json_path}")
print("\n🎉 Done! Open cse222_knowledge_graph.png to see the visual graph.")
