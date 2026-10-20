"""Generator controls (data/controls_synthetic/):

  markov1.txt      Markov-1 character model (space included) trained on the Voynich paragraph
                   text (corpora.voynich()), sampled to N_TOKENS words
  rugg_grille.txt  Rugg-style table-and-grille: a 3-column table (prefix / mid / suffix) filled
                   from Voynich's own most frequent word prefixes, cores and suffixes; words are
                   read through a moving grille (3 holes at fixed row offsets) that steps down
                   one row per word; the grille is swapped each line
  latin_merged.txt latin_augustine with phonemic distinctions merged: vowels i o u y -> a (e kept),
                   b->p, d->t, g->k, m->n (Lindemann & Bowern style under-distinguishing script)
  lull_ars_brevis_table.txt  Llull's Ars brevis Figure 4 table generated from its rule: for each
                   of the 84 three-letter combinations of B..K, the 20 compartments with T

All get a <name>.meta.json page/line sidecar (section labels: generator block number, or for
latin_merged Augustine's running 1000-word blocks). Run: python ctl_generators.py
"""
import json
import random
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

import corpora
from ctl_nomenclator import stats, write_variant, OUT, SEED, N_TOKENS

ROOT = Path(__file__).parent


def layout(rng, words, section_every=600):
    """6-10 words per line, 10-25 lines per page; section label = block of ~section_every words."""
    pages, i, pno = [], 0, 0
    while i < len(words):
        n_lines = rng.randint(10, 25)
        lines = []
        sec = f"block{i // section_every}"
        for _ in range(n_lines):
            if i >= len(words):
                break
            n = rng.randint(6, 10)
            lines.append(words[i:i + n])
            i += n
        pno += 1
        pages.append(dict(page=pno, section=sec, lines=lines))
    return pages


# ------------------------------------------------------------------ Markov-1 chars
def markov1(rng, vms):
    s = " " + " ".join(vms) + " "
    trans = defaultdict(Counter)
    for a, b in zip(s, s[1:]):
        trans[a][b] += 1
    tables = {a: (list(c.keys()), np.cumsum(list(c.values())) / sum(c.values())) for a, c in trans.items()}
    words, cur, buf = [], " ", []
    while len(words) < N_TOKENS:
        syms, cdf = tables[cur]
        nxt = syms[int(np.searchsorted(cdf, rng.random()))]
        if nxt == " ":
            if buf:
                words.append("".join(buf))
                buf = []
        else:
            buf.append(nxt)
        cur = nxt
    return words


# ------------------------------------------------------------------ Rugg grille
def split3(w):
    if len(w) < 4:
        return None
    return w[:2], w[2:-2], w[-2:]


def rugg_grille(rng, vms, rows=250, n_grilles=40):
    pre, mid, suf = Counter(), Counter(), Counter()
    for w in vms:
        p = split3(w)
        if p:
            pre[p[0]] += 1
            suf[p[2]] += 1
            if p[1]:
                mid[p[1]] += 1
    def column(cnt, k):
        items = cnt.most_common(k)
        tot = sum(v for _, v in items)
        # fill the column proportional to frequency (a table author lists common parts more often)
        col = []
        for s, v in items:
            col.extend([s] * max(1, round(rows * v / tot)))
        rng.shuffle(col)
        return col[:rows] + col[:max(0, rows - len(col))]
    table = [column(pre, 40), column(mid, 60), column(suf, 40)]
    # a few empty cells in prefix / mid columns give short words
    for c in (0, 1):
        for i in rng.sample(range(rows), rows // 8):
            table[c][i] = ""
    grilles = [tuple(rng.randint(0, 12) for _ in range(3)) for _ in range(n_grilles)]
    words, pos, g = [], 0, 0
    line_len = rng.randint(6, 10)
    while len(words) < N_TOKENS:
        off = grilles[g]
        w = "".join(table[c][(pos + off[c]) % rows] for c in range(3))
        if w:
            words.append(w)
        pos = (pos + 1) % rows
        if len(words) % line_len == 0:
            g = (g + 1) % len(grilles)
            line_len = rng.randint(6, 10)
    meta = dict(table=table, grilles=grilles)
    return words, meta


# ------------------------------------------------------------------ Latin merged
MERGE = str.maketrans({"i": "a", "o": "a", "u": "a", "y": "a", "b": "p", "d": "t", "g": "k", "m": "n"})


def latin_merged():
    words = corpora.control("latin_augustine")[:N_TOKENS]
    return [w.translate(MERGE) for w in words]


# ------------------------------------------------------------------ Lullian table
def lull_table():
    letters = "BCDEFGHIK"
    pages = []
    for n, (x, y, z) in enumerate(combinations(letters, 3), 1):
        cells = [x + y + z, x + y + "T" + x, x + y + "T" + y, x + y + "T" + z,
                 x + z + "T" + x, x + z + "T" + y, x + z + "T" + z,
                 x + "T" + x + y, x + "T" + x + z, x + "T" + y + z,
                 y + z + "T" + x, y + z + "T" + y, y + z + "T" + z,
                 y + "T" + x + y, y + "T" + x + z, y + "T" + y + z,
                 z + "T" + x + y, z + "T" + x + z, z + "T" + y + z,
                 "T" + x + y + z]
        pages.append(dict(page=n, section=f"column {x}{y}{z}", lines=[[c.lower()] for c in cells]))
    return pages


def main():
    vms = corpora.voynich()
    rows = []

    rng = random.Random(SEED)
    w = markov1(rng, vms)
    toks = write_variant("markov1", layout(rng, w), "Markov-1 character model trained on Voynich paragraph text")
    rows.append(("markov1", stats(toks)))

    rng = random.Random(SEED + 10)
    w, meta = rugg_grille(rng, vms)
    toks = write_variant("rugg_grille", layout(rng, w), "Rugg table-and-grille from Voynich prefix/mid/suffix")
    (OUT / "rugg_grille.key.json").write_text(json.dumps(meta), encoding="utf-8")
    rows.append(("rugg_grille", stats(toks)))

    rng = random.Random(SEED + 20)
    w = latin_merged()
    pages = []
    for i in range(0, len(w), 200):
        pages.append(dict(page=len(pages) + 1, section=f"block{i // 1000}",
                          lines=[w[j:j + 10] for j in range(i, min(i + 200, len(w)), 10)]))
    toks = write_variant("latin_merged", pages, "latin_augustine with i,o,u,y->a, b->p, d->t, g->k, m->n")
    rows.append(("latin_merged", stats(toks)))
    rows.append(("latin_augustine (ref)", stats(corpora.control("latin_augustine")[:N_TOKENS])))

    toks = write_variant("lull_ars_brevis_table", lull_table(),
                         "Ars brevis Figure 4 table generated from Llull's rule (84 columns x 20 compartments)")
    rows.append(("lull_ars_brevis_table", stats(toks)))

    rows.append(("Voynich EVA (first 35k)", stats(vms[:N_TOKENS])))
    cols = ["tokens", "types", "hapax", "mean_len", "sd_len", "alpha", "h1", "h2", "redup"]
    out = [f"ctl_generators.py seed={SEED}", f"{'variant':26}" + "".join(f"{c:>10}" for c in cols)]
    for name, st in rows:
        out.append(f"{name:26}" + "".join(
            f"{st[c]:>10.3f}" if isinstance(st[c], float) else f"{st[c]:>10}" for c in cols))
    text = "\n".join(out) + "\n"
    (ROOT / "results_ctl_generators.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
