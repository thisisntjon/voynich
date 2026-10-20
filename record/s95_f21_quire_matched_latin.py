"""s95 — size-matched per-quire copied-Latin control for F-21 R_P1.

Defect being repaired (s86 Part 3B-3): each held-out Voynich quire's R_P1 (a few hundred to
~11k tokens, scored against a reference lexicon of the other 14 quires) was compared with ONE
whole-corpus CREMMA_all R_P1 (57k tokens, scored against itself, 0.703). R_P1 may depend on
sample size and on the held-out/reference design, so the comparison is unmatched.

Here, for every quire q of the 15 (s86's quires_15) on ZL3b, RF1b, IT2a:
  * Voynich R_P1 is recomputed exactly as s86 does (S86.confusion_enrichment, SET_P1_PALEO,
    freq_min=10, min_len=3, ref_freq_items = tokens of the other 14 quires).
  * A control distribution of N_DRAWS draws is built from each control corpus: a random
    contiguous excerpt of n_q tokens (n_q = tokens in quire q) is the "held-out" text, and a
    contiguous block of m_q tokens (m_q = tokens in the other 14 quires) taken from the rest of
    the corpus (circular complement, random offset) is the reference. Same function, same args.
  * Controls: CREMMA_all (copied Latin, s86's own control, primary) and latin_pliny_herbal
    (edited, non-copied Latin prose via corpora.control; secondary, descriptive).
R_P1 is a bag-of-types statistic (line breaks never enter it), so token count is matched
exactly and the excerpt's line count is reported, not matched.

Pre-registered calls (thresholds also in the stub header):
  C1: Voynich R_P1 < size-matched CREMMA_all median on >= 8/15 quires, on all 3 translits.
  C2: Voynich R_P1 < size-matched CREMMA_all 5th percentile on >= 8/15, on all 3 translits.
  S : size dependence in controls: Spearman rho(excerpt tokens, R_P1) over all pooled draws of a
      control; "size-dependent" if |rho| >= 0.20 and p < 0.001.
  F0 fixture (gate, run first): planted copied-with-visual-confusions text scores above planted
      composed text at matched size in >= 18/20 seeds, else abort.
NaN rules: a quire whose Voynich R_P1 is NaN counts as not below; a quire whose control has
> 50% NaN draws counts as not below; NaN draws are otherwise dropped from the percentiles.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import subprocess
import sys
import time
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

import corpora  # noqa: E402
import s86_sticky_table_solver_and_triangulation as S86  # noqa: E402

SELF = ROOT / "s95_f21_quire_matched_latin.py"
STUB = ROOT / "s95_f21_quire_matched_latin.prereg.sha256"
OUT = ROOT / "results_s95.txt"
RUNS = ROOT / "runs" / "s95"

SEED = 20261018 + 95
N_DRAWS = 200
N_WORKERS = 2
QUIRES_15 = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "M", "N", "O", "Q", "S", "T"]  # = s86 l.2047
TRANSLITS = ["ZL3b", "RF1b", "IT2a"]
C_MIN = 8            # >= 8/15
RHO_MIN = 0.20
RHO_P = 1e-3
FIX_SEEDS = 20
FIX_MIN = 18
NAN_MAX = 0.50
CREMMA_PATH = ROOT / "data" / "controls_realline" / "cremma_all.meta.json"
PROSE_NAME = "latin_pliny_herbal"

log_lines: list[str] = []


def emit(s: str = "") -> None:
    print(s, flush=True)
    log_lines.append(s)


def flush() -> None:
    OUT.write_text("\n".join(log_lines) + "\n", encoding="utf-8", newline="\n")


def clock() -> str:
    r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
    return r.stdout.strip() + " (`date`)"


def sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def stub_match() -> str:
    if not STUB.exists():
        return "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            h, f = ln.split(None, 1)
            want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    return "True" if (want and not bad and SELF.name in want) else f"False (mismatch: {bad})"


def lower_prio() -> None:
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:  # noqa: BLE001
        pass


def rp1(held: list[str], ref: list[str]) -> float:
    """s86's R_P1 exactly as s86 Part 3B-3 calls it (l.2198)."""
    return S86.confusion_enrichment(held, S86.SET_P1_PALEO, freq_min=10, min_len=3, ref_freq_items=ref)["ratio"]


# ---------------------------------------------------------------- fixture
def fixture(seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    alpha = "abcdefghiklmnoprstuy"
    endings = ["a", "o", "y", "us", "um", "is", "es", "or", "ar", "an"]
    stems = set()
    while len(stems) < 300:
        stems.add("".join(rng.choice(alpha) for _ in range(rng.randint(2, 5))))
    lex = [s + e for s in sorted(stems) for e in endings]
    rng.shuffle(lex)
    w = np.array([1.0 / (i + 1) ** 1.05 for i in range(len(lex))])
    w /= w.sum()
    partner = defaultdict(list)
    for a, b in S86.SET_P1_PALEO:
        partner[a].append(b)
        partner[b].append(a)

    def text(n: int, mode: str, r: random.Random) -> list[str]:
        idx = np.random.default_rng(r.randrange(1 << 30)).choice(len(lex), size=n, p=w)
        out = []
        for i in idx:
            t = lex[i]
            if r.random() < 0.04:
                if mode == "copied":
                    pos = [k for k, ch in enumerate(t) if ch in partner]
                    if pos:
                        k = r.choice(pos)
                        t = t[:k] + r.choice(partner[t[k]]) + t[k + 1:]
                else:
                    k = r.randrange(len(t))
                    t = t[:k] + r.choice([c for c in alpha if c != t[k]]) + t[k + 1:]
            out.append(t)
        return out

    res = []
    for mode in ("copied", "composed"):
        r = random.Random(seed * 7 + (1 if mode == "copied" else 2))
        res.append(rp1(text(3000, mode, r), text(30000, mode, r)))
    return res[0], res[1]


# ---------------------------------------------------------------- controls
_CTRL: dict[str, tuple[list[str], list[int]]] = {}


def load_controls() -> dict[str, tuple[list[str], list[int]]]:
    d = json.loads(CREMMA_PATH.read_text(encoding="utf-8"))
    toks, line_id = [], []
    li = 0
    for p in d["pages"]:  # identical tokenisation to s86 l.2128
        for ln in p["lines"]:
            ws = [w.lower() for w in ln if w]
            if not ws:
                continue
            toks.extend(ws)
            line_id.extend([li] * len(ws))
            li += 1
    pl = corpora.control(PROSE_NAME)
    return {"CREMMA_all": (toks, line_id), PROSE_NAME: (pl, [i // 10 for i in range(len(pl))])}


def _init() -> None:
    lower_prio()
    _CTRL.update(load_controls())


def draw_task(args: tuple) -> tuple:
    cname, tr, q, n, m, k = args
    toks, line_id = _CTRL[cname]
    N = len(toks)
    rng = random.Random(f"{SEED}|{cname}|{tr}|{q}|{k}")
    s = rng.randrange(N - n + 1)
    held = toks[s:s + n]
    n_lines = len(set(line_id[s:s + n]))
    rest = toks[s + n:] + toks[:s]  # circular complement, keeps contiguity except at the wrap
    m_eff = min(m, len(rest))
    o = rng.randrange(len(rest))
    ref = (rest[o:] + rest[:o])[:m_eff]
    return (cname, tr, q, k, n, m_eff, n_lines, rp1(held, ref))


def main() -> None:
    lower_prio()
    t0 = time.time()
    emit("=" * 100)
    emit("s95 — F-21 R_P1: Voynich held-out quires vs size-matched copied-Latin (CREMMA_all) excerpts")
    emit("=" * 100)
    emit(f"started {clock()}")
    emit(f"stub_match={stub_match()}")
    try:
        import psutil
        emit(f"free RAM {psutil.virtual_memory().available / 2**30:.1f} GB; workers={N_WORKERS} BelowNormal")
    except Exception:  # noqa: BLE001
        pass
    emit(f"N_DRAWS={N_DRAWS} SEED={SEED} C_MIN={C_MIN}/15 RHO_MIN={RHO_MIN} RHO_P={RHO_P} FIX={FIX_MIN}/{FIX_SEEDS}")
    emit()

    # F0 fixture
    emit("--- F0 fixture: planted copied(visual confusions) vs composed(random substitutions), held 3000 / ref 30000 ---")
    fx = [fixture(1000 + i) for i in range(FIX_SEEDS)]
    wins = sum(1 for a, b in fx if (not math.isnan(a)) and (math.isnan(b) or a > b))
    emit(f"  copied median R_P1={np.nanmedian([a for a, _ in fx]):.3f}  composed median={np.nanmedian([b for _, b in fx]):.3f}  copied>composed {wins}/{FIX_SEEDS}")
    f0 = wins >= FIX_MIN
    emit(f"  F0 fixture pass = {f0}")
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "fixture.json").write_text(json.dumps(dict(pairs=fx, wins=wins, pass_=f0)), encoding="utf-8")
    if not f0:
        emit("ABORT: fixture failed")
        flush()
        sys.exit(2)
    emit()

    # Voynich per-quire
    zl = S86.parse_ivtff_rich(S86.TRANSLIT_IVTFF["ZL3b"])
    loci = {(p, r["line"]) for p, rs in zl.items() for r in rs if r["para_native"]}
    vq: dict[str, dict] = {}
    tasks = []
    for tr in TRANSLITS:
        raw = zl if tr == "ZL3b" else S86.parse_ivtff_rich(S86.TRANSLIT_IVTFF[tr], zl_para_loci=loci)
        by_q = defaultdict(list)
        for rs in raw.values():
            for r in rs:
                by_q[r["quire"]].append(r["words"])
        for q in QUIRES_15:
            ho = [w for ln in by_q[q] for w in ln]
            trw = [w for qk in QUIRES_15 if qk != q for ln in by_q[qk] for w in ln]
            vq[(tr, q)] = dict(n=len(ho), m=len(trw), lines=len(by_q[q]), r=rp1(ho, trw))
            for cname in ("CREMMA_all", PROSE_NAME):
                for k in range(N_DRAWS):
                    tasks.append((cname, tr, q, len(ho), len(trw), k))
    s86_cut = 0.703
    emit("--- reproduction check of s86 3B-3 (R_P1 < 0.703 whole-corpus) ---")
    for tr in TRANSLITS:
        v = [vq[(tr, q)]["r"] for q in QUIRES_15]
        emit(f"  {tr}: {sum(1 for x in v if not math.isnan(x) and x < s86_cut)}/15 below 0.703, median {np.nanmedian(v):.3f}")
    emit()

    emit(f"--- control draws: {len(tasks)} tasks on {N_WORKERS} workers ---")
    with Pool(N_WORKERS, initializer=_init) as pool:
        draws = pool.map(draw_task, tasks, chunksize=50)
    with (RUNS / "control_draws.tsv").open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("control\ttranslit\tquire\tdraw\tn_tok\tm_ref\tn_lines\tR_P1\n")
        for d in draws:
            fh.write("\t".join(str(x) for x in d) + "\n")
    cd = defaultdict(list)
    cl = defaultdict(list)
    for cname, tr, q, k, n, m_eff, nl, r in draws:
        cd[(cname, tr, q)].append(r)
        cl[(cname, tr, q)].append(nl)
    emit(f"  done in {time.time() - t0:.0f}s")
    emit()

    from scipy.stats import spearmanr
    calls = {}
    rows = []
    for cname in ("CREMMA_all", PROSE_NAME):
        emit(f"=== control: {cname} ({'copied Latin, PRIMARY' if cname == 'CREMMA_all' else 'edited non-copied Latin prose, secondary'}) ===")
        for tr in TRANSLITS:
            emit(f"  {tr}: quire  n_tok  lines | ctrl_lines | Voy R_P1 | ctrl med   p05   p95  nan% | <med <p05")
            nb_med = nb_p05 = 0
            for q in QUIRES_15:
                v = vq[(tr, q)]
                arr = np.array(cd[(cname, tr, q)], dtype=float)
                ok = arr[~np.isnan(arr)]
                nanf = 1 - len(ok) / len(arr)
                if len(ok) and nanf <= NAN_MAX:
                    med, p05, p95 = np.median(ok), np.percentile(ok, 5), np.percentile(ok, 95)
                else:
                    med = p05 = p95 = float("nan")
                below_med = (not math.isnan(v["r"])) and (not math.isnan(med)) and v["r"] < med
                below_p05 = (not math.isnan(v["r"])) and (not math.isnan(p05)) and v["r"] < p05
                nb_med += below_med
                nb_p05 += below_p05
                rows.append((cname, tr, q, v["n"], v["m"], v["lines"], float(np.mean(cl[(cname, tr, q)])), v["r"], med, p05, p95, nanf, below_med, below_p05))
                emit(f"        {q:>5} {v['n']:6d} {v['lines']:6d} | {np.mean(cl[(cname, tr, q)]):10.0f} | {v['r']:8.3f} | {med:8.3f} {p05:5.3f} {p95:5.3f} {100*nanf:4.0f} | {'Y' if below_med else '.':>4} {'Y' if below_p05 else '.':>4}")
            calls[(cname, tr)] = (nb_med, nb_p05)
            emit(f"    {tr}: below matched median {nb_med}/15 ; below matched 5th pct {nb_p05}/15")
        # size dependence
        xs, ys = [], []
        for (c2, tr, q), lst in cd.items():
            if c2 != cname:
                continue
            for r in lst:
                if not math.isnan(r):
                    xs.append(vq[(tr, q)]["n"])
                    ys.append(r)
        rho, p = spearmanr(xs, ys)
        sized = abs(rho) >= RHO_MIN and p < RHO_P
        calls[(cname, "S")] = (rho, p, sized)
        by_n = defaultdict(list)
        for x, y in zip(xs, ys):
            by_n[x].append(y)
        small = [y for x in sorted(by_n)[:5] for y in by_n[x]]
        big = [y for x in sorted(by_n)[-5:] for y in by_n[x]]
        emit(f"  S[{cname}]: Spearman rho(n_tok, R_P1) = {rho:+.3f}, p = {p:.2e}, n = {len(xs)} draws; "
             f"median R_P1 at 5 smallest sizes {np.median(small):.3f} vs 5 largest {np.median(big):.3f}; size-dependent = {sized}")
        emit()

    # Voynich size dependence (descriptive)
    vx = [vq[(tr, q)]["n"] for tr in TRANSLITS for q in QUIRES_15 if not math.isnan(vq[(tr, q)]["r"])]
    vy = [vq[(tr, q)]["r"] for tr in TRANSLITS for q in QUIRES_15 if not math.isnan(vq[(tr, q)]["r"])]
    vr, vp = spearmanr(vx, vy)
    emit(f"  Voynich (descriptive, 45 quire-translit points): rho(n_tok, R_P1) = {vr:+.3f}, p = {vp:.2e}")
    emit()

    with (RUNS / "per_quire.tsv").open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("control\ttranslit\tquire\tn_tok\tm_ref\tlines\tctrl_mean_lines\tvoy_R_P1\tctrl_median\tctrl_p05\tctrl_p95\tctrl_nan_frac\tbelow_median\tbelow_p05\n")
        for r in rows:
            fh.write("\t".join(f"{x:.4f}" if isinstance(x, float) else str(x) for x in r) + "\n")

    emit("=" * 100)
    emit("PRE-REGISTERED CALLS")
    c1 = all(calls[("CREMMA_all", tr)][0] >= C_MIN for tr in TRANSLITS)
    c2 = all(calls[("CREMMA_all", tr)][1] >= C_MIN for tr in TRANSLITS)
    for tr in TRANSLITS:
        a, b = calls[("CREMMA_all", tr)]
        pa, pb = calls[(PROSE_NAME, tr)]
        emit(f"  {tr}: CREMMA_all below median {a}/15, below p05 {b}/15 | {PROSE_NAME} (descriptive) below median {pa}/15, below p05 {pb}/15")
    emit(f"  F0 fixture pass = {f0}")
    emit(f"  C1 (below size-matched copied-Latin median on >= {C_MIN}/15, all 3 translits) = {c1}")
    emit(f"  C2 (below size-matched copied-Latin 5th pct on >= {C_MIN}/15, all 3 translits) = {c2}")
    for cname in ("CREMMA_all", PROSE_NAME):
        rho, p, sized = calls[(cname, "S")]
        emit(f"  S[{cname}] size-dependent (|rho| >= {RHO_MIN}, p < {RHO_P}) = {sized} (rho {rho:+.3f})")
    if c1 and c2:
        v = "F-21 HOLDS PER QUIRE: Voynich R_P1 is below the size-matched copied-Latin median and 5th percentile on >= 8/15 quires on all three transliterations"
    elif c1:
        v = "F-21 HOLDS PER QUIRE AT THE MEDIAN (C1) BUT NOT AT THE STRICT 5th-PERCENTILE BAR (C2): weakly separated from copied Latin per quire"
    else:
        v = "F-21 DOES NOT HOLD PER QUIRE (C1 False): Voynich R_P1 is not below the size-matched copied-Latin median on >= 8/15 quires on all three transliterations"
    emit(f"finished {clock()}; elapsed {time.time() - t0:.0f}s")
    emit(f"VERDICT: C1={c1} C2={c2} -> {v}")
    flush()


if __name__ == "__main__":
    main()
