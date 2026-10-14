"""Agreement statistics for the judge panel (Stage 5) and, later, judges vs professor labels (Stage 6). NO LLM.

  krippendorff_alpha  any number of raters, missing ratings allowed; interval or nominal distance.
                      1 = perfect agreement, 0 = no better than chance, < 0 = systematic disagreement.
                      Common reading: >= 0.8 reliable, 0.667-0.8 tentative, below that do not rely on the scores.
  weighted_kappa      two raters, quadratic weights (a 1 vs 5 disagreement counts far more than 4 vs 5)
  length_bias         Spearman correlation between how long each design is and the score it got: a strong positive
                      value means the judges reward length (verbosity bias)
"""
from __future__ import annotations

import itertools

import numpy as np


def _delta(a: float, b: float, level: str) -> float:
    return float(a != b) if level == "nominal" else (a - b) ** 2


def krippendorff_alpha(ratings: list[list[float | None]], level: str = "interval") -> float | None:
    """ratings[r][u]: rater r's value for unit u, None when missing. Units with fewer than 2 values are not pairable."""
    units = [[x for x in col if x is not None] for col in zip(*ratings)]
    units = [u for u in units if len(u) >= 2]
    values = [x for u in units for x in u]
    n = len(values)
    if n < 2:
        return None
    d_o = sum(sum(_delta(a, b, level) for a, b in itertools.permutations(u, 2)) / (len(u) - 1) for u in units) / n
    d_e = sum(_delta(a, b, level) for a, b in itertools.permutations(values, 2)) / (n * (n - 1))
    if d_e == 0:
        return 1.0 if d_o == 0 else None
    return round(1 - d_o / d_e, 3)


def weighted_kappa(a: list[int], b: list[int], labels=(1, 2, 3, 4, 5)) -> float | None:
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(pairs) < 2:
        return None
    from sklearn.metrics import cohen_kappa_score
    x, y = zip(*pairs)
    if len(set(x) | set(y)) < 2:
        return 1.0 if x == y else None
    k = cohen_kappa_score(x, y, weights="quadratic", labels=list(labels))
    return None if np.isnan(k) else round(float(k), 3)


def length_bias(lengths: list[float], scores: list[float]) -> float | None:
    if len(lengths) < 4 or len(set(lengths)) < 2 or len(set(scores)) < 2:
        return None
    from scipy.stats import spearmanr
    r = spearmanr(lengths, scores).statistic
    return None if np.isnan(r) else round(float(r), 3)


def panel_agreement(scores: dict[str, dict[str, int | None]]) -> dict:
    """scores[judge][dimension] -> alpha over (judges x dimensions) and quadratic-weighted kappa for each judge pair."""
    judges = sorted(scores)
    dims = sorted({d for s in scores.values() for d in s})
    matrix = [[scores[j].get(d) for d in dims] for j in judges]
    pairs = {f"{a}~{b}": weighted_kappa([scores[a].get(d) for d in dims], [scores[b].get(d) for d in dims])
             for a, b in itertools.combinations(judges, 2)}
    return {"judges": judges, "krippendorff_alpha_interval": krippendorff_alpha(matrix) if len(judges) >= 2 else None,
            "weighted_kappa": pairs}
