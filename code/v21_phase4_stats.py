#!/usr/bin/env python3
"""GaitEval v2.1 Phase 4 — subject-level statistics over all Phase-2/3 LLM cells.

Per cell: point metrics from the runner's summary.json (fixed-K macro-F1),
subject-cluster bootstrap CI, permutation-vs-chance p.
Per dataset: paired subject bootstrap contrasts against the 7B zero-shot cell
(zs - noev, zs - shufev, zs - feat, zs - lorder-*, sft - zs when present).

Unparsed predictions map to an "UNPARSED" sentinel class inside the bootstrap
(same convention as the v1 R2 recompute), so bootstrap point deltas can differ
slightly from fixed-K summary numbers; both are recorded.

Also emits V21_RESULTS.md: master table merging the Phase-1 reference suite.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bootstrap_subject import (  # noqa: E402
    paired_subject_bootstrap,
    permutation_test_vs_chance,
    subject_cluster_bootstrap,
)

SENT = "UNPARSED"
CONTRASTS = [("zs", "noev"), ("zs", "shufev"), ("zs", "feat"),
             ("zs", "lorder-rev"), ("zs", "lorder-shuf1"), ("sft", "zs")]
DS_ORDER = ["ataxia", "gmfcs", "parkinsonism", "pathogait", "asd_kinect", "care_pd"]
COND_ORDER = ["zs", "feat", "sft", "lorder-rev", "lorder-shuf1", "shufev", "noev", "zs_mixed"]


def load_cell(run_dir):
    rows = [json.loads(l) for l in open(os.path.join(run_dir, "results.jsonl"))]
    summ = json.load(open(os.path.join(run_dir, "summary.json")))
    y = [r["true"] for r in rows]
    p = [r["pred"] if r["pred"] is not None else SENT for r in rows]
    s = [str(r["subject_id"]) for r in rows]
    ids = [r["sample_id"] for r in rows]
    return {"rows": dict(zip(ids, zip(y, p, s))), "y": y, "p": p, "subj": s,
            "ids": ids, "summary": summ}


def r4(x):
    return None if x is None else round(float(x), 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="new_data/v21_runs")
    ap.add_argument("--ref", default="new_data/v2_reference_suite.json")
    ap.add_argument("--out", default="new_data/v21_phase4_stats.json")
    ap.add_argument("--md", default="new_data/V21_RESULTS.md")
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()

    cells = {}
    for d in sorted(os.listdir(args.runs)):
        run_dir = os.path.join(args.runs, d)
        if not os.path.isfile(os.path.join(run_dir, "summary.json")):
            continue
        ds, cond = d.split("__", 1)
        cells[(ds, cond)] = load_cell(run_dir)

    out = {"cells": {}, "contrasts": {}}
    for (ds, cond), c in sorted(cells.items()):
        bt = subject_cluster_bootstrap(c["y"], c["p"], c["subj"],
                                       metric="macro_f1", n=args.n_boot, seed=0)
        pt = permutation_test_vs_chance(c["y"], c["p"], metric="macro_f1",
                                        n=args.n_boot, seed=0)
        out["cells"][f"{ds}__{cond}"] = {
            "n": c["summary"]["n"], "n_unparsed": c["summary"]["n_unparsed"],
            "acc": c["summary"]["accuracy"], "macro_f1": c["summary"]["macro_f1"],
            "n_subj": len(set(c["subj"])),
            "mf1_subj_ci": [r4(bt["ci_lo"]), r4(bt["ci_hi"])],
            "perm_p_vs_chance": r4(pt["p_value"]),
        }
        print(f"[cell] {ds}/{cond}: mf1={c['summary']['macro_f1']} "
              f"CI=[{r4(bt['ci_lo'])},{r4(bt['ci_hi'])}] permp={r4(pt['p_value'])}",
              flush=True)

    for ds in sorted({d for d, _ in cells}):
        for ca, cb in CONTRASTS:
            if (ds, ca) not in cells or (ds, cb) not in cells:
                continue
            A, B = cells[(ds, ca)], cells[(ds, cb)]
            common = [i for i in A["ids"] if i in B["rows"]]
            if len(common) < len(A["ids"]) or len(common) < len(B["ids"]):
                print(f"[warn] {ds} {ca}-{cb}: pairing on {len(common)} common ids",
                      flush=True)
            y = [A["rows"][i][0] for i in common]
            pa = [A["rows"][i][1] for i in common]
            pb = [B["rows"][i][1] for i in common]
            sj = [A["rows"][i][2] for i in common]
            pb_res = paired_subject_bootstrap(y, pa, pb, sj, metric="macro_f1",
                                              n=args.n_boot, seed=0)
            out["contrasts"][f"{ds}__{ca}_minus_{cb}"] = {
                "delta": r4(pb_res["delta"]), "ci": [r4(pb_res["ci_lo"]), r4(pb_res["ci_hi"])],
                "p": r4(pb_res["p_value"]), "n_pairs": len(common),
                "n_valid_draws": pb_res["n_valid_draws"],
            }
            print(f"[pair] {ds} {ca}-{cb}: d={r4(pb_res['delta'])} "
                  f"CI=[{r4(pb_res['ci_lo'])},{r4(pb_res['ci_hi'])}] p={r4(pb_res['p_value'])}",
                  flush=True)

    json.dump(out, open(args.out, "w"), indent=1)
    print(f"[done] wrote {args.out}", flush=True)

    ref = json.load(open(args.ref)) if os.path.isfile(args.ref) else {}
    lines = ["# GaitEval v2.1 — master results (Phase 1-4)", "",
             "Point metrics: runner fixed-K macro-F1. CI: 95% subject-cluster bootstrap "
             "(UNPARSED-sentinel convention). p: permutation vs stratified chance.", "",
             "## Per-cell", "",
             "| dataset | condition | n | mF1 | 95% CI | perm p | unparsed |",
             "|---|---|---|---|---|---|---|"]
    for ds in DS_ORDER:
        rr = ref.get(ds if ds != "asd_kinect" else "asd", ref.get(ds, {}))
        if rr:
            ci = rr.get("lr_balanced", {}).get("subj_ci", ["", ""])
            lines.append(f"| {ds} | ref LR (feat) | {rr['n_test']} | "
                         f"{rr['lr_balanced']['mf1']} | [{ci[0]}, {ci[1]}] | "
                         f"{rr.get('lr_perm_p', '')} | – |")
            lines.append(f"| {ds} | ref chance | {rr['n_test']} | "
                         f"{rr['chance_mf1']['mean']} | – | – | – |")
        for cond in COND_ORDER:
            cell = out["cells"].get(f"{ds}__{cond}")
            if not cell:
                continue
            ci = cell["mf1_subj_ci"]
            lines.append(f"| {ds} | 7B {cond} | {cell['n']} | {cell['macro_f1']} | "
                         f"[{ci[0]}, {ci[1]}] | {cell['perm_p_vs_chance']} | "
                         f"{cell['n_unparsed']} |")
    lines += ["", "### Caveats", "",
              "- **pathogait**: the v2.1 test split has 2 subjects (720 clips each); "
              "subject-cluster bootstrap is degenerate (CIs collapse to a point) and "
              "row-level permutation p is anti-conservative under clustering. Treat "
              "pathogait LLM cells as sample-level point estimates; subject-level "
              "uncertainty comes from the Phase-1 LOSO reference (12 subjects).",
              "- **ataxia**: n=8 test clips over 3 subjects; no power (perm p=1.0 "
              "even at mF1 .27). LOSO reference (20 subjects) is the primary number.",
              "- **asd_kinect**: 1 clip per subject; cluster bootstrap reduces to an "
              "ordinary bootstrap.",
              "- **care_pd zs_mixed** (12-class mixed-label variant) is a diagnostic "
              "cell, not a benchmark number.",
              "", "## Paired contrasts (subject-paired bootstrap, macro-F1)", "",
              "| dataset | contrast | delta | 95% CI | p |", "|---|---|---|---|---|"]
    for k, v in out["contrasts"].items():
        ds, rest = k.split("__", 1)
        lines.append(f"| {ds} | {rest.replace('_minus_', ' − ')} | {v['delta']} | "
                     f"[{v['ci'][0]}, {v['ci'][1]}] | {v['p']} |")
    open(args.md, "w").write("\n".join(lines) + "\n")
    print(f"[done] wrote {args.md}", flush=True)


if __name__ == "__main__":
    main()
