"""Convert an IVTFF transliteration file into the scoreboard meta.json page format:

    {"source": ..., "alphabet": ..., "pages": [{"id", "section", "hand", "lang", "quire",
                                                 "lines": [[tok, ...], ...]}, ...]}

Usage (run with -I; the input dirs are untrusted downloads):
    python -I tools/ivtff_to_meta.py IN.txt OUT.meta.json [--collapse glyph+] [--check]

Rules (mirror vparse.clean so ZL3b round-trips to corpora.voynich / metrics_new.voynich_pages):
  * paragraph loci only: locus type (after the comma + one char) starts with 'P';
  * page variables $I (illustration/section), $H (hand), $L (Currier language),
    $Q (quire) from the <fNN> <! ... > header line;
  * <!...> inline comments removed; <-> (drawing interruption) is a word break;
    every other <...> tag removed;
  * [a:b] alternatives -> a; {..} ligature braces removed, contents kept;
    @nnn; extended-glyph codes -> '?' (the token is then dropped, as in vparse);
    "'" removed; ',' (uncertain space) is a word break;
  * tokens containing '?' (unreadable glyph) are dropped; empty lines are dropped;
  * alphabet-specific: for the v101 alphabet (GC) the characters ! # % * are v101
    glyphs (the original voyn_101.txt has them with identical counts) and are kept;
    for Eva files '!' is the IVTFF placeholder (removed) and '*' is unreadable ('?').
  * --collapse glyph | glyph+ : corpora.to_glyphs with GLYPHS / GLYPHS_PLUS
    (multi-letter EVA glyphs -> single private-use chars), Eva files only.
No existing file is modified; the output path must not exist unless --force.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGE_RE = re.compile(r"^<(f\w+)>\s+<!(.*)>")
LINE_RE = re.compile(r"^<(f\w+)\.(\d+),(.)(\w+)>\s*(.*)$")
VAR_RE = re.compile(r"\$(\w)=(\w+)")
HDR_RE = re.compile(r"^#=IVTFF\s+(\S+)\s+(\S+)")


def clean(text, v101=False):
    text = re.sub(r"<![^>]*>", "", text)                      # inline comments
    text = re.sub(r"<->", ".", text)                          # drawing interruption
    text = re.sub(r"<[^>]*>", "", text)                       # <%> <$> <~> ...
    text = re.sub(r"\[([^:\]]*)(:[^\]]*)?\]", r"\1", text)   # [a:b] -> a
    text = re.sub(r"@\d+;", "?", text)                        # extended glyph -> unreadable
    text = text.replace("{", "").replace("}", "").replace("'", "")
    if not v101:
        text = text.replace("!", "").replace("*", "?")
    text = text.replace(",", ".")
    return [w for w in text.split(".") if w]


def convert(path, collapse=None):
    path = Path(path)
    alphabet = "?"
    pages, cur, meta = [], None, {}
    n_dropped = 0
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if raw.startswith("#"):
            m = HDR_RE.match(raw)
            if m:
                alphabet = m.group(1)
            continue
        if not raw.strip():
            continue
        m = PAGE_RE.match(raw)
        if m:
            meta = dict(VAR_RE.findall(m.group(2)))
            cur = dict(id=m.group(1), section=meta.get("I", "?"), hand=meta.get("H", "?"),
                       lang=meta.get("L", "?"), quire=meta.get("Q", "?"), lines=[])
            pages.append(cur)
            continue
        m = LINE_RE.match(raw)
        if not m:
            continue
        page, _n, _c, unit, text = m.groups()
        if not unit.startswith("P"):
            continue
        if cur is None or cur["id"] != page:
            cur = dict(id=page, section=meta.get("I", "?"), hand=meta.get("H", "?"),
                       lang=meta.get("L", "?"), quire=meta.get("Q", "?"), lines=[])
            pages.append(cur)
        ws = clean(text, v101=alphabet.lower().startswith("v101"))
        kept = [w for w in ws if "?" not in w]
        n_dropped += len(ws) - len(kept)
        if collapse:
            sys.path.insert(0, str(ROOT))
            import corpora  # noqa: E402
            units = corpora.GLYPHS_PLUS if collapse == "glyph+" else corpora.GLYPHS
            kept = [corpora.to_glyphs(w, units) for w in kept]
        if kept:
            cur["lines"].append(kept)
    pages = [p for p in pages if p["lines"]]
    return dict(source=str(path.as_posix()), alphabet=alphabet, collapse=collapse,
                units="P*", dropped_unreadable_tokens=n_dropped, pages=pages)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--collapse", choices=["glyph", "glyph+"], default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="compare with metrics_new.voynich_pages (ZL3b only)")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists() and not a.force:
        sys.exit(f"refusing to overwrite {out}")
    d = convert(a.inp, a.collapse)
    toks = [t for p in d["pages"] for ln in p["lines"] for t in ln]
    alph = sorted({c for t in toks for c in t})
    print(f"{a.inp}: alphabet={d['alphabet']} pages={len(d['pages'])} "
          f"lines={sum(len(p['lines']) for p in d['pages'])} tokens={len(toks)} "
          f"types={len(set(toks))} chars={len(alph)} dropped={d['dropped_unreadable_tokens']}")
    if a.check:
        sys.path.insert(0, str(ROOT))
        from scoreboard import metrics_new as M
        ref = M.voynich_pages("glyph+" if a.collapse == "glyph+" else
                              "glyph" if a.collapse == "glyph" else "eva")
        rt = M.flat_tokens(ref)
        diff = abs(len(toks) - len(rt)) / len(rt)
        same3 = d["pages"][0]["lines"][:3] == ref[0]["lines"][:3]
        print(f"check: vparse tokens={len(rt)} diff={diff:.4%} (<0.5%: {diff < 0.005}) "
              f"f1r first 3 lines identical: {same3}  all tokens identical: {toks == rt}")
        if not (diff < 0.005 and same3):
            sys.exit("VALIDATION FAILED")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
