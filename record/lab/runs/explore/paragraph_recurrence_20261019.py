"""EXPLORATORY: adjacent-line exact-word recurrence across paragraph boundaries.
No segmentation model, no semantic or novelty claim. Uses existing ZL3b markers.
Circularly shift boundary mask within each page; retain actual line text/order.
This null does not control paragraph-position vocabulary or short final lines.
"""
from pathlib import Path
from collections import Counter, defaultdict
import re, json, hashlib
import numpy as np

SOURCE = Path('./data/ZL3b-n.txt')
pages = defaultdict(list)
sections = {}
for raw in SOURCE.read_text(encoding='utf-8-sig').splitlines():
    h = re.match(r'<(f\d+[rv]\d*)>.*\$I=(\w)', raw)
    if h:
        sections[h[1]] = h[2]
    m = re.match(r'<(f\d+[rv]\d*)\.(\d+),[^>]*P[^>]*>\s*(.*)', raw)
    if not m:
        continue
    body = m[3]
    start = '<%>' in body
    body = re.sub(r'<[^>]*>', '', body)
    # Retain token position; uncertain readings become None, not joined strings.
    words = [w if re.fullmatch('[a-z]+', w) else None for w in re.split(r'[.,\s]+', body) if w]
    pages[m[1]].append((int(m[2]), start, words))

freq = Counter(w for rows in pages.values() for _,_,ws in rows for w in ws if w)
top20 = set(w for w,n in freq.most_common(20))
out = {'status':'EXPLORATORY', 'source':str(SOURCE), 'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'results':[]}
rng = np.random.default_rng(20261019)
for trim in (0, 1, 2):
    for rare in (False, True):
        records = []
        for page, rows in pages.items():
            scores, bounds = [], []
            for (li,_,wa),(lj,s,wb) in zip(rows,rows[1:]):
                if lj != li+1:
                    continue
                aa = wa[trim:len(wa)-trim] if trim else wa
                bb = wb[trim:len(wb)-trim] if trim else wb
                a = Counter(w for w in aa if w and (not rare or w not in top20))
                b = Counter(w for w in bb if w and (not rare or w not in top20))
                if not a or not b:
                    continue
                scores.append(sum(n*b[w] for w,n in a.items()) / (sum(a.values())*sum(b.values())))
                bounds.append(s)
            x,mask = np.array(scores),np.array(bounds,dtype=bool)
            if mask.sum() >= 1 and (~mask).sum() >= 2:
                records.append((page,x,mask))
        for section in ('ALL','B','S','H'):
            rr = [r for r in records if section=='ALL' or sections.get(r[0])==section]
            if not rr:
                continue
            within = np.mean([x[~b].mean() for _,x,b in rr])
            across = np.mean([x[b].mean() for _,x,b in rr])
            observed = within-across
            null = []
            for _ in range(499):
                vals=[]
                for _,x,b in rr:
                    shifted=np.roll(b,int(rng.integers(len(b))))
                    vals.append(x[~shifted].mean()-x[shifted].mean())
                null.append(float(np.mean(vals)))
            row=dict(trim=trim,exclude_top20=rare,section=section,pages=len(rr),within=float(within),across=float(across),difference=float(observed),null_mean=float(np.mean(null)),p_upper=(1+sum(v>=observed for v in null))/500)
            out['results'].append(row)
            print(json.dumps(row),flush=True)
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
