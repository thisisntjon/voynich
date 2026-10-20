"""Download the third-party files this research reads, and check them against the copies our runs used.

Usage: python tools/fetch_data.py [--only <path prefix>]

Reads data/FETCH.tsv (dest, sha256, urls separated by spaces). Each file is downloaded from the first
URL that answers, written to its dest path, and its sha256 compared with the one our runs used.
A mismatch is reported, not hidden: the source may have been revised since we fetched it, and results
computed from a different version may differ. Files already present with the right sha256 are skipped.

These files are not redistributed here because their licences are unstated or restrictive; see
data/SOURCES.tsv. Larger sources (Yale scans, herbals, library) have their own fetch scripts in tools/.
"""
import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main(only: str | None):
    rows = list(csv.DictReader(open(ROOT / "data" / "FETCH.tsv", encoding="utf-8"), delimiter="\t"))
    ok = changed = failed = 0
    for r in rows:
        if only and not r["dest"].startswith(only):
            continue
        dest = ROOT / r["dest"]
        if dest.exists() and sha(dest.read_bytes()) == r["sha256"]:
            ok += 1
            continue
        data = None
        for url in r["urls"].split():
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "voynich-handover-fetch/1"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = resp.read()
                break
            except Exception as e:  # try the next mirror
                print(f"  {url}: {e}")
        if data is None:
            print(f"FAILED  {r['dest']}")
            failed += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        if sha(data) == r["sha256"]:
            print(f"ok      {r['dest']}")
            ok += 1
        else:
            print(f"CHANGED {r['dest']}: sha256 {sha(data)[:16]} differs from the {r['sha256'][:16]} our runs used")
            changed += 1
    print(f"{ok} match, {changed} changed upstream, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[a.index("--only") + 1] if "--only" in a else None)
