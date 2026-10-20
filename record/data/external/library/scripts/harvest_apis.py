import json, time, sys, requests, urllib.parse, xml.etree.ElementTree as ET, os
R = "raw"
S = requests.Session(); S.headers["User-Agent"] = "voynich-library-harvest/0.1 (research bibliography; mailto:none)"
def get(url, **kw):
    for i in range(5):
        try:
            r = S.get(url, timeout=60, **kw)
            if r.status_code == 429: time.sleep(5*(i+1)); continue
            r.raise_for_status(); return r
        except Exception as e:
            print("retry", url[:120], e, file=sys.stderr); time.sleep(3*(i+1))
    return None
def openalex(filt, name):
    out=[]; cur="*"
    while cur:
        r=get(f"https://api.openalex.org/works?filter={filt}&per-page=200&cursor={cur}")
        if not r: break
        j=r.json(); out+=j["results"]; cur=j["meta"].get("next_cursor")
        if not j["results"]: break
        time.sleep(0.3)
    json.dump(out, open(f"{R}/openalex_{name}.json","w")); print("openalex",name,len(out))
def crossref():
    out=[]; cur="*"
    while True:
        r=get(f"https://api.crossref.org/works?query.bibliographic=voynich&rows=500&cursor={urllib.parse.quote(cur)}&mailto=none@example.org")
        if not r: break
        m=r.json()["message"]; out+=m["items"]
        if not m["items"] or len(out)>=m["total-results"]: break
        cur=m["next-cursor"]
    json.dump(out, open(f"{R}/crossref.json","w")); print("crossref",len(out))
def arxiv():
    r=get("http://export.arxiv.org/api/query?search_query=all:voynich&max_results=500")
    open(f"{R}/arxiv.xml","w").write(r.text if r else ""); print("arxiv bytes", len(r.text) if r else 0)
def zenodo():
    out=[]; page=1
    while True:
        r=get(f"https://zenodo.org/api/records?q=voynich&size=25&page={page}&sort=mostrecent")
        if not r: break
        h=r.json()["hits"]["hits"]; out+=h
        if not h or page>60: break
        page+=1; time.sleep(1.2)
    json.dump(out, open(f"{R}/zenodo.json","w")); print("zenodo",len(out))
def s2():
    out=[]; tok=None
    fields="title,year,authors,venue,externalIds,url,openAccessPdf,abstract,publicationTypes,isOpenAccess,citationCount,publicationDate,journal"
    while True:
        u=f"https://api.semanticscholar.org/graph/v1/paper/search/bulk?query=voynich&fields={fields}"+(f"&token={tok}" if tok else "")
        r=get(u)
        if not r: break
        j=r.json(); out+=j.get("data",[]); tok=j.get("token")
        if not tok: break
        time.sleep(3)
    json.dump(out, open(f"{R}/s2.json","w")); print("s2",len(out))
which=sys.argv[1:] or ["oa","cr","ax","zn","s2"]
if "oa" in which:
    openalex("title_and_abstract.search:voynich","titleabs")
    openalex("fulltext.search:voynich","fulltext")
if "cr" in which: crossref()
if "ax" in which: arxiv()
if "zn" in which: zenodo()
if "s2" in which: s2()
