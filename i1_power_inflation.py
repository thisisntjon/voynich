"""I1: power check for F4 under Voynich-like type inflation.

F4 found no homophone classes in Voynich, but its positive control (F3 flow
cipher, ~4.7k types) is less type-rich than Voynich (~7k types, hapax share
~0.68). Question: does F4's FROZEN procedure still recover classes when the
known cipher is given Voynich-like inflation? If not, F4's Voynich negative
is uninformative about the cipher family.

Inflation: every Naibbe piece gets m-1 extra homophones made by Voynich-style
spelling alternations (ch<->sh, e<->ee, i<->ii, k<->t, o-prefix, y<->dy ...),
weighted Zipf-like (weight 1/(rank+1)^ZIPF) so most variants are rare. Then
f3.cipher_stream(beta=1.5) as in the F4 control; the true unit is unchanged.
The F4 procedure (f4.analyse, f4.heldout, parameters P, FRACS) is imported
and not modified.

Run: python i1_power_inflation.py [m ...]  -> results_i1.txt
"""
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import b4_selfcite_sim as b4
import c4_naibbe_lines as c4
import f3_flow_choice as f3
import f4_homophone_classes as f4

OUT = Path(__file__).parent / "results_i1.txt"
ZIPF = 1.2
RULES = [("ch", "sh"), ("sh", "ch"), ("ee", "e"), ("e", "ee"), ("ii", "i"), ("i", "ii"),
         ("k", "t"), ("t", "k"), ("o", "a"), ("a", "o"), ("y", "dy"), ("l", "r"), ("r", "l")]


def variants(piece, m, rng):
    """piece plus up to m-1 distinct spelling variants (1-2 rule applications)."""
    out, tries = [piece], 0
    while len(out) < m and tries < 60 * m:
        tries += 1
        v = piece
        for _ in range(rng.choice((1, 1, 2))):
            a, b = rng.choice(RULES)
            idx = [i for i in range(len(v)) if v.startswith(a, i)]
            if idx:
                i = rng.choice(idx)
                v = v[:i] + b + v[i + len(a):]
        if rng.random() < 0.15:
            v = "o" + v
        if v and v not in out:
            out.append(v)
    return out


def inflate(tab, m, seed=0):
    rng = random.Random(seed)
    new = defaultdict(lambda: defaultdict(Counter))
    for role, by_letter in tab.items():
        for letter, pieces in by_letter.items():
            for piece, c in pieces.items():
                for r, v in enumerate(variants(piece, m, rng)):
                    new[role][letter][v] += c / (r + 1) ** ZIPF
    return new


def control(m):
    by = b4.pages()
    R = f3.ratio_table(by)
    seq, tab = f3.naibbe_chunks()
    toks = f3.cipher_stream(seq, inflate(tab, m) if m > 1 else tab, R, 1.5, seed=2)
    sk = c4.skeleton(list(zip(toks, ["".join(l) for l, _ in seq])), by)
    return {p: [dict(r, words=[w for w, _ in r["words"]], units=[u for _, u in r["words"]]) for r in recs]
            for p, recs in sk.items()}


def type_stats(by):
    c = Counter(w for l in f4.lines_of(by) for w in l)
    return len(c), sum(v == 1 for v in c.values()) / len(c), sum(c.values())


def main():
    ms = [int(x) for x in sys.argv[1:]] or [1, 2, 3, 5, 8]
    log = ["I1: F4 frozen procedure on the F3 flow cipher with m homophones per piece (Zipf weights).",
           "cot = honest held-out (odd->even) class-over-token, bits/token minus line-shuffled; 3 KMeans seeds.", ""]
    vt, vh, vn = type_stats(b4.pages())
    log.append(f"VOYNICH reference: tokens {vn}  types {vt}  hapax share {vh:.3f}   (F4: cot mean -0.005, null -0.004)")
    log.append("")
    for m in ms:
        by = control(m)
        nt, hs, nn = type_stats(by)
        res, _ = f4.analyse(f"CONTROL m={m}", by)
        A, B = f4.page_halves(by)
        cots = [res["rev"]["cot"]] + [f4.heldout(B, A, res["f"], seed=s)["cot"] for s in (1, 2)]
        tari = np.mean([t[0] for t in res["truth"]])
        null = f4.shuffled_book(by)
        nres, _ = f4.analyse(f"NULL m={m}", null)
        nA, nB = f4.page_halves(null)
        ncots = [nres["rev"]["cot"]] + [f4.heldout(nB, nA, nres["f"], seed=s)["cot"] for s in (1, 2)]
        line = (f"m={m:<2} tokens {nn}  types {nt:<5} hapax {hs:.3f}  K={res['K']:<4} truth type ARI {tari:.3f}  "
                f"cot {np.mean(cots):+.4f} ({' '.join(f'{x:+.4f}' for x in cots)})  "
                f"null cot {np.mean(ncots):+.4f}  seed ARI {res['seed']:.3f}")
        print(line, flush=True)
        log.append(line)
        OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    log += ["", "Reading: recovery 'holds' if cot stays clearly above its null (gap > ~0.006, the F4 seed spread)",
            "at the m whose types/hapax match Voynich. If it collapses there, F4's Voynich negative is uninformative."]
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
