# Reproducibility scope for the eight-page manuscript

| Evidence | Reproduction status |
|---|---|
| 55 released prediction files; 42 shared-condition cells | Fixed-task-label accuracy, macro-F1, kappa, counts and parser outputs recomputed on CPU |
| Six confusion figures and per-class scores | Regenerated from committed predictions |
| No-evidence, shuffled evidence, reversed/shuffled candidate order | Complete across six datasets for Qwen2.5-7B summary zero-shot controls; fixed permutation seeds, not a multi-seed robustness study |
| Matched LR/SVM points | Archived source measurements; missing feature layers prevent retraining them here |
| Participant intervals and paired tail areas | Archived historical estimator, separated from freshly checked fixed-label point estimates |
| GMFCS corrected split | 1,602/478/866 clips, 94/84/166 participants; intersections empty; corrected SFT IDs/truths/raw parsing checked by `evidence/verify_corrections.py` |
| GMFCS shared-condition training provenance | Test outputs cover 255 clips / 149 participants; full training input manifests are still unavailable for independent separation checks |
| PATHOGAIT feature-SFT without valid-frame fraction | Recovered completed run; matching 2,181 test IDs; scores and raw parsing checked; macro-F1 .6316 versus .6870 with the field |
| GMFCS Table 5 view entries | Summary is log-only (866 clips), normalized coordinates are draft-only/unverified, raw/z-features are historical 899-clip aggregates; not verified matched-test estimates |
| Full source-to-model training/inference | Requires external authorized poses, original input layers, training manifests and checkpoints/adapters |
| Complete matched pose–prompt–output panels | Output decisions are available; complete shared-condition pose/input correspondence remains absent |

Run `bash scripts/reproduce.sh` after installing `requirements-analysis.txt`. Historical bootstrap intervals used a dynamic label union; they are not presented as newly recomputed fixed-label confidence intervals. A non-significant comparison does not establish equivalence. PATHOGAIT's two participants and the small ATAXIA/PARKINSONISM tests constrain population-level inference. Runtime changes in the feature-removal rerun prevent causal attribution of the entire difference to the removed field. No new model execution is performed by this release update.
