#!/usr/bin/env python
"""Fetch the public Yale Beinecke MS 408 ("Cipher Manuscript") scans via IIIF (s45, O-048).

Source: IIIF Presentation v3 manifest https://collections.library.yale.edu/manifests/2002046
Each canvas carries one IIIF Image API service; we fetch <service>/full/<SIZE>/0/default.jpg
for every canvas whose label names a folio (labels like "1r", "69v and 70r", "85r (part)");
covers, flyleaves, head/tail/spine/fore-edge are skipped.

Rules (PLAN.md 22:29 s45 approval): everything lands in data/external/yale_scans/ (untrusted),
JPEG/JSON only, HEAD-then-GET with a running byte total that STOPS above 6 GB, every URL /
byte count / sha256 logged to data/external/yale_scans/MANIFEST.md.  Run with `python -I`
from the project root:

    python -I tools/fetch_yale_scans.py [--size full|2000,] [--workers 4] [--limit N]

Idempotent: a file whose sha256 line is already in MANIFEST.md is not fetched again.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "external" / "yale_scans"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
CAP_BYTES = 6 * 1024 ** 3
UA = "voynich-s45-fetch/1.0 (research; python urllib)"
FOLIO_RE = re.compile(r"\d+[rv]")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def http_head(url: str) -> int | None:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            cl = r.headers.get("Content-Length")
            return int(cl) if cl else None
    except Exception:
        return None


def http_get(url: str, dest: Path, retries: int = 3) -> int:
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r, dest.open("wb") as f:
                n = 0
                for chunk in iter(lambda: r.read(1 << 18), b""):
                    f.write(chunk)
                    n += len(chunk)
            return n
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 + 3 * attempt)
    raise RuntimeError(f"GET failed {url}: {last}")


def label_text(lbl) -> str:
    if isinstance(lbl, dict):
        for v in lbl.values():
            if isinstance(v, list) and v:
                return str(v[0])
    return str(lbl)


def safe_name(label: str) -> str:
    s = label.lower()
    s = s.replace(" and ", "_and_").replace("(part of 85-86 foldout)", "p8586")
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s


def parse_canvases(man: dict) -> list[dict]:
    out = []
    for i, c in enumerate(man.get("items", [])):
        label = label_text(c.get("label", ""))
        svc = None
        for ap in c.get("items", []):
            for an in ap.get("items", []):
                body = an.get("body", {})
                for s in body.get("service", []) or []:
                    svc = s.get("id") or s.get("@id")
        out.append(dict(index=i, label=label, service=svc,
                        width=c.get("width"), height=c.get("height")))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--size", default="full", help="IIIF size segment: 'full' or e.g. '2000,'")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0, help="debug: fetch at most N canvases")
    args = ap.parse_args(argv)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pages").mkdir(exist_ok=True)
    manifest_path = OUT / "manifest_2002046.json"
    log_path = OUT / "MANIFEST.md"

    done = set()
    if log_path.exists():
        for ln in log_path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\| (\S+) \|", ln)
            if m:
                done.add(m.group(1))
    else:
        log_path.write_text(
            "# data/external/yale_scans/MANIFEST.md — s45 Yale IIIF scans (untrusted downloads)\n\n"
            f"Source manifest: {MANIFEST_URL}\nFetched by tools/fetch_yale_scans.py (size={args.size}); "
            "byte cap 6 GB.  Rights: public domain per the Yale catalog.\n\n"
            "| file | label | url | bytes | sha256 |\n|---|---|---|---|---|\n", encoding="utf-8")

    t0 = time.time()
    if not manifest_path.exists():
        n = http_get(MANIFEST_URL, manifest_path)
        print(f"manifest: {n} bytes sha256={sha256_file(manifest_path)}")
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"| manifest_2002046.json | (manifest) | {MANIFEST_URL} | {n} | {sha256_file(manifest_path)} |\n")
    man = json.loads(manifest_path.read_text(encoding="utf-8"))
    canvases = parse_canvases(man)
    jobs = [c for c in canvases if c["service"] and FOLIO_RE.search(c["label"])]
    if args.limit:
        jobs = jobs[: args.limit]
    print(f"{len(canvases)} canvases, {len(jobs)} folio-labelled canvases to fetch (size={args.size})")

    # HEAD probe on the first job to estimate total
    probe = jobs[0]
    purl = f"{probe['service']}/full/{args.size}/0/default.jpg"
    cl = http_head(purl)
    print(f"HEAD {purl} -> Content-Length={cl}")
    if cl and cl * len(jobs) > CAP_BYTES:
        print(f"STOP: estimated total {cl * len(jobs) / 1e9:.2f} GB exceeds 6 GB cap"); return 2

    total = sum(p.stat().st_size for p in (OUT / "pages").glob("*.jpg"))
    index_rows = []

    def one(c):
        name = f"{c['index']:03d}_{safe_name(c['label'])}.jpg"
        dest = OUT / "pages" / name
        url = f"{c['service']}/full/{args.size}/0/default.jpg"
        if name in done and dest.exists():
            return name, c, url, dest.stat().st_size, None, True
        n = http_get(url, dest)
        return name, c, url, n, sha256_file(dest), False

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(one, c) for c in jobs]
        for k, fu in enumerate(as_completed(futs), 1):
            name, c, url, n, h, skipped = fu.result()
            index_rows.append(dict(file=name, label=c["label"], index=c["index"], service=c["service"],
                                   width=c["width"], height=c["height"], url=url, bytes=n))
            if not skipped:
                total += n
                with log_path.open("a", encoding="utf-8") as f:
                    f.write(f"| {name} | {c['label']} | {url} | {n} | {h} |\n")
            print(f"[{k}/{len(jobs)}] {name} {n} bytes {'(cached)' if skipped else ''} total={total / 1e6:.0f} MB", flush=True)
            if total > CAP_BYTES:
                print("STOP: 6 GB cap reached; cancelling remaining fetches")
                for f2 in futs:
                    f2.cancel()
                break
    index_rows.sort(key=lambda r: r["index"])
    (OUT / "pages_index.json").write_text(json.dumps(index_rows, indent=1), encoding="utf-8")
    print(f"done: {len(index_rows)} files, {total / 1e6:.0f} MB on disk, {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
