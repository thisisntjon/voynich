"""EXPLORATORY measured-band PCA. No inferred text, synthetic pixels or OCR.
PCA can amplify registration artefacts: compare any candidate stroke with raw bands.
Local derivatives credited to Lazarus Project / RIT, Beinecke MS408 f17r.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import cv2,numpy as np,json,os
cv2.setNumThreads(1)
src=Path('<local-path>');out=Path(__file__).parent
box=(1100,980,4100,1350)
bands=['MB535GN_004','MB365UV_007','MB450RB_001','MB470LB_002','MB505CN_003','MB570AM_005','MB625RD_006','MB700IR_008','MB735IR_009','MB780IR_010','WBUVO22_020']
arr=[];meta=[];ref=None
for b in bands:
 files=list(src.glob('*'+b+'*.tif'))
 if not files:meta.append(dict(band=b,excluded='missing'));continue
 with Image.open(files[0]) as im:a=np.asarray(im.transpose(Image.Transpose.ROTATE_270).crop(box),dtype=np.float32)
 lo,hi=np.percentile(a,[1,99]);a=np.clip((a-lo)/(hi-lo),0,1).astype(np.float32)
 if ref is None:
  ref=a.copy();shift=(0.,0.);response=1.
 else:shift,response=cv2.phaseCorrelate(ref,a,cv2.createHanningWindow((a.shape[1],a.shape[0]),cv2.CV_32F))
 row=dict(band=b,shift=list(shift),response=float(response),stretch=[float(lo),float(hi)])
 if max(abs(v) for v in shift)>3 or response<.1:
  row['excluded']='unreliable local alignment';meta.append(row);continue
 a=cv2.warpAffine(a,np.float32([[1,0,-shift[0]],[0,1,-shift[1]]]),(a.shape[1],a.shape[0]),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
 arr.append(a[4:-4,4:-4]);meta.append(row)
stack=np.stack(arr,axis=-1)
x=stack.reshape(-1,stack.shape[-1]);x=x-x.mean(axis=0)
sd=x.std(axis=0);x=x/np.maximum(sd,1e-6)
cov=x.T@x/len(x);vals,vecs=np.linalg.eigh(cov);order=np.argsort(vals)[::-1];vals=vals[order];vecs=vecs[:,order]
scores=(x@vecs[:,:6]).reshape(stack.shape[0],stack.shape[1],-1)
canvas=Image.new('RGB',(1500,6*220+55),'white')
for k in range(scores.shape[-1]):
 a=scores[:,:,k];lo,hi=np.percentile(a,[1,99]);im=Image.fromarray(np.uint8(np.clip((a-lo)/(hi-lo),0,1)*255)).resize((1500,181),Image.Resampling.LANCZOS)
 ImageDraw.Draw(canvas).text((8,k*220+5),f'PC{k+1} variance {vals[k]/sum(vals):.3f}; sign arbitrary; 1-99% display stretch',fill='black')
 canvas.paste(im,(0,k*220+30))
ImageDraw.Draw(canvas).text((8,6*220+10),'Lazarus Project / Chester F. Carlson Center for Imaging Science, RIT. Beinecke MS408 f17r. Local research.',fill='black')
canvas.save(out/'msi17_margin_pca_20261019.png')
(out/'msi17_margin_pca_20261019.json').write_text(json.dumps(dict(box=box,bands=meta,variance_fractions=(vals/vals.sum()).tolist(),loadings=vecs.tolist()),indent=2)+'\n')
print(json.dumps(dict(accepted=len(arr),bands=meta)))
