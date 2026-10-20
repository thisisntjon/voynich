"""S27: K4 bound rows (Phase 3 step 1, workflow/phases/phase-3.md) + the shared Phase 3 scoring library
used unchanged by s28_generator_mechanism.py and s10_cipher_mechanism.py (they import this file).

PRE-REGISTRATION (frozen in s27_k4_bound.prereg.sha256 before the run; PREREG-v2.1.md item 7 governs).

What is scored (bound rows, NO count, no predictions of their own):
  * K4 lossy shared-codeword nomenclator at its MIDDLE setting, k4_lossy_nomenclator.py:143-146 configs[1]:
    pool_cap=7025, k_choices=6, rank_window=180, beta=1.8, codebook seed 20261017 (k4.build_shared_codebook),
    k4.encrypt_shared with Voynich's own R = f3.ratio_table(by), Qi/Qe/para = k1.line_tables(by) (circular,
    as the plan says: "what even a circular word code reaches"), plaintext k2.plaintext_streams(by),
    seeds 1, 2, 3 (no calibration: a bound has no free parameter), per transliteration T in {ZL3b, RF1b, IT2a}.
  * K4 shuffled-plaintext NULL (k4.py:155-160 pattern), seed 1, per T: reference for F1 / NMI-h1 only.
  * flow_cipher_layer (data/controls_synthetic/flow_cipher_layer.meta.json, k5 export of k1 CIPHER +layer:
    real Naibbe key, Voynich-measured tables; 159 pages): the cipher-family anchor, no decode step.

Plan table rows carried verbatim (workflow/phases/phase-3.md "The design"):
| bound rows (no count) | **s27**: K4 lossy nomenclator at its middle setting; `flow_cipher_layer` (real Naibbe key, Voynich-measured tables) | — | what even a circular word code reaches |
Research §3 expectation (not a prediction cell): F1 +0.047, NMI-h1 0.27 reached by the circular word code; types/hapax fail.

Shared scoring (identical for s27 / s28 / s10; "the result file wins" on any disagreement with the plan text):
  Board: scoreboard/run_v2.py loaded by path (s21 pattern), score_one on (a) the full book, rows all / A / B
  (sidecar page field lang; A under v2.1 item 4: m_final_enrich no weight), scored whole like Voynich (no 25k
  cut; types_25k is the 25k-scale count inside score_one), and (b) the 41 held-out pages of g1_edge_joint.py
  split_names (Random(20261017) shuffle, 80/20 of 207; verified identical to the 41-page set behind
  s15_ranges.json -> g1_heldout_41), rows all / A / B. In/out per family L/C/G/X with run_v2.in_out and the
  s15_ranges.json tight flags; the v2.1 item 1 within-manuscript lo95/hi95 printed beside every weighted
  metric ("in-width" = lo95 <= value <= hi95; a stated margin, not a pass/fail). Kill-candidate flag per row per
  family: >= 3 weighted outs on tight ranges (v2 §7). jsd_first_fg / p_init_enrich are declared "fixed by the
  pools, no weight" for s28 / s10 (Voynich-token edge pools, decision 4) and coupling (cross_excess_eva,
  x_edge_mi_word) is reached/not-reached only against the B value (v2.1 item 5), no weight.
  Extras (full book, per T, per seed), each with DELTA = entrant - Voynich(T) and a page-bootstrap 95 % interval,
  B = 1000, paired on the shared page skeleton (same page ids resampled for both texts; independent resampling
  when the page sets differ, as for flow_cipher_layer), np.random.default_rng(20261017):
    CHARWIN  = bits/token(unigram-GT-renorm) - bits/token(char3-WB) on m3's page split (m3.page_split seed
               20261017, 80/20, one fold; m3.build_models), per-page bit sums resampled over the test pages.
               Own null: invariant under within-line shuffle (both models are order-free) -> printed as "n/a".
    MORAN I  = s21_moran_realline estimator (within-line lag-1 word-length Moran I, global mean), resampled over
               pages; own null = within-line shuffle, 999 draws, seed 20261017, median / q99 / one-sided p.
    F1       = n1_habit_table.residual on the quire split (train even quires, test odd quires; TOPN 300,
               within-line-shuffle corrected), per-page sums (n1.page_sums) resampled over the test pages
               (rng seed 7 as n1.residual, B = 1000) -> "quires for F1 as n6". Own CI = the entrant's own interval.
    NMI-h1   = n3.nmi_tests(by)['h1'] (quire-block exact null, floor 1/55) and n4.nmi_bifolio(by)['h1']
               (bifolio-block null); bar 0.206 = 0.75 x 0.275; reported, not counted (1/55 floor).
  Rule for the three unbanded metrics (plan, verbatim): "Reached" = interval includes zero or lies above;
  "missed" = interval entirely below zero. Per-dataset own-null q99 lines are printed, not decisive.
  Cell call = ZL3b, majority over measurement seeds 1-3; RF1b / IT2a beside; a cell whose majority call flips on
  another file is marked UNSTABLE (v2 §2). For s27 the calls are informational (bound rows enter no count).
  Verdict rule (plan, verbatim; applied in s33): the family whose three unbanded predictions (CHARWIN sign,
  F1 reached/missed, Moran reached/missed) all hold on untouched material, while the other family misses at
  least one, earns a "registered lean" (Tier 2 is explicitly not available from this pair). If both hold or
  both miss, the result is "tie at this design". BH q=0.05 over the round's p-values; every negative carries a
  power line (v2.1 item 6): smallest |DELTA| detectable at power 0.8 ~ 2.8 x bootstrap SE(DELTA) (two-sided 0.05).
  P-values entering the round's BH family: Moran own-null p (seed median per T), NMI-h1 quire-block p and
  bifolio p (floor-bound entries "floor, not ranked"); printed as PVAL| lines for s33.

Constraints: python -I, one CPU process, no GPU, no paid calls, no new data; sidecars only under runs/s27/;
scoreboard/scoreboard.json never written; wall-clock guard 40 min (STOPPED line, exit 2).
Writes: results_s27.txt (+ runs/s27/*.meta.json sidecars, runs/s27/rows.json).
Run: python -I s27_k4_bound.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import random
import subprocess
import sys
import time
from collections import Counter, OrderedDict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

import c2_section_generator as c2  # noqa: E402
import f3_flow_choice as f3  # noqa: E402
import g1_edge_joint as g1  # noqa: E402
import k1_joint_producer as k1  # noqa: E402
import k2_nomenclator as k2  # noqa: E402
import k4_lossy_nomenclator as k4  # noqa: E402
import m3_bakeoff_reconcile as m3  # noqa: E402
import n1_habit_table as N  # noqa: E402
import n3_content_signals as n3  # noqa: E402
import n4_habit7k as n4  # noqa: E402
import s31_null_glyph_charwin_pilot as s31  # noqa: E402

SEED = 20261017
B_BOOT = 1000
N_DRAWS = 999
NMI_BAR = 0.206
WALL_LIMIT_S = 40 * 60
RANGES = ROOT / "s15_ranges.json"
TRANSLITS = N.TRANSLITS  # {"ZL3b": "ZL3b_eva", "RF1b": "RF1b", "IT2a": "IT2a"}
TARGET_SET = ["types_25k", "h2", "jsd_first_fg", "p_init_enrich", "m_final_enrich"]
POOL_FIXED = {"jsd_first_fg", "p_init_enrich"}
COUPLING = ["cross_excess_eva", "x_edge_mi_word"]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now; `date` unavailable)"


def load_by_path(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


R2 = load_by_path("run_v2_phase3", ROOT / "scoreboard" / "run_v2.py")


def stub_match(script: Path, stub: Path) -> str:
    if not stub.exists():
        return "NO STUB"
    want = {}
    for ln in stub.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    return "True" if want and not bad else f"False (mismatch: {', '.join(bad) or 'empty stub'})"


# ---------------------------------------------------------------- data
def load_T(T):
    """N.load(T) records (page, words, hand, illus, quire, lang) + M5 para_start carried from the ZL3b layout
    by (page, line index) where the page's line count matches; otherwise para_start = first line of the page."""
    by = N.load(TRANSLITS[T])
    lay = k1.layout()
    n_exact = n_fallback = 0
    for page, recs in by.items():
        src = lay.get(page)
        if src is not None and len(src) == len(recs):
            for r, s in zip(recs, src):
                r["para_start"] = bool(s["para_start"])
            n_exact += 1
        else:
            for i, r in enumerate(recs):
                r["para_start"] = i == 0
            n_fallback += 1
    return by, n_exact, n_fallback


def pages_of(by):
    return s31.by_to_pages(by)


def heldout_ids(by):
    _, te = g1.split_names(by)
    return set(te)


def pages_to_by(pages):
    """Sidecar pages -> by (for F1/NMI on an external sidecar such as flow_cipher_layer)."""
    by = OrderedDict()
    for p in pages:
        recs = [dict(page=p["id"], words=list(ln), hand=p.get("hand", "?"), illus=p.get("section", "?"),
                     quire=p.get("quire"), lang=p.get("lang", "?"), para_start=(i == 0))
                for i, ln in enumerate(p["lines"]) if ln]
        if recs:
            by[p["id"]] = recs
    return by


# ---------------------------------------------------------------- extras with page bootstrap
def charwin_pages(pages):
    """Per test page (m3.page_split, one fold): (bits unigram-GT-renorm, bits char3-WB, tokens)."""
    fold = m3.page_split(pages, SEED)[0]
    test = set(fold)
    train = [w for i, p in enumerate(pages) if i not in test for ln in p["lines"] for w in ln]
    models = m3.build_models(train)
    rn, wb = models["unigram-GT-renorm"], models["char3-WB"]
    rows = {}
    for i in fold:
        ws = [w for ln in pages[i]["lines"] for w in ln]
        rows[pages[i]["id"]] = np.array([-sum(rn.logp_word(w) for w in ws), -sum(wb.logp_word(w) for w in ws), len(ws)])
    return rows


def charwin_stat(arr):
    s = arr.sum(0)
    return s[0] / s[2] - s[1] / s[2]


def moran_pages(pages):
    """Per page sufficient statistics for the s21 within-line Moran I (global mean, within-line pairs)."""
    rows = {}
    for p in pages:
        n = s1 = s2 = npair = spp = sl = sr = 0.0
        for ln in p["lines"]:
            if not ln:
                continue
            x = np.array([len(t) for t in ln], dtype=float)
            n += len(x); s1 += x.sum(); s2 += (x * x).sum()
            if len(x) > 1:
                npair += len(x) - 1; spp += (x[:-1] * x[1:]).sum(); sl += x[:-1].sum(); sr += x[1:].sum()
        rows[p["id"]] = np.array([n, s1, s2, npair, spp, sl, sr])
    return rows


def moran_stat(arr):
    n, s1, s2, npair, spp, sl, sr = arr.sum(0)
    mean = s1 / n
    denom = s2 - n * mean * mean
    num = spp - mean * (sl + sr) + npair * mean * mean
    return (n / npair) * num / denom


def moran_line_null(pages, seed=SEED):
    """s21: within-line shuffle null, 999 draws; returns (I, median, q99, p, pairs, tokens)."""
    lengths, line_id, left, right = [], [], [], []
    nl = 0
    for p in pages:
        for ln in p["lines"]:
            if not ln:
                continue
            start = len(lengths)
            lengths.extend(len(t) for t in ln)
            line_id.extend([nl] * len(ln))
            if len(ln) > 1:
                idx = np.arange(start, start + len(ln))
                left.append(idx[:-1]); right.append(idx[1:])
            nl += 1
    x = np.asarray(lengths, dtype=float); lid = np.asarray(line_id); left = np.concatenate(left); right = np.concatenate(right)

    def I(v):
        z = v - v.mean()
        return float(len(v) / len(left) * np.dot(z[left], z[right]) / np.dot(z, z))

    obs = I(x)
    rng = np.random.default_rng(seed)
    out = np.empty(N_DRAWS)
    for d in range(N_DRAWS):
        perm = np.lexsort((rng.random(len(x)), lid))
        out[d] = I(x[perm])
    p = float((1 + int(np.count_nonzero(out >= obs))) / (N_DRAWS + 1))
    return dict(I=obs, median=float(np.median(out)), q99=float(np.quantile(out, 0.99)), p=p,
                sd=float(out.std()), pairs=int(len(left)), tokens=int(len(x)))


def f1_pages(by):
    """n1.residual's quire split with per-test-page sums: dict page -> (n, E2, W, sE2, sW, sn)."""
    tr, te = N.split(by, "quires")
    real = N.page_sums(tr, te)
    rng = random.Random(3)
    sh_tr = [rng.sample(l, len(l)) for l in tr]
    sh_te = [(p, rng.sample(l, len(l))) for p, l in te]
    shuf = N.page_sums(sh_tr, sh_te)
    return {p: np.concatenate([real[p], shuf[p]]) for p in real}


def f1_stat(arr):
    r = arr.sum(0)
    return (r[1] - r[2]) / r[0] - (r[4] - r[5]) / r[3]


def boot_delta(rows_e, rows_v, stat, seed, paired):
    """DELTA = stat(entrant) - stat(voynich) with a page bootstrap (B_BOOT). Paired when the page sets coincide."""
    rng = np.random.default_rng(seed)
    if paired:
        ids = sorted(set(rows_e) & set(rows_v))
        E = np.array([rows_e[i] for i in ids]); V = np.array([rows_v[i] for i in ids])
        n = len(ids)
        ds = []
        for _ in range(B_BOOT):
            ix = rng.integers(0, n, n)
            ds.append(stat(E[ix]) - stat(V[ix]))
    else:
        E = np.array(list(rows_e.values())); V = np.array(list(rows_v.values()))
        ds = []
        for _ in range(B_BOOT):
            ds.append(stat(E[rng.integers(0, len(E), len(E))]) - stat(V[rng.integers(0, len(V), len(V))]))
    ds = np.array(ds)
    full = stat(np.array(list(rows_e.values()))) - stat(np.array(list(rows_v.values())))
    lo, hi = np.percentile(ds, [2.5, 97.5])
    return float(full), float(lo), float(hi), float(ds.std())


def call_of(lo, hi):
    return "missed" if hi < 0 else "reached"


def nmi_h1(by):
    q = n3.nmi_tests(by)["h1"]
    b = n4.nmi_bifolio(by)["h1"]
    return dict(obs=q[0], pq=q[1], nbq=q[2], naq=q[3], pb=b[1], nbb=b[2], nab=b[3])


# ---------------------------------------------------------------- references per T (computed once per run)
class VoyRef:
    def __init__(self, T, by):
        self.T = T
        self.by = by
        self.pages = pages_of(by)
        self.ids41 = heldout_ids(by)
        self.cw = charwin_pages(self.pages)
        self.mo = moran_pages(self.pages)
        self.f1 = f1_pages(by)
        self.charwin = charwin_stat(np.array(list(self.cw.values())))
        self.moran = moran_stat(np.array(list(self.mo.values())))
        self.moran_null = moran_line_null(self.pages)
        self.f1v, self.f1ci = N.residual(by, "quires")
        self.nmi = nmi_h1(by)


# ---------------------------------------------------------------- board rows
class Board:
    def __init__(self, emit):
        R = json.loads(RANGES.read_text(encoding="utf-8"))
        self.ranges, self.tight, self.noweight = R["ranges"], R.get("tight", {}), set(R.get("no_weight", []))
        self.wm = R["within_manuscript"]
        self.g41 = R["g1_heldout_41"]
        self.full = R["full_rows"]
        self.fams = ["L", "C", "G", "X"]
        kinds = dict((a, b) for a, b, _ in R2.NEW_KEYS)
        self.weighted = [k for k in R2.V1_KEYS + R2.NEW_NUMERIC if k not in self.noweight and kinds.get(k, "WEIGHTED") != "REPORT"]
        self.emit = emit
        self.rows = []

    def hdr(self):
        self.emit(f"{'row':34s} {'tok':>6s} {'typ':>5s} {'t25k':>5s} {'h2':>6s} {'sdlen':>6s} {'jsdf':>6s} {'pinit':>6s} "
                  f"{'mfin':>6s} {'cross':>6s} {'redup':>6s} {'edgeMI':>6s} {'posH':>6s} {'ltr-rtl':>7s} {'moran':>6s} | "
                  f"{'L':>8s} {'C':>8s} {'G':>8s} {'X':>8s} | width-flags")

    def row(self, label, pages, lang, scale):
        """scale = 'full' or 'g41'. Prints one row, returns the dict."""
        pg = R2.subset_lang(pages, None if lang == "all" else lang)
        if not pg:
            self.emit(f"{label:34s} (no pages)")
            return None
        row = R2.score_one(label, pg, lambda s: None)
        io = {}
        for k in R2.V1_KEYS + R2.NEW_NUMERIC:
            v = R2.fin(row.get(k))
            io[k] = {f: R2.in_out(v, self.ranges.get(k, {}).get(f)) for f in self.fams}
        fam_cells = []
        kills = []
        for f in self.fams:
            outs = [k for k in self.weighted if io[k][f] == "OUT" and not (lang == "A" and k == "m_final_enrich")]
            ins = [k for k in self.weighted if io[k][f] == "IN"]
            outs_t = [k for k in outs if self.tight.get(k, {}).get(f)]
            fam_cells.append(f"{len(ins):2d}/{len(outs):2d}/{len(outs_t):1d}")
            if len(outs_t) >= 3:
                kills.append(f)
            row.setdefault("in_out", {})[f] = dict(ins=len(ins), outs=len(outs), out_tight=outs_t, out_metrics=outs)
        flags = []
        for k in TARGET_SET + COUPLING + ["x_moran_I", "redup_pct"]:
            v = R2.fin(row.get(k))
            w = self.wm.get(k, {})
            if v is None or w.get("lo95") is None:
                flags.append(f"{k[:5]}=na")
                continue
            if scale == "g41":
                ok = w["lo95"] <= v <= w["hi95"]
            else:
                ref = self.full["ZL3b"].get(k)
                half = (w["hi95"] - w["lo95"]) / 2
                ok = ref is not None and abs(v - ref) <= half
            tag = "W" if ok else "o"
            if k in POOL_FIXED:
                tag += "(pool)"
            if k in COUPLING:
                tag += "(B-ref)"
            if lang == "A" and k == "m_final_enrich":
                tag += "(A:nw)"
            flags.append(f"{k[:6]}:{tag}")

        def f(k, d=3):
            v = R2.fin(row.get(k))
            return "nan" if v is None else f"{v:.{d}f}"
        self.emit(f"{label:34s} {row['tokens']:6d} {row['types']:5d} {row['types_25k']:5d} {f('h2')} {f('sd_len')} "
                  f"{f('jsd_first_fg')} {f('p_init_enrich', 1):>6s} {f('m_final_enrich', 1):>6s} {f('cross_excess_eva')} "
                  f"{f('redup_pct')} {f('x_edge_mi_word')} {f('x_position_entropy')} {f('x_ltr_minus_rtl', 4):>7s} {f('x_moran_I')} | "
                  + " ".join(fam_cells) + " | " + " ".join(flags)
                  + (f"  KILL-CAND:{''.join(kills)}" if kills else "") + (f"  errors:{list(row['errors'])}" if row["errors"] else ""))
        row["label"], row["scale"], row["lang"] = label, scale, lang
        self.rows.append({k: v for k, v in row.items() if k != "v1_full"})
        return row

    def block(self, label, pages, ids41):
        out = {}
        for lang in ("all", "A", "B"):
            out[f"full_{lang}"] = self.row(f"{label} full {lang}", pages, lang, "full")
        p41 = [p for p in pages if p["id"] in ids41]
        for lang in ("all", "A", "B"):
            out[f"g41_{lang}"] = self.row(f"{label} g41 {lang}", p41, lang, "g41")
        return out


# ---------------------------------------------------------------- one entrant text: extras + cells
def extras(emit, entrant, T, seed, by_e, ref: VoyRef, cells, pvals, paired=True, do_f1=True):
    pages_e = pages_of(by_e)
    cw = charwin_pages(pages_e)
    mo = moran_pages(pages_e)
    cw_v = charwin_stat(np.array(list(cw.values())))
    d, lo, hi, se = boot_delta(cw, ref.cw, charwin_stat, SEED, paired)
    call = call_of(lo, hi)
    sign = "positive" if cw_v > 0 else "negative"
    emit(f"  CHARWIN  {cw_v:+.4f} ({sign})  Voynich {ref.charwin:+.4f}  DELTA {d:+.4f} [{lo:+.4f}, {hi:+.4f}]  -> {call}; "
         f"own null: n/a (invariant under within-line shuffle)")
    emit(f"CELL|{entrant}|{T}|{seed}|CHARWIN|{cw_v:+.5f}|{ref.charwin:+.5f}|{d:+.5f}|{lo:+.5f}|{hi:+.5f}|{call}|sign={sign};se={se:.5f}")
    mv = moran_stat(np.array(list(mo.values())))
    d, lo, hi, se = boot_delta(mo, ref.mo, moran_stat, SEED, paired)
    call = call_of(lo, hi)
    nul = moran_line_null(pages_e)
    emit(f"  MORAN I  {mv:+.4f} ({'positive' if mv > 0 else 'non-positive'})  Voynich {ref.moran:+.4f}  DELTA {d:+.4f} [{lo:+.4f}, {hi:+.4f}]  -> {call}; "
         f"own line-shuffle null (999): median {nul['median']:+.4f} q99 {nul['q99']:+.4f} p={nul['p']:.3f} "
         f"above own q99: {mv > nul['q99']}  (Voynich q99 {ref.moran_null['q99']:+.4f} p={ref.moran_null['p']:.3f})")
    emit(f"CELL|{entrant}|{T}|{seed}|MORAN|{mv:+.5f}|{ref.moran:+.5f}|{d:+.5f}|{lo:+.5f}|{hi:+.5f}|{call}|sign={'positive' if mv > 0 else 'non-positive'};q99={nul['q99']:+.5f};p={nul['p']:.4f};se={se:.5f}")
    pvals.append(f"PVAL|{entrant}|{T}|{seed}|moran_line_shuffle|{nul['p']:.4f}|{1 / (N_DRAWS + 1):.4f}|one-sided, 999 draws; power 0.8 at I excess ~ {2.8 * nul['sd']:.4f} over null median")
    if do_f1:
        f1r = f1_pages(by_e)
        fv, fci = N.residual(by_e, "quires")
        d, lo, hi, se = boot_delta(f1r, ref.f1, f1_stat, 7, paired)
        call = call_of(lo, hi)
        emit(f"  F1 resid {fv:+.4f} own CI [{fci[0]:+.4f}, {fci[1]:+.4f}]  Voynich {ref.f1v:+.4f} [{ref.f1ci[0]:+.4f}, {ref.f1ci[1]:+.4f}]  "
             f"DELTA {d:+.4f} [{lo:+.4f}, {hi:+.4f}]  -> {call}")
        emit(f"CELL|{entrant}|{T}|{seed}|F1|{fv:+.5f}|{ref.f1v:+.5f}|{d:+.5f}|{lo:+.5f}|{hi:+.5f}|{call}|ownlo={fci[0]:+.5f};ownhi={fci[1]:+.5f};se={se:.5f}")
        nm = nmi_h1(by_e)
        below = nm["obs"] < NMI_BAR
        emit(f"  NMI-h1   {nm['obs']:.3f} (bar {NMI_BAR}; Voynich {ref.nmi['obs']:.3f})  quire-block p={nm['pq']:.3f} ({nm['nbq']} blocks, {nm['naq']} assignments, floor {1 / nm['naq']:.4f})  "
             f"bifolio p={nm['pb']:.3f} ({nm['nbb']} blocks, {nm['nab']} assignments)  -> {'below bar' if below else 'REACHES bar'} (reported, not counted)")
        emit(f"CELL|{entrant}|{T}|{seed}|NMI|{nm['obs']:.5f}|{ref.nmi['obs']:.5f}|{nm['obs'] - ref.nmi['obs']:+.5f}|nan|nan|{'below' if below else 'reached'}|pq={nm['pq']:.4f};pb={nm['pb']:.4f}")
        pvals.append(f"PVAL|{entrant}|{T}|{seed}|nmi_h1_quire_block|{nm['pq']:.4f}|{1 / nm['naq']:.4f}|exact null, {nm['naq']} assignments")
        pvals.append(f"PVAL|{entrant}|{T}|{seed}|nmi_h1_bifolio|{nm['pb']:.4f}|{1 / nm['nab']:.4f}|{nm['nab']} assignments")
    cells.append((entrant, T, seed))


def power_lines(emit, lines):
    """One TEST/FILED/POWER/STATUS block per CELL line whose call is 'missed' or whose interval includes zero."""
    emit("=== POWER (v2.1 item 6.1): every negative / null-difference cell beside its smallest detectable DELTA ===")
    for ln in lines:
        if not ln.startswith("CELL|"):
            continue
        f = ln.split("|")
        if f[4] == "NMI":
            continue
        se = float(f[11].split("se=")[1].split(";")[0]) if "se=" in f[11] else float("nan")
        mde = 2.8 * se
        lo, hi = float(f[8]), float(f[9])
        kind = "missed (entrant below Voynich)" if f[10] == "missed" else ("interval includes zero (no detected difference)" if lo <= 0 <= hi else "entrant above Voynich")
        emit(f"TEST    : {f[1]} {f[2]} seed {f[3]} {f[4]} DELTA vs Voynich (page bootstrap B={B_BOOT})")
        emit(f"FILED   : value {f[5]} Voynich {f[6]} DELTA {f[7]} [{f[8]}, {f[9]}] -> {f[10]}; {kind}")
        emit(f"POWER   : smallest |DELTA| detectable at power 0.8 (two-sided 0.05, normal approx.) = 2.8 x SE {se:.4f} = {mde:.4f}; observed |DELTA| {abs(float(f[7])):.4f} {'>=' if abs(float(f[7])) >= mde else '<'} MDE")
        emit(f"STATUS  : {'POWERED' if abs(float(f[7])) >= mde or f[10] == 'missed' else 'UNDERPOWERED for a difference of the observed size'}")
        emit()


def wall_guard(t0, emit, flush):
    if time.time() - t0 > WALL_LIMIT_S:
        emit(f"STOPPED: wall-clock guard {WALL_LIMIT_S} s exceeded at {clock()}; results above are partial")
        flush()
        sys.exit(2)


def write_sidecar(run_dir, name, by):
    run_dir.mkdir(parents=True, exist_ok=True)
    obj = dict(name=name, tokenization="eva", pages=pages_of(by))
    (run_dir / f"{name}.meta.json").write_text(json.dumps(obj), encoding="utf-8")


def header(emit, title, script, stub):
    emit(title)
    emit(f"run started {clock()}")
    emit(f"{script.name} sha256={sha256(script)}  prereg stub_match={stub_match(script, stub)}")
    emit(f"ranges: {RANGES.name} sha256={sha256(RANGES)}; scorer scoreboard/run_v2.py sha256={sha256(ROOT / 'scoreboard' / 'run_v2.py')[:16]}... (loaded by path; scoreboard.json untouched)")
    emit(f"shared library: s27_k4_bound.py sha256={sha256(ROOT / 's27_k4_bound.py')}")
    emit(f"python -I; one CPU process; no GPU; no paid calls; no new data; DELTA page bootstrap B={B_BOOT}; Moran null {N_DRAWS} draws; seed {SEED}")


# ---------------------------------------------------------------- s27 main
SELF = ROOT / "s27_k4_bound.py"
STUB = ROOT / "s27_k4_bound.prereg.sha256"
OUT = ROOT / "results_s27.txt"
RUN_DIR = ROOT / "runs" / "s27"
K4_CFG = dict(pool_cap=7025, k_choices=6, rank_window=180)
K4_BETA = 1.8
SEEDS = (1, 2, 3)


def main():
    t0 = time.time()
    lines_out = []

    def emit(s=""):
        print(s, flush=True)
        lines_out.append(s)

    def flush():
        OUT.write_text("\n".join(lines_out) + "\n", encoding="utf-8", newline="\n")

    header(emit, "S27: K4 bound rows (middle setting k=6 w=180 beta=1.8, 3 T x 3 seeds) + flow_cipher_layer anchor (phase-3.md step s27)", SELF, STUB)
    emit("bound rows enter no count; K4 is circular twice (Voynich R table, Voynich codeword pool); flow_cipher_layer = real Naibbe key on Voynich-measured tables, no decode")
    emit()
    board = Board(emit)
    cells, pvals = [], []
    for T in TRANSLITS:
        by, n_exact, n_fb = load_T(T)
        ref = VoyRef(T, by)
        emit(f"=== {T}: {len(by)} pages, {sum(len(r['words']) for recs in by.values() for r in recs)} tokens; para_start exact on {n_exact} pages, first-line fallback on {n_fb}; 41 held-out pages: {len(ref.ids41)} ===")
        emit(f"Voynich {T} references: CHARWIN {ref.charwin:+.4f}  Moran I {ref.moran:+.4f} (line-shuffle q99 {ref.moran_null['q99']:+.4f}, p={ref.moran_null['p']:.3f})  "
             f"F1 {ref.f1v:+.4f} [{ref.f1ci[0]:+.4f}, {ref.f1ci[1]:+.4f}]  NMI-h1 {ref.nmi['obs']:.3f} (quire p {ref.nmi['pq']:.3f}, bifolio p {ref.nmi['pb']:.3f})")
        pvals.append(f"PVAL|voynich|{T}|0|moran_line_shuffle|{ref.moran_null['p']:.4f}|{1 / (N_DRAWS + 1):.4f}|reference row, not an entrant")
        board.hdr()
        board.block(f"Voynich {T}", ref.pages, ref.ids41)
        Qi, Qe, para = k1.line_tables(by)
        R = f3.ratio_table(by)
        g = c2.Gen(by)
        streams = k2.plaintext_streams(by, shuffle=False)
        allw = [w for v in streams.values() for w in v]
        book, n_used, mean_col = k4.build_shared_codebook(allw, g.freq, seed=SEED, **K4_CFG)
        emit(f"K4 codebook {T}: plaintext types {len(book)}, codewords used {n_used}, mean owners/codeword {mean_col:.1f}")
        for s in SEEDS:
            wall_guard(t0, emit, flush)
            enc = k4.encrypt_shared(by, streams, book, R, Qi, Qe, para, beta=K4_BETA, seed=s)
            name = f"s27_k4_{T}_s{s}"
            write_sidecar(RUN_DIR, name, enc)
            emit(f"--- {name} (K4 k=6 w=180 b=1.8, seed {s}) ---")
            board.hdr()
            board.block(name, pages_of(enc), ref.ids41)
            extras(emit, "s27_k4", T, s, enc, ref, cells, pvals)
            emit(f"    elapsed {time.time() - t0:.0f}s")
            flush()
        # shuffled-plaintext null, seed 1 (F1 / NMI reference only)
        shuf = k2.plaintext_streams(by, shuffle=True)
        enc0 = k4.encrypt_shared(by, shuf, book, R, Qi, Qe, para, beta=K4_BETA, seed=1)
        emit(f"--- s27_k4null_{T}_s1 (shuffled plaintext, seed 1; F1/NMI reference) ---")
        extras(emit, "s27_k4null", T, 1, enc0, ref, cells, pvals)
        flush()
        if T == "ZL3b":
            wall_guard(t0, emit, flush)
            _, fpages = R2.load_meta(ROOT / "data" / "controls_synthetic" / "flow_cipher_layer.meta.json")
            emit(f"--- flow_cipher_layer (file, {len(fpages)} pages; cipher-family anchor, independent page bootstrap) ---")
            board.hdr()
            board.block("flow_cipher_layer", fpages, ref.ids41)
            fby = pages_to_by(fpages)
            try:
                extras(emit, "s27_flow_cipher_layer", T, 0, fby, ref, cells, pvals, paired=False)
            except Exception as e:  # noqa: BLE001
                emit(f"  flow_cipher_layer extras failed: {type(e).__name__}: {e}")
            flush()
        emit()
    emit("=== summary of calls (bound rows; informational, no count) ===")
    for ln in lines_out:
        if ln.startswith("CELL|"):
            f = ln.split("|")
            emit(f"  {f[1]:24s} {f[2]} s{f[3]} {f[4]:8s} value {f[5]} Voynich {f[6]} DELTA {f[7]} [{f[8]}, {f[9]}] -> {f[10]}  {f[11]}")
    emit()
    power_lines(emit, list(lines_out))
    emit("=== p-values printed by this file (round family members for s33; floor-bound = 'floor, not ranked') ===")
    for p in pvals:
        emit(p)
    emit()
    (RUN_DIR / "rows.json").write_text(json.dumps(board.rows, default=str), encoding="utf-8")
    emit(f"sidecars: {RUN_DIR} ({len(list(RUN_DIR.glob('*.meta.json')))} files); rows.json written there")
    emit(f"elapsed {time.time() - t0:.0f}s; run ended {clock()}")
    flush()


if __name__ == "__main__":
    main()
