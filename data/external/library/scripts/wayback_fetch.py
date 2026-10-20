import requests,json,sys,os,time,hashlib,re
pat,outdir,maxn=sys.argv[1],sys.argv[2],int(sys.argv[3])
os.makedirs(outdir,exist_ok=True)
S=requests.Session(); S.headers['User-Agent']='voynich-library-research (wayback, 1 req/1.5s)'
r=S.get('https://web.archive.org/cdx/search/cdx',params={'url':pat,'output':'json','filter':'statuscode:200','collapse':'urlkey','fl':'timestamp,original,mimetype,length'},timeout=120)
rows=r.json()[1:]; print('cdx',len(rows),flush=True)
log=open(f'{outdir}/_wayback.tsv','a')
for ts,orig,mt,ln in rows[:maxn]:
    if re.search(r'\.(jpe?g|png|gif|css|js|ico)$',orig,re.I): continue
    u=f'https://web.archive.org/web/{ts}id_/{orig}'
    try: x=S.get(u,timeout=90)
    except Exception as e: log.write(f'{orig}\tERR\t{e}\n'); continue
    fn=os.path.join(outdir,re.sub(r'^https?://','',orig).rstrip('/').replace('?','_'))
    if orig.endswith('/'): fn+='/index.html'
    try:
        os.makedirs(os.path.dirname(fn),exist_ok=True)
        if os.path.isdir(fn): fn+='/_index_.html'
        open(fn,'wb').write(x.content)
    except Exception as e: fn='WRITE-ERR'
    log.write(f'{orig}\t{ts}\t{x.status_code}\t{mt}\t{len(x.content)}\t{hashlib.sha256(x.content).hexdigest()}\t{fn}\n'); log.flush()
    time.sleep(1.5)
print('done',flush=True)
