# pass 2: failed pass-1 items. Landing page -> citation_pdf_url meta; Zenodo DOI -> Zenodo API files. Logs stage/acquire2_log.jsonl
import json,os,re,time,hashlib,requests,subprocess,collections
from urllib.parse import urlparse,urljoin
rows={r['id']:r for r in json.load(open('stage/catalogue_final.json'))}
L=[json.loads(l) for l in open('stage/acquire_log.jsonl')]
logf='stage/acquire2_log.jsonl'; done=set()
if os.path.exists(logf): done={json.loads(l)['id'] for l in open(logf)}
S=requests.Session(); S.headers['User-Agent']='Mozilla/5.0 (X11; Linux x86_64) voynich-library-research (open-access fetch)'
class R: pass
def get(u,**k):
    time.sleep(1.2); t0=time.time()
    r=S.get(u,timeout=(20,30),stream=True,**k); data=b''
    for ch in r.iter_content(1<<16):
        data+=ch
        if len(data)>45e6 or time.time()-t0>120: break
    o=R(); o.status_code=r.status_code; o.headers=r.headers; o.content=data; o.url=r.url
    o.text=data.decode(r.encoding or 'utf-8','replace') if 'html' in r.headers.get('content-type','') else ''
    o.json=lambda d=data: json.loads(d)
    r.close(); return o
def save(rid,data,u,kind):
    fn=f'pdf/oa/{rid}.pdf'; open(fn,'wb').write(data)
    subprocess.run(['pdftotext','-enc','UTF-8',fn,f'text/{rid}.txt'],timeout=180,capture_output=True)
    t=f'text/{rid}.txt' if os.path.exists(f'text/{rid}.txt') else ''
    return dict(id=rid,status='ok',url=u,file=fn,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),kind=kind,text=t,text_bytes=os.path.getsize(t) if t else 0)
for x in L:
    if x['status']=='ok' or x['id'] in done: continue
    r=rows[x['id']]; rec=dict(id=x['id'],status='fail',tries=[])
    try:
        m=re.search(r'zenodo\.(\d+)',(r.get('doi') or '')+' '+(r.get('url') or '')+' '+(r.get('oa_url') or ''))
        cands=[]
        if m:
            z=get(f'https://zenodo.org/api/records/{m.group(1)}')
            if z.status_code==200:
                j=z.json(); rec['license']=j['metadata'].get('license',{}).get('id','')
                cands=[f['links']['self'] for f in j.get('files',[]) if f['key'].lower().endswith('.pdf') and f.get('size',0)<40e6][:1]
                if not cands and j.get('metadata',{}).get('access_right')!='open': rec['tries'].append(('zenodo','access_'+str(j['metadata'].get('access_right'))))
            else: rec['tries'].append(('zenodo_api',z.status_code))
        else:
            for u in [r.get('oa_url'),r.get('url')]:
                if not u or not u.startswith('http'): continue
                h=get(u)
                if h.status_code!=200 or 'html' not in h.headers.get('content-type',''): rec['tries'].append((u,h.status_code)); continue
                mm=re.search(r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)',h.text) or re.search(r'content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url',h.text)
                if mm: cands.append(urljoin(h.url,mm.group(1).replace('&amp;','&'))); break
                rec['tries'].append((u,'no_citation_pdf_url'))
        for c in cands:
            d=get(c); 
            if d.status_code==200 and d.content.startswith(b'%PDF') and len(d.content)<45e6:
                rec=save(x['id'],d.content,c,'pass2'); rec['license']=rec.get('license','');break
            rec['tries'].append((c,d.status_code,'not_pdf' if d.status_code==200 else ''))
    except Exception as e: rec['tries'].append(('err',str(e)[:120]))
    open(logf,'a').write(json.dumps(rec)+'\n')
print('done',flush=True)
