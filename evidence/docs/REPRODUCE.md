# Reproducing the paper

Every number listed below is checked automatically by `scripts/verify_repro.py`
(83 checks; tolerance = half a unit in the third decimal, since the paper prints
3-decimal roundings).

## 0. Setup

```bash
pip install -r requirements.txt
export GAITEVAL_ROOT=/path/to/workspace   # holds data/, results/, cache/
```

## 1. No raw data needed: Table 2 (primary zero-shot benchmark, 60 cells)

```bash
python scripts/score_table2.py      # re-parses predictions/v1/*/results.jsonl
python scripts/verify_repro.py      # 60 Table-2 checks pass; data-dependent ones SKIP
```
Re-parsing uses the boundary-anchored longest-match parser; macro-F1 follows the
paper's invalid-as-error convention (an unparsed output enters the macro average as
an extra zero-F1 label, as in scikit-learn's label union). GMFCS is scored on the
corrected participant-disjoint test split (`splits/gmfcs_test_sd_ids.txt`, 866 clips,
166 participants).

## 2. With the source data: views, references, statistics

1. Download the datasets (`docs/DATASETS.md`) under `$GAITEVAL_ROOT/data/`.
2. Regenerate the derived views and the corrected GMFCS partition:
   ```bash
   cd gaiteval
   python feature_extraction_multi.py
   python make_feature_view.py --dataset <ds> --data-root $GAITEVAL_ROOT/data/abnormal_dataset_processed
   python make_normalized_view.py ...      # 32-frame canonical 12-joint view
   python make_subject_splits.py           # writes train_sd / val_sd / test_sd for GMFCS
   ```
3. Linear / RF references (Table 4, supplement):
   ```bash
   python feature_baseline.py                                   # ATAXIA, PARKINSONISM, PATHOGAIT rows + RF
   python cr_gmfcs_sd_references.py --features-dir ... --subject-map ...   # GMFCS row (corrected split)
   ```
4. GMFCS corrected-split re-score and paired test (supplement "GMFCS corrected-split rerun"):
   ```bash
   python cr_gmfcs_sd_rescore.py
   python cr_gmfcs_paired.py
   ```
5. `python ../scripts/verify_repro.py` -> all 83 checks pass.

| Paper item | Script | Output checked |
|---|---|---|
| Table 2 (all rows) | `scripts/score_table2.py` | `table2_rescored.json` |
| Table 4, ATAXIA/PARKINSONISM/PATHOGAIT + RF | `gaiteval/feature_baseline.py` | `feature_baselines.json` |
| Table 4 GMFCS + supp. original-vs-corrected | `gaiteval/cr_gmfcs_sd_references.py` | `cr_gmfcs_sd_references.json` |
| Supp. paired SFT-LR (GMFCS) | `gaiteval/cr_gmfcs_paired.py` | `cr_gmfcs_sd_paired.json` |

## 3. GPU experiments (LLM inference and LoRA-SFT)

Zero-shot runs: `gaiteval/view_run.py` against a vLLM server (temperature 0).
LoRA-SFT (Table 5): `gaiteval/make_sft_data.py` then `gaiteval/sft_train.py`
(rank 16, alpha 32, dropout 0.05, all-linear, completion-only, 3 epochs, lr 1e-4,
effective batch 16, max length 1024; trl 0.11.4, peft 0.13.2), then evaluate the
merged model with `view_run.py`. The raw generations of every published run are in
`predictions/`, so all statistics can be recomputed without rerunning the models.
Standardized six-condition suite (Table 7): `gaiteval/v2_reference_suite.py`,
`v21_llm_runner.py`, `v21_make_sft_data.py`, `v21_phase4_stats.py`; outputs in
`predictions/v21/`.
