#!/usr/bin/env python3
"""GaitEval v2.1 reference suite (local CPU) — Phase 1 of the 6-dataset campaign.

Per dataset (from the v2.1 contract's 03_features_raw_and_z.csv):
  majority + simulated stratified-chance macro-F1, LR/SVM (balanced + None), RF,
  subject-cluster bootstrap CIs, permutation-vs-chance for LR, and LOSO for
  small-subject datasets. Labeled samples only (label_task-eligible).

Design notes carried from R1/R2 reviews: subject is the resampling unit from
day one; vff/frame-length are absent from the feature set by construction
(v2.1 data standard); chance null reported alongside majority.
"""
import argparse
import csv
import json
import os
import sys

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from bootstrap_subject import subject_cluster_bootstrap, permutation_test_vs_chance  # noqa: E402


def log(*a):
    print(*a, flush=True)


def load_dataset(root):
    path = os.path.join(root, "03_features_raw_and_z.csv")
    if not os.path.exists(path):
        path = os.path.join(root, "modalities", "03_features_raw_and_z.csv")
    dataset = os.path.basename(os.path.normpath(root))
    contract = json.load(open(os.path.join(os.path.dirname(__file__), "..", "datasets.json")))["datasets"]
    allowed = next(d["label_set"] for d in contract if d["id"] == dataset)
    with open(path) as fh:
        rd = csv.reader(fh)
        hdr = next(rd)
        rows = list(rd)
    idx = {h: i for i, h in enumerate(hdr)}
    feat_cols = [i for i, h in enumerate(hdr) if h.startswith("raw__")]
    if not feat_cols:raise ValueError("No raw feature columns")
    if any(any(q in hdr[i] for q in ["valid_frame", "clip_length", "frame_count"]) for i in feat_cols):
        raise ValueError("Capture-quality feature in S inputs")
    need = ["label", "split", "subject_id", "sample_id"]
    for n in need:
        if n not in idx:
            raise RuntimeError(f"{root}: missing column {n}; header={hdr[:10]}...")
    X, y, split, subj, sid = [], [], [], [], []
    for r in rows:
        lab = r[idx["label"]]
        if lab not in allowed:
            continue  # unlabeled samples excluded from supervised suite
        X.append([float(r[i]) if r[i] not in ("", "nan", "None", "null") else np.nan
                  for i in feat_cols])
        y.append(lab)
        split.append(r[idx["split"]])
        subj.append(str(r[idx["subject_id"]]))
        sid.append(r[idx["sample_id"]])
    labels = sorted(allowed)
    lmap = {l: i for i, l in enumerate(labels)}
    return (np.array(X), np.array([lmap[v] for v in y]), np.array(split),
            np.array(subj), labels, [hdr[i] for i in feat_cols])


def chance_mf1(y_te, n_sim=2000, seed=0):
    rng = np.random.default_rng(seed)
    p = np.bincount(y_te) / len(y_te)
    vals = [f1_score(y_te, rng.choice(len(p), size=len(y_te), p=p),
                     average="macro", zero_division=0) for _ in range(n_sim)]
    return float(np.mean(vals)), float(np.std(vals))


def metrics(y, p):
    return {"acc": round(float(accuracy_score(y, p)), 4),
            "mf1": round(float(f1_score(y, p, average="macro", zero_division=0)), 4),
            "kappa": round(float(cohen_kappa_score(y, p)), 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="extracted/ dir containing dataset subdirs")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--out", default="v2_reference_suite.json")
    ap.add_argument("--loso-max-subjects", type=int, default=110)
    args = ap.parse_args()
    from pathlib import Path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
    from validate_inputs import validate
    validate(Path(args.root))

    ds_dirs = args.datasets or sorted(
        d for d in os.listdir(args.root) if os.path.isdir(os.path.join(args.root, d)))
    out = {}
    for ds in ds_dirs:
        root = os.path.join(args.root, ds)
        try:
            X, y, split, subj, labels, fnames = load_dataset(root)
        except Exception as e:
            raise RuntimeError(f"{ds}: {e}") from e
        tr, te = split == "train", split == "test"
        if te.sum() == 0 or tr.sum() == 0 or len(labels) < 2:
            log(f"[skip] {ds}: degenerate split/labels")
            continue
        # subject-disjoint sanity
        overlap = set(subj[tr]) & set(subj[te])
        if overlap:raise ValueError(f"{ds}: training/test participant overlap")
        rec = {"n_train": int(tr.sum()), "n_test": int(te.sum()),
               "n_features": len(fnames), "labels": labels,
               "n_subj_test": int(len(set(subj[te]))),
               "train_test_subject_overlap": sorted(overlap)}
        keep = ~np.all(np.isnan(X[tr]), axis=0)  # drop features the layout cannot support (v1 protocol)
        X = X[:, keep]
        rec["n_features"] = int(keep.sum())
        Xtr, Xte, ytr, yte = X[tr], X[te], y[tr], y[te]
        maj = int(np.bincount(ytr).argmax())
        rec["majority"] = metrics(yte, np.full_like(yte, maj))
        cm, cs = chance_mf1(yte)
        rec["chance_mf1"] = {"mean": round(cm, 4), "std": round(cs, 4)}
        models = {
            "lr_balanced": LogisticRegression(max_iter=2000, class_weight="balanced"),
            "svm_balanced": LinearSVC(class_weight="balanced", max_iter=5000),
            "lr_none": LogisticRegression(max_iter=2000),
            "svm_none": LinearSVC(max_iter=5000),
            "rf": RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                         random_state=0, n_jobs=-1),
        }
        preds = {}
        for name, mdl in models.items():
            pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), mdl)
            pipe.fit(Xtr, ytr)
            p = pipe.predict(Xte)
            preds[name] = p
            m = metrics(yte, p)
            bt = subject_cluster_bootstrap(yte, p, subj[te], metric="macro_f1",
                                           n=2000, seed=0)
            m["subj_ci"] = [round(float(bt["ci_lo"]), 4), round(float(bt["ci_hi"]), 4)]
            rec[name] = m
        pt = permutation_test_vs_chance(yte, preds["lr_balanced"],
                                        metric="macro_f1", n=2000, seed=0)
        rec["lr_perm_p"] = round(float(pt["p_value"]), 4)
        # LOSO over the pooled labeled samples for small-subject datasets
        uniq = sorted(set(subj))
        if len(uniq) <= args.loso_max_subjects:
            lp = np.empty_like(y)
            for s in uniq:
                m_ = subj == s
                pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                     LogisticRegression(max_iter=2000, class_weight="balanced"))
                if len(set(y[~m_])) < 2:
                    lp[m_] = -1
                    continue
                pipe.fit(X[~m_], y[~m_])
                lp[m_] = pipe.predict(X[m_])
            ok = lp >= 0
            bt = subject_cluster_bootstrap(y[ok], lp[ok], subj[ok],
                                           metric="macro_f1", n=2000, seed=0)
            rec["loso_lr"] = {**metrics(y[ok], lp[ok]),
                              "subj_ci": [round(float(bt["ci_lo"]), 4),
                                          round(float(bt["ci_hi"]), 4)],
                              "n_subjects": len(uniq)}
        out[ds] = rec
        log(f"[ds] {ds}: n_te={rec['n_test']} subj_te={rec['n_subj_test']} "
            f"overlap={len(overlap)} maj={rec['majority']['mf1']} chance={cm:.3f} "
            f"LR={rec['lr_balanced']['mf1']} CI={rec['lr_balanced']['subj_ci']} "
            f"SVM={rec['svm_balanced']['mf1']} RF={rec['rf']['mf1']} "
            f"permp={rec['lr_perm_p']}"
            + (f" LOSO={rec['loso_lr']['mf1']}" if "loso_lr" in rec else ""))
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
    log(f"[done] wrote {args.out}")


if __name__ == "__main__":
    main()
