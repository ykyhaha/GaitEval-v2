"""Editable scientific figures in the supplied outlined / handwritten style.

No generated patient imagery or invented measurements. Resource images are
credited source assets; small measurement traces and icons are schematic.
Run from any directory: python figure_source/draw_figures.py
"""
from pathlib import Path
import json,math,shutil,io,os
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch,Rectangle,Circle,Ellipse,Polygon,FancyArrowPatch,PathPatch
from matplotlib.path import Path as MPath

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;ASSET=HERE/'assets';OUT=ROOT/'paper/figures'
REG=HERE/'fonts/ComicNeue-Regular.ttf';BOLD=HERE/'fonts/ComicNeue-Bold.ttf'
for f in [REG,BOLD]:fm.fontManager.addfont(str(f))
FONT=fm.FontProperties(family=['Comic Neue','DejaVu Sans']);FB=fm.FontProperties(family=['Comic Neue','DejaVu Sans'],weight='bold')
MPL_FONTS=Path(matplotlib.get_data_path())/'fonts/ttf'
SANS=fm.FontProperties(fname=MPL_FONTS/'DejaVuSans-Bold.ttf')
MONO=fm.FontProperties(fname=MPL_FONTS/'DejaVuSansMono.ttf')
plt.rcParams.update({'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','font.family':'Comic Neue','savefig.pad_inches':0})
INK='#171C20';GRAY='#687079';BLUE='#278CFA';CYAN='#40BDE8';ORANGE='#FB8A13';VIOLET='#A583F6';GREEN='#27B779';RED='#E05151'
PALE={'blue':'#EDF5FF','cyan':'#ECFAFE','orange':'#FFF3DF','violet':'#F4EFFF','green':'#EAF9EF','red':'#FFECEC'}

class Draw:
 def __init__(self,w,h,inches,name):
  self.w=w;self.h=h;self.name=name;self.k=inches*72/w
  self.f=plt.figure(figsize=(inches,inches*h/w));self.ax=self.f.add_axes([0,0,1,1]);self.ax.set(xlim=(0,w),ylim=(h,0));self.ax.axis('off')
 def text(self,x,y,s,size=20,color=INK,bold=False,font=None,ha='left',va='top',z=6):
  self.ax.text(x,y,s,fontsize=size*self.k,fontproperties=font or (FB if bold else FONT),color=color,ha=ha,va=va,linespacing=1.12,zorder=z)
 def box(self,x,y,w,h,fill='white',edge=INK,lw=2,r=12,dash=None,z=1):
  p=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={r}',facecolor=fill,edgecolor=edge,linewidth=lw*self.k,zorder=z)
  if dash:p.set_linestyle((0,dash))
  self.ax.add_patch(p);return p
 def rect(self,x,y,w,h,fill='white',edge=INK,lw=2,z=2):
  p=Rectangle((x,y),w,h,facecolor=fill,edgecolor=edge,linewidth=lw*self.k,zorder=z);self.ax.add_patch(p);return p
 def line(self,pts,color=INK,lw=2,dash=None,z=3):
  xx,yy=zip(*pts);self.ax.plot(xx,yy,color=color,lw=lw*self.k,ls='-' if not dash else (0,dash),solid_capstyle='round',solid_joinstyle='round',zorder=z)
 def arrow(self,pts,color=INK,lw=2.4,dash=None,head=14,z=5):
  if len(pts)>2:self.line(pts[:-1],color,lw,dash,z)
  p=FancyArrowPatch(pts[-2],pts[-1],arrowstyle='->',mutation_scale=head*self.k,color=color,lw=lw*self.k,shrinkA=0,shrinkB=0,zorder=z)
  if dash:p.set_linestyle((0,dash))
  self.ax.add_patch(p)
 def dot(self,x,y,r=4,fill=INK,edge=None,lw=1,z=5):self.ax.add_patch(Circle((x,y),r,facecolor=fill,edgecolor=edge or fill,lw=lw*self.k,zorder=z))
 def ellipse(self,x,y,w,h,fill='white',edge=INK,lw=2,z=4):self.ax.add_patch(Ellipse((x,y),w,h,facecolor=fill,edgecolor=edge,lw=lw*self.k,zorder=z))
 def polygon(self,pts,fill='white',edge=INK,lw=2,z=4):self.ax.add_patch(Polygon(pts,closed=True,facecolor=fill,edgecolor=edge,lw=lw*self.k,zorder=z))
 def curve(self,points,color=INK,lw=2,fill='none',z=4):
  codes=[MPath.MOVETO]+[MPath.CURVE4]*(len(points)-1);self.ax.add_patch(PathPatch(MPath(points,codes),facecolor=fill,edgecolor=color,lw=lw*self.k,zorder=z))
 def image(self,x,y,w,h,path,crop=None):
  im=Image.open(path).convert('RGB')
  if crop:im=im.crop(crop)
  iw,ih=im.size;s=min(w/iw,h/ih);ww,hh=iw*s,ih*s
  self.ax.imshow(im,extent=(x+(w-ww)/2,x+(w+ww)/2,y+(h+hh)/2,y+(h-hh)/2),zorder=2,interpolation='lanczos')
 def save(self):
  OUT.mkdir(exist_ok=True,parents=True)
  for ext in ['pdf','svg','png']:
   buffer=io.BytesIO();self.f.savefig(buffer,format=ext,dpi=450,facecolor='white');data=buffer.getvalue()
   if ext=='pdf':assert data.rstrip().endswith(b'%%EOF')
   if ext=='svg':assert data.rstrip().endswith(b'</svg>')
   if ext=='png':Image.open(io.BytesIO(data)).load();assert data[-8:]==b'IEND\xaeB`\x82'
   dest=OUT/f'{self.name}.{ext}';tmp=dest.with_suffix('.'+ext+'.tmp')
   with tmp.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
   os.replace(tmp,dest)
  dirfd=os.open(OUT,os.O_RDONLY);os.fsync(dirfd);os.close(dirfd)
  plt.close(self.f)

def person(d,x,y,s=1,color=CYAN,pose=0):
 d.dot(x+17*s,y+7*s,6*s,color,INK,1.6)
 d.box(x+9*s,y+17*s,16*s,22*s,color,INK,1.7,4*s,z=4)
 arms=[[(9,21),(2,31),(0,40)],[(25,21),(32,29),(38,31)]]
 legs=[[(12,39),(8,52),(2,62)],[(22,39),(27,51),(35,60)]]
 if pose%2:arms=[[(9,21),(1,24),(-3,19)],[(25,21),(30,31),(28,41)]];legs=[[(12,39),(18,52),(25,62)],[(22,39),(16,50),(5,58)]]
 for pts in arms+legs:d.line([(x+a*s,y+b*s) for a,b in pts],INK,2.8)
def skeleton(d,x,y,w,h,color=BLUE,pose=0,box=False):
 p=np.array([[.50,.02],[.50,.20],[.28,.23],[.18,.43],[.12,.58],[.72,.23],[.82,.40],[.88,.52],[.50,.52],[.34,.53],[.28,.75],[.18,.96],[.66,.53],[.78,.74],[.90,.92]])
 if pose%2:p[3:5]=[[.20,.35],[.13,.30]];p[6:8]=[[.78,.45],[.72,.63]];p[10:12]=[[.48,.76],[.62,.97]];p[13:15]=[[.55,.76],[.36,.96]]
 p=p*[w,h]+[x,y]
 edges=[(0,1),(1,2),(2,3),(3,4),(1,5),(5,6),(6,7),(1,8),(8,9),(9,10),(10,11),(8,12),(12,13),(13,14)]
 for a,b in edges:d.line([p[a],p[b]],color,2)
 for a in p:d.dot(*a,2.3,color)
 if box:d.rect(x-3,y-4,w+6,h+8,'none',color,1)
def film(d,x,y,w,h,asset,frames=4):
 d.rect(x,y,w,h,INK,INK,1)
 for xx in np.arange(x+5,x+w-5,15):
  d.rect(xx,y+3,9,4,'white','none',0);d.rect(xx,y+h-7,9,4,'white','none',0)
 d.image(x+4,y+11,w-8,h-22,asset)
def pageicon(d,x,y,s=1,fill=PALE['orange'],color=INK):
 d.polygon([(x,y),(x+26*s,y),(x+36*s,y+10*s),(x+36*s,y+47*s),(x,y+47*s)],fill,color,1.8)
 d.line([(x+26*s,y),(x+26*s,y+10*s),(x+36*s,y+10*s)],color,1.7,z=5)
 for yy,ww in [(18,22),(25,22),(32,17),(39,20)]:d.line([(x+7*s,y+yy*s),(x+(7+ww)*s,y+yy*s)],color,1.4,z=5)
def chip(d,x,y,s=1,fill='#BDE5FF'):
 d.box(x+4*s,y+5*s,42*s,38*s,fill,INK,2,7*s,z=4)
 for v in [12,24,36]:
  d.line([(x-2*s,y+v*s),(x+4*s,y+v*s)],INK,2);d.line([(x+46*s,y+v*s),(x+52*s,y+v*s)],INK,2)
 for u in [14,26,38]:
  d.line([(x+u*s,y-1*s),(x+u*s,y+5*s)],INK,2);d.line([(x+u*s,y+43*s),(x+u*s,y+49*s)],INK,2)
 for a,b in [((15,16),(26,23)),((26,23),(36,16)),((26,23),(17,34)),((26,23),(36,34))]:d.line([(x+a[0]*s,y+a[1]*s),(x+b[0]*s,y+b[1]*s)],INK,1.7,z=5)
 for a,b in [(15,16),(26,23),(36,16),(17,34),(36,34)]:d.dot(x+a*s,y+b*s,2.5*s,'white',INK,1.4)
def lock(d,x,y,s=1):
 d.curve([(x+5*s,y+14*s),(x+5*s,y-5*s),(x+27*s,y-5*s),(x+27*s,y+14*s)],INK,2)
 d.box(x,y+12*s,32*s,25*s,'#FFD791',INK,2,4*s,z=4);d.dot(x+16*s,y+23*s,2.4*s,INK);d.line([(x+16*s,y+23*s),(x+16*s,y+29*s)],INK,2)
def funnel(d,x,y,s=1,color=GREEN):
 d.polygon([(x,y),(x+44*s,y),(x+28*s,y+22*s),(x+28*s,y+37*s),(x+17*s,y+43*s),(x+17*s,y+22*s)],'#D9F4E4',INK,1.8)
 for a,c in [(10,BLUE),(22,ORANGE),(34,VIOLET)]:d.dot(x+a*s,y+7*s,2.7*s,c)
def trainicon(d,x,y,s=1):
 d.rect(x,y,37*s,29*s,'#D9F4E4',INK,1.7);d.line([(x-4*s,y+33*s),(x+41*s,y+33*s)],INK,2)
 for i,h in enumerate([10,17,12]):d.rect(x+(7+i*8)*s,y+(24-h)*s,5*s,h*s,[BLUE,ORANGE,GREEN][i],INK,.8)
def target(d,x,y,s=1,color=RED):
 for r in [15,9,3]:d.ellipse(x,y,r*2*s,r*2*s,'none',color,1.7)
 d.line([(x-20*s,y),(x+20*s,y)],color,1.1);d.line([(x,y-20*s),(x,y+20*s)],color,1.1)
def tokens(d,x,y,labels=('A','B','C','D'),colors=None,sz=24,gap=6):
 colors=colors or [BLUE,GREEN,ORANGE,VIOLET]
 for i,(a,c) in enumerate(zip(labels,colors)):
  d.box(x+i*(sz+gap),y,sz,sz,'white',c,1.8,4);d.text(x+i*(sz+gap)+sz/2,y+sz/2,a,sz*.68,c,True,ha='center',va='center')
def magnifier(d,x,y,s=1,color=CYAN):
 d.ellipse(x,y,24*s,24*s,'#F2FBFF',INK,2);d.line([(x+9*s,y+9*s),(x+23*s,y+23*s)],INK,4)
 d.line([(x+9*s,y+9*s),(x+23*s,y+23*s)],color,2)
def trace(d,x,y,w,h,kind=0,col=BLUE):
 xx=np.linspace(0,1,60);yy=np.sin(xx*2*np.pi)*(h*.3)
 if kind==1:yy+=np.sin(xx*10*np.pi)*h*.1
 d.line([(x,y+h),(x+w,y+h)],'#BFC8CF',1);d.line(list(zip(x+xx*w,y+h/2+yy)),col,2.3)
def tick(d,x,y,s=1,color=GREEN):d.line([(x,y+7*s),(x+6*s,y+13*s),(x+18*s,y-2*s)],color,4)
def cross(d,x,y,s=1,color=RED):d.line([(x,y),(x+11*s,y+11*s)],color,3);d.line([(x+11*s,y),(x,y+11*s)],color,3)
def header(d,x,y,label,color=BLUE):
 d.ax.text(x,y,label,fontsize=26*d.k,fontproperties=FB,color=color,ha='left',va='top',zorder=8,bbox={'facecolor':'white','edgecolor':'none','pad':1})

def overview():
 d=Draw(1360,650,7.0,'overview')
 # Equal status, equal card area, native population and task labels.
 d.box(7,30,663,310,'white',GREEN,3,18);header(d,23,4,'(a) Six resources, six native tasks',GREEN)
 ds=[('ASD-Kinect','asd_kinect','ASD / typical','provenance caveat',PALE['cyan']),('ATAXIA','ataxia','Normal / imitated','healthy volunteers',PALE['green']),('CARE-PD','care_pd','UPDRS gait score 0-3','Parkinson\'s cohort',PALE['orange']),('GMFCS','gmfcs','GMFCS I-IV','cerebral-palsy cohort',PALE['violet']),('PARKINSONISM','parkinsonism','Mild / severe','Parkinson\'s cohort',PALE['red']),('PATHOGAIT','pathogait','Six gait patterns','healthy, simulated gait',PALE['blue'])]
 for j,(name,key,task,pop,fill) in enumerate(ds):
  x=18+(j%3)*216;y=40+(j//3)*145
  d.box(x,y,205,135,fill,'#B9C4CC',1.5,9);d.text(x+102.5,y+5,name,22,INK,True,ha='center',font=SANS)
  crop=None
  if key=='care_pd':crop=(0,40,212,295)
  if key=='parkinsonism':crop=(8,0,146,269)
  d.image(x+8,y+31,189,65,ASSET/f'{key}.png',crop)
  d.text(x+102.5,y+99,task,19,INK,True,ha='center');d.text(x+102.5,y+119,pop,17.5,GRAY,ha='center')
 d.arrow([(672,184),(689,184)],GREEN,3.3)
 # Four views; z is contained in the named-feature tile, never a fifth modality.
 d.box(694,30,659,310,'white',VIOLET,3,18);header(d,709,4,'(b) One evidence view per run',VIOLET)
 views=[(707,43,'Raw coordinates',BLUE),(1031,43,'Normalized coordinates',CYAN),(707,190,'Motion summary',ORANGE),(1031,190,'Named features + z',GREEN)]
 for x,y,title,col in views:
  d.box(x,y,309,136,'white',col,2,10);d.text(x+12,y+7,title,23,col,True)
  if title=='Raw coordinates':
   skeleton(d,x+13,y+43,40,72,BLUE)
   for k,row in enumerate(json.loads((ASSET/'coordinate_excerpt.json').read_text())):d.text(x+65,y+47+k*20,' '.join(f'{v:+.2f}' for v in row),16.5,INK,font=MONO)
   d.text(x+65,y+109,'124-frame source',17,GRAY)
  elif title=='Normalized coordinates':
   d.line([(x+26,y+110),(x+92,y+110)],GRAY,1);d.line([(x+58,y+114),(x+58,y+38)],GRAY,1)
   skeleton(d,x+30,y+42,54,66,CYAN,1)
   d.text(x+108,y+48,'Center + scale + align',19)
   d.text(x+108,y+72,'32 frames / 12 joints',19,INK,True)
   d.text(x+108,y+105,'Coordinate subset probes',17,GRAY)
  elif title=='Motion summary':
   pageicon(d,x+17,y+42,.9,PALE['orange'])
   d.text(x+68,y+44,'Amplitude / asymmetry',19)
   d.text(x+68,y+69,'Stability / smoothness',19)
   d.text(x+68,y+101,'Fixed, label-free template',17,GRAY)
  else:
   for i,(hh,col2) in enumerate([(22,BLUE),(40,GREEN),(31,ORANGE)]):d.rect(x+17+i*18,y+105-hh,12,hh,col2,INK,1)
   d.text(x+83,y+45,'Supported measurements',19)
   d.text(x+83,y+70,'Train-only scaling: f → z',19,INK,True)
   d.text(x+83,y+103,'Shared columns: LLM / LR / SVM',16,GRAY)
 # Connected bus to three complementary evaluation questions.
 d.line([(337,342),(337,356),(1140,356),(1140,373)],GRAY,1.7)
 d.line([(1025,342),(1025,356)],GRAY,1.7)
 for xx in [226,679]:d.arrow([(xx,356),(xx,373)],GRAY,2)
 d.dot(337,356,3.4,GREEN);d.dot(1025,356,3.4,VIOLET)
 # Signal probe.
 x=7;y=379;d.box(x,y,437,214,'white',ORANGE,3,16);header(d,x+15,y+10,'(c) Is signal recoverable?',ORANGE)
 trainicon(d,x+21,y+53,1.12);d.text(x+80,y+55,'Same numerical evidence',21,INK,True)
 d.text(x+80,y+82,'Supervised LR / linear SVM',20)
 # Two visibly different labeled distributions: schematic, no fabricated scores.
 d.rect(x+21,y+119,96,61,PALE['orange'],'#C3CBD0',1)
 for a,b in [(10,40),(17,30),(28,45),(37,23),(55,38)]:d.dot(x+21+a,y+122+b,3,BLUE)
 for a,b in [(50,12),(63,22),(75,13),(82,29),(68,38)]:d.dot(x+21+a,y+122+b,3,ORANGE)
 d.line([(x+44,y+175),(x+108,y+121)],INK,1.6)
 d.arrow([(x+130,y+150),(x+155,y+150)],ORANGE,2.4)
 d.text(x+171,y+126,'Feature signal',22,INK,True)
 d.text(x+171,y+156,'vs. LLM evidence use',20)
 d.text(x+21,y+188,'Label-prior references anchor chance.',18,GRAY)
 # Evidence interventions.
 x=461;d.box(x,y,437,214,'white',BLUE,3,16);header(d,x+15,y+10,'(d) Does evidence matter?',BLUE)
 pageicon(d,x+22,y+54,.84,PALE['blue']);d.arrow([(x+61,y+77),(x+89,y+77)],BLUE)
 chip(d,x+98,y+53,.93)
 d.text(x+166,y+55,'No / shuffled evidence',20,INK,True)
 d.text(x+166,y+83,'Same task, altered evidence',18,GRAY)
 tokens(d,x+25,y+128,sz=26);d.arrow([(x+154,y+141),(x+200,y+141)],BLUE,2)
 tokens(d,x+215,y+128,('D','C','B','A'),[VIOLET,ORANGE,GREEN,BLUE],26)
 d.text(x+25,y+169,'Reverse / shuffle candidate order',20)
 d.text(x+25,y+192,'Keep the test records and labels fixed.',17.5,GRAY)
 # Adaptation and transfer have clearly scoped branches.
 x=915;d.box(x,y,438,214,'white',GREEN,3,16);header(d,x+15,y+10,'(e) What does adaptation learn?',GREEN)
 chip(d,x+20,y+57,.85);d.arrow([(x+73,y+77),(x+104,y+77)],GREEN)
 d.box(x+113,y+53,122,54,PALE['green'],GREEN,1.8,9);d.text(x+174,y+66,'LoRA-SFT',21,GREEN,True,ha='center')
 d.arrow([(x+239,y+77),(x+272,y+77)],GREEN);target(d,x+300,y+77,.75,GREEN)
 d.text(x+22,y+117,'All six: in-distribution summary SFT',19,INK,True)
 d.line([(x+22,y+149),(x+414,y+149)],'#BEDACC',1.2,(4,3))
 d.text(x+23,y+160,'ATAXIA',20,INK,True);d.arrow([(x+122,y+174),(x+240,y+174)],ORANGE,2.5)
 d.arrow([(x+240,y+181),(x+122,y+181)],ORANGE,2.5);d.text(x+252,y+161,'PATHOGAIT',20,INK,True)
 d.text(x+23,y+190,'Transfer probe: normal vs. abnormal',17.5,GRAY)
 # Bottom scoring rail uses no invented data or outcomes.
 d.box(7,607,1346,38,'#F0F4F7','#9DAAB3',1.5,9)
 d.text(23,616,'Six-dataset shared suite: 6 × 7 conditions',20,INK,True)
 d.text(1335,616,'Accuracy   •   fixed-label macro-F1   •   κ   •   per-class / participant checks',19,INK,ha='right')
 d.save()

def methods():
 d=Draw(680,910,3.35,'methods')
 # Pose sequence and split contract.
 d.box(7,23,666,137,'white',VIOLET,3,17);header(d,20,4,'1  Pose source + participant split',VIOLET)
 film(d,22,49,333,88,ROOT/'evidence/qualitative/gmfcs_zs_fail_sft_fix.png')
 d.text(22,139,'Recorded keypoints',17.8,GRAY);d.text(197,138,r'$X\in\mathbb{R}^{T\times J\times C}$',19,GRAY)
 d.line([(373,46),(373,143)],'#D8CBDD',1.4,(4,3))
 for j,(label,col,xx) in enumerate([('train',GREEN,394),('val.',ORANGE,486),('test',BLUE,578)]):
  person(d,xx+8,49,.60,col,j);d.text(xx+23,98,label,19,col,True,ha='center')
  for k in range(3):d.rect(xx+k*19,126,14,13,col,'white',.5)
 d.text(395,143,'Transform statistics from training only',16.5,GRAY)
 d.arrow([(340,163),(340,183)],VIOLET,2.5)
 # Deterministic feature group with mini explanatory plots and explicit role mapping.
 d.box(7,186,666,145,'white',ORANGE,3,17);header(d,21,174,'2  Map joints → deterministic measurements',ORANGE)
 for j,(name,col) in enumerate([('Range',BLUE),('Asymmetry',GREEN),('Stability',VIOLET),('Smoothness',ORANGE)]):
  x=24+j*164;d.box(x,217,145,98,'white','#D8D1C8',1.3,8);d.text(x+72.5,221,name,20,col,True,ha='center')
  if j==0:
   trace(d,x+16,253,111,32,0,col);d.arrow([(x+111,253),(x+111,285)],col,1.5,head=9);d.arrow([(x+111,285),(x+111,253)],col,1.5,head=9)
   d.text(x+72,293,'max − min',18,ha='center')
  elif j==1:
   d.rect(x+25,258,32,28,'#BDE8D1',GREEN,1.4);d.rect(x+87,246,32,40,'#BDE5FF',BLUE,1.4)
   d.text(x+41,287,'Left',17,GREEN,ha='center');d.text(x+102,287,'Right',17,BLUE,ha='center')
  elif j==2:
   d.polygon([(x+48,250),(x+72,241),(x+96,250),(x+84,276),(x+61,276)],PALE['violet'],INK,1.5)
   d.line([(x+70,242),(x+70,286)],VIOLET,1.3,(3,2));d.arrow([(x+35,280),(x+112,280)],VIOLET,1.4,head=9)
   d.text(x+73,294,'trunk / pelvis',16.5,ha='center')
  else:
   trace(d,x+16,251,111,36,1,col);d.text(x+72,295,'mean |Δ³p|',18,ha='center')
 d.text(24,315,'Keep supported joint roles; exclude capture-quality terms in the shared suite.',17.5,GRAY)
 d.arrow([(340,334),(340,351)],ORANGE,2.5)
 # Evidence rendering and train-only statistics: features feed two downstream routes.
 d.box(7,356,666,132,'white',CYAN,3,17);header(d,21,343,'3  Render one input view',CYAN)
 d.box(24,388,299,85,PALE['cyan'],CYAN,1.8,9);pageicon(d,39,404,.73,PALE['cyan'])
 d.text(82,398,'Numerical feature values',20,INK,True);d.text(82,427,r'$z=(f-\mu_{\mathrm{train}})/\sigma_{\mathrm{train}}$',19);d.text(82,452,'Fitted once on training records',16.5,GRAY)
 d.box(347,388,309,85,PALE['orange'],ORANGE,1.8,9);pageicon(d,361,404,.73,PALE['orange'])
 d.text(405,398,'Deterministic summary',20,INK,True);d.text(405,427,'Numbers + fixed descriptors',18.5);d.text(405,452,'No answer label / identity fields',16.5,GRAY)
 # Numeric bypass to matched supervised references.
 d.dot(171,474,3.4,GREEN);d.arrow([(171,475),(171,500),(70,500),(70,755)],GREEN,2.4)
 d.text(18,597,'same',17,GREEN);d.text(18,615,'features',17,GREEN)
 d.arrow([(303,475),(303,499),(502,499),(502,508)],CYAN,2.5)
 d.line([(502,490),(502,499)],ORANGE,2.2);d.dot(502,499,3,CYAN)
 # Model-visible evidence and interventions, all six datasets.
 d.box(94,514,579,135,'white',BLUE,3,17);header(d,111,502,'4  Evidence + candidate classes',BLUE)
 d.box(111,548,216,80,PALE['blue'],'#AECDEB',1.5,8)
 d.text(122,554,'[selected evidence view]',17.8,INK,True);tokens(d,124,589,sz=25)
 d.text(354,549,'Zero-shot controls',19,BLUE,True)
 d.text(354,573,r'$\varnothing\qquad e_i\longrightarrow e_{\pi(i)}$',20)
 d.text(354,601,'Candidate-order controls',18.5,BLUE,True)
 tokens(d,354,624,('D','C','B','A'),[VIOLET,ORANGE,GREEN,BLUE],19,4)
 d.text(460,625,'reverse / shuffle',16.5,GRAY)
 # Two LLM paths, neither an agent nor a hidden reasoning evaluator.
 d.arrow([(391,651),(391,667),(246,667),(246,680)],BLUE,2.5)
 d.arrow([(391,667),(542,667),(542,680)],BLUE,2.5);d.dot(391,667,3.2,BLUE)
 d.box(114,685,264,71,PALE['blue'],BLUE,2,10);chip(d,127,698,.73)
 d.text(180,694,'Qwen2.5-7B (ZS)',20,BLUE,True);d.text(180,722,'Frozen; temperature 0',18)
 d.box(398,685,275,71,PALE['violet'],VIOLET,2,10);chip(d,410,698,.73,fill='#E0D2FF')
 d.text(462,694,'Summary LoRA-SFT',20,VIOLET,True);d.text(462,722,'r = 16 / 3 epochs',18)
 # References have a distinct input path and no prompt/control input.
 d.box(7,761,179,69,PALE['green'],GREEN,2,10);trainicon(d,17,778,.72)
 d.text(55,770,'LR / SVM',21,GREEN,True);d.text(55,797,'Signal probe',18)
 d.arrow([(246,758),(246,770)],BLUE,2.4);d.arrow([(541,758),(541,770)],VIOLET,2.4)
 d.box(204,775,469,55,'white','#89939C',2,10)
 d.text(219,784,'Parse the last complete candidate mention',18,INK,True)
 d.text(219,807,'No match → invalid → error (never dropped)',17.5,RED)
 # All scores use the same held-out record/label identity.
 d.arrow([(96,833),(96,847),(340,847),(340,859)],GREEN,2.1)
 d.arrow([(440,833),(440,847),(340,847)],BLUE,2.1)
 d.box(7,862,666,43,'#F1F5F8','#9CA8B1',1.7,9)
 d.text(340,870,'Accuracy / macro-F1 / κ · per-class errors · participant checks',18,INK,True,ha='center')
 d.save()

if __name__=='__main__':
 overview();methods();print('Wrote editable SVG, embedded-font PDF and high-resolution PNG for both figures.')
