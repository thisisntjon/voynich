"""vx01_a1_gen.py - A1 planted-book generators with TRUE (prefix, core, suffix) labels (script 2, part 1).

Plan: PLAN-X01-v5.1 (SHA256 af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393), section 4 (A1), 3a (seeds).
All results from books made here are UNVERIFIED until the Independent Verifier signs.
Own generators: NO import of SlotSegmenter or any other project segmenter. Every token carries the triple it was
built from. The only project inputs are the three transliteration sidecars (token counts, layout, rank-frequency,
glyph rates for NULL), read as plain JSON.

Books (per transliteration set; plan section 4 "Books"):
  G1  independent prefix x core x suffix draws, Zipf exponent 1.0, Slot-sized inventories (28/2360/19, 29/2491/20,
      25/2420/20; empty string counted in prefix and suffix inventories; sizes from the plan), pieces drawn from the
      frozen EVA glyph list below. Empty prefix and empty suffix take Zipf rank 1 in their streams.
  G2  Rugg-like table and grille (shape of ctl_generators.py:77-113): 250 rows, columns of 40/60/40 pieces from fixed
      glyph pools (NOT from Voynich words), 40 grilles, word = column 0 + column 1 + column 2; own table seed and own
      grille seed per book; the grille index advances at each real line start (real layout); true labels = the three
      column picks. Rugg-sized inventories.
  NULL same token count, same rank-frequency profile (each rank keeps the real count), same word length per rank,
      same glyph unigram rates, same lines/words-per-line layout as the real set; every word type is an i.i.d. glyph
      string; NO affix inventory; truth is the whole word as core.
Implementation choices NOT fixed by the plan (written here, frozen with this file): glyph list and glyph weights,
piece-length weights, blank cells only in columns 0 and 2 (so every core is non-empty), start row from the book seed,
G2 count of tokens = real token count, uniqueness of pieces inside an inventory. Layout: all book types use the real
line lengths of the set (4130 / 4130 / 4117 lines).
Seeds: derive_seed(master, set, family, "A1", 0) of vx01_common (plan 3a).
Library only: never started directly, no dev log of its own.
"""
from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

import vx01_common as C

ROOT = Path(__file__).resolve().parent
EVA_GLYPHS = "oyehaidlkrctsnqpfmgx"                         # frozen list, 20 glyphs
GLYPH_WEIGHTS = tuple(1.0 / (i + 2) for i in range(len(EVA_GLYPHS)))
LEN_W_PREFIX = {1: 0.4, 2: 0.4, 3: 0.2}
LEN_W_SUFFIX = {1: 0.4, 2: 0.4, 3: 0.2}
LEN_W_CORE = {2: 0.15, 3: 0.30, 4: 0.30, 5: 0.15, 6: 0.10}
LEN_W_MID = {1: 0.2, 2: 0.4, 3: 0.3, 4: 0.1}
G2_ROWS, G2_COLS, G2_GRILLES, G2_OFFSET_MAX = 250, (40, 60, 40), 40, 12

# Plan section 4 "Inventory sizes": tokens, prefixes (incl. empty), cores, suffixes (incl. empty).
SETS = {
    "ZL3b": dict(file="data/translit/ZL3b_eva.meta.json", n_tok=34857, nP=28, nC=2360, nS=19),
    "RF1b": dict(file="data/translit/RF1b.meta.json", n_tok=34618, nP=29, nC=2491, nS=20),
    "IT2a": dict(file="data/translit/IT2a.meta.json", n_tok=34411, nP=25, nC=2420, nS=20),
}
SET_ORDER = ("ZL3b", "RF1b", "IT2a")


def load_set(tset: str) -> dict:
    """Real sidecar: tokens in reading order and line lengths. Used for layout and NULL marginals only."""
    d = json.loads((ROOT / SETS[tset]["file"]).read_text(encoding="utf-8"))
    layout, toks = [], []
    for pg in d["pages"]:
        for ln in pg["lines"]:
            layout.append(len(ln))
            toks.extend(ln)
    assert len(toks) == SETS[tset]["n_tok"], (tset, len(toks))
    return dict(tokens=toks, layout=layout)


def _piece(rng, lenw):
    lens = sorted(lenw)
    L = rng.choices(lens, [lenw[k] for k in lens])[0]
    return "".join(rng.choices(EVA_GLYPHS, GLYPH_WEIGHTS, k=L))


def _distinct(rng, n, lenw):
    out, seen = [], set()
    guard = 0
    while len(out) < n:
        s = _piece(rng, lenw)
        guard += 1
        if guard > 5_000_000:
            raise RuntimeError("cannot draw %d distinct pieces" % n)
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _zipf_cum(n):
    tot, cum = 0.0, []
    for r in range(1, n + 1):
        tot += 1.0 / r
        cum.append(tot)
    return cum


def gen_g1(tset: str, master: int, real=None) -> dict:
    spec = SETS[tset]
    real = real or load_set(tset)
    rng = random.Random(C.derive_seed(master, tset, "G1", "A1", 0))
    P = [""] + _distinct(rng, spec["nP"] - 1, LEN_W_PREFIX)
    S = [""] + _distinct(rng, spec["nS"] - 1, LEN_W_SUFFIX)
    Cr = _distinct(rng, spec["nC"], LEN_W_CORE)
    # ranks: the empty string keeps rank 1; the other pieces are in drawn order (already random)
    n = spec["n_tok"]
    ps = rng.choices(P, cum_weights=_zipf_cum(len(P)), k=n)
    cs = rng.choices(Cr, cum_weights=_zipf_cum(len(Cr)), k=n)
    ss = rng.choices(S, cum_weights=_zipf_cum(len(S)), k=n)
    truth = list(zip(ps, cs, ss))
    return dict(set=tset, family="G1", master=master, tokens=[a + b + c for a, b, c in truth], truth=truth,
                layout=real["layout"], inventory=dict(P=len(P), C=len(Cr), S=len(S)))


def _column(rng, pieces, rows):
    tot = sum(1.0 / (i + 1) for i in range(len(pieces)))
    col = []
    for i, s in enumerate(pieces):
        col.extend([s] * max(1, round(rows * (1.0 / (i + 1)) / tot)))
    rng.shuffle(col)
    return col[:rows] + col[:max(0, rows - len(col))]


def gen_g2(tset: str, master: int, table_master: int, grille_master: int, real=None) -> dict:
    spec = SETS[tset]
    real = real or load_set(tset)
    rt = random.Random(C.derive_seed(table_master, tset, "G2table", "A1", 0))
    rg = random.Random(C.derive_seed(grille_master, tset, "G2grille", "A1", 0))
    rb = random.Random(C.derive_seed(master, tset, "G2", "A1", 0))
    pools = [_distinct(rt, G2_COLS[0], LEN_W_PREFIX), _distinct(rt, G2_COLS[1], LEN_W_MID),
             _distinct(rt, G2_COLS[2], LEN_W_SUFFIX)]
    table = [_column(rt, pools[c], G2_ROWS) for c in range(3)]
    for c in (0, 2):                                        # blanks only in prefix and suffix columns
        for i in rt.sample(range(G2_ROWS), G2_ROWS // 8):
            table[c][i] = ""
    grilles = [tuple(rg.randint(0, G2_OFFSET_MAX) for _ in range(3)) for _ in range(G2_GRILLES)]
    pos = rb.randrange(G2_ROWS)
    g = 0
    truth = []
    for L in real["layout"]:
        off = grilles[g % G2_GRILLES]
        for _ in range(L):
            truth.append(tuple(table[c][(pos + off[c]) % G2_ROWS] for c in range(3)))
            pos = (pos + 1) % G2_ROWS
        g += 1
    assert len(truth) == spec["n_tok"]
    inv = dict(P=len({t[0] for t in truth}), C=len({t[1] for t in truth}), S=len({t[2] for t in truth}))
    return dict(set=tset, family="G2", master=master, tokens=[a + b + c for a, b, c in truth], truth=truth,
                layout=real["layout"], inventory=inv)


def gen_null(tset: str, master: int, real=None) -> dict:
    real = real or load_set(tset)
    rng = random.Random(C.derive_seed(master, tset, "NULL", "A1", 0))
    toks = real["tokens"]
    freq = Counter(toks)
    ranked = sorted(freq, key=lambda w: (-freq[w], w))
    gl = Counter("".join(toks))
    glyphs = sorted(gl)
    weights = [gl[g] for g in glyphs]
    used, new_types = set(), []
    for w in ranked:
        L = len(w)
        guard = 0
        while True:
            s = "".join(rng.choices(glyphs, weights, k=L))
            guard += 1
            if guard > 2_000_000:
                raise RuntimeError("cannot draw a distinct null word of length %d" % L)
            if s not in used:
                used.add(s)
                break
        new_types.append(s)
    bag = []
    for w, s in zip(ranked, new_types):
        bag.extend([s] * freq[w])
    rng.shuffle(bag)
    assert len(bag) == len(toks)
    return dict(set=tset, family="NULL", master=master, tokens=bag, truth=[("", t, "") for t in bag],
                layout=real["layout"], inventory=dict(P=0, C=len(new_types), S=0))
