#!/usr/bin/env python3
"""Build v2.1 SFT data (messages format for sft_train.py) — prompts byte-identical
to v21_llm_runner's zero-shot condition; completion = candidate label string.
care_pd restricted to its primary UPDRS_GAIT task."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v21_llm_runner import RENDER, flat_prompt  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--datasets", nargs="*", default=[
        "ataxia", "gmfcs", "parkinsonism", "pathogait", "asd_kinect", "care_pd"])
    args = ap.parse_args()
    for ds in args.datasets:
        droot = os.path.join(args.root, ds)
        recs = [json.loads(l) for l in open(os.path.join(droot, "records_slim.jsonl"))]
        for r in recs:
            r["label"] = None if r["label"] is None else str(r["label"])
        recs = [r for r in recs if r["label"] not in (None, "", "None")]
        if ds == "care_pd":
            recs = [r for r in recs if r["label_task"] == "UPDRS_GAIT"]
        summaries = {}
        for line in open(os.path.join(droot, "04_motion_summary.jsonl")):
            s = json.loads(line)
            summaries[s["sample_id"]] = s.get("text_en") or ""
        rend = RENDER.get(ds, {})
        label_vals = next(d["label_set"] for d in json.load(open(os.path.join(os.path.dirname(__file__), "..", "datasets.json")))["datasets"] if d["id"] == ds)
        if any(r["label"] not in label_vals for r in recs):
            raise ValueError(f"{ds}: label outside task contract")
        if any(not summaries.get(r["sample_id"], "").strip() for r in recs):
            raise ValueError(f"{ds}: missing model-visible evidence")
        cands = [rend.get(l, l) for l in label_vals]
        out_dir = os.path.join(args.out_root, ds)
        os.makedirs(out_dir, exist_ok=True)
        counts = {}
        for split in ("train", "val", "test"):
            rows = [r for r in recs if r["split"] == split]
            with open(os.path.join(out_dir, f"{split}.jsonl"), "w") as fh:
                for r in rows:
                    prompt = flat_prompt(summaries.get(r["sample_id"], ""), cands)
                    fh.write(json.dumps({"messages": [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": rend.get(r["label"], r["label"])},
                    ], "sample_id": r["sample_id"], "subject_id": str(r["subject_id"])}) + "\n")
            counts[split] = len(rows)
        json.dump({"dataset": ds, "labels": label_vals, "candidates": cands,
                   "counts": counts}, open(os.path.join(out_dir, "meta.json"), "w"), indent=1)
        print(f"[sftdata] {ds}: {counts} labels={len(cands)}", flush=True)


if __name__ == "__main__":
    main()
