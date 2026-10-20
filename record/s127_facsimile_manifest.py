"""s127 step 1: full-facsimile manifest. Reuses s45 scans (data/external/yale_scans/pages, read-only),
downloads only canvases missing there into data/facsimile_full/extra/, writes data/facsimile_full/MANIFEST.tsv.
Sequential, 2 s pause, 3 retries. Never overwrites existing files. Rights: Yale images kept local only."""
import json, os, hashlib, time, urllib.request
from PIL import Image
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "data", "external", "yale_scans")
OUT = os.path.join(ROOT, "data", "facsimile_full"); EXTRA = os.path.join(OUT, "extra")
os.makedirs(EXTRA, exist_ok=True)
man = json.load(open(os.path.join(SRC, "manifest_2002046.json"), encoding="utf-8"))
have = {int(f[:3]): f for f in os.listdir(os.path.join(SRC, "pages")) if f.endswith(".jpg")}
def sha(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()
rows, fails = [], []
for i, c in enumerate(man["items"], 1):
    label = c["label"].get("none", ["?"])[0]
    svc = c["items"][0]["items"][0]["body"]["service"]
    svc = svc[0] if isinstance(svc, list) else svc
    sid = svc.get("@id") or svc.get("id")
    if i in have:
        p = os.path.join(SRC, "pages", have[i]); origin = "s45_reuse"
    else:
        safe = "".join(ch if ch.isalnum() else "_" for ch in label).strip("_")
        p = os.path.join(EXTRA, f"{i:03d}_{safe}.jpg"); origin = "s127_download"
        if not os.path.exists(p):
            url = sid + "/full/full/0/default.jpg"; ok = False
            for a in range(3):
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "voynich-research-s127 (personal, local copy)"})
                    data = urllib.request.urlopen(req, timeout=120).read()
                    open(p + ".part", "wb").write(data); os.replace(p + ".part", p); ok = True; break
                except Exception as e:
                    print("retry", i, a, e); time.sleep(5 * (a + 1))
            time.sleep(2)
            if not ok: fails.append((i, label)); continue
    w, h = Image.open(p).size
    rows.append([str(i), label, os.path.relpath(p, ROOT).replace("\\", "/"), sid, sha(p), f"{w}x{h}", str(os.path.getsize(p)), origin])
with open(os.path.join(OUT, "MANIFEST.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("canvas\tfolio_label\tfile\tiiif_service\tsha256\tpixels\tbytes\torigin\n")
    for r in rows: f.write("\t".join(r) + "\n")
tot = sum(int(r[6]) for r in rows)
print(f"canvases={len(man['items'])} listed={len(rows)} failures={fails} total_bytes={tot}")
