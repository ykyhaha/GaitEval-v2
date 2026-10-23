# Reproducibility scope

| Paper artifact | Evidence and command | Status |
|---|---|---|
| Six-dataset summary/z-feature/SFT point metrics | results/v21_runs/*/results.jsonl; scripts/audit_results.py | Recomputed, prediction-backed |
| Six-dataset confusion matrices | scripts/render_result_figures.py | Regenerated from genuine predictions |
| No-evidence, shuffled evidence, candidate-order controls | same prediction directory | Point metrics recomputed |
| LR/SVM reference values | results/references_task_matched.json | Source results, feature inputs absent |
| Cluster intervals and paired bootstrap values | results/v21_phase4_stats.json | Archived estimator, not a fresh execution |
| GMFCS S split provenance | source manifests state 149 test participants / 255 clips, no overlap | Full input manifests required for independent verification |
| Full source-to-features-to-LLM run | code plus original S external inputs and checkpoints | Blocked by missing input layers/adapters |
| Matched pose–prompt–output qualitative panel | output logs available; input/pose correspondence absent | Incomplete; no fabricated examples |
| PATHOGAIT L feature-SFT without valid-frame fraction | Original feature-SFT never rerun with only that feature removed | Not executed; no causal or kinematics-only superiority claim |

The historical bootstrap uses a dynamic label union and excludes draws with one participant or one truth class. Its intervals and paired bootstrap tail areas are identified separately from fixed-task-label point estimates. A non-significant difference is not an equivalence test. Very small participant counts are descriptive limits. No new training or inference was performed by packaging this release.
