# html/pdf in mirrors -> plain text under out/web/<site>/... (.txt), plus pages index TSV
import os,csv,hashlib,subprocess,sys
from bs4 import BeautifulSoup
def conv(src,dst):
    os.makedirs(os.path.dirname(dst),exist_ok=True)
    if src.lower().endswith('.pdf'):
        subprocess.run(['pdftotext','-enc','UTF-8',src,dst],timeout=180,capture_output=True); return
    s=BeautifulSoup(open(src,'rb').read(),'html.parser')
    for x in s(['script','style']): x.decompose()
    t='\n'.join(l.strip() for l in s.get_text('\n').splitlines() if l.strip())
    title=(s.title.string.strip() if s.title and s.title.string else '')
    open(dst,'w',encoding='utf-8').write(f'# {title}\n# source: {src}\n\n'+t)
    return title
for site,tsv in [('voynich_nu','mirror/voynich_nu/_crawl.tsv'),('philipneal','mirror/philipneal/_wayback.tsv')]:
    rows=[]; seen=set()
    for l in open(tsv,encoding='utf-8'):
        p=l.rstrip('\n').split('\t')
        if len(p)<6: continue
        if len(p)>=7: url,ts,st,ct,b,sha,path=p[:7]; url=url+' (wayback '+ts+')'
        else: url,st,ct,b,sha,path=p[:6]
        if st!='200' or not os.path.exists(path) or path in seen: continue
        seen.add(path); title=''
        rel=os.path.relpath(path,'mirror/'+site)
        txt=''
        if 'html' in ct or path.lower().endswith(('.html','.htm')) or 'pdf' in ct:
            dst='out/web/'+site+'/text/'+rel+'.txt'
            try: title=conv(path,dst) or ''; txt=os.path.relpath(dst,'out')
            except Exception as e: print('ERR',path,e,file=sys.stderr)
        rows.append([url,ct,b,sha,'web/'+site+'/raw/'+rel,txt,title])
    with open(f'out/indexes/{site}_pages.tsv','w',encoding='utf-8',newline='\n') as f:
        f.write('url\tcontent_type\tbytes\tsha256\traw_copy\ttext_copy\ttitle\n')
        for r in rows: f.write('\t'.join(str(x).replace('\t',' ') for x in r)+'\n')
    print(site,len(rows),sum(1 for r in rows if r[5]))
