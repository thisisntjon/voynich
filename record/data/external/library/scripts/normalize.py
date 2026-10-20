"""Normalize every harvested source into stage/records.jsonl (one record per source hit)."""
import json,re,html,glob,os,xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
R='raw'; recs=[]
def clean(s): return ' '.join(html.unescape(re.sub(r'<[^>]+>',' ',s or '')).split())
def add(**k):
    k.setdefault('authors',[]); k.setdefault('abstract',''); 
    for f in ['title','venue','doi','url','oa_url','oa_status','license','year','type','abstract']: k[f]=clean(str(k.get(f) or ''))
    k['doi']=k['doi'].lower().replace('https://doi.org/','').replace('http://dx.doi.org/','')
    recs.append(k)
# OpenAlex
def oa_abs(ii):
    if not ii: return ''
    pos={}
    for w,ps in ii.items():
        for p in ps: pos[p]=w
    return ' '.join(pos[i] for i in sorted(pos))
seen_oa=set()
for name in ['titleabs','fulltext']:
    for w in json.load(open(f'{R}/openalex_{name}.json')):
        if w['id'] in seen_oa and name=='fulltext': continue
        seen_oa.add(w['id'])
        loc=w.get('primary_location') or {}; src=(loc.get('source') or {})
        oa=w.get('open_access') or {}
        add(src='openalex_'+name, src_id=w['id'], type=w.get('type'), authors=[a['author']['display_name'] for a in w.get('authorships',[])],
            year=w.get('publication_year'), title=w.get('title') or w.get('display_name'), venue=src.get('display_name'),
            doi=w.get('doi'), url=(loc.get('landing_page_url') or w['id']), oa_url=oa.get('oa_url'), oa_status=oa.get('oa_status'),
            license=loc.get('license'), abstract=oa_abs(w.get('abstract_inverted_index')), cited_by=w.get('cited_by_count'))
# Crossref
cr={}
for f in ['crossref','crossref_query']:
    for it in json.load(open(f'{R}/{f}.json')): cr[it['DOI']]=it
for it in cr.values():
    dp=(it.get('issued') or {}).get('date-parts',[[None]])[0][0]
    add(src='crossref',src_id=it['DOI'],type=it.get('type'),authors=[(' '.join(filter(None,[a.get('given'),a.get('family')])) or a.get('name','')) for a in it.get('author',[])],
        year=dp,title=(it.get('title') or [''])[0],venue=(it.get('container-title') or [''])[0] or it.get('publisher'),doi=it['DOI'],url=it.get('URL'),
        license=';'.join(l.get('URL','') for l in it.get('license',[])[:1]),abstract=it.get('abstract',''))
# Semantic Scholar
for p in json.load(open(f'{R}/s2.json',encoding='utf-8-sig')):
    ext=p.get('externalIds') or {}; oap=p.get('openAccessPdf') or {}
    add(src='s2',src_id=p['paperId'],type=','.join(p.get('publicationTypes') or []),authors=[a.get('name','') for a in (p.get('authors') or [])],
        year=p.get('year'),title=p.get('title'),venue=p.get('venue') or ((p.get('journal') or {}).get('name') if isinstance(p.get('journal'),dict) else ''),
        doi=ext.get('DOI',''),arxiv=ext.get('ArXiv',''),url=p.get('url'),oa_url=oap.get('url'),oa_status=oap.get('status'),license=oap.get('license'),abstract=p.get('abstract'),acl=ext.get('ACL',''))
# arXiv
ns={'a':'http://www.w3.org/2005/Atom','arxiv':'http://arxiv.org/schemas/atom'}
ax={}
for f in ['arxiv.xml','arxiv2.xml']:
    try: root=ET.parse(f'{R}/{f}').getroot()
    except Exception: continue
    for e in root.findall('a:entry',ns): ax[e.find('a:id',ns).text]=e
for i,e in ax.items():
    aid=re.sub(r'v\d+$','',i.split('/abs/')[-1])
    d=e.find('arxiv:doi',ns)
    add(src='arxiv',src_id=aid,type='preprint',authors=[a.find('a:name',ns).text for a in e.findall('a:author',ns)],year=e.find('a:published',ns).text[:4],
        title=e.find('a:title',ns).text,venue='arXiv',doi=(d.text if d is not None else ''),arxiv=aid,url=f'https://arxiv.org/abs/{aid}',oa_url=f'https://arxiv.org/pdf/{aid}',oa_status='green',abstract=e.find('a:summary',ns).text)
# Zenodo
for h in json.load(open(f'{R}/zenodo.json')):
    m=h['metadata']; rt=m.get('resource_type',{})
    files=[f['links']['self'] for f in h.get('files',[]) if f.get('key','').lower().endswith('.pdf')]
    add(src='zenodo',src_id=str(h['id']),type=(rt.get('subtype') or rt.get('type')),authors=[c['name'] for c in m.get('creators',[])],year=(m.get('publication_date') or '')[:4],
        title=m.get('title'),venue='Zenodo',doi=m.get('doi') or h.get('doi'),url=h['links'].get('self_html') or f"https://zenodo.org/records/{h['id']}",
        oa_url=(files[0] if files else ''),oa_status=('open' if m.get('access_right')=='open' else m.get('access_right')),license=(m.get('license') or {}).get('id',''),abstract=m.get('description',''),
        zenodo_files=[(f.get('key'),f.get('size'),f.get('checksum'),f['links']['self']) for f in h.get('files',[])], concept=h.get('conceptrecid'))
# Internet Archive
for d in json.load(open(f'{R}/internetarchive.json')):
    t=d.get('title'); t=t[0] if isinstance(t,list) else t
    cr_=d.get('creator') or []; cr_=cr_ if isinstance(cr_,list) else [cr_]
    desc=d.get('description') or ''; desc=' '.join(desc) if isinstance(desc,list) else desc
    add(src='internetarchive',src_id=d['identifier'],type='ia_'+str(d.get('mediatype')),authors=cr_,year=str(d.get('year') or d.get('date','')[:4]),title=t,venue='Internet Archive',
        url=f"https://archive.org/details/{d['identifier']}",license=d.get('licenseurl',''),abstract=desc[:2000],ia_collection=d.get('collection'))
# Open Library
for d in json.load(open(f'{R}/openlibrary.json')):
    add(src='openlibrary',src_id=d.get('key'),type='book',authors=d.get('author_name',[]),year=d.get('first_publish_year'),title=d.get('title'),venue=', '.join((d.get('publisher') or [])[:2]),
        url='https://openlibrary.org'+d.get('key',''),isbn=(d.get('isbn') or [''])[0],oa_status=('ia:'+d['ia'][0] if d.get('ia') and d.get('ebook_access')=='public' else d.get('ebook_access','')))
# HAL / EuropePMC
for d in json.load(open(f'{R}/hal.json')):
    add(src='hal',src_id=d.get('docid'),type=d.get('docType_s'),authors=d.get('authFullName_s',[]),year=d.get('producedDateY_i'),title=(d.get('title_s') or [''])[0],venue=d.get('journalTitle_s'),
        doi=d.get('doiId_s'),url=d.get('uri_s'),oa_url=d.get('fileMain_s'),oa_status=('open' if d.get('openAccess_bool') else ''),abstract=(d.get('abstract_s') or [''])[0])
for d in json.load(open(f'{R}/europepmc.json')):
    add(src='europepmc',src_id=d.get('id'),type=d.get('pubType'),authors=[a.strip() for a in (d.get('authorString') or '').split(',') if a.strip()],year=d.get('pubYear'),title=d.get('title'),
        venue=d.get('journalTitle') or (d.get('journalInfo') or {}).get('journal',{}).get('title',''),doi=d.get('doi'),url=f"https://europepmc.org/article/{d.get('source')}/{d.get('id')}",oa_status=('open' if d.get('isOpenAccess')=='Y' else ''),abstract=d.get('abstractText',''))
# voynich.nu bibliography
for r in json.load(open('stage/vnu_refs.json')):
    if not r['title'] and not r['authors']: continue
    if r['authors'].startswith('Note about'): continue
    links=[l for l in r['links'] if l.startswith('http')]
    add(src='zandbergen_refs',src_id='vnu#'+r['src_id'],type='bibliography_entry',authors=[r['authors'].rstrip('.')],year=r['year'],title=r['title'] or r['raw'][:200],venue=r['raw'][:400],url=(links[0] if links else 'https://www.voynich.nu/refs.html#'+r['src_id']),raw=r['raw'])
for w in json.load(open('stage/vnu_web.json')):
    add(src='zandbergen_web',src_id='vnu-web:'+w['url'],type='website_'+w['section'],title=w['anchor'] or w['url'],venue='voynich.nu refs.html web resources: '+w['section'],url=w['url'],abstract=w['context'])
# Reeds
s=BeautifulSoup(open(f'{R}/biblios/reeds_biblio.html','rb').read(),'html.parser')
for sec in s.find_all('h2'):
    ol=sec.find_next(['ol','ul'])
    for n,li in enumerate(ol.find_all('li',recursive=False)):
        t=' '.join(li.get_text(' ').split())
        m=re.match(r"^(.*?)\.\s+``(.*?)''",t) or re.match(r"^(.*?)\.\s+(.*?)\.",t)
        yr=re.findall(r'\b(1[5-9]\d\d|20[0-2]\d)\b',t)
        add(src='reeds_biblio',src_id=f"reeds:{sec.get_text()[:4]}:{n+1}",type=('manuscript_unpublished' if 'Manuscripts' in sec.get_text() else 'bibliography_entry'),
            authors=[m.group(1)] if m else [],year=yr[0] if yr else '',title=(m.group(2) if m else t[:200]),venue=t[:400],url='https://www.voynich.nu/hist/reeds/reeds_biblio.html',raw=t)
# Stolfi bib
b=open(f'{R}/biblios/stolfi_voynich.bib',encoding='latin-1').read()
for e in re.split(r'\n(?=@)',b):
    m=re.match(r'@(\w+)\{([^,]+),',e)
    if not m: continue
    g=lambda k:(re.search(k+r'\s*=\s*\{(.*?)\},?\s*\n',e,re.S) or [None,''])[1]
    add(src='stolfi_bib',src_id='stolfi:'+m.group(2),type='bib_'+m.group(1),authors=[a.strip() for a in g('author').split(' and ')],year=g('year'),title=g('title').replace('{','').replace('}',''),venue=g('howpublished') or g('journal') or g('booktitle'),url=(re.search(r'url\{([^}]*)\}',e) or [None,''])[1],raw=e[:500])
# Wikipedia citations (all languages)
for f in sorted(glob.glob(f'{R}/biblios/wiki_*.html')):
    lang=f.split('_')[-1][:2]
    s=BeautifulSoup(open(f,'rb').read(),'html.parser')
    for i,c in enumerate(s.find_all('cite')):
        t=' '.join(c.get_text(' ').split())
        if len(t)<15: continue
        hrefs=[a['href'] for a in c.find_all('a',href=True) if a['href'].startswith('http') and 'wikipedia.org' not in a['href'] and 'wikidata' not in a['href']]
        doi=(re.search(r'doi\.org/(10\.[^\s"&]+)',' '.join(a['href'] for a in c.find_all('a',href=True))) or [None,''])[1].replace('%2F','/')
        tm=re.search(r'["“«„](.+?)["”»“]',t); yr=re.findall(r'\b(1[5-9]\d\d|20[0-2]\d)\b',t)
        add(src='wikipedia_'+lang,src_id=f'wiki-{lang}:{i}',type='wikipedia_citation',authors=[t.split('(')[0].split('.')[0][:80]] if '(' in t[:120] else [],year=yr[0] if yr else '',
            title=(tm.group(1) if tm else t[:200]),venue=t[:400],doi=doi,url=(hrefs[0] if hrefs else ''),raw=t)
# Bowern resource page
s=BeautifulSoup(open(f'{R}/biblios/bowern_resources.html','rb').read(),'html.parser')
body=s.find('div',class_='entry-content') or s
for li in body.find_all('li'):
    t=' '.join(li.get_text(' ').split()); hs=[a['href'] for a in li.find_all('a',href=True)]
    if 'voynich' not in t.lower() and not hs: continue
    if len(t)<20: continue
    add(src='bowern_resources',src_id='bowern:'+(hs[0] if hs else t[:40]),type='curated_link',title=t[:250],venue='Bowern Yale Voynich resources page',url=(hs[0] if hs else 'https://campuspress.yale.edu/clairebowern/voynich-resources/'),raw=t)
os.makedirs('stage',exist_ok=True)
with open('stage/records.jsonl','w') as o:
    for r in recs: o.write(json.dumps(r,ensure_ascii=False)+'\n')
from collections import Counter
print(len(recs)); print(Counter(r['src'] for r in recs))
