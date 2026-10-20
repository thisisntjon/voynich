"""Wave-5 library collector: gather open sources into data/external/wave5-<slug>/.

Collection ONLY (user instruction 2026-10-18: gather + validate, sort later).
Nothing here is ingested into findings/VKB. Each item records: source URL,
licence evidence, bytes, sha256, magic-byte check, HTTP status. Downloads are
untrusted: never execute code from data/external (see its README).

Run: python -I tools/fetch_library_wave5.py
Re-runs skip files already present with the same size.
"""
import hashlib, json, os, sys, urllib.request, urllib.error

ROOT = os.path.join("data", "external")  # relative: \\?\ long-path root breaks makedirs
UA = {"User-Agent": "voynich-wave5-collector/1.0 (research library staging)"}
MAX_BYTES = 80_000_000

def get(url, timeout=120):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

def magic_ok(kind, b):
    if kind == "pdf": return b[:5] == b"%PDF-"
    if kind == "zip": return b[:2] == b"PK"
    if kind == "text": return b"<html" not in b[:512].lower() and b"<!doctype" not in b[:512].lower()
    if kind == "xml": return b"<?xml" in b[:512] or b"<TEI" in b[:4096]
    if kind == "any": return len(b) > 0
    return False

def save(slug, fname, url, kind, license_note, manifest):
    d = os.path.join(ROOT, "wave5-" + slug)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, fname)
    rec = {"slug": slug, "file": fname, "url": url, "kind": kind, "license": license_note}
    try:
        status, b = get(url)
        rec["http"] = status
        if len(b) > MAX_BYTES:
            rec.update(status="SKIPPED-TOO-LARGE", bytes=len(b)); manifest.append(rec); print(rec); return
        rec["bytes"] = len(b)
        rec["sha256"] = hashlib.sha256(b).hexdigest()
        rec["md5"] = hashlib.md5(b).hexdigest()
        rec["magic_ok"] = magic_ok(kind, b)
        if not rec["magic_ok"]:
            fname2 = fname + ".SUSPECT"
            with open(os.path.join(d, fname2), "wb") as f: f.write(b)
            rec.update(status="SUSPECT-MAGIC", saved_as=fname2)
        else:
            if os.path.exists(path) and os.path.getsize(path) == len(b):
                rec["status"] = "ALREADY-PRESENT"
            else:
                with open(path, "wb") as f: f.write(b)
                rec["status"] = "FETCHED"
    except Exception as e:
        rec.update(status="FAILED", error=f"{type(e).__name__}: {e}")
    manifest.append(rec); print(json.dumps(rec)[:300])

def zenodo(slug, recid, manifest):
    try:
        _, raw = get(f"https://zenodo.org/api/records/{recid}")
        meta = json.loads(raw)
        lic = (meta.get("metadata", {}).get("license") or {}).get("id", "see record")
        for fl in meta.get("files", []):
            if fl.get("size", 0) > MAX_BYTES:
                manifest.append({"slug": slug, "file": fl["key"], "status": "SKIPPED-TOO-LARGE",
                                 "bytes": fl.get("size"), "license": lic, "url": fl["links"]["self"]})
                continue
            kind = "xml" if fl["key"].endswith(".xml") else ("zip" if fl["key"].endswith(".zip") else "any")
            save(slug, fl["key"], fl["links"]["self"], kind, f"Zenodo {recid} license={lic}", manifest)
    except Exception as e:
        manifest.append({"slug": slug, "status": "FAILED-ZENODO-API", "error": str(e)})

def github(slug, repo, manifest):
    lic = "see repo"
    branch = "main"
    try:
        _, raw = get(f"https://api.github.com/repos/{repo}")
        m = json.loads(raw)
        branch = m.get("default_branch", "main")
        lic = ((m.get("license") or {}).get("spdx_id")) or "no LICENSE via API"
    except Exception as e:
        manifest.append({"slug": slug, "status": "GITHUB-API-FAILED", "error": str(e)})
    save(slug, repo.replace("/", "-") + ".zip",
         f"https://codeload.github.com/{repo}/zip/refs/heads/{branch}",
         "zip", f"GitHub {repo} license={lic} branch={branch}", manifest)

def main():
    M = []
    # CEUR-WS Vol-3313 remaining papers (have 4, 6, 10 locally). Volume licence CC-BY-4.0.
    for n in [1, 2, 3, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16]:
        save("ceur3313", f"paper{n}.pdf", f"https://ceur-ws.org/Vol-3313/paper{n}.pdf",
             "pdf", "CEUR-WS Vol-3313 CC-BY-4.0 (volume page fetched Wave 5)", M)
    save("beasley-2024", "2024_Beasley_Bryce_Thesis.pdf",
         "https://shareok.org/bitstreams/7915fbcc-74be-4c0a-b0f5-8a1658cb3d41/download",
         "pdf", "ShareOK OU thesis, open bitstream; item page fetched 2026-10-18 (607.04 KB stated)", M)
    save("parisel-2025", "parisel_arxiv_2509.10573.pdf", "https://arxiv.org/pdf/2509.10573",
         "pdf", "arXiv nonexclusive; abstract page states CC-BY-4.0 per Wave 5 fetch", M)
    save("rao-2010-indus", "rao_etal_2010_J10-4016.pdf", "https://aclanthology.org/J10-4016.pdf",
         "pdf", "ACL Anthology open", M)
    zenodo("decknamen-tei", 14638445, M)          # validated: cc-by-4.0
    zenodo("htr-model-medieval", 7547438, M)      # CATMuS-era HTR model
    github("ndd-entropy", "simomarsili/ndd", M)
    github("neurodecipher", "j-luo93/NeuroDecipher", M)
    github("cnt-tironian", "transcribo442nal/cnt-tabs-image-corpus", M)
    github("naibbe-code", "greshko/naibbe-cipher", M)
    save("fuchs-1542", "Dehistoriastirp00Fuch_djvu.txt",
         "https://archive.org/download/Dehistoriastirp00Fuch/Dehistoriastirp00Fuch_djvu.txt",
         "text", "Public domain per BHL/archive.org item page (Wave 5 fetch)", M)
    save("geomancy-fasciculus", "b3299753x_djvu.txt",
         "https://archive.org/download/b3299753x/b3299753x_djvu.txt",
         "text", "archive.org public-domain scan set; item verified Wave 5", M)
    out = os.path.join(ROOT, "wave5-MANIFEST.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(M, f, indent=1)
    ok = sum(1 for r in M if r.get("status") in ("FETCHED", "ALREADY-PRESENT"))
    print(f"MANIFEST {out} items={len(M)} ok={ok}")

if __name__ == "__main__":
    main()
