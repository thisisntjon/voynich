#!/usr/bin/env python
"""s115-A0 fetch: Bodleian MS. Canon. Misc. 408 page images (IIIF, height 1024) into data/anchor_A0/bodleian_canon_misc_408/.

Reads the canvas list from data/herbals_alchemical/bodleian_canon_misc_408/canvases_structures.tsv (derived from the
Bodleian IIIF manifest, licence CC BY-NC 4.0 in the manifest 'attribution').  Sequential, 1 s pause, 3 retries.
Writes images/<idx>_<label>.jpg and fetch_manifest.tsv (idx, canvas label, url, bytes, sha256).  Run with python -I.
"""
import csv, hashlib, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/herbals_alchemical/bodleian_canon_misc_408/canvases_structures.tsv"
OUT = ROOT / "data/anchor_A0/bodleian_canon_misc_408"


def main():
    (OUT / "images").mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(SRC, encoding="utf-8"), delimiter="\t"))
    out = []
    for r in rows:
        lab = re.sub(r"[^A-Za-z0-9]+", "_", r["canvas_label"]).strip("_")
        fn = OUT / "images" / f"{int(r['idx']):03d}_{lab}.jpg"
        url = r["image_service"].rstrip("/") + "/full/,1024/0/default.jpg"
        if not fn.exists() or fn.stat().st_size == 0:
            for k in range(4):
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "voynich-research-s115/1.0"})
                    data = urllib.request.urlopen(req, timeout=60).read()
                    if not data.startswith(b"\xff\xd8"):
                        raise ValueError("not a JPEG")
                    fn.write_bytes(data)
                    break
                except Exception as e:  # noqa: BLE001
                    print("retry", k, fn.name, e, file=sys.stderr)
                    time.sleep(3 * (k + 1))
            else:
                print("FAILED", fn.name, file=sys.stderr)
                continue
            time.sleep(1.0)
        b = fn.read_bytes()
        out.append((r["idx"], r["canvas_label"], url, len(b), hashlib.sha256(b).hexdigest(), fn.name))
        print(fn.name, len(b), flush=True)
    with open(OUT / "fetch_manifest.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("idx\tcanvas_label\turl\tbytes\tsha256\tfile\n")
        for o in out:
            f.write("\t".join(map(str, o)) + "\n")
    print("n", len(out), "of", len(rows))


if __name__ == "__main__":
    main()
