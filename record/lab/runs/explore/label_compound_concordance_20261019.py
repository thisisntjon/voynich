"""EXPLORATORY exact label -> consecutive body-word concatenation concordance.
Published lead: MarcoP, Voynich Ninja thread2013 (2017). No novelty claim.
Strict letters only; uncertain tokens block matches; no crossing line boundaries.
Comma joins (uncertain spaces treated as absent); period separates words.
"""
from pathlib import Path
from collections import defaultdict,Counter
import re,json
ROOT=Path('.')
labels=[]; body=[]; sections={}
for raw in (ROOT/'data/ZL3b-n.txt').read_text(encoding='utf-8-sig').splitlines():
    h=re.match(r'<(f\d+[rv]\d*)>.*\$I=(\w)',raw)
    if h:sections[h[1]]=h[2]
    m=re.match(r'<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)',raw)
    if not m:continue
    page,line,typ=m[1],int(m[2]),m[3]
    txt=re.sub(r'<[^>]*>','',m[4]).replace(',','')
    ws=[w if re.fullmatch('[a-z]+',w) else None for w in re.split(r'[.\s]+',txt) if w]
    if 'L' in typ and len(ws)==1 and ws[0]:labels.append(dict(page=page,line=line,type=typ,word=ws[0]))
    if 'P' in typ:body.append((page,line,ws))
ng=defaultdict(list); exact=Counter()
for page,line,ws in body:
    exact.update(w for w in ws if w)
    for n in (2,3):
        for i in range(len(ws)-n+1):
            chunk=ws[i:i+n]
            if None in chunk:continue
            ng[''.join(chunk)].append(dict(page=page,line=line,word_index=i+1,parts=chunk))
matches=[]
for l in labels:
    occ=ng.get(l['word'],[])
    if not occ:continue
    matches.append(dict(**l,section=sections.get(l['page']),whole_body_count=exact[l['word']],split_occurrences=occ,own_page=[o for o in occ if o['page']==l['page']]))
summary=dict(label_instances=len(labels),matched_instances=len(matches),own_page_instances=sum(bool(r['own_page']) for r in matches),own_page_types=len({r['word'] for r in matches if r['own_page']}),pharma_own_page=[r for r in matches if r['section']=='P' and r['own_page']])
out=dict(status='EXPLORATORY',summary=summary,matches=matches)
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
