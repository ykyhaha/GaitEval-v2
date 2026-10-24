import csv,json,re
from pathlib import Path
from sklearn.metrics import accuracy_score,f1_score,cohen_kappa_score
R=Path(__file__).resolve().parent
def rows(p):return [json.loads(l) for l in (R/p).read_text().splitlines() if l.strip()]
def score(rs):
 y=[r['true_label'] for r in rs];p=[r['pred_label'] for r in rs]
 return {'n':len(rs),'accuracy':accuracy_score(y,p),'macro_f1':f1_score(y,p,average='macro',labels=sorted(set(y)),zero_division=0),'kappa':cohen_kappa_score(y,p),'invalid':sum(x==-1 for x in p)}
splits={s:list(csv.DictReader((R/f'splits/gmfcs_{s}_sd.tsv').open(),delimiter='\t')) for s in ['train','val','test']}
people={s:{r['patient_id'] for r in rs} for s,rs in splits.items()}
out={'gmfcs_corrected_split':{'clips':{s:len(rs) for s,rs in splits.items()},'subjects':{s:len(v) for s,v in people.items()},'overlap':{a+'_'+b:sorted(people[a]&people[b]) for a,b in [('train','val'),('train','test'),('val','test')]}}}
gs=rows('predictions/v1/cr_sft_gmfcs_sd_results.jsonl')
out['gmfcs_corrected_sft']=score(gs)
out['gmfcs_corrected_sft']['exact_test_id_match']={r['id'] for r in gs}=={'test_sd_'+r['sample_index'] for r in splits['test']}
out['gmfcs_corrected_sft']['unique_ids']=len({r['id'] for r in gs})
oldgm={r['id']:r for r in rows('predictions/v1/sft-qwen7b_gmfcs/results.jsonl')}
index={r['sample_index']:r for r in splits['test']}
out['gmfcs_corrected_sft']['truth_matches_original_test']=all(oldgm[index[r['id'].removeprefix('test_sd_')]['orig_split']+'_'+index[r['id'].removeprefix('test_sd_')]['orig_sample_index']]['true_label']==r['true_label'] for r in gs)
orig=rows('predictions/v1/sft-feat-qwen7b_pathological/results.jsonl'); new=rows('predictions/v1/cr_sft_pathogait_novff_results.jsonl')
out['pathogait_with_vff']=score(orig);out['pathogait_without_vff']=score(new)
o={r['id']:r for r in orig};n={r['id']:r for r in new}
out['pathogait_same_test']={'same_ids':set(o)==set(n),'same_true_labels':all(r['true_label']==o[r['id']]['true_label'] for r in new),'old_unique_ids':len(o),'new_unique_ids':len(n)}
out['pathogait_delta_mf1']=out['pathogait_without_vff']['macro_f1']-out['pathogait_with_vff']['macro_f1']
qwen72=rows('predictions/v1/full_motionsum_pathological_qwen72b/results.jsonl')
out['pathogait_qwen72_correct_rounding']=score(qwen72)
assert round(out['pathogait_qwen72_correct_rounding']['macro_f1'],3)==.055
def anchored(raw,lm):
 text=re.sub(r'\s+',' ',raw.strip().lower());best=None
 for k,name in lm.items():
  for m in re.finditer(r'(?<![a-z0-9])'+re.escape(name.lower())+r'(?![a-z0-9])',text):
   key=(m.start(),len(name),-k)
   if best is None or key>best[0]:best=(key,k)
 return best[1] if best else -1
glm={0:'GMFCS I',1:'GMFCS II',2:'GMFCS III',3:'GMFCS IV'}
plm={}
for r in orig+new:
 if r['pred_label']>=0 and r['raw_output'].strip() in ['normal gait','antalgic gait','lurching gait','steppage gait','stiff-legged gait','Trendelenburg gait','trendelenburg gait']:
  plm[r['pred_label']]=r['raw_output'].strip()
out['pathogait_decoded_label_map']=plm
out['gmfcs_raw_parser_disagreements']=sum(anchored(r['raw_output'],glm)!=r['pred_label'] for r in gs)
out['pathogait_raw_parser_disagreements']=sum(anchored(r['raw_output'],plm)!=r['pred_label'] for r in orig+new)
qual=json.loads((R/'qualitative/qualitative_examples_source.json').read_text())
qchecks={}
for key,ds,rid,runs in [('gmfcs_zs_fail_sft_fix','gmfcs','test_22',[('full_motionsum_gmfcs_qwen72b','zs_raw'),('sft-qwen7b_gmfcs','sft_raw')]),('pathogait_zs_fail','pathological','test_290',[('full_motionsum_pathological_qwen72b','pred_raw')]),('ataxia_sft_success_minority','ataxia','test_11',[('full_motionsum_ataxia_qwen72b','zs_raw'),('sft-qwen7b_ataxia','sft_raw')])]:
 q=qual[key];qchecks[key]={}
 for run,field in runs:
  rec=next(r for r in rows(f'predictions/v1/{run}/results.jsonl') if r['id']==rid)
  qchecks[key][field+'_matches_raw_prediction']=q[field]==rec['raw_output']
  qchecks[key]['truth_numeric']=rec['true_label']
out['qualitative_crosschecks']=qchecks
prepared=json.loads((R/'qualitative/matched_cases_prepared.json').read_text())
gcase=next(r for r in prepared if r['dataset']=='gmfcs')
actual=next(r for r in gs if r['id']==gcase['record_id'])
out['gmfcs_case_after_corrected_training']={'record_id':gcase['record_id'],'truth':gcase['ground_truth_evaluation_only'],'corrected_raw_output':actual['raw_output'],'prepared_output_matches':actual['raw_output']==gcase['actual_output'],'old_source_output':qual['gmfcs_zs_fail_sft_fix']['sft_raw'],'old_success_caption_not_reused':actual['raw_output']!=qual['gmfcs_zs_fail_sft_fix']['sft_raw']}
out['prepared_prompts_redacted']=all(all(m.group(1).strip()=='[REDACTED]' for m in re.finditer(r'(?im)\b(?:label|sample_index):\s*([^|\n]+)',r['summary_redacted'])) for r in prepared)
assert all(not x for x in out['gmfcs_corrected_split']['overlap'].values())
assert out['gmfcs_corrected_sft']['exact_test_id_match'] and out['gmfcs_corrected_sft']['truth_matches_original_test']
assert out['pathogait_same_test']['same_ids'] and out['pathogait_same_test']['same_true_labels']
assert abs(out['gmfcs_corrected_sft']['macro_f1']-.25853028769390884)<1e-12
assert abs(out['pathogait_without_vff']['macro_f1']-.631640891013)<1e-12
assert out['gmfcs_raw_parser_disagreements']==out['pathogait_raw_parser_disagreements']==0
assert out['gmfcs_case_after_corrected_training']['prepared_output_matches']
assert out['gmfcs_case_after_corrected_training']['old_success_caption_not_reused']
assert out['prepared_prompts_redacted']
(R/'metrics_verified.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
