#!/usr/bin/env python3
"""Recompute committed prediction metrics; validate counts, sample alignment and summaries.

No source inputs, models, GPU, or third-party Python packages are required.
"""
import collections,csv,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATASETS=['asd_kinect','ataxia','care_pd','gmfcs','parkinsonism','pathogait']
TASK_LABELS={d['id']:d['label_set'] for d in json.loads((ROOT/'datasets.json').read_text())['datasets']}
COMMON=['zs','feat','sft','lorder-rev','lorder-shuf1','shufev','noev']
def read_rows(path):return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
def score(rows, labels=None):
 labels=sorted(labels if labels is not None else {r['true'] for r in rows});n=len(rows)
 if not n:raise ValueError('Cannot score empty predictions')
 if any(r['true'] not in labels for r in rows):raise ValueError('Target outside fixed task label set')
 acc=sum(r['true']==r['pred'] for r in rows)/n;f=[]
 for label in labels:
  tp=sum(r['true']==label and r['pred']==label for r in rows)
  fp=sum(r['true']!=label and r['pred']==label for r in rows)
  fn=sum(r['true']==label and r['pred']!=label for r in rows)
  f.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
 yt=collections.Counter(r['true'] for r in rows);yp=collections.Counter(r['pred'] for r in rows)
 pe=sum(yt[k]*yp[k] for k in labels)/n**2
 return dict(n=n,subjects=len({r['subject_id'] for r in rows}),accuracy=acc,macro_f1=sum(f)/len(f),kappa=(acc-pe)/(1-pe),invalid=sum(r['pred'] not in labels for r in rows),top_share=max(yp.values())/n)
def main():
 output=ROOT/'results/derived';output.mkdir(exist_ok=True)
 errors=[];records=[];ids={};class_counts={}
 for path in sorted((ROOT/'results/v21_runs').glob('*/results.jsonl')):
  run=path.parent.name;ds,condition=run.split('__',1);rows=read_rows(path);metric=score(rows, TASK_LABELS[ds] if condition!='zs_mixed' else None)
  summary=json.loads((path.parent/'summary.json').read_text())
  for a,b in [('n','n'),('accuracy','accuracy'),('macro_f1','macro_f1'),('invalid','n_unparsed')]:
   if round(metric[a],4)!=summary[b]:errors.append(f'{run}: {a} != summary')
  sample_set={(r['sample_id'],r['subject_id'],r['true']) for r in rows}
  if len(sample_set)!=len(rows):errors.append(f'{run}: duplicate sample records')
  if condition!='zs_mixed':
   if ds in ids and ids[ds]!=sample_set:errors.append(f'{run}: test-set mismatch')
   ids[ds]=sample_set
  if condition=='zs':class_counts[ds]=dict(collections.Counter(r['true'] for r in rows))
  records.append(dict(dataset=ds,condition=condition,**metric,source=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 for ds in DATASETS:
  for cond in COMMON:
   if not (ROOT/f'results/v21_runs/{ds}__{cond}/results.jsonl').exists():errors.append(f'missing shared cell {ds}/{cond}')
 report={'prediction_files':len(records),'common_cells':len(DATASETS)*len(COMMON),'all_summaries_match':not errors,'identical_test_records_within_dataset':not any('test-set mismatch' in e for e in errors),'class_counts':class_counts,'errors':errors,'metrics':records}
 (output/'audit_report.json').write_text(json.dumps(report,indent=2))
 with (output/'metrics_all_runs.csv').open('w',newline='') as fh:
  writer=csv.DictWriter(fh,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
 with (output/'shared_six_dataset_metrics.csv').open('w',newline='') as fh:
  writer=csv.DictWriter(fh,fieldnames=list(records[0]));writer.writeheader();writer.writerows(r for r in records if r['condition'] in COMMON)
 print(json.dumps({k:v for k,v in report.items() if k not in ['metrics','class_counts']},indent=2))
 if errors:sys.exit(1)
if __name__=='__main__':main()
