"""E1: do high-coupling joins create language-like word order?

Pre-registered in this file before the run. Decision thresholds below are
not to be edited after results_e1.txt exists.

Question: the largest cross-space couplings (results_d1.txt) may be false
word breaks. Joining those boundaries should then raise adjacent-token
information and character h2. A random join of the same number of
boundaries is the null. If the targeted join only removes the coupling and
leaves token order where it was, the coupling is a production rule between
separate tokens.

Policies
  BASE   ZL paragraph tokens, comma = break, '?' tokens dropped
  STRICT commas are not breaks (vparse strict_spaces)
  J1     join an original boundary iff left ends 'y' and right starts 'q'
  J2     join iff (left[-1], right[0]) is in the d1 top-8 pairs
  NULL   20 reps: join the same count of original boundaries as J2, at random
  PMI1   join iff PMI(last, first) > 1 bit, PMI fit on even pages, scored on odd

TOP8 is copied from results_d1.txt and is not refit here:
  y-q, r-a, n-c, s-a, n-o, y-l, r-c, l-d

Joins are decided on the original tokens. Consecutive joins chain.
Metrics use within-line pairs only.
  h2             a1 char conditional entropy, space between tokens
  cross_mi       plug-in MI(last char; first char) of remaining boundaries
  tok_frac       (H_cond shuffled within line - H_cond) / H(token)
                 positive means adjacent tokens predict each other

Decision, using J* = whichever of J1, J2, PMI1 has the higher tok_frac
  FAVOUR_RESEGMENT  J*.tok_frac >= BASE + 0.02
                    and J*.tok_frac >= NULL mean + 0.02
                    and J*.h2 >= NULL mean h2 + 0.15
  FAVOUR_RULE       J1.cross_mi <= 0.5 * BASE.cross_mi
                    and J1.tok_frac < BASE + 0.02
  else INCONCLUSIVE
A text can print both flags. STRICT is a sensitivity row, not in the decision.
Dante and Caesar are chunked into 9-word lines and scored at BASE only.
"""
import math
import random
from collections import Counter
from pathlib import Path

import a1_profile
import corpora
import vparse

OUT = Path(__file__).parent / "results_e1.txt"
SEED = 20261017
NNULL = 20
TOP8 = {("y", "q"), ("r", "a"), ("n", "c"), ("s", "a"),
        ("n", "o"), ("y", "l"), ("r", "c"), ("l", "d")}

log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def lines_of(recs):
    out = []
    for r in recs:
        ws = [w for w in r["words"] if "?" not in w and w.isalpha()]
        if len(ws) >= 2:
            out.append(ws)
    return out


def boundaries(lines):
    """Original adjacent pairs as (line_index, left_index)."""
    return [(i, j) for i, ws in enumerate(lines) for j in range(len(ws) - 1)]


def apply_joins(lines, join_set):
    """join_set holds (line_index, left_index) into the original lines."""
    out = []
    for i, ws in enumerate(lines):
        groups = [[ws[0]]]
        for j in range(len(ws) - 1):
            if (i, j) in join_set:
                groups[-1].append(ws[j + 1])
            else:
                groups.append([ws[j + 1]])
        out.append(["".join(g) for g in groups])
    return out


def edges(lines):
    return [(a[-1], b[0]) for ws in lines for a, b in zip(ws, ws[1:]) if a and b]


def plug_mi(pairs):
    if not pairs:
        return 0.0
    n = len(pairs)
    pj, pa, pb = Counter(pairs), Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in pj.items())


def token_frac(lines):
    """Excess adjacent-token information / unigram token entropy. Within lines."""
    words = [w for ws in lines for w in ws]
    pairs = [(a, b) for ws in lines for a, b in zip(ws, ws[1:])]
    if len(words) < 2 or not pairs:
        return 0.0, 0.0, 0.0
    def H(counter, n):
        return -sum(v / n * math.log2(v / n) for v in counter.values())
    hw = H(Counter(words), len(words))
    # H(next | prev) = H(pair) - H(prev)
    hp = H(Counter(pairs), len(pairs))
    hprev = H(Counter(a for a, _ in pairs), len(pairs))
    hcond = hp - hprev
    rng = random.Random(SEED)
    shuf = []
    for _ in range(5):
        sp = []
        for ws in lines:
            ws = ws[:]
            rng.shuffle(ws)
            sp.extend(zip(ws, ws[1:]))
        if not sp:
            continue
        shuf.append(H(Counter(sp), len(sp)) - H(Counter(a for a, _ in sp), len(sp)))
    excess = (sum(shuf) / len(shuf) - hcond) if shuf else 0.0
    return excess / hw if hw else 0.0, excess, hw


def lengths(lines):
    lens = [len(w) for ws in lines for w in ws]
    n = len(lens)
    mean = sum(lens) / n
    var = sum((x - mean) ** 2 for x in lens) / n
    return n, mean, var ** 0.5


def score(name, lines, njoin, nbound):
    flat = [w for ws in lines for w in ws]
    h2 = a1_profile.char_entropies(flat)["h2"]
    frac, excess, hw = token_frac(lines)
    n, mean, sd = lengths(lines)
    row = dict(name=name, n=n, mean=mean, sd=sd, h2=h2, cross=plug_mi(edges(lines)),
               frac=frac, excess=excess, hw=hw,
               joined=njoin, rate=(njoin / nbound if nbound else 0.0))
    emit(f"{name:10} n={n:6d} len={mean:5.2f} sd={sd:4.2f} h2={h2:5.3f} "
         f"crossMI={row['cross']:5.3f} tok_excess={excess:6.3f}b "
         f"H={hw:5.2f} tok_frac={frac:7.4f} "
         f"joined={njoin:5d} ({100 * row['rate']:4.1f}%)")
    return row


def pmi_table(lines):
    pairs = edges(lines)
    n = len(pairs)
    pj, pa, pb = Counter(pairs), Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pmi = {}
    for (a, b), c in pj.items():
        pmi[(a, b)] = math.log2((c * n) / (pa[a] * pb[b]))
    return pmi


def main():
    base_recs = vparse.paragraph_text(vparse.load())
    base = lines_of(base_recs)
    strict = lines_of(vparse.paragraph_text(vparse.load(strict_spaces=True)))
    bnds = boundaries(base)
    nbound = len(bnds)

    def pred_join(pred):
        chosen = {(i, j) for i, j in bnds if pred(base[i][j], base[i][j + 1])}
        return apply_joins(base, chosen), len(chosen)

    j1_lines, n1 = pred_join(lambda a, b: a.endswith("y") and b.startswith("q"))
    j2_lines, n2 = pred_join(lambda a, b: (a[-1], b[0]) in TOP8)

    def even_page(page):
        digits = "".join(ch for ch in page if ch.isdigit())
        return int(digits or "0") % 2 == 0
    even_lines = lines_of([r for r in base_recs if even_page(r["page"])])
    odd_recs = [r for r in base_recs if not even_page(r["page"])]
    odd_lines = lines_of(odd_recs)
    pmi = pmi_table(even_lines)
    odd_b = boundaries(odd_lines)
    pmi_set = {(i, j) for i, j in odd_b
               if pmi.get((odd_lines[i][j][-1], odd_lines[i][j + 1][0]), 0.0) > 1.0}
    pmi_lines = apply_joins(odd_lines, pmi_set)

    emit("E1 resegmentation  seed=20261017  paragraph P*  '?' dropped")
    emit("tok_frac = within-line adjacent-token excess / token entropy")
    emit(f"boundaries={nbound}  even-pages PMI fit, odd-pages PMI1 score")
    emit()
    rows = {}
    rows["BASE"] = score("BASE", base, 0, nbound)
    rows["STRICT"] = score("STRICT", strict, 0, sum(len(ws) - 1 for ws in strict))
    rows["J1"] = score("J1 y-q", j1_lines, n1, nbound)
    rows["J2"] = score("J2 top8", j2_lines, n2, nbound)
    rows["ODD"] = score("ODD base", odd_lines, 0, len(odd_b))
    rows["PMI1"] = score("PMI1 odd", pmi_lines, len(pmi_set), len(odd_b))

    rng = random.Random(SEED)
    null_frac, null_h2, null_cross = [], [], []
    for rep in range(NNULL):
        chosen = set(rng.sample(bnds, n2))
        lines = apply_joins(base, chosen)
        flat = [w for ws in lines for w in ws]
        null_frac.append(token_frac(lines)[0])
        null_h2.append(a1_profile.char_entropies(flat)["h2"])
        null_cross.append(plug_mi(edges(lines)))
    nf = sum(null_frac) / NNULL
    nh = sum(null_h2) / NNULL
    nc = sum(null_cross) / NNULL
    emit(f"{'NULL':10} reps={NNULL} join_count={n2}  "
         f"h2={nh:5.3f} crossMI={nc:5.3f} tok_frac={nf:6.4f}")

    for name in ("italian_dante", "latin_caesar"):
        words = corpora.control(name)
        chunked = [words[i:i + 9] for i in range(0, len(words) - 9, 9)]
        score(name[:10], chunked, 0, sum(len(ws) - 1 for ws in chunked))

    cands = [("J1", rows["J1"]), ("J2", rows["J2"]), ("PMI1", rows["PMI1"])]
    best_name, best = max(cands, key=lambda kv: kv[1]["frac"])
    base_f, base_c = rows["BASE"]["frac"], rows["BASE"]["cross"]
    # PMI1 is scored on odd pages; compare its frac to ODD base, its h2 to NULL
    # only when the winner is J1 or J2. If PMI1 wins the frac ranking, compare
    # against ODD and do not use the all-page NULL (different sample).
    emit()
    emit(f"best tok_frac among J1/J2/PMI1: {best_name} = {best['frac']:.4f}")
    flags = []
    if best_name == "PMI1":
        if (best["frac"] >= rows["ODD"]["frac"] + 0.02
                and best["h2"] >= rows["ODD"]["h2"] + 0.15):
            flags.append("FAVOUR_RESEGMENT")
    elif (best["frac"] >= base_f + 0.02 and best["frac"] >= nf + 0.02
          and best["h2"] >= nh + 0.15):
        flags.append("FAVOUR_RESEGMENT")
    if rows["J1"]["cross"] <= 0.5 * base_c and rows["J1"]["frac"] < base_f + 0.02:
        flags.append("FAVOUR_RULE")
    if not flags:
        flags.append("INCONCLUSIVE")
    emit("DECISION: " + " ".join(flags))
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
