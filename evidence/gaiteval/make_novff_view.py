#!/usr/bin/env python3
"""Camera-ready A4/E4: derive a feature_vector view with valid_frame_fraction removed.

Reads each split's <split>_feature_vector.jsonl and writes
<split>_feature_vector_novff.jsonl with the 'valid_frame_fraction: ...' line stripped
from summary_text. Everything else (ids, labels, ordering) is unchanged, so the SFT
data builder and view_run treat it as a first-class view.
"""
import argparse, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registry
from datasets import list_datasets

LINE = re.compile(r"^valid_frame_fraction:.*\n?", re.M)

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True)
ap.add_argument("--data-root", required=True)
args = ap.parse_args()
meta = list_datasets(args.data_root)[args.dataset]
from view_run import _find_view_file
for base in ("train", "val", "test"):
    split = registry.split_name(args.dataset, base)
    src = _find_view_file(meta["dir"], split, "feature_vector")
    dst = os.path.join(os.path.dirname(src), f"{split}_feature_vector_novff.jsonl")
    n, hit = 0, 0
    with open(src) as fi, open(dst, "w") as fo:
        for line in fi:
            r = json.loads(line)
            t2 = LINE.sub("", r["summary_text"])
            hit += (t2 != r["summary_text"])
            r["summary_text"] = t2
            fo.write(json.dumps(r) + "\n")
            n += 1
    print(f"[novff] {split}: {n} rows, vff removed in {hit}", flush=True)
    assert hit == n, f"vff line missing in {n-hit} rows of {src}"
