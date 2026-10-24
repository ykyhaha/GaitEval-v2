"""view_run.py — Derived-view flat-prompt runner for the GaitEval benchmark.

Unlike flat_run.py (which sends the prebuilt RAW-coordinate prompts, ~40-62k
tokens), this runner builds a short classification prompt from a *derived view*
of each clip — by default the ~320-token biomechanical "motion summary" produced
by feature_extraction_multi.py. This (a) fits any 32k-context model without
YaRN, and (b) is the core multimodal-ablation view (Exp 4): does a compact,
interpretable derived representation beat raw coordinate dumps?

Views
-----
  motion_summary : the natural-language biomech summary (features/<split>_motion_summary.jsonl)

(metadata / biomech-table views can be added the same way.)

Usage
-----
    python view_run.py --dataset pathological --split test \\
        --backend vllm --model qwen --view motion_summary --limit 20 \\
        --out-dir $GAITEVAL_ROOT/results/view_ds3_qwen

Reuses parse_label() from flat_run.py and evaluate() from eval_general.py so the
parsing + metrics are identical to the raw flat path.
"""

from __future__ import annotations

import paths  # noqa: E402  (GAITEVAL_ROOT layout)
import argparse
import json
import logging
import os
import random
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from glob import glob
from typing import Any, Dict, List, Optional

import numpy as np

# Kept as a literal rather than imported from make_perturbed_views: that module
# imports the primitive engine and numpy-heavy helpers, and view_run is the hot
# path every cached run depends on. The set is asserted against the real registry
# in test_view_prompt.py, so the two cannot drift apart silently.
_PERTURB_NAMES = ("identity", "translate", "scale", "mirror", "shuffle_time",
                  "reverse_time", "drop_arms", "noise", "desymmetrize")

from datasets import list_datasets
from eval_general import evaluate
from flat_run import parse_label, _read_existing_results
from model_client import make_llm_client, resolve_model
import registry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Prompt construction from a derived view
# ---------------------------------------------------------------------------

def _render_labels(label_map: Dict[int, str], order: str = "sorted",
                   seed: int = 0) -> str:
    """Render the candidate-class block.

    The DEFAULT (order='sorted') is byte-identical to the inline expression that
    produced the cached runs; test_view_prompt.py locks those bytes. Changing
    them silently makes cached and fresh runs incomparable rather than raising.

    order='reversed'/'shuffled' exist for the L0 label-order sensitivity probe:
    a model that reads the summary should be invariant to the order classes are
    listed in, whereas a model emitting a positional default (e.g. always the
    first-listed class) will track the order. That distinction matters here
    because 21/65 cached runs collapse to a single class, and label-order
    invariance is what separates "collapsed onto a class" from "collapsed onto
    a position". Only the ORDER may change -- never the label set, or the probe
    would confound two variables.
    """
    keys = sorted(label_map)
    if order == "sorted":
        pass
    elif order == "reversed":
        keys = keys[::-1]
    elif order == "shuffled":
        random.Random(seed).shuffle(keys)
    else:
        raise ValueError(
            f"unknown label order {order!r}; expected sorted/reversed/shuffled")
    return "\n".join(f"- {label_map[k]}" for k in keys)


def build_view_prompt(summary_text: str, label_map: Dict[int, str],
                      style: str = "flat", label_order: str = "sorted",
                      label_seed: int = 0) -> str:
    """Wrap a derived-view text in a single-turn classification instruction.

    style='flat'       : minimal "read summary -> output label" (default).
    style='structured' : a reasoning-anchored prompt that names the
                         discriminative biomechanical dimensions and asks the
                         model to weigh evidence for EACH class before deciding.
                         Tests whether scaffolding breaks the majority collapse.
                         (Measured answer: it does not -- structured runs still
                         collapse at 0.993-1.000.)

    Defaults reproduce the cached runs byte-for-byte.
    """
    labels = _render_labels(label_map, order=label_order, seed=label_seed)
    if style == "structured":
        return (
            "You are a gait-analysis expert classifying a walking clip from a "
            "compact biomechanical motion summary derived from a 3D skeleton "
            "sequence. The summary reports motion amplitudes, left/right "
            "asymmetry, trunk/pelvis stability, trajectory variability, and "
            "movement smoothness (jerk).\n\n"
            f"{summary_text.strip()}\n\n"
            "Candidate classes:\n"
            f"{labels}\n\n"
            "Reason step by step:\n"
            "1. List the 2-3 most abnormal biomechanical signals in this summary "
            "(e.g. high asymmetry, high jerk, large trunk sway, reduced amplitude).\n"
            "2. For EACH candidate class, briefly state whether those signals are "
            "consistent or inconsistent with it.\n"
            "3. Do NOT default to the most common class; pick the class best "
            "supported by the specific signals.\n"
            "Finally, on a new line, output exactly: FINAL: <one class name>"
        )
    return (
        "You are classifying a gait clip from a compact biomechanical motion "
        "summary derived from a 3D skeleton sequence. The summary reports motion "
        "amplitudes, left/right asymmetry, trunk/pelvis stability, trajectory "
        "variability, and movement smoothness.\n\n"
        f"{summary_text.strip()}\n\n"
        "Task: based ONLY on the motion summary above, classify the gait into "
        "exactly one of the following classes:\n"
        f"{labels}\n\n"
        "Return only one label, written exactly as listed above."
    )


def _find_view_file(dataset_dir: str, split: str, view: str) -> str:
    """Locate the derived-view JSONL for a dataset/split."""
    fname = f"{split}_{view}.jsonl"
    hits = glob(os.path.join(dataset_dir, "**", fname), recursive=True)
    if not hits:
        raise FileNotFoundError(
            f"No '{fname}' found under {dataset_dir}. "
            "Run feature_extraction_multi.py first."
        )
    return hits[0]


import re

# The motion-summary header from feature_extraction_multi.py embeds the
# ground-truth label and sample_index ("... | label: antalgic gait | sample_index: 0 | ...").
# Feeding that to the model is catastrophic label leakage — redact it here so the
# model only ever sees the biomechanical statistics. (Defense-in-depth; the
# source generator is also being fixed.)
_LEAK_LABEL = re.compile(r"(?im)\blabel:\s*[^|\n]+")
_LEAK_INDEX = re.compile(r"(?im)\bsample_index:\s*\S+")


def _redact_leak(text: str) -> str:
    text = _LEAK_LABEL.sub("label: [REDACTED]", text)
    text = _LEAK_INDEX.sub("sample_index: [REDACTED]", text)
    return text


def _load_view_items(
    view_path: str,
    split: str,
) -> List[Dict[str, Any]]:
    """Parse a derived-view JSONL into [{id, summary_text, label_numeric}]."""
    items: List[Dict[str, Any]] = []
    with open(view_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            text = _redact_leak(rec.get("summary_text") or rec.get("text") or "")
            si = rec.get("sample_index")
            items.append(
                {
                    "id": f"{split}_{si}",
                    "summary_text": text,
                    "label_numeric": int(rec["label"]),
                }
            )
    return items


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------

def run(
    *,
    dataset_id: str,
    split: str,
    backend: str,
    model: str,
    view: str,
    data_root: str,
    out_dir: str,
    limit: Optional[int],
    max_workers: int,
    max_tokens: int,
    no_think: bool = False,
    shuffle: bool = False,
    seed: int = 0,
    prompt_style: str = "flat",
    label_order: str = "sorted",
) -> None:
    os.makedirs(out_dir, exist_ok=True)
    results_file = os.path.join(out_dir, "results.jsonl")

    model_id = resolve_model(model, backend)
    logger.info("Backend=%s Model=%s View=%s Workers=%d", backend, model_id, view, max_workers)

    registry = list_datasets(data_root)
    if dataset_id not in registry:
        raise ValueError(f"Dataset '{dataset_id}' not registered. Found: {sorted(registry)}")
    meta = registry[dataset_id]
    label_map = {int(k): v for k, v in meta["label_map"].items()}
    ordinal = meta["ordinal"]

    view_path = _find_view_file(meta["dir"], split, view)
    items = _load_view_items(view_path, split)
    logger.info("Loaded %d %s items for %s/%s", len(items), view, dataset_id, split)

    if shuffle:
        import random
        random.Random(seed).shuffle(items)
        logger.info("Shuffled items with seed=%d", seed)

    existing = _read_existing_results(results_file)
    todo = [it for it in items if it["id"] not in existing]
    if limit is not None:
        todo = todo[:limit]
    logger.info("Resuming: %d done. Running %d (limit=%s).", len(existing), len(todo), limit)

    if todo:
        client = make_llm_client(backend)
        file_lock = threading.Lock()
        prog = {"done": len(existing), "unparsed": 0}
        tok = {"prompt_tokens": 0, "completion_tokens": 0}
        tok_lock = threading.Lock()
        errors: List[tuple[str, str]] = []
        t0 = time.time()

        def call_one(item: Dict[str, Any]) -> Dict[str, Any]:
            prompt_text = build_view_prompt(item["summary_text"], label_map,
                                            prompt_style, label_order=label_order,
                                            label_seed=seed)
            # A reasoning model (Qwen3) opens <think> and, under a small max_tokens,
            # is cut off mid-thought -> parse_label then mines a label from the
            # unfinished reasoning. This is the exact defect that invalidated every
            # L1 run. Disabling thinking makes the model answer immediately; a
            # classification prompt needs no chain.
            extra = ({"chat_template_kwargs": {"enable_thinking": False}}
                     if no_think else {})
            resp = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt_text}],
                temperature=0,
                max_tokens=max_tokens,
                extra_body=extra,
            )
            raw = resp.choices[0].message.content or "" if resp.choices else ""
            if resp.usage is not None:
                with tok_lock:
                    tok["prompt_tokens"] += resp.usage.prompt_tokens or 0
                    tok["completion_tokens"] += resp.usage.completion_tokens or 0
            pred, unparsed = parse_label(raw, label_map)
            return {
                "id": item["id"],
                "true_label": item["label_numeric"],
                "pred_label": pred,
                "pred_str": label_map.get(pred, "unparsed") if not unparsed else "unparsed",
                "raw_output": raw,
                "unparsed": unparsed,
            }

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futs = {ex.submit(call_one, it): it["id"] for it in todo}
            for fut in as_completed(futs):
                sid = futs[fut]
                try:
                    res = fut.result()
                except Exception as exc:  # noqa: BLE001
                    errors.append((sid, f"{type(exc).__name__}: {exc}"))
                    traceback.print_exc()
                    continue
                with file_lock:
                    with open(results_file, "a") as fh:
                        fh.write(json.dumps(res) + "\n")
                prog["done"] += 1
                if res.get("unparsed"):
                    prog["unparsed"] += 1

        wall = time.time() - t0
        logger.info("Finished %d in %.1fs. Errors: %d Unparsed: %d",
                    len(todo), wall, len(errors), prog["unparsed"])
        for sid, msg in errors[:10]:
            logger.error("  id=%s: %s", sid, msg)
        with open(os.path.join(out_dir, "run_meta.json"), "w") as fh:
            json.dump(
                {
                    "dataset": dataset_id, "split": split, "backend": backend,
                    "model": model_id, "view": view,
                    "prompt_style": prompt_style, "label_order": label_order,
                    "n_attempted": len(todo), "n_errors": len(errors),
                    "n_unparsed": prog["unparsed"], "wall_time_seconds": round(wall, 2),
                    "prompt_tokens": tok["prompt_tokens"],
                    "completion_tokens": tok["completion_tokens"],
                },
                fh, indent=2,
            )

    all_results = list(_read_existing_results(results_file).values())
    if not all_results:
        logger.warning("No results to evaluate.")
        return
    y_true = np.array([r["true_label"] for r in all_results])
    y_pred = np.array([r["pred_label"] for r in all_results])
    evaluate(
        y_true=y_true, y_pred=y_pred, label_map=label_map, ordinal=ordinal,
        out_dir=out_dir,
        model_label=f"{model_id} ({backend}, view={view}) — {dataset_id}/{split}",
    )

    if limit is not None and limit <= 20:
        print("\n--- Predictions (true -> pred) ---")
        for r in sorted(all_results, key=lambda x: x["id"]):
            status = "UNPARSED" if r.get("unparsed") else ""
            print(f"  {r['id']:14s} true={label_map.get(r['true_label'],'?'):28s} "
                  f"pred={r.get('pred_str','?'):28s} {status}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", required=True, choices=registry.dataset_ids())
    p.add_argument("--split", default="test", choices=["train", "val", "test"])
    p.add_argument("--backend", default="vllm", choices=["vllm", "openai", "together", "openrouter"])
    p.add_argument("--model", default="qwen")
    p.add_argument("--view", default="motion_summary",
                   choices=["motion_summary", "feature_vector", "feature_vector_z",
                            "feature_vector_novff", "normalized"])
    p.add_argument("--perturb", default=None, choices=sorted(_PERTURB_NAMES),
                   help="L4: read the perturbed view <split>__<perturb>_<view>.jsonl "
                        "built by make_perturbed_views.py. Perturbation happens "
                        "upstream on the keypoints; the runner only selects the file.")
    p.add_argument("--data-root", default=paths.DATA_ROOT)
    p.add_argument("--out-dir", default=None)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--max-workers", type=int, default=8)
    p.add_argument("--max-tokens", type=int, default=64)
    p.add_argument("--shuffle", action="store_true",
                   help="Deterministically shuffle before --limit (class-mixed subset)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--prompt-style", default="flat", choices=["flat", "structured"],
                   help="flat (minimal) or structured (reasoning-anchored, anti-collapse)")
    p.add_argument("--label-order", default="sorted",
                   choices=["sorted", "reversed", "shuffled"],
                   help="L0 label-order sensitivity probe; 'sorted' reproduces "
                        "cached runs byte-for-byte")
    p.add_argument("--raw-split", action="store_true",
                   help="Use --split verbatim instead of resolving the frozen "
                        "evaluation partition from the manifest (audit/debug only)")
    p.add_argument("--no-think", action="store_true",
                   help="disable Qwen3 reasoning (empty <think></think>) so a short "
                        "classification prompt is not truncated mid-thought — the "
                        "defect that invalidated the L1 runs.")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S",
    )

    # GMFCS's predefined split leaked subjects across train/val/test, so its
    # frozen evaluation partition is the repaired `*_sd` one. Resolving it here
    # (rather than making every caller remember) means `--split test` cannot
    # silently evaluate on the leaky partition. --raw-split opts out.
    split = args.split if args.raw_split else registry.split_name(args.dataset,
                                                                  args.split)
    if split != args.split:
        logger.info("split %r resolves to frozen partition %r for dataset %r",
                    args.split, split, args.dataset)
    model_id_safe = resolve_model(args.model, args.backend).replace(chr(47), chr(45))
    # A perturbed run reads <split>__<perturb>_<view>.jsonl. _find_view_file builds
    # f"{split}_{view}.jsonl", so folding the perturb into the view name selects the
    # right file without touching the loader every cached run depends on.
    view_name = f"_{args.perturb}_{args.view}" if args.perturb else args.view
    out_dir = args.out_dir or os.path.join(
        paths.RESULTS,
        (f"pert_{args.dataset}_{model_id_safe}__{args.perturb}" if args.perturb
         else f"view_{args.view}_{args.dataset}_{model_id_safe}"),
    )
    run(
        dataset_id=args.dataset, split=split, backend=args.backend, model=args.model,
        view=view_name, data_root=args.data_root, out_dir=out_dir, limit=args.limit,
        max_workers=args.max_workers, max_tokens=args.max_tokens,
        no_think=args.no_think,
        shuffle=args.shuffle, seed=args.seed, prompt_style=args.prompt_style,
        label_order=args.label_order,
    )


if __name__ == "__main__":
    main()
