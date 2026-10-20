import json,re,glob,os,csv,collections,unicodedata
rows=json.load(open('stage/catalogue_rows.json'))
C='ctx'
docs=[p for p in glob.glob(C+'/**/*',recursive=True) if os.path.isfile(p) and re.search(r'\.(md|yaml|txt|tsv)$',p) and 'held_files' not in p and 'page-facts' not in p and 'folio_evidence' not in p]
lines=[]
for p in docs:
    for i,l in enumerate(open(p,encoding='utf-8',errors='replace')):
        lines.append((p[len(C)+1:],i+1,l))
low=[l[2].lower() for l in lines]
IDRE=re.compile(r'\b((?:F|H|X|O|L|D|P)-\d{2,3}|c-\d{3})\b')
STOP=set('the and voynich manuscript anon anonymous unknown editor review from with what this that rene'.split())
def surname(a):
    a=a.split(';')[0].strip()
    if not a: return ''
    if ',' in a: s=a.split(',')[0]
    else: s=a.split()[-1] if a.split() else ''
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    s=re.sub(r'[^a-z\-\']','',s)
    return '' if len(s)<4 or s in STOP else s
idx_year=collections.defaultdict(list)
for k,l in enumerate(low):
    for y in set(re.findall(r'\b(1[5-9]\d\d|20[0-2]\d)\b',l)): idx_year[y].append(k)
out=[]
for r in rows:
    keys=[]
    if r['doi']: keys.append(('doi',r['doi'].lower()))
    if r.get('arxiv'): keys.append(('arxiv',r['arxiv']))
    for m in re.findall(r'zenodo\.(\d{6,9})',r['doi']+' '+r['url']): keys.append(('zenodo',m))
    hits=[]
    for kind,k in keys:
        for j,l in enumerate(low):
            if k in l: hits.append((kind,j))
    s=surname(r['authors']); y=str(r['year'] or '')[:4]
    tw=[w for w in re.findall(r'[a-z]{6,}',(r['title'] or '').lower()) if w not in ('voynich','manuscript','manuscrit','analysis','language','through')][:8]
    if s and re.match(r'\d{4}$',y):
        for j in idx_year.get(y,[]):
            if re.search(r'\b'+re.escape(s)+r'\b',low[j]):
                win=' '.join(low[max(0,j-3):j+4])
                hits.append(('author_year_title' if any(w in win for w in tw) else 'author_year',j))
    if not hits: continue
    files=collections.Counter(); ids=collections.Counter(); kinds=set(h[0] for h in hits); strong=bool(kinds-{'author_year','author_year_title'})
    for kind,j in hits:
        f,n,l=lines[j]; files[f"{f}:{n}"]+=1
        for jj in range(max(0,j-2),min(len(lines),j+3)):
            if lines[jj][0]==f:
                for i in IDRE.findall(lines[jj][2]): ids[i]+=1
    out.append(dict(id=r['id'],match=('exact_id' if strong else ('author_year_title' if 'author_year_title' in kinds else 'author_year_only')),n_lines=len(set(j for _,j in hits)),project_ids=' '.join(sorted(ids)),where=' '.join(list(files)[:8])))
json.dump(out,open('stage/crosswalk.json','w'))
print(len(out),collections.Counter(o['match'] for o in out)); print(sum(1 for o in out if o['project_ids']))
