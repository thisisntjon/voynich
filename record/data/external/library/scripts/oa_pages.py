import json,requests,time
for filt,name in [("title_and_abstract.search:voynich","titleabs"),("fulltext.search:voynich","fulltext")]:
    out=[];p=1
    while True:
        r=requests.get(f"https://api.openalex.org/works?filter={filt}&per-page=200&page={p}",timeout=60)
        if r.status_code!=200: print(name,p,r.status_code,r.text[:200]); break
        res=r.json()["results"]
        if not res: break
        out+=res; p+=1; time.sleep(0.5)
    json.dump(out,open(f"raw/openalex_{name}.json","w")); print(name,len(out),flush=True)
