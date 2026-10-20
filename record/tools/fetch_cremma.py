"""Fetch the CREMMA Medii Aevi (HTR-United CREMMA-Medieval-LAT) transcription XML, plain
variant only, pinned to release tag v0.1.2, into data/external/cremma/.

Scope (approved 2026-10-17, phase-1 s18): `data/*/*.xml` excluding `*.chocomufin.xml`, plus
README.md, data-registry.csv, table.csv and htr-united.yml from the repo root. No images, no
chocomufin variant, no txt. Hard stop: if the selected byte sum exceeds 200 MB nothing is
downloaded.

Method:
  1. GET https://api.github.com/repos/HTR-United/CREMMA-Medieval-LAT/git/trees/<TAG_SHA>?recursive=1
     (TAG_SHA is the commit the v0.1.2 tag points at; the tree lists path, size and git blob
     SHA-1 for every file).
  2. Select the paths above, print the byte sum, abort if > 200_000_000.
  3. For each selected path: if --reuse DIR holds the same relative path and its git blob
     SHA-1 (sha1(b"blob <len>\\0" + bytes)) equals the tree's, copy that file instead of
     downloading; otherwise GET https://raw.githubusercontent.com/HTR-United/CREMMA-Medieval-LAT/v0.1.2/<path>.
  4. Verify every written file against the tree's blob SHA-1; any mismatch is deleted and
     counted as a failure (exit 1).
  5. Write <dest>/FETCH-MANIFEST.txt (tab-separated: path, bytes, sha1, source) and
     <dest>/tree_v0.1.2.json (the raw tree response, for provenance).

Run from the project root, script outside the data folder, isolated interpreter:
    python -I tools/fetch_cremma.py --dest data/external/cremma --reuse data/external/cremma-medieval-lat-mlc1
The destination must not exist or must be empty.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO = "HTR-United/CREMMA-Medieval-LAT"
TAG = "v0.1.2"
TAG_SHA = "9439fe33a07eeb2814fa4b94b65c280f20aa6ec1"
TREE_URL = f"https://api.github.com/repos/{REPO}/git/trees/{TAG_SHA}?recursive=1"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{TAG}/"
LIMIT = 200_000_000
XML_RE = re.compile(r"^data/[^/]+/[^/]+\.xml$")
ROOT_META = {"README.md", "data-registry.csv", "table.csv", "htr-united.yml"}
UA = {"User-Agent": "voynich-phase1-s18-fetch (python urllib)"}


def blob_sha1(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(f"blob {len(data)}\0".encode("ascii"))
    h.update(data)
    return h.hexdigest()


def http_get(url: str, retries: int = 3) -> bytes:
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"GET failed after {retries} tries: {url}: {last}")


def select(tree: dict) -> list[dict]:
    if tree.get("truncated"):
        sys.exit("tree response is truncated; refusing to continue")
    out = []
    for e in tree["tree"]:
        if e["type"] != "blob":
            continue
        p = e["path"]
        if (XML_RE.match(p) and not p.endswith(".chocomufin.xml")) or p in ROOT_META:
            out.append(e)
    return sorted(out, key=lambda e: e["path"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest", type=Path, required=True)
    ap.add_argument("--reuse", type=Path, default=None,
                    help="existing folder with the same relative layout; byte-identical files "
                         "(same git blob SHA-1) are copied from here instead of downloaded")
    ap.add_argument("--tree-json", type=Path, default=None,
                    help="use a saved tree response instead of calling the API")
    a = ap.parse_args(argv)

    dest: Path = a.dest
    if dest.exists() and any(dest.iterdir()):
        sys.exit(f"destination {dest} exists and is not empty; refusing")
    dest.mkdir(parents=True, exist_ok=True)

    if a.tree_json:
        tree_bytes = a.tree_json.read_bytes()
    else:
        tree_bytes = http_get(TREE_URL)
    tree = json.loads(tree_bytes.decode("utf-8"))
    if tree.get("sha") != TAG_SHA:
        sys.exit(f"tree sha {tree.get('sha')} != expected {TAG_SHA}")
    (dest / f"tree_{TAG}.json").write_bytes(tree_bytes)

    sel = select(tree)
    xml = [e for e in sel if e["path"].endswith(".xml")]
    meta = [e for e in sel if not e["path"].endswith(".xml")]
    total = sum(e["size"] for e in sel)
    print(f"selected {len(sel)} files: {len(xml)} plain xml = {sum(e['size'] for e in xml):,} B; "
          f"{len(meta)} metadata = {sum(e['size'] for e in meta):,} B; total {total:,} B")
    if total > LIMIT:
        sys.exit(f"ABORT: {total:,} B exceeds the {LIMIT:,} B limit; nothing downloaded")

    rows = []
    n_dl = n_cp = b_dl = b_cp = 0
    failures = []
    for e in sel:
        rel, size, sha = e["path"], e["size"], e["sha"]
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        src = "downloaded"
        data = None
        if a.reuse is not None:
            cand = a.reuse / rel
            if cand.is_file():
                cb = cand.read_bytes()
                if len(cb) == size and blob_sha1(cb) == sha:
                    data = cb
                    src = "copied-from-mlc1"
        if data is None:
            data = http_get(RAW_BASE + urllib.parse.quote(rel))
        got = blob_sha1(data)
        if len(data) != size or got != sha:
            failures.append((rel, size, len(data), sha, got))
            print(f"MISMATCH {rel}: size {len(data)} vs {size}, sha1 {got} vs {sha}", file=sys.stderr)
            continue
        target.write_bytes(data)
        if src == "downloaded":
            n_dl += 1
            b_dl += size
        else:
            n_cp += 1
            b_cp += size
        rows.append((rel, size, sha, src))
        print(f"{src:18} {size:9,} {rel}")

    # re-verify from disk
    bad_disk = []
    for rel, size, sha, _ in rows:
        d = (dest / rel).read_bytes()
        if len(d) != size or blob_sha1(d) != sha:
            bad_disk.append(rel)
    man = dest / "FETCH-MANIFEST.txt"
    with man.open("w", encoding="utf-8", newline="\n") as f:
        f.write(f"# CREMMA-Medieval-LAT {TAG} (tree {TAG_SHA}); sha1 = git blob SHA-1 from the tree API, "
                f"verified on the bytes written\n")
        f.write("# path\tbytes\tsha1\tsource\n")
        for rel, size, sha, src in rows:
            f.write(f"{rel}\t{size}\t{sha}\t{src}\n")
    print(f"written {len(rows)} files: downloaded {n_dl} ({b_dl:,} B), copied {n_cp} ({b_cp:,} B); "
          f"mismatches {len(failures)}; disk re-verify failures {len(bad_disk)}")
    print(f"manifest: {man}")
    return 1 if (failures or bad_disk) else 0


if __name__ == "__main__":
    sys.exit(main())
