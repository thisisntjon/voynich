"""B2: do a 2-state HMM and Sukhotin's algorithm find vowels in Voynich?

Claim under test (user document, section "Deconstructing the Script Architecture"):
  * a 2-state character HMM splits natural alphabets into vowels/consonants but
    splits Voynich into word-final (m n g v y) vs other glyphs;
  * Sukhotin's algorithm is unstable on Voynich: with spaces it calls a e o y
    vowels (74% alternation); without spaces a g c n o y.
Literature: Reddy & Knight 2011 (HMM word-final split); Zandbergen (voynich.nu
a2_char) reports the R&K result depends on initial conditions. So we also
measure restart stability.

Controls: six natural-language texts. Null: Voynich with characters shuffled
across the whole text (word-length profile kept, all sequence structure gone).
Each corpus: 25k tokens, two variants: spaces kept as symbol '_' / spaces removed.
Run: python b2_hmm_sukhotin.py   -> results_b2.txt
"""
import random
from collections import Counter
from pathlib import Path

import numpy as np

import corpora

OUT = Path(__file__).parent / "results_b2.txt"
N_TOK = 25000
SEG = 120          # chars per training segment (batched forward-backward)
N_SEG = 350        # ~42k chars used for HMM training
RESTARTS = 20
ITERS = 120
VOWELS = set("aeiouy")   # control truth (y counted as vowel; German/English/Latin)
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def glyph_label(c):
    inv = {v: k for k, v in corpora.SYMS.items()}
    return inv.get(c, c)


# ---------------------------------------------------------------- HMM
def baum_welch(segs, V, seed):
    rng = np.random.default_rng(seed)
    A = rng.dirichlet([5, 5], size=2)
    B = rng.dirichlet(np.ones(V), size=2)
    pi = np.array([0.5, 0.5])
    X = segs  # (N, T) int
    N, T = X.shape
    prev_ll = -np.inf
    for it in range(ITERS):
        al = np.zeros((N, T, 2)); c = np.zeros((N, T))
        a = pi * B[:, X[:, 0]].T
        c[:, 0] = a.sum(1); al[:, 0] = a / c[:, 0:1]
        for t in range(1, T):
            a = (al[:, t - 1] @ A) * B[:, X[:, t]].T
            c[:, t] = a.sum(1); al[:, t] = a / c[:, t:t + 1]
        be = np.ones((N, T, 2))
        for t in range(T - 2, -1, -1):
            b = (B[:, X[:, t + 1]].T * be[:, t + 1]) @ A.T
            be[:, t] = b / c[:, t + 1:t + 2]
        g = al * be
        g /= g.sum(2, keepdims=True)
        xi = np.zeros((2, 2))
        for t in range(T - 1):
            m = al[:, t, :, None] * A[None] * (B[:, X[:, t + 1]].T * be[:, t + 1])[:, None, :]
            m /= m.sum((1, 2), keepdims=True)
            xi += m.sum(0)
        A = xi / xi.sum(1, keepdims=True)
        pi = g[:, 0].mean(0)
        B = np.full((2, V), 1e-6)
        for s in range(2):
            np.add.at(B[s], X.ravel(), g[:, :, s].ravel())
        B /= B.sum(1, keepdims=True)
        ll = np.log(c).sum()
        if ll - prev_ll < 0.01:
            break
        prev_ll = ll
    return ll, A, B


def hmm_partition(text, sym_list, seed0):
    idx = {s: i for i, s in enumerate(sym_list)}
    arr = np.array([idx[ch] for ch in text[:SEG * N_SEG]])
    segs = arr[: (len(arr) // SEG) * SEG].reshape(-1, SEG)
    runs = []
    for r in range(RESTARTS):
        ll, A, B = baum_welch(segs, len(sym_list), seed0 + r)
        # assign each symbol to the state with higher posterior P(state|sym)
        stat = np.linalg.matrix_power(A, 200)[0]
        post = (B * stat[:, None])
        part = frozenset(s for s in sym_list if post[0, idx[s]] > post[1, idx[s]])
        runs.append((ll, part, frozenset(sym_list) - part))
    runs.sort(key=lambda x: -x[0])
    best = runs[0]
    canon = lambda p, q: frozenset([p, q])
    agree = sum(canon(r[1], r[2]) == canon(best[1], best[2]) for r in runs)
    return best, agree


def final_rate(words):
    tot, fin = Counter(), Counter()
    for w in words:
        for i, ch in enumerate(w):
            tot[ch] += 1
            if i == len(w) - 1:
                fin[ch] += 1
    return {c: fin[c] / tot[c] for c in tot}, tot


def auc(scores_pos, scores_neg):
    if not scores_pos or not scores_neg:
        return float("nan")
    wins = sum((p > n) + 0.5 * (p == n) for p in scores_pos for n in scores_neg)
    return wins / (len(scores_pos) * len(scores_neg))


def score_partition(part_a, part_b, words, is_control):
    """How well does the HMM split match (i) vowel/consonant, (ii) word-final rate?"""
    fr, tot = final_rate(words)
    out = {}
    letters = [c for c in tot if c != "_"]
    # orient: call 'X' the side with higher mean final-rate
    def mfr(p):
        v = [fr[c] for c in p if c in fr]
        return np.mean(v) if v else 0
    X, Y = (part_a, part_b) if mfr(part_a) >= mfr(part_b) else (part_b, part_a)
    out["AUC_final"] = auc([fr[c] for c in X if c in fr], [fr[c] for c in Y if c in fr])
    # token-weighted share of word-final occurrences that fall on side X
    fin_tok = sum(fr[c] * tot[c] for c in X if c in fr)
    out["final_tokens_on_X"] = fin_tok / sum(fr[c] * tot[c] for c in letters)
    if is_control:
        w = lambda p: sum(tot[c] for c in p if c in tot)
        acc1 = (sum(tot[c] for c in letters if (c in VOWELS) == (c in X))) / w(letters)
        out["vowel_acc"] = max(acc1, 1 - acc1)
    return X, Y, out


# ---------------------------------------------------------------- Sukhotin
def sukhotin(words, with_spaces):
    seqs = words if with_spaces else ["".join(words)]
    F = Counter()
    alph = set()
    for s in seqs:
        alph.update(s)
        for a, b in zip(s, s[1:]):
            if a != b:
                F[(a, b)] += 1; F[(b, a)] += 1
    alph = sorted(alph)
    r = {c: sum(F[(c, d)] for d in alph) for c in alph}
    vow = []
    cons = set(alph)
    while True:
        cand = [c for c in cons if r[c] > 0]
        if not cand:
            break
        v = max(cand, key=lambda c: r[c])
        vow.append(v); cons.discard(v)
        for c in cons:
            r[c] -= 2 * F[(c, v)]
    V = set(vow)
    alt = n = 0
    for w in words:  # alternation measured within words in both cases
        for a, b in zip(w, w[1:]):
            n += 1
            alt += (a in V) != (b in V)
    return vow, alt / max(n, 1)


# ---------------------------------------------------------------- corpora
def corpora_list():
    out = []
    for tok in ("eva", "glyph"):
        out.append((f"voynich_{tok}", corpora.voynich(tokenization=tok)[:N_TOK], False))
    v = corpora.voynich()[:N_TOK]
    rng = random.Random(1)
    chars = list("".join(v)); rng.shuffle(chars)
    shuf, i = [], 0
    for w in v:
        shuf.append("".join(chars[i:i + len(w)])); i += len(w)
    out.append(("NULL_voy_charshuf", shuf, False))
    for name in corpora.CONTROLS:
        out.append((name, corpora.control(name, N_TOK), True))
    return out


def main():
    emit("B2: 2-state HMM and Sukhotin vowel identification")
    emit(f"tokens/corpus={N_TOK}, HMM train chars={SEG*N_SEG}, restarts={RESTARTS}")
    emit("HMM: 'X' = state whose glyphs have the higher word-final rate.")
    emit("AUC_final = P(final-rate of an X glyph > that of a Y glyph); 1.0 = perfect final/non-final split.")
    emit("vowel_acc = token-weighted agreement of the split with a,e,i,o,u,y (controls only; 0.5 = chance-ish).")
    emit("stable = restarts (of %d) landing on the same partition as the best one." % RESTARTS)
    emit()
    for name, words, is_ctrl in corpora_list():
        lab = (lambda c: glyph_label(c)) if name == "voynich_glyph" else (lambda c: c)
        for spaces in (True, False):
            text = "_".join(words) if spaces else "".join(words)
            syms = sorted(set(text))
            (ll, pa, pb), agree = hmm_partition(text, syms, 100)
            X, Y, sc = score_partition(pa - {"_"}, pb - {"_"}, words, is_ctrl)
            sp_side = "X" if ("_" in pa) == (X == pa - {"_"}) else "Y"
            fr, tot = final_rate(words)
            top = lambda S: " ".join(lab(c) for c in sorted(S, key=lambda c: -tot.get(c, 0))[:14])
            emit(f"[{name}] spaces={'kept' if spaces else 'removed'}  LL={ll:.0f}  stable={agree}/{RESTARTS}"
                 + ("  space-symbol-side=" + sp_side if spaces else ""))
            emit(f"   X (final-ish): {top(X)}")
            emit(f"   Y            : {top(Y)}")
            emit("   " + "  ".join(f"{k}={v:.3f}" for k, v in sc.items()))
        for spaces in (True, False):
            vow, alt = sukhotin(words, spaces)
            emit(f"   Sukhotin spaces={'kept' if spaces else 'removed'}: vowels={' '.join(lab(c) for c in vow)}  "
                 f"within-word alternation={alt:.3f}")
        emit()
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
