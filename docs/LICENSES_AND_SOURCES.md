# Dataset access and example provenance

The release does not redistribute the full source datasets, raw clinical videos, or model weights. Repository code rights and dataset/image rights are separate. No blanket relicensing is asserted.

| Dataset | Official source | Terms / release boundary |
|---|---|---|
| ASD-Kinect | https://zenodo.org/records/4025120 ; DOI 10.5061/dryad.s7h44j150 | Dataset downloaded from the official record. Example is original Svideo.avi (child ASD/1/video), not augmented. Paper is Al-Jubouri et al., JPCS1818 012201, CC BY3.0. Verify dataset-specific record terms. |
| ATAXIA | https://data.mendeley.com/datasets/2vkk2r9tx3/1 | Dataset CC BY4.0. Example is a source-paper video illustration (Khalil et al., IEEE2022). Source-paper image rights are not automatically the dataset license. |
| CARE-PD | https://neurips2025.care-pd.ca/ ; https://github.com/TaatiTeam/CARE-PD | Official project states CC BY-NC4.0; use with its terms and cohort attribution requirements. Example is a crop of static/images/benchmark.png. |
| GMFCS | https://simtk.org/projects/video-gaitlab ; https://github.com/stanfordnmbl/mobile-gaitlab | Processed trajectories CC BY-NC2.0; source code Apache2.0. Original demo RGB use is restricted; only a newly drawn skeleton from the source demo keypoints is used here. This is not confirmed as an evaluated test record. |
| PARKINSONISM | https://github.com/abbasilab/Video-Tracking-PD ; DOI10.1038/s41531-024-00742-x | Final source article CC BY4.0. Source data/code terms must be checked independently. Example is a cropped recording illustration, not a severity annotation. |
| PATHOGAIT | https://github.com/kooksung/pathological_gait_datasets | Source repository supplies recordings but no blanket license was found. Do not redistribute the full raw dataset or assert a new license. Example renders a recorded skeleton; permission for redistributed derived displays requires confirmation. |

Source examples are resource illustrations only, never paired to a prediction without sample-level correspondence. No depicted face or body is used to infer a diagnosis. The public release contains genuine model outputs and derived scores; it does not claim distribution permission for omitted original inputs.
