"""s122 -- s117's within-line co-occurrence test with a near-copy control, a within-page null and a tuple list.
Design: DECISIONS.md D-066 (bb) (Jon approved 's122: settle T vs near-copy (Recommended)'); follows L-345.
Copied from tools/s117_line_cooccurrence.py (s117, stub-frozen, never edited, D-071). s117's statistics (S, N_T, Q),
nulls, constants and decision thresholds are unchanged; everything below the '--- s122 additions' heading is new.

Question (as s117): inside a line, do particular unit pairs co-occur more than the quire's own pool predicts? If so,
is the excess a TABLE (T: a small set of recurring tuples reused across quires), CONTENT (C: graded clusters,
quire-local) or none (P: plain pool)? s122 asks in addition whether a T call can be told apart from NEAR-COPY
(lines holding spelling variants of each other, F-13/F-40), and whether T survives a within-page null.

Reading-order agnostic in the test itself: a line is used only as a SET of units. The only order-dependent quantity
is the near-copy calibration statistic (adjacent-word edit distance, F-13), which only sets a fixture parameter.

Modes (run from the project root, python -I tools/s122_cooccurrence_nearcopy.py ...):
  --fixture   (1) estimates the real F-13 near-copy rate and calibrates the near-copy producer (printed first, before
              any fixture book is scored); (2) four planted books (table / content / pool / nearcopy) x 10 seeds on
              the real ZL3b line and quire layout, representations core, word, tri. Writes
              runs/s122/fixture_<YYYYmmdd_HHMMSS>.txt. No co-occurrence statistic of the real text is computed.
  --run       real data, ZL3b primary, RF1b and IT2a replication, both nulls, plus the top-50 tuple list. Refuses to
              run unless the stub s122_cooccurrence_nearcopy.prereg.sha256 verifies and the fixture gate passed.
              Writes results_s122_<YYYYmmdd_HHMMSS>.txt (never overwrites).

Kept from s117 unchanged (see s117's docstring for full text): data (P* lines, '?'/'*' tokens dropped, quire = page
'quire' field), representations core/word/tri, line = set of distinct units, curveball null with Besag-Clifford hub
(TRADES 5, R_E 100, R_H 100), statistics S, N_T (LIFT 3, MIN_OUTSIDE 3, leave-top-quire-out), Q (Louvain), and
constants ALPHA 0.01, NT_MIN 10, NT_RATIO 2. s117 rule per null: P if p_S > ALPHA; T if p_S <= ALPHA and
N_T > q99_H(N_T) and N_T >= NT_MIN and N_T >= NT_RATIO x q99_H(N_T); C if excess, not T, and p_Q <= ALPHA; else X.

s122 additions (D-066 bb), frozen before any fixture book was scored:
  (2) Within-page null: the same curveball, strata = page instead of quire (N_T's outside-top-quire test still uses
      quires, as in s117's diagnostic). Run for every cell alongside the quire null.
      Cell CALL (both nulls): T if the s117 rule gives T under the quire null AND under the page null; otherwise
      the s117 rule without T under the quire null: P if p_S(quire) > ALPHA; C if p_Q(quire) <= ALPHA; else X.
      (Q is therefore computed under the quire null whenever there is excess, including T cells; under s117 it
      was skipped for T cells. This adds a number and changes no s117 statistic.)
      Transliteration call = the CALL shared by >= 2 of 3 representations, else MIXED. Overall CALL = ZL3b's
      transliteration call if RF1b and IT2a agree, else NOT_REPLICATED (ZL3b call printed). Per-null calls are
      printed beside the CALL.
  (1) Near-copy producer (fourth planted book): each line of k tokens is generated token by token in the line's
      quire q. Token 1 is a seed drawn from the quire pool. Each later token is, with probability P_COPY (0.15, as
      the pool producer) an exact copy of an earlier token; otherwise with probability P_NC an edit-distance-1/2
      variant of a uniformly chosen seed of this line; otherwise a new seed from the quire pool. A variant of seed
      s is drawn from the word types at Levenshtein distance 1 or 2 from s, weighted by their frequency in quire q;
      if none occur in q, by global frequency; if none exist, one glyph of s is substituted by a glyph drawn from
      the global glyph distribution. Variants are real words of the book, so variant pairs recur across quires.
      Calibration of P_NC (the F-13 near-copy rate): r_real = share of adjacent within-line word pairs of ZL3b
      (raw words, after dropping '?'/'*' tokens) at edit distance 1 or 2. For P_NC on the grid 0.00, 0.05, ...,
      0.95, two near-copy books (calibration seeds SEED+7001, SEED+7002, not fixture seeds) give r(P_NC) by the same
      statistic on the produced line order; P_NC = linear interpolation of the grid where r(P_NC) crosses r_real
      (0 if r(0) >= r_real; 0.95 if r(0.95) < r_real). Printed in the fixture file before any book is scored.
      Expected call for nearcopy: NOT T.
  (3) Descriptive top-50 tuple list per transliteration x representation (quire null, no call from it): among the
      real book's candidate tuples (>= 3 lines, >= 2 quires) that pass N_T's global test (count > null q99 and
      >= LIFT x null mean), ranked by line count (ties: lift), with null mean, lift, whether it also passes the
      cross-quire test (counted in N_T), its quires (lines per quire), and its pages.
  Fixture gate (per representation, both-null CALL): table T on >= 8/10 seeds; nearcopy NOT T on >= 8/10; content
    C and pool P on >= 8/10 (s117's bars). If table passes and nearcopy fails in any representation:
    T_UNIDENTIFIABLE, stop (no stub, no real run). Any other failure: FIXTURE_GATE FAIL, stop.
  Fixture compute: table and nearcopy books under both nulls; content and pool under the quire null, and under the
    page null only for a seed whose quire-null call is T (the CALL needs the page null only then; identical result).
  Compute: 4 workers, BelowNormal; refuses to start with < 4 GB free RAM.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import sys, json, hashlib, subprocess, time, math, random, argparse
from collections import Counter, defaultdict
from itertools import combinations
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

RUNDIR = os.path.join(ROOT, "runs", "s122")
STUB = os.path.join(ROOT, "s122_cooccurrence_nearcopy.prereg.sha256")
TRANSLITS = [("ZL3b", "ZL3b_eva"), ("RF1b", "RF1b"), ("IT2a", "IT2a")]
REPS = ["core", "word", "tri"]
SEED = 20261018
R_E = 100
R_H = 100
TRADES = 5
ALPHA = 0.01
NT_MIN = 10
NT_RATIO = 2.0
MIN_LINES = 3
MIN_QUIRES = 2
MIN_OUTSIDE = 3      # lines outside the tuple's top quire
LIFT = 3.0           # observed / null-mean count, globally and outside the top quire
WORKERS = 4

# fixture producer parameters
P_COPY = 0.15          # in-line copy rate of the pool producer (gives F-40-like repeats; collapsed by the line set)
T_ROWS, T_WIDTH, T_PROB = 60, 3, 0.25      # table: 60 rows of 3 words, a row in 25% of lines with >= 4 tokens
T_RANKS = (30, 600)    # table words drawn from global frequency ranks 30..600
C_TOPICS, C_SIZE, C_ALPHA, C_LAMBDA = 4, 40, 0.5, 0.35   # content: 4 topics/quire, 40 words, Dirichlet 0.5, 35%
# s122: near-copy producer; P_NC is calibrated at fixture time (calibrate_nc) and passed to every job
P_NC = None
NC_GRID = [round(0.05 * i, 2) for i in range(20)]   # 0.00 .. 0.95
NC_CAL_SEEDS = (7001, 7002)
TOP_TUPLES = 50
MIN_FREE_GB = 4.0


def now():
    try:
        return subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S %Z"]).decode().strip()
    except Exception:
        return time.strftime("%Y-%m-%d %H:%M:%S")


def lower_priority():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 10)
        return "BelowNormal"
    except Exception as e:
        return f"priority not lowered: {e}"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ----------------------------------------------------------------------------------------------------- data
def load_book(fname):
    """-> dict(lines=[[word,...]], quire=[int], page=[int], quires=[names]) from a meta.json (P* lines)."""
    d = json.load(open(os.path.join(ROOT, "data", "translit", f"{fname}.meta.json"), encoding="utf-8"))
    lines, qn, pn = [], [], []
    for p in d["pages"]:
        for l in p["lines"]:
            ws = [w for w in l if w and "?" not in w and "*" not in w]
            if ws:
                lines.append(ws); qn.append(str(p.get("quire"))); pn.append(str(p["id"]))
    quires = sorted(set(qn))
    pages = sorted(set(pn))
    return dict(lines=lines, quire=np.array([quires.index(q) for q in qn]),
                page=np.array([pages.index(x) for x in pn]), quires=quires, pages=pages)


def build_rep(lines, rep, want_names=False):
    """-> (unit line sets as list of sorted int arrays, kept line index, n_units, tri feature table or None)."""
    if rep == "core":
        seg = SlotSegmenter([w for l in lines for w in l])
        lu = [[seg.segment(w)[1] for w in l] for l in lines]
        lu = [[u for u in l if u] for l in lu]
    else:
        lu = lines
    vocab = {}
    sets, keep = [], []
    for i, l in enumerate(lu):
        s = sorted({vocab.setdefault(u, len(vocab)) for u in l})
        if s:
            sets.append(s); keep.append(i)
    tri = None
    names = [None] * len(vocab)
    for u, k in vocab.items():
        names[k] = u
    gnames = None
    if rep == "tri":
        inv = [None] * len(vocab)
        for u, k in vocab.items():
            inv[k] = u
        gv = {}
        tri = []
        for u in inv:
            s = "#" + u + "#"
            tri.append(np.array(sorted({gv.setdefault(s[i:i + 3], len(gv)) for i in range(len(s) - 2)}), np.int64))
        tri = (tri, len(gv))
        gnames = [None] * len(gv)
        for g_, k in gv.items():
            gnames[k] = g_
    if want_names:
        return sets, np.array(keep), len(vocab), tri, (names, gnames)
    return sets, np.array(keep), len(vocab), tri


# ------------------------------------------------------------------------------------------------ the null
def curveball(sets, strata_idx, rng, trades=TRADES):
    """sets: list of sorted lists; strata_idx: list of index arrays. Returns a new list of lists."""
    out = [list(s) for s in sets]
    for idx in strata_idx:
        n = len(idx)
        if n < 2:
            continue
        for _ in range(trades * n):
            a, b = rng.sample(idx, 2)
            A, B = out[a], out[b]
            sA = set(A); sB = set(B)
            onlyA = sA - sB; onlyB = sB - sA
            if not onlyA or not onlyB:
                continue
            pool = list(onlyA | onlyB)
            rng.shuffle(pool)
            k = len(onlyA)
            sh = sA & sB
            out[a] = list(sh) + pool[:k]
            out[b] = list(sh) + pool[k:]
    return out


# ------------------------------------------------------------------------------------------------ counting
_TRI_CACHE = {}


def _tri_idx(k):
    r = _TRI_CACHE.get(k)
    if r is None:
        c = np.array(list(combinations(range(k), 3)), np.int64).reshape(-1, 3)
        r = _TRI_CACHE[k] = c
    return r


def count_book(sets, quire, V, tri, NQ, do_triples=True):
    """-> dict kind -> (codes, counts, nquires, qcodes, qcounts); kinds 'p' (pairs) and 't' (triples).
    qcodes = code * NQ + quire (unique per (tuple, quire))."""
    by_k = defaultdict(list)
    for i, s in enumerate(sets):
        by_k[len(s)].append(i)
    out = {}
    if tri is None:
        pc, pq, tc, tq = [], [], [], []
        for k, ids in by_k.items():
            if k < 2:
                continue
            M = np.array([sorted(sets[i]) for i in ids], np.int64)
            qv = quire[ids]
            iu, ju = np.triu_indices(k, 1)
            c = (M[:, iu] * V + M[:, ju])
            pc.append(c.ravel()); pq.append(np.repeat(qv, c.shape[1]))
            if do_triples and k >= 3:
                T = _tri_idx(k)
                c3 = (M[:, T[:, 0]] * V + M[:, T[:, 1]]) * V + M[:, T[:, 2]]
                tc.append(c3.ravel()); tq.append(np.repeat(qv, c3.shape[1]))
        kinds = [("p", pc, pq)] + ([("t", tc, tq)] if do_triples else [])
    else:
        feats, G = tri
        pc, pq = [], []
        for li, s in enumerate(sets):
            if len(s) < 2:
                continue
            tg = np.concatenate([feats[u] for u in s])
            lab = np.concatenate([np.full(len(feats[u]), j) for j, u in enumerate(s)])
            iu, ju = np.triu_indices(len(tg), 1)
            m = (lab[iu] != lab[ju]) & (tg[iu] != tg[ju])
            a = tg[iu[m]]; b = tg[ju[m]]
            c = np.unique(np.minimum(a, b) * G + np.maximum(a, b))
            pc.append(c); pq.append(np.full(len(c), quire[li]))
        kinds = [("p", pc, pq)]
    for kind, cl, ql in kinds:
        if not cl:
            out[kind] = tuple(np.zeros(0, np.int64) for _ in range(5))
            continue
        c = np.concatenate(cl); q = np.concatenate(ql).astype(np.int64)
        qc, qn = np.unique(c * NQ + q, return_counts=True)
        codes, inv, cnt = np.unique(qc // NQ, return_inverse=True, return_counts=True)
        tot = np.bincount(inv, weights=qn).astype(np.int64)
        out[kind] = (codes, tot, cnt, qc, qn.astype(np.int64))
    return out


def lookup(keys, codes, vals, default=0):
    """vals at codes matching keys (codes sorted unique)."""
    if len(codes) == 0:
        return np.full(len(keys), default, vals.dtype if len(vals) else np.int64)
    pos = np.searchsorted(codes, keys)
    pos = np.clip(pos, 0, len(codes) - 1)
    hit = codes[pos] == keys
    r = np.where(hit, vals[pos], default)
    return r


class Acc:
    """Accumulates over the R_E null books: pair sums (for E) over the universe U, and for candidate tuples the
    global sum and running top-2 count, and per (tuple, quire) the sum of per-quire counts and the running top-2 of
    the count OUTSIDE that quire (total minus that quire's count)."""

    def __init__(self, U, cand, NQ):
        self.U = U
        self.sum = np.zeros(len(U))
        self.NQ = NQ
        self.cand = cand
        z = lambda n: np.zeros(n, np.int64)
        self.gsum = {k: z(len(v)) for k, v in cand.items()}
        self.g1 = {k: z(len(v)) for k, v in cand.items()}
        self.g2 = {k: z(len(v)) for k, v in cand.items()}
        self.qsum = {k: z(len(v) * NQ) for k, v in cand.items()}
        self.m1 = {k: z(len(v) * NQ) for k, v in cand.items()}
        self.m2 = {k: z(len(v) * NQ) for k, v in cand.items()}

    @staticmethod
    def _top2(m1, m2, x):
        return np.maximum(m1, x), np.maximum(m2, np.minimum(m1, x))

    def add(self, cnt):
        self.sum += lookup(self.U, cnt["p"][0], cnt["p"][1])
        NQ = self.NQ
        for k, cand in self.cand.items():
            if not len(cand):
                continue
            codes, tot, _, qc, qn = cnt[k]
            x = lookup(cand, codes, tot)
            self.gsum[k] += x
            self.g1[k], self.g2[k] = self._top2(self.g1[k], self.g2[k], x)
            xq = dense_q(cand, qc, qn, NQ)
            self.qsum[k] += xq
            minus = np.repeat(x, NQ) - xq
            self.m1[k], self.m2[k] = self._top2(self.m1[k], self.m2[k], minus)


def dense_q(cand, qc, qn, NQ):
    """per-(candidate, quire) counts as a dense flat array of len(cand) * NQ."""
    out = np.zeros(len(cand) * NQ, np.int64)
    if not len(cand) or not len(qc):
        return out
    t = qc // NQ
    ci = np.clip(np.searchsorted(cand, t), 0, len(cand) - 1)
    ok = cand[ci] == t
    out[ci[ok] * NQ + qc[ok] % NQ] = qn[ok]
    return out


def candidates(cnt, kind):
    codes, tot, nq = cnt[kind][0], cnt[kind][1], cnt[kind][2]
    return codes[(tot >= MIN_LINES) & (nq >= MIN_QUIRES)]


def score(cnt, acc, RE, want_graph):
    codes, tot = cnt["p"][0], cnt["p"][1]
    E = lookup(codes, acc.U, acc.sum, 0.0) / RE
    # Poisson-deviance form of the PMI excess (half deviance, smoothed): sum over the universe U of
    # n ln((n+.5)/(E+.5)) - (n - E); pairs absent from the book contribute E.
    S = float(np.sum(tot * np.log((tot + 0.5) / (E + 0.5)) - tot)) + float(acc.sum.sum()) / RE
    NT = 0
    per_kind = {}
    NQ = acc.NQ
    for k, cand in acc.cand.items():
        c = candidates(cnt, k)
        if not len(c):
            per_kind[k] = 0
            continue
        obs = lookup(c, cnt[k][0], cnt[k][1])
        ci = np.searchsorted(cand, c)
        Et = acc.gsum[k][ci] / RE
        glob = (obs > acc.g2[k][ci]) & (obs >= LIFT * Et)
        oq = dense_q(c, cnt[k][3], cnt[k][4], NQ).reshape(len(c), NQ)
        qstar = np.argmax(oq, axis=1)
        om = obs - oq[np.arange(len(c)), qstar]
        f = ci * NQ + qstar
        Em = Et - acc.qsum[k][f] / RE
        cross = (om >= MIN_OUTSIDE) & (om > acc.m2[k][f]) & (om >= LIFT * Em)
        n = int(np.sum(glob & cross))
        per_kind[k] = n
        NT += n
    G = None
    if want_graph:
        m = (tot >= 2) & (tot > E)
        G = (codes[m], (tot - E)[m])
    return S, NT, per_kind, G


def modularity(G, V):
    import networkx as nx
    codes, w = G
    if len(codes) == 0:
        return 0.0
    g = nx.Graph()
    a = codes // V; b = codes % V
    g.add_weighted_edges_from(zip(a.tolist(), b.tolist(), w.tolist()))
    comm = nx.community.louvain_communities(g, weight="weight", resolution=1, seed=SEED)
    return float(nx.community.modularity(g, comm, weight="weight"))


def analyze(book, rep, strata="quire", seed=SEED, RE=R_E, RH=R_H, do_Q=True, n_tuples=0):
    """Full s117 analysis of one book in one representation. Returns a dict of statistics and the call."""
    t0 = time.time()
    sets, keep, V, tri, nm = build_rep(book["lines"], rep, want_names=True)
    lab = (book["quire"] if strata == "quire" else book["page"])[keep]
    quire = book["quire"][keep].astype(np.int64)
    NQ = int(book["quire"].max()) + 1
    strata_idx = [list(np.nonzero(lab == s)[0]) for s in np.unique(lab)]
    Vc = tri[1] if tri else V
    do_t = tri is None
    rng_seeds = np.random.SeedSequence([seed, REPS.index(rep), 0 if strata == "quire" else 1]).generate_state(RE + RH + 1)

    # Besag-Clifford parallel method: one hub reached from the real book, every null book from the hub, so the
    # real book and all null books are exchangeable under the null (the curveball chain is reversible).
    hub = curveball(sets, strata_idx, random.Random(int(rng_seeds[RE + RH])))

    def null_book(i):
        return curveball(hub, strata_idx, random.Random(int(rng_seeds[i])))

    def counts_of(s):
        return count_book(s, quire, Vc, tri, NQ, do_t)

    # pass A: real + held-out books -> universe of pair codes and candidate tuples
    real = counts_of(sets)
    U = [real["p"][0]]
    cand = {k: [candidates(real, k)] for k in real}
    for i in range(RE, RE + RH):
        c = counts_of(null_book(i))
        U.append(c["p"][0])
        for k in cand:
            cand[k].append(candidates(c, k))
    U = np.unique(np.concatenate(U))
    cand = {k: np.unique(np.concatenate(v)) for k, v in cand.items()}
    acc = Acc(U, cand, NQ)
    # pass B: expectation books
    for i in range(RE):
        acc.add(counts_of(null_book(i)))
    # pass C: score real and held-out
    S0, NT0, pk0, G0 = score(real, acc, RE, True)
    Sh, NTh, Gh = [], [], []
    for i in range(RE, RE + RH):
        s, n, _, g = score(counts_of(null_book(i)), acc, RE, True)
        Sh.append(s); NTh.append(n); Gh.append(g)
    Sh = np.array(Sh); NTh = np.array(NTh)
    pS = (1 + int(np.sum(Sh >= S0))) / (RH + 1)
    q99NT = float(np.quantile(NTh, 0.99))
    excess = pS <= ALPHA
    is_T = excess and NT0 > q99NT and NT0 >= NT_MIN and NT0 >= NT_RATIO * q99NT
    Q0 = pQ = None
    Qh = None
    # s122: Q under the quire null whenever there is excess (also for T cells; the both-null CALL needs it)
    if do_Q and excess:
        Q0 = modularity(G0, Vc)
        Qh = np.array([modularity(g, Vc) for g in Gh])
        pQ = (1 + int(np.sum(Qh >= Q0))) / (RH + 1)
    if not excess:
        call = "P"
    elif is_T:
        call = "T"
    elif pQ is not None and pQ <= ALPHA:
        call = "C"
    else:
        call = "X"
    return dict(rep=rep, strata=strata, n_lines=len(sets), V=V, S=S0, S_null_mean=float(Sh.mean()),
                S_null_sd=float(Sh.std(ddof=1)), z_S=float((S0 - Sh.mean()) / (Sh.std(ddof=1) or 1)), p_S=pS,
                N_T=NT0, N_T_kinds=pk0, N_T_null_mean=float(NTh.mean()), N_T_null_q99=q99NT,
                Q=Q0, Q_null_mean=None if Qh is None else float(Qh.mean()),
                Q_null_q99=None if Qh is None else float(np.quantile(Qh, 0.99)), p_Q=pQ, call=call,
                n_cand={k: len(v) for k, v in cand.items()}, secs=round(time.time() - t0, 1),
                tuples=(top_tuples(book, sets, keep, V, tri, nm, real, acc, RE, n_tuples) if n_tuples else None))


def fmt(r):
    q = "n/a" if r["Q"] is None else (f"{r['Q']:.4f} (null mean {r['Q_null_mean']:.4f}, q99 {r['Q_null_q99']:.4f}, "
                                      f"p {r['p_Q']:.4f})")
    return (f"{r['rep']:4s} null={r['strata']:5s} lines {r['n_lines']} units {r['V']} | S {r['S']:.1f} null "
            f"{r['S_null_mean']:.1f}+-{r['S_null_sd']:.1f} z {r['z_S']:.2f} p {r['p_S']:.4f} | N_T {r['N_T']} "
            f"{r['N_T_kinds']} null mean {r['N_T_null_mean']:.2f} q99 {r['N_T_null_q99']:.2f} | Q {q} | call "
            f"{r['call']} | {r['secs']}s")


# ------------------------------------------------------------------------------------------------ producers
def layout_and_vocab():
    b = load_book("ZL3b_eva")
    n = [len(l) for l in b["lines"]]
    NQ = len(b["quires"])
    qfreq = [Counter() for _ in range(NQ)]
    g = Counter()
    for l, q in zip(b["lines"], b["quire"]):
        qfreq[q].update(l); g.update(l)
    return b, n, qfreq, g


def produce(kind, seed, layout, p_nc=None):
    b, n, qfreq, g = layout
    rng = np.random.default_rng([seed, ["table", "content", "pool", "nearcopy"].index(kind)])
    NQ = len(qfreq)
    qw = []
    for q in range(NQ):
        ws = list(qfreq[q]); p = np.array([qfreq[q][w] for w in ws], float)
        qw.append((ws, np.cumsum(p) / p.sum()))
    def pool_line(q, k, line):
        ws, cdf = qw[q]
        draws = np.minimum(np.searchsorted(cdf, rng.random(k)), len(ws) - 1)
        for d in draws:
            if line and rng.random() < P_COPY:
                line.append(line[rng.integers(len(line))])
            else:
                line.append(ws[d])
        return line
    lines = []
    if kind == "table":
        ranked = [w for w, _ in g.most_common()][T_RANKS[0]:T_RANKS[1]]
        table = [list(rng.choice(ranked, size=T_WIDTH, replace=False)) for _ in range(T_ROWS)]
        for k, q in zip(n, b["quire"]):
            line = []
            if k >= T_WIDTH + 1 and rng.random() < T_PROB:
                line = list(table[rng.integers(T_ROWS)])
            lines.append(pool_line(q, k - len(line), line))
    elif kind == "content":
        topics = []
        for q in range(NQ):
            ws = [w for w in qfreq[q] if qfreq[q][w] >= 2]
            tq = []
            for _ in range(C_TOPICS):
                mem = list(rng.choice(ws, size=min(C_SIZE, len(ws)), replace=False))
                tq.append((mem, np.cumsum(rng.dirichlet(np.full(len(mem), C_ALPHA)))))
            topics.append(tq)
        for k, q in zip(n, b["quire"]):
            mem, wt = topics[q][rng.integers(C_TOPICS)]
            line = []
            for _ in range(k):
                if rng.random() < C_LAMBDA:
                    line.append(mem[min(int(np.searchsorted(wt, rng.random())), len(mem) - 1)])
                else:
                    pool_line(q, 1, line)
            lines.append(line)
    elif kind == "nearcopy":
        p_nc = P_NC if p_nc is None else p_nc
        nb = neighbors(g)
        gl, gcdf = glyph_dist(g)
        def variant(s, q):
            cands = nb.get(s, [])
            inq = [w for w in cands if qfreq[q][w] > 0]
            if inq:
                p = np.array([qfreq[q][w] for w in inq], float)
                return inq[min(int(np.searchsorted(np.cumsum(p) / p.sum(), rng.random())), len(inq) - 1)]
            if cands:
                p = np.array([g[w] for w in cands], float)
                return cands[min(int(np.searchsorted(np.cumsum(p) / p.sum(), rng.random())), len(cands) - 1)]
            for _ in range(10):
                i = int(rng.integers(len(s)))
                c = gl[min(int(np.searchsorted(gcdf, rng.random())), len(gl) - 1)]
                if c != s[i]:
                    return s[:i] + c + s[i + 1:]
            return s + gl[0]
        for k, q in zip(n, b["quire"]):
            line, seeds = [], []
            for _ in range(k):
                if line and rng.random() < P_COPY:
                    line.append(line[rng.integers(len(line))])
                elif seeds and rng.random() < p_nc:
                    line.append(variant(seeds[rng.integers(len(seeds))], q))
                else:
                    ws, cdf = qw[q]
                    w = ws[min(int(np.searchsorted(cdf, rng.random())), len(ws) - 1)]
                    seeds.append(w); line.append(w)
            lines.append(line)
    else:
        for k, q in zip(n, b["quire"]):
            lines.append(pool_line(q, k, []))
    return dict(lines=lines, quire=b["quire"].copy(), page=b["page"].copy(), quires=b["quires"], pages=b["pages"])


# ------------------------------------------------------------------------------------- s122 additions: helpers
def lev(a, b, maxd=2):
    """Levenshtein distance, returns maxd + 1 once it is known to exceed maxd."""
    if abs(len(a) - len(b)) > maxd:
        return maxd + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        if min(cur) > maxd:
            return maxd + 1
        prev = cur
    return prev[-1]


def _deletes(w, d=2):
    out = {w}
    fr = {w}
    for _ in range(d):
        nx_ = set()
        for x in fr:
            for i in range(len(x)):
                nx_.add(x[:i] + x[i + 1:])
        out |= nx_
        fr = nx_
    return out


_NB = {}


def neighbors(g):
    """word type -> list of word types at Levenshtein distance 1 or 2 (symmetric-delete index, verified)."""
    key = id(g)
    if key in _NB:
        return _NB[key]
    idx = defaultdict(set)
    ws = list(g)
    for w in ws:
        for k in _deletes(w):
            idx[k].add(w)
    nb = {}
    for w in ws:
        c = set()
        for k in _deletes(w):
            c |= idx[k]
        c.discard(w)
        nb[w] = sorted(x for x in c if lev(w, x) <= 2)
    _NB[key] = nb
    return nb


def glyph_dist(g):
    c = Counter()
    for w, n in g.items():
        for ch in w:
            c[ch] += n
    gl = sorted(c)
    p = np.array([c[x] for x in gl], float)
    return gl, np.cumsum(p) / p.sum()


def adjacent_ed(lines):
    """-> (Counter of Levenshtein distance 0, 1, 2, '3+' over adjacent within-line word pairs, n pairs)."""
    c = Counter()
    for l in lines:
        for a, b in zip(l, l[1:]):
            d = lev(a, b)
            c[d if d <= 2 else "3+"] += 1
    return c, sum(c.values())


def rate12(lines):
    c, n = adjacent_ed(lines)
    return (c[1] + c[2]) / max(n, 1)


def calibrate_nc(layout, P):
    """Estimate the real F-13 near-copy rate (adjacent-word edit distance) and set P_NC to match it."""
    b = layout[0]
    c, n = adjacent_ed(b["lines"])
    r_real = (c[1] + c[2]) / n
    P(f"F-13 NEAR-COPY RATE ESTIMATE (real ZL3b, adjacent within-line word pairs, raw words, '?'/'*' dropped): "
      f"n pairs {n}; ED0 {c[0] / n:.4f}  ED1 {c[1] / n:.4f}  ED2 {c[2] / n:.4f}  ED3+ {c['3+'] / n:.4f}; "
      f"r_real = share at ED 1-2 = {r_real:.4f}")
    # same statistic for pairs drawn from the quire pool (two independent pool tokens of the same quire)
    rng = np.random.default_rng([SEED, 99])
    qfreq = layout[2]
    pc = Counter()
    nq_lines = Counter(int(x) for x in b["quire"])
    for q in range(len(qfreq)):
        ws = list(qfreq[q]); p = np.array([qfreq[q][w] for w in ws], float); p /= p.sum()
        m = int(round(n * nq_lines[q] / len(b["quire"])))
        a = rng.choice(len(ws), m, p=p); bb = rng.choice(len(ws), m, p=p)
        for i, j in zip(a, bb):
            d = lev(ws[i], ws[j]); pc[d if d <= 2 else "3+"] += 1
    pn = sum(pc.values())
    P(f"  quire-pool baseline (independent same-quire token pairs, {pn} pairs): ED0 {pc[0] / pn:.4f}  ED1 "
      f"{pc[1] / pn:.4f}  ED2 {pc[2] / pn:.4f}  ED3+ {pc['3+'] / pn:.4f}; share at ED 1-2 = "
      f"{(pc[1] + pc[2]) / pn:.4f}")
    grid = []
    for x in NC_GRID:
        r = float(np.mean([rate12(produce("nearcopy", SEED + s, layout, p_nc=x)["lines"]) for s in NC_CAL_SEEDS]))
        grid.append((x, r))
    P("  near-copy producer r(P_NC) on calibration seeds " + str(list(NC_CAL_SEEDS)) + ": "
      + ", ".join(f"{x:.2f}:{r:.4f}" for x, r in grid))
    if grid[0][1] >= r_real:
        p_nc = 0.0
    elif grid[-1][1] < r_real:
        p_nc = grid[-1][0]
    else:
        for (x0, r0), (x1, r1) in zip(grid, grid[1:]):
            if r0 < r_real <= r1:
                p_nc = x0 + (x1 - x0) * (r_real - r0) / (r1 - r0)
                break
    p_nc = round(p_nc, 4)
    chk = float(np.mean([rate12(produce("nearcopy", SEED + s, layout, p_nc=p_nc)["lines"]) for s in NC_CAL_SEEDS]))
    P(f"  calibrated P_NC = {p_nc:.4f} (producer r at P_NC = {chk:.4f} vs r_real {r_real:.4f})")
    return p_nc


def top_tuples(book, sets, keep, V, tri, nm, real, acc, RE, n):
    """Descriptive list: candidate tuples of the real book passing N_T's global test, ranked by line count."""
    NQ = acc.NQ
    names, gnames = nm
    rows = []
    for k in acc.cand:
        c = candidates(real, k)
        if not len(c):
            continue
        obs = lookup(c, real[k][0], real[k][1])
        ci = np.searchsorted(acc.cand[k], c)
        Et = acc.gsum[k][ci] / RE
        glob = (obs > acc.g2[k][ci]) & (obs >= LIFT * Et)
        oq = dense_q(c, real[k][3], real[k][4], NQ).reshape(len(c), NQ)
        qstar = np.argmax(oq, axis=1)
        om = obs - oq[np.arange(len(c)), qstar]
        f = ci * NQ + qstar
        Em = Et - acc.qsum[k][f] / RE
        cross = (om >= MIN_OUTSIDE) & (om > acc.m2[k][f]) & (om >= LIFT * Em)
        for j in np.nonzero(glob)[0]:
            rows.append((int(obs[j]), float(obs[j] / Et[j]) if Et[j] > 0 else float("inf"), k, int(c[j]),
                         float(Et[j]), bool(cross[j]), oq[j]))
    rows.sort(key=lambda r: (-r[0], -r[1]))
    out = []
    pg = book["page"][keep]
    for obs, lift, k, code, Et, cross, oq in rows[:n]:
        if tri is None:
            ids = [code // V, code % V] if k == "p" else [code // (V * V), (code // V) % V, code % V]
            label = " + ".join(names[i] for i in ids)
            hit = [i for i, s in enumerate(sets) if all(u in s for u in ids)]
        else:
            feats, G = tri
            a, b = code // G, code % G
            label = f"{gnames[a]} ~ {gnames[b]}"
            hit = []
            for i, s in enumerate(sets):
                ua = [u for u in s if a in feats[u]]
                if ua and any(b in feats[v] for v in s if any(v != x for x in ua)):
                    hit.append(i)
        qs = ", ".join(f"{book['quires'][q]}:{int(oq[q])}" for q in np.argsort(-oq, kind="stable") if oq[q] > 0)
        pc = Counter(book["pages"][pg[i]] for i in hit)
        pages = ", ".join(f"{p}" + (f"x{m}" if m > 1 else "") for p, m in sorted(pc.items()))
        out.append(dict(kind=k, label=label, lines=obs, E=Et, lift=lift, in_NT=cross, quires=qs,
                        n_quires=int(np.sum(oq > 0)), n_pages=len(pc), pages=pages, n_hit=len(hit)))
    return out


def both_call(rq, rp):
    """s122 cell CALL: T only if the s117 rule gives T under the quire AND the page null; else the s117 rule
    without T under the quire null."""
    if rq["call"] == "T" and rp is not None and rp["call"] == "T":
        return "T"
    if rq["p_S"] > ALPHA:
        return "P"
    if rq["p_Q"] is not None and rq["p_Q"] <= ALPHA:
        return "C"
    return "X"


def ram_check():
    try:
        import psutil
        free = psutil.virtual_memory().available / 2 ** 30
    except Exception:
        return "free RAM unknown"
    if free < MIN_FREE_GB:
        raise SystemExit(f"free RAM {free:.1f} GB < {MIN_FREE_GB} GB; not starting")
    return f"free RAM {free:.1f} GB"


EXPECT = {"table": "T", "content": "C", "pool": "P", "nearcopy": "not T"}
KINDS = ("table", "content", "pool", "nearcopy")
_LAYOUT = None


def _fixture_job(args):
    kind, s, rep, strata, ov = args
    global _LAYOUT
    for name, val in ov.items():
        globals()[name] = val
    lower_priority()
    if _LAYOUT is None:
        _LAYOUT = layout_and_vocab()
    book = produce(kind, SEED + s, _LAYOUT)
    r = analyze(book, rep, strata=strata, seed=SEED + 1000 + s, do_Q=(strata == "quire"))
    r["kind"] = kind; r["seed"] = s
    return r


def _real_job(args):
    tr, fname, rep, strata = args
    lower_priority()
    book = load_book(fname)
    r = analyze(book, rep, strata=strata, do_Q=(strata == "quire"), n_tuples=TOP_TUPLES if strata == "quire" else 0)
    r["translit"] = tr
    return r


def run_pool(fn, jobs, P):
    import multiprocessing as mp
    res = []
    with mp.get_context("spawn").Pool(WORKERS) as pool:
        for r in pool.imap_unordered(fn, jobs):
            P(("  " + (f"{r.get('kind','')} seed {r.get('seed','')} " if 'kind' in r else f"{r['translit']} ")
               + fmt(r)))
            res.append(r)
    return res


def run_fixture(seeds, reps):
    os.makedirs(RUNDIR, exist_ok=True)
    out = os.path.join(RUNDIR, f"fixture_{time.strftime('%Y%m%d_%H%M%S')}.txt")
    if os.path.exists(out):
        raise SystemExit("refusing to overwrite " + out)
    L = []
    def P(s=""):
        print(s, flush=True); L.append(s)
        open(out, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    P(f"s122 fixture. started {now()}; {lower_priority()}; workers {WORKERS}; {ram_check()}; script sha256 "
      f"{sha(os.path.abspath(__file__))}")
    layout = layout_and_vocab()
    p_nc = calibrate_nc(layout, P)
    P(f"R_E {R_E} R_H {R_H} TRADES {TRADES} ALPHA {ALPHA} NT_MIN {NT_MIN} NT_RATIO {NT_RATIO}; producers: table "
      f"rows {T_ROWS}x{T_WIDTH} prob {T_PROB} ranks {T_RANKS}; content topics {C_TOPICS}x{C_SIZE} alpha {C_ALPHA} "
      f"lambda {C_LAMBDA}; pool copy {P_COPY}; nearcopy P_NC {p_nc} (copy {P_COPY})")
    ov = {"P_NC": p_nc}
    jobs = [(k, s, rep, st, ov) for rep in reps for k in ("nearcopy", "table") for s in seeds
            for st in ("quire", "page")]
    jobs += [(k, s, rep, "quire", ov) for rep in reps for k in ("content", "pool") for s in seeds]
    res = run_pool(_fixture_job, jobs, P)
    extra = [(r["kind"], r["seed"], r["rep"], "page", ov) for r in res
             if r["kind"] in ("content", "pool") and r["call"] == "T"]
    if extra:
        P(f"  page null needed for {len(extra)} content/pool seeds with a quire-null T")
        res += run_pool(_fixture_job, extra, P)
    P("")
    ok = {}
    for rep in reps:
        for k in KINDS:
            rq = sorted([r for r in res if r["rep"] == rep and r["kind"] == k and r["strata"] == "quire"],
                        key=lambda r: r["seed"])
            calls, cq, cp = [], [], []
            for r in rq:
                rp = [x for x in res if x["rep"] == rep and x["kind"] == k and x["strata"] == "page"
                      and x["seed"] == r["seed"]]
                rp = rp[0] if rp else None
                calls.append(both_call(r, rp)); cq.append(r["call"]); cp.append(rp["call"] if rp else "-")
            ncor = sum((c != "T") if k == "nearcopy" else (c == EXPECT[k]) for c in calls)
            need = math.ceil(0.8 * len(calls))
            ok[(rep, k)] = ncor >= need
            P(f"FIXTURE {rep:4s} {k:8s} expect {EXPECT[k]:5s}: correct {ncor}/{len(calls)} (CALL {''.join(calls)}; "
              f"quire-null {''.join(cq)}; page-null {''.join(cp)}) need >= {need}: "
              f"{'PASS' if ok[(rep, k)] else 'FAIL'}")
    t_ok = all(ok[(r, "table")] for r in reps)
    nc_ok = all(ok[(r, "nearcopy")] for r in reps)
    if t_ok and not nc_ok:
        bad = [r for r in reps if not ok[(r, "nearcopy")]]
        P(f"T_UNIDENTIFIABLE: table and near-copy books are not separated in {', '.join(bad)} (near-copy gives T "
          f"under both nulls on > 2/10 seeds). Stop: no stub, no real run.")
    P(f"FIXTURE_GATE {'PASS' if all(ok.values()) else 'FAIL'}; finished {now()}")
    return out


def verify_stub():
    if not os.path.exists(STUB):
        raise SystemExit(f"stub missing: {STUB}; freeze before --run")
    raw = open(STUB, "rb").read()
    if b"\r" in raw:
        raise SystemExit("stub contains CR bytes")
    n, fx = 0, None
    for line in raw.decode().split("\n"):
        if not line.strip() or line.startswith("#"):
            continue
        h, p = line.split(" ", 1)
        p = p.lstrip("*")
        if sha(os.path.join(ROOT, p)) != h:
            raise SystemExit(f"stub mismatch for {p}")
        if p.startswith("runs/s122/fixture_"):
            fx = p
        n += 1
    if fx is None or "FIXTURE_GATE PASS" not in open(os.path.join(ROOT, fx), encoding="utf-8").read():
        raise SystemExit("stub names no fixture file with FIXTURE_GATE PASS")
    return n, fx


def majority(calls):
    c = Counter(calls).most_common(1)[0]
    return c[0] if c[1] >= 2 else "MIXED"


def run_real():
    nver, fx = verify_stub()
    out = os.path.join(ROOT, f"results_s122_{time.strftime('%Y%m%d_%H%M%S')}.txt")
    if os.path.exists(out):
        raise SystemExit("refusing to overwrite " + out)
    L = []
    def P(s=""):
        print(s, flush=True); L.append(s)
        open(out, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    P(f"s122 within-line co-occurrence, quire null + page null, near-copy controlled -- REAL RUN. Design D-066 (bb). "
      f"started {now()}; {lower_priority()}; workers {WORKERS}; {ram_check()}")
    P(f"script tools/s122_cooccurrence_nearcopy.py sha256 {sha(os.path.abspath(__file__))}; stub "
      f"{os.path.basename(STUB)} verified ({nver} files) sha256 {sha(STUB)}; fixture {fx} (FIXTURE_GATE PASS)")
    for tr, f in TRANSLITS:
        P(f"data {tr}: data/translit/{f}.meta.json sha256 {sha(os.path.join(ROOT, 'data', 'translit', f + '.meta.json'))}")
    P(f"R_E {R_E} R_H {R_H} TRADES {TRADES} ALPHA {ALPHA} NT_MIN {NT_MIN} NT_RATIO {NT_RATIO} seed {SEED}")
    jobs = [(tr, f, rep, st) for st in ("quire", "page") for tr, f in TRANSLITS for rep in REPS]
    res = run_pool(_real_job, jobs, P)
    P("")
    def get(tr, rep, st):
        return [x for x in res if x["translit"] == tr and x["rep"] == rep and x["strata"] == st][0]
    tcall = {}
    for tr, _ in TRANSLITS:
        calls = []
        for rep in REPS:
            rq, rp = get(tr, rep, "quire"), get(tr, rep, "page")
            c = both_call(rq, rp)
            pq = "n/a" if rq["p_Q"] is None else format(rq["p_Q"], ".4f")
            P(f"CALL {tr} {rep}: {c}  (quire null: {rq['call']}, p_S {rq['p_S']:.4f}, z_S {rq['z_S']:.2f}, N_T "
              f"{rq['N_T']} vs q99 {rq['N_T_null_q99']:.2f}, p_Q {pq} | page null: {rp['call']}, p_S "
              f"{rp['p_S']:.4f}, z_S {rp['z_S']:.2f}, N_T {rp['N_T']} vs q99 {rp['N_T_null_q99']:.2f})")
            calls.append(c)
        tcall[tr] = majority(calls)
        P(f"CALL {tr} transliteration: {tcall[tr]}")
    z = tcall["ZL3b"]
    overall = z if tcall["RF1b"] == z and tcall["IT2a"] == z else f"NOT_REPLICATED (ZL3b {z})"
    P(f"CALL overall: {overall}")
    P("")
    P(f"DESCRIPTIVE top-{TOP_TUPLES} recurring tuples (quire null; candidates passing N_T's global test, ranked by "
      f"lines; no call from this list). Columns: rank | kind | tuple | lines | null mean | lift | in N_T | n quires "
      f"| quires (lines) | n pages | pages")
    for tr, _ in TRANSLITS:
        for rep in REPS:
            rq = get(tr, rep, "quire")
            P(f"TUPLES {tr} {rep} ({len(rq['tuples'])} listed)")
            for i, t in enumerate(rq["tuples"], 1):
                P(f"  {i:2d} | {t['kind']} | {t['label']} | {t['lines']} | {t['E']:.2f} | {t['lift']:.1f} | "
                  f"{'Y' if t['in_NT'] else 'n'} | {t['n_quires']} | {t['quires']} | {t['n_pages']} | {t['pages']}")
    P(f"finished {now()}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--calibrate", action="store_true", help="print the near-copy calibration only (no file)")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--reps", default=",".join(REPS))
    a = ap.parse_args()
    if a.fixture:
        run_fixture(list(range(a.seeds)), a.reps.split(","))
    elif a.calibrate:
        calibrate_nc(layout_and_vocab(), print)
    elif a.run:
        run_real()
    else:
        ap.print_help()
