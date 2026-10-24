# Datasets: access and licensing

GaitEval **does not redistribute any source recording**. Download each dataset from
its official release, accept its terms, and regenerate the model-visible views with
the code in `gaiteval/` (see `docs/REPRODUCE.md`). Each source keeps its upstream
license; the status below is what the official release states as of 2026-10.

| GaitEval name | Population / task | Official source | License status |
|---|---|---|---|
| GMFCS | Children with cerebral palsy; 4-level GMFCS | SimTK release (group 1918) — https://simtk.org/frs/?group_id=1918 ; paper: https://www.nature.com/articles/s41467-020-17807-z ; code: https://github.com/stanfordnmbl/mobile-gaitlab | see SimTK release terms |
| ATAXIA | 20 healthy volunteers, normal vs. imitated ataxic gait | Mendeley Data — https://data.mendeley.com/datasets/2vkk2r9tx3/1 | see Mendeley record |
| PARKINSONISM | Parkinson's disease patients; binary motor severity | https://github.com/abbasilab/Video-Tracking-PD ; paper: https://www.nature.com/articles/s41531-024-00742-x | CC BY-NC-ND 4.0 |
| PATHOGAIT | Healthy volunteers simulating six gait patterns (Kinect v2) | https://github.com/kooksung/pathological_gait_datasets ; paper: https://doi.org/10.1109/ACCESS.2020.3013029 | **no explicit license** in the official repository — obtain it there; do not re-host |
| CARE-PD (standardized suite) | Multi-site Parkinson's cohort; UPDRS gait 0-3 | https://huggingface.co/datasets/vida-adl/CARE-PD ; https://github.com/TaatiTeam/CARE-PD | see release (README and metadata header word the ND term differently) |
| ASD-Kinect (standardized suite) | Autism vs. typical, Kinect | Dryad — https://datadryad.org/dataset/doi:10.5061/dryad.s7h44j150 | see Dryad record |

## What this repository does ship

- `splits/` — frozen split indices and subject maps for the four core resources,
  including the corrected participant-disjoint GMFCS partition used in the paper
  (`gmfcs_{train,val,test}_sd.tsv`: new index -> original split/index, patient id).
- `gaiteval/` — deterministic feature extraction, view generators (raw / normalized
  coordinates, motion summary, named and z-scored feature views), prompts, the
  boundary-anchored label parser, the vLLM runner, SFT data builder and trainer,
  scoring and subject-cluster bootstrap code.
- `predictions/` — the raw model generations and parsed predictions behind the
  paper's tables (model outputs and dataset-provided labels only; no pose data).

GaitEval introduces no new human-subjects data and is intended for evaluating
motion-evidence use by models, not for training or deploying diagnostic systems.
