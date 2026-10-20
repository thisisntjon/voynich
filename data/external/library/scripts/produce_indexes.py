import json,csv,re,collections,os,glob,hashlib
os.makedirs('out/indexes',exist_ok=True); os.makedirs('out/inventory',exist_ok=True)
def c(v): return str(v if v is not None else '').replace('\t',' ').replace('\n',' ').replace('\r',' ')
# blogs
b=json.load(open('raw/blogs.json')); seen=set()
with open('out/indexes/blog_posts.tsv','w',encoding='utf-8',newline='\n') as f:
    f.write('site\tdate\ttitle\turl\texcerpt\n')
    for p in sorted(b,key=lambda x:(x['site'],x['date'] or '')):
        if p['url'] in seen: continue
        seen.add(p['url']); f.write('\t'.join(c(p[k]) for k in ['site','date','title','url','excerpt'])+'\n')
print('blog posts',len(seen),collections.Counter(p['site'] for p in b))
# forum
t=json.load(open('raw/ninja_threads.json'))
with open('out/indexes/forum_threads_voynich_ninja.tsv','w',encoding='utf-8',newline='\n') as f:
    f.write('thread_id\tforum\ttitle\turl\tlisting_row\n')
    for x in sorted(t,key=lambda x:x['tid']): f.write('\t'.join(c(x[k]) for k in ['tid','forum','title','url','row'])+'\n')
print('threads',len(t))
# held documents
held=list(csv.DictReader(open('ctx/held_files.tsv',encoding='utf-8'),delimiter='\t'))
rd=[l for p in glob.glob('ctx/data/**/*.md',recursive=True) for l in open(p,encoding='utf-8',errors='replace') if 'facts' not in p]
cat=json.load(open('stage/catalogue_final.json'))
p2id=collections.defaultdict(list)
for r in cat:
    for p in r['local_path'].split():
        p2id[p].append(r['id'])
docs=[h for h in held if re.search(r'\.(pdf|djvu|txt|html?|xml|zip|doc|docx|epub|ods|xlsx|xlsm|bib|tsv|csv|json)$',h['path'],re.I)]
skip=r'/(word-coordinates|papers/rozanova_2608.17096_src|timm-schinner-generator/|controls_raw/|controls_gibberish/|controls_realline/|controls_synthetic/|cremma/|cremma-medieval|gaskell-bowern-gibberish/|bowern-lindemann-entropy/|herbals_alchemical/|herbals_period/|controls_tabular_ruled/|s127_picture/|vkb/|physical/|egerton_caption_gate/|egerton_ventura_rule/)'
n=0
with open('out/inventory/held_documents.tsv','w',encoding='utf-8',newline='\n') as f:
    f.write('path\tbytes\tsha256\tcatalogue_ids\tcontext_line\n')
    for h in docs:
        if re.search(skip,h['path']): continue
        fn=h['path'].split('/')[-1]
        ctx=next((l.strip() for l in rd if fn in l and len(fn)>6),'')
        f.write('\t'.join(c(x) for x in [h['path'],h['bytes'],h['sha256'],' '.join(p2id.get(h['path'],[])),ctx[:300]])+'\n'); n+=1
print('held docs',n)
