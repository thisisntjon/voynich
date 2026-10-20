"""vx01_a1_metrics.py - A1 scoring: boundary F1, exact triple, false structure, oracle parse (script 2, part 2).

Plan: PLAN-X01-v5.1 (SHA256 af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393), section 4 "Metrics", "Oracle ceiling",
"Roll-up"; rule 6 (thresholds). All results are UNVERIFIED until the Independent Verifier signs.
No segmenter is imported here. A segmenter is any function w -> (prefix, core, suffix) or None (token dropped).

Definitions (plan section 4, written as code)
  truth boundaries of a token = {len(P)} if P non-empty, plus {len(P)+len(C)} if S non-empty (glyph positions).
  predicted boundaries use the same rule on the predicted triple; a dropped token (None) or a triple whose parts do
  not join back to the word has NO predicted boundary and counts as a miss.
  Boundary F1: micro over every token occurrence (token-weighted), exact position (0-glyph tolerance); precision =
  pooled hits / pooled predicted; recall = pooled hits / pooled true; F1 of the pooled values; 0 if both are 0.
  Exact triple: share of tokens whose predicted (P, C, S) equals the truth. A dropped token is a miss.
  False structure (NULL books): share of tokens given a non-empty prefix OR suffix (dropped token: none).
  Type-weighted F1 (report only): same as F1 with each distinct (word, true triple) pair weighted 1.
Thresholds (rule 6, fixed before any run, confirmed by Eve 2026-10-18 22:17 PDT): F1 >= 0.85, exact >= 0.70,
NULL false structure <= 0.05, books passing >= 10 of 15 in each of 9 cells (3 sets x {G1, G2, NULL}).
Library only: never started directly, no dev log of its own.
"""
from __future__ import annotations

import math
from collections import Counter

F1_MIN = 0.85
EXACT_MIN = 0.70
NULL_MAX = 0.05
BOOKS_MIN = 10
BOOKS_N = 15
FAMILIES = ("G1", "G2", "NULL")


def boundaries(p: str, c: str, s: str) -> frozenset:
    b = set()
    if p:
        b.add(len(p))
    if s:
        b.add(len(p) + len(c))
    return frozenset(b)


def _pred(w, r):
    """Return (predicted triple or None, predicted boundary set)."""
    if r is None:
        return None, frozenset()
    p, c, s = r
    if p + c + s != w:
        return tuple(r), frozenset()
    return tuple(r), boundaries(p, c, s)


def _f1(tp, pred, tru):
    prec = tp / pred if pred else 0.0
    rec = tp / tru if tru else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    return prec, rec, f1


def score_book(tokens, truth, seg_fn) -> dict:
    pairs = Counter(zip(tokens, truth))
    n = len(tokens)
    cache = {}
    tp = pred = tru = exact = struct = dropped = 0
    ttp = tpred = ttru = 0
    for (w, t), cnt in pairs.items():
        r = cache.get(w, False)
        if r is False:
            r = seg_fn(w)
            cache[w] = r
        ptriple, pb = _pred(w, r)
        tb = boundaries(*t)
        h = len(tb & pb)
        tp += h * cnt
        pred += len(pb) * cnt
        tru += len(tb) * cnt
        ttp += h
        tpred += len(pb)
        ttru += len(tb)
        if ptriple is not None and ptriple == tuple(t):
            exact += cnt
        if r is None:
            dropped += cnt
        elif r[0] or r[2]:
            struct += cnt
    prec, rec, f1 = _f1(tp, pred, tru)
    _, _, tf1 = _f1(ttp, tpred, ttru)
    return dict(n_tokens=n, precision=prec, recall=rec, f1=f1, exact=exact / n, false_structure=struct / n,
                type_f1=tf1, dropped_share=dropped / n)


def book_passes(family: str, sc: dict) -> bool:
    if family == "NULL":
        return sc["false_structure"] <= NULL_MAX
    return sc["f1"] >= F1_MIN and sc["exact"] >= EXACT_MIN


def oracle_fn(truth):
    """Bayes parse that knows the true inventories and their true counts (ceiling check, dev books only)."""
    cp, cc, cs = Counter(t[0] for t in truth), Counter(t[1] for t in truth), Counter(t[2] for t in truth)
    lp = {k: math.log(v) for k, v in cp.items()}
    lc = {k: math.log(v) for k, v in cc.items()}
    ls = {k: math.log(v) for k, v in cs.items()}
    maxp = max(len(k) for k in lp)
    maxs = max(len(k) for k in ls)

    def seg(w):
        best, bkey = None, None
        for i in range(0, min(maxp, len(w)) + 1):
            p = w[:i]
            if p not in lp:
                continue
            for j in range(0, min(maxs, len(w) - i) + 1):
                s = w[len(w) - j:] if j else ""
                if s not in ls:
                    continue
                c = w[i:len(w) - j]
                if c not in lc:
                    continue
                key = (-(lp[p] + lc[c] + ls[s]), p, c, s)
                if bkey is None or key < bkey:
                    best, bkey = (p, c, s), key
        return best
    return seg


def rollup(rows) -> dict:
    """rows: dicts with keys set, family, segmenter, passed (bool). Returns {segmenter: {(set, family): n_pass},
    ... 'adequate'}: ADEQUATE ON PLANTED BOOKS only if every one of the 9 cells has >= 10 passing books of 15."""
    cells = {}
    for r in rows:
        cells.setdefault(r["segmenter"], {}).setdefault((r["set"], r["family"]), [0, 0])
        c = cells[r["segmenter"]][(r["set"], r["family"])]
        c[1] += 1
        c[0] += 1 if r["passed"] else 0
    out = {}
    for seg, d in cells.items():
        ok = len(d) == 9 and all(v[1] == BOOKS_N and v[0] >= BOOKS_MIN for v in d.values())
        out[seg] = dict(cells=d, adequate=ok)
    return out
