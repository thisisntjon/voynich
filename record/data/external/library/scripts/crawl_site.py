import sys,os,time,re,requests,hashlib,json
from urllib.parse import urljoin,urlparse,urldefrag
from bs4 import BeautifulSoup
start,dom,outdir,maxn=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4])
prefix=sys.argv[5] if len(sys.argv)>5 else ""
os.makedirs(outdir,exist_ok=True)
S=requests.Session(); S.headers["User-Agent"]="Mozilla/5.0 voynich-library-research (polite crawler, 1 req/s)"
seen=set(); q=[start]; n=0
done={}
if os.path.exists(f"{outdir}/_crawl.tsv"):
    for l in open(f"{outdir}/_crawl.tsv"):
        p_=l.rstrip('\n').split('\t')
        if len(p_)>=6: done[p_[0]]=p_
log=open(f"{outdir}/_crawl.tsv","a")
docext=('.pdf','.txt','.zip','.doc','.docx','.xlsx','.xls','.csv','.ods','.odt','.rtf','.tsv','.evt','.eva')
while q and n<maxn:
    u=urldefrag(q.pop(0))[0]
    if u in seen: continue
    seen.add(u)
    p=urlparse(u)
    if not p.netloc.endswith(dom) or not p.path.startswith(prefix): continue
    if re.search(r'\.(jpe?g|png|gif|bmp|tiff?|css|js|ico|svg|mp4|mp3|wav)$',p.path,re.I): continue
    if u in done and done[u][1]=='200' and os.path.isfile(done[u][5]):
        ct=done[u][2]
        if 'html' in ct:
            s=BeautifulSoup(open(done[u][5],'rb').read(),'html.parser')
            for a in s.find_all(['a','frame','iframe'],href=True)+s.find_all(['frame','iframe'],src=True):
                v=urljoin(u,a.get('href') or a.get('src'))
                if v not in seen: q.append(v)
        continue
    if u in done: continue
    try: r=S.get(u,timeout=60)
    except Exception as e: log.write(f"{u}\tERR\t{e}\n"); continue
    n+=1; ct=r.headers.get("content-type","")
    path=p.path if not p.path.endswith('/') else p.path+"index.html"
    fn=os.path.join(outdir,p.netloc+path)
    try:
        os.makedirs(os.path.dirname(fn),exist_ok=True)
        if os.path.isdir(fn): fn=fn+'/_index_.html'
        if r.status_code==200 and len(r.content)<60_000_000:
            open(fn,'wb').write(r.content)
    except Exception as e:
        fn='WRITE-ERR:'+str(e)[:80]
    log.write(f"{u}\t{r.status_code}\t{ct}\t{len(r.content)}\t{hashlib.sha256(r.content).hexdigest()}\t{fn}\n"); log.flush()
    if r.status_code==200 and 'html' in ct:
        s=BeautifulSoup(r.content,'html.parser')
        for a in s.find_all(['a','frame','iframe'],href=True)+s.find_all(['frame','iframe'],src=True):
            h=a.get('href') or a.get('src')
            v=urljoin(u,h)
            if v not in seen: q.append(v)
    time.sleep(1.0)
print("fetched",n,"queue",len(q))
