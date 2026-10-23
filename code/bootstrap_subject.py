"""bootstrap_subject.py — subject-cluster bootstrap + permutation test vs chance.

Fixes two statistical bugs in the old `bootstrap_ci.py`:

1. **Wrong resampling unit.** `bootstrap_ci.py` resamples CLIP indices
   (`np.arange(len(y))`) with replacement. Clips from the same subject are
   correlated and contributed in wildly unequal numbers in this benchmark (one
   test subject can carry hundreds of clips, another a handful) so a clip-level
   bootstrap treats them as independent draws and understates the true CI width
   — it can make a 3-subject test set look as precise as a 300-subject one.
   `subject_cluster_bootstrap` / `paired_subject_bootstrap` here resample
   SUBJECTS (clusters) with replacement instead: each draw picks
   `len(unique_subjects)` subject ids with replacement and pools every clip
   belonging to a drawn subject.

2. **Wrong null for "does signal exist?".** The majority-class baseline is NOT
   a valid null: majority-class prediction has a degenerate macro-F1 (every
   non-majority class scores 0), so a random predictor legitimately beats it.
   Comparing a probe to majority only tells you the probe beats a strawman, not
   that it beats chance. `permutation_test_vs_chance` builds the null by
   permuting the model's OWN predictions across samples (equivalent to a random
   predictor whose output distribution is matched to the model's), and reports
   the fraction of permutations whose macro-F1 matches or exceeds the observed
   one -- the correct one-sided test for "is there recoverable signal".

No RandomForest anywhere in this module -- linear probe only, per the redesign.

With 2-5 test subjects (this benchmark's smallest partitions), a subject
bootstrap draw WILL sometimes collapse to a single subject or a single class.
Metrics are not meaningful there; rather than silently averaging over them (or
crashing), every degenerate draw is recorded as NaN and excluded from the CI,
and the count of degenerate draws is always returned so a suspiciously narrow
CI cannot hide the fact that most of the draws it's based on were nonsense.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Sequence, Tuple, Union

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    cohen_kappa_score,
    f1_score,
)

logger = logging.getLogger(__name__)

ArrayLike = Union[np.ndarray, Sequence[Any]]

_METRIC_FUNCS: Dict[str, Callable[[np.ndarray, np.ndarray], float]] = {
    "macro_f1": lambda yt, yp: f1_score(yt, yp, average="macro", zero_division=0),
    "balanced_accuracy": balanced_accuracy_score,
    "accuracy": accuracy_score,
    "cohen_kappa": cohen_kappa_score,
}


def _metric_fn(name: str) -> Callable[[np.ndarray, np.ndarray], float]:
    try:
        return _METRIC_FUNCS[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown metric '{name}'; choose from {sorted(_METRIC_FUNCS)}"
        ) from exc


def _score(y_true: np.ndarray, y_pred: np.ndarray,
          fn: Callable[[np.ndarray, np.ndarray], float]) -> float:
    """Compute `fn`, returning NaN for a degenerate sample instead of a
    misleading number: macro-F1/kappa/balanced-accuracy are not meaningful
    when the resampled ground truth contains fewer than 2 classes."""
    if len(np.unique(y_true)) < 2:
        return float("nan")
    try:
        return float(fn(y_true, y_pred))
    except Exception:  # noqa: BLE001 — degenerate edge case, not a bug to raise
        logger.debug("metric raised on a degenerate sample; recording NaN", exc_info=True)
        return float("nan")


def _group_indices(subjects: np.ndarray) -> Dict[str, np.ndarray]:
    groups: Dict[str, List[int]] = {}
    for i, s in enumerate(subjects):
        groups.setdefault(s, []).append(i)
    return {s: np.asarray(idx, dtype=int) for s, idx in groups.items()}


def _resample_by_subject(
    groups: Dict[str, np.ndarray], uniq: np.ndarray, rng: np.random.Generator,
) -> Tuple[np.ndarray, int]:
    """Draw len(uniq) subject ids WITH replacement; return the concatenated clip
    indices for the draw and the number of DISTINCT subjects it landed on."""
    drawn = rng.choice(uniq, size=len(uniq), replace=True)
    idx = np.concatenate([groups[s] for s in drawn])
    return idx, len(set(drawn.tolist()))


def _percentiles(ci: float) -> Tuple[float, float]:
    tail = (1.0 - ci) / 2.0
    return tail * 100.0, (1.0 - tail) * 100.0


# ---------------------------------------------------------------------------
# 1. subject-cluster bootstrap CI for a single predictor
# ---------------------------------------------------------------------------

def subject_cluster_bootstrap(
    y_true: ArrayLike,
    y_pred: ArrayLike,
    subjects: ArrayLike,
    metric: str = "macro_f1",
    n: int = 2000,
    seed: int = 0,
    ci: float = 0.95,
) -> Dict[str, Any]:
    """Subject-cluster (block) bootstrap point estimate + CI for `metric`.

    Each of the `n` draws samples len(unique(subjects)) subject ids WITH
    replacement and pools every clip belonging to a drawn subject; `metric` is
    then computed on the pooled clips. This is the correct resampling unit
    when clips from one subject are correlated and unevenly numerous.

    Returns a dict with the point estimate (computed on the full, unresampled
    sample), the percentile CI, and degenerate-draw bookkeeping:
    `n_degenerate` (draws with <2 classes and/or a single distinct subject,
    where `metric` was not computable and NaN was recorded instead),
    `n_valid_draws`, and `ci_width`. Callers MUST check `n_degenerate` /
    `n_valid_draws` before trusting the CI — with very few subjects (this
    benchmark has test partitions as small as 2-5 subjects) most draws can be
    degenerate, and a CI computed from a handful of valid draws is not
    trustworthy even though the code will still return numbers for it.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    subjects = np.asarray([str(s) for s in subjects])
    if not (len(y_true) == len(y_pred) == len(subjects)):
        raise ValueError("y_true, y_pred, subjects must have equal length")
    if len(y_true) == 0:
        raise ValueError("empty input")

    fn = _metric_fn(metric)
    point = _score(y_true, y_pred, fn)

    groups = _group_indices(subjects)
    uniq = np.array(sorted(groups))
    n_subjects = len(uniq)

    rng = np.random.default_rng(seed)
    vals = np.empty(n)
    n_single_subject = 0
    n_single_class = 0
    for b in range(n):
        idx, n_distinct = _resample_by_subject(groups, uniq, rng)
        yt, yp = y_true[idx], y_pred[idx]
        single_subject = n_distinct == 1
        single_class = len(np.unique(yt)) < 2
        if single_subject:
            n_single_subject += 1
        if single_class:
            n_single_class += 1
        # A draw landing on one subject is degenerate even if that subject's own
        # clips happen to span >1 class: it carries zero between-subject
        # variance, so it cannot stand in for the quantity this bootstrap is
        # meant to estimate (uncertainty ACROSS subjects), and is forced to NaN
        # rather than silently accepted as a valid draw.
        vals[b] = float("nan") if (single_subject or single_class) else _score(yt, yp, fn)

    degenerate = np.isnan(vals)
    valid = vals[~degenerate]
    lo_pct, hi_pct = _percentiles(ci)
    if len(valid) == 0:
        ci_lo = ci_hi = float("nan")
    else:
        ci_lo, ci_hi = float(np.percentile(valid, lo_pct)), float(np.percentile(valid, hi_pct))

    return {
        "metric": metric,
        "point_estimate": point,
        "n_subjects": n_subjects,
        "n_clips": int(len(y_true)),
        "n_draws": n,
        "n_degenerate": int(degenerate.sum()),
        "n_degenerate_single_subject": n_single_subject,
        "n_degenerate_single_class": n_single_class,
        "n_valid_draws": int(len(valid)),
        "ci_level": ci,
        "ci_lo": ci_lo,
        "ci_hi": ci_hi,
        "ci_width": float(ci_hi - ci_lo) if len(valid) else float("nan"),
    }


# ---------------------------------------------------------------------------
# 2. paired subject-cluster bootstrap for a difference between two predictors
# ---------------------------------------------------------------------------

def paired_subject_bootstrap(
    y_true: ArrayLike,
    pred_a: ArrayLike,
    pred_b: ArrayLike,
    subjects: ArrayLike,
    metric: str = "macro_f1",
    n: int = 2000,
    seed: int = 0,
    ci: float = 0.95,
) -> Dict[str, Any]:
    """Paired subject-cluster bootstrap for metric(pred_a) - metric(pred_b).

    The SAME subject resample is applied to both predictors on every draw
    (paired), so the CI/p-value isolate the difference instead of compounding
    two independently-resampled distributions' variance. p-value is the
    two-sided bootstrap p-value, 2*min(P(diff>0), P(diff<0)), computed over
    non-degenerate draws only.
    """
    y_true = np.asarray(y_true)
    pred_a = np.asarray(pred_a)
    pred_b = np.asarray(pred_b)
    subjects = np.asarray([str(s) for s in subjects])
    if not (len(y_true) == len(pred_a) == len(pred_b) == len(subjects)):
        raise ValueError("y_true, pred_a, pred_b, subjects must have equal length")
    if len(y_true) == 0:
        raise ValueError("empty input")

    fn = _metric_fn(metric)
    point = _score(y_true, pred_a, fn) - _score(y_true, pred_b, fn)

    groups = _group_indices(subjects)
    uniq = np.array(sorted(groups))

    rng = np.random.default_rng(seed)
    diffs = np.empty(n)
    n_single_subject = 0
    n_single_class = 0
    for b in range(n):
        idx, n_distinct = _resample_by_subject(groups, uniq, rng)
        yt = y_true[idx]
        single_subject = n_distinct == 1
        single_class = len(np.unique(yt)) < 2
        if single_subject:
            n_single_subject += 1
        if single_class:
            n_single_class += 1
        # See subject_cluster_bootstrap: a single-subject draw is forced
        # degenerate regardless of that subject's own class diversity.
        if single_subject or single_class:
            diffs[b] = float("nan")
        else:
            diffs[b] = _score(yt, pred_a[idx], fn) - _score(yt, pred_b[idx], fn)

    degenerate = np.isnan(diffs)
    valid = diffs[~degenerate]
    lo_pct, hi_pct = _percentiles(ci)
    if len(valid) == 0:
        ci_lo = ci_hi = p_value = float("nan")
    else:
        ci_lo, ci_hi = float(np.percentile(valid, lo_pct)), float(np.percentile(valid, hi_pct))
        # P(diff>=0)/P(diff<=0), not P(diff>0)/1-P(diff>0): the latter mishandles
        # an atom of exact ties at 0 (e.g. comparing a predictor to itself would
        # otherwise report p=0 instead of the correct p=1). Add-one smoothed so
        # p is never reported as exactly 0 from a finite number of draws.
        n_valid = len(valid)
        p_ge = float((1 + np.sum(valid >= 0)) / (n_valid + 1))
        p_le = float((1 + np.sum(valid <= 0)) / (n_valid + 1))
        p_value = float(min(2 * min(p_ge, p_le), 1.0))

    return {
        "metric": metric,
        "delta": point,
        "ci_level": ci,
        "ci_lo": ci_lo,
        "ci_hi": ci_hi,
        "p_value": p_value,
        "n_draws": n,
        "n_degenerate": int(degenerate.sum()),
        "n_degenerate_single_subject": n_single_subject,
        "n_degenerate_single_class": n_single_class,
        "n_valid_draws": int(len(valid)),
    }


# ---------------------------------------------------------------------------
# 3. permutation test vs chance (the "is signal present?" test)
# ---------------------------------------------------------------------------

def permutation_test_vs_chance(
    y_true: ArrayLike,
    y_pred: ArrayLike,
    metric: str = "macro_f1",
    n: int = 5000,
    seed: int = 0,
) -> Dict[str, Any]:
    """One-sided permutation test: is `y_pred` better than a random predictor
    matched to its OWN output class distribution?

    The null is built by permuting `y_pred` across samples `n` times (each
    permutation is exactly a random predictor with the same marginal class
    distribution the model actually produced) and recomputing `metric` against
    the fixed `y_true` each time. This is the correct null for "does
    recoverable signal exist" -- unlike the majority baseline, which has a
    degenerate macro-F1 that a random predictor legitimately beats, so
    comparing against it does not test for signal.

    p-value = (1 + #{null >= observed}) / (1 + #{valid permutations}), i.e.
    the one-sided fraction of the null distribution at or above the observed
    score (add-one smoothed so p is never reported as exactly 0).
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have equal length")

    fn = _metric_fn(metric)
    observed = _score(y_true, y_pred, fn)

    rng = np.random.default_rng(seed)
    null_vals = np.empty(n)
    for b in range(n):
        perm = rng.permutation(y_pred)
        null_vals[b] = _score(y_true, perm, fn)

    degenerate = np.isnan(null_vals)
    valid = null_vals[~degenerate]
    if len(valid) == 0:
        return {
            "metric": metric,
            "observed": observed,
            "null_mean": float("nan"),
            "null_sd": float("nan"),
            "p_value": float("nan"),
            "n_permutations": n,
            "n_degenerate": int(degenerate.sum()),
            "n_valid_permutations": 0,
        }

    p_value = float((1 + np.sum(valid >= observed)) / (len(valid) + 1))
    return {
        "metric": metric,
        "observed": observed,
        "null_mean": float(np.mean(valid)),
        "null_sd": float(np.std(valid)),
        "null_p95": float(np.percentile(valid, 95)),
        "p_value": p_value,
        "n_permutations": n,
        "n_degenerate": int(degenerate.sum()),
        "n_valid_permutations": int(len(valid)),
    }
