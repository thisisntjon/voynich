"""EXPLORATORY unfitted-label page link, quire/hand/section page permutations.
Exact glyph string, ignoring spaces inside each body line; uncertainty blocks.
No glyph substitutions, fitted segmentation, physical boundaries or semantics inferred.
"""
from pathlib import Path
from collections import defaultdict
import re,json
import numpy as np
ROOT=Path('.')
meta={}; labs=defaultdict(set); bodies=defaultdict(list); exact=defaultdict(set)
for raw in (ROOT/'data/ZL3b-n.txt').read_text(encoding='utf-8-sig').splitlines():
 h=re.match(r'<(f\d+[rv]\d*)>\s+<!(.*)',raw)
 if h:meta[h[1]]=dict(re.findall(r'\$(\w)=(\S+)',h[2]))
 m=re.match(r'<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)',raw)
 if not m:continue
 page,typ,txt=m[1],m[3],re.sub('<[^>]*>','',m[4])
 if 'L' in typ:
  word=txt.replace(',','').strip()
  if re.fullmatch('[a-z]+',word):labs[page].add(word)
 if 'P' in typ:
  ws=[w if re.fullmatch('[a-z]+',w) else '|' for w in re.split('[.\s]+',txt.replace(',','')) if w]
  bodies[page].append(''.join(ws));exact[page].update(w for w in ws if w!='|')
groups=defaultdict(list)
for p in sorted(labs):
 if bodies[p]:groups[tuple(meta[p].get(k,'?') for k in ('Q','H','I'))].append(p)
groups={k:v for k,v in groups.items() if len(v)>=3}
rng=np.random.default_rng(20261019);out=[]
for minlen in (5,6,7):
 for mode in ('whole_word','glyphstream'):
  gs=[];examples=[]
  for key,pp in groups.items():
   pp=[p for p in pp if any(len(w)>=minlen for w in labs[p])]
   if len(pp)<3:continue
   matrix=np.zeros((len(pp),len(pp)))
   for i,p in enumerate(pp):
    words=sorted(w for w in labs[p] if len(w)>=minlen)
    for j,q in enumerate(pp):
     matches=[w for w in words if (w in exact[q] if mode=='whole_word' else any(w in line for line in bodies[q]))]
     matrix[i,j]=len(matches)/len(words)
     if i==j:examples.extend(dict(page=p,word=w,whole_word=w in exact[p]) for w in matches)
   gs.append((pp,matrix))
  if not gs:continue
  n=sum(len(pp) for pp,m in gs)
  obs=sum(np.trace(m) for pp,m in gs)/n
  null=[sum(m[np.arange(len(pp)),rng.permutation(len(pp))].sum() for pp,m in gs)/n for _ in range(999)]
  row=dict(min_length=minlen,mode=mode,pages=n,groups=len(gs),observed=float(obs),null_mean=float(np.mean(null)),null_q99=float(np.quantile(null,.99)),p_upper=(1+sum(x>=obs for x in null))/1000,examples=examples)
  out.append(row);print(json.dumps({k:v for k,v in row.items() if k!='examples'}))
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
