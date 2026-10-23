#!/usr/bin/env python3
"""acc / macro-F1 / Cohen's kappa / top-class share from a v21 results.jsonl (fixed-K, unparsed=error)."""
import json, sys, collections

def cell(path):
    rows = [json.loads(l) for l in open(path + "/results.jsonl")]
    labels = sorted({r["true"] for r in rows})
    li = {l: i for i, l in enumerate(labels)}
    yt = [li[r["true"]] for r in rows]
    yp = [li[r["pred"]] if r["pred"] in li else -1 for r in rows]
    n = len(rows)
    acc = sum(a == b for a, b in zip(yt, yp)) / n
    K = len(labels)
    f1 = []
    for k in range(K):
        tp = sum(a == k and b == k for a, b in zip(yt, yp))
        fp = sum(a != k and b == k for a, b in zip(yt, yp))
        fn = sum(a == k and b != k for a, b in zip(yt, yp))
        f1.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.0)
    # kappa over K+1 categories (unparsed = its own category, never in truth)
    cats = K + 1
    po = acc
    pt = collections.Counter(yt); pp = collections.Counter(yp)
    pe = sum((pt.get(c,0)/n)*(pp.get(c,0)/n) for c in range(cats))
    kappa = (po-pe)/(1-pe) if pe < 1 else 0.0
    top = max(collections.Counter(yp).values())/n
    return {"n": n, "acc": round(acc,4), "mf1": round(sum(f1)/K,4),
            "kappa": round(kappa,4), "top_share": round(top,2),
            "unparsed": sum(1 for v in yp if v < 0)}

if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(p.rstrip("/").split("/")[-1], json.dumps(cell(p)))
