"""
ProfsAgent Knowledge Graph — Hierarchical Layered Visualization
================================================================
Creates a clean, top-to-bottom layered view of the CSE222 Knowledge Graph.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import os
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ============================================================
# 1. REBUILD THE GRAPH (same data as before)
# ============================================================

G = nx.DiGraph()

# Course
G.add_node("COURSE", type="Course", title="CSE222: Algorithm Design & Analysis")

# COs
cos = {
    "CO1": "Design algorithms (greedy, D&C, DP)",
    "CO2": "Analyze correctness & complexity",
    "CO3": "Design & apply graph algorithms",
    "CO4": "Implement algorithms",
    "CO5": "Explain NP-hardness & reductions",
}
for co_id, desc in cos.items():
    G.add_node(co_id, type="CO", title=desc)
    G.add_edge("COURSE", co_id, relation="HAS_OBJECTIVE")

# LOs
los = {
    "LO1": {"desc": "Apply D&C to recursive algorithms", "bloom": "Apply", "co": "CO1"},
    "LO2": {"desc": "Apply DP to optimization", "bloom": "Apply", "co": "CO1"},
    "LO3": {"desc": "Apply greedy to scheduling & MST", "bloom": "Apply", "co": "CO1"},
    "LO4": {"desc": "Prove correctness (loop invariants)", "bloom": "Analyze", "co": "CO2"},
    "LO5": {"desc": "Analyze complexity (recurrences)", "bloom": "Analyze", "co": "CO2"},
    "LO6": {"desc": "Apply BFS, DFS, shortest path, MST", "bloom": "Apply", "co": "CO3"},
    "LO7": {"desc": "Implement algorithms in code", "bloom": "Apply", "co": "CO4"},
    "LO8": {"desc": "Explain P vs NP, reductions", "bloom": "Understand", "co": "CO5"},
}
for lo_id, data in los.items():
    G.add_node(lo_id, type="LO", title=data["desc"], bloom=data["bloom"])
    G.add_edge(data["co"], lo_id, relation="DECOMPOSES_INTO")

# Modules
modules = {
    "MOD1": "Wk 1: Intro & Asymptotic",
    "MOD2": "Wk 2-3: Divide & Conquer",
    "MOD3": "Wk 4-5: Dynamic Prog.",
    "MOD4": "Wk 6-7: Greedy",
    "MOD5": "Wk 8-11: Graphs",
    "MOD6": "Wk 12-13: NP-Complete",
}
for mod_id, title in modules.items():
    G.add_node(mod_id, type="Module", title=title)

lo_mod = {
    "LO1": ["MOD2"], "LO2": ["MOD3"], "LO3": ["MOD4"],
    "LO4": ["MOD1", "MOD2", "MOD3"], "LO5": ["MOD1"],
    "LO6": ["MOD5"], "LO7": ["MOD2", "MOD3", "MOD4", "MOD5"],
    "LO8": ["MOD6"],
}
for lo, mods in lo_mod.items():
    for m in mods:
        G.add_edge(lo, m, relation="TAUGHT_IN")

# Topics (abbreviated for clarity in chart)
topics_data = {
    "MOD1": ["T1: Big-O Notation", "T2: Runtime Analysis"],
    "MOD2": ["T3: Merge Sort", "T4: Binary Search", "T5: Count Inversions", "T6: Master Theorem"],
    "MOD3": ["T7: Fibonacci DP", "T8: Matrix Chain", "T9: 0/1 Knapsack", "T10: Seq. Alignment", "T11: Bellman-Ford"],
    "MOD4": ["T12: Interval Sched.", "T13: Prim's MST", "T14: Kruskal's MST", "T15: Huffman Coding"],
    "MOD5": ["T16: BFS & DFS", "T17: Dijkstra", "T18: Topological Sort", "T19: SCC"],
    "MOD6": ["T20: P vs NP", "T21: NP-Complete Proofs", "T22: Poly. Reductions"],
}
for mod_id, topic_list in topics_data.items():
    for t_str in topic_list:
        t_id = t_str.split(":")[0].strip()
        G.add_node(t_id, type="Topic", title=t_str.split(": ", 1)[1])
        G.add_edge(mod_id, t_id, relation="CONTAINS")

# Assessments
assessments = {
    "A1": "PA 1 (5%)", "A2": "PA 2 (5%)", "A3": "PA 3 (5%)",
    "A4": "Quiz 1 (12.5%)", "A5": "Quiz 2 (12.5%)",
    "A6": "Mid-Sem (30%)", "A7": "End-Sem (30%)",
}
for a_id, title in assessments.items():
    G.add_node(a_id, type="Assessment", title=title)

lo_ass = {
    "LO1": ["A1", "A4", "A6"], "LO2": ["A2", "A5", "A6", "A7"],
    "LO3": ["A2", "A5", "A6"], "LO4": ["A4", "A6", "A7"],
    "LO5": ["A4", "A6", "A7"], "LO6": ["A3", "A5", "A7"],
    "LO7": ["A1", "A2", "A3"], "LO8": ["A7"],
}
for lo, asses in lo_ass.items():
    for a in asses:
        G.add_edge(lo, a, relation="ASSESSED_BY")

# ============================================================
# 2. HIERARCHICAL LAYOUT (Custom layered positioning)
# ============================================================

# Define layers (y-position, top to bottom)
layers = {
    "Course": 6,
    "CO": 5,
    "LO": 4,
    "Module": 3,
    "Topic": 2,
    "Assessment": 1,
}

# Sort nodes into their layers
layer_nodes = {k: [] for k in layers}
for n, d in G.nodes(data=True):
    t = d.get("type", "")
    if t in layer_nodes:
        layer_nodes[t].append(n)

# Sort within each layer for consistent ordering
for k in layer_nodes:
    layer_nodes[k] = sorted(layer_nodes[k])

# Assign x,y positions
pos = {}
for layer_name, y_val in layers.items():
    nodes_in_layer = layer_nodes[layer_name]
    n_count = len(nodes_in_layer)
    if n_count == 0:
        continue
    # Spread evenly across x-axis
    total_width = max(n_count * 1.8, 2)
    start_x = -total_width / 2
    spacing = total_width / max(n_count - 1, 1) if n_count > 1 else 0
    for i, node in enumerate(nodes_in_layer):
        pos[node] = (start_x + i * spacing, y_val * 3)

# ============================================================
# 3. DRAW THE LAYERED GRAPH
# ============================================================

color_map = {
    "Course": "#1565C0",
    "CO": "#2E7D32",
    "LO": "#66BB6A",
    "Module": "#E65100",
    "Topic": "#FFB74D",
    "Assessment": "#C62828",
}

size_map = {
    "Course": 1400,
    "CO": 900,
    "LO": 700,
    "Module": 800,
    "Topic": 400,
    "Assessment": 700,
}

fig, ax = plt.subplots(1, 1, figsize=(32, 20))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

node_colors = [color_map.get(G.nodes[n].get("type", ""), "#999") for n in G.nodes()]
node_sizes = [size_map.get(G.nodes[n].get("type", ""), 400) for n in G.nodes()]

# Build labels
labels = {}
for n, d in G.nodes(data=True):
    t = d.get("type", "")
    if t == "Course":
        labels[n] = "CSE222"
    elif t in ("CO", "LO"):
        labels[n] = n
    elif t == "Module":
        labels[n] = n
    elif t == "Topic":
        labels[n] = n
    elif t == "Assessment":
        labels[n] = n
    else:
        labels[n] = n

# Separate edges by relation type for different styling
taught_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("relation") == "TAUGHT_IN"]
assessed_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("relation") == "ASSESSED_BY"]
other_edges = [(u, v) for u, v, d in G.edges(data=True) 
               if d.get("relation") not in ("TAUGHT_IN", "ASSESSED_BY")]

# Draw edges with different colors for different relation types
nx.draw_networkx_edges(G, pos, edgelist=other_edges, ax=ax,
                       edge_color="#AAAAAA", arrows=True, arrowsize=10,
                       width=0.8, alpha=0.5, connectionstyle="arc3,rad=0.05")

nx.draw_networkx_edges(G, pos, edgelist=taught_edges, ax=ax,
                       edge_color="#E65100", arrows=True, arrowsize=10,
                       width=0.8, alpha=0.4, style="dashed",
                       connectionstyle="arc3,rad=0.08")

nx.draw_networkx_edges(G, pos, edgelist=assessed_edges, ax=ax,
                       edge_color="#C62828", arrows=True, arrowsize=10,
                       width=0.8, alpha=0.4, style="dotted",
                       connectionstyle="arc3,rad=0.1")

# Draw nodes
nx.draw_networkx_nodes(G, pos, ax=ax,
                       node_color=node_colors,
                       node_size=node_sizes,
                       edgecolors="white",
                       linewidths=1.5)

# Draw labels
nx.draw_networkx_labels(G, pos, labels, ax=ax,
                        font_size=7, font_weight="bold", font_color="white")

# Layer labels on the left side
layer_labels = {
    6: "COURSE",
    5: "OBJECTIVES (CO)",
    4: "LEARNING OUTCOMES (LO)",
    3: "MODULES (Weeks)",
    2: "TOPICS",
    1: "ASSESSMENTS",
}
for y_mult, label in layer_labels.items():
    ax.text(-22, y_mult * 3, label, fontsize=11, fontweight="bold",
            color="#555555", ha="right", va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#F0F0F0", edgecolor="#CCCCCC"))

# Add node detail annotations below each node
for n, d in G.nodes(data=True):
    t = d.get("type", "")
    title = d.get("title", "")
    x, y = pos[n]
    if t == "CO":
        ax.text(x, y - 0.65, title, fontsize=5, ha="center", va="top", color="#333",
                style="italic", wrap=True)
    elif t == "LO":
        bloom = d.get("bloom", "")
        lo_text = f"{title}\n[{bloom}]"
        ax.text(x, y - 0.6, lo_text, fontsize=5, ha="center", va="top", color="#2E7D32",
                style="italic", wrap=True)
    elif t == "Module":
        ax.text(x, y - 0.6, d.get("title", ""), fontsize=5.5, ha="center", va="top", color="#333")
    elif t == "Topic":
        ax.text(x, y - 0.5, title, fontsize=4.5, ha="center", va="top", color="#555", rotation=30)
    elif t == "Assessment":
        ax.text(x, y - 0.6, title, fontsize=5.5, ha="center", va="top", color="#333")

# Legend
legend_handles = [
    mpatches.Patch(color="#1565C0", label="Course"),
    mpatches.Patch(color="#2E7D32", label="Course Objective (CO)"),
    mpatches.Patch(color="#66BB6A", label="Learning Outcome (LO)"),
    mpatches.Patch(color="#E65100", label="Module / Week"),
    mpatches.Patch(color="#FFB74D", label="Topic"),
    mpatches.Patch(color="#C62828", label="Assessment"),
]
ax.legend(handles=legend_handles, loc="upper right", fontsize=10,
          framealpha=0.95, edgecolor="#CCCCCC", title="Node Types", title_fontsize=11)

ax.set_title("ProfsAgent Knowledge Graph — CSE222: Algorithm Design & Analysis\n(Hierarchical Layered View)",
             fontsize=18, fontweight="bold", pad=20)
ax.axis("off")

plt.tight_layout()

output_path = os.path.join(r"C:\Users\amitk\OneDrive\Desktop\ProfsAgent", "cse222_knowledge_graph_layered.png")
plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
print(f"📊 Layered Knowledge Graph saved to: {output_path}")
print("🎉 Done!")
