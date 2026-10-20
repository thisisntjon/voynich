"""D2 slot bake-off: held-out (page-split) bits/token, 4 word models.
(i) word unigram (ii) char-trigram (iii) induced 3-slot indep (iv) slot prefix->core.
Train/test split is BY PAGE (paragraph units only), seed 42, 80/20.
All models scored as P(word) on test tokens -> bits/token = -mean log2 P.
"""
import math, random
from collections import Counter, defaultdict
import vparse

SEED = 42
ALPHA = 0.1          # add-alpha smoothing (unigram, char ctx, prefix, suffix)
MIN_AFFIX = 20       # min train-token count for prefix/suffix inventory
MAX_AFF = 3

recs = vparse.paragraph_text(vparse.load())
bypage = defaultdict(list)
for r in recs:
    bypage[r["page"]].extend(w for w in r["words"] if "?" not in w)
pages = sorted(p for p, ws in bypage.items() if ws)
rng = random.Random(SEED); rng.shuffle(pages)
n_tr = int(round(0.8 * len(pages)))
tr_pages, te_pages = pages[:n_tr], pages[n_tr:]
train = [w for p in tr_pages for w in bypage[p]]
test = [w for p in te_pages for w in bypage[p]]
tr_types, te_types = set(train), set(test)
print(f"pages total={len(pages)} train={len(tr_pages)} test={len(te_pages)}")
print(f"train tokens={len(train)} types={len(tr_types)} | test tokens={len(test)} types={len(te_types)}")
unseen_tok = sum(1 for w in test if w not in tr_types)
print(f"test unseen-Type tokens={unseen_tok} ({100*unseen_tok/len(test):.1f}%) "
      f"unseen types={len(te_types-tr_types)}/{len(te_types)} ({100*len(te_types-tr_types)/len(te_types):.1f}%)")

def bits(probs_words):
    return -sum(math.log2(p) for p in probs_words) / len(probs_words)

# ---------- (i) word unigram: add-alpha over train types + 1 UNK bucket ----------
wc = Counter(train); N = len(train); V = len(wc)
den_u = N + ALPHA * (V + 1)
def p_unigram(w): return (wc.get(w, 0) + ALPHA) / den_u

# ---------- (ii) char trigram: ^^w$ , P(c|prev2), add-alpha per ctx ----------
alphabet = sorted(set("".join(train))) + ["$"]
A = len(alphabet); aset = set(alphabet) - {"$"}
ctx_c, ctx_tot = defaultdict(Counter), Counter()
for w in train:
    s = "^^" + w + "$"
    for i in range(2, len(s)):
        ctx_c[s[i-2:i]][s[i]] += 1; ctx_tot[s[i-2:i]] += 1
def p_char_str(w, end=True):
    s = "^^" + w + ("$" if end else ""); lp = 0.0
    for i in range(2, len(s)):
        ctx, c = s[i-2:i], s[i]
        lp += math.log2((ctx_c[ctx].get(c, 0) + ALPHA) / (ctx_tot[ctx] + ALPHA * A))
    return 2 ** lp
def p_trigram(w): return p_char_str(w, end=True)

# ---------- (iii) induced 3-slot ----------
pref_cnt, suff_cnt = Counter(), Counter()
for w in train:
    for k in range(1, MAX_AFF + 1):
        if len(w) > k: pref_cnt[w[:k]] += 1; suff_cnt[w[-k:]] += 1
PREF = {p for p, c in pref_cnt.items() if c >= MIN_AFFIX} | {""}
SUFF = {s for s, c in suff_cnt.items() if c >= MIN_AFFIX} | {""}
print(f"affix inventory (count>={MIN_AFFIX}): prefixes={len(PREF)-1} suffixes={len(SUFF)-1}")

def parses(w):
    out = []
    for pl in range(0, MAX_AFF + 1):
        p = w[:pl]
        if p not in PREF: continue
        for sl in range(0, MAX_AFF + 1):
            if pl + sl >= len(w): continue          # core length >= 1
            s = w[len(w)-sl:] if sl else ""
            if s not in SUFF: continue
            out.append((p, w[pl:len(w)-sl if sl else len(w)], s))
    return out or [("", w, "")]

def longest_seg(w):  # initial hard segmentation: longest pref, then longest suff
    cands = parses(w)
    return max(cands, key=lambda t: (len(t[0]), len(t[2])))

def fit_slots(segfn):
    pc, sc, cc = Counter(), Counter(), Counter()
    joint = defaultdict(Counter)   # prefix -> core, for model (iv)
    for w in train:
        p, c, s = segfn(w); pc[p] += 1; sc[s] += 1; cc[c] += 1; joint[p][c] += 1
    return pc, sc, cc, joint

pc, sc, cc, joint = fit_slots(longest_seg)
# one MAP re-segmentation pass (hard EM iteration)
def slot_probs(pc, sc, cc):
    dp = N + ALPHA * len(PREF); ds = N + ALPHA * len(SUFF)
    n1 = sum(1 for c in cc.values() if c == 1); p_unk = min(0.5, n1 / N)  # Good-Turing reserve
    Pp = lambda p: (pc.get(p, 0) + ALPHA) / dp
    Ps = lambda s: (sc.get(s, 0) + ALPHA) / ds
    def Pcore(c):
        return (1 - p_unk) * cc[c] / N if c in cc else p_unk * p_char_str(c, end=True)
    return Pp, Ps, Pcore, p_unk
Pp, Ps, Pcore, p_unk = slot_probs(pc, sc, cc)
def map_seg(w): return max(parses(w), key=lambda t: Pp(t[0]) * Pcore(t[1]) * Ps(t[2]))
pc, sc, cc, joint = fit_slots(map_seg)
Pp, Ps, Pcore, p_unk = slot_probs(pc, sc, cc)
print(f"slot model: distinct cores(train,MAP seg)={len(cc)} core hapax-reserve p_unk={p_unk:.3f}")
print(f"top prefixes={pc.most_common(6)} top suffixes={sc.most_common(6)} top cores={cc.most_common(6)}")

def p_slot(w):   # sum over parses (generative marginal)
    return sum(Pp(p) * Pcore(c) * Ps(s) for p, c, s in parses(w))

# ---------- (iv) prefix -> core dependence, backoff to marginal core ----------
K_BACK = 10.0
Np = {p: sum(joint[p].values()) for p in joint}
def Pcore_given_pref(c, p):
    n = Np.get(p, 0)
    if n == 0: return Pcore(c)
    lam = n / (n + K_BACK)
    return lam * (joint[p].get(c, 0) / n) + (1 - lam) * Pcore(c)
def p_slot_dep(w):
    return sum(Pp(p) * Pcore_given_pref(c, p) * Ps(s) for p, c, s in parses(w))

# ---------- score ----------
models = [("(i) word-unigram", p_unigram), ("(ii) char-trigram", p_trigram),
          ("(iii) slot-indep", p_slot), ("(iv) slot pref->core", p_slot_dep)]
seen_idx = [i for i, w in enumerate(test) if w in tr_types]
unseen_idx = [i for i, w in enumerate(test) if w not in tr_types]
results = {}
print(f"\n{'model':<22} {'bits/tok ALL':>12} {'seen-type':>10} {'UNSEEN-type':>12} {'ppl':>9}")
for name, fn in models:
    ps = [max(fn(w), 1e-300) for w in test]
    b_all = bits(ps); b_seen = bits([ps[i] for i in seen_idx]); b_un = bits([ps[i] for i in unseen_idx])
    results[name] = (b_all, b_seen, b_un)
    print(f"{name:<22} {b_all:12.3f} {b_seen:10.3f} {b_un:12.3f} {2**b_all:9.1f}")
best = min(results, key=lambda k: results[k][0])
print(f"\nWINNER (all test tokens): {best} at {results[best][0]:.3f} bits/tok")
for name in results:
    if name != best: print(f"  beats {name} by {results[name][0]-results[best][0]:.3f} bits/tok")
bu = min(results, key=lambda k: results[k][2])
print(f"WINNER on UNSEEN types only: {bu} at {results[bu][2]:.3f} bits/tok "
      f"(slot-indep {results['(iii) slot-indep'][2]:.3f} vs trigram {results['(ii) char-trigram'][2]:.3f}: "
      f"diff {results['(iii) slot-indep'][2]-results['(ii) char-trigram'][2]:+.3f})")

# ---------- coverage ----------
def segmentable(w):  # some parse whose core was seen in train (MAP cores)
    return any(c in cc for _, c, _ in parses(w))
seg_tok = sum(1 for w in test if segmentable(w))
seg_typ = sum(1 for w in te_types if segmentable(w))
core_unseen_tok = sum(1 for w in test if map_seg(w)[1] not in cc)
novel_char_tok = sum(1 for w in test if any(ch not in aset for ch in w))
# trigram: fraction of test char-predictions whose context never seen in train
tot_pred = unctx = 0
for w in test:
    s = "^^" + w + "$"
    for i in range(2, len(s)):
        tot_pred += 1; unctx += (s[i-2:i] not in ctx_tot)
print(f"\nCOVERAGE: test tokens segmentable(core seen)={seg_tok}/{len(test)} ({100*seg_tok/len(test):.1f}%) "
      f"types={seg_typ}/{len(te_types)} ({100*seg_typ/len(te_types):.1f}%)")
print(f"unigram UNK tokens={unseen_tok} ({100*unseen_tok/len(test):.1f}%); slot MAP-core-unseen tokens="
      f"{core_unseen_tok} ({100*core_unseen_tok/len(test):.1f}%); trigram novel-char tokens={novel_char_tok}, "
      f"unseen-context predictions={unctx}/{tot_pred} ({100*unctx/tot_pred:.2f}%)")
# train bits for overfit contrast (subsample-free, same scorers)
print("\nTRAIN bits/tok (overfit contrast):")
for name, fn in models:
    print(f"  {name:<22} {bits([max(fn(w),1e-300) for w in train]):8.3f}")
