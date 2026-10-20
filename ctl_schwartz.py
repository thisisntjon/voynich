"""G control 2: Schwartz (2026) keyless writing procedure, implemented in Python.

THIS IS A RE-IMPLEMENTATION FROM THE PREPRINT TEXT, not Schwartz's code (none is published).
Preprint: data/external/schwartz-2026-preprint/text.txt (bootloops.ai/voynich.pdf, 2026-10-01);
line numbers below (L###) refer to that text file. Seed 20261017.

The procedure (§5.2, L845-859; Figure 6 caption L836-844): "Each word is written by one pass
through the loop: a check of the position on the line, an adjustment toward the previous word's
length, then one of three branches (reuse of a word from the scribe's own vocabulary, a copy of
a recent word, or a fresh coinage by letter habit)". Implemented per Voynich page in the real
ZL3b page/line shape (ctl_common.voynich_pages), one generator state per hand.

Parameters, with source
-----------------------
 branch shares (Table 2 block ii, L796-799; posterior branch probabilities on test-half tokens):
    Scribe 1 (hand 1):  reuse 0.729, copy 0.020, coin 0.251
    Scribe 2 (hand 2):  reuse 0.767, copy 0.049, coin 0.184
    Hands 3/4/5/? were not fitted by Schwartz (L661); here they take Scribe 1's shares when
    their Currier language is A and Scribe 2's when it is B (L1,'?' -> Scribe 1).
 reuse: "frequency-weighted draws from the scribe's own vocabulary" (L847-848); vocabulary and
    weights = the hand's own ZL3b paragraph tokens (Appendix C, L1533: "reused words ... drawn
    from Scribe 2's observed vocabulary").
 copy: "copied from one of the preceding twenty or so words, mostly on the same page" (L848-849);
    source = uniform over the preceding <= 20 words of the current page (COPY_SPAN=20; a page's
    first word falls back to reuse). "nearly all verbatim" for Scribe 2 (L850); a copy counts as
    such "when it lies within one glyph edit" (L1237). P_VERBATIM = 0.9 for both hands (the
    preprint gives no number; assumption, documented), else one random single-glyph edit
    (substitute / insert / delete one EVA character from the hand's glyph inventory).
 coin: "coined afresh, following the scribe's letter habits" (L851); "new spellings being drawn
    from a glyph-bigram model" (L1240). Bigram model (with start/end symbols, add-0.01
    smoothing) over FOLDED units "iin, ii, ee, ch, sh" (L221-222, the primary parsing), fitted on
    the hand's tokens.
 line-boundary words: "a preference for particular words at line boundaries ... distinct words
    rather than ordinary words modified at the line's edge" (L852-857); "line-start factors" are
    "fitted values not used elsewhere in the paper" (L843-844) and are NOT printed, so they are
    fitted here from ZL3b per hand: the line-initial word distribution P_init is decomposed as
    w_init*B_init + (1-w_init)*P_mid with P_mid the mid-line distribution, w_init = total
    variation distance TV(P_init, P_mid) and B_init = normalised positive excess
    max(P_init - P_mid, 0). With prob w_init a line-initial token is drawn from B_init (skipping
    the three branches); the same for line-final words (w_final, B_final). A one-word line counts
    as line-initial. Only word types with >= MIN_COUNT (3) tokens in the hand enter the excess:
    with every type (MIN_COUNT=1) the TV distance is inflated by sampling noise of the ~70 %
    hapax vocabulary (hand 1 w_init 0.658 over 735 types, hand 2 0.675 over 536; that run gave
    p-init x5.96, m-final x6.68); with MIN_COUNT=3 hand 1 w_init 0.297 (214 types), hand 2 0.353
    (154). Sensitivity: w_init(hand 1) = 0.216 / 0.149 / 0.063 at MIN_COUNT 5 / 10 / 20, and the
    share of p-initial words in B_init falls to 0 by MIN_COUNT 10: Voynich's p-initial line
    words are mostly rare types, so a "distinct boundary words" model cannot carry the x16
    p-initial enrichment, whatever the cut. MIN_COUNT is the one choice the preprint leaves open.
 word-length correlation: "a short-range correlation in word length" (L855), "an adjustment
    toward the previous word's length" (L838); value not printed. Implemented as a tilt
    exp(-beta*|len(w) - len(prev)|) on reuse weights and copy candidates, and as rejection
    sampling with the same kernel on coinage (<= 20 tries). beta per hand is fitted by bisection
    so that the generated within-line lag-1 Pearson correlation of word length matches the
    hand's ZL3b value (fit printed at run time).
Not implemented: nothing else is in the procedure as described; Schwartz's own page layout
is "the same number of words on each corresponding line" (L1528-1529), as here.

Outputs: data/controls_synthetic/schwartz_reuse.txt / .meta.json ; parameters printed and
stored in the sidecar under "fit".
Run:  python ctl_schwartz.py
"""
import math
import random
import re
from collections import Counter, defaultdict

import ctl_common as cc

SEED = 20261017
COPY_SPAN = 20
P_VERBATIM = 0.9
MIN_COUNT = 3
SHARES = {"1": dict(reuse=0.729, copy=0.020, coin=0.251),
          "2": dict(reuse=0.767, copy=0.049, coin=0.184)}
FOLD = re.compile(r"iin|ii|ee|ch|sh|.")
MAXLEN = 14


def share_key(hand, lang):
    if hand in SHARES:
        return hand
    return "2" if lang == "B" else "1"


def tv_decompose(pos, mid, freq):
    """w = TV(P_pos, P_mid) over types with >= MIN_COUNT tokens; B = normalised positive excess."""
    npos, nmid = sum(pos.values()), sum(mid.values())
    exc = {w: pos[w] / npos - mid.get(w, 0) / nmid for w in pos if freq[w] >= MIN_COUNT}
    exc = {w: v for w, v in exc.items() if v > 0}
    tot = sum(exc.values())
    ws = sorted(exc)
    return tot, ws, [exc[w] / tot for w in ws]


def lag1_corr(pages):
    xs, ys = [], []
    for p in pages:
        for l in p["lines"]:
            for a, b in zip(l, l[1:]):
                xs.append(len(a)); ys.append(len(b))
    n = len(xs); mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs); syy = sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy)


class HandModel:
    def __init__(self, hand, pages):
        self.hand = hand
        self.pages = pages
        toks = [w for p in pages for l in p["lines"] for w in l]
        self.freq = Counter(toks)
        self.vocab = sorted(self.freq)
        self.vw = [self.freq[w] for w in self.vocab]
        self.vlen = [len(w) for w in self.vocab]
        self.glyphs = sorted(set("".join(toks)))
        # boundary words
        first = Counter(l[0] for p in pages for l in p["lines"])
        last = Counter(l[-1] for p in pages for l in p["lines"] if len(l) > 1)
        mid = Counter(w for p in pages for l in p["lines"] for w in l[1:-1])
        self.w_init, self.b_init, self.b_init_w = tv_decompose(first, mid, self.freq)
        self.w_final, self.b_final, self.b_final_w = tv_decompose(last, mid, self.freq)
        # folded glyph bigram model with start "^" and end "$"
        big = defaultdict(Counter)
        for w in toks:
            u = ["^"] + FOLD.findall(w) + ["$"]
            for a, b in zip(u, u[1:]):
                big[a][b] += 1
        units = sorted({u for c in big.values() for u in c} | set(big))
        self.big = {}
        for a in big:
            cand = [u for u in units if u != "^"]
            wts = [big[a][u] + 0.01 for u in cand]
            self.big[a] = (cand, wts)
        self.lag1 = lag1_corr(pages)
        self.beta = 0.0
        self._reuse_cache = {}

    def reuse_weights(self, lprev):
        if lprev is None or self.beta == 0:
            return self.vocab, self.vw
        key = min(lprev, MAXLEN)
        if key not in self._reuse_cache:
            self._reuse_cache[key] = [f * math.exp(-self.beta * abs(n - key)) for f, n in zip(self.vw, self.vlen)]
        return self.vocab, self._reuse_cache[key]

    def coin(self, rng, lprev):
        for _ in range(20):
            u, out = "^", []
            while True:
                cand, wts = self.big[u]
                u = rng.choices(cand, wts)[0]
                if u == "$" or len(out) > 30:
                    break
                out.append(u)
            w = "".join(out) or rng.choice(self.vocab)
            if lprev is None or self.beta == 0 or rng.random() < math.exp(-self.beta * abs(len(w) - lprev)):
                return w
        return w

    def edit1(self, rng, w):
        g = rng.choice(self.glyphs)
        i = rng.randrange(len(w) + 1)
        op = rng.random()
        if op < 1 / 3 and i < len(w):
            return w[:i] + g + w[i + 1:]
        if op < 2 / 3 and len(w) > 1 and i < len(w):
            return w[:i] + w[i + 1:]
        return w[:i] + g + w[i:]


def generate(models, template, seed, betas=None):
    rng = random.Random(seed)
    out = []
    for p in template:
        m = models[p["hand"]]
        sh = SHARES[share_key(p["hand"], p["lang"])]
        if betas is not None:
            m.beta = betas.get(p["hand"], 0.0); m._reuse_cache.clear()
        page_words = []
        lines = []
        for l in p["lines"]:
            line = []
            n = len(l)
            for j in range(n):
                lprev = len(line[-1]) if line else None
                w = None
                if j == 0 and rng.random() < m.w_init:
                    w = rng.choices(m.b_init, m.b_init_w)[0]
                elif j == n - 1 and n > 1 and rng.random() < m.w_final:
                    w = rng.choices(m.b_final, m.b_final_w)[0]
                else:
                    r = rng.random()
                    if r < sh["copy"] and page_words:
                        cands = page_words[-COPY_SPAN:]
                        wts = [math.exp(-m.beta * abs(len(c) - lprev)) if lprev else 1.0 for c in cands]
                        w = rng.choices(cands, wts)[0]
                        if rng.random() >= P_VERBATIM:
                            w = m.edit1(rng, w)
                    elif r < sh["copy"] + sh["coin"]:
                        w = m.coin(rng, lprev)
                    else:
                        w = rng.choices(*m.reuse_weights(lprev))[0]
                line.append(w); page_words.append(w)
            lines.append(line)
        out.append(dict(p, lines=lines))
    return out


def fit_betas(models, template):
    """Bisection per hand on beta so generated lag-1 length correlation = ZL3b's."""
    betas = {}
    for hand, m in models.items():
        sub = [p for p in template if p["hand"] == hand]
        lo, hi = 0.0, 3.0
        for _ in range(14):
            mid = (lo + hi) / 2
            m.beta = mid; m._reuse_cache.clear()
            c = lag1_corr(generate({hand: m}, sub, SEED + 1))
            if c < m.lag1:
                lo = mid
            else:
                hi = mid
        betas[hand] = (lo + hi) / 2
        m.beta = betas[hand]; m._reuse_cache.clear()
        print(f"hand {hand}: target lag1 corr {m.lag1:+.4f} -> beta {betas[hand]:.4f} "
              f"(generated {lag1_corr(generate({hand: m}, sub, SEED + 1)):+.4f})")
    return betas


def main():
    template = cc.voynich_pages()
    by_hand = defaultdict(list)
    for p in template:
        by_hand[p["hand"]].append(p)
    models = {h: HandModel(h, ps) for h, ps in by_hand.items()}
    fit = {}
    for h, m in sorted(models.items()):
        print(f"hand {h}: pages {len(m.pages)} tokens {sum(m.vw)} types {len(m.vocab)} shares={SHARES[share_key(h, m.pages[0]['lang'])]} "
              f"w_init {m.w_init:.3f} ({len(m.b_init)} boundary types, top {m.b_init[max(range(len(m.b_init)), key=lambda i: m.b_init_w[i])]}) "
              f"w_final {m.w_final:.3f} ({len(m.b_final)} types, top {m.b_final[max(range(len(m.b_final)), key=lambda i: m.b_final_w[i])]})")
    betas = fit_betas(models, template)
    for h, m in models.items():
        fit[h] = dict(shares=SHARES[share_key(h, m.pages[0]["lang"])], w_init=m.w_init, w_final=m.w_final,
                      n_boundary_init=len(m.b_init), n_boundary_final=len(m.b_final),
                      lag1_target=m.lag1, beta=betas[h], vocab_types=len(m.vocab), vocab_tokens=sum(m.vw))
    pages = generate(models, template, SEED, betas)
    print(f"generated lag1 corr overall {lag1_corr(pages):+.4f} vs Voynich {lag1_corr(template):+.4f}")
    cc.write_control("schwartz_reuse", pages, seed=SEED, source="Python re-implementation of Schwartz 2026 §5.2 (ctl_schwartz.py)",
                     params=dict(COPY_SPAN=COPY_SPAN, P_VERBATIM=P_VERBATIM, MIN_COUNT=MIN_COUNT, folded_units="iin ii ee ch sh"), fit=fit)
    print(cc.stats_row("schwartz_reuse", cc.ctl_stats(pages)))


if __name__ == "__main__":
    main()
