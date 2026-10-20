"""Naibbe-family cipher-with-randomiser control (after Greshko 2025).

Plaintext: the same Latin herbal as ctl_nomenclator (Macer + Pliny, N_TOKENS tokens).
Each word is split left-to-right into units: at every step a unigram or a bigram with p = 0.5
(the dice). Each unit is enciphered by one of six substitution tables chosen uniformly at random
per unit (the card draw); every table maps each of the 26 letters and 676 bigrams to a distinct
string of 1-4 symbols from the 18-symbol core alphabet. Word boundaries are kept.
Output: data/controls_synthetic/naibbe_like.txt + .meta.json (lines = plaintext lines,
20 lines/page, sections = plaintext chapters/books).   Run: python ctl_naibbe.py
"""
import json
import random
from itertools import product
from pathlib import Path

import corpora
from ctl_nomenclator import (plaintext, stats, write_variant, pages_from_lines, OUT, SEED, N_TOKENS,
                             CORE_SYMS)

ROOT = Path(__file__).parent
LETTERS = "abcdefghijklmnopqrstuvwxyz"


def make_table(rng):
    """Random one-to-one map from the 26 + 676 units to distinct 1-4 symbol strings."""
    pool = set()
    while len(pool) < 702 * 2:
        n = rng.choice([1, 2, 2, 2, 3, 3, 4])
        pool.add("".join(rng.choice(CORE_SYMS) for _ in range(n)))
    pool = sorted(pool, key=lambda s: (len(s), s))
    rng.shuffle(pool)
    units = list(LETTERS) + ["".join(p) for p in product(LETTERS, repeat=2)]
    # frequent letters get the short strings: sort pool by length and assign letters first
    pool.sort(key=len)
    return dict(zip(units, pool))


def split_units(rng, w):
    out, i = [], 0
    while i < len(w):
        if i + 1 < len(w) and rng.random() < 0.5:
            out.append(w[i:i + 2])
            i += 2
        else:
            out.append(w[i])
            i += 1
    return out


def main():
    rng = random.Random(SEED)
    tables = [make_table(random.Random(SEED + 100 + k)) for k in range(6)]
    pt = plaintext()
    secs = [s for s, _ in pt]
    enc_lines = []
    for _, line in pt:
        enc = []
        for w in line:
            w = "".join(c for c in w if c in LETTERS)
            if not w:
                continue
            enc.append("".join(tables[rng.randrange(6)][u] for u in split_units(rng, w)))
        enc_lines.append(enc)
    pages = pages_from_lines(enc_lines, secs)
    toks = write_variant("naibbe_like", pages,
                         "Naibbe-like: unigram/bigram split p=0.5, 6 random substitution tables chosen per unit, "
                         "1-4 symbol entries, word boundaries kept")
    (OUT / "naibbe_like.key.json").write_text(json.dumps(tables), encoding="utf-8")
    rows = [("naibbe_like", stats(toks)), ("Voynich EVA (first 35k)", stats(corpora.voynich()[:N_TOKENS]))]
    cols = ["tokens", "types", "hapax", "mean_len", "sd_len", "alpha", "h1", "h2", "redup"]
    out = [f"ctl_naibbe.py seed={SEED}", f"{'variant':26}" + "".join(f"{c:>10}" for c in cols)]
    for name, st in rows:
        out.append(f"{name:26}" + "".join(
            f"{st[c]:>10.3f}" if isinstance(st[c], float) else f"{st[c]:>10}" for c in cols))
    text = "\n".join(out) + "\n"
    (ROOT / "results_ctl_naibbe.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
