import json,re,csv,collections,os,unicodedata,glob
rows=json.load(open('stage/catalogue_rows.json'))
cw={o['id']:o for o in json.load(open('stage/crosswalk.json'))}
held=list(csv.DictReader(open('ctx/held_files.tsv',encoding='utf-8'),delimiter='\t'))
docs=[h for h in held if re.search(r'\.(pdf|djvu|txt|html?|xml|zip|doc|docx|epub|ods|xlsx|xlsm)$',h['path'],re.I) and not re.search(r'/(word-coordinates|papers/rozanova_2608|timm-schinner-generator|controls_raw|cremma|gaskell-bowern|bowern-lindemann|yale_scans|herbals_|controls_tabular_ruled|s127_picture/sources/voynich_nu_raw)/',h['path'])]
# README context per filename
ctxlines=[]
for p in glob.glob('ctx/data/**/*.md',recursive=True)+glob.glob('ctx/data/**/*.tsv',recursive=True)+glob.glob('ctx/data/**/*.json',recursive=True):
    if 'facts.tsv' in p or 'folio_evidence' in p: continue
    ctxlines+= [l for l in open(p,encoding='utf-8',errors='replace')]
def ids_in(s):
    s=s.lower(); out=set()
    for m in re.findall(r'(?<![\d.])(\d{4}\.\d{4,5})(?![\d])',s): out.add('ax:'+m)
    for m in re.findall(r'zenodo[ ._/:a-z]*?(\d{7,9})',s): out.add('zn:'+m)
    for m in re.findall(r'(10\.\d{4,9}/[^\s|,;)\]`"]+)',s): out.add('doi:'+m.rstrip('.'))
    return out
docidx=collections.defaultdict(set)
for h in docs:
    fn=h['path'].split('/')[-1]; stem=re.sub(r'\.(pdf|txt|html?|zip|xml)$','',fn)
    ks=ids_in(h['path'])
    for l in ctxlines:
        if fn in l or (len(stem)>8 and stem in l): ks|=ids_in(l)
    for k in ks: docidx[k].add(h['path'])
def norm(s): return unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower()
def surname(a):
    a=a.split(';')[0].strip(); s=a.split(',')[0] if ',' in a else (a.split()[-1] if a.split() else '')
    return re.sub(r'[^a-z]','',norm(s))
fnidx=[(h['path'],norm(h['path'].split('/')[-1])) for h in docs]
for r in rows:
    paths=set()
    if r['doi']: paths|=docidx.get('doi:'+r['doi'].lower(),set())
    if r.get('arxiv'): paths|=docidx.get('ax:'+r['arxiv'],set())
    for m in re.findall(r'zenodo\.(\d{7,9})',r['doi']+' '+r['url']): paths|=docidx.get('zn:'+m,set())
    s=surname(r['authors']); y=str(r['year'])[:4]
    if len(s)>=4 and re.match(r'\d{4}$',y) and r['relevance'] in ('core','curated_bibliography'):
        tw=[w for w in re.findall(r'[a-z]{5,}',norm(r['title'])) if w not in ('voynich','manuscript')]
        for p,f in fnidx:
            if s in f and y in f: paths.add(p)
    r['local_path']=' '.join(sorted(paths)[:6])
    o=cw.get(r['id'])
    if o:
        lab={'exact_id':'cited (DOI/arXiv/Zenodo id found)','author_year_title':'likely cited (author+year+title word)','author_year_only':'possibly cited (author+year only; unverified)'}[o['match']]
        r['project_status']=f"{lab}; ids: {o['project_ids'] or '-'}; where: {o['where']}"
    else: r['project_status']='not yet used'
    r['project_ids']=o['project_ids'] if o else ''
cols=['id','type','relevance','authors','year','title','venue','doi','arxiv','url','oa_status','oa_url','license','local_path','topic_tags','claim_summary','project_status','sources','n_sources','source_ids']
os.makedirs('out',exist_ok=True)
def clean(v): return str(v if v is not None else '').replace('\t',' ').replace('\n',' ').replace('\r',' ')
with open('out/catalogue.tsv','w',encoding='utf-8',newline='\n') as f:
    f.write('\t'.join(cols)+'\n')
    for r in rows: f.write('\t'.join(clean(r.get(c,'')) for c in cols)+'\n')
with open('out/catalogue_abstracts.jsonl','w') as f:
    for r in rows:
        if r.get('abstract'): f.write(json.dumps({'id':r['id'],'title':r['title'],'abstract':r['abstract']},ensure_ascii=False)+'\n')
# crosswalk tsv
with open('out/catalogue_to_findings.tsv','w',encoding='utf-8',newline='\n') as f:
    f.write('catalogue_id\tmatch\tproject_ids\twhere\tyear\tauthors\ttitle\n')
    rid={r['id']:r for r in rows}
    for i,o in sorted(cw.items()):
        r=rid[i]; f.write('\t'.join(clean(x) for x in [i,o['match'],o['project_ids'],o['where'],r['year'],r['authors'][:80],r['title'][:200]])+'\n')
json.dump(rows,open('stage/catalogue_final.json','w'),ensure_ascii=False)
print('rows',len(rows),'with local',sum(1 for r in rows if r['local_path']),'cited',sum(1 for r in rows if r['project_status']!='not yet used'))
print(collections.Counter(r['oa_status'] for r in rows).most_common(12))
