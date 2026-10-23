# Running models with the missing external inputs

These commands are the configured recipe, not a claim of a new run. Recover the original S corpus and training artifacts first. Preserve the six task contracts in datasets.json. A GPU/vLLM environment and authorized base model access are separate requirements.

```bash
python3 scripts/validate_inputs.py --root /absolute/path/to/S_inputs
# Start an OpenAI-compatible vLLM server serving Qwen/Qwen2.5-7B-Instruct.
python3 code/v21_llm_runner.py --root /absolute/path/to/S_inputs --dataset asd_kinect --condition zs --out-dir reruns/asd_kinect__zs
python3 code/v21_make_sft_data.py --root /absolute/path/to/S_inputs --out-root sft_data
python3 code/sft_train.py --data-dir sft_data/asd_kinect --out-dir adapters/asd_kinect --epochs 3 --lr 0.0001 --bsz 8 --grad-accum 2 --lora-r 16
python3 code/v2_reference_suite.py --root /absolute/path/to/S_inputs --datasets asd_kinect ataxia care_pd gmfcs parkinsonism pathogait --out rerun_references.json
```

Repeat inference for each dataset and the six zero-shot/control conditions (`zs`, `feat`, `noev`, `shufev`, `lorder-rev`, `lorder-shuf1`). For SFT inference, serve each dataset's merged checkpoint, set NE_MODEL to its served model name, and use the same runner's `zs` prompt. NE_MAXTOK defaults to48 and temperature is0. Training defaults are the committed source recipe; the source comments record trl0.11.4, peft0.13.2, transformers4.57.3. This historical GPU environment has not been rebuilt here.

The baseline suite retains source estimator settings. Release changes add fixed task labels, input-path compatibility, fail-fast quality/overlap checks, and shared preflight validation. Source raw columns are scaled and median-imputed using training data inside each pipeline; unsupported all-missing columns are dropped using training data. Archived bootstrap behavior is retained and identified in the paper. New baseline values must be compared with committed references before replacing any paper result.

This release's CPU scoring/figure path is verified independently of these absent inputs. Full pose extraction, feature construction, and historical model retraining cannot be reconstructed from this snapshot alone.
