import requests,re,time,json,html
from bs4 import BeautifulSoup
S=requests.Session(); S.headers["User-Agent"]="Mozilla/5.0 voynich-library-research (thread index only, 1 req/s)"
forums={25:'News',27:'Voynich Research',34:'Astrology & Astronomy',35:'Library and Research',36:'Water Cooler',37:'Library',4:'Fiction, Media',41:'Analysis of the text',42:'Physical material',43:'Imagery',44:'Provenance & history',45:'Marginalia',48:'Codicology and Paleography',49:'Pre-Modern Cryptography',56:'Non Voynich medievalia',57:'Curated threads',58:'Theories & Solutions',6:'Voynich Talk'}
out={}; 
for fid,name in forums.items():
    page=1
    while page<400:
        u=f"https://www.voynich.ninja/forum-{fid}{'' if page==1 else f'-page-{page}'}.html"
        try: r=S.get(u,timeout=60)
        except Exception as e: print('err',u,e); break
        if r.status_code!=200: print(u,r.status_code); break
        s=BeautifulSoup(r.text,'html.parser'); new=0
        for a in s.select('span.subject_new a, span.subject_old a, span[id^="tid_"] a, a[id^="tid_"]'):
            m=re.search(r'thread-(\d+)',a.get('href',''))
            if not m: continue
            tid=int(m.group(1))
            if tid in out: continue
            tr=a.find_parent('tr'); cells=[' '.join(td.get_text(' ').split()) for td in tr.find_all('td')] if tr else []
            out[tid]=dict(tid=tid,forum=name,forum_id=fid,title=' '.join(a.get_text().split()),url=f"https://www.voynich.ninja/thread-{tid}.html",row=' | '.join(cells)[:300])
            new+=1
        print(fid,page,new,len(out),flush=True)
        nxt=s.find('a',class_='pagination_next')
        if not nxt or new==0: break
        page+=1; time.sleep(1)
json.dump(list(out.values()),open('raw/ninja_threads.json','w'),ensure_ascii=False); print('total',len(out))
