"""C4: Naibbe ciphertext through the a2 and B4 line tests (and C3 coupling).

Source: Greshko, "The Naibbe cipher" (Cryptologia 2025), supplementary files,
Zenodo record 17219445, file "Naibbe Cipher.xlsx" (md5 e5191f03...12f29,
downloaded 2026-10-17 into data/naibbe_zenodo_17219445/, with the user's
approval). The workbook's cached sheet 'analysis' (column C, from row 7) holds
one encryption: 20,923 tokens of the "Four-Text Sampler" plaintext (Dante,
Pliny, an alchemical herbal, De sphaera), 78-card deck, standard spacing
scheme. Read with openpyxl as data (values only), no macros.

Naibbe output is a token stream with no line structure, so lines are imposed
two ways:
  skeleton : poured into Voynich's real pages/line lengths in order (B4 layout)
  wrap     : wrapped at a fixed width of 50 EVA characters incl. spaces
             (Voynich mean paragraph line = 49.6), like a copyist
             filling lines
Any line-edge effect must therefore come from the cipher or the layout itself.
Tests: a2 (JSD of first/last glyph and length of line-initial / line-final
words vs mid-line, within-line shuffle null), b4.report (p-initial and
m-final enrichment, h2, repeats, same-column copies), c3 edge coupling.
Controls: Voynich (target); natural language = Dante verse (a2/b4) and
Italian prose (c3). Null: Naibbe tokens shuffled across the whole stream,
same layout.
Run: python c4_naibbe_lines.py  -> results_c4.txt
"""
import contextlib
import io
import random
from pathlib import Path

import openpyxl

import a2_position as a2
import b4_selfcite_sim as b4
import c3_edge_coupling as c3

HERE = Path(__file__).parent
XLSX = HERE / "data" / "naibbe_zenodo_17219445" / "Naibbe_Cipher.xlsx"
OUT = HERE / "results_c4.txt"
WIDTH = 50
log = b4.log


def emit(s=""):
    b4.emit(s)


def naibbe_tokens():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    col = [r[2] for r in wb["analysis"].iter_rows(min_row=7, min_col=1, max_col=3, values_only=True)]
    return [w.strip() for w in col if isinstance(w, str) and w.strip() and w.strip() != "XXXXX"]


def skeleton(tokens, by):
    it = iter(tokens)
    out = {}
    for page, recs in by.items():
        lines = []
        for r in recs:
            line = [w for _, w in zip(r["words"], it)]
            if len(line) < len(r["words"]):
                break
            lines.append(dict(r, words=line))
        if len(lines) < len(recs):
            if len(lines) >= 2:
                out[page] = lines
            break
        out[page] = lines
    return out


def wrap(tokens):
    lines, cur, n = [], [], 0
    for w in tokens:
        if cur and n + 1 + len(w) > WIDTH:
            lines.append(cur); cur, n = [], 0
        n += len(w) + (1 if cur else 0)
        cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def a2_report(name, lines):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        a2.report(name, lines)
    for s in buf.getvalue().rstrip().splitlines():
        emit(s)


def main():
    toks = naibbe_tokens()
    emit("C4: Naibbe ciphertext (Greshko 2025, Zenodo 17219445, cached 'Four-Text Sampler' run) through a2, B4 and C3")
    emit(f"tokens={len(toks)} types={len(set(toks))}; layouts: Voynich page/line skeleton, and {WIDTH}-char wrap")
    emit()
    by = b4.pages()
    shuf = toks[:]; random.Random(7).shuffle(shuf)
    sk, sk_null = skeleton(toks, by), skeleton(shuf, by)
    vlines = [r["words"] for recs in by.values() for r in recs]
    vchars = sum(len(" ".join(l)) for l in vlines) / len(vlines)
    emit(f"Voynich mean line length = {vchars:.1f} chars; skeleton fills {len(sk)} pages")
    emit()
    emit("--- a2: line position (all lines) ---")
    a2_report("VOYNICH", vlines)
    a2_report("NAIBBE skeleton", [r["words"] for recs in sk.values() for r in recs])
    a2_report("NAIBBE wrap", wrap(toks))
    a2_report("NULL Naibbe shuf", [r["words"] for recs in sk_null.values() for r in recs])
    a2_report("CTRL dante", b4.verse_lines("italian_dante"))
    emit()
    emit("--- b4.report: lines 2+ of each page ---")
    b4.report("VOYNICH", by)
    b4.report("NAIBBE skeleton", sk)
    b4.report("NAIBBE wrap", lines=wrap(toks))
    b4.report("NULL Naibbe shuf", sk_null)
    b4.report("CTRL_dante", lines=b4.verse_lines("italian_dante"))
    emit()
    emit("--- c3 edge coupling ---")
    for name, lines in (("VOYNICH all", vlines), ("NAIBBE skeleton", [r["words"] for recs in sk.values() for r in recs]),
                        ("NAIBBE wrap", wrap(toks)), ("NULL Naibbe shuffled", wrap(shuf)),
                        ("CTRL italian_dante", c3.prose_lines("italian_dante"))):
        a, b = c3.score(lines, c3.EVA), c3.score(lines, c3.GLY)
        emit(f"{name:22} EVA MI={a[0]:.4f} excess={a[2]:+.4f} (z {a[3]:6.1f})   glyph+ MI={b[0]:.4f} excess={b[2]:+.4f} (z {b[3]:6.1f})")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
