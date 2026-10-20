import json,requests,time,sys
R="raw"; S=requests.Session(); S.headers["User-Agent"]="voynich-library-harvest/0.1 (bibliography research)"
def g(u,**k):
    for i in range(4):
        try:
            r=S.get(u,timeout=60,**k)
            if r.status_code==429: time.sleep(10*(i+1)); continue
            return r
        except Exception as e: print("err",u[:100],e,flush=True); time.sleep(5)
def dump(n,o): json.dump(o,open(f"{R}/{n}.json","w")); print(n,len(o),flush=True)
# DBLP
r=g("https://dblp.org/search/publ/api?q=voynich&h=1000&format=json")
try:
    _d=r.json()["result"]["hits"].get("hit",[])
except Exception: _d=[]
dump("dblp",_d)
# Internet Archive
out=[]
for page in range(1,20):
    r=g("https://archive.org/advancedsearch.php",params={"q":"voynich","fl[]":["identifier","title","creator","date","year","mediatype","collection","description","licenseurl","subject","language"],"rows":500,"page":page,"output":"json"})
    if not r or not r.ok: break
    d=r.json()["response"]["docs"]; out+=d
    if len(d)<500: break
dump("internetarchive",out)
# Google Books
out=[]
for q in ["voynich manuscript","intitle:voynich","voynich cipher","voynich"]:
    for start in range(0,400,40):
        r=g("https://www.googleapis.com/books/v1/volumes",params={"q":q,"startIndex":start,"maxResults":40})
        if not r or not r.ok: print("gb",r.status_code if r else None,flush=True); break
        it=r.json().get("items",[])
        out+=it
        if len(it)<40: break
        time.sleep(1)
dump("googlebooks",out)
# Open Library
r=g("https://openlibrary.org/search.json",params={"q":"voynich","limit":1000})
dump("openlibrary", r.json().get("docs",[]) if r and r.ok else [])
# HAL
r=g("https://api.archives-ouvertes.fr/search/",params={"q":"voynich","rows":1000,"wt":"json","fl":"docid,title_s,authFullName_s,producedDateY_i,docType_s,uri_s,doiId_s,journalTitle_s,abstract_s,fileMain_s,openAccess_bool"})
dump("hal", r.json()["response"]["docs"] if r and r.ok else [])
# Europe PMC
r=g("https://www.ebi.ac.uk/europepmc/webservices/rest/search",params={"query":"voynich","format":"json","pageSize":1000,"resultType":"core"})
dump("europepmc", r.json().get("resultList",{}).get("result",[]) if r and r.ok else [])
# arXiv by title/abstract
r=g("https://export.arxiv.org/api/query",params={"search_query":"ti:voynich OR abs:voynich","max_results":500})
open(f"{R}/arxiv2.xml","w").write(r.text if r else ""); print("arxiv2",r.text.count("<entry>") if r else 0,flush=True)
# Crossref title query
out=[]; cur="*"
while True:
    r=g("https://api.crossref.org/works",params={"query":"voynich","rows":1000,"cursor":cur,"mailto":"none@example.org"})
    if not r or not r.ok: break
    m=r.json()["message"]; out+=m["items"]
    if not m["items"] or len(out)>=m["total-results"] or len(out)>=3000: break
    cur=m["next-cursor"]
dump("crossref_query",out)
