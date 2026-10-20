"""Synthetic positional-numeral nomenclator control.

Companion to ctl_nomenclator.py (whose random-core three-slot codebook cannot push the
character conditional entropy h2 down: 3.18 vs Voynich 2.11).  Here the codebook is a
POSITIONAL NUMERAL: every plaintext word type is ranked by frequency (rank 1 = most frequent)
and its rank is written as a mixed-radix numeral, radices RADICES = (8, 12, 15, 10) from the
most- to the least-significant digit, each digit position having its OWN glyph alphabet drawn
from a 22-letter ASCII alphabet (overlap between positions allowed), leading zeros dropped.
Frequent words therefore get short codes and every glyph is locked to a digit position
(Tiltman's slot structure).

Variants (data/controls_synthetic/, each with .meta.json and .key.json):
  nomen_numeric        word-rank numerals; lines = plaintext lines, 20 lines/page
  nomen_numeric_lines  the same code with the nomen_lines layout: 6-10 words/line, 10-25
                       lines/page, line-initial marker 'p' (prob 0.20), line-final 'm' (0.15)
  nomen_numeric_sylls  the numeral scheme applied to syllable ranks; syllable numerals
                       concatenated within the word (word boundaries = plaintext words)

Run:  python ctl_nomen_numeric.py   (writes results_ctl_nomen_numeric.txt)
"""
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import corpora
from a1_profile import char_entropies
from ctl_nomenclator import N_TOKENS, OUT, pages_from_lines, plaintext, syllabify, write_variant

SEED = 20261017
ROOT = Path(__file__).parent

RADICES = (8, 12, 15, 10)            # most- to least-significant digit
# 22-letter ASCII alphabet; 'p' and 'm' are reserved for the line-edge markers
ALPHABET22 = list("abcdefghijklnoqrstuvxy")
assert len(ALPHABET22) == 22 and "p" not in ALPHABET22 and "m" not in ALPHABET22


# ------------------------------------------------------------------ numeral code
def make_digit_alphabets(rng, radices=RADICES, alphabet=ALPHABET22):
    """One glyph list per digit position (position-locked glyph identities); positions may
    share glyphs, as the draws are independent."""
    return [rng.sample(alphabet, r) for r in radices]


def digits(value, radices=RADICES):
    """Mixed-radix digits of value, most-significant first, leading zeros dropped."""
    cap = math.prod(radices)
    assert 0 < value < cap, (value, cap)
    ds = []
    for r in reversed(radices):           # least-significant first
        ds.append(value % r)
        value //= r
    ds.reverse()
    i = 0
    while i < len(ds) - 1 and ds[i] == 0:
        i += 1
    return list(zip(range(i, len(ds)), ds[i:]))   # [(position, digit), ...]


def numeral(value, alphs, radices=RADICES):
    return "".join(alphs[pos][d] for pos, d in digits(value, radices))


def build_numeral_code(types_by_freq, alphs):
    """rank 1 (most frequent) -> shortest numeral; one-to-one by construction."""
    code = {w: numeral(rank, alphs) for rank, w in enumerate(types_by_freq, start=1)}
    assert len(set(code.values())) == len(code)
    return code


# ------------------------------------------------------------------ measures
def entropy_counts(c):
    n = sum(c.values())
    return -sum(v / n * math.log2(v / n) for v in c.values() if v)


def position_lock(toks):
    """Token-weighted mean over glyphs of the entropy (bits) of the glyph's relative-position
    quintile distribution (scoreboard/metrics_new.extra_signatures (d)); low = position-locked."""
    q, tot = defaultdict(Counter), Counter()
    for w in toks:
        L = len(w)
        for i, ch in enumerate(w):
            rp = i / (L - 1) if L > 1 else 0.5
            q[ch][min(4, int(rp * 5))] += 1
            tot[ch] += 1
    N = sum(tot.values())
    return sum(tot[ch] / N * entropy_counts(q[ch]) for ch in tot)


def stats(words):
    c = Counter(words)
    lens = [len(w) for w in words]
    ce = char_entropies(words)
    redup = sum(a == b for a, b in zip(words, words[1:])) / (len(words) - 1) * 100
    return dict(tokens=len(words), types=len(c), hapax=sum(v == 1 for v in c.values()) / len(c),
                mean_len=float(np.mean(lens)), sd_len=float(np.std(lens)), alpha=ce["alpha"],
                h1=ce["h1"], h2=ce["h2"], redup=redup, poslock=position_lock(words))


# ------------------------------------------------------------------ layout with line markers
def lines_layout(stream, rng, p_init=0.20, p_final=0.15):
    """Same layout rules as ctl_nomenclator nomen_lines: 6-10 words/line, 10-25 lines/page,
    line-initial 'p' marker (p_init), line-final 'm' suffix (p_final)."""
    pages, i, pno = [], 0, 0
    while i < len(stream):
        n_lines = rng.randint(10, 25)
        lines, sec = [], stream[i][0]
        for _ in range(n_lines):
            if i >= len(stream):
                break
            n = rng.randint(6, 10)
            line = [cw for _, cw in stream[i:i + n]]
            i += n
            if rng.random() < p_init:
                line[0] = "p" + line[0]
            if rng.random() < p_final:
                line[-1] = line[-1] + "m"
            lines.append(line)
        pno += 1
        pages.append(dict(page=pno, section=sec, lines=lines))
    return pages


# ------------------------------------------------------------------ main
def main():
    rng = random.Random(SEED)
    pt = plaintext()
    pt_words = [w for _, l in pt for w in l]
    freq = Counter(pt_words)
    types_by_freq = [w for w, _ in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))]
    secs = [s for s, _ in pt]
    plain_lines = [l for _, l in pt]
    rows = []

    # 1. word-rank positional numerals
    alphs = make_digit_alphabets(rng)
    code = build_numeral_code(types_by_freq, alphs)
    enc_lines = [[code[w] for w in l] for l in plain_lines]
    pages = pages_from_lines(enc_lines, secs)
    note1 = (f"positional-numeral nomenclator: word frequency rank written in mixed radix {RADICES} "
             "(most- to least-significant), one glyph alphabet per digit position, leading zeros "
             "dropped; lines = plaintext lines, 20 lines/page")
    toks = write_variant("nomen_numeric", pages, note1)
    rows.append(("nomen_numeric", stats(toks)))
    key = dict(seed=SEED, radices=list(RADICES), digit_alphabets=alphs, code=code)
    (OUT / "nomen_numeric.key.json").write_text(json.dumps(key, ensure_ascii=False), encoding="utf-8")

    # 2. the same code with the nomen_lines layout and edge markers
    rng2 = random.Random(SEED + 2)
    stream = [(s, code[w]) for s, l in pt for w in l]
    pages = lines_layout(stream, rng2)
    toks = write_variant("nomen_numeric_lines", pages,
                         note1 + "; layout: 6-10 words/line, 10-25 lines/page, line-initial 'p' marker "
                                 "p=0.20, line-final 'm' suffix p=0.15")
    rows.append(("nomen_numeric_lines", stats(toks)))
    (OUT / "nomen_numeric_lines.key.json").write_text(
        json.dumps(dict(key, markers=dict(line_initial="p", p_init=0.20, line_final="m", p_final=0.15)),
                   ensure_ascii=False), encoding="utf-8")

    # 3. syllable-rank numerals, concatenated within the word
    rng3 = random.Random(SEED + 1)
    alphs_s = make_digit_alphabets(rng3)
    syl_freq = Counter(s for w in pt_words for s in syllabify(w))
    syl_by_freq = [s for s, _ in sorted(syl_freq.items(), key=lambda kv: (-kv[1], kv[0]))]
    syl_code = build_numeral_code(syl_by_freq, alphs_s)
    enc_lines = [["".join(syl_code[s] for s in syllabify(w)) for w in l] for l in plain_lines]
    pages = pages_from_lines(enc_lines, secs)
    toks = write_variant("nomen_numeric_sylls", pages,
                         f"positional-numeral code on syllable ranks ({len(syl_by_freq)} syllables), "
                         f"mixed radix {RADICES}, one glyph alphabet per digit position, syllable numerals "
                         "concatenated per word; lines = plaintext lines, 20 lines/page")
    rows.append(("nomen_numeric_sylls", stats(toks)))
    (OUT / "nomen_numeric_sylls.key.json").write_text(
        json.dumps(dict(seed=SEED + 1, radices=list(RADICES), digit_alphabets=alphs_s, code=syl_code),
                   ensure_ascii=False), encoding="utf-8")

    # reference
    rows.append(("Voynich EVA (first 35k)", stats(corpora.voynich()[:N_TOKENS])))

    cols = ["tokens", "types", "hapax", "mean_len", "sd_len", "alpha", "h1", "h2", "redup", "poslock"]
    out = [f"ctl_nomen_numeric.py  seed={SEED}  N_TOKENS={N_TOKENS}  radices={RADICES}",
           "h2 = char conditional entropy with space as a symbol (a1_profile.char_entropies); "
           "redup = immediate word repeats (%); poslock = token-weighted mean entropy (bits) of each "
           "glyph's relative-position quintile distribution (metrics_new.extra_signatures (d); max "
           f"{math.log2(5):.3f}, low = position-locked)", ""]
    out.append(f"{'variant':26}" + "".join(f"{c:>10}" for c in cols))
    for name, st in rows:
        out.append(f"{name:26}" + "".join(
            f"{st[c]:>10.3f}" if isinstance(st[c], float) else f"{st[c]:>10}" for c in cols))
    out.append("")
    out.append(f"word code: {len(code)} types; code length distribution "
               f"{dict(sorted(Counter(len(v) for v in code.values()).items()))}; "
               f"token-weighted {dict(sorted(Counter(len(code[w]) for w in pt_words).items()))}")
    out.append(f"syllable code: {len(syl_code)} syllables; numeral length distribution "
               f"{dict(sorted(Counter(len(v) for v in syl_code.values()).items()))}")
    out.append("digit alphabets (word code): " + "  ".join(f"pos{i}[{RADICES[i]}]=" + "".join(a) for i, a in enumerate(alphs)))
    text = "\n".join(out) + "\n"
    (ROOT / "results_ctl_nomen_numeric.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
