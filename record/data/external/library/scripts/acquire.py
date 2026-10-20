import json,os,re,time,hashlib,requests,subprocess,threading,queue,collections
from urllib.parse import urlparse
rows=json.load(open('stage/catalogue_final.json'))
os.makedirs('pdf/oa',exist_ok=True); os.makedirs('text',exist_ok=True)
logf='stage/acquire_log.jsonl'
done=set()
if os.path.exists(logf):
    for l in open(logf): done.add(json.loads(l)['id'])
tasks=[]
for r in rows:
    if r['id'] in done or r['local_path']: continue
    if r['relevance'] not in ('core','curated_bibliography'): continue
    cand=[]
    if r.get('arxiv'): cand.append(('arxiv',f"https://arxiv.org/pdf/{r['arxiv']}",'pdf'))
    if r.get('zenodo_files'):
        fs=json.loads(r['zenodo_files'])
        for k,sz,ck,link in fs:
            if k.lower().endswith('.pdf') and (sz or 0)<40e6: cand.append(('zenodo',link,'pdf')); break
        else:
            for k,sz,ck,link in fs:
                if re.search(r'\.(md|txt)$',k.lower()) and (sz or 0)<5e6: cand.append(('zenodo',link,'txt')); break
    if r['oa_url'] and not cand: cand.append(('oa',r['oa_url'],'pdf'))
    if r['type']=='ia_texts' and not cand:
        ident=r['url'].split('/details/')[-1]; cand.append(('ia',ident,'iatxt'))
    if cand: tasks.append((r,cand))
print('tasks',len(tasks),collections.Counter(c[0][0] for _,c in tasks),flush=True)
S=requests.Session(); S.headers['User-Agent']='Mozilla/5.0 (X11; Linux x86_64) voynich-library-research (open-access fetch)'
lock=threading.Lock(); hostlast=collections.defaultdict(float)
def polite(host,gap):
    with lock:
        w=hostlast[host]+gap-time.time()
        hostlast[host]=max(time.time(),hostlast[host]+gap)
    if w>0: time.sleep(w)
def fetch(r,cand):
    rec=dict(id=r['id'],status='fail',tries=[])
    for kind,u,fmt in cand:
        try:
            if kind=='ia':
                polite('archive.org',1.5)
                m=S.get(f'https://archive.org/metadata/{u}',timeout=60).json()
                md=m.get('metadata',{})
                if md.get('access-restricted-item') in ('true',True) or 'inlibrary' in str(md.get('collection')) or 'printdisabled' in str(md.get('collection')):
                    rec['tries'].append(('ia','restricted')); continue
                txts=[f['name'] for f in m.get('files',[]) if f['name'].endswith('_djvu.txt')]
                if not txts: rec['tries'].append(('ia','no_djvu_txt')); continue
                u=f'https://archive.org/download/{u}/{txts[0]}'; fmt='txt'; rec['license']=md.get('licenseurl','') or md.get('rights','')
            host=urlparse(u).netloc; polite(host,3.0 if 'arxiv' in host else 1.2)
            resp=S.get(u,timeout=120,stream=True)
            data=b''
            for ch in resp.iter_content(1<<16):
                data+=ch
                if len(data)>45e6: break
            if resp.status_code!=200 or len(data)>45e6: rec['tries'].append((u,resp.status_code,len(data))); continue
            if fmt=='pdf' and not data.startswith(b'%PDF'): rec['tries'].append((u,'not_pdf',resp.headers.get('content-type',''))); continue
            ext='pdf' if fmt=='pdf' else 'txt'
            fn=f"pdf/oa/{r['id']}.{ext}" if ext=='pdf' else f"text/{r['id']}.txt"
            open(fn,'wb').write(data)
            rec.update(status='ok',url=u,file=fn,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),kind=kind)
            if ext=='pdf':
                subprocess.run(['pdftotext','-enc','UTF-8',fn,f"text/{r['id']}.txt"],timeout=180,capture_output=True)
                rec['text']=f"text/{r['id']}.txt" if os.path.exists(f"text/{r['id']}.txt") else ''
                rec['text_bytes']=os.path.getsize(rec['text']) if rec['text'] else 0
            else: rec['text']=fn; rec['text_bytes']=len(data)
            break
        except Exception as e: rec['tries'].append((u,'err',str(e)[:100]))
    with lock:
        open(logf,'a').write(json.dumps(rec)+'\n')
q=queue.Queue()
for t in tasks: q.put(t)
def worker():
    while True:
        try: r,c=q.get_nowait()
        except queue.Empty: return
        fetch(r,c)
ts=[threading.Thread(target=worker) for _ in range(4)]
[t.start() for t in ts]; [t.join() for t in ts]
print('done',flush=True)
