# GaitEval

**GaitEval: A Multi-Condition Benchmark for Evaluating Whether Large Language Models Use Pose-Derived Gait Evidence**

Kaiyuan Yang · Xupeng Chen · Fan Huang · Jiangpeng He

Indiana University · New York University | WACV 2027

[Project website](https://ykyhaha.github.io/GaitEval-v2/) · [Eight-page paper](submission/01586_main_cameraready.pdf) · [Supplement](submission/01586_supp.pdf) · [LaTeX source](paper/) · [Citation](citation.bib)

This release follows the user-edited v2.2 manuscript: **8 main-text pages, 3 reference pages, 6 main tables, 2 figures**. All six resources—ASD-Kinect, ATAXIA, CARE-PD, GMFCS, PARKINSONISM, PATHOGAIT—have equal benchmark membership and retain their dataset-specific tasks. Input-view, model, adaptation, and transfer comparisons identify their actual test records; no scores from different test populations are treated as matched estimates.

## Reproduce released scores

```bash
python3 -m pip install -r requirements-analysis.txt
bash scripts/reproduce.sh
```

This CPU path recomputes **55 prediction-file point metrics**, verifies all **42 shared-condition cells**, checks the recorded parser outputs, regenerates six confusion figures, and checks the released GMFCS split repair and PATHOGAIT feature-removal predictions. LR/SVM references and historical participant-bootstrap statistics remain explicitly identified archived measurements. No new model training or inference is claimed.

- GMFCS repaired evaluation: 866 test clips / 166 participants; split intersections and exact test IDs are independently checked. The shared-condition comparison instead uses 255 clips / 149 participants.
- PATHOGAIT feature-removal evaluation: matching 2,181 test IDs, feature-SFT macro-F1 .6870 → .6316 after removing valid-frame fraction. Runtime changes, one training realization, and two participants limit attribution.
- The four GMFCS input-view entries in main Table 5 remain **provisional**, as explained in the main text and supplementary record audit. Source aggregates/logs do not establish matching corrected-test predictions. They are excluded from matched-test conclusions.

Full source poses, complete shared-condition training/input manifests, adapters, and full training logs remain external. Fresh inference/training requires authorized source inputs and the GPU/model stack; see [running models](docs/RUN_MODELS.md). The release supports score/split verification and does not claim full end-to-end retraining from bundled inputs.

## Build the manuscript and website

Compile the supplement before the main paper so cross-document table numbers resolve:

```bash
bash BUILD_LATEX.sh
python3 scripts/build_website.py
python3 scripts/verify_publication.py
```

The website builder preserves the HTML/CSS/JS template in `website/`, refreshes paper/figure/result assets, and mirrors the static site under `docs/` for GitHub Pages (`main:/docs`). Old paper-download filenames remain byte-identical aliases of the current PDF.

## Contents

| Folder | Contents |
|---|---|
| `paper/` | Current editable manuscript, supplement, tables, references, figures and PDFs |
| `figure_source/` | Exact editable diagram source, assets, fonts and source credits |
| `results/` | Original 55-run shared release and archived matched references/statistics |
| `evidence/` | Corrective split maps, generations, source-bound metrics and verification code |
| `code/`, `scripts/` | Inference/training recipes, score checks, plots and website build |
| `docs/`, `website/` | Public project page, attribution, reproducibility and paper-to-file mapping |
| `submission/` | Current paper/supplement and submission checklist |
| `audit/` | Publication snapshot, page counts, hashes and verification reports |

See [table-to-file mapping](docs/TABLE_TO_FILES.md), [reproducibility scope](docs/REPRODUCIBILITY.md), and [licenses and source access](docs/LICENSES_AND_SOURCES.md). Original patient RGB videos and model checkpoints are not redistributed; source data/image terms remain separate from code licensing.
