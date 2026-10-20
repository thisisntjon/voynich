import requests,json,time,html,re
S=requests.Session(); S.headers["User-Agent"]="Mozilla/5.0 voynich-library-research"
out=[]
selfhosted=["ciphermysteries.com","voynichportal.com","www.voynich.ninja"]
wpcom=["manuscriptroadtrip.wordpress.com","voynichimagery.wordpress.com","herculeaninquiries.wordpress.com","marcoponzi.wordpress.com","voynichthoughts.wordpress.com","bi3mw.de","stephenbax.net","proto-romance.com","voynichmanuscript.wordpress.com","voynichresearch.wordpress.com","koen-g.github.io","ellievelinska.wordpress.com"]
def wp(base,api):
    n=0
    for page in range(1,40):
        u=f"{api}?search=voynich&per_page=100&page={page}&_fields=id,date,link,title,excerpt" if 'wp-json' in api else f"{api}?search=voynich&number=100&page={page}&fields=ID,date,URL,title,excerpt"
        try: r=S.get(u,timeout=60)
        except Exception as e: print(base,'err',e); break
        if r.status_code!=200: print(base,page,r.status_code); break
        try: j=r.json()
        except Exception: print(base,'nonjson',r.text[:80]); break
        posts=j if isinstance(j,list) else j.get('posts',[])
        if not posts: break
        for p in posts:
            t=p['title']['rendered'] if isinstance(p.get('title'),dict) else p.get('title')
            ex=p['excerpt']['rendered'] if isinstance(p.get('excerpt'),dict) else p.get('excerpt','')
            out.append(dict(site=base,date=p.get('date'),url=p.get('link') or p.get('URL'),title=html.unescape(re.sub('<[^>]+>','',t or '')),excerpt=' '.join(html.unescape(re.sub('<[^>]+>',' ',ex or '')).split())[:400]))
            n+=1
        time.sleep(1)
    print(base,n,flush=True)
for b in selfhosted: wp(b,f"https://{b}/wp-json/wp/v2/posts")
for b in wpcom: wp(b,f"https://public-api.wordpress.com/rest/v1.1/sites/{b}/posts/")
json.dump(out,open('raw/blogs.json','w'),ensure_ascii=False); print('total',len(out))
