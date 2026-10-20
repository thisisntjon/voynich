# P2/P4: add project-cited rows, attach fetched full text, write catalogue + manifests + topic index + unchecked claims
import json,os,re,collections,shutil,hashlib
rows=json.load(open('stage/catalogue_final.json'))
byid={r['id']:r for r in rows}
cols=['id','type','relevance','authors','year','title','venue','doi','arxiv','url','oa_status','oa_url','license','local_path','topic_tags','claim_summary','project_status','sources','n_sources','source_ids']
def clean(v): return str(v if v is not None else '').replace('\t',' ').replace('\n',' ').replace('\r',' ')
# 1 project-cited rows (metadata retrieved from Crossref / Zenodo API on 2026-10-19)
have={(r.get('doi') or '').lower() for r in rows}
n=max(int(r['id'][2:]) for r in rows)
for m in json.load(open('raw/crossref_projcited.json')):
    if m['doi'].lower() in have: continue
    n+=1; ab=re.sub(r'<[^>]+>',' ',m.get('abstract','')); ab=' '.join(ab.split())
    cs=re.split(r'(?<=[.!?])\s',ab)[0][:300] if ab else ''
    r=dict(id=f'VL{n:05d}',type=m.get('type',''),relevance='project_cited',authors=m['authors'],year=m['year'],title=m['title'],venue=m['venue'],doi=m['doi'],arxiv='',url=m.get('url') or 'https://doi.org/'+m['doi'],oa_status='',oa_url='',license=m.get('license',''),local_path='',topic_tags='',claim_summary=cs,project_status='cited (DOI found in project docs)',project_ids='',sources='crossref' if 'zenodo' not in m['doi'] else 'zenodo',n_sources=1,source_ids=m['doi'],abstract=ab,zenodo_files='',cited_by='')
    rows.append(r); byid[r['id']]=r; have.add(m['doi'].lower())
# 2 full text
L=[json.loads(l) for l in open('stage/acquire_log.jsonl')]
if os.path.exists('stage/acquire2_log.jsonl'): L+=[json.loads(l) for l in open('stage/acquire2_log.jsonl')]
ok={}
for x in L:
    if x['status']=='ok': ok[x['id']]=x
fails={x['id']:x for x in L if x['status']!='ok' and x['id'] not in ok}
os.makedirs('out/fulltext/pdf',exist_ok=True); os.makedirs('out/corpus/papers',exist_ok=True)
man=[]
for i,x in sorted(ok.items()):
    r=byid[i]; lp=[]
    if x['file'].endswith('.pdf'):
        d='out/fulltext/pdf/'+i+'.pdf'
        if not os.path.exists(d): shutil.copy2(x['file'],d)
        lp.append('fulltext/pdf/'+i+'.pdf')
    t=x.get('text') or ''
    tb=0
    if t and os.path.exists(t) and os.path.getsize(t)>200:
        d='out/corpus/papers/'+i+'.txt'
        head=f"# {i} | {r['authors'][:120]} | {r['year']} | {r['title'][:200]}\n# source: {x['url']}\n# licence: {r.get('license') or x.get('license') or 'unknown'} | local research copy, do not redistribute\n\n"
        open(d,'w',encoding='utf-8').write(head+open(t,encoding='utf-8',errors='replace').read()); tb=os.path.getsize(d)
        lp.append('corpus/papers/'+i+'.txt')
    old=r['local_path']; r['local_path']=' '.join(lp+([old] if old else []))
    man.append([i,x.get('kind',''),x['url'],lp[0] if lp else '',x.get('sha256',''),x.get('bytes',0),('corpus/papers/'+i+'.txt') if tb else '',tb,r.get('license') or x.get('license',''),r['year'],r['title'][:160]])
with open('out/fulltext/FULLTEXT-MANIFEST.tsv','w',encoding='utf-8',newline='\n') as f:
    f.write('catalogue_id\tvia\tsource_url\tfile\tsha256\tbytes\ttext_file\ttext_bytes\tlicense\tyear\ttitle\n')
    for m in man: f.write('\t'.join(clean(v) for v in m)+'\n')
with open('out/fulltext/NOT-FETCHED.tsv','w',encoding='utf-8',newline='\n') as f:
    f.write('catalogue_id\treason\tyear\ttitle\turl\n')
    for i,x in sorted(fails.items()):
        r=byid[i]; f.write('\t'.join(clean(v) for v in [i,json.dumps(x.get('tries',[]))[:300],r['year'],r['title'][:160],r['url']])+'\n')
# 3 catalogue
with open('out/catalogue.tsv','w',encoding='utf-8',newline='\n') as f:
    f.write('\t'.join(cols)+'\n')
    for r in rows: f.write('\t'.join(clean(r.get(c,'')) for c in cols)+'\n')
with open('out/catalogue_abstracts.jsonl','w') as f:
    for r in rows:
        if r.get('abstract'): f.write(json.dumps({'id':r['id'],'title':r['title'],'abstract':r['abstract']},ensure_ascii=False)+'\n')
# 4 topic index
tags=collections.defaultdict(list)
for r in rows:
    for t in (r['topic_tags'] or '').split(','):
        if t: tags[t].append(r)
os.makedirs('out/topics',exist_ok=True)
with open('out/topics/topic_index.tsv','w',encoding='utf-8',newline='\n') as f:
    f.write('tag\tid\trelevance\tyear\tauthors\ttitle\tlocal_path\n')
    for t in sorted(tags):
        for r in sorted(tags[t],key=lambda r:(r['relevance']!='core',str(r['year']))):
            f.write('\t'.join(clean(v) for v in [t,r['id'],r['relevance'],r['year'],r['authors'][:80],r['title'][:200],r['local_path'].split(' ')[0] if r['local_path'] else ''])+'\n')
with open('out/topics/TOPICS.md','w',encoding='utf-8') as f:
    f.write('# Topic index (keyword-regex tags on title+abstract; not judgments)\n\nFull lists: `topic_index.tsv` (tag, id, ...). Below: counts, and core items with local full text (up to 25 per tag, oldest first).\n\n')
    for t in sorted(tags,key=lambda t:-len(tags[t])):
        rs=tags[t]; core=[r for r in rs if r['relevance'] in('core','project_cited')]
        f.write(f"## {t}  ({len(rs)} rows, {len(core)} core)\n\n")
        for r in sorted([r for r in core if r['local_path']],key=lambda r:str(r['year']))[:25]:
            f.write(f"- {r['id']} {r['year']} {r['authors'][:50]}: {r['title'][:110]}  -> `{r['local_path'].split(' ')[0]}`\n")
        f.write('\n')
# 5 published claims not yet checked by the project
uc=[r for r in rows if 'decipherment_claim' in (r['topic_tags'] or '') and r['relevance']=='core' and r['project_status']=='not yet used']
with open('out/unchecked_claims.tsv','w',encoding='utf-8',newline='\n') as f:
    f.write('id\tyear\tauthors\ttitle\tvenue\ttype\tpeer_reviewed_guess\tlocal_path\tclaim_summary\turl\n')
    for r in sorted(uc,key=lambda r:str(r['year']),reverse=True):
        pr='journal/proceedings' if r['type'] in('article','journal-article','proceedings-article','book-chapter') and r['venue'] and 'zenodo' not in r['venue'].lower() else 'no/unknown'
        f.write('\t'.join(clean(v) for v in [r['id'],r['year'],r['authors'][:80],r['title'][:200],r['venue'][:80],r['type'],pr,r['local_path'].split(' ')[0] if r['local_path'] else '',r['claim_summary'][:300],r['url'] or r['oa_url']])+'\n')
json.dump(rows,open('stage/catalogue_final2.json','w'),ensure_ascii=False)
print('rows',len(rows),'fulltext ok',len(ok),'pdf',sum(1 for m in man if m[3].endswith('.pdf')),'text',sum(1 for m in man if m[7]),'not fetched',len(fails),'unchecked',len(uc))
print(collections.Counter(r['relevance'] for r in rows))
print(collections.Counter((m[8] or 'unknown')[:30] for m in man).most_common(10))
