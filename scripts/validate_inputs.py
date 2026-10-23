#!/usr/bin/env python3
"""Validate the external S input contract before inference/training.
Stops on missing evidence, inconsistent task labels, and subject leakage.
"""
import argparse,csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(root):
 report={}
 for ds in json.loads((ROOT/'datasets.json').read_text())['datasets']:
  name=ds['id'];p=root/name
  for n in ds['required_external_inputs']:
   if not (p/n).is_file():raise ValueError(f'{name}: missing {n}')
  records=[json.loads(l) for l in (p/'records_slim.jsonl').read_text().splitlines() if l.strip()]
  if name=='care_pd':records=[r for r in records if r.get('label_task')=='UPDRS_GAIT']
  records=[r for r in records if str(r.get('label')) in ds['label_set']]
  if not records:raise ValueError(f'{name}: no eligible records')
  groups={s:{str(r['subject_id']) for r in records if r['split']==s} for s in ['train','val','test']}
  for a,b in [('train','test'),('train','val'),('val','test')]:
   if groups[a]&groups[b]:raise ValueError(f'{name}: {a}/{b} participant overlap')
  ids=[r['sample_id'] for r in records]
  if len(set(ids))!=len(ids):raise ValueError(f'{name}: duplicate sample ids')
  summaries={r['sample_id']:r.get('text_en','') for r in map(json.loads,(p/'04_motion_summary.jsonl').read_text().splitlines())}
  if any(not summaries.get(i,'').strip() for i in ids):raise ValueError(f'{name}: missing summary')
  with (p/'03_features_raw_and_z.csv').open() as f:rows=list(csv.DictReader(f))
  columns=list(rows[0]) if rows else []
  forbidden=['valid_frame_fraction','clip_length','valid_frames','frame_count']
  if any(any(q in c for q in forbidden) for c in columns):raise ValueError(f'{name}: capture-quality feature in S inputs')
  if not any(c.startswith('z__') for c in columns):raise ValueError(f'{name}: no z-features')
  feature_ids={r['sample_id'] for r in rows}
  if not set(ids)<=feature_ids:raise ValueError(f'{name}: missing feature record')
  counts={s:sum(r['split']==s for r in records) for s in groups}
  if len(groups['test'])!=ds['n_test_subjects']:raise ValueError(f'{name}: test participant count differs from paper')
  if counts['test']!=ds['n_test'] or counts['train']!=ds['n_train']:raise ValueError(f'{name}: counts differ from paper contract')
  report[name]={'counts':counts,'subjects':{s:len(v) for s,v in groups.items()},'overlap':[]}
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args()
 print(json.dumps(validate(a.root),indent=2))
