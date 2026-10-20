#!/usr/bin/env python
"""s103 data fetch (not scored): period illustrated herbals for the D-066 (i) comparison.

Sequential, polite downloads (one request at a time, 1.0 s pause, retries with back-off), modest resolution:
  ljs419    : Penn Oversize LJS 419 'Erbario', OPenn web derivatives (1800 px high), every <surface> in the TEI.
              OPenn https was too slow (TLS resets, ~1 file/min; 2 files fetched, kept), so the same Penn images are
              taken from Penn's IIIF image server (Colenda manifest), height 1024 px, into ljs419/iiif/
              (--ms ljs419_iiif --manifest <colenda manifest>).
              Images: Public Domain Mark 1.0; metadata CC-BY-4.0 (OPenn page).
  sloane4016: BL Sloane MS 4016 'Herbal', IIIF level-0 thumbnail size 769x1024 from the BL manifest.
              Usage terms (manifest metadata): 'Public Domain in most countries other than the UK.'
Downloads land in data/herbals_period/<ms>/ (untrusted data, images + metadata only); this script lives outside
that folder and is run with `python -I`.  A manifest (folio, url, bytes, sha256) is written to
data/herbals_period/<ms>/manifest.json.  Existing files are never overwritten (skipped, hash re-checked).

Usage: python -I tools/s103_fetch_herbals.py --ms ljs419 --tei <path> | --ms sloane4016 --manifest <path>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "herbals_period"
UA = {"User-Agent": "voynich-research s103 (sequential, 1 req/s; contact via project owner)"}


def get(url, tries=5):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            print(f"  retry {k + 1} {url}: {e}", flush=True)
            time.sleep(3 * (k + 1))
    raise RuntimeError(f"failed {url}")


def fetch(ms, items):
    out = DATA / ms
    out.mkdir(parents=True, exist_ok=True)
    man_p = out / "manifest.json"
    man = json.loads(man_p.read_text(encoding="utf-8")) if man_p.exists() else []
    have = {m["file"] for m in man}
    for i, (folio, url) in enumerate(items):
        fn = f"{i:04d}_{re.sub(r'[^A-Za-z0-9]+', '_', folio).strip('_')}.jpg"
        p = out / fn
        if fn in have and p.exists():
            continue
        if p.exists():
            b = p.read_bytes()
        else:
            b = get(url)
            p.write_bytes(b)
            time.sleep(1.0)
        man.append({"file": fn, "folio": folio, "url": url, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()})
        man_p.write_text(json.dumps(man, indent=1), encoding="utf-8")
        print(f"{ms} {i + 1}/{len(items)} {folio} {len(b)}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ms", required=True, choices=["ljs419", "ljs419_iiif", "sloane4016"])
    ap.add_argument("--tei")
    ap.add_argument("--manifest")
    a = ap.parse_args()
    if a.ms == "ljs419":
        t = Path(a.tei).read_text(encoding="utf-8")
        items = []
        for m in re.finditer(r'<surface n="([^"]+)"[^>]*>(.*?)</surface>', t, re.S):
            w = re.search(r'url="(web/[^"]+_web\.jpg)"', m.group(2))
            if w:
                items.append((m.group(1), "https://openn.library.upenn.edu/Data/0001/ljs419/data/" + w.group(1)))
    elif a.ms == "ljs419_iiif":
        m = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
        items = []
        for c in m["sequences"][0]["canvases"]:
            svc = c["images"][0]["resource"]["service"]["@id"]
            items.append((c["label"], svc + "/full/,1024/0/default.jpg"))
        fetch("ljs419/iiif", items)
        return
    else:
        m = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
        items = []
        for c in m["items"]:
            lab = c["label"]["en"][0]
            body = c["items"][0]["items"][0]["body"]["id"]
            items.append((lab, body))
    fetch(a.ms, items)


if __name__ == "__main__":
    main()
