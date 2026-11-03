"""Topic -> simulation type classifier and the coverage report (docs/09_phase2_A_simulation_catalogue.md §6.3).

Every weekly topic of every IIIT-D course (data/enriched) is compared with the 12 types' descriptions and examples
(simulations/types.yaml) and with examples of topics better taught another way ("none"), using the local embedding
model the knowledge graph already uses (all-MiniLM-L6-v2, CPU; no AI calls). A topic gets the type it is closest to,
or "none" when nothing is close enough. The two settings (how close is close enough, and how much closer "none" may
be) are calibrated on hand-labelled topics (simulations/classifier/labels.tsv); accuracy is reported with 5-fold
cross-validation so the calibration does not flatter itself.

    python scripts/sims.py coverage      -> simulations/coverage.md (+ every topic's type in simulations/_build/coverage_topics.csv)
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from profsagent.config import CACHE, DATA
from profsagent.sims.catalogue import BUILD, SIMS, types

MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMB = CACHE / "emb_local" / "sims_topics.npz"
LABELS = SIMS / "classifier" / "labels.tsv"
PARAMS = SIMS / "classifier" / "params.json"
REPORT = SIMS / "coverage.md"
NONE = "none"


def course_topics() -> list[dict]:
    out = []
    for f in sorted((DATA / "enriched").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        h = d["header"]
        code = re.sub(r"\s+", "", (h.get("course_code") or "")).upper()
        m = re.match(r"[A-Z]+", code)
        for w in d.get("weekly_plan") or []:
            for t in w.get("lecture_topics") or []:
                t = re.sub(r"\s+", " ", (t or "")).strip()
                if len(t) >= 3:
                    out.append({"dept": m.group(0) if m else "?", "code": code, "course": h.get("name") or "", "topic": t})
    return out


_model = None


def embed(texts: list[str]) -> np.ndarray:
    """Unit vectors, cached on disk by text (data/cache is not committed)."""
    global _model
    keys = [hashlib.sha1(t.encode("utf-8")).hexdigest()[:16] for t in texts]
    cache: dict[str, np.ndarray] = {}
    if EMB.exists():
        z = np.load(EMB, allow_pickle=False)
        cache = dict(zip(z["keys"].tolist(), z["vecs"]))
    todo = [i for i, k in enumerate(keys) if k not in cache]
    if todo:
        if _model is None:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(MODEL, device="cpu")
        vecs = _model.encode([texts[i] for i in todo], batch_size=128, normalize_embeddings=True, show_progress_bar=False)
        for i, v in zip(todo, vecs):
            cache[keys[i]] = v.astype(np.float32)
        EMB.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(EMB, keys=np.array(list(cache)), vecs=np.stack(list(cache.values())))
    return np.stack([cache[k] for k in keys])


def text_of(t: dict, with_course: bool) -> str:
    return f"{t['topic']} ({t['course']})" if with_course and t.get("course") else t["topic"]


class Classifier:
    def __init__(self, threshold: float = 0.35, margin: float = 0.0, topk: int = 2):
        ty = types()
        self.ids = [t["id"] for t in ty["types"]]
        protos, owner = [], []
        for i, t in enumerate(ty["types"]):
            for p in [f"{t['name']}: {t['does']}"] + list(t["examples"]):
                protos.append(p)
                owner.append(i)
        for p in ty["none_examples"]:
            protos.append(p)
            owner.append(len(self.ids))
        self.P, self.owner = embed(protos), np.array(owner)
        self.threshold, self.margin, self.topk = threshold, margin, topk

    def scores(self, X: np.ndarray) -> np.ndarray:
        """n x 13: per type (and "none" last), the mean of the topk closest prototypes."""
        S = X @ self.P.T
        out = np.zeros((len(X), len(self.ids) + 1), np.float32)
        for c in range(len(self.ids) + 1):
            cols = S[:, self.owner == c]
            k = min(self.topk, cols.shape[1])
            out[:, c] = np.sort(cols, axis=1)[:, -k:].mean(axis=1)
        return out

    def decide(self, sc: np.ndarray) -> list[tuple[str, float, str | None]]:
        res = []
        for row in sc:
            types_ = row[:-1]
            b = int(types_.argmax())
            second = int(np.argsort(types_)[-2])
            if types_[b] < self.threshold or row[-1] - types_[b] > self.margin:
                res.append((NONE, float(types_[b]), self.ids[b]))
            else:
                res.append((self.ids[b], float(types_[b]), self.ids[second] if types_[b] - types_[second] < 0.03 else None))
        return res


def read_labels() -> list[dict]:
    rows = []
    for line in LABELS.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or line.startswith("dept\t"):
            continue
        dept, code, topic, acc = line.split("\t")
        ok = {NONE if a == "0" else next(i for i in types_ids() if i.startswith(a + "-")) for a in acc.split("|")}
        rows.append({"dept": dept, "code": code, "topic": topic, "course": _course_names().get(code, ""), "ok": ok})
    return rows


def types_ids() -> list[str]:
    return [t["id"] for t in types()["types"]]


_names: dict | None = None


def _course_names() -> dict:
    global _names
    if _names is None:
        _names = {}
        for f in (DATA / "enriched").glob("*.json"):
            h = json.loads(f.read_text(encoding="utf-8"))["header"]
            _names[re.sub(r"\s+", "", (h.get("course_code") or "")).upper()] = h.get("name") or ""
    return _names


def accuracy(pred: list, rows: list[dict]) -> float:
    return sum(p[0] in r["ok"] for p, r in zip(pred, rows)) / max(1, len(rows))


GRID = [(th, mg) for th in np.arange(0.20, 0.56, 0.01) for mg in np.arange(-0.10, 0.16, 0.01)]


def calibrate(rows: list[dict], with_course: bool, topk: int) -> tuple[float, float, float]:
    clf = Classifier(topk=topk)
    sc = clf.scores(embed([text_of(r, with_course) for r in rows]))
    best = (0.0, 0.35, 0.0)
    for th, mg in GRID:
        clf.threshold, clf.margin = float(th), float(mg)
        a = accuracy(clf.decide(sc), rows)
        if a > best[0] + 1e-9:
            best = (a, float(th), float(mg))
    return best


def cross_validate(rows: list[dict], with_course: bool, topk: int, folds: int = 5) -> float:
    """Calibrate on 4/5 of the labels, score on the other 1/5; the mean is an honest accuracy estimate."""
    idx = np.random.RandomState(7).permutation(len(rows))
    clf = Classifier(topk=topk)
    sc_all = clf.scores(embed([text_of(r, with_course) for r in rows]))
    hits = 0
    for f in range(folds):
        test = set(idx[f::folds].tolist())
        train = [i for i in range(len(rows)) if i not in test]
        best = (-1.0, 0.35, 0.0)
        for th, mg in GRID:
            clf.threshold, clf.margin = float(th), float(mg)
            a = accuracy(clf.decide(sc_all[train]), [rows[i] for i in train])
            if a > best[0] + 1e-9:
                best = (a, float(th), float(mg))
        clf.threshold, clf.margin = best[1], best[2]
        tl = sorted(test)
        hits += sum(p[0] in rows[i]["ok"] for p, i in zip(clf.decide(sc_all[tl]), tl))
    return hits / len(rows)


def main(args: list[str]) -> int:
    rows = read_labels()
    variants = []
    for with_course in (False, True):
        for topk in (1, 2, 3):
            cv = cross_validate(rows, with_course, topk)
            variants.append((cv, with_course, topk))
            print(f"  variant: course name {'on ' if with_course else 'off'} · top-{topk} prototypes → cross-validated accuracy {cv:.0%}")
    cv, with_course, topk = max(variants)
    acc, th, mg = calibrate(rows, with_course, topk)
    PARAMS.write_text(json.dumps({"with_course": with_course, "topk": topk, "threshold": round(th, 3), "margin": round(mg, 3),
                                  "accuracy_on_labels": round(acc, 3), "cross_validated_accuracy": round(cv, 3), "labels": len(rows),
                                  "model": MODEL}, indent=1), encoding="utf-8")
    clf = Classifier(th, mg, topk)
    lab_pred = clf.decide(clf.scores(embed([text_of(r, with_course) for r in rows])))
    none_rows = [r for r in rows if r["ok"] == {NONE}]
    sim_rows = [r for r in rows if NONE not in r["ok"]]
    p_none = [p for p, r in zip(lab_pred, rows) if r["ok"] == {NONE}]
    p_sim = [p for p, r in zip(lab_pred, rows) if NONE not in r["ok"]]
    print(f"chosen: course name {'on' if with_course else 'off'}, top-{topk}, threshold {th:.2f}, margin {mg:+.2f}: "
          f"accuracy {acc:.0%} on the {len(rows)} labels, {cv:.0%} cross-validated")

    topics = course_topics()
    preds = clf.decide(clf.scores(embed([text_of(t, with_course) for t in topics])))
    BUILD.mkdir(parents=True, exist_ok=True)
    with (BUILD / "coverage_topics.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["dept", "course", "topic", "type", "score", "also"])
        for t, p in zip(topics, preds):
            w.writerow([t["dept"], t["code"], t["topic"], p[0], f"{p[1]:.3f}", p[2] or ""])
    by = defaultdict(list)
    for t, p in zip(topics, preds):
        by[t["dept"]].append(p[0])
    names = {t["id"]: t["name"] for t in types()["types"]}
    short = {i: i.split("-")[0] for i in types_ids()}
    L = ["# Simulation coverage of IIIT-D's courses (generated)", "",
         f"Made by `python scripts/sims.py coverage`: every weekly topic of the {len({t['code'] for t in topics})} courses in our course data "
         f"({len(topics):,} topic lines) labelled with a simulation type (docs/09 §3) or \"none\" (better taught another way).",
         "", "**How far to trust it:**",
         f"- **Model:** {MODEL} on the CPU, with no AI calls. Settings: course name {'used' if with_course else 'not used'}, "
         f"top-{topk} prototypes, threshold {th:.2f}, margin {mg:+.2f}.",
         f"- **Accuracy:** checked against {len(rows)} hand-labelled topics (`simulations/classifier/labels.tsv`, labelled by Claude, to be reviewed by Amit). "
         f"It was right on **{acc:.0%}** of them, and **{cv:.0%} cross-validated** (calibrated on 4/5 of the labels, scored on the rest).",
         f"- **Topics that should get no simulation:** it said \"none\" for {sum(p[0] == NONE for p in p_none)} of {len(none_rows)}.",
         f"- **Topics that should get a simulation:** it gave one that fits for {sum(p[0] in r['ok'] for p, r in zip(p_sim, sim_rows))} of {len(sim_rows)}.",
         "- **Use:** treat the shares below as estimates that rank the work, not exact counts.", "",
         "## Per department", "",
         "| Department | Topics | With a simulation type | Most common types (share of the department's topics) |", "|---|---|---|---|"]
    tot_n = tot_s = 0
    for dep, ps in sorted(by.items(), key=lambda kv: -len(kv[1])):
        c = Counter(ps)
        n, s = len(ps), len(ps) - c[NONE]
        tot_n, tot_s = tot_n + n, tot_s + s
        top = ", ".join(f"{short[k]} {names[k].split(',')[0].split(' and ')[0].lower()} {100 * v / n:.0f}%" for k, v in c.most_common() if k != NONE)
        L.append(f"| {dep} | {n} | {100 * s / n:.0f}% | {top} |")
    L.append(f"| **All** | **{tot_n}** | **{100 * tot_s / tot_n:.0f}%** | |")
    allc = Counter(p[0] for p in preds)
    L += ["", "## Per type, all departments", "", "| Type | Topics | Example topics |", "|---|---|---|"]
    ex = defaultdict(list)
    for t, p in zip(topics, preds):
        if len(ex[p[0]]) < 4 and t["topic"] not in ex[p[0]] and len(t["topic"]) < 70:
            ex[p[0]].append(f"{t['topic']} ({t['code']})")
    for i in types_ids() + [NONE]:
        L.append(f"| {names.get(i, 'none: better taught another way')} | {allc[i]} | {'; '.join(ex[i])} |")
    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"report: {REPORT.relative_to(SIMS.parent)} · every topic: simulations/_build/coverage_topics.csv · "
          f"{100 * tot_s / tot_n:.0f}% of {tot_n:,} topics get a simulation type")
    return 0
