"""s101 -- Leave-One-Quire-Out (LOQO) Power Audit of Producer Exclusions (F-23, F-30, F-34, F-41).

PRE-REGISTERED (frozen in s101_loqo_power_audit.prereg.sha256 BEFORE any planted run on Voynich-fitted parameters;
before the freeze this script ran only on its synthetic fixture `--s101-fixture`, which reads no Voynich data).

QUESTION (Red-Team Risk 2 / RT-5, workflow/research/next-steps-redteam-2026-10-18.md):
Several findings exclude a producer family because it matched Voynich on 0/15 or < 8/15 held-out quires:
  - F-23: lexical producers s57 (local-memory copy-and-vary), s58 (two-layer independent affix wrapper TL),
          s61 (joint whole-word producer JW), and s67 (constrained assembly with length cadence CA).
  - F-30: weakened table-and-grille WTG_global and WTG_scribe (s71).
  - F-34: per-line sticky Naibbe cipher line_sticky_fit and line_sticky75 vs per-word tables (s81, C1 >= 5/6
          battery exclusion and C2 s69 prefix-memory call-pattern match).
  - F-41: per-line core-pool producer LP91 (s91, C1 four-part core signature and C2 combined LP91+s81 word battery).
An exclusion is informative only if the LOQO test can PASS a correctly specified planted instance of that producer.

PROTOCOL:
1. For each excluded producer family and each transliteration T in (ZL3b, RF1b, IT2a), generate a planted manuscript
   from that same producer, with parameters fitted to Voynich training quires, on Voynich's exact page, line, and
   quire structure.
2. Run the IDENTICAL pipeline, fit, and LOQO scoring each original run used on the planted text, importing the
   original functions verbatim (from s57_local_memory_model, s58_two_layer_heldout, s61_joint_word_producer,
   s67_constrained_assembly_loqo, s71_weakened_grille_and_sticky_naibbe_loqo, s81_sticky_table_loqo,
   s87_core_layer_genre, and s91_line_pool_producer_loqo). Do not reimplement.
3. Report recovery: on how many of 15 folds (x/15) the producer is called a match to its own planted text on each
   transliteration (ZL3b, RF1b, IT2a).
4. PRE-REGISTERED DECISION RULE (written before running):
   For a given producer family and transliteration (15 LOQO folds), let r in {0..15} be the number of folds on
   which the original LOQO pass criterion calls the producer a match to its own planted text:
     - POWERED       if r >= 10   (>= 10/15 folds recovered)
     - WEAK          if 5 <= r <= 9 (5-9/15 folds recovered)
     - UNINFORMATIVE if r <= 4    (<= 4/15 folds recovered)
   Family-level cross-transliteration call uses the same thresholds on min_T r(T) (and prints the call for every
   individual transliteration ZL3b, RF1b, IT2a as well as the family call).

COMPUTE & GOVERNANCE:
- At most 2 worker processes at BelowNormal priority; OMP/MKL/OPENBLAS threads = 1.
- RTX 5080 via torch cuda; torch.cuda.empty_cache() called between folds.
- Free RAM >= 4.0 GB checked before starting.
- Every timestamp stamped from `date`.
- Writes ONLY results_s101.txt and runs/s101/ sidecars (fixture writes ONLY runs/s101/fixture.txt). Never overwrites.

Run:
  Fixture:     python -I s101_loqo_power_audit.py --s101-fixture
  Stub helper: python -I s101_loqo_power_audit.py --list-locals
  Main audit:  python -I s101_loqo_power_audit.py
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import multiprocessing as mp  # noqa: E402
import random  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import Counter, OrderedDict, defaultdict  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import torch  # noqa: E402

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

# Verbatim imports of original producer and LOQO scoring modules (do not reimplement)
import g1_edge_joint as G1  # noqa: E402
import s57_local_memory_model as S57  # noqa: E402
import s58_two_layer_heldout as S58  # noqa: E402
import s61_joint_word_producer as S61  # noqa: E402
import s67_constrained_assembly_loqo as S67  # noqa: E402
import s69_prefix_stream_memory as S69  # noqa: E402
import s71_weakened_grille_and_sticky_naibbe_loqo as S71  # noqa: E402
import s81_sticky_table_loqo as S81  # noqa: E402
import s87_core_layer_genre as S87  # noqa: E402
import s91_line_pool_producer_loqo as S91  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s101_loqo_power_audit.py"
STUB = ROOT / "s101_loqo_power_audit.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s101"
FIXTURE = "--s101-fixture" in sys.argv
LIST_LOCALS = "--list-locals" in sys.argv
OUT = (RUN_DIR / "fixture.txt") if FIXTURE else (ROOT / "results_s101.txt")

SEED = 20261017
PLANT_SEED = 101000
N_WORKERS = 2
MIN_FREE_GB = 4.0
TRANSLITS = OrderedDict([("ZL3b", "ZL3b_eva"), ("RF1b", "RF1b"), ("IT2a", "IT2a")])
PREDS = S67.PREDS  # ["P1", "P2", "P3", "P4", "P5", "P7"]

DATA_FILES = [
    "data/translit/ZL3b_eva.meta.json",
    "data/translit/RF1b.meta.json",
    "data/translit/IT2a.meta.json",
    "data/ZL3b-n.txt",
    "data/external/voynich-nu-ivtff/RF1b-er.txt",
    "data/external/voynich-nu-ivtff/IT2a-n.txt",
    "data/naibbe_zenodo_17219445/Naibbe_Cipher.xlsx",
    "runs/s49/lang_latin_cremma.meta.json",
    "runs/s49/lang_italian_dante.meta.json",
    "runs/s57/fit_ZL3b.json",
    "runs/s57/fit_RF1b.json",
    "runs/s57/fit_IT2a.json",
    "runs/s58/fit_ZL3b.json",
    "runs/s58/fit_RF1b.json",
    "runs/s58/fit_IT2a.json",
    "runs/s61/fit_ZL3b.json",
    "runs/s61/fit_RF1b.json",
    "runs/s61/fit_IT2a.json",
    "runs/s67/cells.json",
    "runs/s81/cells.json",
    "runs/s91/calls.json",
]

log: list[str] = []
T0 = time.time()


def emit(s: str = "") -> None:
    print(s, flush=True)
    log.append(s)


def flush_checkpoint(tag: str) -> None:
    """Write checkpoint copy inside runs/s101/ without overwriting final OUT until completion."""
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    cp = RUN_DIR / f"checkpoint_{tag}.txt"
    cp.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


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


def below_normal() -> bool:
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.GetCurrentProcess.restype = ctypes.c_void_p
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        return bool(k.SetPriorityClass(k.GetCurrentProcess(), 0x00004000))  # BELOW_NORMAL_PRIORITY_CLASS
    except Exception:  # noqa: BLE001
        return False


def free_gb() -> float:
    try:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        m = MS()
        m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPhys / (2 ** 30)
    except Exception:  # noqa: BLE001
        return float("nan")


def empty_cuda() -> None:
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def worker_init() -> None:
    below_normal()
    try:
        torch.set_num_threads(1)
    except Exception:  # noqa: BLE001
        pass


def local_modules() -> list[str]:
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


def stub_files() -> list[str]:
    return local_modules() + list(DATA_FILES)


def stub_match() -> str:
    if not STUB.exists():
        return "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = ln.split(None, 1)
        if len(parts) < 2 or len(parts[0]) != 64:
            continue
        h, f = parts
        want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    missing = [m for m in stub_files() if m not in want]
    ok = bool(want) and not bad and not missing
    return "True" if ok else f"False (mismatch: {', '.join(bad) or '-'}; not in stub: {', '.join(missing) or '-'})"


# ==============================================================================
# PRE-REGISTERED POWER CALL RULE (FROZEN BEFORE RUNNING)
# ==============================================================================
def power_call(r: int, n_folds: int = 15) -> str:
    """Pre-registered rule (for 15 folds):
      - POWERED       if r >= 10
      - WEAK          if 5 <= r <= 9
      - UNINFORMATIVE if r <= 4
    For synthetic fixture with n_folds != 15, scales thresholds proportionally:
      powered >= ceil(10 * n_folds / 15), weak >= ceil(5 * n_folds / 15).
    """
    if n_folds == 15:
        if r >= 10:
            return "POWERED"
        if r >= 5:
            return "WEAK"
        return "UNINFORMATIVE"
    t_pow = math.ceil(10 * n_folds / 15)
    t_weak = math.ceil(5 * n_folds / 15)
    if r >= t_pow:
        return "POWERED"
    if r >= t_weak:
        return "WEAK"
    return "UNINFORMATIVE"


def recentred_holds(cells: dict, gen_pt: dict, real_pt: dict) -> dict[str, bool]:
    """Non-gating diagnostic: s81_sticky_table_loqo.py (lines 367-371) re-centring of P4 and P5 on the planted text."""
    hw = (S57.S15_JSD[1] - S57.S15_JSD[0]) / 2.0
    out = {k: bool(cells[k][0]) for k in PREDS}
    out["P4"] = abs(gen_pt["P4"] - real_pt["P4"]) <= hw
    out["P5"] = (gen_pt["P5"] > 0) == (real_pt["P5"] > 0)
    return out


# ==============================================================================
# PLANTING HELPERS (FITTED TO VOYNICH TRAINING QUIRES)
# ==============================================================================
def load_voynich_fitted_params() -> dict:
    """Load parameters fitted to Voynich training pages/quires by the original s57, s58, s61, s67, s71, s81, s91 runs."""
    s67_cells = json.loads((ROOT / "runs" / "s67" / "cells.json").read_text(encoding="utf-8"))
    s81_cells = json.loads((ROOT / "runs" / "s81" / "cells.json").read_text(encoding="utf-8"))
    out = {"s57": {}, "s58": {}, "s61": {}, "s67": {}, "s71": dict(S71.WTG_PARAMS), "s81": {}, "s91": {}}
    for T in TRANSLITS:
        out["s57"][T] = json.loads((ROOT / "runs" / "s57" / f"fit_{T}.json").read_text(encoding="utf-8"))["params"]
        out["s58"][T] = json.loads((ROOT / "runs" / "s58" / f"fit_{T}.json").read_text(encoding="utf-8"))["params"]
        out["s61"][T] = json.loads((ROOT / "runs" / "s61" / f"fit_{T}.json").read_text(encoding="utf-8"))["params"]["JW"]
        # s67 CA: median fitted parameters across the 15 training-quire folds of T
        ca_prms = [s67_cells[k]["params"]["CA"] for k in sorted(s67_cells) if k.startswith(f"{T}|")]
        out["s67"][T] = {k: float(np.median([p[k] for p in ca_prms])) for k in S67.KEYS}
        # s81 line_sticky_fit|latin_cremma: median fitted p across the 15 training-quire folds of T
        p_vals = [
            s81_cells[k]["models"]["line_sticky_fit|latin_cremma"]["p"]
            for k in sorted(s81_cells)
            if k.startswith(f"{T}|")
        ]
        out["s81"][T] = float(np.median(p_vals))
        # s91 LP91: median fitted parameters across the 15 training-quire folds of T
        s91_prms = [
            json.loads(p.read_text(encoding="utf-8"))["fit"]["params"]
            for p in sorted((ROOT / "runs" / "s91" / "folds").glob(f"{T}_*.json"))
        ]
        out["s91"][T] = {k: float(np.median([p[k] for p in s91_prms])) for k in S91.KEYS}
    return out


# ==============================================================================
# WORKERS FOR EACH ORIGINAL LOQO PIPELINE
# ==============================================================================
def fit_lexical_split_worker(job: dict) -> dict:
    """Fit s57, s58, or s61 on the planted manuscript's G1.split_names training split using S57.fit / S58.fit / S61.fit."""
    below_normal()
    t0 = time.time()
    fam = job["fam"]
    T = job["T"]
    pages = job["pages"]  # [(pid, quire, lines)]
    by = OrderedDict((pid, ls) for pid, _, ls in pages)
    train_names, _ = G1.split_names(by)
    tr_pages = [by[p] for p in train_names]
    seg = SlotSegmenter([w for ls in tr_pages for l in ls for w in l])
    if fam == "s57":
        F = S57.fit(tr_pages, seg, lambda _s: None, time.time())
    elif fam == "s58":
        F = S58.fit(tr_pages, seg, lambda _s: None, time.time())
    elif fam == "s61":
        F = S61.fit(tr_pages, seg, lambda _s: None, time.time(), use_state=True)
    else:
        raise ValueError(fam)
    empty_cuda()
    return dict(fam=fam, T=T, params=F["params"], loss=float(F["loss"]), n_evals=int(F["n_evals"]), secs=time.time() - t0)


def run_lexical_loqo_fold_worker(job: dict) -> dict:
    """Run one LOQO fold (T, Q) for s57, s58, or s61 on its planted manuscript using S57.Measured, S57.draws_for, S67.score_model."""
    below_normal()
    t0 = time.time()
    S57.N_DRAW = S67.N_DRAW
    fam = job["fam"]
    T = job["T"]
    Q = job["Q"]
    pages = job["pages"]
    prm = job["params"]
    off = job["off"]

    train = [(p, ls) for p, q, ls in pages if q != Q]
    test = [(p, ls) for p, q, ls in pages if q == Q]
    tr_pages = [ls for _, ls in train]
    seg = SlotSegmenter([w for ls in tr_pages for l in ls for w in l])
    tr_counts = [len(ls) for ls in tr_pages]
    te_counts = [len(ls) for _, ls in test]

    if fam == "s57":
        prod = S57.Producer(tr_pages, seg)
    elif fam == "s58":
        prod = S58.TLProducer(tr_pages, seg)
    elif fam == "s61":
        prod = S61.JWProducer(tr_pages, seg, use_state=True)
    else:
        raise ValueError(fam)
    prod.set_params(prm)

    gens = []
    for s in S67.SEEDS:
        pg = prod.text(s, tr_counts + te_counts)
        gtr = [(f"g{i}", pg[i]) for i in range(len(train))]
        gte = [(f"h{i}", pg[len(train) + i]) for i in range(len(test))]
        gens.append((gtr, gte))

    real_m = S57.Measured(f"{T} {Q} {fam} planted", train, test)
    ms = [S57.Measured(f"{T} {Q} {fam} gen s{i}", a, b) for i, (a, b) in enumerate(gens)]
    real_dr = S57.draws_for([real_m], S67.SEED + off)
    real_pt = real_m.point()
    gen_dr = S57.draws_for(ms, S67.SEED + off + 1)
    real_test_pages = [ls for _, ls in test]
    cells, gen_pt, rt, small = S67.score_model(
        real_m, real_pt, real_dr, ms, gen_dr, len(test), [[ls for _, ls in b] for _, b in gens], real_test_pages
    )
    holds = {k: bool(cells[k][0]) for k in PREDS}
    rec_holds = recentred_holds(cells, gen_pt, real_pt)
    # Also compute S57.score_cells P1..P6 count
    cells_p16 = S57.score_cells(real_pt, real_dr, gen_pt, gen_dr)
    n_p16 = sum(1 for k in ("P1", "P2", "P3", "P4", "P5", "P6") if cells_p16[k][0])
    empty_cuda()
    return dict(
        fam=fam,
        T=T,
        Q=Q,
        n_test=len(test),
        n=sum(1 for k in PREDS if holds[k]),
        n_rec=sum(1 for k in PREDS if rec_holds[k]),
        n_p16=n_p16,
        holds=holds,
        rec_holds=rec_holds,
        real_pt={k: float(v) for k, v in real_pt.items()},
        gen_pt={k: float(v) for k, v in gen_pt.items()},
        type_ratio=float(rt),
        small=bool(small),
        secs=time.time() - t0,
    )


def run_s67_ca_fold_worker(job: dict) -> dict:
    """Run one LOQO fold (T, Q) of s67 CA (and CA0) on its planted manuscript using S67.fit, S67.CAProducer, S57.Measured, S67.score_model."""
    below_normal()
    t0 = time.time()
    S57.N_DRAW = job.get("n_draw", S67.N_DRAW)
    T = job["T"]
    Q = job["Q"]
    pages = job["pages"]
    off = job["off"]
    grids = job.get("grids")

    train = [(p, ls) for p, q, ls in pages if q != Q]
    test = [(p, ls) for p, q, ls in pages if q == Q]
    tr_pages = [ls for _, ls in train]
    seg = SlotSegmenter([w for ls in tr_pages for l in ls for w in l])

    F = S67.fit(tr_pages, seg, use_class=True, grids=grids)
    params = {"CA": F["params"], "CA0": F["p0"]}
    tr_counts = [len(ls) for ls in tr_pages]
    te_counts = [len(ls) for _, ls in test]
    prod = S67.CAProducer(tr_pages, seg, True)
    gens = {}
    for m in ("CA", "CA0"):
        prod.set_params(params[m])
        gens[m] = []
        for s in S67.SEEDS:
            pg = prod.text(s, tr_counts + te_counts)
            gtr = [(f"g{i}", pg[i]) for i in range(len(train))]
            gte = [(f"h{i}", pg[len(train) + i]) for i in range(len(test))]
            gens[m].append((gtr, gte))

    real_m = S57.Measured(f"{T} {Q} s67 planted", train, test)
    real_dr = S57.draws_for([real_m], S67.SEED + off)
    real_pt = real_m.point()
    real_test_pages = [ls for _, ls in test]

    models_out = {}
    for j, m in enumerate(("CA", "CA0")):
        ms = [S57.Measured(f"{T} {Q} {m} s{i}", a, b) for i, (a, b) in enumerate(gens[m])]
        gen_dr = S57.draws_for(ms, S67.SEED + off + 1 + j)
        cells, gen_pt, rt, small = S67.score_model(
            real_m, real_pt, real_dr, ms, gen_dr, len(test), [[ls for _, ls in b] for _, b in gens[m]], real_test_pages
        )
        holds = {k: bool(cells[k][0]) for k in PREDS}
        rec_holds = recentred_holds(cells, gen_pt, real_pt)
        models_out[m] = dict(
            n=sum(1 for k in PREDS if holds[k]),
            n_rec=sum(1 for k in PREDS if rec_holds[k]),
            holds=holds,
            rec_holds=rec_holds,
            gen_pt={k: float(v) for k, v in gen_pt.items()},
            type_ratio=float(rt),
            small=bool(small),
            params=params[m],
        )
    empty_cuda()
    return dict(
        T=T,
        Q=Q,
        n_test=len(test),
        fit_loss=float(F["loss"]),
        fit_evals=int(F["n_evals"]),
        real_pt={k: float(v) for k, v in real_pt.items()},
        models=models_out,
        secs=time.time() - t0,
    )


def run_s71_wtg_fold_worker(job: dict) -> dict:
    """Run one LOQO fold (T, Q) of s71 WTG on its planted manuscript using S71.run_loqo_fold_worker."""
    below_normal()
    r = S71.run_loqo_fold_worker(job)
    # Add non-gating recentred diagnostic for WTG_global and WTG_scribe
    real_pt = r["real_point"]
    hw = (S57.S15_JSD[1] - S57.S15_JSD[0]) / 2.0
    for m_name in ("WTG_global", "WTG_scribe"):
        md = r["models"][m_name]
        gpt = md["gen_point"]
        rec_h = dict(md["holds"])
        rec_h["P4"] = abs(gpt["P4"] - real_pt["P4"]) <= hw
        rec_h["P5"] = (gpt["P5"] > 0) == (real_pt["P5"] > 0)
        md["rec_holds"] = rec_h
        md["n_rec"] = sum(1 for k in PREDS if rec_h[k])
    empty_cuda()
    return r


def run_s81_sticky_fold_worker(job: dict) -> dict:
    """Run one LOQO fold (T, Q) of s81 sticky Naibbe on its planted manuscript using S81.run_fold verbatim."""
    below_normal()
    # Restrict S81.VARIANTS in worker to the tested sticky Naibbe + default comparators
    S81.VARIANTS = [
        ("line_sticky75", "latin_cremma"),
        ("line_sticky_fit", "latin_cremma"),
        ("default", "latin_cremma"),
    ]
    r = S81.run_fold(job)
    # Also compute recentred P4/P5 diagnostic (S81's own fixture rule from lines 367-371)
    real_pt = r["real_point"]
    hw = (S57.S15_JSD[1] - S57.S15_JSD[0]) / 2.0
    for nm, md in r["models"].items():
        # Extract gen_pt P4 and P5 from md['text'] or recompute sign/distance
        rec_h = dict(md["holds"])
        # Parse gen P4 and P5 from text strings formatted by S57.score_cells
        try:
            # P4 text: "jsd_first_fg gen 0.XXXX vs s15 width ..."
            g4 = float(md["text"]["P4"].split("gen ")[1].split()[0])
            rec_h["P4"] = abs(g4 - real_pt["P4"]) <= hw
        except Exception:  # noqa: BLE001
            pass
        try:
            # P5 text: "CHARWIN gen +0.XXXX (real ...)"
            g5 = float(md["text"]["P5"].split("gen ")[1].split()[0])
            rec_h["P5"] = (g5 > 0) == (real_pt["P5"] > 0)
        except Exception:  # noqa: BLE001
            pass
        md["rec_holds"] = rec_h
        md["n_rec"] = sum(1 for k in PREDS if rec_h[k])
    empty_cuda()
    return r


def run_s91_lp91_fold_worker(job: dict) -> dict:
    """Run one LOQO fold (T, Q) of s91 LP91 on its planted manuscript using S91.run_fold verbatim."""
    below_normal()
    r = S91.run_fold(job)
    empty_cuda()
    return r


# ==============================================================================
# SYNTHETIC FIXTURE (--s101-fixture; NO VOYNICH DATA READ)
# ==============================================================================
def run_fixture() -> bool:
    emit("s101 FIXTURE (synthetic only; no Voynich data read)")
    emit(f"date: {clock()}")
    fg = free_gb()
    emit(f"device: {S87.DEV} ({torch.cuda.get_device_name(0) if S87.DEV.type == 'cuda' else 'cpu'}); "
         f"below_normal={below_normal()}; free RAM={fg:.1f} GB; stub_match={stub_match()}")
    if fg < MIN_FREE_GB:
        emit(f"STOP: free RAM {fg:.1f} GB < {MIN_FREE_GB} GB")
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
        return False

    # Synthetic 6-quire world (6 quires A..F x 8 pages x 10 lines)
    rng = random.Random(101)
    alph = "acdehiklnorsty"
    pres = ["", "q", "o", "ch", "sh", "d"]
    sufs = ["", "y", "dy", "in", "ol", "r"]
    cores = sorted({"".join(rng.choice(alph) for _ in range(rng.randint(2, 4))) for _ in range(250)})
    fam = {c: rng.randrange(4) for c in cores}
    fam_pre = [rng.sample(pres, 3) for _ in range(4)]
    fam_suf = [rng.sample(sufs, 3) for _ in range(4)]
    cw = [1.0 / ((1 + i) ** 0.85) for i in range(len(cores))]

    base_pages = []
    for _pg in range(48):
        page = []
        for _li in range(10):
            ln = []
            for _wi in range(rng.randint(5, 9)):
                c = rng.choices(cores, cw)[0]
                f = fam[c]
                ln.append(rng.choice(fam_pre[f]) + c + rng.choice(fam_suf[f]))
            page.append(ln)
        base_pages.append(page)

    seg0 = SlotSegmenter([w for ls in base_pages for l in ls for w in l])
    truth = dict(p_rep=0.15, tau=4.0, gamma=1.0, rho=0.5)
    pr = S67.CAProducer(base_pages, seg0, True)
    pr.set_params(truth)
    gpages = pr.text(101, [10] * 48)
    quires = [chr(ord("A") + i // 8) for i in range(48)]
    planted_pages = [(f"fx{i:02d}", quires[i], ls) for i, ls in enumerate(gpages)]
    folds = sorted(set(quires))

    small_grids = ([0.0, 0.15, 0.3], [4.0, 12.0], [0.0, 1.0], [0.0, 0.5])
    rec_cnt = 0
    raw_cnt = 0
    for fi, Q in enumerate(folds):
        r = run_s67_ca_fold_worker(dict(T="FX", Q=Q, pages=planted_pages, off=500 + 10 * fi, grids=small_grids, n_draw=30))
        m_ca = r["models"]["CA"]
        if m_ca["n"] >= 5:
            raw_cnt += 1
        if m_ca["n_rec"] >= 5:
            rec_cnt += 1
        emit(f"  fixture fold {Q}: raw {m_ca['n']}/6, recentred {m_ca['n_rec']}/6, fitted {m_ca['params']}")

    call_raw = power_call(raw_cnt, len(folds))
    call_rec = power_call(rec_cnt, len(folds))
    ok = (rec_cnt >= math.ceil(10 * len(folds) / 15)) and (call_raw in ("POWERED", "WEAK", "UNINFORMATIVE"))
    emit(f"fixture summary: raw={raw_cnt}/{len(folds)} ({call_raw}), recentred={rec_cnt}/{len(folds)} ({call_rec})")
    emit(f"FIXTURE {'PASS' if ok else 'FAIL'} ({time.time() - T0:.1f}s; date {clock()})")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    return ok


# ==============================================================================
# MAIN POWER AUDIT EXECUTION
# ==============================================================================
def main() -> int:
    if LIST_LOCALS:
        for f in stub_files():
            print(f)
        return 0
    if FIXTURE:
        return 0 if run_fixture() else 1

    below_normal()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite existing {OUT}")

    fg = free_gb()
    emit("s101 -- Leave-One-Quire-Out (LOQO) Power Audit of Producer Exclusions (F-23, F-30, F-34, F-41)")
    emit(f"date start: {clock()}")
    emit(f"device: {S87.DEV} ({torch.cuda.get_device_name(0) if S87.DEV.type == 'cuda' else 'cpu'}); "
         f"torch {torch.__version__}; numpy {np.__version__}; python {sys.version.split()[0]}; "
         f"priority BelowNormal={below_normal()}; workers={N_WORKERS}; free RAM={fg:.2f} GB (req >= {MIN_FREE_GB} GB)")
    emit(f"sha256 {SELF.name}: {sha256(SELF)}")
    emit(f"sha256 {STUB.name}: {sha256(STUB) if STUB.exists() else 'missing'}")
    sm = stub_match()
    emit(f"stub_match: {sm}")
    for f in stub_files():
        p = ROOT / f
        emit(f"  hashed {f} sha256={sha256(p) if p.exists() else 'MISSING'}")
    emit("")
    emit("PRE-REGISTERED DECISION RULE (frozen before running):")
    emit("  For each excluded producer family on 15 LOQO folds, let recovery r in {0..15} be the number of folds")
    emit("  where the original LOQO pipeline calls the producer a match to its own planted text:")
    emit("    - POWERED       if r >= 10/15")
    emit("    - WEAK          if 5/15 <= r <= 9/15")
    emit("    - UNINFORMATIVE if r <= 4/15")
    emit("")
    if fg < MIN_FREE_GB:
        emit(f"STOP: free RAM {fg:.2f} GB < {MIN_FREE_GB} GB; aborting.")
        OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
        return 1

    # Load Voynich transliterations & training-quire fitted parameters
    voy_pages_by_T: dict[str, list[tuple[str, str, list[list[str]]]]] = {}
    voy_meta_by_T: dict[str, list[dict]] = {}
    for T, fn in TRANSLITS.items():
        voy_pages_by_T[T] = S67.load_pages(ROOT / "data" / "translit" / f"{fn}.meta.json")
        voy_meta_by_T[T] = S71.load_translit_meta(T)
    folds = S67.folds_of(voy_pages_by_T["ZL3b"])
    emit(f"Folds (15 quires with >= 4 pages in ZL3b): {folds} ({len(folds)} folds)")
    voy_prm = load_voynich_fitted_params()
    emit("Loaded Voynich training-quire fitted parameters for planting:")
    for fam_k in ("s57", "s58", "s61", "s67", "s81", "s91"):
        emit(f"  {fam_k}: {voy_prm[fam_k]}")
    emit(f"  s71 WTG: {voy_prm['s71']}")
    emit("")

    # Generate planted manuscripts for every excluded producer family across ZL3b, RF1b, IT2a
    emit("Generating planted manuscripts (fitted to Voynich training quires q != 'A', exact Voynich page/line/quire structure)...")
    planted_s57 = {}
    planted_s58 = {}
    planted_s61 = {}
    planted_s67 = {}
    planted_wtg_global = {}
    planted_wtg_scribe = {}
    planted_s81 = {}
    planted_s81_p69 = {}
    planted_s91_words = {}
    planted_s91_cores = {}

    K_naibbe = S81.key_tables()
    letters_lat = S81.plain_letters("latin_cremma")

    for ti, T in enumerate(TRANSLITS):
        vp = voy_pages_by_T[T]
        vm = voy_meta_by_T[T]
        tr_voy = [ls for _, q, ls in vp if q != "A"]
        seg_voy = SlotSegmenter([w for ls in tr_voy for l in ls for w in l])
        counts_all = [len(ls) for _, _, ls in vp]
        skel_all = [[len(l) for l in ls] for _, _, ls in vp]

        # 1. s57 planted
        p57 = S57.Producer(tr_voy, seg_voy)
        p57.set_params(voy_prm["s57"][T])
        l57 = p57.text(PLANT_SEED + 570 + ti, counts_all)
        planted_s57[T] = [(vp[i][0], vp[i][1], l57[i]) for i in range(len(vp))]

        # 2. s58 planted
        p58 = S58.TLProducer(tr_voy, seg_voy)
        p58.set_params(voy_prm["s58"][T])
        l58 = p58.text(PLANT_SEED + 580 + ti, counts_all)
        planted_s58[T] = [(vp[i][0], vp[i][1], l58[i]) for i in range(len(vp))]

        # 3. s61 planted
        p61 = S61.JWProducer(tr_voy, seg_voy, use_state=True)
        p61.set_params(voy_prm["s61"][T])
        l61 = p61.text(PLANT_SEED + 610 + ti, counts_all)
        planted_s61[T] = [(vp[i][0], vp[i][1], l61[i]) for i in range(len(vp))]

        # 4. s67 CA planted
        p67 = S67.CAProducer(tr_voy, seg_voy, use_class=True)
        p67.set_params(voy_prm["s67"][T])
        l67 = p67.text(PLANT_SEED + 670 + ti, counts_all)
        planted_s67[T] = [(vp[i][0], vp[i][1], l67[i]) for i in range(len(vp))]

        # 5. s71 WTG_global & WTG_scribe planted
        tr_meta_voy = [p for p in vm if p["quire"] != "A"]
        wtg_prod = S71.WTGProducer(tr_meta_voy, seg_voy, S71.WTG_PARAMS)
        rng_g = random.Random(PLANT_SEED + 710 + ti)
        rng_s = random.Random(PLANT_SEED + 715 + ti)
        pg_g, pg_s = [], []
        for p in vm:
            ll = [len(ln) for ln in p["lines"]]
            pf = p.get("para")
            lines_g = wtg_prod.generate_page(rng_g, len(p["lines"]), hand="ALL", line_lens=ll, para_flags=pf)
            lines_s = wtg_prod.generate_page(rng_s, len(p["lines"]), hand=p["hand"], line_lens=ll, para_flags=pf)
            pg_g.append(dict(p, lines=lines_g))
            pg_s.append(dict(p, lines=lines_s))
        planted_wtg_global[T] = pg_g
        planted_wtg_scribe[T] = pg_s

        # 6. s81 line_sticky (p = fitted Voynich median = 0.75) planted
        l81 = S81.encipher(letters_lat, K_naibbe, skel_all, "line", voy_prm["s81"][T], seed=PLANT_SEED + 810 + ti)
        planted_s81[T] = [(vp[i][0], vp[i][1], l81[i]) for i in range(len(vp))]
        planted_s81_p69[T] = [dict(id=vp[i][0], lines=l81[i], gaps=None, para=None) for i in range(len(vp))]

        # 7. s91 LP91 planted (both core stream and combined LP91 + s81 word stream)
        ctrain_voy = [(p, q, [[seg_voy.segment(w)[1] for w in l] for l in ls]) for p, q, ls in vp if q != "A"]
        glob_voy = Counter(c for _, _, ls in ctrain_voy for l in ls for c in l if c)
        B_voy = S91.bigram_of([(p, ls) for p, q, ls in ctrain_voy])
        prod91 = S91.LP91(glob_voy, B_voy)
        prod91.set_params(voy_prm["s91"][T])
        spec_all = [(p, q, [len(l) for l in ls]) for p, q, ls in vp]
        c91 = S81.encipher(letters_lat, K_naibbe, skel_all, "line", S91.STICKY_P, seed=PLANT_SEED + 910 + ti)
        cp91, wp91 = prod91.text(spec_all, PLANT_SEED + 915 + ti, cipher=c91, seg=seg_voy)
        planted_s91_cores[T] = [(vp[i][0], vp[i][1], cp91[i][1]) for i in range(len(vp))]
        planted_s91_words[T] = [(vp[i][0], vp[i][1], wp91[i][1]) for i in range(len(vp))]

    emit(f"Planted manuscripts generated in {time.time() - T0:.1f}s ({clock()}).")
    emit("")
    flush_checkpoint("planted")

    ctx = mp.get_context("spawn")
    summary_rows: list[dict] = []

    # ==========================================================================
    # PART 1: F-30 (s71 WEAKENED TABLE-AND-GRILLE: WTG_global & WTG_scribe)
    # ==========================================================================
    emit("================================================================================")
    emit("AUDIT 1 — F-30 (s71 Weakened Table-and-Grille: WTG_global & WTG_scribe on 15-Quire LOQO)")
    emit("================================================================================")
    t_part = time.time()
    dummy_ca = dict(
        models=dict(
            CA=dict(
                n=0,
                holds={k: False for k in PREDS},
                text={k: "" for k in PREDS},
                gen_point={k: 0.0 for k in ("P1", "P2", "P3", "P4", "P5")},
                type_ratio=1.0,
                small=False,
            )
        )
    )
    wtg_jobs = []
    for m_tag, planted_dict in (("WTG_global", planted_wtg_global), ("WTG_scribe", planted_wtg_scribe)):
        for ti, T in enumerate(TRANSLITS):
            for fi, Q in enumerate(folds):
                wtg_jobs.append((
                    m_tag,
                    dict(T=T, Q=Q, pages_meta=planted_dict[T], s67_cell=dummy_ca, off=1000 * ti + 10 * fi),
                ))

    wtg_res = {}
    with ctx.Pool(N_WORKERS, initializer=worker_init) as pool:
        async_res = [(m_tag, pool.apply_async(run_s71_wtg_fold_worker, (job,))) for m_tag, job in wtg_jobs]
        for m_tag, ar in async_res:
            r = ar.get()
            wtg_res[(m_tag, r["T"], r["Q"])] = r

    for m_tag in ("WTG_global", "WTG_scribe"):
        rec_by_T = {}
        rec_recentred_by_T = {}
        pred_cnt_by_T = {}
        for T in TRANSLITS:
            rs = [wtg_res[(m_tag, T, Q)]["models"][m_tag] for Q in folds]
            rec_by_T[T] = sum(1 for x in rs if x["n"] >= 5)
            rec_recentred_by_T[T] = sum(1 for x in rs if x["n_rec"] >= 5)
            pred_cnt_by_T[T] = {k: sum(1 for x in rs if x["holds"][k]) for k in PREDS}
            call_T = power_call(rec_by_T[T])
            emit(
                f"  F-30 {m_tag:12s} | {T}: recovery {rec_by_T[T]:2d}/15 -> {call_T:13s} | "
                + ", ".join(f"{k} {pred_cnt_by_T[T][k]:2d}/15" for k in PREDS)
                + f" | [diagnostic recentred P4/P5: {rec_recentred_by_T[T]:2d}/15]"
            )
        fam_call = power_call(min(rec_by_T.values()))
        emit(
            f"  => F-30 {m_tag:12s} CALL: {fam_call} "
            f"(ZL3b {rec_by_T['ZL3b']}/15 [{power_call(rec_by_T['ZL3b'])}], "
            f"RF1b {rec_by_T['RF1b']}/15 [{power_call(rec_by_T['RF1b'])}], "
            f"IT2a {rec_by_T['IT2a']}/15 [{power_call(rec_by_T['IT2a'])}])"
        )
        summary_rows.append(
            dict(
                finding="F-30",
                family=f"s71_{m_tag}",
                rule=">=5/6 (P1..P5,P7)",
                recovery=rec_by_T,
                calls_by_T={T: power_call(rec_by_T[T]) for T in TRANSLITS},
                family_call=fam_call,
                recentred_recovery=rec_recentred_by_T,
                per_pred=pred_cnt_by_T,
            )
        )
    (RUN_DIR / "f30_s71_wtg.json").write_text(
        json.dumps({f"{m}|{T}|{Q}": v for (m, T, Q), v in wtg_res.items()}, indent=1, default=float),
        encoding="utf-8",
        newline="\n",
    )
    emit(f"Completed F-30 audit in {time.time() - t_part:.1f}s ({clock()}).\n")
    flush_checkpoint("f30")

    # ==========================================================================
    # PART 2: F-34 (s81 STICKY NAIBBE: line_sticky_fit & line_sticky75)
    # ==========================================================================
    emit("================================================================================")
    emit("AUDIT 2 — F-34 (s81 Per-Line Sticky Naibbe on 15-Quire LOQO: C1 >=5/6 Exclusion & C2 s69 Call Match)")
    emit("================================================================================")
    t_part = time.time()
    ref_calls_s81 = {}
    for T in TRANSLITS:
        p69 = planted_s81_p69[T]
        trs69 = S69.split_pages(S69.norm_pages(p69))
        r69_full = S81.s69_fold(f"Planted81_{T}_full", p69, trs69)
        ref_calls_s81[T] = r69_full["calls"]
        emit(
            f"  Planted s81 ({T}) full-text s69 reference calls: "
            + " ".join(f"{c}={'T' if r69_full['calls'][c] else 'F'}" for c in S81.CS)
            + f" (M1={r69_full['M1']:+.4f})"
        )

    s81_jobs = []
    for ti, T in enumerate(TRANSLITS):
        for fi, Q in enumerate(folds):
            s81_jobs.append(
                dict(
                    T=T,
                    Q=Q,
                    pages=planted_s81[T],
                    pages69=planted_s81_p69[T],
                    off=1000 * ti + 50 * fi,
                    ref_calls=ref_calls_s81[T],
                    fixture=False,
                )
            )

    s81_res = {}
    with ctx.Pool(N_WORKERS, initializer=worker_init) as pool:
        for r in pool.imap_unordered(run_s81_sticky_fold_worker, s81_jobs):
            s81_res[(r["T"], r["Q"])] = r

    for v_name in ("line_sticky_fit|latin_cremma", "line_sticky75|latin_cremma"):
        rec_c1, rec_c1_rec, rec_c2, pred_cnt = {}, {}, {}, {}
        for T in TRANSLITS:
            rs = [s81_res[(T, Q)]["models"][v_name] for Q in folds]
            rec_c1[T] = sum(1 for x in rs if x["n"] >= 5)
            rec_c1_rec[T] = sum(1 for x in rs if x["n_rec"] >= 5)
            rec_c2[T] = sum(1 for x in rs if x["match"])
            pred_cnt[T] = {k: sum(1 for x in rs if x["holds"][k]) for k in PREDS}
            emit(
                f"  F-34 {v_name:28s} | {T}: C1(>=5/6)={rec_c1[T]:2d}/15 [{power_call(rec_c1[T]):13s}] "
                f"(recentred P4/P5: {rec_c1_rec[T]:2d}/15 [{power_call(rec_c1_rec[T])}]) | "
                f"C2(s69 match)={rec_c2[T]:2d}/15 [{power_call(rec_c2[T]):13s}] | "
                + ", ".join(f"{k} {pred_cnt[T][k]:2d}/15" for k in PREDS)
            )
        call_c1 = power_call(min(rec_c1.values()))
        call_c2 = power_call(min(rec_c2.values()))
        emit(
            f"  => F-34 {v_name:28s} C1 (>=5/6 battery) CALL: {call_c1} "
            f"(ZL3b {rec_c1['ZL3b']}/15, RF1b {rec_c1['RF1b']}/15, IT2a {rec_c1['IT2a']}/15)"
        )
        emit(
            f"  => F-34 {v_name:28s} C2 (s69 call match) CALL: {call_c2} "
            f"(ZL3b {rec_c2['ZL3b']}/15, RF1b {rec_c2['RF1b']}/15, IT2a {rec_c2['IT2a']}/15)"
        )
        summary_rows.append(
            dict(
                finding="F-34",
                family=f"s81_{v_name}_C1",
                rule="C1 >=5/6 (P1..P5,P7)",
                recovery=rec_c1,
                calls_by_T={T: power_call(rec_c1[T]) for T in TRANSLITS},
                family_call=call_c1,
                recentred_recovery=rec_c1_rec,
                per_pred=pred_cnt,
            )
        )
        summary_rows.append(
            dict(
                finding="F-34",
                family=f"s81_{v_name}_C2_s69",
                rule="C2 s69 call-pattern match",
                recovery=rec_c2,
                calls_by_T={T: power_call(rec_c2[T]) for T in TRANSLITS},
                family_call=call_c2,
                recentred_recovery=rec_c2,
                per_pred={},
            )
        )
    (RUN_DIR / "f34_s81_sticky.json").write_text(
        json.dumps({f"{T}|{Q}": v for (T, Q), v in s81_res.items()}, indent=1, default=float),
        encoding="utf-8",
        newline="\n",
    )
    emit(f"Completed F-34 audit in {time.time() - t_part:.1f}s ({clock()}).\n")
    flush_checkpoint("f34")

    # ==========================================================================
    # PART 3: F-23 (LEXICAL PRODUCERS: s57, s58, s61, s67 CA)
    # ==========================================================================
    emit("================================================================================")
    emit("AUDIT 3 — F-23 (Lexical Producers s57, s58, s61, s67 CA on 15-Quire LOQO)")
    emit("================================================================================")
    t_part = time.time()

    # 3A. Fit s57, s58, s61 on their planted manuscripts' training splits (S57.fit, S58.fit, S61.fit)
    split_fit_jobs = []
    for fam, p_dict in (("s57", planted_s57), ("s58", planted_s58), ("s61", planted_s61)):
        for T in TRANSLITS:
            split_fit_jobs.append(dict(fam=fam, T=T, pages=p_dict[T]))

    fitted_lex_params = {}
    with ctx.Pool(N_WORKERS, initializer=worker_init) as pool:
        for r in pool.imap_unordered(fit_lexical_split_worker, split_fit_jobs):
            fitted_lex_params[(r["fam"], r["T"])] = r
            emit(
                f"  Fitted {r['fam']} on planted {r['T']} training split ({r['n_evals']} evals, {r['secs']:.1f}s): "
                f"params={r['params']}, loss={r['loss']:.2f}"
            )

    # 3B. Run 15-quire LOQO scoring for s57, s58, s61 on their planted manuscripts
    lex_fold_jobs = []
    for fi_fam, (fam, p_dict) in enumerate((("s57", planted_s57), ("s58", planted_s58), ("s61", planted_s61))):
        for ti, T in enumerate(TRANSLITS):
            prm = fitted_lex_params[(fam, T)]["params"]
            for fi, Q in enumerate(folds):
                lex_fold_jobs.append(
                    dict(
                        fam=fam,
                        T=T,
                        Q=Q,
                        pages=p_dict[T],
                        params=prm,
                        off=2000 * fi_fam + 500 * ti + 10 * fi,
                    )
                )

    lex_res = {}
    with ctx.Pool(N_WORKERS, initializer=worker_init) as pool:
        for r in pool.imap_unordered(run_lexical_loqo_fold_worker, lex_fold_jobs):
            lex_res[(r["fam"], r["T"], r["Q"])] = r

    for fam in ("s57", "s58", "s61"):
        rec_by_T, rec_rec_by_T, rec_all6_by_T, pred_cnt_by_T = {}, {}, {}, {}
        for T in TRANSLITS:
            rs = [lex_res[(fam, T, Q)] for Q in folds]
            rec_by_T[T] = sum(1 for x in rs if x["n"] >= 5)
            rec_rec_by_T[T] = sum(1 for x in rs if x["n_rec"] >= 5)
            rec_all6_by_T[T] = sum(1 for x in rs if x["n"] == 6)
            pred_cnt_by_T[T] = {k: sum(1 for x in rs if x["holds"][k]) for k in PREDS}
            emit(
                f"  F-23 {fam:6s}       | {T}: recovery(>=5/6)={rec_by_T[T]:2d}/15 [{power_call(rec_by_T[T]):13s}] "
                f"(all 6/6: {rec_all6_by_T[T]:2d}/15; recentred P4/P5 >=5/6: {rec_rec_by_T[T]:2d}/15) | "
                + ", ".join(f"{k} {pred_cnt_by_T[T][k]:2d}/15" for k in PREDS)
            )
        fam_call = power_call(min(rec_by_T.values()))
        emit(
            f"  => F-23 {fam:6s} CALL: {fam_call} "
            f"(ZL3b {rec_by_T['ZL3b']}/15 [{power_call(rec_by_T['ZL3b'])}], "
            f"RF1b {rec_by_T['RF1b']}/15 [{power_call(rec_by_T['RF1b'])}], "
            f"IT2a {rec_by_T['IT2a']}/15 [{power_call(rec_by_T['IT2a'])}])"
        )
        summary_rows.append(
            dict(
                finding="F-23",
                family=f"F23_{fam}",
                rule=">=5/6 (P1..P5,P7)",
                recovery=rec_by_T,
                calls_by_T={T: power_call(rec_by_T[T]) for T in TRANSLITS},
                family_call=fam_call,
                recentred_recovery=rec_rec_by_T,
                per_pred=pred_cnt_by_T,
            )
        )

    # 3C. Run s67 CA (and CA0) per-fold fit + LOQO scoring on its planted manuscript
    s67_jobs = []
    for ti, T in enumerate(TRANSLITS):
        for fi, Q in enumerate(folds):
            s67_jobs.append(dict(T=T, Q=Q, pages=planted_s67[T], off=1000 * ti + 10 * fi))

    s67_res = {}
    with ctx.Pool(N_WORKERS, initializer=worker_init) as pool:
        for r in pool.imap_unordered(run_s67_ca_fold_worker, s67_jobs):
            s67_res[(r["T"], r["Q"])] = r
            print(
                f"  [s67 {time.time() - t_part:.0f}s] {r['T']} {r['Q']} ({r['secs']:.0f}s): "
                f"CA {r['models']['CA']['n']}/6 (recentred {r['models']['CA']['n_rec']}/6)",
                flush=True,
            )

    for m_name in ("CA", "CA0"):
        rec_by_T, rec_rec_by_T, pred_cnt_by_T = {}, {}, {}
        for T in TRANSLITS:
            rs = [s67_res[(T, Q)]["models"][m_name] for Q in folds]
            rec_by_T[T] = sum(1 for x in rs if x["n"] >= 5)
            rec_rec_by_T[T] = sum(1 for x in rs if x["n_rec"] >= 5)
            pred_cnt_by_T[T] = {k: sum(1 for x in rs if x["holds"][k]) for k in PREDS}
            emit(
                f"  F-23 s67_{m_name:3s}     | {T}: recovery(>=5/6)={rec_by_T[T]:2d}/15 [{power_call(rec_by_T[T]):13s}] "
                f"(recentred P4/P5 >=5/6: {rec_rec_by_T[T]:2d}/15) | "
                + ", ".join(f"{k} {pred_cnt_by_T[T][k]:2d}/15" for k in PREDS)
            )
        fam_call = power_call(min(rec_by_T.values()))
        emit(
            f"  => F-23 s67_{m_name:3s} CALL: {fam_call} "
            f"(ZL3b {rec_by_T['ZL3b']}/15 [{power_call(rec_by_T['ZL3b'])}], "
            f"RF1b {rec_by_T['RF1b']}/15 [{power_call(rec_by_T['RF1b'])}], "
            f"IT2a {rec_by_T['IT2a']}/15 [{power_call(rec_by_T['IT2a'])}])"
        )
        summary_rows.append(
            dict(
                finding="F-23",
                family=f"F23_s67_{m_name}",
                rule=">=5/6 (P1..P5,P7)",
                recovery=rec_by_T,
                calls_by_T={T: power_call(rec_by_T[T]) for T in TRANSLITS},
                family_call=fam_call,
                recentred_recovery=rec_rec_by_T,
                per_pred=pred_cnt_by_T,
            )
        )

    (RUN_DIR / "f23_lexical_loqo.json").write_text(
        json.dumps(
            {
                "s57_s58_s61": {f"{fam}|{T}|{Q}": v for (fam, T, Q), v in lex_res.items()},
                "s67": {f"{T}|{Q}": v for (T, Q), v in s67_res.items()},
            },
            indent=1,
            default=float,
        ),
        encoding="utf-8",
        newline="\n",
    )
    emit(f"Completed F-23 audit in {time.time() - t_part:.1f}s ({clock()}).\n")
    flush_checkpoint("f23")

    # ==========================================================================
    # PART 4: F-41 (s91 LINE-POOL PRODUCER LP91: C1 Core Signature & C2 Word Battery)
    # ==========================================================================
    emit("================================================================================")
    emit("AUDIT 4 — F-41 (s91 Line-Pool Producer LP91 on 15-Quire LOQO: C1 Core Signature & C2 Word Battery)")
    emit("================================================================================")
    t_part = time.time()

    # Compute planted LP91 whole-text profiles to record planted locality band alongside frozen s87 band
    zl_ref = S91.S80.S55.voynich_pages("ZL3b")
    line_lens_zl = [len(ln) for p in zl_ref for ln in p["lines"] if ln]
    page_nl_zl = [len(p["lines"]) for p in zl_ref]
    planted_prof_91 = []
    for i, T in enumerate(TRANSLITS):
        P_pl = [(p, ls) for p, _, ls in planted_s91_words[T]]
        planted_prof_91.append(
            S87.profile(
                f"PLANTED_LP91_{T}",
                S87.layout(None, True, P_pl, line_lens_zl, page_nl_zl),
                "slot",
                S91.N_MATCH,
                S91.SEED87 + 100 * i,
                interval=True,
            )
        )
    lb_planted = S87.loc_band_from(planted_prof_91)
    ob_planted = S87.order_band_from(planted_prof_91)
    emit(
        f"  Planted LP91 profiles: recomputed loc_band=[{lb_planted[0]:.4f}, {lb_planted[1]:.4f}] "
        f"(frozen s87 loc_band=[{S91.LOC_BAND_S87[0]:.4f}, {S91.LOC_BAND_S87[1]:.4f}]); "
        f"recomputed order_band K100=[{ob_planted[100][0]:+.4f}, {ob_planted[100][1]:+.4f}]"
    )
    for p in planted_prof_91:
        ok_p, _, fl_p = S91.flags(p, S91.LOC_BAND_S87)
        emit(f"    {p['name']}: {S91.short(p)} flags(s87)={fl_p} ({'PASS' if ok_p else 'FAIL'})")

    s91_jobs = []
    for ti, T in enumerate(TRANSLITS):
        for fi, Q in enumerate(folds):
            s91_jobs.append(dict(T=T, Q=Q, ti=ti, fi=fi, pages=planted_s91_words[T], seg="slot", c2=True))

    s91_res = {}
    s91_fold_dir = RUN_DIR / "s91_folds"
    s91_fold_dir.mkdir(parents=True, exist_ok=True)
    with ctx.Pool(N_WORKERS, initializer=worker_init) as pool:
        for r in pool.imap_unordered(run_s91_lp91_fold_worker, s91_jobs):
            s91_res[(r["T"], r["Q"])] = r
            (s91_fold_dir / f"{r['T']}_{r['Q']}.json").write_text(
                json.dumps(r, default=float, indent=0), encoding="utf-8", newline="\n"
            )
            ok_f, _, fl_f = S91.flags(r["pH"], S91.LOC_BAND_S87)
            print(
                f"  [s91 {time.time() - t_part:.0f}s] {r['T']} {r['Q']} ({r['secs']:.0f}s): "
                f"C1={fl_f} ({'PASS' if ok_f else 'FAIL'}), C2={r['c2']['n']}/6, fit={r['fit']['params']}",
                flush=True,
            )

    rec_c1_s87, rec_c1_self, rec_c2_s91 = {}, {}, {}
    comp_cnt_by_T = {}
    c2_pred_by_T = {}
    for T in TRANSLITS:
        c1_ok_list = []
        c1_self_list = []
        c2_ok_list = []
        comp_cnt = Counter()
        for Q in folds:
            r = s91_res[(T, Q)]
            ok_87, comp_87, _ = S91.flags(r["pH"], S91.LOC_BAND_S87)
            c1_ok_list.append(bool(ok_87))
            for ck, cv in comp_87.items():
                if cv:
                    comp_cnt[ck] += 1
            # Self-band diagnostic (using ob_planted and lb_planted as in s91 fixture line 629)
            saved_ob = S87.ORDER_BAND
            try:
                S87.ORDER_BAND = ob_planted
                ok_sf, _, _ = S91.flags(r["pH"], lb_planted)
            finally:
                S87.ORDER_BAND = saved_ob
            c1_self_list.append(bool(ok_sf))
            c2_ok_list.append(r["c2"]["n"] >= 5)

        rec_c1_s87[T] = sum(c1_ok_list)
        rec_c1_self[T] = sum(c1_self_list)
        rec_c2_s91[T] = sum(c2_ok_list)
        comp_cnt_by_T[T] = dict(comp_cnt)
        c2_pred_by_T[T] = {k: sum(1 for Q in folds if s91_res[(T, Q)]["c2"]["holds"][k]) for k in PREDS}
        emit(
            f"  F-41 s91_LP91 C1   | {T}: recovery(s87 bands)={rec_c1_s87[T]:2d}/15 [{power_call(rec_c1_s87[T]):13s}] "
            f"(planted-self bands: {rec_c1_self[T]:2d}/15) | "
            f"a_order {comp_cnt['a_order']:2d}/15, b_Rw {comp_cnt['b_Rwithin']:2d}/15, "
            f"c_Rc<Rw {comp_cnt['c_Rcross<Rwithin']:2d}/15, d_loc {comp_cnt['d_locality']:2d}/15"
        )
        emit(
            f"  F-41 s91_LP91 C2   | {T}: recovery(>=5/6)={rec_c2_s91[T]:2d}/15 [{power_call(rec_c2_s91[T]):13s}] | "
            + ", ".join(f"{k} {c2_pred_by_T[T][k]:2d}/15" for k in PREDS)
        )

    call_s91_c1 = power_call(min(rec_c1_s87.values()))
    call_s91_c2 = power_call(min(rec_c2_s91.values()))
    emit(
        f"  => F-41 s91_LP91 C1 (core signature) CALL: {call_s91_c1} "
        f"(ZL3b {rec_c1_s87['ZL3b']}/15 [{power_call(rec_c1_s87['ZL3b'])}], "
        f"RF1b {rec_c1_s87['RF1b']}/15 [{power_call(rec_c1_s87['RF1b'])}], "
        f"IT2a {rec_c1_s87['IT2a']}/15 [{power_call(rec_c1_s87['IT2a'])}])"
    )
    emit(
        f"  => F-41 s91_LP91 C2 (LP91+s81 words) CALL: {call_s91_c2} "
        f"(ZL3b {rec_c2_s91['ZL3b']}/15 [{power_call(rec_c2_s91['ZL3b'])}], "
        f"RF1b {rec_c2_s91['RF1b']}/15 [{power_call(rec_c2_s91['RF1b'])}], "
        f"IT2a {rec_c2_s91['IT2a']}/15 [{power_call(rec_c2_s91['IT2a'])}])"
    )
    summary_rows.append(
        dict(
            finding="F-41",
            family="s91_LP91_C1_core",
            rule="C1 S87.c1 (a_order,b_Rw,c_Rc<Rw,d_loc)",
            recovery=rec_c1_s87,
            calls_by_T={T: power_call(rec_c1_s87[T]) for T in TRANSLITS},
            family_call=call_s91_c1,
            recentred_recovery=rec_c1_self,
            per_pred=comp_cnt_by_T,
        )
    )
    summary_rows.append(
        dict(
            finding="F-41",
            family="s91_LP91_C2_words",
            rule="C2 >=5/6 (P1..P5,P7)",
            recovery=rec_c2_s91,
            calls_by_T={T: power_call(rec_c2_s91[T]) for T in TRANSLITS},
            family_call=call_s91_c2,
            recentred_recovery=rec_c2_s91,
            per_pred=c2_pred_by_T,
        )
    )
    emit(f"Completed F-41 audit in {time.time() - t_part:.1f}s ({clock()}).\n")

    # ==========================================================================
    # FINAL SUMMARY TABLE OF ALL AUDITED PRODUCER FAMILIES (F-23, F-30, F-34, F-41)
    # ==========================================================================
    emit("================================================================================")
    emit("SUMMARY TABLE — s101 LOQO POWER AUDIT (PRE-REGISTERED RULE: >=10/15 POWERED, 5-9/15 WEAK, <=4/15 UNINFORMATIVE)")
    emit("================================================================================")
    emit(
        f"  {'Finding':<7s} {'Producer Family':<34s} {'ZL3b (Call)':<21s} {'RF1b (Call)':<21s} "
        f"{'IT2a (Call)':<21s} {'Family Call':<15s} {'Recentred(Z/R/I)'}"
    )
    for row in summary_rows:
        r = row["recovery"]
        c = row["calls_by_T"]
        rc = row["recentred_recovery"]
        z_str = f"{r['ZL3b']:2d}/15 ({c['ZL3b']})"
        r_str = f"{r['RF1b']:2d}/15 ({c['RF1b']})"
        i_str = f"{r['IT2a']:2d}/15 ({c['IT2a']})"
        rc_str = f"{rc['ZL3b']:2d}/{rc['RF1b']:2d}/{rc['IT2a']:2d} of 15"
        emit(
            f"  {row['finding']:<7s} {row['family']:<34s} {z_str:<21s} {r_str:<21s} "
            f"{i_str:<21s} {row['family_call']:<15s} {rc_str}"
        )

    (RUN_DIR / "summary_s101.json").write_text(
        json.dumps(
            dict(
                stub_match=sm,
                rule="POWERED if recovery >= 10/15; WEAK if 5..9/15; UNINFORMATIVE if <= 4/15",
                rows=summary_rows,
                elapsed_secs=time.time() - T0,
            ),
            indent=1,
            default=float,
        ),
        encoding="utf-8",
        newline="\n",
    )
    emit("")
    emit(f"elapsed: {time.time() - T0:.1f}s")
    emit(f"date end: {clock()}")
    emit(f"outputs: {OUT}, {RUN_DIR}")

    # Write final results_s101.txt once at completion (never overwriting)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
