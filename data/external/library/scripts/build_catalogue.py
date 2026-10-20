import json,re,csv,collections,unicodedata
recs=[json.loads(l) for l in open('stage/records.jsonl')]
CURATED={'zandbergen_refs','zandbergen_web','reeds_biblio','stolfi_bib','bowern_resources'}
def low(s): return (s or '').lower()
rej=collections.Counter(); kept=[]
for r in recs:
    t=low(r['title']); a=low(r['abstract']); txt=t+' '+a
    src=r['src']; auth=' '.join(r['authors']).lower()
    ethel=re.search(r'gadfly|ovod|ethel|lilian|e\. ?l\. voynich|boole',txt) and not re.search(r'manuscript|codex|cipher|beinecke|ms 408|voynichese',txt)
    if src in CURATED or src.startswith('wikipedia'):
        r['relevance']='curated_bibliography'; kept.append(r); continue
    if ethel: rej['ethel_voynich_literary']+=1; continue
    if src=='internetarchive':
        if r['type']=='ia_texts' and 'voynich' in txt: r['relevance']='core' if 'voynich' in t else 'mention'
        elif 'voynich' in t: r['relevance']='popular_media'
        else: rej['ia_other']+=1; continue
        kept.append(r); continue
    if src=='openlibrary':
        if 'voynich' in t: r['relevance']='core'; kept.append(r)
        else: rej['openlibrary_not_title']+=1
        continue
    if src=='openalex_fulltext':
        if 'voynich' in auth and 'voynich' not in t: rej['author_surname_voynich']+=1; continue
        r['relevance']='core' if 'voynich' in t else 'mention'; kept.append(r); continue
    if 'voynich' in t or 'voynichese' in txt: r['relevance']='core'
    elif 'voynich' in a and re.search(r'manuscript|codex|cipher|script|beinecke|undeciphered|text',a): r['relevance']='mention'
    elif 'voynich' in auth: rej['author_surname_voynich']+=1; continue
    else: rej['no_voynich_context']+=1; continue
    kept.append(r)
# dedupe
def nt(s):
    s=unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower()
    s=re.sub(r'[^a-z0-9]','',s); return s[:70]
par=list(range(len(kept)))
def f(i):
    while par[i]!=i: par[i]=par[par[i]]; i=par[i]
    return i
def u(i,j): par[f(i)]=f(j)
keys=collections.defaultdict(list)
for i,r in enumerate(kept):
    if r['doi']:
        d=r['doi']; d=re.sub(r'\.v\d+$','',d) 
        keys['doi:'+d].append(i)
    ax=r.get('arxiv') or (re.search(r'arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})',r['url']+' '+r['oa_url']) or [None,None])[1] or (re.search(r'10\.48550/arxiv\.([0-9.]+)',r['doi']) or [None,None])[1]
    if ax: keys['ax:'+re.sub(r'v\d+$','',ax)].append(i); r['arxiv']=ax
    if r.get('concept'): keys['zc:'+str(r['concept'])].append(i)
    if r['src']=='zenodo': keys['zr:'+r['src_id']].append(i)
    if r['src']=='openalex_titleabs' or r['src']=='openalex_fulltext': keys['oa:'+r['src_id']].append(i)
    n=nt(r['title'])
    if len(n)>=25 and r['type'] not in ('website_sites','curated_link'): keys['t:'+n].append(i)
for k,v in keys.items():
    for j in v[1:]: u(v[0],j)
groups=collections.defaultdict(list)
for i in range(len(kept)): groups[f(i)].append(kept[i])
SRCPRI=['crossref','openalex_titleabs','openalex_fulltext','s2','arxiv','zenodo','hal','europepmc','openlibrary','internetarchive','zandbergen_refs','reeds_biblio','stolfi_bib','wikipedia_en','bowern_resources','zandbergen_web']
def pri(r):
    s=r['src']; return SRCPRI.index(s) if s in SRCPRI else 50
TAGS=[('transcription',r'transcri|translitera|\beva\b|ivtff|interlinear|alphabet'),('statistics',r'entropy|statistic|zipf|frequenc|distribution|network|quantitativ|information theor|markov|n-gram|cluster|complex'),
('linguistics',r'linguist|language|morpholog|phonolog|grammar|word order|syntax|dialect|currier|lexic|vowel|syllab'),('cipher',r'cipher|crypt|encipher|decrypt|steganograph|nomenclat|\bcode\b|codebook'),
('botany',r'plant|botan|herbal|flora|species|pharmac'),('astronomy',r'astronom|astrolog|zodiac|\bstars?\b|constellat|cosmolog'),
('provenance',r'provenance|rudolf|marci|marcus marci|kircher|baresch|barschius|wilfrid|wilfred|jesuit|mondragone|sinapius|horcick|tepenec|bacon|dee\b|kelley|history of the'),
('codicology',r'codicolog|quire|bifoli|folio|binding|parchment|vellum|palaeograph|paleograph|scribe|hand(s)?\b|foliation'),('imaging_materials',r'radiocarbon|carbon dat|\bink\b|pigment|mccrone|multispectral|imaging|spectr|material'),
('hoax_gibberish',r'hoax|gibberish|meaningless|forger|fake|rugg|timm|self-citation|glossolal|nonsense|random'),('decipherment_claim',r'decipher|decod|solved|solution|translat|key to|deciphered|reading of'),
('comparison_text',r'egerton|tacuinum|rohonc|seraphinian|copiale|soyga|linear a|indus|rongorongo|compar'),('machine_learning',r'neural|deep learning|machine learning|\bllm|transformer|embedding|artificial intelligence|\bai\b|gpt')]
def first_sentence(a):
    a=re.sub(r'^(abstract|summary)[:.\s]+','',a.strip(),flags=re.I)
    m=re.match(r'(.{30,260}?[.!?])(\s|$)',a)
    return (m.group(1) if m else a[:220]).replace('\t',' ')
rows=[]
for g in groups.values():
    g.sort(key=pri); b=g[0]
    def pick(fld):
        for r in g:
            if r.get(fld): return r[fld]
        return ''
    srcs=sorted(set(r['src'] for r in g))
    rel=sorted(set(r['relevance'] for r in g),key=['core','curated_bibliography','mention','popular_media'].index)[0]
    title=b['title'] or pick('title'); abstract=max((r['abstract'] for r in g),key=len)
    text=' '.join([title,abstract,pick('venue')]).lower()
    tags=[n for n,p in TAGS if re.search(p,text)]
    typ=b['type']
    oa_url=pick('oa_url'); oa=pick('oa_status')
    if b['src']=='arxiv' or pick('arxiv'): oa=oa or 'green'
    authors='; '.join(b['authors'] or next((r['authors'] for r in g if r['authors']),[]))
    rows.append(dict(type=typ,authors=authors[:300],year=b['year'] or pick('year'),title=title[:400],venue=(pick('venue') if b['src'] not in ('zandbergen_refs','reeds_biblio','wikipedia_en') else b['venue'])[:300],
        doi=pick('doi'),arxiv=pick('arxiv'),url=b['url'] or pick('url'),oa_url=oa_url,oa_status=oa,license=pick('license'),relevance=rel,topic_tags=','.join(tags),
        claim_summary=first_sentence(abstract) if abstract else '',sources=','.join(srcs),source_ids='|'.join(f"{r['src']}={r['src_id']}" for r in g)[:1500],n_sources=len(srcs),
        zenodo_files=json.dumps(pick('zenodo_files')) if pick('zenodo_files') else '',cited_by=pick('cited_by'),abstract=abstract))
order=['core','curated_bibliography','mention','popular_media']
rows.sort(key=lambda r:(order.index(r['relevance']),str(r['year'] or '9999'),r['title'].lower()))
for i,r in enumerate(rows): r['id']=f'VL{i+1:05d}'
json.dump(rows,open('stage/catalogue_rows.json','w'),ensure_ascii=False)
print('kept',len(kept),'rows',len(rows)); print('rejected',dict(rej))
print(collections.Counter(r['relevance'] for r in rows)); print(collections.Counter(t for r in rows for t in r['topic_tags'].split(',') if t))
