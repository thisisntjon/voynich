"""D1 EDGE COUPLING: does information cross the spaces in Voynich text?

Measures, per corpus (common sample N tokens so plug-in bias is comparable):
 (a) MI in bits between LAST char/glyph of word i and FIRST of word i+1 (across spaces),
 (b) MI between adjacent chars WITHIN words (scale reference),
 (c) next-token predictability: word-bigram conditional-entropy reduction vs unigram,
     as % of unigram token entropy, raw (plug-in) and shuffle-corrected.

Voynich pairs are taken only WITHIN a manuscript line (no pair spans a line/page break);
controls are continuous streams. MI is reported plug-in, Miller-Madow corrected, and
against a permutation null (first-chars shuffled against last-chars, 20 reps).

Nulls (all preserve VMS line lengths): word-shuffled VMS, iid unigram resample,
and a within-word char-bigram Markov pseudo-text (iid words by construction).
"""
import math
import random
from collections import Counter, defaultdict

import numpy as np

import corpora

N = 19000          # common token count (Caesar, the smallest corpus, has 19,520)
SEED = 7
LINES_OUT = []


def emit(s=""):
    print(s)
    LINES_OUT.append(s)


# ---------- entropy / MI helpers ----------
def H(counter, n):
    return -sum(v / n * math.log2(v / n) for v in counter.values())


def mi_plugin(pairs):
    """Return MI, Miller-Madow-corrected MI, H(X), H(Y), counts for (x,y) pairs."""
    n = len(pairs)
    cx, cy, cxy = Counter(), Counter(), Counter()
    for x, y in pairs:
        cx[x] += 1; cy[y] += 1; cxy[(x, y)] += 1
    mi = H(cx, n) + H(cy, n) - H(cxy, n)
    bias = (len(cx) - 1) * (len(cy) - 1) / (2 * n * math.log(2))
    return dict(mi=mi, mi_mm=max(mi - bias, 0.0), hx=H(cx, n), hy=H(cy, n),
                n=n, kx=len(cx), ky=len(cy), cxy=cxy, cx=cx, cy=cy)


def mi_perm_null(pairs, reps=20, seed=SEED):
    xs = [p[0] for p in pairs]; ys = [p[1] for p in pairs]
    rng = random.Random(seed)
    vals = []
    for _ in range(reps):
        y2 = ys[:]; rng.shuffle(y2)
        vals.append(mi_plugin(list(zip(xs, y2)))["mi"])
    return float(np.mean(vals)), float(np.std(vals))


def cross_pairs(lines):
    return [(a[-1], b[0]) for line in lines for a, b in zip(line, line[1:]) if a and b]


def within_pairs(lines):
    return [(w[i], w[i + 1]) for line in lines for w in line for i in range(len(w) - 1)]


def word_gain(lines, n_shuffle=3, seed=SEED):
    """(c) unigram H, bigram conditional H, raw % and shuffle-corrected % gain."""
    words = [w for line in lines for w in line]
    pairs = [(a, b) for line in lines for a, b in zip(line, line[1:])]
    succ = Counter(b for _, b in pairs)          # marginal of the predicted token
    first = Counter(a for a, _ in pairs)
    joint = Counter(pairs)
    h1 = H(succ, len(pairs))
    hcond = H(joint, len(pairs)) - H(first, len(pairs))
    raw_pct = 100 * (h1 - hcond) / h1
    corr_pct = float("nan")
    if n_shuffle:
        rng = random.Random(seed)
        lens = [len(l) for l in lines]
        hs = []
        for _ in range(n_shuffle):
            w = words[:]; rng.shuffle(w)
            sh, i = [], 0
            for L in lens:
                sh.append(w[i:i + L]); i += L
            hs.append(word_gain(sh, n_shuffle=0)[1])
        corr_pct = 100 * (np.mean(hs) - hcond) / h1
    return h1, hcond, raw_pct, corr_pct, len(set(words))


# ---------- corpus builders ----------
def vms_lines(tokenization="eva", n=N):
    recs = corpora.voynich_lines()
    lines, total = [], 0
    for r in recs:
        ws = r["words"]
        if tokenization == "glyph":
            ws = [corpora.to_glyphs(w, corpora.GLYPHS) for w in ws]
        if n and total + len(ws) > n:
            ws = ws[: n - total]
        if len(ws) >= 2:
            lines.append(ws); total += len(ws)
        if n and total >= n:
            break
    return lines


def rechunk(words, lens):
    out, i = [], 0
    for L in lens:
        out.append(words[i:i + L]); i += L
    return out


def markov_pseudo(lines, seed=SEED):
    """IID pseudo-words from a within-word char-bigram model (start ^, end $)."""
    rng = random.Random(seed)
    trans = defaultdict(Counter)
    words = [w for line in lines for w in line]
    for w in words:
        prev = "^"
        for ch in w + "$":
            trans[prev][ch] += 1; prev = ch

    def gen():
        out, prev = [], "^"
        while True:
            c = trans[prev]
            ch = rng.choices(list(c), weights=list(c.values()))[0]
            if ch == "$" or len(out) > 20:
                if out:
                    return "".join(out)
                prev = "^"; continue
            out.append(ch); prev = ch

    return [[gen() for _ in line] for line in lines]


# ---------- main ----------
def analyse(name, lines, n_shuffle=3, perm=True):
    words = [w for line in lines for w in line]
    cp, wp = cross_pairs(lines), within_pairs(lines)
    a, b = mi_plugin(cp), mi_plugin(wp)
    pm, ps = mi_perm_null(cp) if perm else (float("nan"), float("nan"))
    h1, hcond, raw, corr, types = word_gain(lines, n_shuffle=n_shuffle)
    emit(f"{name:26} tok={len(words):6d} types={types:6d} | "
         f"CROSS MI={a['mi']:.4f} MM={a['mi_mm']:.4f} permNull={pm:.4f}+/-{ps:.4f} "
         f"(npairs={a['n']}, Hlast={a['hx']:.3f} Hfirst={a['hy']:.3f}) | "
         f"WITHIN MI={b['mi']:.4f} MM={b['mi_mm']:.4f} (npairs={b['n']}) | "
         f"cross/within={a['mi_mm'] / b['mi_mm'] if b['mi_mm'] else float('nan'):.3f} | "
         f"Hword={h1:.3f} Hcond={hcond:.3f} gain_raw={raw:.2f}% gain_shufcorr={corr:.2f}%")
    return a


def top_contributors(a, k=8):
    n = a["n"]
    contrib = []
    for (x, y), c in a["cxy"].items():
        pxy, px, py = c / n, a["cx"][x] / n, a["cy"][y] / n
        contrib.append((pxy * math.log2(pxy / (px * py)), x, y, c, pxy / (px * py)))
    contrib.sort(reverse=True)
    return contrib[:k]


def main():
    emit(f"D1 EDGE COUPLING  common N={N} tokens/corpus (VMS-full also shown), seed={SEED}")
    emit("MI in bits. MM=Miller-Madow corrected. gain = bigram entropy reduction / unigram H.")
    emit("-" * 100)

    v_eva = vms_lines("eva")
    v_gly = vms_lines("glyph")
    r_eva = analyse("VMS EVA chars", v_eva)
    r_gly = analyse("VMS glyphs (ch/sh=1)", v_gly)
    analyse("Latin Caesar", [corpora.control("latin_caesar", n_tokens=N)])
    analyse("Italian Dante", [corpora.control("italian_dante", n_tokens=N)])
    analyse("VMS EVA full (all lines)", vms_lines("eva", n=None))

    emit("-" * 100)
    lens = [len(l) for l in v_eva]
    flat = [w for l in v_eva for w in l]
    rng = random.Random(SEED); sh = flat[:]; rng.shuffle(sh)
    analyse("NULL VMS shuffled words", rechunk(sh, lens), n_shuffle=1)
    vocab, weights = zip(*Counter(flat).items())
    iid = rng.choices(vocab, weights=weights, k=len(flat))
    analyse("NULL VMS iid unigram", rechunk(iid, lens), n_shuffle=1)
    analyse("NULL VMS char-bigram pseudo", markov_pseudo(v_eva), n_shuffle=1)

    emit("-" * 100)
    inv = {v: k for k, v in corpora.SYMS.items()}  # glyph symbol -> EVA name (ASCII-safe)
    for label, r in [("VMS EVA", r_eva), ("VMS glyph", r_gly)]:
        tops = ", ".join(f"{inv.get(x, x)!r}->{inv.get(y, y)!r} c={c} obs/exp={r_:.2f} (+{v:.4f}b)"
                         for v, x, y, c, r_ in top_contributors(r))
        emit(f"Top cross-space MI contributors {label}: {tops}")

    emit("-" * 100)
    emit("Reading: compare CROSS MM vs its permNull and vs the three NULL rows (bias floor);")
    emit("compare gain_shufcorr across corpora (raw gain is inflated by sparse bigrams).")
    with open("results_d1.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(LINES_OUT) + "\n")


if __name__ == "__main__":
    main()
