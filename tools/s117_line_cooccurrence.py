"""s117 -- within-line co-occurrence of distinct units against the F-41 quire pool. Design: DECISIONS.md D-066 (w),
lead 1 of .inventory/runs/2026-10-18/bigpicture-mechanism.md.

Question: inside a line, do particular unit pairs co-occur more than the quire's own pool predicts? If so, is the
excess a TABLE (T: a small set of recurring tuples reused across quires), CONTENT (C: graded clusters, quire-local,
no fixed tuples) or is there no excess (P: plain pool)?

Reading-order agnostic: a line is used only as a SET of units. Word order inside a line, line order and page order
are never read.

Modes (run from the project root, python -I tools/s117_line_cooccurrence.py ...):
  --fixture   three planted books (table / content / pool) x 10 seeds on the real ZL3b line and quire layout.
              Writes runs/s117/fixture_<YYYYmmdd_HHMMSS>.txt. No co-occurrence statistic of the real text is computed
              (only line sizes, quire/page membership and per-quire word frequencies are read).
  --run       real data, ZL3b primary, RF1b and IT2a replication. Refuses to run unless the stub
              s117_line_cooccurrence.prereg.sha256 verifies. Writes results_s117_<YYYYmmdd_HHMMSS>.txt (never
              overwrites).

Frozen design (fixed before any real co-occurrence statistic):
  Data: data/translit/{ZL3b_eva,RF1b,IT2a}.meta.json (P* running-text lines, the S97.TRANSLITS map). Tokens with
    '?' or '*' are dropped. Quire = page 'quire' field.
  Representations (unit = what the null shuffles; feature = what is counted):
    core  unit = SlotSegmenter core (scoreboard.metrics_new, fitted on all tokens of the book), feature = unit.
    word  unit = raw whitespace word, feature = unit.
    tri   unit = raw word; features = padded glyph 3-grams of '#'+word+'#'. A feature pair counts only when the two
          3-grams come from two DIFFERENT word types of the line (word-internal 3-gram pairs are excluded); no triples.
  Line = the set of distinct units (repeats inside a line are collapsed, so F-40 in-line reuse is controlled, not
    tested). Lines with no unit are dropped.
  Null (the F-41 pool): curveball randomisation of the binary line x unit incidence matrix within each quire. It keeps
    every line's number of distinct units and every unit's number of lines in each quire, and reshuffles which
    units share a line. Besag-Clifford parallel scheme: a hub is reached from the real book by TRADES x n_lines
    trades per quire and every null book is TRADES x n_lines trades from the hub (TRADES = 5), so real and null
    books are exchangeable.
    R_E = 100 null books estimate per-tuple expectations and q99s; R_H = 100 further, independent null books give
    the null distribution of each book-level statistic (real and held-out books are scored identically against the
    same R_E set, so they are exchangeable under the null).
  Statistics (pairs = unordered feature pairs; a tuple's count = number of lines containing it):
    S   total pairwise PMI excess (Poisson half-deviance) = sum over the pair universe U (all pairs seen in the real or
        held-out books) of n ln((n + 0.5) / (E + 0.5)) - (n - E), E = mean count over the R_E books.
        p_S = (1 + #{held S >= real S}) / (R_H + 1).
    N_T recurring excess tuples = number of pairs and triples (pairs only for tri) that (i) occur in >= 3 lines and
        >= 2 quires; (ii) globally: count > the null q99 (2nd-largest of its R_E counts) and count >= LIFT x its null
        mean; (iii) reused across quires: with q* = the tuple's top quire in the scored book, its count OUTSIDE q* is
        >= MIN_OUTSIDE lines, > the null q99 of the outside-q* count, and >= LIFT x the null mean outside q*.
        LIFT = 3, MIN_OUTSIDE = 3. Compared with q99_H(N_T), the 99th percentile over the R_H held-out books.
    Q   gradedness = Louvain modularity (networkx, seed fixed, resolution 1) of the pair-excess graph: edges = pairs
        with count >= 2 and count > E, weight count - E. p_Q as p_S. Q is computed only when the rule needs it
        (excess present and not T); otherwise printed as 'n/a'.
  Decision rule (per representation x transliteration), applied identically to fixture and real books:
    P  if p_S > ALPHA (no excess over the pool);
    T  if p_S <= ALPHA and N_T > q99_H(N_T) and N_T >= NT_MIN and N_T >= NT_RATIO x q99_H(N_T);
    C  if p_S <= ALPHA, not T, and p_Q <= ALPHA;
    X  (excess, unclassified) otherwise.
    Constants: ALPHA = 0.01 (so p <= ALPHA needs the real book above all 100 held-out books), NT_MIN = 10,
    NT_RATIO = 2.
  Transliteration call = the call shared by >= 2 of the 3 representations, else MIXED.
  Overall CALL = ZL3b's transliteration call if RF1b and IT2a give the same call; else NOT_REPLICATED (ZL3b call
    printed).
  Fixture gate: each producer classified correctly on >= 8/10 seeds in EACH representation; if not, stop.
  Diagnostic (not a call): S and N_T under a within-PAGE curveball null (cores and words), to show how much of any
    quire-null excess is page-local vocabulary. N_T's outside-top-quire test still uses quires.

Fixture producers (real ZL3b layout: every line's token count and quire; words drawn from real per-quire word
frequencies; no real co-occurrence is used):
  pool    each token drawn from its quire's word distribution, with in-line copy rate P_COPY = 0.15 (F-41 style).
  table   a global table of 60 rows x 3 words (global frequency ranks 30..600); 25% of lines with >= 4 tokens carry
          one row (uniform over rows, so rows recur across quires); the rest of the line is pool.
  content per quire 4 topics of 40 words (types with count >= 2 in that quire), Dirichlet(0.5) weights; each line
          picks one topic; each token comes from the topic with probability 0.35, else from the pool (quire-local).
  Expected calls: table T, content C, pool P.

Development history (before the 10-seed fixture, on fixture books only, no real statistic): the first draft started
every null chain from the real book (pool books scored z -8 below their null -> Besag-Clifford hub); S summed
n ln(n/E) over present pairs (tri null sd 4,000 because the total of cross-word pairs varies -> deviance form);
N_T used a per-quire q99 rule with a null floor of 100-200 tuples (-> LIFT 3, MIN_OUTSIDE 3, leave-top-quire-out).
Those settings were chosen on fixture seed 1 at R_E = R_H = 40 and are frozen here; the 10-seed fixture tests them.
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

RUNDIR = os.path.join(ROOT, "runs", "s117")
STUB = os.path.join(ROOT, "s117_line_cooccurrence.prereg.sha256")
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
                page=np.array([pages.index(x) for x in pn]), quires=quires)


def build_rep(lines, rep):
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


def analyze(book, rep, strata="quire", seed=SEED, RE=R_E, RH=R_H, do_Q=True):
    """Full s117 analysis of one book in one representation. Returns a dict of statistics and the call."""
    t0 = time.time()
    sets, keep, V, tri = build_rep(book["lines"], rep)
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
    if do_Q and excess and not is_T:
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
                n_cand={k: len(v) for k, v in cand.items()}, secs=round(time.time() - t0, 1))


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


def produce(kind, seed, layout):
    b, n, qfreq, g = layout
    rng = np.random.default_rng([seed, ["table", "content", "pool"].index(kind)])
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
    else:
        for k, q in zip(n, b["quire"]):
            lines.append(pool_line(q, k, []))
    return dict(lines=lines, quire=b["quire"].copy(), page=b["page"].copy(), quires=b["quires"])


EXPECT = {"table": "T", "content": "C", "pool": "P"}
_LAYOUT = None


def _fixture_job(args):
    kind, s, rep = args[:3]
    global _LAYOUT
    for name, val in (args[3] if len(args) > 3 else {}).items():
        globals()[name] = val
    lower_priority()
    if _LAYOUT is None:
        _LAYOUT = layout_and_vocab()
    book = produce(kind, SEED + s, _LAYOUT)
    r = analyze(book, rep, seed=SEED + 1000 + s)
    r["kind"] = kind; r["seed"] = s
    if len(args) > 3:
        r["kind"] = kind + "".join(f" {k}={v}" for k, v in args[3].items())
    return r


def _real_job(args):
    tr, fname, rep, strata = args
    lower_priority()
    book = load_book(fname)
    r = analyze(book, rep, strata=strata, do_Q=(strata == "quire"))
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
    P(f"s117 fixture. started {now()}; {lower_priority()}; workers {WORKERS}; script sha256 "
      f"{sha(os.path.abspath(__file__))}")
    P(f"R_E {R_E} R_H {R_H} TRADES {TRADES} ALPHA {ALPHA} NT_MIN {NT_MIN} NT_RATIO {NT_RATIO}; producers: table "
      f"rows {T_ROWS}x{T_WIDTH} prob {T_PROB} ranks {T_RANKS}; content topics {C_TOPICS}x{C_SIZE} alpha {C_ALPHA} "
      f"lambda {C_LAMBDA}; pool copy {P_COPY}")
    jobs = [(k, s, rep) for rep in reps for k in ("table", "content", "pool") for s in seeds]
    res = run_pool(_fixture_job, jobs, P)
    P("")
    ok_all = True
    for rep in reps:
        for k in ("table", "content", "pool"):
            rr = sorted([r for r in res if r["rep"] == rep and r["kind"] == k], key=lambda r: r["seed"])
            ncor = sum(r["call"] == EXPECT[k] for r in rr)
            need = math.ceil(0.8 * len(rr))
            ok = ncor >= need
            ok_all &= ok
            P(f"FIXTURE {rep:4s} {k:7s} expect {EXPECT[k]}: correct {ncor}/{len(rr)} (calls "
              f"{''.join(r['call'] for r in rr)}) need >= {need}: {'PASS' if ok else 'FAIL'}")
    P(f"FIXTURE_GATE {'PASS' if ok_all else 'FAIL'}; finished {now()}")
    return out


def run_power(seeds=(0, 1, 2), reps=("core", "word")):
    """Diagnostic, not a gate: weaker planted strengths, to say what effect a P call on real data would have missed."""
    os.makedirs(RUNDIR, exist_ok=True)
    out = os.path.join(RUNDIR, f"power_{time.strftime('%Y%m%d_%H%M%S')}.txt")
    if os.path.exists(out):
        raise SystemExit("refusing to overwrite " + out)
    L = []
    def P(s=""):
        print(s, flush=True); L.append(s)
        open(out, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    P(f"s117 power diagnostic (not a gate). started {now()}; {lower_priority()}; script sha256 "
      f"{sha(os.path.abspath(__file__))}")
    grid = [("table", {"T_PROB": 0.10}), ("table", {"T_PROB": 0.05}),
            ("content", {"C_LAMBDA": 0.20}), ("content", {"C_LAMBDA": 0.10})]
    jobs = [(k, s, rep, ov) for rep in reps for k, ov in grid for s in seeds]
    res = run_pool(_fixture_job, jobs, P)
    P("")
    for rep in reps:
        for k, ov in grid:
            lab = k + "".join(f" {a}={b}" for a, b in ov.items())
            rr = sorted([r for r in res if r["rep"] == rep and r["kind"] == lab], key=lambda r: r["seed"])
            P(f"POWER {rep:4s} {lab:22s} expect {EXPECT[k]}: correct {sum(r['call'] == EXPECT[k] for r in rr)}/"
              f"{len(rr)} calls {''.join(r['call'] for r in rr)}")
    P(f"finished {now()}")
    return out


def verify_stub():
    if not os.path.exists(STUB):
        raise SystemExit(f"stub missing: {STUB}; freeze before --run")
    raw = open(STUB, "rb").read()
    if b"\r" in raw:
        raise SystemExit("stub contains CR bytes")
    n = 0
    for line in raw.decode().split("\n"):
        if not line.strip() or line.startswith("#"):
            continue
        h, p = line.split(" ", 1)
        p = p.lstrip("*")
        if sha(os.path.join(ROOT, p)) != h:
            raise SystemExit(f"stub mismatch for {p}")
        n += 1
    return n


def majority(calls):
    c = Counter(calls).most_common(1)[0]
    return c[0] if c[1] >= 2 else "MIXED"


def run_real():
    nver = verify_stub()
    out = os.path.join(ROOT, f"results_s117_{time.strftime('%Y%m%d_%H%M%S')}.txt")
    if os.path.exists(out):
        raise SystemExit("refusing to overwrite " + out)
    L = []
    def P(s=""):
        print(s, flush=True); L.append(s)
        open(out, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    P(f"s117 within-line co-occurrence vs the F-41 quire pool -- REAL RUN. Design D-066 (w). started {now()}; "
      f"{lower_priority()}; workers {WORKERS}")
    P(f"script tools/s117_line_cooccurrence.py sha256 {sha(os.path.abspath(__file__))}; stub "
      f"{os.path.basename(STUB)} verified ({nver} files) sha256 {sha(STUB)}")
    for tr, f in TRANSLITS:
        P(f"data {tr}: data/translit/{f}.meta.json sha256 {sha(os.path.join(ROOT, 'data', 'translit', f + '.meta.json'))}")
    P(f"R_E {R_E} R_H {R_H} TRADES {TRADES} ALPHA {ALPHA} NT_MIN {NT_MIN} NT_RATIO {NT_RATIO} seed {SEED}")
    jobs = [(tr, f, rep, "quire") for tr, f in TRANSLITS for rep in REPS]
    jobs += [(tr, f, rep, "page") for tr, f in TRANSLITS for rep in ("core", "word")]
    res = run_pool(_real_job, jobs, P)
    P("")
    tcall = {}
    for tr, _ in TRANSLITS:
        calls = []
        for rep in REPS:
            r = [x for x in res if x["translit"] == tr and x["rep"] == rep and x["strata"] == "quire"][0]
            P(f"CALL {tr} {rep}: {r['call']}  (p_S {r['p_S']:.4f}, z_S {r['z_S']:.2f}, N_T {r['N_T']} vs null q99 "
              f"{r['N_T_null_q99']:.2f}, p_Q {'n/a' if r['p_Q'] is None else format(r['p_Q'], '.4f')})")
            calls.append(r["call"])
        tcall[tr] = majority(calls)
        P(f"CALL {tr} transliteration: {tcall[tr]}")
    for tr, _ in TRANSLITS:
        for rep in ("core", "word"):
            r = [x for x in res if x["translit"] == tr and x["rep"] == rep and x["strata"] == "page"][0]
            P(f"DIAGNOSTIC page-null {tr} {rep}: p_S {r['p_S']:.4f} z_S {r['z_S']:.2f} N_T {r['N_T']} vs null q99 "
              f"{r['N_T_null_q99']:.2f} (rule would give {r['call']}; not a call)")
    z = tcall["ZL3b"]
    overall = z if tcall["RF1b"] == z and tcall["IT2a"] == z else f"NOT_REPLICATED (ZL3b {z})"
    P(f"CALL overall: {overall}")
    P(f"finished {now()}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--power", action="store_true")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--reps", default=",".join(REPS))
    a = ap.parse_args()
    if a.fixture:
        run_fixture(list(range(a.seeds)), a.reps.split(","))
    elif a.power:
        run_power()
    elif a.run:
        run_real()
    else:
        ap.print_help()
