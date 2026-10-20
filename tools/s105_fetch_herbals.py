#!/usr/bin/env python
"""s105 data fetch (gate D, not scored): alchemical-herbal family scans for D-066 (l-frozen).

Sequential, polite downloads (one request at a time, 1.0 s pause, retries with back-off), height 1024 px:
  bsb_clm5905  : BSB Clm 5905 (Ebersberg 1479, Vitus Auslasser), MDZ IIIF manifest bsb00092488, every canvas from
                 the 'Beginn Herbarium' range (canvas 0192) to the end of the illustrated part (canvas 0590).
                 Licence (manifest 'license'): https://creativecommons.org/publicdomain/mark/1.0/
  bl_add41623  : BL Add MS 41623 'Codex Bellunensis', IIIF manifest
                 https://bl.digirati.io/iiif/ark:/81055/vdc_100165149757.0x000001, every canvas, size 756x1024
                 (the manifest's own image body). Usage terms: 'Public Domain in most countries other than the UK.'
Downloads land in data/herbals_alchemical/<ms>/ (untrusted data, images + metadata only); this script lives outside
that folder and is run with `python -I`. A manifest (index, label, url, bytes, sha256) is written to
data/herbals_alchemical/<ms>/manifest.json. Existing files are never overwritten (skipped, hash re-checked).

Usage: python -I tools/s105_fetch_herbals.py --ms bsb_clm5905|bl_add41623 --manifest <iiif manifest json>
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
DATA = ROOT / "data" / "herbals_alchemical"
UA = {"User-Agent": "voynich-research s105 (sequential, 1 req/s; contact via project owner)"}


def get(url, tries=5):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                b = r.read()
            if len(b) < 2000 or b[:2] != b"\xff\xd8":
                raise RuntimeError(f"not a jpeg ({len(b)} bytes)")
            return b
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
    for i, (idx, label, url) in enumerate(items):
        fn = f"{idx:04d}_{re.sub(r'[^A-Za-z0-9]+', '_', label).strip('_')}.jpg"
        p = out / fn
        if fn in have and p.exists():
            continue
        if p.exists():
            b = p.read_bytes()
        else:
            b = get(url)
            p.write_bytes(b)
            time.sleep(1.0)
        man.append({"file": fn, "canvas_index": idx, "label": label, "url": url, "bytes": len(b),
                    "sha256": hashlib.sha256(b).hexdigest()})
        man_p.write_text(json.dumps(man, indent=1), encoding="utf-8")
        print(f"{ms} {i + 1}/{len(items)} {label} {len(b)}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ms", required=True, choices=["bsb_clm5905", "bl_add41623"])
    ap.add_argument("--manifest", required=True)
    a = ap.parse_args()
    m = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    items = []
    if a.ms == "bsb_clm5905":
        for i, c in enumerate(m["sequences"][0]["canvases"], start=1):
            if 192 <= i <= 590:
                svc = c["images"][0]["resource"]["service"]["@id"]
                items.append((i, c["label"], svc + "/full/,1024/0/default.jpg"))
    else:
        for i, c in enumerate(m["items"], start=1):
            items.append((i, c["label"]["en"][0], c["items"][0]["items"][0]["body"]["id"]))
    fetch(a.ms, items)


if __name__ == "__main__":
    main()
