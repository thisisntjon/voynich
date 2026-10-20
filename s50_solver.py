"""s50 helper: 5-gram letter LM and the homophonic SA/Gibbs solver with null flags (see s50_solver_ladder.py).

Everything here is specified in the s50_solver_ladder.py docstring; this module only implements it.
"""
from __future__ import annotations

import math
import time

import numpy as np

ALPHA = "abcdefghiklmnopqrstuxyz"   # 23 period letters (j->i, v->u, w->uu, ss for sharp s)
A = len(ALPHA)
A_IDX = {c: i for i, c in enumerate(ALPHA)}
W5 = np.array([A ** 4, A ** 3, A ** 2, A, 1], dtype=np.int64)


def letters_of(words):
    """Map corpora.control word tokens to the 23-letter stream (spaces dropped)."""
    out = []
    for w in words:
        w = w.replace("ß", "ss").replace("j", "i").replace("v", "u").replace("w", "uu")
        out.extend(A_IDX[c] for c in w if c in A_IDX)
    return np.asarray(out, dtype=np.int64)


# ------------------------------------------------------------------ language model
def train_lm(t):
    """Interpolated Witten-Bell 5-gram over the 23 letters; returns dense log2 P(x_e | x_{e-4..e-1}) (A^5,)
    and the unigram distribution q (A,)."""
    c1 = np.bincount(t, minlength=A).astype(np.float64)
    P = (c1 + 0.5) / (c1.sum() + 0.5 * A)          # order-1
    q = P.copy()
    for k in range(2, 6):
        n = len(t) - k + 1
        code = np.zeros(n, dtype=np.int64)
        for j in range(k):
            code = code * A + t[j:j + n]
        ck = np.bincount(code, minlength=A ** k).astype(np.float64).reshape(A ** (k - 1), A)
        ch = ck.sum(1)
        T = (ck > 0).sum(1).astype(np.float64)
        low = P.reshape(1, A ** (k - 2), A) if k > 2 else P.reshape(1, 1, A)
        num = ck.reshape(A, A ** (k - 2), A) + T.reshape(A, A ** (k - 2), 1) * low
        den = (ch + T).reshape(A, A ** (k - 2), 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            Pk = np.where(den > 0, num / np.where(den > 0, den, 1.0), np.broadcast_to(low, num.shape))
        P = Pk.reshape(-1)
        if k == 3:
            P3 = P.copy()
    lm5 = np.log2(P).astype(np.float32)
    lm3 = np.broadcast_to(np.log2(P3).reshape(1, A ** 3), (A ** 2, A ** 3)).reshape(-1).astype(np.float32)
    return lm5, q, lm3


def lm_bits_per_letter(lm, t):
    n = len(t) - 4
    code = np.zeros(n, dtype=np.int64)
    for j in range(5):
        code = code * A + t[j:j + n]
    return float(-lm[code].mean())


def lm_total(lm, x):
    n = len(x) - 4
    if n <= 0:
        return 0.0
    code = x[0:n] * W5[0] + x[1:n + 1] * W5[1] + x[2:n + 2] * W5[2] + x[3:n + 3] * W5[3] + x[4:n + 4]
    return float(lm[code].sum(dtype=np.float64))


def xlogx(v):
    v = np.asarray(v, dtype=np.float64)
    return np.where(v > 0, v * np.log2(np.where(v > 0, v, 1.0)), 0.0)


# ------------------------------------------------------------------ solver
class Solver:
    """State: letter[u] in 0..A-1 and null[u] for every unit type u of the stream s (int array).
    Score (bits) = LM + HOMO + NULL - w_kl * M * KL(p_dec || q):
      LM   = sum of log2 P_LM over the 5-gram windows of the decoded (non-null) letter stream,
      HOMO = sum_x [ sum_{u in x} n_u log2 n_u - N_x log2 N_x ]  (ML homophone choice log-likelihood),
      NULL = sum_{u null} n_u log2(n_u / N0) + N0 log2(N0/N) + (N-N0) log2((N-N0)/N)  (ML null emission),
      KL   = unigram KL of the decoded letters against the LM's unigram q."""

    def __init__(self, s, lm, q, w_kl, allow_null, rng, forced_null=None):
        self.s = np.asarray(s, dtype=np.int64)
        self.U = int(self.s.max()) + 1 if len(self.s) else 0
        self.n = np.bincount(self.s, minlength=self.U).astype(np.float64)
        self.N = float(len(self.s))
        self.lm, self.q, self.w_kl = lm, q, w_kl
        self.logq = np.log2(q)
        self.allow_null = allow_null
        self.rng = rng
        self.forced = np.zeros(self.U, dtype=bool) if forced_null is None else forced_null.copy()
        self.nlogn = xlogx(self.n)
        self.null_cap = 0.40
        self.null_start = 0.5
        self.null_T = 1.0
        self.null_pen = 0.0

    # ---- state helpers
    def set_state(self, letter, null):
        self.letter = letter.astype(np.int64).copy()
        self.null = (null | self.forced).copy()
        self._rebuild()

    def _rebuild(self):
        keep = ~self.null[self.s]
        self.cu = self.s[keep]                       # compact stream of unit ids
        self.x = self.letter[self.cu]
        self.M = len(self.x)
        order = np.argsort(self.cu, kind="stable")
        cnt = np.bincount(self.cu, minlength=self.U)
        starts = np.concatenate(([0], np.cumsum(cnt)))
        self.pos_order, self.pos_starts = order, starts
        self.lm_sum = lm_total(self.lm, self.x)

    def pos(self, u):
        return self.pos_order[self.pos_starts[u]:self.pos_starts[u + 1]]

    def letter_stats(self):
        nn = ~self.null
        Nx = np.bincount(self.letter[nn], weights=self.n[nn], minlength=A)
        Sx = np.bincount(self.letter[nn], weights=self.nlogn[nn], minlength=A)
        return Nx, Sx

    def aux_terms(self, Nx, Sx, N0, S0):
        homo = float((Sx - xlogx(Nx)).sum())
        if N0 > 0:
            nul = float(S0 - xlogx(N0) + xlogx(N0) - N0 * math.log2(self.N) + xlogx(self.N - N0) - (self.N - N0) * math.log2(self.N))
        else:
            nul = 0.0
        M = Nx.sum()
        if M > 0:
            p = Nx / M
            kl = float((xlogx(p) - p * self.logq).sum())
        else:
            kl = 0.0
        return homo + nul - self.w_kl * M * kl

    def aux_options(self, Nx, Sx, N0, S0, nu, su):
        """aux_terms for every option 'u -> letter b' at once (vectorised over b)."""
        I = np.eye(A)
        Nb = Nx[None, :] + nu * I
        Sb = Sx[None, :] + su * I
        homo = (Sb - xlogx(Nb)).sum(1)
        if N0 > 0:
            nul = S0 - N0 * math.log2(self.N) + float(xlogx(self.N - N0)) - (self.N - N0) * math.log2(self.N)
        else:
            nul = 0.0
        M = Nb.sum(1)
        p = Nb / M[:, None]
        kl = (xlogx(p) - p * self.logq[None, :]).sum(1)
        return homo + nul - self.w_kl * M * kl

    def score(self):
        Nx, Sx = self.letter_stats()
        N0 = float(self.n[self.null].sum())
        S0 = float(self.nlogn[self.null].sum())
        return self.lm_sum + self.aux_terms(Nx, Sx, N0, S0)

    # ---- per-unit option scores
    def _lm_options(self, u, x, cu, pos):
        """LM totals for u -> each letter b, on a stream where u occupies `pos` (letters at pos ignored)."""
        M = len(x)
        if len(pos) == 0:
            return np.zeros(A)
        E = np.unique((pos[:, None] + np.arange(5)[None, :]).ravel())
        E = E[(E >= 4) & (E < M)]
        if len(E) == 0:
            return np.zeros(A)
        idx = E[:, None] - 4 + np.arange(5)[None, :]
        L = x[idx]
        isu = cu[idx] == u
        codes0 = (np.where(isu, 0, L) * W5).sum(1)
        mult = (isu * W5).sum(1)
        cur = self.lm[(L * W5).sum(1)].sum(dtype=np.float64)
        vals = self.lm[codes0[None, :] + np.arange(A)[:, None] * mult[None, :]].sum(1, dtype=np.float64)
        return vals - cur

    def gibbs_unit(self, u, T, null_move):
        if self.forced[u] or self.n[u] == 0:
            return
        Nx, Sx = self.letter_stats()
        N0 = float(self.n[self.null].sum())
        S0 = float(self.nlogn[self.null].sum())
        nu, su = self.n[u], self.nlogn[u]
        was_null = bool(self.null[u])
        if not was_null:
            a = self.letter[u]
            Nx[a] -= nu
            Sx[a] -= su
        else:
            N0 -= nu
            S0 -= su
        # letter options
        if was_null:
            if not null_move:
                return
            keep = ~self.null[self.s] | (self.s == u)
            cu2 = self.s[keep]
            x2 = self.letter[cu2]
            pos2 = np.flatnonzero(cu2 == u)
            lm_null = self.lm_sum
            x2[pos2] = 0
            base2 = lm_total(self.lm, x2)
            d = self._lm_options(u, x2, cu2, pos2)
            # _lm_options returns vals - cur where cur used letter 0 at pos2
            lm_let = base2 + d
        else:
            d = self._lm_options(u, self.x, self.cu, self.pos(u))
            lm_let = self.lm_sum + d
            if null_move:
                lm_null = lm_total(self.lm, self.x[self.cu != u])
        opt = np.empty(A + (1 if null_move else 0))
        opt[:A] = lm_let + self.aux_options(Nx, Sx, N0, S0, nu, su)
        if null_move:
            opt[A] = lm_null + self.aux_terms(Nx, Sx, N0 + nu, S0 + su)
            opt[A] -= self.null_pen * nu
            if (N0 + nu) / self.N > self.null_cap:
                opt[A] = -np.inf
        if null_move:
            T = min(T, self.null_T)
        z = (opt - opt.max()) / max(T, 1e-9)
        p = np.exp2(z)
        p /= p.sum()
        k = int(self.rng.choice(len(opt), p=p)) if T > 1e-6 else int(np.argmax(opt))
        if k == A:
            if not was_null:
                self.null[u] = True
                self._rebuild()
            return
        if was_null:
            self.null[u] = False
            self.letter[u] = k
            self._rebuild()
            return
        if k != self.letter[u]:
            self.letter[u] = k
            P = self.pos(u)
            self.x[P] = k
            self.lm_sum = float(lm_let[k])

    def null_gains(self):
        """Score change from flagging each non-null, non-forced unit as null (all units at once, exact)."""
        cur = self.score()
        Nx, Sx = self.letter_stats()
        N0 = float(self.n[self.null].sum())
        S0 = float(self.nlogn[self.null].sum())
        g = np.full(self.U, -np.inf)
        for u in np.flatnonzero(~self.null & ~self.forced & (self.n > 0)):
            a = self.letter[u]
            Nb, Sb = Nx.copy(), Sx.copy()
            Nb[a] -= self.n[u]
            Sb[a] -= self.nlogn[u]
            if (N0 + self.n[u]) / self.N > self.null_cap:
                continue
            g[u] = lm_total(self.lm, self.x[self.cu != u]) + self.aux_terms(Nb, Sb, N0 + self.n[u], S0 + self.nlogn[u]) - cur
        return g

    def stepwise_nulls(self, max_rounds, T, deadline=None, trace=None, tag=""):
        """Forward selection: flag the single best-gain unit as null, re-anneal letters 3 sweeps, repeat."""
        for rd in range(max_rounds):
            g = self.null_gains()
            u = int(np.argmax(g))
            if not np.isfinite(g[u]) or g[u] <= 0:
                break
            self.null[u] = True
            self._rebuild()
            self.allow_null = False
            self.run(3, T, T, 1)
            if deadline is not None and time.time() > deadline:
                break
        if trace is not None:
            trace.append(f"{tag} stepwise nulls: {rd + 1} rounds, nulls {int(self.null.sum())}, score {self.score():.1f}")

    def run(self, sweeps, T0, T1, null_every, deadline=None, trace=None, tag=""):
        units = np.flatnonzero((self.n > 0) & ~self.forced)
        for sw in range(sweeps):
            frac = sw / max(1, sweeps - 1)
            T = T0 * (T1 / T0) ** frac if sw < sweeps - 2 else 0.0
            nm = self.allow_null and sw >= self.null_start * sweeps and (sw % null_every == 0)
            for u in self.rng.permutation(units):
                self.gibbs_unit(int(u), T, nm)
            if trace is not None and (sw % 10 == 0 or sw == sweeps - 1):
                trace.append(f"{tag} sweep {sw} T={T:.3f} score={self.score():.1f} nulls={int(self.null.sum())} M={self.M}")
            if deadline is not None and time.time() > deadline:
                if trace is not None:
                    trace.append(f"{tag} deadline hit at sweep {sw}")
                break
        return self.score()


def init_key(n, q, rng, mode):
    """mode 'rank': deficit-greedy by frequency; 'random': letters drawn from q independently."""
    U = len(n)
    if mode == "random":
        return rng.choice(A, size=U, p=q).astype(np.int64)
    order = np.argsort(-n, kind="stable")
    deficit = q * n.sum()
    letter = np.zeros(U, dtype=np.int64)
    for u in order:
        b = int(np.argmax(deficit))
        letter[u] = b
        deficit[b] -= n[u]
    return letter


def transparency(s, U):
    """Key-free null score per unit type: mean log2 [P_bigram(next | prev) / P_skip(next | prev)] over the unit's
    occurrences (prev/next = the neighbouring units). An inserted null leaves its neighbours adjacent in the
    plaintext, so its spanning pair looks like an ordinary bigram; a letter unit's spanning pair is a skip-gram."""
    a, b, c = s[:-2], s[1:-1], s[2:]
    big = np.bincount(s[:-1] * U + s[1:], minlength=U * U).reshape(U, U) + 0.1
    skp = np.bincount(a * U + c, minlength=U * U).reshape(U, U) + 0.1
    big /= big.sum(1, keepdims=True)
    skp /= skp.sum(1, keepdims=True)
    d = np.log2(big[a, c]) - np.log2(skp[a, c])
    return np.bincount(b, weights=d, minlength=U) / np.maximum(1, np.bincount(b, minlength=U))


NULL_INIT_K = (0, 8)
P1_ROBUST = None     # phase-1 table log2((1-e) P + e/A) with e = P1_ROBUST (None: plain table)
_ROB = {}


def robust(lm, e):
    key = (id(lm), e)
    if key not in _ROB:
        _ROB.clear()
        _ROB[key] = np.log2((1 - e) * np.exp2(lm.astype(np.float64)) + e / A).astype(np.float32)
    return _ROB[key]


STEPWISE = 0         # > 0: phase 2 = stepwise forward null selection with at most STEPWISE rounds
P1_NULL_PEN = None   # bits per occurrence charged to the null option during phase 1 (None: no null moves in phase 1)


def solve(s, lm, q, *, w_kl, allow_null, restarts, sweeps, T0, T1, seed, forced_null=None,
          deadline=None, trace=None, tag=""):
    """Best-of-restarts. Restart 0 starts from the frequency-deficit key, the others from letters drawn from q; the
    initial null flags are the top-k transparency units, k cycling over NULL_INIT_K (k = 0 when nulls are off).
    Phase 1: `sweeps` letter-only Gibbs sweeps, T geometric T0 -> T1. Phase 2 (null moves on): `sweeps` sweeps with
    letter and null options every sweep, T geometric 2 -> T1 (last two greedy). Returns (letter, null, score)."""
    rng = np.random.default_rng(seed)
    best = None
    for r in range(restarts):
        sv = Solver(s, robust(lm, P1_ROBUST) if P1_ROBUST else lm, q, w_kl, allow_null, rng, forced_null)
        letter = init_key(sv.n, q, rng, "rank" if r == 0 else "random")
        null0 = np.zeros(sv.U, dtype=bool)
        if allow_null:
            k = NULL_INIT_K[r % len(NULL_INIT_K)]
            tr = transparency(sv.s, sv.U)
            tr[sv.forced | (sv.n == 0)] = -np.inf
            null0[np.argsort(-tr)[:k]] = True
        sv.set_state(letter, null0)
        sv.allow_null = allow_null and P1_NULL_PEN is not None
        sv.null_start, sv.null_pen = 0.0, (P1_NULL_PEN or 0.0)
        sc = sv.run(sweeps, T0, T1, 1, deadline=deadline, trace=trace, tag=f"{tag} r{r} p1")
        if P1_ROBUST:
            sv.lm = lm
            sv.set_state(sv.letter, sv.null)
            sc = sv.score()
        if allow_null and STEPWISE:
            sv.stepwise_nulls(STEPWISE, 1.0, deadline=deadline, trace=trace, tag=f"{tag} r{r}")
            sv.allow_null = True
            sv.null_start, sv.null_pen = 0.0, 0.0
            sc = sv.run(4, 0.5, 0.5, 1, deadline=deadline, trace=trace, tag=f"{tag} r{r} p2")
        elif allow_null:
            sv.allow_null = True
            sv.null_start, sv.null_pen = 0.0, 0.0
            sc = sv.run(sweeps, 2.0, T1, 1, deadline=deadline, trace=trace, tag=f"{tag} r{r} p2")
        if trace is not None:
            trace.append(f"{tag} restart {r} final score {sc:.1f} nulls {int(sv.null.sum())}")
        if best is None or sc > best[2]:
            best = (sv.letter.copy(), sv.null.copy(), sc)
        if deadline is not None and time.time() > deadline:
            break
    return best
