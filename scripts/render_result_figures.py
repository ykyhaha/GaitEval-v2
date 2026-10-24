#!/usr/bin/env python3
"""Regenerate six confusion figures and exact per-class/clinical tables from S predictions."""
import collections,json,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import cohen_kappa_score,mean_absolute_error
from audit_results import ROOT,DATASETS,read_rows,score

NAMES={'asd_kinect':'ASD-Kinect','ataxia':'ATAXIA','care_pd':'CARE-PD','gmfcs':'GMFCS','parkinsonism':'PARKINSONISM','pathogait':'PATHOGAIT'}
COND=[('zs','Zero-shot summary'),('feat','Zero-shot z-features'),('sft','LoRA-SFT summary')]
def esc(s):return str(s).replace('_',r'\_')
def table(label,caption,head,cols,body):
 return '\n'.join([r'\begin{table}[H]',r'\centering',r'\caption{'+caption+'}',r'\label{'+label+'}',r'\small',r'\begin{adjustbox}{max width=\textwidth}',r'\begin{tabular}{'+cols+'}',r'\toprule',head+r' \\',r'\midrule',*body,r'\bottomrule',r'\end{tabular}',r'\end{adjustbox}',r'\end{table}'])+'\n'
def main():
 figs=ROOT/'results/derived/figures';figs.mkdir(parents=True,exist_ok=True);tabs=ROOT/'results/derived/tables';tabs.mkdir(parents=True,exist_ok=True)
 binary=[];ordinal=[]
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42})
 for ds in DATASETS:
  full=[read_rows(ROOT/f'results/v21_runs/{ds}__{cond}/results.jsonl') for cond,_ in COND]
  labels=sorted({r['true'] for r in full[0]});invalid=any(r['pred'] not in labels for rows in full for r in rows)
  predlabels=labels+(['UNPARSED'] if invalid else []);perclass=[]
  fig,axes=plt.subplots(1,3,figsize=(11,3.4 if len(labels)<5 else 4.1),layout='constrained')
  for ax,rows,(co,title) in zip(axes,full,COND):
   mat=np.zeros((len(labels),len(predlabels)),dtype=int)
   for r in rows:mat[labels.index(r['true']),predlabels.index(r['pred']) if r['pred'] in labels else -1]+=1
   pct=mat/np.maximum(mat.sum(axis=1,keepdims=True),1)
   ax.imshow(pct,cmap='Blues',vmin=0,vmax=1)
   for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):ax.text(j,i,f'{mat[i,j]}\n{pct[i,j]:.0%}',ha='center',va='center',fontsize=7,color='white' if pct[i,j]>.52 else '#18344A')
   show=lambda x:x.replace('typically_developing','typical').replace('mimicked_ataxia','imitated ataxia').replace('_',' ')
   ax.set_xticks(range(len(predlabels)),[show(x) for x in predlabels],rotation=45,ha='right')
   ax.set_yticks(range(len(labels)),[show(x) for x in labels]);ax.set_xlabel('Predicted label');ax.set_ylabel('True label');ax.set_title(title)
   for k,label in enumerate(labels):
    tp=mat[k,k];support=mat[k].sum();predsum=mat[:,k].sum();rec=tp/support;precision=tp/predsum if predsum else 0;f1=2*precision*rec/(precision+rec) if precision+rec else 0
    perclass.append(f'{title} & {esc(label)} & {support} & {precision:.3f} & {rec:.3f} & {f1:.3f}'+r' \\')
   if len(labels)==2:
    positive={'asd_kinect':'ASD','ataxia':'mimicked_ataxia','parkinsonism':'severe'}[ds];pos=labels.index(positive);neg=1-pos;sen=mat[pos,pos]/mat[pos].sum();spe=mat[neg,neg]/mat[neg].sum()
    binary.append(f'{NAMES[ds]} & {title} & {esc(positive)} & {sen:.3f} & {spe:.3f} & {(sen+spe)/2:.3f}'+r' \\')
   if ds in ['gmfcs','care_pd']:
    yt=[int(r['true']) for r in rows];yp=[int(r['pred']) for r in rows]
    ordinal.append(f'{NAMES[ds]} & {title} & {score(rows)["macro_f1"]:.3f} & {mean_absolute_error(yt,yp):.3f} & {cohen_kappa_score(yt,yp,weights="quadratic"):.3f}'+r' \\')
  fig.savefig(figs/f'confusion_{ds}.pdf',bbox_inches='tight');fig.savefig(figs/f'confusion_{ds}.png',dpi=150,bbox_inches='tight');plt.close(fig)
  tex=table('tab:per_class_'+ds,r'\textbf{'+NAMES[ds]+r' per-class S results.} Precision, recall, and F1 are recomputed from committed predictions; all task classes are retained.',r'Condition & Class & Support & Precision & Recall & F1','llrrrr',perclass)
  (tabs/f'per_class_{ds}.tex').write_text(tex)
 (tabs/'binary_metrics.tex').write_text(table('tab:binary_metrics',r'\textbf{Binary S metrics.} Sensitivity is recall of the explicitly named positive class, and specificity is recall of its complement. Case-sensitive source label identities are preserved.',r'Dataset & Condition & Positive class & Sensitivity & Specificity & Balanced acc.','lllrrr',binary))
 (tabs/'ordinal_metrics.tex').write_text(table('tab:ordinal_metrics',r'\textbf{Ordinal S error structure.} MAE and quadratic-weighted $\kappa$ use the ordered numeric labels.',r'Dataset & Condition & Macro-F1 & MAE & Quadratic $\kappa$','llrrr',ordinal))
 print('Generated six prediction-backed confusion figures and eight per-class/structured tables.')
if __name__=='__main__':main()
