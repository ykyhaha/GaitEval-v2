#!/usr/bin/env python3
"""Build SFT/RL chat data from the motion-summary view.

Each example is the EXACT zero-shot benchmark prompt (build_view_prompt flat,
leak-redacted) as the user turn, and the ground-truth class name as the assistant
turn. Training on this asks: can a fine-tuned LLM learn the motion-summary->class
mapping that it fails to do zero-shot (and that a RandomForest learns trivially)?

Writes <out>/<dataset>/{train,val,test}.jsonl with OpenAI-style messages, plus a
meta.json with the label set. Same prompt distribution as the zero-shot eval, so
the only change is the supervision.
"""
import os
import json
import argparse

from datasets import list_datasets
from view_run import _find_view_file, _load_view_items, build_view_prompt
import registry


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True,
                    choices=registry.dataset_ids())
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--prompt-style", default="flat", choices=["flat", "structured"])
    ap.add_argument("--view", default="motion_summary",
                    choices=["motion_summary", "feature_vector", "feature_vector_z",
                             "feature_vector_novff"])
    args = ap.parse_args()

    reg = list_datasets(args.data_root)
    meta = reg[args.dataset]
    label_map = {int(k): v for k, v in meta["label_map"].items()}

    # backward-compatible: motion_summary -> <out>/<ds>; other views -> <out>/<ds>_<view>
    sub = args.dataset if args.view == "motion_summary" else f"{args.dataset}_{args.view}"
    out_dir = os.path.join(args.out_root, sub)
    os.makedirs(out_dir, exist_ok=True)
    counts = {}
    for split in ("train", "val", "test"):
        # Resolve the frozen partition (GMFCS -> *_sd) exactly as view_run.py does,
        # so SFT trains on the same subject-disjoint split it is evaluated on.
        frozen = registry.split_name(args.dataset, split)
        if frozen != split:
            print(f"[frozen] {args.dataset}: {split} -> {frozen}")
        try:
            vp = _find_view_file(meta["dir"], frozen, args.view)
        except FileNotFoundError:
            print(f"[skip] no {frozen} {args.view} for {args.dataset}")
            continue
        items = _load_view_items(vp, frozen)
        path = os.path.join(out_dir, f"{split}.jsonl")
        n = 0
        with open(path, "w") as fh:
            for it in items:
                prompt = build_view_prompt(it["summary_text"], label_map, args.prompt_style)
                rec = {
                    "messages": [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": label_map[it["label_numeric"]]},
                    ],
                    "label": it["label_numeric"],
                    "label_name": label_map[it["label_numeric"]],
                    "id": it["id"],
                }
                fh.write(json.dumps(rec) + "\n")
                n += 1
        counts[split] = n
        print(f"[ok] {args.dataset}/{split}: {n} -> {path}")

    with open(os.path.join(out_dir, "meta.json"), "w") as fh:
        json.dump({"dataset": args.dataset, "label_map": label_map,
                   "n_classes": len(label_map), "counts": counts,
                   "ordinal": meta["ordinal"], "prompt_style": args.prompt_style}, fh, indent=2)
    print(f"[done] {args.dataset}: {counts}; classes={list(label_map.values())}")


if __name__ == "__main__":
    main()
