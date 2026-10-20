"""F1: once the cross-space edge table is known, is any word order left?

E2 showed Voynich's 0.195-bit cross-space coupling is a P(first glyph | last
glyph) table. E1 showed within-line token information is tiny (+0.028 bits vs
Dante +0.536). If Voynich encodes a language, word order should carry
information BEYOND the edge glyphs (syntax, collocations, phrases). If it is a
notation or generator with an edge rule, the edge table should account for
nearly all of it.

Held-out language-model test (bits per token, lower = better). Each text is
split into train/test by alternating blocks (Voynich: even/odd pages;
controls: alternating 20-line blocks). Pairs are adjacent tokens within a line.
  U   unigram P(w)                         add-0.5, shared UNK
  E   edge     P(w | last glyph of prev)   Witten-Bell backoff to U
  E2  edge-2   P(w | last two glyphs)      Witten-Bell backoff to E
  W   word     P(w | prev word)            Witten-Bell backoff to E2
Witten-Bell: P(w|h) = (c(h,w) + m*T(h)*P_back(w)) / (c(h) + m*T(h)), T(h) =
distinct followers of h; m from a fixed grid on the test half (same optimism
for all texts). (A first run used plain additive backoff; every conditional
model, controls included, scored worse than unigram, so that estimator was
replaced before any verdict was used. Thresholds below are unchanged.)
  edge gain     = U - E2       (what the edge table buys)
  residual gain = E2 - W       (word order beyond the edge table)
  share = residual / (U - W)
Texts: Voynich all / Currier A / Currier B; null: Voynich tokens shuffled
within lines; Naibbe (c4 skeleton); c2 section generator; six prose controls
cut into 9-word lines, first 33,000 tokens; Dante verse lines.

Pre-registered reading (written before running):
  (gains are taken as excess over the same text's within-line shuffle; this
  calibration was added after the first runs showed raw residuals < 0 on
  controls; the verdict prints NO POWER if a prose control is <= 0.01 bits)
  favours LANGUAGE (syntax present): Voynich residual gain >= 0.25 x the
      smallest prose-control residual gain AND > 3 x the within-line-shuffle
      null's residual gain.
  favours EDGE-RULE notation/generator: Voynich residual gain <= 0.10 x the
      smallest prose-control residual gain, or within 2 x the shuffle null.
  otherwise INCONCLUSIVE.
Run: python f1_residual_order.py  -> results_f1.txt
"""
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import b4_selfcite_sim as b4
import c2_section_generator as c2
import c3_edge_coupling as c3
import c4_naibbe_lines as c4
import corpora

OUT = Path(__file__).parent / "results_f1.txt"
GRID_A = (0.25, 0.5, 1, 2, 4)
GRID_K = (0.25, 0.5, 1, 2, 4)
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def pairs_of(lines):
    return [(a, b) for ws in lines for a, b in zip(ws, ws[1:])]


TOPN = None   # None = whole words; else words outside the train top-N -> <first..last> class


def mapper(train_lines, topn):
    if not topn:
        return lambda w: w
    top = {w for w, _ in Counter(w for ws in train_lines for w in ws).most_common(topn)}
    return lambda w: w if w in top else f"<{w[0]}.{w[-1]}>"


class Models:
    """Target and word context are mapped tokens; edge contexts use the real
    last glyphs of the previous token."""
    def __init__(self, train_lines, f):
        self.f = f
        toks = [f(w) for ws in train_lines for w in ws]
        self.uni = Counter(toks); self.n = len(toks); self.V = len(self.uni) + 1
        self.e1 = defaultdict(Counter); self.e2 = defaultdict(Counter); self.w = defaultdict(Counter)
        for a, b in pairs_of(train_lines):
            b = f(b)
            self.e1[a[-1]][b] += 1; self.e2[a[-2:]][b] += 1; self.w[f(a)][b] += 1

    def pu(self, w):
        return (self.uni.get(w, 0) + 0.5) / (self.n + 0.5 * self.V)

    @staticmethod
    def wb(c, w, m, back):
        if not c:
            return back
        t = m * len(c)
        return (c.get(w, 0) + t * back) / (sum(c.values()) + t)

    def pe(self, prev, w, a):
        return self.wb(self.e1.get(prev[-1]), w, a, self.pu(w))

    def pe2(self, prev, w, a):
        return self.wb(self.e2.get(prev[-2:]), w, a, self.pe(prev, w, a))

    def pw(self, prev, w, a, k):
        return self.wb(self.w.get(self.f(prev)), w, k, self.pe2(prev, w, a))


def bits(test_pairs, f):
    return -sum(math.log2(f(a, b)) for a, b in test_pairs) / len(test_pairs)


def evaluate(train, test):
    f = mapper(train, TOPN)
    m = Models(train, f)
    tp = [(a, f(b)) for a, b in pairs_of(test)]
    U = bits(tp, lambda a, b: m.pu(b))
    E = min(bits(tp, lambda a, b: m.pe(a, b, x)) for x in GRID_A)
    best_a = min(GRID_A, key=lambda x: bits(tp, lambda a, b: m.pe2(a, b, x)))
    E2 = bits(tp, lambda a, b: m.pe2(a, b, best_a))
    W = min(bits(tp, lambda a, b: m.pw(a, b, best_a, k)) for k in GRID_K)
    return U, E, E2, W, len(tp)


def split_blocks(lines, block=20):
    tr = [l for i, l in enumerate(lines) if (i // block) % 2 == 0]
    te = [l for i, l in enumerate(lines) if (i // block) % 2 == 1]
    return tr, te


def split_pages(by):
    tr, te = [], []
    for i, recs in enumerate(by.values()):
        (tr if i % 2 == 0 else te).extend(r["words"] for r in recs)
    return tr, te


def shuffled(lines, seed=3):
    rng = random.Random(seed)
    return [rng.sample(l, len(l)) for l in lines]


def row(name, tr, te):
    """Residual and edge gains, each minus the same text's within-line-shuffle
    value (train and test both shuffled), which removes the backoff cost a
    sparse word model pays on small data."""
    U, E, E2, W, n = evaluate(tr, te)
    sU, sE, sE2, sW, _ = evaluate(shuffled(tr), shuffled(te))
    edge = (U - E2) - (sU - sE2)
    resid = (E2 - W) - (sE2 - sW)
    emit(f"{name:26} U={U:6.3f} E2={E2:6.3f} W={W:6.3f}  edge gain={U - E2:+.3f} (shuf {sU - sE2:+.3f}, excess {edge:+.3f})"
         f"  residual={E2 - W:+.3f} (shuf {sE2 - sW:+.3f}, excess {resid:+.3f})  pairs={n}")
    return resid


def main():
    global TOPN
    for TOPN in (None, 100, 300):
        run()
    OUT.write_text(chr(10).join(log) + chr(10), encoding="utf-8")


def run():
    emit(f"=== F1, target vocabulary: {'whole words' if not TOPN else f'top-{TOPN} train words, others -> <first.last> class'} ===")
    emit("held-out bits/token; residual = word-order gain beyond last-two-glyph edge table")
    emit()
    by = b4.pages()
    v = row("VOYNICH all", *split_pages(by))
    for lang in "AB":
        sub = {p: recs for p, recs in by.items() if recs[0]["lang"] == lang}
        row(f"VOYNICH Currier {lang}", *split_pages(sub))
    flat = [w for recs in by.values() for r in recs for w in r["words"]]
    random.Random(5).shuffle(flat)
    it = iter(flat)
    nul = row("NULL token-shuffled MS", *split_pages({p: [dict(r, words=[next(it) for _ in r["words"]]) for r in recs]
                                                     for p, recs in by.items()}))
    emit()
    nb = c4.skeleton(c4.naibbe_tokens(), by)
    row("NAIBBE (c4 skeleton)", *split_pages(nb))
    g = c2.Gen(by)
    row("c2 section ps=0.6", *split_pages(g.generate("section", 2, p_seed=0.6)))
    emit()
    ctrl = {}
    for name in corpora.CONTROLS:
        ctrl[name] = row(f"CTRL {name}", *split_blocks(c3.prose_lines(name)))
    row("CTRL dante verse lines", *split_blocks(b4.verse_lines("italian_dante")))
    emit()
    lo = min(ctrl.values())
    emit(f"residual excess: smallest prose = {lo:+.3f}; Voynich = {v:+.3f}; token-shuffled null = {nul:+.3f}")
    if lo <= 0.01:
        verdict = "NO POWER (a prose control shows no residual word order at this size)"
    elif v >= 0.25 * lo and v > 3 * max(nul, 1e-9):
        verdict = "FAVOURS LANGUAGE (word order beyond the edge table)"
    elif v <= 0.10 * lo or v <= 2 * max(nul, 0.0):
        verdict = "FAVOURS EDGE-RULE NOTATION/GENERATOR"
    else:
        verdict = "INCONCLUSIVE"
    emit(f"pre-registered verdict: {verdict}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
