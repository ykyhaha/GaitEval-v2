#!/usr/bin/env python
"""GaitEval v2.1 LLM runner — Phase 2 (zero-shot + controls) against a local vLLM server.

Conditions:
  zs           flat prompt over motion-summary text_en (labeled test rows)
  feat         named z-features rendered as text (from 03_features_raw_and_z.csv)
  lorder-rev   zs with reversed candidate order
  lorder-shuf1 zs with shuffled candidate order (seed 1)
  shufev       zs with summaries deranged across test rows (evidence decoupled from clip)
  noev         candidate labels only; deterministic -> one generation defines the run

care_pd uses only its UPDRS_GAIT task. The archived 12-class mixed-label
diagnostic is not supported as a common-protocol rerun.
"""
import argparse
import concurrent.futures as cf
import csv
import json
import os
import random
import re
from urllib import request as ur

MODEL = os.environ.get("NE_MODEL", "Qwen/Qwen2.5-7B-Instruct")

RENDER = {  # dataset -> label -> prompt-facing candidate string
    "gmfcs": {l: f"GMFCS level {l}" for l in "1234"},
    "care_pd": {l: f"UPDRS gait score {l}" for l in "0123"},
}


def norm(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def parse(raw, cands):
    """Boundary-anchored longest-match over candidate strings; returns index or -1."""
    text = norm(raw or "")
    best = None
    for i, c in enumerate(cands):
        needle = norm(c)
        pat = re.compile(r"(?<![a-z0-9])" + re.escape(needle) + r"(?![a-z0-9])")
        pos = -1
        for mt in pat.finditer(text):
            pos = mt.start()
        if pos >= 0:
            key = (pos, len(needle), -i)
            if best is None or key > best[0]:
                best = (key, i)
    return best[1] if best else -1


def flat_prompt(evidence, cands, evidence_kind="motion summary"):
    labels = "\n".join(f"- {c}" for c in cands)
    return (
        f"You are classifying a gait clip from a compact biomechanical {evidence_kind} "
        "derived from a skeleton sequence.\n\n"
        f"{evidence.strip()}\n\n"
        f"Task: based ONLY on the {evidence_kind} above, classify the gait into exactly "
        "one of the following classes:\n"
        f"{labels}\n\n"
        "Return only one label, written exactly as listed above."
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.expanduser("~/v21_text"))
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--condition", required=True,
                    choices=["zs", "feat", "featraw", "lorder-rev", "lorder-shuf1", "shufev", "noev"])
    ap.add_argument("--port", default=os.environ.get("PORT", "8000"))
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--care-pd-mixed", action="store_true")
    ap.add_argument("--max-workers", type=int, default=16)
    args = ap.parse_args()
    ds = args.dataset
    if args.care_pd_mixed:
        raise SystemExit("Archived mixed-label diagnostic is outside the six-dataset task contract.")
    droot = os.path.join(args.root, ds)

    recs = {}
    for line in open(os.path.join(droot, "records_slim.jsonl")):
        r = json.loads(line)
        r["label"] = None if r["label"] is None else str(r["label"])
        recs[r["sample_id"]] = r
    test = [r for r in recs.values() if r["split"] == "test" and r["label"] not in (None, "", "None")]
    if ds == "care_pd" and not args.care_pd_mixed:
        test = [r for r in test if r["label_task"] == "UPDRS_GAIT"]
    rend = RENDER.get(ds, {})
    if ds == "care_pd" and args.care_pd_mixed:
        rend = {}
    label_vals = json.load(open(os.path.join(os.path.dirname(__file__), "..", "datasets.json")))["datasets"]
    label_vals = next(r["label_set"] for r in label_vals if r["id"] == ds)
    cands = [rend.get(l, l) for l in label_vals]
    cand_of = {l: rend.get(l, l) for l in label_vals}

    summaries = {}
    for line in open(os.path.join(droot, "04_motion_summary.jsonl")):
        s = json.loads(line)
        summaries[s["sample_id"]] = s.get("text_en") or ""

    feats = {}
    if args.condition in ("feat", "featraw"):
        pref = "z__" if args.condition == "feat" else "raw__"
        head = ("Named biomechanical features (z-scored against the training reference):"
                if args.condition == "feat" else "Named biomechanical features:")
        fmt = "{:+.3f}" if args.condition == "feat" else "{:.4g}"
        with open(os.path.join(droot, "03_features_raw_and_z.csv")) as fh:
            rd = csv.reader(fh)
            hdr = next(rd)
            idx = {h: i for i, h in enumerate(hdr)}
            zcols = [(h[len(pref):], i) for i, h in enumerate(hdr) if h.startswith(pref)]
            for row in rd:
                lines = []
                for name, i in zcols:
                    v = row[i]
                    if v in ("", "nan", "None", "null"):
                        continue
                    lines.append(f"{name.replace('_', ' ')}: {fmt.format(float(v))}")
                feats[row[idx["sample_id"]]] = head + "\n" + "\n".join(lines)

    order = list(range(len(cands)))
    if args.condition == "lorder-rev":
        order = order[::-1]
    elif args.condition == "lorder-shuf1":
        rng = random.Random(1)
        rng.shuffle(order)
    cands_o = [cands[i] for i in order]

    shuf_map = {}
    if args.condition == "shufev":
        ids = [r["sample_id"] for r in test]
        rng = random.Random(0)
        d = ids[:]
        while True:  # derangement
            rng.shuffle(d)
            if all(a != b for a, b in zip(ids, d)):
                break
        shuf_map = dict(zip(ids, d))

    def call(prompt):
        req = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                          "temperature": 0,
                          "max_tokens": int(os.environ.get("NE_MAXTOK", "48"))}).encode()
        resp = ur.urlopen(ur.Request(f"http://localhost:{args.port}/v1/chat/completions", req,
                                     {"Content-Type": "application/json"}), timeout=300)
        return json.load(resp)["choices"][0]["message"]["content"]

    os.makedirs(args.out_dir, exist_ok=True)
    results = []
    if args.condition == "noev":
        labels_block = "\n".join(f"- {c}" for c in cands_o)
        prompt = ("You are classifying a gait clip. No motion evidence is available for this clip.\n\n"
                  "Task: classify the gait into exactly one of the following classes:\n"
                  f"{labels_block}\n\nReturn only one label, written exactly as listed above.")
        txt = call(prompt)
        pi = parse(txt, cands)
        for r in test:
            results.append({"sample_id": r["sample_id"], "subject_id": str(r["subject_id"]),
                            "true": r["label"], "pred": label_vals[pi] if pi >= 0 else None,
                            "raw_output": txt})
    else:
        def work(r):
            sid = r["sample_id"]
            if args.condition in ("feat", "featraw"):
                ev, kind = feats.get(sid, ""), "feature description"
            elif args.condition == "shufev":
                ev, kind = summaries.get(shuf_map[sid], ""), "motion summary"
            else:
                ev, kind = summaries.get(sid, ""), "motion summary"
            if not ev.strip():
                raise ValueError(f"Missing evidence for {sid}")
            txt = call(flat_prompt(ev, cands_o, kind))
            pi = parse(txt, cands)
            return {"sample_id": sid, "subject_id": str(r["subject_id"]), "true": r["label"],
                    "pred": label_vals[pi] if pi >= 0 else None, "raw_output": txt}
        with cf.ThreadPoolExecutor(args.max_workers) as ex:
            results = list(ex.map(work, test))

    with open(os.path.join(args.out_dir, "results.jsonl"), "w") as fh:
        for r in results:
            fh.write(json.dumps(r) + "\n")
    n = len(results)
    ok = [r for r in results if r["pred"] is not None]
    acc = sum(r["pred"] == r["true"] for r in ok) / max(n, 1)
    import collections
    li = {l: i for i, l in enumerate(label_vals)}
    yt = [li[r["true"]] for r in results]
    yp = [li[r["pred"]] if r["pred"] is not None else -1 for r in results]
    K = len(label_vals)
    f1s = []
    for k in range(K):
        tp = sum(1 for a, b in zip(yt, yp) if a == k and b == k)
        fp = sum(1 for a, b in zip(yt, yp) if a != k and b == k)
        fn = sum(1 for a, b in zip(yt, yp) if a == k and b != k)
        f1s.append(2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0)
    summ = {"dataset": ds, "condition": args.condition, "model": MODEL, "n": n,
            "n_unparsed": n - len(ok), "accuracy": round(acc, 4),
            "macro_f1": round(sum(f1s) / K, 4), "labels": label_vals,
            "pred_counts": dict(collections.Counter(r["pred"] or "UNPARSED" for r in results))}
    with open(os.path.join(args.out_dir, "summary.json"), "w") as fh:
        json.dump(summ, fh, indent=1)
    print(f"[V21] {ds}/{args.condition}: n={n} acc={acc:.4f} mf1={summ['macro_f1']:.4f} "
          f"unparsed={summ['n_unparsed']}", flush=True)


if __name__ == "__main__":
    main()
