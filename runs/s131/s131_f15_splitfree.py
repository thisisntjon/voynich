"""s131: F-15 restated without a word split (X-01 track; Jon brief 11:17: run only findings with no published
split-free number; workflow/research/x01-published-first.md, L-370).

F-15 (slot split): affixes depend on the core; free assembly of prefix x core x suffix makes ~65% too many types.
Split-free restatement on raw characters (no SlotSegmenter, no glyph tokenizer): for each word of length n >= 5,
B = first 2 characters, E = last 2 characters, M = the middle (n-4 >= 1 characters).
  S1 dependence: excess MI(B;E | n), MI(B;M | n), MI(M;E | n) over a within-length shuffle null (200 perms):
     the second part is permuted among words of the same length, which keeps every marginal and length.
  S2 free assembly: types made by drawing B, M, E independently from their within-length token distributions
     (same token count, 20 draws) divided by observed types.
CALL per transliteration:
  RESTATED      all three S1 p <= 0.01 and S2 ratio >= 1.30
  PARTIAL       all three S1 p <= 0.01, S2 ratio < 1.30
  NOT_RESTATED  otherwise
Overall: RESTATED only if all of ZL3b, RF1b and IT2a are RESTATED.
References (Latin Caesar, Italian Dante, German Faust; letters only, lowercased) are reported for context, not gated.
Fixture (planted, before real data): FREE (B, M, E drawn independently per length from ZL3b marginals) must be
NOT_RESTATED; LEXICON (Zipf draws from a fixed 2,000-type vocabulary built by free assembly) must be RESTATED.
Modes: fixture | run
"""
import os, re, sqlite3, sys
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
VKB = os.path.join(ROOT, "data", "vkb", "vkb.sqlite")
REFS = {"latin_caesar": "latin_caesar.txt", "italian_dante": "italian_dante.txt", "german_faust": "german_faust.txt"}
SEED, NPERM, NDRAW, MINLEN = 131, 200, 20, 5
P_GATE, RATIO_GATE = 0.01, 1.30


def voynich_words(translit):
    c = sqlite3.connect(f"file:{VKB}?mode=ro", uri=True)
    return [w for (w,) in c.execute("select word from tokens where translit=? order by rowid", (translit,))
            if w and re.fullmatch(r"[a-z]+", w)]


def ref_words(fname):
    t = open(os.path.join(ROOT, "data", "controls", fname), encoding="utf-8", errors="replace").read().lower()
    return re.findall(r"[a-z]+", t)


def parts(words):
    ws = [w for w in words if len(w) >= MINLEN]
    return ws, [w[:2] for w in ws], [w[2:-2] for w in ws], [w[-2:] for w in ws], np.array([len(w) for w in ws])


def codes(xs):
    u = {}
    return np.array([u.setdefault(x, len(u)) for x in xs], dtype=np.int64)


def mi(a, b):
    n = len(a)
    j = a * (b.max() + 1) + b
    pj = np.bincount(j) / n
    pa = np.bincount(a) / n
    pb = np.bincount(b) / n
    nz = np.nonzero(pj)[0]
    return float((pj[nz] * np.log2(pj[nz] / (pa[nz // (b.max() + 1)] * pb[nz % (b.max() + 1)]))).sum())


def cond_mi(a, b, L):
    tot = 0.0
    n = len(a)
    for l in np.unique(L):
        k = L == l
        if k.sum() > 1:
            tot += k.sum() / n * mi(codes(a[k]), codes(b[k]))
    return tot


def shuffle_within(b, L, rng):
    out = b.copy()
    for l in np.unique(L):
        idx = np.nonzero(L == l)[0]
        out[idx] = b[rng.permutation(idx)]
    return out


def s1(a, b, L, rng):
    obs = cond_mi(a, b, L)
    null = np.array([cond_mi(a, shuffle_within(b, L, rng), L) for _ in range(NPERM)])
    p = (1 + (null >= obs).sum()) / (NPERM + 1)
    return obs - null.mean(), float(np.quantile(null, 0.99)) - null.mean(), p


def s2(B, M, E, L, rng):
    obs = len(set(zip(B, M, E)))
    by = defaultdict(list)
    for i, l in enumerate(L):
        by[l].append(i)
    ratios = []
    for _ in range(NDRAW):
        made = set()
        for l, idx in by.items():
            idx = np.array(idx)
            b = B[rng.choice(idx, len(idx))]
            m = M[rng.choice(idx, len(idx))]
            e = E[rng.choice(idx, len(idx))]
            made.update(zip(b, m, e))
        ratios.append(len(made) / obs)
    return float(np.mean(ratios))


def analyse(name, words, rng, gate=True):
    ws, B, M, E, L = parts(words)
    B, M, E = np.array(B, dtype=object), np.array(M, dtype=object), np.array(E, dtype=object)
    res = {}
    for lab, (x, y) in {"B;E": (B, E), "B;M": (B, M), "M;E": (M, E)}.items():
        res[lab] = s1(codes(x), codes(y), L, rng)
    ratio = s2(B, M, E, L, rng)
    allp = all(v[2] <= P_GATE for v in res.values())
    call = "RESTATED" if allp and ratio >= RATIO_GATE else "PARTIAL" if allp else "NOT_RESTATED"
    s = "  ".join(f"{k} excess {v[0]:.4f} bits (null q99 +{v[1]:.4f}) p {v[2]:.4f}" for k, v in res.items())
    print(f"{name}: words>={MINLEN} {len(ws)}, types {len(set(ws))}  {s}  free-assembly type ratio {ratio:.3f}"
          + (f"  CALL={call}" if gate else "  (context, not gated)"), flush=True)
    return call


def planted(rng):
    ws, B, M, E, L = parts(voynich_words("ZL3b"))
    B, M, E = np.array(B, dtype=object), np.array(M, dtype=object), np.array(E, dtype=object)
    by = defaultdict(list)
    for i, l in enumerate(L):
        by[l].append(i)
    free = []
    for l, idx in by.items():
        idx = np.array(idx)
        free += [b + m + e for b, m, e in zip(B[rng.choice(idx, len(idx))], M[rng.choice(idx, len(idx))], E[rng.choice(idx, len(idx))])]
    vocab = list(dict.fromkeys(free))[:2000]
    z = 1 / np.arange(1, len(vocab) + 1)
    lex = list(rng.choice(np.array(vocab, dtype=object), size=len(free), p=z / z.sum()))
    return free, lex


def fixture():
    rng = np.random.default_rng(SEED)
    free, lex = planted(rng)
    a = analyse("FIXTURE_FREE (must be NOT_RESTATED)", free, rng)
    b = analyse("FIXTURE_LEXICON (must be RESTATED)", lex, rng)
    print("CONTROL_PASS" if a == "NOT_RESTATED" and b == "RESTATED" else "CONTROL_FAIL")


def run():
    rng = np.random.default_rng(SEED)
    calls = [analyse(t, voynich_words(t), rng) for t in ("ZL3b", "RF1b", "IT2a")]
    for k, f in REFS.items():
        analyse(k, ref_words(f), rng, gate=False)
    print("OVERALL_CALL=" + ("RESTATED" if all(c == "RESTATED" for c in calls) else
                             "PARTIAL" if all(c in ("RESTATED", "PARTIAL") for c in calls) else "NOT_RESTATED"))


if __name__ == "__main__":
    fixture() if sys.argv[1] == "fixture" else run()
