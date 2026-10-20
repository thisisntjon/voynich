#!/usr/bin/env python3
"""s111_subject_vs_batch.py - does core vocabulary follow subject across quires, or the quire (batch) regardless of subject?

FROZEN DESIGN: .inventory/registers/DECISIONS.md row D-066 section (p) (approved by Jon 2026-10-18 15:48).  Power rule:
workflow/TRIANGULATION.md "Exclusions need power" (D-068).  Nothing below changes the statistic, null, power gate, calls or
thresholds; the implementation choices the frozen text leaves open are listed under IMPLEMENTATION and are frozen in the stub.

DATA (existing loaders only):
  pages   = data/translit/ZL3b_eva.meta.json (P* paragraph loci only; labels excluded) via
            s77.load_codicology_and_inventory() + s77.load_meta_pages() -> id, quire ($Q), section ($I), Davis hand
            (folio_evidence_inventory.tsv / $H, f115r and quire T -> Hand 3 as in s60/s77).
  subject = standard section from $I: H -> herbal, A/C/Z -> astro_cosmo, B -> balneo, P -> pharma, S -> recipes.
            $I = T (text-only pages) is none of the five subjects -> excluded.  Herbal illustration sub-type: not coded
            anywhere in the tree (grep: no illustration-type table), so herbal is one subject (frozen text: "where already coded").
  hands   = Davis Hands 1, 2, 3 only (frozen: "Hand 1 pairs, Hand 2 pairs, Hand 3 pairs"); Hands 4, 5 and '?' excluded.
  side    = folio side r/v from the page id (f<n>[rv]...); pairs only between pages of the same side.
  cores   = SlotSegmenter (scoreboard.metrics_new) fitted on all ZL3b P* tokens; core = segment(w)[1].  Sensitivity:
            identity (whole word) and Seg_Affix2 (s77.SegAffix2, fitted on all ZL3b P* tokens), same machinery.

PAGE TABLES (written from the loaders before any statistic; included pages = 185 of 207):
  subject x quire x hand page counts (hand, subject, quire: pages):
    H1 herbal: A 15, B 14, C 16, D 12, E 8, F 8, G 12, O 6, Q 4      H1 pharma: O 6, S 10
    H2 astro_cosmo: N 3   H2 balneo: M 19   H2 herbal: D 4, E 8, F 4, G 4
    H3 herbal: H 1, Q 6   H3 recipes: H 2, T 23
  pages per hand: H1 111, H2 42, H3 32.  Minimum tokens on an included page: 44 (subsample size N_SUB below).
  page-pair cells (same folio side, within hand):
    H1: SS-SQ 265, SS-DQ 2000, DS-SQ 18, DS-DQ 742
    H2: SS-SQ 100, SS-DQ 72,   DS-SQ 0,  DS-DQ 249      (BATCH not estimable for Hand 2: no DS-SQ pair)
    H3: SS-SQ 127, SS-DQ 26,   DS-SQ 1,  DS-DQ 86
  The full per-page table (id quire hand subject side tokens) is printed at the top of every output.

STATISTIC (frozen): sim(i,j) = 1 - JSD_2(core distribution of i, of j), each page subsampled without replacement to
  N_SUB tokens, 20 subsamples, sim averaged over the 20 (subsample s of i vs subsample s of j).  Within hand h:
  SUBJECT_h = mean sim(SS-DQ) - mean sim(DS-DQ);  BATCH_h = mean sim(DS-SQ) - mean sim(DS-DQ).
  Combined = inverse-variance weighted mean over the hands where the contrast is estimable (variance = page-bootstrap
  variance of the hand's contrast; weights fixed from the observed data and reused in the null).
NULL (frozen): SUBJECT - subject labels permuted among pages within each (hand, quire); BATCH - quire labels permuted
  among pages within each (hand, subject); 10,000 each; exact p = (1 + #{null >= obs}) / (1 + 10,000); the combined null
  applies the same per-hand permutations jointly with the fixed weights.
RATIO: SUBJECT/BATCH, bootstrap 95% percentile CI over pages (pages resampled with replacement within hand, pair weight
  = product of page multiplicities, self-pairs dropped), N_BOOT = 2,000; replicates with an empty cell are dropped and counted.
POWER GATE (frozen, D-068): planted texts from the real core distributions: (a) pure subject vocabulary, (b) pure batch
  vocabulary.  Page j of hand h: tokens ~ Multinomial(n_j, (1-lam) g_h + lam t_k), g_h = the hand's real pooled core
  distribution, t_k = g_all * exp(z_k) normalised, z_k ~ N(0,1) per core, one vector per subject (a) or per quire (b),
  shared across hands; real page metadata and token counts kept.  Effect scale ("observed effect scale of a section-vs-
  quire difference"): lam is set so that the planted text's pooled-group excess divergence G equals the REAL G for
  section labels (a) or quire labels (b).  G(labels) = for each hand, groups with >= M_CAL pooled tokens, mean pairwise
  JSD between groups' pooled distributions subsampled to M_CAL tokens (R_CAL subsamples) minus the same with labels
  permuted among the hand's pages (P_CAL permutations); averaged over hands weighted by group-pair count.  G is a
  descriptive of pooled group distributions, not SUBJECT/BATCH; it is computed in the fixture before the freeze because
  the frozen power rule requires an observed scale.  lam chosen on grid LAM_GRID by |G_planted - G_real| (seed CAL_SEED).
  15 resamples per condition (fresh z and multinomial draws).  PASS for a condition: right contrast p < 0.01 on >= 10/15
  AND the other contrast p >= 0.01 on >= 10/15.  Gate evaluated combined (binding) and per hand (reported).
CALLS (frozen): SUBJECT_REAL = SUBJECT > 0 at p < 0.01; BATCH_REAL = BATCH > 0 at p < 0.01 (combined, primary = slot cores).
VERDICT (frozen): content-led if SUBJECT_REAL and ratio CI above 1; batch-led if BATCH_REAL and CI below 1; mixed if both
  real and CI spans 1; none if neither.  (Combinations outside these four print 'unclassified'.)  If the combined power
  gate fails, the line reads 'VERDICT: HOLD (power gate failed ...)' and still names the frozen-rule outcome (D-068).
COMPUTE: 1 worker, BelowNormal, BLAS threads 1; free RAM >= 4 GB checked before heavy steps.

Run:  python -I s111_subject_vs_batch.py --fixture   (pre-freeze; writes runs/s111/fixture_<stamp>.txt)
      python -I s111_subject_vs_batch.py --real      (requires stub match; writes results_s111.txt; never overwrites)
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"

import hashlib  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import Counter, defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

import s77_deconfounded_scribe_and_comma_ablation_loqo as S77  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s111_subject_vs_batch.py"
STUB = ROOT / "s111_subject_vs_batch.prereg.sha256"
OUT = ROOT / "results_s111.txt"
FIXDIR = ROOT / "runs" / "s111"
DATA_FILES = ["data/translit/ZL3b_eva.meta.json", "data/folio_evidence_inventory.tsv", "data/ZL3b-n.txt"]

SEED = 20261018
SUBJ = {"H": "herbal", "A": "astro_cosmo", "C": "astro_cosmo", "Z": "astro_cosmo", "B": "balneo", "P": "pharma",
        "S": "recipes"}
HANDS = ("1", "2", "3")
N_SUBSAMP = 20
N_PERM = 10_000
N_BOOT = 2_000
ALPHA = 0.01
N_RES = 15
N_NEED = 10
M_CAL = 400
R_CAL = 10
P_CAL = 10
LAM_GRID = [round(0.02 * i, 2) for i in range(0, 41)]
CAL_SEED = 777
MIN_FREE_GB = 4.0

log_lines: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log_lines.append(s)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return time.strftime("%Y-%m-%d %H:%M:%S") + " (time.strftime)"


def below_normal():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.GetCurrentProcess.restype = ctypes.c_void_p
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        return bool(k.SetPriorityClass(k.GetCurrentProcess(), 0x00004000))
    except Exception:  # noqa: BLE001
        return False


def free_gb():
    try:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MS()
        m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPhys / 2 ** 30
    except Exception:  # noqa: BLE001
        return float("nan")


def wait_ram(tag):
    while True:
        g = free_gb()
        if not (g < MIN_FREE_GB):
            return
        print(f"[{tag}] free RAM {g:.2f} GB < {MIN_FREE_GB}; waiting 60 s", flush=True)
        time.sleep(60)


def local_modules():
    out = []
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f:
            continue
        p = Path(f).resolve()
        try:
            rel = p.relative_to(ROOT)
        except ValueError:
            continue
        if p.suffix == ".py" and p.exists():
            out.append(rel.as_posix())
    return sorted(set(out) | {SELF.name})


def stub_files():
    return local_modules() + list(DATA_FILES)


def stub_match():
    if not STUB.exists():
        return "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    missing = [m for m in stub_files() if m not in want]
    ok = bool(want) and not bad and not missing
    return "True" if ok else f"False (mismatch: {', '.join(bad) or '-'}; not in stub: {', '.join(missing) or '-'})"


# ============================================================================ data
def side(pid):
    m = re.match(r"^f\d+([rv])", pid)
    return m.group(1) if m else "?"


def load():
    inv = S77.load_codicology_and_inventory()
    pages = S77.load_meta_pages("ZL3b_eva.meta.json", inv)
    all_tokens = [w for p in pages for ln in p["lines"] for w in ln]
    inc = []
    for p in pages:
        if p["hand"] not in HANDS or p["section"] not in SUBJ:
            continue
        toks = [w for ln in p["lines"] for w in ln]
        inc.append(dict(id=p["id"], quire=p["quire"], hand=p["hand"], subject=SUBJ[p["section"]], side=side(p["id"]),
                        tokens=toks))
    return pages, all_tokens, inc


def tables(pages, inc):
    emit(f"pages loaded {len(pages)}; included {len(inc)} (Hands 1-3, five subjects)")
    emit("per-page table: id quire hand subject side tokens")
    for p in inc:
        emit(f"  {p['id']:8s} {p['quire']:2s} H{p['hand']} {p['subject']:12s} {p['side']} {len(p['tokens'])}")
    cnt = Counter((p["hand"], p["subject"], p["quire"]) for p in inc)
    emit("subject x quire x hand page counts:")
    for k in sorted(cnt):
        emit(f"  H{k[0]} {k[1]:12s} {k[2]:2s} {cnt[k]}")
    for h in HANDS:
        P = [p for p in inc if p["hand"] == h]
        cc = Counter()
        for i in range(len(P)):
            for j in range(i + 1, len(P)):
                if P[i]["side"] != P[j]["side"]:
                    continue
                ss = P[i]["subject"] == P[j]["subject"]
                sq = P[i]["quire"] == P[j]["quire"]
                cc[("SS" if ss else "DS") + "-" + ("SQ" if sq else "DQ")] += 1
        emit(f"  pair cells H{h} (pages {len(P)}): " + ", ".join(f"{k} {cc.get(k, 0)}" for k in ("SS-SQ", "SS-DQ", "DS-SQ", "DS-DQ")))
    emit(f"min tokens on an included page: {min(len(p['tokens']) for p in inc)}")


def encode(inc, rep, slot, aff2):
    def f(w):
        if rep == "slot":
            return slot.segment(w)[1]
        if rep == "affix2":
            return aff2.segment(w)[1]
        return w
    seqs = [[f(w) for w in p["tokens"]] for p in inc]
    vocab = sorted({c for s in seqs for c in s})
    ix = {c: i for i, c in enumerate(vocab)}
    return [np.array([ix[c] for c in s], dtype=np.int64) for s in seqs], len(vocab)


# ============================================================================ similarity
def xlogx(a):
    out = np.zeros_like(a)
    m = a > 0
    out[m] = a[m] * np.log2(a[m])
    return out


def subsample_counts(seqs, V, n_sub, rng):
    """(n_pages, N_SUBSAMP, V) normalised distributions of N_SUBSAMP subsamples of n_sub tokens each."""
    D = np.zeros((len(seqs), N_SUBSAMP, V), dtype=np.float64)
    for i, s in enumerate(seqs):
        for r in range(N_SUBSAMP):
            pick = rng.choice(len(s), size=n_sub, replace=False)
            np.add.at(D[i, r], s[pick], 1.0)
    D /= n_sub
    return D


def pair_sims(D, I, J):
    """mean over subsamples of 1 - JSD_2 between D[I, r] and D[J, r]."""
    sims = np.zeros(len(I))
    for r in range(N_SUBSAMP):
        P = D[I, r]
        Q = D[J, r]
        M = 0.5 * (P + Q)
        jsd = 0.5 * (xlogx(P).sum(1) + xlogx(Q).sum(1)) - xlogx(M).sum(1)
        sims += 1.0 - jsd
    return sims / N_SUBSAMP


class HandData:
    def __init__(self, h, idx, inc, D):
        self.h = h
        self.idx = np.array(idx)
        n = len(idx)
        I, J = [], []
        for a in range(n):
            for b in range(a + 1, n):
                if inc[idx[a]]["side"] == inc[idx[b]]["side"]:
                    I.append(a)
                    J.append(b)
        self.I = np.array(I, dtype=np.int64)
        self.J = np.array(J, dtype=np.int64)
        self.sim = pair_sims(D, self.idx[self.I], self.idx[self.J]) if len(I) else np.zeros(0)
        subs = sorted({inc[i]["subject"] for i in idx})
        qs = sorted({inc[i]["quire"] for i in idx})
        self.subj = np.array([subs.index(inc[i]["subject"]) for i in idx])
        self.quire = np.array([qs.index(inc[i]["quire"]) for i in idx])
        self.n = n


def contrasts(ss, sq, sim, w=None):
    """ss, sq: (..., npairs) bool; returns SUBJECT, BATCH (nan if a cell is empty)."""
    if w is None:
        w = np.ones(sim.shape[-1])
    def cm(mask):
        ww = mask * w
        den = ww.sum(-1)
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(den > 0, (ww * sim).sum(-1) / np.where(den > 0, den, 1), np.nan)
    ssdq = cm(ss & ~sq)
    dsdq = cm(~ss & ~sq)
    dssq = cm(~ss & sq)
    return ssdq - dsdq, dssq - dsdq


def perm_labels(lab, groups, B, rng):
    """B permutations of lab, shuffling within each group id."""
    out = np.tile(lab, (B, 1))
    for g in np.unique(groups):
        ii = np.where(groups == g)[0]
        if len(ii) < 2:
            continue
        order = np.argsort(rng.random((B, len(ii))), axis=1)
        out[:, ii] = lab[ii][order]
    return out


def analyse(hds, rng, n_perm=N_PERM, n_boot=N_BOOT, do_boot=True):
    """hds: list of HandData. Returns per-hand and combined stats."""
    res = {}
    for hd in hds:
        ss = hd.subj[hd.I] == hd.subj[hd.J]
        sq = hd.quire[hd.I] == hd.quire[hd.J]
        S, Bt = contrasts(ss, sq, hd.sim)
        r = dict(S=float(S), B=float(Bt), n=hd.n, npairs=len(hd.sim))
        # null SUBJECT: permute subject within quire
        ps = perm_labels(hd.subj, hd.quire, n_perm, rng)
        ss_p = ps[:, hd.I] == ps[:, hd.J]
        r["S_null"], _ = contrasts(ss_p, np.broadcast_to(sq, ss_p.shape), hd.sim)
        # null BATCH: permute quire within subject
        pq = perm_labels(hd.quire, hd.subj, n_perm, rng)
        sq_p = pq[:, hd.I] == pq[:, hd.J]
        _, r["B_null"] = contrasts(np.broadcast_to(ss, sq_p.shape), sq_p, hd.sim)
        r["pS"] = pval(r["S"], r["S_null"])
        r["pB"] = pval(r["B"], r["B_null"])
        if do_boot:
            cnt = np.stack([np.bincount(rng.integers(0, hd.n, hd.n), minlength=hd.n) for _ in range(n_boot)])
            w = cnt[:, hd.I] * cnt[:, hd.J]
            bS, bB = contrasts(np.broadcast_to(ss, w.shape), np.broadcast_to(sq, w.shape), hd.sim, w.astype(float))
            r["bS"], r["bB"] = bS, bB
            r["varS"] = float(np.nanvar(bS)) if np.isfinite(r["S"]) and np.isfinite(bS).sum() > 10 else np.nan
            r["varB"] = float(np.nanvar(bB)) if np.isfinite(r["B"]) and np.isfinite(bB).sum() > 10 else np.nan
        res[hd.h] = r
    if do_boot:
        comb = {}
        for key in ("S", "B"):
            hs = [h for h in res if np.isfinite(res[h][key]) and np.isfinite(res[h]["var" + key]) and res[h]["var" + key] > 0]
            if not hs:
                comb[key] = np.nan
                comb[key + "_w"] = {}
                comb["p" + key] = 1.0
                comb["b" + key] = np.full(n_boot, np.nan)
                continue
            wts = {h: 1.0 / res[h]["var" + key] for h in hs}
            W = sum(wts.values())
            comb[key + "_w"] = {h: wts[h] / W for h in hs}
            comb[key] = sum(comb[key + "_w"][h] * res[h][key] for h in hs)
            nul = sum(comb[key + "_w"][h] * res[h][key + "_null"] for h in hs)
            comb["p" + key] = pval(comb[key], nul)
            comb["b" + key] = sum(comb[key + "_w"][h] * res[h]["b" + key] for h in hs)
        res["comb"] = comb
    return res


def pval(obs, null):
    if not np.isfinite(obs):
        return float("nan")
    null = np.asarray(null)
    null = null[np.isfinite(null)]
    return float((1 + np.sum(null >= obs - 1e-12)) / (1 + len(null)))


def ratio_ci(bS, bB):
    ok = np.isfinite(bS) & np.isfinite(bB) & (bB != 0)
    r = bS[ok] / bB[ok]
    if len(r) < 10:
        return (float("nan"), float("nan")), int((~ok).sum())
    return (float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))), int((~ok).sum())


# ============================================================================ planted fixture
def build_hds(inc, D):
    return [HandData(h, [i for i, p in enumerate(inc) if p["hand"] == h], inc, D) for h in HANDS]


def group_excess(seqs, V, inc, labels, rng):
    """G(labels): pooled-group mean pairwise JSD minus page-label-permuted, averaged over hands (weights = group pairs)."""
    tot, wsum = 0.0, 0
    for h in HANDS:
        idx = [i for i, p in enumerate(inc) if p["hand"] == h]
        lab = np.array([labels[i] for i in idx])

        def gjsd(lb):
            pools = defaultdict(list)
            for k, i in zip(lb, idx):
                pools[k].append(seqs[i])
            pools = [np.concatenate(v) for v in pools.values()]
            pools = [v for v in pools if len(v) >= M_CAL]
            if len(pools) < 2:
                return np.nan, 0
            vals = []
            for _ in range(R_CAL):
                Ds = []
                for v in pools:
                    c = np.bincount(v[rng.choice(len(v), M_CAL, replace=False)], minlength=V) / M_CAL
                    Ds.append(c)
                Ds = np.array(Ds)
                a, b = np.triu_indices(len(Ds), 1)
                M = 0.5 * (Ds[a] + Ds[b])
                vals.append(np.mean(0.5 * (xlogx(Ds[a]).sum(1) + xlogx(Ds[b]).sum(1)) - xlogx(M).sum(1)))
            return float(np.mean(vals)), len(a)

        real, npair = gjsd(lab)
        if not np.isfinite(real):
            continue
        perm = [gjsd(rng.permutation(lab))[0] for _ in range(P_CAL)]
        perm = [x for x in perm if np.isfinite(x)]
        tot += npair * (real - float(np.mean(perm)))
        wsum += npair
    return tot / wsum if wsum else float("nan")


def planted(inc, seqs_real, V, kind, lam, rng):
    labels = [p["subject"] if kind == "subject" else p["quire"] for p in inc]
    g_all = np.bincount(np.concatenate(seqs_real), minlength=V).astype(float)
    g_all /= g_all.sum()
    g_h = {}
    for h in HANDS:
        c = np.bincount(np.concatenate([s for s, p in zip(seqs_real, inc) if p["hand"] == h]), minlength=V).astype(float)
        g_h[h] = c / c.sum()
    topics = {}
    for k in sorted(set(labels)):
        t = g_all * np.exp(rng.standard_normal(V))
        topics[k] = t / t.sum()
    out = []
    for s, p, k in zip(seqs_real, inc, labels):
        pr = (1 - lam) * g_h[p["hand"]] + lam * topics[k]
        c = rng.multinomial(len(s), pr / pr.sum())
        out.append(np.repeat(np.arange(V), c))
    return out, labels


def run_fixture(inc, seqs, V, n_sub):
    emit("\n=== POWER FIXTURE (D-068): planted pure-subject and pure-batch texts from the real slot-core distributions ===")
    rng = np.random.default_rng(CAL_SEED)
    tgt = {"subject": group_excess(seqs, V, inc, [p["subject"] for p in inc], rng),
           "batch": group_excess(seqs, V, inc, [p["quire"] for p in inc], rng)}
    emit(f"effect scale: real G(section labels) = {tgt['subject']:.5f}; real G(quire labels) = {tgt['batch']:.5f} "
         f"(pooled-group JSD excess over page-permuted labels; M_CAL {M_CAL}, R_CAL {R_CAL}, P_CAL {P_CAL})")
    lam = {}
    for kind in ("subject", "batch"):
        best = None
        for L in LAM_GRID:
            r2 = np.random.default_rng([CAL_SEED, int(L * 100)])
            ps, lb = planted(inc, seqs, V, kind, L, r2)
            G = group_excess(ps, V, inc, lb, r2)
            if best is None or abs(G - tgt[kind]) < best[1]:
                best = (L, abs(G - tgt[kind]), G)
        lam[kind] = best[0]
        emit(f"  {kind}: lam = {best[0]:.2f} (planted G {best[2]:.5f} vs target {tgt[kind]:.5f})")
    gate = {}
    for kind in ("subject", "batch"):
        right, other = ("S", "B") if kind == "subject" else ("B", "S")
        rows = []
        for t in range(N_RES):
            wait_ram("fixture")
            r2 = np.random.default_rng([SEED, 111, 0 if kind == "subject" else 1, t])
            ps, _ = planted(inc, seqs, V, kind, lam[kind], r2)
            D = subsample_counts(ps, V, n_sub, r2)
            res = analyse(build_hds(inc, D), r2)
            rows.append(res)
            c = res["comb"]
            emit(f"  {kind} resample {t:2d}: combined SUBJECT {c['S']:+.5f} p {c['pS']:.4f} | BATCH {c['B']:+.5f} p {c['pB']:.4f} | "
                 + " ".join(f"H{h} S {res[h]['S']:+.4f} p {res[h]['pS']:.3f} B {res[h]['B']:+.4f} p {res[h]['pB']:.3f}" for h in HANDS))
        for scope in ["comb"] + list(HANDS):
            get = (lambda r, k: r["comb"]["p" + k]) if scope == "comb" else (lambda r, k, s=scope: r[s]["p" + k])
            hit = sum(1 for r in rows if np.isfinite(get(r, right)) and get(r, right) < ALPHA)
            quiet = sum(1 for r in rows if not (np.isfinite(get(r, other)) and get(r, other) < ALPHA))
            ok = hit >= N_NEED and quiet >= N_NEED
            gate[(kind, scope)] = (hit, quiet, ok)
            emit(f"  GATE {kind:7s} {'combined' if scope == 'comb' else 'H' + scope:8s}: right contrast ({right}) p<{ALPHA} on "
                 f"{hit}/{N_RES}; other ({other}) quiet on {quiet}/{N_RES} -> {'PASS' if ok else 'FAIL'}")
    passed = gate[("subject", "comb")][2] and gate[("batch", "comb")][2]
    emit(f"POWER_GATE combined: {'PASS' if passed else 'FAIL'} (pure-subject {'PASS' if gate[('subject', 'comb')][2] else 'FAIL'}, "
         f"pure-batch {'PASS' if gate[('batch', 'comb')][2] else 'FAIL'})")
    return passed, gate, lam, tgt


# ============================================================================ real
def report(rep, res, gate_pass, primary):
    c = res["comb"]
    emit(f"\n--- representation: {rep} ---")
    for h in HANDS:
        r = res[h]
        ci, nd = ratio_ci(r["bS"], r["bB"])
        rt = r["S"] / r["B"] if np.isfinite(r["B"]) and r["B"] != 0 else float("nan")
        emit(f"  H{h} (pages {r['n']}, pairs {r['npairs']}): SUBJECT {r['S']:+.5f} p {r['pS']:.4f} | BATCH {r['B']:+.5f} p {r['pB']:.4f} | "
             f"ratio {rt:+.3f} CI [{ci[0]:+.3f}, {ci[1]:+.3f}] (boot dropped {nd})")
    ci, nd = ratio_ci(c["bS"], c["bB"])
    rt = c["S"] / c["B"] if np.isfinite(c["B"]) and c["B"] != 0 else float("nan")
    emit(f"  combined weights SUBJECT {c['S_w']} BATCH {c['B_w']}")
    emit(f"  combined: SUBJECT {c['S']:+.5f} p {c['pS']:.4f} | BATCH {c['B']:+.5f} p {c['pB']:.4f} | ratio {rt:+.3f} "
         f"95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}] (boot dropped {nd})")
    s_real = bool(np.isfinite(c["S"]) and c["S"] > 0 and c["pS"] < ALPHA)
    b_real = bool(np.isfinite(c["B"]) and c["B"] > 0 and c["pB"] < ALPHA)
    lo, hi = ci
    if s_real and b_real:
        v = "content-led" if lo > 1 else ("batch-led" if hi < 1 else "mixed")
    elif s_real:
        v = "content-led" if lo > 1 else "unclassified"
    elif b_real:
        v = "batch-led" if hi < 1 else "unclassified"
    else:
        v = "none"
    tag = "" if primary else f"[{rep}] "
    emit(f"{tag}SUBJECT_REAL = {s_real} (SUBJECT {c['S']:+.5f}, p {c['pS']:.4f})")
    emit(f"{tag}BATCH_REAL = {b_real} (BATCH {c['B']:+.5f}, p {c['pB']:.4f})")
    emit(f"{tag}RATIO SUBJECT/BATCH = {rt:+.3f}, bootstrap 95% CI [{lo:+.3f}, {hi:+.3f}]")
    if primary:
        emit(f"CALL: SUBJECT_REAL={s_real} BATCH_REAL={b_real} RATIO={rt:+.3f} CI=[{lo:+.3f},{hi:+.3f}]")
        if gate_pass:
            emit(f"VERDICT: {v}")
        else:
            emit(f"VERDICT: HOLD (power gate failed, D-068; frozen-rule outcome would be '{v}')")
    else:
        emit(f"[{rep}] sensitivity outcome by the frozen rule: {v}")
    return v


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in ("--fixture", "--real"):
        sys.exit("usage: --fixture | --real")
    if OUT.exists():
        sys.exit(f"{OUT.name} exists; never overwritten")
    bn = below_normal()
    t0 = time.time()
    emit(f"S111 subject vs batch (D-066 (p)); mode {mode}; started {clock()}; BelowNormal {bn}; free RAM {free_gb():.1f} GB")
    pages, all_tokens, inc = load()
    slot = SlotSegmenter(all_tokens)
    aff2 = S77.SegAffix2(all_tokens)
    emit(f"stub match: {stub_match()}")
    if mode == "--real" and stub_match() != "True":
        sys.exit("stub does not match; refusing real run")
    tables(pages, inc)
    n_sub = min(len(p["tokens"]) for p in inc)
    emit(f"N_SUB {n_sub}; subsamples {N_SUBSAMP}; perms {N_PERM}; boots {N_BOOT}; alpha {ALPHA}; gate {N_NEED}/{N_RES}; seed {SEED}")
    seqs, V = encode(inc, "slot", slot, aff2)
    emit(f"slot cores: {V} types")
    gate_pass, gate, lam, tgt = run_fixture(inc, seqs, V, n_sub)
    emit(f"fixture done {clock()}; elapsed {time.time() - t0:.0f} s")
    if mode == "--fixture":
        FIXDIR.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        fp = FIXDIR / f"fixture_{stamp}.txt"
        if fp.exists():
            sys.exit("fixture file exists")
        fp.write_text("\n".join(log_lines) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {fp}")
        return
    emit("\n=== REAL DATA (primary: slot cores; sensitivity: identity, affix2) ===")
    for rep in ("slot", "identity", "affix2"):
        wait_ram("real")
        sq, Vr = encode(inc, rep, slot, aff2)
        rng = np.random.default_rng([SEED, 999, ("slot", "identity", "affix2").index(rep)])
        D = subsample_counts(sq, Vr, n_sub, rng)
        res = analyse(build_hds(inc, D), rng)
        emit(f"[{rep}] types {Vr}")
        if rep == "slot":
            primary_res = res
            continue
        report(rep, res, gate_pass, primary=False)
    emit("\n=== PRIMARY (slot cores) ===")
    emit(f"POWER_GATE combined: {'PASS' if gate_pass else 'FAIL'}")
    report("slot", primary_res, gate_pass, primary=True)
    emit(f"finished {clock()}; elapsed {time.time() - t0:.0f} s; stub match at end: {stub_match()}")
    if OUT.exists():
        sys.exit("results file appeared during run; not overwriting")
    OUT.write_text("\n".join(log_lines) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
