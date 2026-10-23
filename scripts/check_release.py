#!/usr/bin/env python3
"""Check all recorded metrics, fixed label sets, and parsing of genuine outputs."""
import importlib.util,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'code'))
from v21_llm_runner import parse,RENDER
m=importlib.util.spec_from_file_location('audit',R/'scripts/audit_results.py');a=importlib.util.module_from_spec(m);m.loader.exec_module(a)
errs=[];n=0
for ds in json.loads((R/'datasets.json').read_text())['datasets']:
 name=ds['id'];labels=ds['label_set'];c=[RENDER.get(name,{}).get(v,v) for v in labels]
 for condition in ds['common_conditions']:
  p=R/f'results/v21_runs/{name}__{condition}/results.jsonl'
  rows=a.read_rows(p)
  if sorted({r['true'] for r in rows})!=sorted(labels):errs.append(f'{name}/{condition}: label set')
  if len(rows)!=ds['n_test']:errs.append(f'{name}/{condition}: count')
  for r in rows:
   i=parse(r['raw_output'],c);pred=labels[i] if i>=0 else None
   if pred!=r['pred']:errs.append(f'{name}/{condition}: parser mismatch {r["sample_id"]}')
   n+=1
print(json.dumps({'records_checked':n,'errors':errs},indent=2))
if errs:raise SystemExit(1)
