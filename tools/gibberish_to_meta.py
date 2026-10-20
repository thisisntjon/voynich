"""Convert the Gaskell-Bowern (2022) volunteer gibberish texts into scoreboard sidecars.

Source: data/external/gaskell-bowern-gibberish/danielgaskell-voynich-main/voynich-main/
        data/gibberish_transcriptions/"Gibberish - <WRITER>.txt"  (38 files, CRLF, a few
        accented Latin letters, '_' rules as page separators, '-' at line end as a
        hyphenation mark, stray punctuation).
Output: data/controls_gibberish/gib_<WRITER>.meta.json (38 files) plus gib_pooled.meta.json
        (all writers concatenated, one page block per writer), PREREG-v2 sidecar format
        {"name", "tokenization", "source", "pages": [{"id","section","hand","lang","quire",
         "lines": [[tok, ...], ...]}, ...]}
        one corpus per text, writer id as "hand", section "gib", lang "?", quire "?",
        wrapped 8 tokens/line, 20 lines/page; tokens are lowercase a-z only.

Token rule (PREREG-v2 §7, family X):
  1. lines are read in file order; a line made only of '_' is a page separator in the
     source and is dropped (the 8x20 wrap below is the only page structure kept);
  2. a token ending in '-' at the end of a source line is joined to the first token of
     the next non-empty line (hyphenation);
  3. each token is NFKD-decomposed, combining marks removed, lowercased, and every
     character outside a-z deleted; empty results are dropped.

Run from the project root with the isolated interpreter (the source is external data):
    python -I tools/gibberish_to_meta.py [--src DIR] [--dst DIR]
Prints one line per writer with the token count and a total; writes nothing else.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = (ROOT / "data" / "external" / "gaskell-bowern-gibberish" / "danielgaskell-voynich-main"
       / "voynich-main" / "data" / "gibberish_transcriptions")
DST = ROOT / "data" / "controls_gibberish"
LINE_LEN, PAGE_LEN = 8, 20
NAME_RE = re.compile(r"^Gibberish - (.+)\.txt$")


def clean_token(tok: str) -> str:
    s = unicodedata.normalize("NFKD", tok)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z]", "", s)


def tokens_of(text: str) -> list[str]:
    raw_lines = [ln.strip() for ln in text.splitlines()]
    out: list[str] = []
    carry = ""
    for ln in raw_lines:
        if not ln or set(ln) <= {"_"}:
            continue
        parts = ln.split()
        if carry:
            parts[0] = carry + parts[0]
            carry = ""
        if parts[-1].endswith("-") and len(parts[-1]) > 1:
            carry = parts.pop().rstrip("-")
        for p in parts:
            t = clean_token(p)
            if t:
                out.append(t)
    if carry:
        t = clean_token(carry)
        if t:
            out.append(t)
    return out


def wrap(tokens: list[str], writer: str) -> list[dict]:
    lines = [tokens[i:i + LINE_LEN] for i in range(0, len(tokens), LINE_LEN)]
    pages = []
    for k, i in enumerate(range(0, len(lines), PAGE_LEN)):
        pages.append(dict(id=f"{writer}_p{k:03d}", section="gib", hand=writer, lang="?",
                          quire="?", lines=lines[i:i + PAGE_LEN]))
    return pages


def convert(src: Path, dst: Path) -> list[tuple[str, int]]:
    dst.mkdir(parents=True, exist_ok=True)
    counts = []
    pooled_pages = []
    for f in sorted(src.glob("*.txt")):
        m = NAME_RE.match(f.name)
        if not m:
            print(f"skip (name pattern): {f.name}", file=sys.stderr)
            continue
        writer = m.group(1).strip().replace(" ", "_")
        toks = tokens_of(f.read_text(encoding="utf-8", errors="strict"))
        name = f"gib_{writer}"
        doc = dict(name=name, tokenization="latin",
                   source=f"Gaskell & Bowern 2022 volunteer gibberish, writer {writer}, "
                          f"file {f.name}; tools/gibberish_to_meta.py: a-z only, "
                          f"{LINE_LEN} tokens/line, {PAGE_LEN} lines/page",
                   pages=wrap(toks, writer))
        (dst / f"{name}.meta.json").write_text(json.dumps(doc, ensure_ascii=True),
                                                encoding="utf-8")
        counts.append((name, len(toks)))
        pooled_pages.extend(doc["pages"])
    pooled = dict(name="gib_pooled", tokenization="latin",
                  source="Gaskell & Bowern 2022 volunteer gibberish, all writers concatenated in "
                         "file order, one page block per writer (hand = writer id); same token "
                         "rule as the per-writer files",
                  pages=pooled_pages)
    (dst / "gib_pooled.meta.json").write_text(json.dumps(pooled, ensure_ascii=True), encoding="utf-8")
    counts.append(("gib_pooled", sum(len(ln) for p in pooled_pages for ln in p["lines"])))
    return counts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, default=SRC)
    ap.add_argument("--dst", type=Path, default=DST)
    a = ap.parse_args(argv)
    counts = convert(a.src, a.dst)
    for name, n in counts:
        print(f"{name:16} tokens={n}")
    per = [c for c in counts if c[0] != "gib_pooled"]
    print(f"writers={len(per)} total_tokens={sum(n for _, n in per)} (+ gib_pooled.meta.json) -> {a.dst}")


if __name__ == "__main__":
    main()
