"""s34 — Morphological Slot, Operator & Label Coupling Investigator:
1. Part 1: 3x3 Directed Inter-Word Slot Coupling Matrix ([P1, C1, S1] -> [P2, C2, S2])
   & Within-Word Slot Mutual Information Hierarchy (MI(P;C), MI(C;S), MI(P;S)).
2. Part 2 (OPEN row O-027): Prefix/Core/Suffix Section Operator Test within Hand 1 (H vs P),
   Hand 2 (B vs H vs T), and Hand 2/3 (B vs S vs H) under Quire-Block (exact 55 Hand-1 splits
   / 500 perms) and Bifolio-Block (500 perms) nulls, both at Token-Level Information Theory
   (MI, symmetric NMI, Uncertainty Coefficient U(Sec|F), and exact Conditional MI(Sec; P|C)
   and MI(Sec; S|C) on top-50 shared cores) and Chunk-Level B5/C1/P1 NMF Topic NMI.
3. Part 3: Same-Folio Label <-> Paragraph Body-Text Vocabulary Coupling (1,000 within-(section, hand)
   and within-section-group folio permutations) across (i) exact word-type overlap & TF-IDF cosine,
   (ii) SlotSegmenter core-stem overlap & TF-IDF cosine, and (iii) 1-2 char prefix-stripped stem
   overlap (stripping o-/y-/d-/s- and s29 full affix-stripped stem), broken down by section
   (Herbal, Pharma, Bio, Cosmo/Astro) plus all-non-label body sensitivity.

All three parts run across ZL3b (data/ZL3b-n.txt), RF1b (RF1b-e.txt), and IT2a (IT2a-n.txt).

PRE-REGISTRATION (frozen in s34_morphology_syntax_geography.prereg.sha256 before execution):
  - Seed: 20261017
  - Part 1: 200 within-line word-order shuffles per (transliteration, Currier subset in {ALL, A, B})
    for all 9 directed inter-word slot pairs; 200 independent token-slot shuffles for within-word
    MI(P;C), MI(C;S), MI(P;S).
  - Part 2 (O-027): Exact 55 Hand-1 quire splits (and exact enumeration when distinct assignments <= 500,
    else 500 Monte Carlo block permutations) + 500 physical bifolio ($Q|$B) permutations across
    (a) Whole word W, (b) Prefix P, (c) Core C, (d) Suffix S, (e1) P|C on top-50 shared cores,
    (e2) S|C on top-50 shared cores.
  - Part 3: 1,000 within-(section, hand) and within-section-group folio permutations across all
    folios containing both L* label tokens and P* paragraph body tokens (and sensitivity across
    all folios with L* and any non-L* body text), broken down by Herbal (H), Pharma (P), Bio (B),
    and Cosmo/Astro (C/A/T/Z).

Run:    python -I s34_morphology_syntax_geography.py
Writes: results_s34_morphology_syntax_geography.txt only. No other file is modified.
"""
from __future__ import annotations

import hashlib
import math
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import normalized_mutual_info_score as sk_nmi

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

import b5_nmf_topics as b5  # noqa: E402
import c1_quire_null as C1  # noqa: E402
import p1_bifolio_null as P1  # noqa: E402
import s29_q1_label_controls as s29  # noqa: E402
import scoreboard.metrics_new as mn  # noqa: E402
import vparse  # noqa: E402

SELF = ROOT / "s34_morphology_syntax_geography.py"
STUB = ROOT / "s34_morphology_syntax_geography.prereg.sha256"
OUT = ROOT / "results_s34_morphology_syntax_geography.txt"

SEED = 20261017
N_SHUF_P1 = 200
N_PERM_P2 = 500
N_PERM_P3 = 1000

TRANSLITS = [
    ("ZL3b", ROOT / "data" / "ZL3b-n.txt"),
    ("RF1b", ROOT / "data" / "external" / "voynich-nu-ivtff" / "RF1b-e.txt"),
    ("IT2a", ROOT / "data" / "external" / "voynich-nu-ivtff" / "IT2a-n.txt"),
]

log: list[str] = []


def emit(s: str = "") -> None:
    print(s, flush=True)
    log.append(s)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now)"


def stub_match() -> str:
    if not STUB.exists():
        return "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = ln.split()
        if len(parts) >= 2:
            want[parts[1].lstrip("*")] = parts[0]
    got = sha256(SELF)
    expected = want.get(SELF.name)
    if expected is None:
        return f"UNLISTED (self={got})"
    return f"MATCH ({got})" if expected == got else f"MISMATCH (want={expected}, got={got})"


# ---------------------------------------------------------------------------
# Fast Plug-in Mutual Information Helpers
# ---------------------------------------------------------------------------
N_MAX_PRECOMP = 50000
CLOG2 = np.array([0.0] + [k * math.log2(k) for k in range(1, N_MAX_PRECOMP)], dtype=np.float64)


def fast_mi_1d(x: np.ndarray, y: np.ndarray, vx: int, vy: int) -> tuple[float, float, float]:
    """Return (MI(X;Y), H(X), H(Y)) in bits using integer arrays x in [0,vx), y in [0,vy)."""
    n = len(x)
    if n == 0:
        return 0.0, 0.0, 0.0
    logn = math.log2(n)
    cx = np.bincount(x, minlength=vx)
    cy = np.bincount(y, minlength=vy)
    sx = CLOG2[cx].sum()
    sy = CLOG2[cy].sum()
    hx = logn - sx / n
    hy = logn - sy / n
    if vx * vy <= 120000:
        cxy = np.bincount(x * vy + y, minlength=vx * vy)
        sxy = CLOG2[cxy].sum()
    else:
        code = np.sort(x * vy + y)
        idx = np.flatnonzero(np.concatenate(([True], code[1:] != code[:-1], [True])))
        sxy = CLOG2[np.diff(idx)].sum()
    mi = logn + (sxy - sx - sy) / n
    return float(mi), float(hx), float(hy)


def batch_mi_from_A_M(A: np.ndarray, M: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute (MI, NMI_sym, U_sec_given_F, H_sec) for a batch of block permutations.
    A: shape (n_perm, S, B) indicator of block-to-section assignment.
    M: shape (B, V) count of feature f in block b.
    """
    J = A @ M  # (n_perm, S, V)
    n = float(M.sum())
    if n == 0:
        z = np.zeros(len(A))
        return z, z, z, z
    logn = math.log2(n)
    cs = J.sum(axis=2)  # (n_perm, S)
    cf = M.sum(axis=0)  # (V,)
    with np.errstate(divide="ignore", invalid="ignore"):
        hs = logn - np.where(cs > 0, cs * np.log2(np.maximum(cs, 1.0)), 0.0).sum(axis=1) / n
        hf = logn - float(np.where(cf > 0, cf * np.log2(np.maximum(cf, 1.0)), 0.0).sum()) / n
        hj = logn - np.where(J > 0, J * np.log2(np.maximum(J, 1.0)), 0.0).sum(axis=(1, 2)) / n
    mi = hs + hf - hj
    nmi_sym = np.where((hs + hf) > 0, 2.0 * mi / (hs + hf), 0.0)
    u_sec = np.where(hs > 0, mi / hs, 0.0)
    return mi, nmi_sym, u_sec, hs


# ---------------------------------------------------------------------------
# PART 1: 3x3 Directed Inter-Word Slot Coupling Matrix & Within-Word Hierarchy
# ---------------------------------------------------------------------------
SLOT_PAIRS_9 = [
    ("S1", "P2", "suffix->next_prefix boundary"),
    ("P1", "P2", "prefix->next_prefix run/agreement"),
    ("C1", "C2", "core->next_core stem transition"),
    ("S1", "S2", "suffix->next_suffix rhyme/agreement"),
    ("C1", "P2", "core->next_prefix coupling"),
    ("S1", "C2", "suffix->next_core coupling"),
    ("P1", "C2", "prefix->next_core coupling"),
    ("P1", "S2", "prefix->next_suffix coupling"),
    ("C1", "S2", "core->next_suffix coupling"),
]


def run_part1(tr_name: str, recs: list[dict]) -> dict:
    para = vparse.paragraph_text(recs)
    toks_all = [w for r in para for w in r["words"] if "?" not in w]
    seg = mn.SlotSegmenter(toks_all)

    vocab = sorted(set(toks_all))
    w2i = {w: i for i, w in enumerate(vocab)}
    ps = sorted({seg.segment(w)[0] for w in vocab})
    cs = sorted({seg.segment(w)[1] for w in vocab})
    ss = sorted({seg.segment(w)[2] for w in vocab})
    p2i = {x: i for i, x in enumerate(ps)}
    c2i = {x: i for i, x in enumerate(cs)}
    s2i = {x: i for i, x in enumerate(ss)}

    P_W = np.array([p2i[seg.segment(w)[0]] for w in vocab], dtype=np.int64)
    C_W = np.array([c2i[seg.segment(w)[1]] for w in vocab], dtype=np.int64)
    S_W = np.array([s2i[seg.segment(w)[2]] for w in vocab], dtype=np.int64)

    emit(f"\n--- PART 1 [{tr_name}]: 3x3 INTER-WORD SLOT COUPLING & WITHIN-WORD HIERARCHY ---")
    emit(
        f"  SlotSegmenter inventory on {tr_name}: {len(toks_all)} tokens, {len(vocab)} word types -> "
        f"{len(ps)} prefixes (incl. empty), {len(cs)} cores, {len(ss)} suffixes (incl. empty)"
    )
    if tr_name == "ZL3b":
        emit(f"  Prefixes ({len(ps)-1} non-empty): {[p for p in ps if p]}")
        emit(f"  Suffixes ({len(ss)-1} non-empty): {[s for s in ss if s]}")

    slot_map = {
        "P1": (P_W, len(ps), ps),
        "C1": (C_W, len(cs), cs),
        "S1": (S_W, len(ss), ss),
        "P2": (P_W, len(ps), ps),
        "C2": (C_W, len(cs), cs),
        "S2": (S_W, len(ss), ss),
    }

    res_p1 = {}
    for sub_label, lang_filter in [("ALL", None), ("Currier_A", "A"), ("Currier_B", "B")]:
        sub_recs = [r for r in para if (lang_filter is None or r["lang"] == lang_filter)]
        lines = [[w2i[w] for w in r["words"] if "?" not in w] for r in sub_recs]
        lines_2 = [ln for ln in lines if len(ln) >= 2]
        flat_w = np.array([w for ln in lines for w in ln], dtype=np.int64)
        n_tok = len(flat_w)
        n_pairs = sum(len(ln) - 1 for ln in lines_2)

        w1 = np.fromiter((w for ln in lines_2 for w in ln[:-1]), dtype=np.int64, count=n_pairs)
        w2 = np.fromiter((w for ln in lines_2 for w in ln[1:]), dtype=np.int64, count=n_pairs)

        # 1A. Within-word slot MIs against 200 frequency-weighted independent token-slot shuffles
        p_tok, c_tok, s_tok = P_W[flat_w], C_W[flat_w], S_W[flat_w]
        np_rng = np.random.default_rng(SEED)
        within_word = {}
        for w_pair, a_arr, b_arr, va, vb in [
            ("P;C", p_tok, c_tok, len(ps), len(cs)),
            ("C;S", c_tok, s_tok, len(cs), len(ss)),
            ("P;S", p_tok, s_tok, len(ps), len(ss)),
        ]:
            obs_mi, hx, hy = fast_mi_1d(a_arr, b_arr, va, vb)
            null_mis = [fast_mi_1d(a_arr, np_rng.permutation(b_arr), va, vb)[0] for _ in range(N_SHUF_P1)]
            m_null = float(np.mean(null_mis))
            sd_null = float(np.std(null_mis)) or 1e-9
            ex = obs_mi - m_null
            z = ex / sd_null
            nmi_sym = 2.0 * obs_mi / (hx + hy) if (hx + hy) > 0 else 0.0
            within_word[w_pair] = dict(obs=obs_mi, null=m_null, sd=sd_null, ex=ex, z=z, nmi=nmi_sym)

        # 1B. 9 directed inter-word slot pairs against 200 within-line shuffles
        obs_inter = {}
        h_inter = {}
        for k1, k2, _desc in SLOT_PAIRS_9:
            arr1, v1, _ = slot_map[k1]
            arr2, v2, _ = slot_map[k2]
            mi_val, hx, hy = fast_mi_1d(arr1[w1], arr2[w2], v1, v2)
            obs_inter[(k1, k2)] = mi_val
            h_inter[(k1, k2)] = (hx, hy)

        py_rng = random.Random(SEED)
        null_inter = {(k1, k2): [] for k1, k2, _ in SLOT_PAIRS_9}
        for _ in range(N_SHUF_P1):
            sh = [py_rng.sample(ln, len(ln)) for ln in lines_2]
            sw1 = np.fromiter((w for ln in sh for w in ln[:-1]), dtype=np.int64, count=n_pairs)
            sw2 = np.fromiter((w for ln in sh for w in ln[1:]), dtype=np.int64, count=n_pairs)
            s_cache = {
                "P1": P_W[sw1],
                "C1": C_W[sw1],
                "S1": S_W[sw1],
                "P2": P_W[sw2],
                "C2": C_W[sw2],
                "S2": S_W[sw2],
            }
            for k1, k2, _ in SLOT_PAIRS_9:
                _, v1, _ = slot_map[k1]
                _, v2, _ = slot_map[k2]
                null_inter[(k1, k2)].append(fast_mi_1d(s_cache[k1], s_cache[k2], v1, v2)[0])

        inter_stats = {}
        for k1, k2, desc in SLOT_PAIRS_9:
            o = obs_inter[(k1, k2)]
            vals = null_inter[(k1, k2)]
            m = float(np.mean(vals))
            sd = float(np.std(vals)) or 1e-9
            ex = o - m
            z = ex / sd
            hx, hy = h_inter[(k1, k2)]
            nmi_ex = 2.0 * ex / (hx + hy) if (hx + hy) > 0 else 0.0
            inter_stats[f"{k1}->{k2}"] = dict(obs=o, null=m, sd=sd, ex=ex, z=z, nmi_ex=nmi_ex, desc=desc)

        emit(f"\n  [{tr_name} | {sub_label}] tokens={n_tok}, lines(>=2w)={len(lines_2)}, adj_pairs={n_pairs}")
        emit("    Within-Word Slot Binding (vs 200 freq-weighted independent slot shuffles):")
        for wp in ("P;C", "C;S", "P;S"):
            d = within_word[wp]
            emit(
                f"      MI({wp:3s}): obs={d['obs']:.4f}  null={d['null']:.4f}+/-{d['sd']:.4f}  "
                f"excess={d['ex']:+.4f} bits  z={d['z']:+7.2f}  NMI_sym={d['nmi']:.4f}"
            )
        emit("    Inter-Word 3x3 Directed Slot Coupling (vs 200 within-line word-order shuffles):")
        emit(f"      {'Pair':8s} {'obs_MI':>8s} {'null_MI':>8s} {'null_SD':>8s} {'excess':>9s} {'z_score':>9s}  {'Role'}")
        for k1, k2, desc in SLOT_PAIRS_9:
            key = f"{k1}->{k2}"
            d = inter_stats[key]
            emit(
                f"      {key:8s} {d['obs']:8.4f} {d['null']:8.4f} {d['sd']:8.4f} "
                f"{d['ex']:+9.4f} {d['z']:+9.2f}  {desc}"
            )

        # Print 3x3 matrix grid of excess MI for quick visual reading
        emit("    3x3 Excess MI Grid (rows=[P1,C1,S1] in word_t, cols=[P2,C2,S2] in word_{t+1}):")
        emit(f"      {'':6s} {'-> P2':>10s} {'-> C2':>10s} {'-> S2':>10s}  {'RowSum_Ex':>10s}")
        for r_slot in ("P1", "C1", "S1"):
            e_p = inter_stats[f"{r_slot}->P2"]["ex"]
            e_c = inter_stats[f"{r_slot}->C2"]["ex"]
            e_s = inter_stats[f"{r_slot}->S2"]["ex"]
            emit(f"      {r_slot:6s} {e_p:+10.4f} {e_c:+10.4f} {e_s:+10.4f}  {e_p+e_c+e_s:+10.4f}")
        col_p = sum(inter_stats[f"{r}->P2"]["ex"] for r in ("P1", "C1", "S1"))
        col_c = sum(inter_stats[f"{r}->C2"]["ex"] for r in ("P1", "C1", "S1"))
        col_s = sum(inter_stats[f"{r}->S2"]["ex"] for r in ("P1", "C1", "S1"))
        emit(f"      {'ColSum':6s} {col_p:+10.4f} {col_c:+10.4f} {col_s:+10.4f}  {col_p+col_c+col_s:+10.4f}")

        # Top concrete S1->P2 and P1->P2 positive PMI transitions on ZL3b ALL
        if tr_name == "ZL3b" and sub_label == "ALL":
            s1_arr, p2_arr = S_W[w1], P_W[w2]
            c_s1 = Counter(s1_arr.tolist())
            c_p2 = Counter(p2_arr.tolist())
            c_sp = Counter(zip(s1_arr.tolist(), p2_arr.tolist()))
            contrib_sp = []
            for (si, pi), cnt in c_sp.items():
                if cnt >= 50:
                    pmi = math.log2((cnt * n_pairs) / (c_s1[si] * c_p2[pi]))
                    mi_term = (cnt / n_pairs) * pmi
                    contrib_sp.append((mi_term, cnt, pmi, ss[si] or "<0>", ps[pi] or "<0>"))
            contrib_sp.sort(reverse=True)
            emit("    Top S1->P2 concrete transitions by positive MI contribution (count >= 50):")
            for mi_t, cnt, pmi, s_str, p_str in contrib_sp[:8]:
                emit(f"      -{s_str:4s} -> {p_str:4s}- : count={cnt:4d}, PMI={pmi:+.3f} bits, dMI={mi_t:+.4f}")

        res_p1[sub_label] = dict(within_word=within_word, inter=inter_stats, n_tok=n_tok, n_pairs=n_pairs)
    return res_p1, seg


# ---------------------------------------------------------------------------
# PART 2: O-027 Prefix/Core/Suffix Section Operator Test
# ---------------------------------------------------------------------------
HAND_STRATA = [
    ("Hand1_H_vs_P", {"1"}, ("H", "P")),
    ("Hand2_B_vs_H_vs_T", {"2"}, ("B", "H", "T")),
    ("Hand23_B_vs_S_vs_H", {"2", "3"}, ("B", "S", "H")),
]


def run_part2(tr_name: str, recs: list[dict], seg: mn.SlotSegmenter, bmap: dict) -> dict:
    para = vparse.paragraph_text(recs)
    emit(f"\n--- PART 2 [{tr_name}]: O-027 PREFIX/CORE/SUFFIX SECTION OPERATOR TEST ---")

    by = defaultdict(list)
    for r in para:
        ws = [w for w in r["words"] if "?" not in w]
        if ws:
            by[r["page"]].append(dict(r, words=ws))
    ch_all = P1.chunks(by, bmap)

    res_p2 = {}
    for h_label, hands, secs in HAND_STRATA:
        sub_recs = [r for r in para if r["hand"] in hands and r["illus"] in secs]
        items = []
        for r in sub_recs:
            q, b = bmap.get(r["page"], (r["quire"], r["page"]))
            qblk = f"{r['quire']}|{r['illus']}"
            bfblk = f"{q}|{b}|{r['illus']}"
            for w in r["words"]:
                if "?" not in w:
                    p, c, s = seg.segment(w)
                    items.append((r["illus"], qblk, bfblk, w, p, c, s))

        # Identify top-50 shared cores across sections (must appear in >= 2 sections of this hand stratum)
        core_sec = defaultdict(Counter)
        for sec, _, _, _w, _p, c, _s in items:
            core_sec[c][sec] += 1
        shared_cores = sorted(
            [c for c, sc in core_sec.items() if len(sc) >= 2],
            key=lambda c: -sum(core_sec[c].values()),
        )
        top50_list = shared_cores[:50]
        top50_c = set(top50_list)
        sub50 = [x for x in items if x[5] in top50_c]

        s2i = {s: i for i, s in enumerate(secs)}
        emit(
            f"\n  [{tr_name} | {h_label}] tokens={len(items)}, shared_cores={len(shared_cores)}, "
            f"top50_shared_tokens={len(sub50)} ({100.0*len(sub50)/max(1,len(items)):.1f}%)"
        )

        # 2A. Token-Level Information-Theoretic Section MI / NMI / Conditional MI under Quire & Bifolio Block Nulls
        tok_results = {}
        for blk_type, b_idx in [("QuireBlk", 1), ("BifolioBlk", 2)]:
            blks = list(dict.fromkeys(x[b_idx] for x in items))
            b2i = {b: i for i, b in enumerate(blks)}
            blab = [s2i[b.split("|")[-1]] for b in blks]

            # Exact enumeration if distinct assignments <= N_PERM_P2 (includes exact 55 Hand-1 quire splits!)
            n_dist = 1
            rem = len(blab)
            for v in Counter(blab).values():
                n_dist *= math.comb(rem, v)
                rem -= v
            np_rng = np.random.default_rng(SEED)
            if n_dist <= N_PERM_P2:
                alls = C1.assignments(blab, np_rng)
                mode_str = f"exact_{len(alls)}"
            else:
                alls = [tuple(np_rng.permutation(blab)) for _ in range(N_PERM_P2)]
                mode_str = f"mc_{len(alls)}"

            alls_full = [tuple(blab)] + list(alls)
            A = np.zeros((len(alls_full), len(secs), len(blks)), dtype=np.float64)
            for pi, a in enumerate(alls_full):
                for bi, si in enumerate(a):
                    A[pi, si, bi] = 1.0

            blk_res = {}
            for feat_name, idx in [
                ("a_WholeWord(W)", 3),
                ("b_Prefix(P)", 4),
                ("c_Core(C)", 5),
                ("d_Suffix(S)", 6),
            ]:
                fvals = sorted({x[idx] for x in items})
                f2i = {f: i for i, f in enumerate(fvals)}
                M = np.zeros((len(blks), len(fvals)), dtype=np.float64)
                for x in items:
                    M[b2i[x[b_idx]], f2i[x[idx]]] += 1
                mi, nmi_s, u_s, _ = batch_mi_from_A_M(A, M)
                obs_mi, null_mi = float(mi[0]), mi[1:]
                obs_nmi, null_nmi = float(nmi_s[0]), nmi_s[1:]
                obs_u, null_u = float(u_s[0]), u_s[1:]
                m_mi, sd_mi = float(null_mi.mean()), float(null_mi.std()) or 1e-9
                ex_mi = obs_mi - m_mi
                z_mi = ex_mi / sd_mi
                p_mi = float(np.mean(null_mi >= obs_mi - 1e-12))
                blk_res[feat_name] = dict(
                    obs_mi=obs_mi,
                    null_mi=m_mi,
                    ex_mi=ex_mi,
                    z_mi=z_mi,
                    p_mi=p_mi,
                    obs_nmi=obs_nmi,
                    null_nmi=float(null_nmi.mean()),
                    obs_u=obs_u,
                    null_u=float(null_u.mean()),
                    n_types=len(fvals),
                )

            # Conditional MI(Sec; P | C) and MI(Sec; S | C) on top-50 shared cores via exact chain rule
            cvals = sorted(top50_c)
            c2i = {c: i for i, c in enumerate(cvals)}
            MC = np.zeros((len(blks), len(cvals)), dtype=np.float64)
            for x in sub50:
                MC[b2i[x[b_idx]], c2i[x[5]]] += 1
            mi_c, nmi_c, u_c, hs_c = batch_mi_from_A_M(A, MC)

            for cond_name, idx in [("e1_Prefix|Core50", 4), ("e2_Suffix|Core50", 6)]:
                cpvals = sorted({(x[5], x[idx]) for x in sub50})
                cp2i = {cp: i for i, cp in enumerate(cpvals)}
                MCP = np.zeros((len(blks), len(cpvals)), dtype=np.float64)
                for x in sub50:
                    MCP[b2i[x[b_idx]], cp2i[(x[5], x[idx])]] += 1
                mi_cp, nmi_cp, _, _ = batch_mi_from_A_M(A, MCP)
                mi_cond = mi_cp - mi_c
                h_sec_given_c = np.maximum(hs_c - mi_c, 1e-9)
                u_cond = mi_cond / h_sec_given_c
                obs_mi, null_mi = float(mi_cond[0]), mi_cond[1:]
                obs_u, null_u = float(u_cond[0]), u_cond[1:]
                obs_nmi, null_nmi = float(nmi_cp[0]), nmi_cp[1:]
                m_mi, sd_mi = float(null_mi.mean()), float(null_mi.std()) or 1e-9
                ex_mi = obs_mi - m_mi
                z_mi = ex_mi / sd_mi
                p_mi = float(np.mean(null_mi >= obs_mi - 1e-12))
                blk_res[cond_name] = dict(
                    obs_mi=obs_mi,
                    null_mi=m_mi,
                    ex_mi=ex_mi,
                    z_mi=z_mi,
                    p_mi=p_mi,
                    obs_nmi=obs_nmi,
                    null_nmi=float(null_nmi.mean()),
                    obs_u=obs_u,
                    null_u=float(null_u.mean()),
                    n_types=len(cpvals),
                )

            tok_results[blk_type] = dict(n_blocks=len(blks), mode=mode_str, features=blk_res)

        emit("    Token-Level Section Mutual Information & Block Permutation Nulls:")
        emit(
            f"      {'Feature':17s} | {'obs_MI':>7s} {'obs_NMI':>7s} {'U(S|F)':>7s} | "
            f"{'Quire_Ex':>9s} {'Quire_z':>8s} {'Quire_p':>8s} | "
            f"{'Bifolio_Ex':>10s} {'Bifol_z':>8s} {'Bifol_p':>8s}"
        )
        for fnm in [
            "a_WholeWord(W)",
            "b_Prefix(P)",
            "c_Core(C)",
            "d_Suffix(S)",
            "e1_Prefix|Core50",
            "e2_Suffix|Core50",
        ]:
            rq = tok_results["QuireBlk"]["features"][fnm]
            rb = tok_results["BifolioBlk"]["features"][fnm]
            emit(
                f"      {fnm:17s} | {rq['obs_mi']:7.4f} {rq['obs_nmi']:7.4f} {rq['obs_u']:7.4f} | "
                f"{rq['ex_mi']:+9.4f} {rq['z_mi']:+8.2f} {rq['p_mi']:8.4f} | "
                f"{rb['ex_mi']:+10.4f} {rb['z_mi']:+8.2f} {rb['p_mi']:8.4f}"
            )

        # 2B. Chunk-Level B5/C1/P1 40-Word NMF Cluster NMI(Section; Cluster(Feature))
        sub_ch = [c for c in ch_all if c["hand"] in hands and c["sec"] in secs]
        qblks_c = list(dict.fromkeys(f"{c['quire']}|{c['sec']}" for c in sub_ch))
        qlab_c = [b.split("|")[-1] for b in qblks_c]
        qix_c = [qblks_c.index(f"{c['quire']}|{c['sec']}") for c in sub_ch]
        n_dist_q = 1
        rem_q = len(qlab_c)
        for v in Counter(qlab_c).values():
            n_dist_q *= math.comb(rem_q, v)
            rem_q -= v
        rng_c = np.random.default_rng(SEED)
        qalls_c = (
            C1.assignments(qlab_c, rng_c)
            if n_dist_q <= N_PERM_P2
            else [tuple(rng_c.permutation(qlab_c)) for _ in range(N_PERM_P2)]
        )

        bfblks_c = list(dict.fromkeys(f"{c['bifolio']}|{c['sec']}" for c in sub_ch))
        bflab_c = [b.split("|")[-1] for b in bfblks_c]
        bfix_c = [bfblks_c.index(f"{c['bifolio']}|{c['sec']}") for c in sub_ch]
        bfalls_c = [tuple(rng_c.permutation(bflab_c)) for _ in range(N_PERM_P2)]

        nmf_results = {}
        emit(
            f"    Chunk-Level 40-Word NMF Topic NMI ({len(sub_ch)} chunks; "
            f"Quire B={len(qblks_c)} n={len(qalls_c)}, Bifolio B={len(bfblks_c)} n={len(bfalls_c)}):"
        )
        emit(
            f"      {'Feature':17s} | {'obs_NMI':>8s} | {'Q_null':>7s} {'Q_ex':>8s} {'Q_z':>7s} {'Q_p':>7s} | "
            f"{'BF_null':>7s} {'BF_ex':>8s} {'BF_z':>7s} {'BF_p':>7s}"
        )
        secs_arr = [c["sec"] for c in sub_ch]
        for fnm, tx_fn in [
            ("a_WholeWord(W)", lambda ws: [w for w in ws]),
            ("b_Prefix(P)", lambda ws: ["P_" + seg.segment(w)[0] for w in ws]),
            ("c_Core(C)", lambda ws: ["C_" + seg.segment(w)[1] for w in ws]),
            ("d_Suffix(S)", lambda ws: ["S_" + seg.segment(w)[2] for w in ws]),
            (
                "e1_Prefix|Core50",
                lambda ws: [
                    "PC_" + seg.segment(w)[1] + "_" + seg.segment(w)[0]
                    for w in ws
                    if seg.segment(w)[1] in top50_c
                ],
            ),
            (
                "e2_Suffix|Core50",
                lambda ws: [
                    "SC_" + seg.segment(w)[1] + "_" + seg.segment(w)[2]
                    for w in ws
                    if seg.segment(w)[1] in top50_c
                ],
            ),
        ]:
            texts = [" ".join(tx_fn(c["text"].split())) or "EMPTY" for c in sub_ch]
            cl = b5.topics(texts, k=len(secs) + 2, seed=0)
            obs_n = float(sk_nmi(secs_arr, cl))
            qvals = np.array([sk_nmi([a[i] for i in qix_c], cl) for a in qalls_c])
            bfvals = np.array([sk_nmi([a[i] for i in bfix_c], cl) for a in bfalls_c])
            qm, qsd = float(qvals.mean()), float(qvals.std()) or 1e-9
            qz = (obs_n - qm) / qsd
            qp = float(np.mean(qvals >= obs_n - 1e-12))
            bfm, bfsd = float(bfvals.mean()), float(bfvals.std()) or 1e-9
            bfz = (obs_n - bfm) / bfsd
            bfp = float(np.mean(bfvals >= obs_n - 1e-12))
            nmf_results[fnm] = dict(
                obs_nmi=obs_n,
                q_null=qm,
                q_ex=obs_n - qm,
                q_z=qz,
                q_p=qp,
                bf_null=bfm,
                bf_ex=obs_n - bfm,
                bf_z=bfz,
                bf_p=bfp,
            )
            emit(
                f"      {fnm:17s} | {obs_n:8.4f} | {qm:7.4f} {obs_n-qm:+8.4f} {qz:+7.2f} {qp:7.4f} | "
                f"{bfm:7.4f} {obs_n-bfm:+8.4f} {bfz:+7.2f} {bfp:7.4f}"
            )

        # Print concrete top shared cores and their prefix shift across sections on ZL3b
        if tr_name == "ZL3b":
            emit(f"    Concrete Top Shared Cores in {h_label} showing Section-Operator Prefix Shifts (P | C):")
            for c_stem in top50_list[:5]:
                sec_p_cnt = {s: Counter() for s in secs}
                for sec, _, _, _w, p, c, _s in sub50:
                    if c == c_stem:
                        sec_p_cnt[sec][p or "<0>"] += 1
                summary_parts = []
                for s in secs:
                    tot_s = sum(sec_p_cnt[s].values())
                    top_ps = ", ".join(
                        f"{p}:{100*v/max(1,tot_s):.0f}%" for p, v in sec_p_cnt[s].most_common(3)
                    )
                    summary_parts.append(f"{s}(n={tot_s}: {top_ps})")
                emit(f"      core='{c_stem}': " + " vs ".join(summary_parts))

        res_p2[h_label] = dict(token_it=tok_results, chunk_nmf=nmf_results)
    return res_p2


# ---------------------------------------------------------------------------
# PART 3: Same-Folio Label <-> Paragraph Body-Text Vocabulary Coupling
# ---------------------------------------------------------------------------
def strip_oyds_12(w: str) -> str:
    """1-2 char prefix-stripped stem (stripping Voynich label/body prefixes o-, y-, d-, s-, qo-, ch-, sh-, ct-, ck-)."""
    if len(w) >= 4 and w[:2] in ("qo", "ch", "sh", "ct", "ck", "ol", "ot", "ok"):
        return w[2:]
    if len(w) >= 3 and w[0] in ("o", "y", "d", "s"):
        return w[1:]
    return w


def strip_oyds_only(w: str) -> str:
    """Strict 1-char label-prefix strip (o-, y-, d-, s- when len >= 3)."""
    if len(w) >= 3 and w[0] in ("o", "y", "d", "s"):
        return w[1:]
    return w


def sec_group_of(illus: str) -> str:
    if illus == "H":
        return "Herbal"
    if illus == "P":
        return "Pharma"
    if illus == "B":
        return "Bio"
    return "Cosmo_Astro"


def tfidf_diag_and_matrix(pages: list[str], lab_docs: dict[str, list[str]], body_docs: dict[str, list[str]]) -> np.ndarray:
    """Compute pairwise TF-IDF cosine matrix S[i, j] between body_docs[pages[i]] and lab_docs[pages[j]]."""
    n = len(pages)
    corpus = [" ".join(body_docs[p]) for p in pages] + [" ".join(lab_docs[p]) for p in pages]
    vec = TfidfVectorizer(min_df=1, token_pattern=r"\S+", sublinear_tf=True)
    X = vec.fit_transform(corpus).toarray()
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    X = X / norms
    B_mat = X[:n]
    L_mat = X[n:]
    return B_mat @ L_mat.T  # S[i, j] = cosine(body_i, label_j)


def run_part3(tr_name: str, recs: list[dict], seg: mn.SlotSegmenter) -> dict:
    emit(f"\n--- PART 3 [{tr_name}]: SAME-FOLIO LABEL <-> PARAGRAPH BODY-TEXT COUPLING ---")
    lab_by_page = defaultdict(list)
    par_by_page = defaultdict(list)
    any_body_by_page = defaultdict(list)
    meta_by_page = {}

    for r in recs:
        ws = [w for w in r["words"] if "?" not in w]
        if not ws:
            continue
        p = r["page"]
        meta_by_page[p] = (r["illus"], r["hand"])
        if r["unit"].startswith("L"):
            lab_by_page[p].extend(ws)
        else:
            any_body_by_page[p].extend(ws)
            if r["unit"].startswith("P"):
                par_by_page[p].extend(ws)

    pages_p = sorted(set(lab_by_page) & set(par_by_page))
    pages_any = sorted(set(lab_by_page) & set(any_body_by_page))
    tot_lab_all = sum(len(v) for v in lab_by_page.values())
    tot_lab_p = sum(len(lab_by_page[p]) for p in pages_p)

    emit(
        f"  [{tr_name}] Total L* label pages={len(lab_by_page)} ({tot_lab_all} tokens); "
        f"pages with BOTH L* and P* paragraph body={len(pages_p)} ({tot_lab_p} label tokens); "
        f"pages with L* and ANY non-L* body={len(pages_any)} ({sum(len(lab_by_page[p]) for p in pages_any)} label tokens)"
    )

    stem_rules = [
        ("i_ExactWord", lambda w: w),
        ("ii_SlotCore", lambda w: seg.segment(w)[1]),
        ("iii_Strip_oyds", strip_oyds_only),
        ("iv_Strip_12pref", strip_oyds_12),
        ("v_s29_AffixStem", s29.strip_label_affixes),
    ]

    p2idx = {p: i for i, p in enumerate(pages_p)}
    n_p = len(pages_p)

    # Build strata for permutation: (1) strict (illus, hand) and (2) 4-section group
    strata_ih = defaultdict(list)
    strata_sec = defaultdict(list)
    for p in pages_p:
        il, hd = meta_by_page[p]
        strata_ih[(il, hd)].append(p2idx[p])
        strata_sec[sec_group_of(il)].append(p2idx[p])

    # Pre-generate 1,000 permutation index arrays for both stratification schemes
    rng_ih = random.Random(SEED)
    perms_ih = np.zeros((N_PERM_P3, n_p), dtype=np.int64)
    for pi in range(N_PERM_P3):
        for idxs in strata_ih.values():
            sh = idxs[:]
            rng_ih.shuffle(sh)
            for a, b in zip(idxs, sh):
                perms_ih[pi, a] = b

    rng_sec = random.Random(SEED)
    perms_sec = np.zeros((N_PERM_P3, n_p), dtype=np.int64)
    for pi in range(N_PERM_P3):
        for idxs in strata_sec.values():
            sh = idxs[:]
            rng_sec.shuffle(sh)
            for a, b in zip(idxs, sh):
                perms_sec[pi, a] = b

    res_p3 = {}
    emit(
        f"    Overall Same-Folio Coupling on {n_p} L*+P* Folios ({tot_lab_p} label tokens, {N_PERM_P3} perms):"
    )
    emit(
        f"      {'Measure':17s} | {'TokHit':>7s} {'Null_IH':>7s} {'Ex_IH':>8s} {'z_IH':>6s} {'p_IH':>6s} | "
        f"{'TypHit':>7s} {'z_Typ':>6s} | {'TFIDF':>7s} {'Null_TF':>7s} {'z_TF':>6s} {'p_TF':>6s}"
    )

    sec_breakdown = {sg: {} for sg in ("Herbal", "Pharma", "Bio", "Cosmo_Astro")}
    rows_arange = np.arange(n_p)

    for rname, fn in stem_rules:
        l_docs = {p: [fn(w) for w in lab_by_page[p]] for p in pages_p}
        b_docs = {p: [fn(w) for w in par_by_page[p]] for p in pages_p}
        b_sets = [set(b_docs[p]) for p in pages_p]
        l_lists = [l_docs[p] for p in pages_p]
        l_types = [set(l_docs[p]) for p in pages_p]

        # Precompute n_p x n_p hit count matrix H_tok[i, j] = # label tokens of page j in body set of page i
        H_tok = np.zeros((n_p, n_p), dtype=np.float64)
        H_typ = np.zeros((n_p, n_p), dtype=np.float64)
        L_tok_cnt = np.array([len( x) for x in l_lists], dtype=np.float64)
        L_typ_cnt = np.array([len(x) for x in l_types], dtype=np.float64)
        for i in range(n_p):
            bs = b_sets[i]
            for j in range(n_p):
                H_tok[i, j] = sum(1 for w in l_lists[j] if w in bs)
                H_typ[i, j] = len(l_types[j] & bs)

        S_tfidf = tfidf_diag_and_matrix(pages_p, l_docs, b_docs)

        # Observed overall metrics
        obs_tok = float(np.diag(H_tok).sum() / L_tok_cnt.sum())
        obs_typ = float(np.diag(H_typ).sum() / L_typ_cnt.sum())
        obs_tf = float(np.diag(S_tfidf).mean())

        # Permuted overall metrics under within-(illus, hand)
        null_tok_ih = H_tok[rows_arange, perms_ih].sum(axis=1) / L_tok_cnt.sum()
        null_typ_ih = H_typ[rows_arange, perms_ih].sum(axis=1) / L_typ_cnt.sum()
        null_tf_ih = S_tfidf[rows_arange, perms_ih].mean(axis=1)

        m_tok, sd_tok = float(null_tok_ih.mean()), float(null_tok_ih.std()) or 1e-9
        z_tok = (obs_tok - m_tok) / sd_tok
        p_tok = float((1 + np.sum(null_tok_ih >= obs_tok - 1e-12)) / (N_PERM_P3 + 1))

        m_typ, sd_typ = float(null_typ_ih.mean()), float(null_typ_ih.std()) or 1e-9
        z_typ = (obs_typ - m_typ) / sd_typ
        p_typ = float((1 + np.sum(null_typ_ih >= obs_typ - 1e-12)) / (N_PERM_P3 + 1))

        m_tf, sd_tf = float(null_tf_ih.mean()), float(null_tf_ih.std()) or 1e-9
        z_tf = (obs_tf - m_tf) / sd_tf
        p_tf = float((1 + np.sum(null_tf_ih >= obs_tf - 1e-12)) / (N_PERM_P3 + 1))

        emit(
            f"      {rname:17s} | {obs_tok:7.4f} {m_tok:7.4f} {obs_tok-m_tok:+8.4f} {z_tok:+6.2f} {p_tok:6.4f} | "
            f"{obs_typ:7.4f} {z_typ:+6.2f} | {obs_tf:7.4f} {m_tf:7.4f} {z_tf:+6.2f} {p_tf:6.4f}"
        )

        # Per-section-group breakdown (using within-section-group permutations so all 4 groups have valid permutations)
        for sg in ("Herbal", "Pharma", "Bio", "Cosmo_Astro"):
            idxs = strata_sec[sg]
            tot_sg_tok = float(L_tok_cnt[idxs].sum())
            obs_sg_tok = float(H_tok[idxs, idxs].sum() / tot_sg_tok)
            null_sg_tok = H_tok[np.ix_(idxs, idxs)][np.arange(len(idxs)), :]  # unused, use perms_sec
            null_sg_vals = H_tok[idxs, perms_sec[:, idxs]].sum(axis=1) / tot_sg_tok
            m_sg, sd_sg = float(null_sg_vals.mean()), float(null_sg_vals.std()) or 1e-9
            z_sg = (obs_sg_tok - m_sg) / sd_sg
            p_sg = float((1 + np.sum(null_sg_vals >= obs_sg_tok - 1e-12)) / (N_PERM_P3 + 1))

            obs_sg_tf = float(S_tfidf[idxs, idxs].mean())
            null_sg_tf = S_tfidf[idxs, perms_sec[:, idxs]].mean(axis=1)
            m_sgtf, sd_sgtf = float(null_sg_tf.mean()), float(null_sg_tf.std()) or 1e-9
            z_sgtf = (obs_sg_tf - m_sgtf) / sd_sgtf
            p_sgtf = float((1 + np.sum(null_sg_tf >= obs_sg_tf - 1e-12)) / (N_PERM_P3 + 1))

            sec_breakdown[sg][rname] = dict(
                n_pages=len(idxs),
                n_tok=int(tot_sg_tok),
                obs_tok=obs_sg_tok,
                null_tok=m_sg,
                ex_tok=obs_sg_tok - m_sg,
                z_tok=z_sg,
                p_tok=p_sg,
                obs_tf=obs_sg_tf,
                null_tf=m_sgtf,
                z_tf=z_sgtf,
                p_tf=p_sgtf,
            )

        res_p3[rname] = dict(
            obs_tok=obs_tok,
            null_tok=m_tok,
            ex_tok=obs_tok - m_tok,
            z_tok=z_tok,
            p_tok=p_tok,
            obs_typ=obs_typ,
            null_typ=m_typ,
            z_typ=z_typ,
            p_typ=p_typ,
            obs_tf=obs_tf,
            null_tf=m_tf,
            z_tf=z_tf,
            p_tf=p_tf,
        )

    emit("\n    Per-Section Breakdown (1,000 within-section folio permutations):")
    for sg in ("Herbal", "Pharma", "Bio", "Cosmo_Astro"):
        first_d = next(iter(sec_breakdown[sg].values()))
        emit(f"      [{sg}: {first_d['n_pages']} folios, {first_d['n_tok']} label tokens]")
        for rname, _ in stem_rules:
            d = sec_breakdown[sg][rname]
            emit(
                f"        {rname:17s}: TokHit={d['obs_tok']:.4f} (null={d['null_tok']:.4f}, ex={d['ex_tok']:+.4f}, "
                f"z={d['z_tok']:+5.2f}, p={d['p_tok']:.4f}) | TFIDF={d['obs_tf']:.4f} (null={d['null_tf']:.4f}, z={d['z_tf']:+5.2f})"
            )

    res_p3["by_section"] = sec_breakdown
    return res_p3


def main() -> None:
    t0 = time.time()
    emit("=== S34: MORPHOLOGICAL SLOT, OPERATOR & LABEL COUPLING INVESTIGATOR ===")
    emit(f"Clock: {clock()}")
    emit(f"Script SHA256 verification: {stub_match()}")
    emit(f"Seed: {SEED} | Part 1 shuffles: {N_SHUF_P1} | Part 2 perms: {N_PERM_P2} | Part 3 perms: {N_PERM_P3}")

    bmap = P1.bifolio_of_pages()
    all_res = {}
    for tr_name, tr_path in TRANSLITS:
        recs = vparse.load(path=tr_path)
        emit("\n" + "=" * 86)
        emit(f"TRANSLITERATION: {tr_name} ({tr_path.name})")
        emit("=" * 86)
        r1, seg = run_part1(tr_name, recs)
        r2 = run_part2(tr_name, recs, seg, bmap)
        r3 = run_part3(tr_name, recs, seg)
        all_res[tr_name] = dict(p1=r1, p2=r2, p3=r3)

    emit("\n" + "=" * 86)
    emit("CROSS-TRANSLITERATION SYNTHESIS & SCIENTIFIC CONCLUSIONS (ZL3b | RF1b | IT2a)")
    emit("=" * 86)
    for tr_name, _ in TRANSLITS:
        p1_all = all_res[tr_name]["p1"]["ALL"]
        p1_a = all_res[tr_name]["p1"]["Currier_A"]
        p1_b = all_res[tr_name]["p1"]["Currier_B"]
        emit(
            f"  [Part 1 {tr_name}] S1->P2 ex: ALL={p1_all['inter']['S1->P2']['ex']:+.4f} (z={p1_all['inter']['S1->P2']['z']:+.1f}), "
            f"A={p1_a['inter']['S1->P2']['ex']:+.4f}, B={p1_b['inter']['S1->P2']['ex']:+.4f} | "
            f"C1->P2 ex: ALL={p1_all['inter']['C1->P2']['ex']:+.4f} | "
            f"P1->P2 ex: ALL={p1_all['inter']['P1->P2']['ex']:+.4f} | "
            f"C1->C2 ex: ALL={p1_all['inter']['C1->C2']['ex']:+.4f} (z={p1_all['inter']['C1->C2']['z']:+.1f}) | "
            f"Within-word P;S ex: ALL={p1_all['within_word']['P;S']['ex']:+.4f}"
        )

    for tr_name, _ in TRANSLITS:
        h1_nmf = all_res[tr_name]["p2"]["Hand1_H_vs_P"]["chunk_nmf"]
        h23_nmf = all_res[tr_name]["p2"]["Hand23_B_vs_S_vs_H"]["chunk_nmf"]
        emit(
            f"  [Part 2 O-027 {tr_name}] Hand1 NMF NMI: W={h1_nmf['a_WholeWord(W)']['obs_nmi']:.3f} "
            f"P={h1_nmf['b_Prefix(P)']['obs_nmi']:.3f} C={h1_nmf['c_Core(C)']['obs_nmi']:.3f} "
            f"S={h1_nmf['d_Suffix(S)']['obs_nmi']:.3f} P|C50={h1_nmf['e1_Prefix|Core50']['obs_nmi']:.3f} | "
            f"Hand23 NMF NMI: W={h23_nmf['a_WholeWord(W)']['obs_nmi']:.3f} "
            f"P={h23_nmf['b_Prefix(P)']['obs_nmi']:.3f} C={h23_nmf['c_Core(C)']['obs_nmi']:.3f} "
            f"S={h23_nmf['d_Suffix(S)']['obs_nmi']:.3f} P|C50={h23_nmf['e1_Prefix|Core50']['obs_nmi']:.3f}"
        )

    for tr_name, _ in TRANSLITS:
        p3 = all_res[tr_name]["p3"]
        emit(
            f"  [Part 3 {tr_name}] Same-folio L*->P* hit (obs vs null, z): "
            f"Exact={p3['i_ExactWord']['obs_tok']:.3f} vs {p3['i_ExactWord']['null_tok']:.3f} (z={p3['i_ExactWord']['z_tok']:+.2f}, p={p3['i_ExactWord']['p_tok']:.3f}) | "
            f"SlotCore={p3['ii_SlotCore']['obs_tok']:.3f} vs {p3['ii_SlotCore']['null_tok']:.3f} (z={p3['ii_SlotCore']['z_tok']:+.2f}, p={p3['ii_SlotCore']['p_tok']:.3f}) | "
            f"Strip12={p3['iv_Strip_12pref']['obs_tok']:.3f} vs {p3['iv_Strip_12pref']['null_tok']:.3f} (z={p3['iv_Strip_12pref']['z_tok']:+.2f}, p={p3['iv_Strip_12pref']['p_tok']:.3f})"
        )

    emit(f"\nCompleted in {time.time() - t0:.2f}s. Wrote {OUT.name}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
