"""EXPLORATORY spectral display of held f17r, not an inferred reading.
Sequential one-band reads; affine percentile stretch only; no generative processing.
Credit: Lazarus Project / Chester F. Carlson Center for Imaging Science at RIT;
Beinecke Rare Book & Manuscript Library MS408 f17r. Local research derivative.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
SRC=Path('<local-path>'); OUT=Path(__file__).parent
bands=['MB535GN_004','WBUVO22_020','MB940IR_012']
panels=[]; records=[]
for band in bands:
 p=next(SRC.glob('*'+band+'*.tif'))
 with Image.open(p) as im:
  im=im.transpose(Image.Transpose.ROTATE_270)
  # Marginalia location is checked from whole-page display before selecting a crop.
  small=np.asarray(im.resize((614,818),Image.Resampling.BILINEAR),dtype=np.float32)
 lo,hi=np.percentile(small,[1,99])
 a=np.uint8(np.clip((small-lo)/(hi-lo),0,1)*255)
 panel=Image.new('RGB',(614,858),'white');panel.paste(Image.fromarray(a).convert('RGB'),(0,40))
 ImageDraw.Draw(panel).text((12,10),band,fill='black')
 panels.append(panel);records.append(dict(file=str(p),orientation='rotate270',display_percentiles=[float(lo),float(hi)]))
canvas=Image.new('RGB',(1842,920),'white')
for i,p in enumerate(panels):canvas.paste(p,(614*i,0))
ImageDraw.Draw(canvas).text((12,875),'Local research display. Lazarus Project / Chester F. Carlson Center for Imaging Science, RIT. Beinecke MS408 f17r.',fill='black')
dest=OUT/'msi17_firstlook_20261019.png';canvas.save(dest)
(OUT/'msi17_firstlook_20261019.json').write_text(json.dumps(records,indent=2)+'\n')
print(dest)
