# Paper-to-file map

| Artifact | Source | Generation / verification |
|---|---|---|
| Main Table1, six-dataset task/counts | datasets.json; results/references_task_matched.json | common conditions checked by scripts/check_release.py |
| Main Table2, all six datasets | results/v21_runs/{dataset}__{zs,feat,sft}/results.jsonl | scripts/audit_results.py; results/derived/shared_six_dataset_metrics.csv |
| Main Table2 chance/LR/SVM | results/references_task_matched.json | committed source values; no absent features silently reconstructed |
| Main Figures1–2 | paper/figures/overview.pdf, methods.pdf | scripts/draw_figures.py with figures/assets and source credits |
| Six supplementary confusion figures and per-class tables | same prediction JSONLs | scripts/render_result_figures.py |
| Evidence/order/SFT contrasts and intervals | results/v21_phase4_stats.json | historical estimator; scope explained in docs/REPRODUCIBILITY.md |
| Qualitative successes/failures | audit/qualitative_cases.json plus each source JSONL | exact actual model output; matching pose/input unavailable |
| Retained accepted-protocol subset tables | paper/supplementary.tex | historical L cells preserved with explicit scope, not six-dataset S reruns |
| Reference entries/numbers | paper/references_frozen.bbl | audit/reference_freeze.json, 67 entries |

The public code and results correspond to the shared six-dataset task. Optional protocol-specific cells and missing experiments remain explicitly identified.
