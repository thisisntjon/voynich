"""F2: are Voynich tokens syllable-sized pieces of a language?

F1 found Voynich's word-order information beyond the edge table (+0.02-0.04
bits) matches Naibbe's (a real cipher of Italian/Latin, tokens = letter codes)
and is 3-10x below every prose control, while its edge-table gain (+0.24-0.27)
is prose-sized. A script that puts spaces between SYLLABLES (or two-syllable
chunks) of a real language predicts exactly that: phonotactics couple the
glyphs across each space, while most word order is spread over several
tokens. Test: rewrite each prose control with a space at every syllable
boundary (and at every second syllable boundary) and measure the same
battery as on Voynich.

Syllabifier (rule-based, Latin/Italian/German-ish): vowel runs are nuclei;
one consonant between nuclei starts the next syllable; of two or more, the
last two go to the next syllable if they form a common onset (stop/f +
l/r, qu, ch, ph, th, gn, sc, st), otherwise the last one. Word-final
consonants stay with the last syllable. Not linguistically exact; it
only needs to place spaces where a syllabary would.

Battery per text (first 33,000 tokens of the rewritten text, 50-char lines):
  c3 cross-space MI excess; F1 edge-gain and residual excess (top-300
  vocabulary); h2 (b4.h2); token mean length and SD; types; hapax share.
Compared with: Voynich, Naibbe, the plain-word controls, token-shuffled null.
Run: python f2_syllable_control.py  -> results_f2.txt
"""
import random
import re
import statistics
from collections import Counter
from pathlib import Path

import b4_selfcite_sim as b4
import c3_edge_coupling as c3
import c4_naibbe_lines as c4
import corpora
import f1_residual_order as f1

OUT = Path(__file__).parent / "results_f2.txt"
N = 33000
WIDTH = 50
VOW = set("aeiouy")
ONSETS = {"pl", "pr", "bl", "br", "tr", "dr", "cl", "cr", "gl", "gr", "fl", "fr", "qu", "ch", "ph", "th",
          "gn", "sc", "st", "sp"}
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def syllables(word):
    nuc = [m.span() for m in re.finditer(r"[aeiouy]+", word)]
    if len(nuc) <= 1:
        return [word]
    cuts = []
    for (s0, e0), (s1, _) in zip(nuc, nuc[1:]):
        cl = word[e0:s1]
        if len(cl) <= 1:
            cuts.append(e0)
        elif cl[-2:] in ONSETS:
            cuts.append(s1 - 2)
        else:
            cuts.append(s1 - 1)
    out, prev = [], 0
    for c in cuts:
        out.append(word[prev:c]); prev = c
    out.append(word[prev:])
    return [x for x in out if x]


def chunk(words, per):
    toks = []
    for w in words:
        sy = syllables(w)
        toks += ["".join(sy[i:i + per]) for i in range(0, len(sy), per)]
    return toks


def wrap(tokens):
    lines, cur, n = [], [], 0
    for w in tokens:
        if cur and n + 1 + len(w) > WIDTH:
            lines.append(cur); cur, n = [], 0
        n += len(w) + (1 if cur else 0)
        cur.append(w)
    return lines + ([cur] if cur else [])


def split_blocks(lines):
    return f1.split_blocks(lines)


def battery(name, lines, tr_te=None):
    toks = [w for l in lines for w in l]
    lens = [len(w) for w in toks]
    cnt = Counter(toks)
    hapax = sum(1 for c in cnt.values() if c == 1) / len(cnt)
    cross = c3.score(lines, c3.EVA)
    f1.TOPN = 300
    tr, te = tr_te or split_blocks(lines)
    U, E, E2, W, _ = f1.evaluate(tr, te)
    sU, _, sE2, sW, _ = f1.evaluate(f1.shuffled(tr), f1.shuffled(te))
    edge = (U - E2) - (sU - sE2)
    resid = (E2 - W) - (sE2 - sW)
    emit(f"{name:26} crossMI excess={cross[2]:+.3f}  edge-gain excess={edge:+.3f}  residual excess={resid:+.3f}  "
         f"h2={b4.h2(toks):.3f}  len {statistics.mean(lens):.2f}±{statistics.pstdev(lens):.2f}  "
         f"types={len(cnt)}  hapax={hapax:.2f}  tokens={len(toks)}")


def main():
    emit("F2: syllable-spaced natural language vs Voynich (same battery)")
    emit("crossMI = c3 (last glyph | next first glyph); edge/residual = F1 held-out excess over own within-line shuffle, top-300 vocab")
    emit()
    by = b4.pages()
    vlines = [r["words"] for recs in by.values() for r in recs]
    battery("VOYNICH", vlines, f1.split_pages(by))
    nb = c4.skeleton(c4.naibbe_tokens(), by)
    battery("NAIBBE (c4 skeleton)", [r["words"] for recs in nb.values() for r in recs], f1.split_pages(nb))
    flat = [w for l in vlines for w in l]
    random.Random(5).shuffle(flat)
    it = iter(flat)
    battery("NULL token-shuffled", [[next(it) for _ in l] for l in vlines])
    emit()
    for name in corpora.CONTROLS:
        words = corpora.control(name, 3 * N)
        for label, toks in (("words", words), ("syllables", chunk(words, 1)), ("2-syllable chunks", chunk(words, 2))):
            battery(f"{name} {label}", wrap(toks[:N]))
        emit()
    emit("example: " + " ".join(chunk(corpora.control("latin_caesar", 12), 1)))
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
