"""EXPLORATORY concordance: exact recurring phrases in physical star-led entries.
Uses existing s100 stars and s45 alignment; no snapping to paragraph markers.
Entry assignments are provisional, not independently verified readings.
"""
from pathlib import Path
from collections import defaultdict,Counter
import csv,json,re
ROOT=Path('.')
rows=defaultdict(list)
for raw in (ROOT/'data/ZL3b-n.txt').read_text(encoding='utf-8-sig').splitlines():
    m=re.match(r'<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)',raw)
    if not m:continue
    body=re.sub(r'<[^>]*>','',m[4])
    ws=[w if re.fullmatch('[a-z]+',w) else None for w in re.split(r'[.,\s]+',body) if w]
    rows[m[1]].append((int(m[2]),m[3],ws))
stars=defaultdict(list)
with (ROOT/'runs/s100/star_classes.tsv').open(encoding='utf-8') as f:
    for r in csv.DictReader(f,delimiter='\t'): stars[r['folio']].append(r)
entries=[]; skipped=[]
for page,ss in stars.items():
    g=json.loads((ROOT/f'runs/s45/pages/{page}.json').read_text())
    mapping={int(d):grp['loci'] for grp in g['alignment'] for d in grp['det']}
    starts=[]
    for s in ss:
        d=int(s['nearest_line_idx'])-1
        loc=mapping.get(d,[])
        if len(loc)!=1:
            skipped.append((page,int(s['star_idx']),loc));continue
        starts.append((int(loc[0]),int(s['star_idx'])))
    starts=sorted(set(starts))
    for j,(start,star) in enumerate(starts):
        end=starts[j+1][0] if j+1<len(starts) else len(rows[page])
        if not 0<=start<end<=len(rows[page]):continue
        tokens=[]
        for line,typ,ws in rows[page][start:end]:
            if 'P' not in typ:continue
            tokens.extend((w,line,k+1) for k,w in enumerate(ws))
        entries.append(dict(page=page,star=star,start_line=rows[page][start][0],tokens=tokens))
freq=Counter(w for e in entries for w,_,_ in e['tokens'] if w)
grams=defaultdict(list)
for ei,e in enumerate(entries):
    ts=e['tokens']
    for n in range(3,9):
        for i in range(len(ts)-n+1):
            words=tuple(t[0] for t in ts[i:i+n])
            if None in words:continue
            grams[words].append((ei,i))
found=[]
for words,occs in grams.items():
    if len({entries[ei]['page'] for ei,i in occs})<2:continue
    found.append(dict(words=list(words),n=len(words),min_word_frequency=min(freq[w] for w in words),occurrences=[dict(page=entries[ei]['page'],star=entries[ei]['star'],line=entries[ei]['tokens'][i][1],word=entries[ei]['tokens'][i][2],context=' '.join(t[0] or '?' for t in entries[ei]['tokens'][max(0,i-4):i+len(words)+4])) for ei,i in occs]))
found.sort(key=lambda r:(-r['n'],r['min_word_frequency'],-len(r['occurrences'])))
output=dict(status='EXPLORATORY',entry_count=len(entries),ambiguous_star_mappings=skipped,cross_page_ngrams_by_length=dict(Counter(r['n'] for r in found)),matches=found)
Path(__file__).with_suffix('.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in output.items() if k!='matches'}))
for r in found[:15]: print(json.dumps(r))
