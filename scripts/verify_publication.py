"""Verify the published eight-page snapshot, static downloads, and displayed scores."""
from pathlib import Path
import hashlib,json,re,html
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
import fitz
R=Path(__file__).resolve().parents[1]
meta=json.loads((R/'audit/current_manuscript.json').read_text())
for path,expected in meta['files_sha256'].items():
 actual=hashlib.sha256((R/path).read_bytes()).hexdigest();assert actual==expected,path
main=fitz.open(R/'paper/main.pdf');supp=fitz.open(R/'paper/supplementary_standalone.pdf')
assert len(main)==11 and main[8].get_text().startswith('References')
assert 'Conclusion' in main[7].get_text()
assert len(re.findall(r'\\bibitem',(R/'paper/references_frozen.bbl').read_text()))==67
assert all('??' not in p.get_text() for p in main)
assert all('??' not in p.get_text() for p in supp)
text='\n'.join(p.get_text() for p in main)
assert [n for n in range(1,7) if f'Table {n}.' in text]==list(range(1,7))
assert 'Table 7.'not in text
for path in ['submission/01586_main_cameraready.pdf','submission/01586_main_camera_ready_preparation.pdf','docs/files/01586_main_cameraready.pdf','docs/files/01586_main_camera_ready_preparation.pdf','website/dist/files/01586_main_cameraready.pdf','website/dist/files/01586_main_camera_ready_preparation.pdf']:
 assert (R/path).read_bytes()==(R/'paper/main.pdf').read_bytes(),path
for path in ['submission/01586_supp.pdf','docs/files/01586_supp.pdf','website/dist/files/01586_supp.pdf']:
 assert (R/path).read_bytes()==(R/'paper/supplementary_standalone.pdf').read_bytes(),path
for p in (R/'website/dist').rglob('*'):
 if p.is_file():assert p.read_bytes()==(R/'docs'/p.relative_to(R/'website/dist')).read_bytes(),p
points=json.loads((R/'results/derived/audit_report.json').read_text());index={(r['dataset'],r['condition']):r for r in points['metrics']}
refs=json.loads((R/'results/references_task_matched.json').read_text());data=json.loads((R/'docs/data.json').read_text())
assert len(data['datasets'])==6
for d in data['datasets']:
 ds=d['id'];assert d['n']==index[ds,'zs']['n'] and d['subjects']==index[ds,'zs']['subjects']
 for field,c in [('summary','zs'),('features','feat'),('sft','sft')]:assert abs(d[field]-index[ds,c]['macro_f1'])<1e-12
 assert d['lr']==refs[ds]['lr_balanced']['mf1'] and d['svm']==refs[ds]['svm_balanced']['mf1']
# Main Table 4 is the website's same-record comparison; do not substitute other test populations.
source=(R/'paper/sec/4_evaluation_conditions.tex').read_text();table=source.split(r'\label{tab:shared_results}',1)[1].split(r'\end{tabular*}',1)[0]
byname={d['name']:d for d in data['datasets']}
for line in table.splitlines():
 parts=line.split('&');d=byname.get(parts[0].strip())
 if not d:continue
 for col,key in [(3,'summary'),(4,'features'),(5,'sft'),(6,'lr'),(7,'svm')]:
  value=float(re.findall(r'[-+]?\d*\.\d+',parts[col])[0]);assert f'{value:.3f}'==f'{d[key]:.3f}',(d['name'],key)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['src','href'] and v:self.links.append(v)
for page in ['index.html','sources.html']:
 parser=Links();parser.feed((R/'docs'/page).read_text())
 for link in parser.links:
  u=urlparse(link)
  if u.scheme or not u.path:continue
  assert (R/'docs'/unquote(u.path)).exists(),(page,link)
assert 'Kaiyuan Yang' in (R/'docs/index.html').read_text()
assert 'Author metadata and outstanding'not in (R/'docs/index.html').read_text()
report={'status':'passed','body_pages':8,'references_start_page':9,'main_pdf_pages':len(main),'supplement_pdf_pages':len(supp),'main_tables':6,'reference_items':67,'shared_prediction_files':points['prediction_files'],'shared_cells':points['common_cells'],'source_files_verified':len(meta['files_sha256']),'website_data_matches_main_table_4':True,'download_aliases_match':True,'static_mirrors_match':True,'broken_local_links':0,'model_execution_performed':False}
(R/'audit/publication_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
