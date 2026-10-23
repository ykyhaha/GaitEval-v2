# Six-dataset standardized results

All six datasets enter the same S contract. L measurements are kept in the manuscript with explicit tags. CARE-PD uses the four-label UPDRS gait task.

| Dataset | Test clips | Test subjects | ZS summary | ZS z-features | SFT summary | LR | SVM |
|---|---:|---:|---:|---:|---:|---:|---:|
| ASD-Kinect | 20 | 20 | 0.3103 | 0.4357 | 0.3103 | 0.6970 | 0.7442 |
| ATAXIA | 8 | 4 | 0.2727 | 0.3333 | 0.3333 | 0.8730 | 0.8730 |
| CARE-PD | 665 | 24 | 0.3206 | 0.1335 | 0.4446 | 0.6591 | 0.6498 |
| GMFCS | 255 | 149 | 0.2647 | 0.1501 | 0.4670 | 0.5788 | 0.5710 |
| PARKINSONISM | 29 | 5 | 0.3958 | 0.7575 | 0.5421 | 0.5606 | 0.5735 |
| PATHOGAIT | 1440 | 2 | 0.0690 | 0.1387 | 0.4510 | 0.8809 | 0.8975 |

Full 55-run metrics and class supports: `derived/metrics_all_runs.csv` / `derived/audit_report.json`. The historical `V21_RESULTS.md` is preserved unchanged for provenance and contains stale metadata and the CARE-PD mixed-task reference; use this index and `references_task_matched.json` for primary comparisons.
