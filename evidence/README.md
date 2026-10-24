# Evidence for the v2.1 corrections

Source snapshots are bound to immutable commits in `provenance.json`:

- Working archive: `james20141606/gaiteval-wacv` at `2348b11f69a248ec57234c92747dda79f368d798`.
- Released companion: `gaiteval/GaitEval` at `60f3503902f5bcd06b77198aaa0cb18aadfcaad9`.

The source experiment-log excerpt documents the earlier execution. It is provenance, not a substitute for the predictions and split maps checked here.

Run `python verify_corrections.py` from any working directory. It checks the three corrected GMFCS participant intersections, exact corrected-test IDs and label alignment, the PATHOGAIT paired test records, raw-output parsing, and the recomputed SFT metrics. It also joins the GMFCS qualitative record to the corrected model and rejects the old success caption, and verifies header-label/index redaction in the prepared prompts. The script asserts the expected checks and writes `metrics_verified.json`.

`qualitative/qualitative_examples_source.json` is the original source metadata, including pre-redaction internal headers. It is **not** a model-visible prompt. `matched_cases_prepared.json` contains the redacted evidence and the flat wrapper used for the paper panels, separately from evaluation-only ground truth. Exact UTF-8 strings are retained; prompt typography in the PDF is normalized to ASCII hyphens.

The `gaiteval/` files are supporting source snapshots, not a complete standalone training installation. The full upstream repository provides the remaining modules. Source poses, complete S train/validation/test inputs, model weights/adapters, and full training logs are not provided here. LR/SVM and paired-bootstrap JSONs remain archived measurements; this revision recomputes LLM point metrics, not those model fits.

The original corrected GMFCS experiment has 866 test clips and 166 participants. It does not verify or replace the different S experiment with 255 clips and 149 participants. The PATHOGAIT L feature-removal experiment has 2,181 clips and two test participants; it is not the 1,440-clip S summary-SFT row.

The global consistency audit found a contradiction in the source draft: the 7B GMFCS summary/raw-feature/z-feature values described as corrected are explicitly associated with 899 clips in `r2_recompute_part1.json`. `source_snapshot/gmfcs_view_lineage_excerpt.json` records that source-bound evidence. These cells, and an independently unverified normalized-coordinate cell, are withheld from corrected comparisons. The 866-clip SFT and references remain valid under their documented scope.

`source_snapshot/S_point_metrics.csv` records the common release's 55 prediction-backed point metrics. `L_point_metrics_verified.json` additionally records the independently rescored L checks, including correct fixed-six-label treatment of PATHOGAIT invalid outputs. Original upstream snapshots are preserved; derived corrections do not silently rewrite those files. Run `../audit/check_global_consistency.py` in the complete repository checkout for cross-table and baseline checks.

Code/output snapshots retain upstream authorship and the included upstream license. Dataset and figure rights are separate. Dataset-access notes reproduce upstream statements and do not constitute new permission; unresolved resource-example rights are explicitly listed in the revision log.
