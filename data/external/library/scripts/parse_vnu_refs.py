import re,json,html
from bs4 import BeautifulSoup
raw=open('raw/voynich_nu/refs.html','rb').read().decode('latin-1')
s=BeautifulSoup(raw,'html.parser')
h2=s.find('h2',id='refs')
rows=[]
for p in h2.find_all_next('p'):
    if p.find_previous('h2') is not h2: break
    pid=p.get('id')
    txt=' '.join(p.get_text(' ').split())
    if not txt or len(txt)<10: continue
    it=p.find('i'); title=' '.join(it.get_text(' ').split()) if it else ''
    m=re.match(r'^(.*?):\s',txt); authors=m.group(1) if m else ''
    yr=re.findall(r'\b(1[4-9]\d\d|20[0-2]\d)\b',txt)
    links=[a['href'] for a in p.find_all('a',href=True)]
    rows.append(dict(src_id=pid or '',authors=authors,title=title,year=yr[-1] if yr else '',raw=txt,links=links,web_dagger=('†' in txt)))
# web resource sections
web=[]
for sec in ['fora','wiki','sites','herbs','solns']:
    h=s.find('h4',id=sec)
    nxt=h.find_next(['h4','h2'])
    node=h.next_element
    for a in h.find_all_next('a',href=True):
        if nxt and a.sourceline and nxt.sourceline and a.sourceline>nxt.sourceline: break
        href=a['href']
        if href.startswith('http'):
            ctx=' '.join(a.parent.get_text(' ').split())[:300]
            web.append(dict(section=sec,url=href,anchor=' '.join(a.get_text(' ').split()),context=ctx))
json.dump(rows,open('stage/vnu_refs.json','w'),ensure_ascii=False,indent=0)
json.dump(web,open('stage/vnu_web.json','w'),ensure_ascii=False,indent=0)
print(len(rows),len(web))
for r in rows[:5]: print(r['authors'],'|',r['title'],'|',r['year'])
