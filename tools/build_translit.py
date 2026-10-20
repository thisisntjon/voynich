"""Rebuild data/translit/*.meta.json from the fetched transliterations, and check them.

Usage: python tools/build_translit.py      (after python tools/fetch_data.py)

Most scripts read the transliteration in the scoreboard meta format (data/translit/<name>.meta.json),
built by tools/ivtff_to_meta.py. These are the recipes that reproduce the files our runs used,
byte for byte; the sha256 below is what our runs read. A different sha256 means the fetched source
changed upstream (fetch_data.py reports that too).
"""
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IV = "data/external/voynich-nu-ivtff"
RECIPES = [
    ("data/translit/ZL3b_eva.meta.json", "data/ZL3b-n.txt", [], "ce233477803a865365e5"),
    ("data/translit/ZL3b_glyphplus.meta.json", "data/ZL3b-n.txt", ["--collapse", "glyph+"], "5694caada69c"),
    ("data/translit/RF1b.meta.json", f"{IV}/RF1b-er.txt", [], "c7d9bccba99b"),
    ("data/translit/GC2a.meta.json", f"{IV}/GC2a-n.txt", [], "4edf466063bc"),
    ("data/translit/IT2a.meta.json", f"{IV}/IT2a-n.txt", [], "0d0d3e758d1e"),
]


def main():
    bad = 0
    for out, src, opts, want in RECIPES:
        o = ROOT / out
        if o.exists():
            o.unlink()  # ivtff_to_meta refuses to overwrite; this file is derived, so rebuilding is safe
        o.parent.mkdir(parents=True, exist_ok=True)
        # Relative paths from the repo root: the meta file records its source path as given.
        r = subprocess.run([sys.executable, "-I", "tools/ivtff_to_meta.py", src, out, *opts],
                           capture_output=True, text=True, cwd=ROOT)
        got = hashlib.sha256(o.read_bytes()).hexdigest() if o.exists() else "missing"
        ok = got.startswith(want)
        bad += not ok
        print(f"{'ok' if ok else 'DIFFERS'}  {out}  sha256 {got[:20]}" + ("" if ok else f" (our runs used {want}...) {r.stderr.strip()[-200:]}"))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
