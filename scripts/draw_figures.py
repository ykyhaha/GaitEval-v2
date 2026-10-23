from pathlib import Path
import numpy as np, json, shutil
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,Circle,FancyArrowPatch,Rectangle,Polygon
V=Path(__file__).resolve().parents[1];A=V/'figures/assets';A.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'pdf.fonttype':42,'svg.fonttype':'none'})
C=['#4674AB','#5F8F78','#A47F49','#687BAC','#A66F88','#4F9299'];ink='#233348'; muted='#627083';line='#D4DCE5'
class D:
 def __init__(self,w,h,width,name):
  self.w=w;self.h=h;self.name=name;self.f=plt.figure(figsize=(width,width*h/w));self.a=self.f.add_axes([0,0,1,1]);self.a.set(xlim=(0,w),ylim=(h,0));self.a.axis('off');self.k=width*72/w
 def text(self,x,y,s,fs=16,c=ink,b=False,ha='left',va='top'):
  self.a.text(x,y,s,fontsize=fs*self.k,color=c,weight='bold' if b else 'normal',ha=ha,va=va,linespacing=1.2)
 def box(self,x,y,w,h,fc='#F4F7FA',ec=line,r=8,lw=.7):
  self.a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={r}',facecolor=fc,edgecolor=ec,linewidth=lw))
 def ln(self,x,y,xx,yy,c=line,lw=.8,ls='-'):self.a.plot([x,xx],[y,yy],c=c,lw=lw,ls=ls,solid_capstyle='round')
 def arr(self,x,y,xx,yy,c=muted):self.a.add_patch(FancyArrowPatch((x,y),(xx,yy),arrowstyle='-|>',mutation_scale=7,lw=.9,color=c))
 def image(self,x,y,w,h,p):
  im=Image.open(p);iw,ih=im.size;s=min(w/iw,h/ih);ww=iw*s;hh=ih*s;self.a.imshow(im,extent=(x+(w-ww)/2,x+(w+ww)/2,y+(h+hh)/2,y+(h-hh)/2),zorder=3)
 def save(self):
  for ext in ['pdf','svg','png']:self.f.savefig(V/f'figures/{self.name}.{ext}',dpi=450,facecolor='white')
  plt.close(self.f)
def skeleton(d,p,x,y,w,h,col=C[0],edges=None):
 p=np.array(p)[:,:2];lo=p.min(0);hi=p.max(0);p=(p-(hi+lo)/2)*min(w/(hi[0]-lo[0]),h/(hi[1]-lo[1]))+[x+w/2,y+h/2]
 if edges is None:edges=[(0,1),(1,2),(2,3),(1,4),(4,5),(5,6),(1,7),(7,8),(8,9),(7,10),(10,11),(11,12)]
 for a,b in edges:d.ln(*p[a],*p[b],col,1)
 d.a.scatter(p[:,0],p[:,1],s=3,c=col,zorder=4)
icon=np.array([[0,0],[0,1],[-.7,1.2],[-1,2],[.7,1.1],[1.2,1.6],[1.4,2.1],[0,2.3],[-.5,3.3],[-.8,4.2],[.5,3.2],[1,4.1],[1.2,4.2]])
# Prepared, credited crops and recorded skeletons live in figures/assets.
# They are resource illustrations, not paired model-input examples.
# Wide overview: six equal cards, sparse view icons, diagnostic axes.
d=D(1000,435,7.0,'overview');d.text(8,4,'a',19,b=True);d.text(32,4,'Six resources · native tasks · participant-aware evaluation',18,b=True)
names=['ASD-Kinect','ATAXIA','CARE-PD','GMFCS','PARKINSONISM','PATHOGAIT'];ids=['asd_kinect','ataxia','care_pd','gmfcs','parkinsonism','pathogait'];tasks=['ASD / typical','Normal / imitated','UPDRS gait 0–3','Severity I–IV','Binary severity','Six simulated patterns']
for j,(n,ds,task) in enumerate(zip(names,ids,tasks)):
 x=8+j*165;d.box(x,35,155,150,'#F8FAFC',line,7);d.text(x+77.5,44,n,15,C[j],True,ha='center');d.image(x+8,67,139,85,A/f'{ds}.png');d.text(x+77.5,164,task,12,muted,ha='center');d.ln(x+77.5,187,x+77.5,196,C[j])
d.ln(85,196,910,196);d.arr(500,196,500,211)
d.text(8,216,'b',19,b=True);d.text(32,216,'Pose evidence, one view per run',18,b=True)
for j,(n,col) in enumerate(zip(['Coordinates','Normalized pose','Motion summary','Named features'],C)):
 x=36+j*242;d.box(x,246,220,78,'white',line,6);d.text(x+110,252,n,15,col,True,ha='center')
 if j==0:
  raw=np.array(json.loads((A/'coordinate_excerpt.json').read_text()))
  for k,row in enumerate(raw):d.text(x+12,276+12*k,'[ '+'  '.join(f'{v:+.2f}' for v in row)+' ]',11,muted)
 elif j==1:
  for k in range(3):skeleton(d,icon,x+32+k*48,276,32,40,col)
 elif j==2:
  for k,ww in enumerate([145,177,130,160]):d.ln(x+18,278+k*10,x+18+ww,278+k*10,col,1)
 else:
  for k,h in enumerate([15,31,22,36,12]):d.box(x+20+k*19,313-h,12,h,col,col,1,0)
  d.text(x+128,284,'f → z',20,col,True)
d.arr(500,327,500,341)
d.text(8,345,'c',19,b=True);d.text(32,345,'What information exists?  What does the model use?',18,b=True)
for j,(n,sub,col) in enumerate([('Same-feature LR / SVM','Recoverable supervised signal',C[1]),('LLMs + evidence controls','Grounding and order sensitivity',C[0]),('Adaptation + scoped transfer','Dataset-specific recovery',C[4])]):
 x=36+j*322;d.box(x,376,300,49,'#F5F8FB',line,6);d.text(x+150,384,n,15,col,True,ha='center');d.text(x+150,405,sub,11.8,muted,ha='center')
d.save()
# Detailed single-column methods, built from vector primitives.
d=D(480,650,3.35,'methods');d.text(12,5,'From pose evidence to a controlled label decision',17,b=True)
d.box(12,34,456,98,'#F4F7FB');d.text(26,42,'1  Source sequence + subject split',16,C[0],True)
for k in range(4):skeleton(d,icon,28+k*54,68,35,50,C[0])
d.ln(252,65,252,118);d.text(268,72,'TRAIN',12,C[1],True);d.text(268,94,'TEST',12,C[4],True)
for k in range(4):d.box(336+k*22,70,16,13,C[1],C[1],2,0)
for k in range(2):d.box(336+k*22,97,16,13,C[4],C[4],2,0)
d.arr(240,134,240,150)
d.box(12,151,456,110,'#F7FAF8');d.text(26,159,'2  Deterministic measurements',16,C[1],True)
for j,(txt,col) in enumerate(zip(['Range','Asymmetry','Variability','Smoothness'],[C[0],C[4],C[1],C[2]])):
 x=28+j*112;xx=np.linspace(x,x+88,60)
 if j==0:
  yy=203+10*np.sin(np.linspace(0,2*np.pi,60));d.a.plot(xx,yy,color=col,lw=1.1)
  d.ln(x+72,193,x+85,193,col);d.ln(x+72,213,x+85,213,col);d.ln(x+80,193,x+80,213,col)
 elif j==1:
  d.a.plot(xx,203+9*np.sin(np.linspace(0,2*np.pi,60)),color=col,lw=1.1)
  d.a.plot(xx,203+4*np.sin(np.linspace(0,2*np.pi,60)),color=C[0],lw=1.1,ls='--')
 elif j==2:
  rng=np.random.default_rng(4);d.a.scatter(x+rng.uniform(3,85,20),203+rng.normal(0,5,20),s=2,c=col,alpha=.65)
  d.ln(x,190,x+88,190,col,.5,'--');d.ln(x,216,x+88,216,col,.5,'--')
 else:
  yy=203+7*np.sin(np.linspace(0,2*np.pi,60))+3*np.sin(np.linspace(0,14*np.pi,60));d.a.plot(xx,yy,color=col,lw=1.1)
 d.ln(x,222,x+88,222);d.text(x+44,236,txt,12,col,ha='center')
d.arr(240,263,240,279)
d.text(26,277,'3  Render one input view',16,C[2],True)
for x,title in [(12,'Named values → train z-score'),(248,'Fixed summary template')]:
 d.box(x,302,220,82,'white',line,6);d.text(x+110,309,title,12,C[2],True,ha='center')
 if x==12:
  for k,h in enumerate([18,31,24,38,13]):d.box(x+25+k*29,372-h,16,h,C[2],C[2],1,0)
 else:
  for k,w in enumerate([169,145,175,118]):d.ln(x+18,336+k*11,x+18+w,336+k*11,C[1],1)
d.arr(122,386,122,407);d.arr(358,386,358,407)
d.box(12,408,456,87,'#F8F6FA');d.text(26,416,'4  Evidence + candidate labels',16,C[4],True)
for j,s in enumerate(['A','B','C','D']):
 x=28+j*48;d.box(x,446,34,25,'white',C[4],5);d.text(x+17,458,s,13,C[4],True,ha='center',va='center')
d.text(250,446,'No / shuffled evidence',12,muted);d.text(250,466,'Reverse / shuffle order',12,muted)
d.arr(170,497,170,507)
# Numeric features bypass text prompts to supervised references.
d.ln(465,238,475,238,C[1]);d.ln(475,238,475,542,C[1]);d.arr(475,542,469,542,C[1])
for x,title,sub,col in [(12,'Zero-shot LLM','Parse candidate label',C[0]),(170,'LoRA-SFT','Train → parse label',C[4]),(328,'Matched LR / SVM','Same feature columns',C[1])]:
 d.box(x,512,140,61,'#F5F8FA',line,6);d.text(x+70,523,title,13,col,True,ha='center');d.text(x+70,548,sub,10.5,muted,ha='center');d.arr(x+70,575,x+70,589)
d.box(12,591,456,49,'#EEF3F8');d.text(240,600,'Accuracy / macro-F1 / κ',15,ink,True,ha='center');d.text(240,621,'Participant-cluster uncertainty · class-wise errors',11,muted,ha='center');d.save()
for n in ['overview','methods']:
 for ext in ['pdf','png','svg']:shutil.copy2(V/f'figures/{n}.{ext}',V/f'paper/figures/{n}.{ext}')
print('overview and methods: PDF / SVG / PNG')
