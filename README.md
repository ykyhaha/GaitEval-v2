# GaitEval v2

Six datasets, one evidence-grounded gait benchmark: ASD-Kinect, ATAXIA, CARE-PD, GMFCS, PARKINSONISM, and PATHOGAIT.

This release accompanies the WACV 2027 camera-ready preparation. The research question, same-feature baseline design, adaptation ladder, and scoped ATAXIA–PATHOGAIT transfer conclusion are retained from the accepted version.

Project website source: `website/dist/`, mirrored under `docs/` for GitHub Pages. Hosting activation is tracked separately from the paper preparation.

## Reproduce committed results

```bash
python3 -m pip install -r requirements-analysis.txt
bash scripts/reproduce.sh
```

The CPU-only path recomputes all 55 prediction-file point metrics, checks all 42 common cells and record alignment, checks parsing of genuine outputs, and regenerates the six confusion figures. Reference scores are committed source measurements. They are NOT silently retrained from absent features.

## Rerun models with authorized source inputs

Obtain the original S records, feature CSVs, summaries, and split manifests from the authors or authorized source. Run `python3 scripts/validate_inputs.py --root /absolute/path/to/S_inputs` before inference or training. The validator requires every dataset and rejects subject overlap, missing evidence, wrong task labels/counts, and capture-quality columns. Then use `code/v21_llm_runner.py` and `code/v21_make_sft_data.py`; model training/inference requires the separately installed GPU stack and checkpoints. The release does not include model weights or training logs.

S is the common subject-disjoint protocol; L denotes retained accepted-protocol subset experiments. Six-dataset membership does not imply every optional model/view/transfer configuration has been run. See docs/REPRODUCIBILITY.md and docs/LICENSES_AND_SOURCES.md.

## Files

- `datasets.json`: six-dataset labels/counts/input contracts.
- `code/`: curated inference, SFT, parsing, and statistics implementation.
- `results/`: original prediction logs, summaries, and task-matched reference index.
- `scripts/`: reproducibility and input checks.
- `docs/`: scope, licensing, and table mapping.
- `website/dist/`: project page source; `docs/` mirrors it for GitHub Pages.
- `paper/`, `figures/`, `submission/`: editable manuscript, figures, preparation PDFs.
- `audit/`: metric/parser/reference/PDF checks.

No source patient videos are redistributed. No blanket license is asserted over upstream code or data; retained authorship and per-source terms apply. This repository is independent of the private editing repository.
