"""Direct spectral crop, local research only. No sharpening, inpainting or OCR.
Coordinates chosen from the first-look full page, not optimized to a reading.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
src=Path('<local-path>');out=Path(__file__).parent
box=(1100,980,4100,1350)
bands=['MB535GN_004','MB365UV_007','WBUVO22_020','MB940IR_012']
canvas=Image.new('RGB',(1500,960),'white');meta=[]
for i,b in enumerate(bands):
 p=next(src.glob('*'+b+'*.tif'))
 with Image.open(p) as im:
  a=np.asarray(im.transpose(Image.Transpose.ROTATE_270).crop(box),dtype=np.float32)
 lo,hi=np.percentile(a,[1,99])
 display=Image.fromarray(np.uint8(np.clip((a-lo)/(hi-lo),0,1)*255)).resize((1500,185),Image.Resampling.LANCZOS)
 y=i*225
 ImageDraw.Draw(canvas).text((10,y+5),b+' | upright pixels '+str(box)+' | affine 1-99% stretch',fill='black')
 canvas.paste(display,(0,y+30));meta.append(dict(file=str(p),box=box,lo=float(lo),hi=float(hi)))
ImageDraw.Draw(canvas).text((10,910),'Lazarus Project / Chester F. Carlson Center for Imaging Science, RIT. Beinecke MS408 f17r. Local research.',fill='black')
canvas.save(out/'msi17_margin_20261019.png')
(out/'msi17_margin_20261019.json').write_text(json.dumps(meta,indent=2)+'\n')
