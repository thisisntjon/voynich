"""B4: does pure self-citation produce Voynich's line-edge effects without hard-coding?

Claim (user document, "Testing the Three Surviving Computational Paradigms"):
  in Timm & Schinner's generator the line-initial gallows (p/f) preference and
  line-final -m markers "do not emerge naturally from self-citation; they had
  to be hard-coded".
Test: a Timm-style generator with NO position-dependent rule. Each page keeps
Voynich's real line count and line lengths. Line 1 is a seed; every later word
copies a source word (p=0.28 the same column of a random earlier line on the
page, otherwise a random word of the previous two lines) and, with p=0.7,
mutates it to a random single-glyph-edit neighbour drawn from the real Voynich
vocabulary (frequency-weighted). Variants:
  SIM_global : seed line = random Voynich tokens (unigram). Null for position.
  SIM_seeded : seed line = the page's real first line (carries the real
               page-first gallows bias) - can copying spread it to later lines?
Measured on lines 2+ of each page (the seed line is excluded) and on the real
Voynich lines 2+: JSD(first glyph of line-initial words, mid-line words),
JSD(last glyph of line-final words, mid-line words), each against a
within-line shuffle null; p/m enrichment; h2; same-column edit<=1 copy rate.
Control: Dante verse lines (a2_position.verse_lines).
Run: python b4_selfcite_sim.py  -> results_b4.txt
"""
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import corpora
from a2_position import stats, null, verse_lines

OUT = Path(__file__).parent / "results_b4.txt"
P_SAMECOL = 0.28
P_MUTATE = 0.7
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def edit1(a, b):
    if a == b:
        return False
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb:
        a, b = b, a
    for i in range(len(b)):
        if b[:i] + b[i + 1:] == a:
            return True
    return False


def build_neighbours(freq):
    """single-glyph-edit neighbours using a deletion index (glyph tokenization)."""
    g = {w: corpora.to_glyphs(w, corpora.GLYPHS_PLUS) for w in freq}
    back = {v: k for k, v in g.items()}
    dele = defaultdict(set)
    for w, s in g.items():
        dele[s].add(w)
        for i in range(len(s)):
            dele[s[:i] + s[i + 1:]].add(w)
    nb = {}
    for w, s in g.items():
        cand = set(dele[s])
        for i in range(len(s)):
            cand |= dele[s[:i] + s[i + 1:]]
        cand.discard(w)
        cand = [c for c in cand if edit1(s, g[c])]
        if cand:
            nb[w] = (cand, [freq[c] for c in cand])
    return nb


def pages():
    by = defaultdict(list)
    for r in corpora.voynich_lines():
        by[r["page"]].append(r)
    return by


def generate(variant, seed, by=None, p_samecol=P_SAMECOL, p_mut=P_MUTATE, recent_lines=2):
    rng = random.Random(seed)
    by = by or pages()
    all_words = [w for p in by.values() for r in p for w in r["words"]]
    freq = Counter(all_words)
    nb = build_neighbours(freq)
    pool = list(freq); weights = [freq[w] for w in pool]
    out = {}
    for page, recs in by.items():
        lines = []
        for li, r in enumerate(recs):
            n = len(r["words"])
            if li == 0:
                line = list(r["words"]) if variant == "seeded" else rng.choices(pool, weights, k=n)
            else:
                line = []
                for j in range(n):
                    same = [l for l in lines if len(l) > j]
                    if same and rng.random() < p_samecol:
                        src = rng.choice(same)[j]
                    else:
                        recent = [w for l in lines[-recent_lines:] for w in l] + line
                        src = rng.choice(recent)
                    if rng.random() < p_mut and src in nb:
                        c, wt = nb[src]
                        src = rng.choices(c, wt)[0]
                    line.append(src)
            lines.append(line)
        out[page] = [dict(recs[i], words=lines[i]) for i in range(len(recs))]
    return out


def h2(words):
    s = "_".join(words)
    c1 = Counter(s); c2 = Counter(zip(s, s[1:]))
    n1, n2 = sum(c1.values()), sum(c2.values())
    H1 = -sum(v / n1 * math.log2(v / n1) for v in c1.values())
    H12 = -sum(v / n2 * math.log2(v / n2) for v in c2.values())
    return H12 - H1


def samecol_rate(by):
    hit = n = 0
    for recs in by.values():
        for a, b in zip(recs, recs[1:]):
            for j, w in enumerate(b["words"]):
                if j < len(a["words"]):
                    n += 1
                    hit += a["words"][j] == w or edit1(a["words"][j], w)
    return hit / n


def enrich(lines, ch, where):
    pos = Counter(); mid = Counter()
    for ws in lines:
        if len(ws) < 3:
            continue
        pos[(ws[0][0] if where == "first" else ws[-1][-1]) == ch] += 1
        for w in ws[1:-1]:
            mid[(w[0] if where == "first" else w[-1]) == ch] += 1
    a = pos[True] / sum(pos.values()); b = mid[True] / max(sum(mid.values()), 1)
    return a / b if b else float("inf")


def report(name, by=None, lines=None):
    if lines is None:
        lines = [r["words"] for recs in by.values() for r in recs[1:]]
    f1, _ = stats(lines, lambda w: w[0]); n1 = null(lines, lambda w: w[0], n=20)
    _, l1 = stats(lines, lambda w: w[-1]); n2 = null(lines, lambda w: w[-1], n=20)
    words = [w for l in lines for w in l]
    rep = sum(a == b for a, b in zip(words, words[1:])) / len(words)
    sc = f"{samecol_rate(by):.3f}" if by else "  -  "
    emit(f"{name:16} JSDfirst={f1:.4f} (null {n1[:,0].mean():.4f})  JSDlast={l1:.4f} (null {n2[:,1].mean():.4f})"
         f"  p-init x{enrich(lines,'p','first'):5.2f}  m-final x{enrich(lines,'m','last'):5.2f}"
         f"  h2={h2(words):.3f}  repeat={100*rep:.2f}%  samecol_edit<=1={sc}  tokens={len(words)}")


def main():
    emit("B4: self-citation generator without positional rules (lines 2+ of each page)")
    emit(f"SIM: P_SAMECOL={P_SAMECOL} P_MUTATE={P_MUTATE}, pool=previous 2 lines; SIMcal: 0.05/0.97, pool=whole page so far; null = within-line word shuffle (20 reps)")
    emit("x-values = rate at line start/end divided by rate mid-line")
    emit()
    by = pages()
    report("VOYNICH", by)
    for v in ("global", "seeded"):
        for s in (1, 2):
            report(f"SIM_{v}_s{s}", generate(v, s, by))
    # calibrated variant: copying weak enough to match Voynich's immediate-repeat
    # and same-column rates (whole page so far as source pool, more mutation)
    for v in ("global", "seeded"):
        report(f"SIMcal_{v}", generate(v, 3, by, p_samecol=0.05, p_mut=0.97, recent_lines=99))
    report("CTRL_dante", lines=verse_lines("italian_dante"))
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
