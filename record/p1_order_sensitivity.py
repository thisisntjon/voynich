"""P1 (Top-10 #5): author-order sensitivity via permutation bounds.
No singulion sequence exists locally, so bound the effect: compare bound
(file) order vs reversed vs quire-block permutations (internal order kept)
vs full page permutations, on order-dependent statistics filed by the team:
Heaps beta (D5) and rare-word page-overlap decay (D5 P4 / a3-style).
If bound order sits inside permutation ranges, sequence claims are
order-fragile; if outside, they survive any bifolio-level reordering.
Run: uv run python p1_order_sensitivity.py -> results_p1.txt
"""
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import b4_selfcite_sim as b4

OUT = Path(__file__).parent / "results_p1_order.txt"  # was results_p1.txt, which overwrote p1_bifolio_null's output (fixed 2026-10-17 19:25)
SEED = 20261017
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def heaps_beta(ordered_words):
    seen, xs, ys = set(), [], []
    for i, w in enumerate(ordered_words, 1):
        seen.add(w)
        if i in (1000, 5000, 10000, 20000, len(ordered_words)):
            xs.append(math.log(i)); ys.append(math.log(len(seen)))
    xs, ys = np.array(xs), np.array(ys)
    return float(np.polyfit(xs, ys, 1)[0])


def jaccard_decay(pages_words):
    freq = Counter(w for ws in pages_words for w in ws)
    rare = [set(w for w in ws if 2 <= freq[w] <= 10) for ws in pages_words]
    def jac(i, j):
        u = rare[i] | rare[j]
        return len(rare[i] & rare[j]) / len(u) if u else 0.0
    adj = np.mean([jac(i, i + 1) for i in range(len(rare) - 1)])
    far = np.mean([jac(i, i + 25) for i in range(len(rare) - 25)])
    return float(adj), float(far), float(adj / far) if far else float("inf")


def measures(pages_words):
    flat = [w for ws in pages_words for w in ws]
    adj, far, ratio = jaccard_decay(pages_words)
    return heaps_beta(flat), adj, far, ratio


def main():
    by = b4.pages()
    pages = list(by)  # insertion order = file/bound order
    quire_of = {}
    for p in pages:
        quire_of[p] = by[p][0].get("quire", "?")
    pw = {p: [w for r in by[p] for w in r["words"] if "?" not in w] for p in pages}
    quires = sorted(set(quire_of.values()))
    qblocks = {q: [p for p in pages if quire_of[p] == q] for q in quires}
    hb, adj, far, ratio = measures([pw[p] for p in pages])
    emit(f"BOUND order: heaps_beta={hb:.3f} rareJac_adj={adj:.4f} far={far:.4f} ratio={ratio:.2f} "
         f"({len(pages)} pages, quires={quires})")
    hp, adjp, farp, ratiop = measures([pw[p] for p in reversed(pages)])
    emit(f"REVERSED   : heaps_beta={hp:.3f} rareJac_adj={adjp:.4f} far={farp:.4f} ratio={ratiop:.2f}")
    rng = random.Random(SEED)
    for name, make in (
            ("quire-permuted", lambda: [p for q in rng.sample(quires, len(quires)) for p in qblocks[q]]),
            ("page-permuted", lambda: rng.sample(pages, len(pages)))):
        vals = [measures([pw[p] for p in make()]) for _ in range(30)]
        arr = np.array(vals)
        emit(f"{name} (30x): heaps {arr[:,0].min():.3f}..{arr[:,0].max():.3f} (mean {arr[:,0].mean():.3f}) | "
             f"adj {arr[:,1].min():.4f}..{arr[:,1].max():.4f} | ratio {arr[:,3].min():.2f}..{arr[:,3].max():.2f} (mean {arr[:,3].mean():.2f})")
    emit("Reading: bound-order stats outside quire-permutation range => survive "
         "bifolio/quire-level reordering; inside => order-fragile, singulion order matters.")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    emit("Wrote results_p1.txt")


if __name__ == "__main__":
    main()
