"""DBSCAN written out step by step for the Manim video (dbscan_scene.py), and its check against scikit-learn.

Definitions (Ester et al., 1996), with minPts counting the point itself, as scikit-learn's min_samples does:
  core point    at least minPts points within distance eps
  border point  not core, but within eps of a core point; it joins that core point's cluster
  noise         neither
The video only draws what run() records; check() compares the result with sklearn.cluster.DBSCAN.
"""
from __future__ import annotations

import numpy as np

NOISE, UNSEEN = -1, -2


def dataset(seed: int) -> np.ndarray:
    """Three groups of different shapes plus scattered points, in screen-sized units (about 8 x 5.6)."""
    r = np.random.RandomState(seed)
    a = r.normal([-2.6, 1.4], [0.42, 0.36], size=(13, 2))                       # round blob
    t = np.linspace(0.15 * np.pi, 0.95 * np.pi, 14)
    b = np.c_[1.2 + 1.55 * np.cos(t), -1.35 + 1.55 * np.sin(t)] + r.normal(0, 0.11, (14, 2))   # arc
    c = np.c_[r.uniform(-3.6, -1.4, 11), r.normal(-1.75, 0.2, 11)]               # elongated strip
    noise = r.uniform([-3.9, -2.6], [3.6, 2.6], size=(7, 2))
    return np.round(spread(np.vstack([a, b, c, noise])), 3)


def spread(P: np.ndarray, dmin: float = 0.22, rounds: int = 200) -> np.ndarray:
    """Push apart any two points closer than dmin (so every dot is visible on screen), a little at a time."""
    P = P.copy()
    for _ in range(rounds):
        d = P[:, None, :] - P[None, :, :]
        dist = np.linalg.norm(d, axis=2) + np.eye(len(P)) * 9
        i, j = np.nonzero(np.triu(dist < dmin))
        if not len(i):
            break
        for a, b in zip(i, j):
            v = P[a] - P[b]
            n = np.linalg.norm(v) or 1e-6
            push = (dmin - n) / 2 + 1e-3
            P[a] += v / n * push
            P[b] -= v / n * push
    return P


def run(P: np.ndarray, eps: float, min_pts: int, order: list[int]) -> dict:
    """DBSCAN in the given visiting order. Returns labels, core flags, neighbour lists and the event list:
       ("noise", i)                         visited, not core, not yet reachable -> marked noise (for now)
       ("seed", i, c)                       visited core point starts cluster c
       ("wave", c, [(j, kind, from_noise)])  the next ring of points reached from cluster c (kind core|border)"""
    n = len(P)
    D = np.linalg.norm(P[:, None, :] - P[None, :, :], axis=2)
    nbrs = [np.flatnonzero(D[i] <= eps).tolist() for i in range(n)]
    core = [len(nb) >= min_pts for nb in nbrs]
    labels = [UNSEEN] * n
    events, c = [], -1
    for i in order:
        if labels[i] != UNSEEN:
            continue
        if not core[i]:
            labels[i] = NOISE
            events.append(("noise", i))
            continue
        c += 1
        labels[i] = c
        events.append(("seed", i, c))
        frontier = [i]
        while frontier:                                   # breadth-first: each wave is one ring of reachability
            wave, nxt = [], []
            for p in frontier:
                for j in nbrs[p]:
                    if labels[j] == NOISE:                # was marked noise earlier, but a core point reaches it
                        labels[j] = c
                        wave.append((j, "border", True))
                    elif labels[j] == UNSEEN:
                        labels[j] = c
                        wave.append((j, "core" if core[j] else "border", False))
                        if core[j]:
                            nxt.append(j)
            if wave:
                events.append(("wave", c, wave))
            frontier = nxt
    return {"labels": labels, "core": core, "nbrs": nbrs, "events": events, "n_clusters": c + 1, "D": D}


def check(P: np.ndarray, eps: float, min_pts: int, res: dict) -> dict:
    """Compare with scikit-learn's DBSCAN: the same core points, the same noise, the same grouping of core points,
    and every border point within eps of a core point of its own cluster (a border point that two clusters reach may
    legitimately go to either, depending on visiting order)."""
    from sklearn.cluster import DBSCAN
    sk = DBSCAN(eps=eps, min_samples=min_pts).fit(P)
    ours, theirs = np.array(res["labels"]), sk.labels_
    core_ours = {i for i, c in enumerate(res["core"]) if c}
    core_sk = set(sk.core_sample_indices_.tolist())
    mapping = {}
    for i in core_ours:
        mapping.setdefault(ours[i], set()).add(theirs[i])
    one_to_one = all(len(v) == 1 for v in mapping.values()) and len({next(iter(v)) for v in mapping.values()}) == len(mapping)
    borders = [i for i in range(len(P)) if ours[i] >= 0 and not res["core"][i]]
    border_ok = all(any(res["D"][i, j] <= eps and res["core"][j] and ours[j] == ours[i] for j in range(len(P))) for i in borders)
    same_border = sum(1 for i in borders if next(iter(mapping[ours[i]])) == theirs[i])
    out = {"points": int(len(P)), "eps": eps, "minPts": min_pts, "clusters_ours": res["n_clusters"],
           "clusters_sklearn": int(len(set(theirs) - {-1})), "core_points_same": core_ours == core_sk,
           "noise_same": set(np.flatnonzero(ours == NOISE).tolist()) == set(np.flatnonzero(theirs == -1).tolist()),
           "core_grouping_same": one_to_one, "border_points": len(borders), "border_points_valid": border_ok,
           "border_points_same_cluster_as_sklearn": same_border}
    out["passed"] = bool(out["core_points_same"] and out["noise_same"] and out["core_grouping_same"] and border_ok
                         and out["clusters_ours"] == out["clusters_sklearn"])
    return out


if __name__ == "__main__":       # pick a dataset that shows every case clearly
    eps, mp = 0.62, 4
    for seed in range(400):
        P = dataset(seed)
        D = np.linalg.norm(P[:, None] - P[None], axis=2) + np.eye(len(P)) * 9
        order = np.random.RandomState(seed + 1000).permutation(len(P)).tolist()
        r = run(P, eps, mp, order)
        ev = r["events"]
        relabel = sum(1 for e in ev if e[0] == "wave" for (_, _, fn) in e[2] if fn)
        noise = sum(1 for x in r["labels"] if x == NOISE)
        border = sum(1 for i, x in enumerate(r["labels"]) if x >= 0 and not r["core"][i])
        sizes = sorted(np.bincount([x for x in r["labels"] if x >= 0]).tolist()) if r["n_clusters"] else []
        if r["n_clusters"] == 3 and 4 <= noise <= 7 and border >= 4 and relabel >= 1 and min(sizes) >= 9 and ev[0][0] == "noise" and D.min() >= 0.2:
            ck = check(P, eps, mp, r)
            if ck["passed"]:
                print("seed", seed, "noise", noise, "border", border, "relabel", relabel, "sizes", sizes, "events", len(ev))
                break
