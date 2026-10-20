"""S109: is Argon's cross-section label network structure beyond word frequency?  (D-066 (n), frozen design)

QUESTION (frozen, D-066 (n)): Argon (quarantined) reports that label types repeated across >= 2 manuscript sections
begin with ok-/ot- far more often than section-local labels (101 types, 56.4% vs 24.9%, chi2 43.1, p 5.2e-11), and that
adjacent label pairs recur across sections (e.g. f80r.4-5 okolo/okary vs f99r.11-12 okary/okolo).  Is either beyond
word frequency?

DATA (read-only): data/ZL3b-n.txt through vparse.load() (Zandbergen-Landini IVTFF, EVA; '[a:b]' -> first reading,
',' -> word break, '@nnn;' -> '?').

SECTION MAP (written here before scoring).  Source: R. Zandbergen, voynich.nu/illustr.html ("Illustrations"), the
page-level classification of illustration type, which is the $I page variable of ZL3b-n.txt.  Folio ranges in ZL file
order (inclusive; the script asserts at load time that every page agrees with ZL $I):
  H  herbal          f1v-f57r, f65r-f65v, f66v, f87r-f87v, f90r1-f96v
  A  astronomical    f67r1-f67r2, f67v1-f68r3, f68v2-f68v1
  C  cosmological    f57v, f67v2, f68v3, f69r-f70r2, f85r2-f86v4, f86v3   (incl. the rosettes foldout)
  Z  zodiac          f70v2-f73v
  B  biological      f75r-f75v, f76v-f84v                                (quire 13 less text-only f76r)
  P  pharmaceutical  f88r-f89v1, f99r-f102v1
  S  stars/recipes   f58r-f58v, f103r-f116r
  Text-only pages (ZL $I=T: f1r, f66r, f76r, f85r1, f86v6, f86v5, f116v) belong to no section in the source and are
  excluded from both tests and from the paragraph control.  (Argon's raw numbers are also recomputed descriptively with
  ZL $I taken as-is, T included as a class, to show whether the 101 is reproduced.)

LOCUS RULE (written here before scoring).  A label locus = one ZL line whose unit starts with 'L' (label) or 'R'
(radial line); circular text ('C' units) excluded as in Argon's count; paragraph text ('P') excluded.  Words containing
'?' are dropped; a locus with no remaining word is dropped.  Label type = the locus's remaining words joined by '.'.
ok/ot = the type's first word starts with 'ok' or 'ot'.  Length = number of EVA characters (dots excluded).
Paragraph control: word tokens of 'P' units ('?' words dropped); a type is a word string; frequency = token count.

TEST 1 (CMH).  Per type: n = number of loci (tokens), sections = distinct sections.  cross = >= 2 sections; local = 1.
2x2 per stratum (rows cross/local, cols ok-ot/other); strata = (frequency bin, length bin) with
  FREQ_BINS: 1,2,3,4,5,6-7,8-11,12-19,20-49,50-99,100+     LEN_BINS: <=3,4,5,6,7,8,9-10,11+
Strata with a zero row or column margin carry no information and are dropped.  Mantel-Haenszel pooled odds ratio,
Robins-Breslow-Greenland 95% CI, CMH test with continuity correction (statsmodels StratifiedTable).  Same statistic,
same bins, on paragraph word types = control.
  LABEL_ENRICH_REAL = CMH p < 0.01 AND label OR > paragraph control's 95% upper bound.

TEST 2 (pairs).  Per page, the page's label loci in ZL file order; adjacent = consecutive in that sequence.  An adjacent
pair is unordered (frozenset; reading-order agnostic); pairs of identical types are skipped.  Statistic X = number of
distinct unordered pairs that occur adjacent on pages of >= 2 different sections.  Null: N_SHUF = 10,000 shuffles of
label order within each page (every page keeps its label set); p = (1 + #{X* >= X}) / (N_SHUF + 1).
  PAIR_EXCESS = p < 0.01.

CONTROLS.  Synthetic fixture (--planted; reads no real data): (F1) ok/ot share driven by frequency only -> no
enrichment call; (F2) planted cross-section enrichment -> call; (F3) 10 planted recurring pairs -> PAIR_EXCESS;
(F4) shuffled labels -> no call on either test.  Real-data positive control: 10 pairs of real hapax label types planted
adjacent on two pages of different sections (overwriting existing loci) -> PAIR_EXCESS at p < 0.01.  Real-data
negative control: label strings shuffled once across all label loci -> neither call.
CONTROLS_OK = fixture passes AND positive control detected AND negative control gives no call.

STOPPING RULE (D-066 (n)).  Controls fail -> INCONCLUSIVE.  Neither call -> the network is word frequency and position;
record and stop.  PAIR_EXCESS -> adjacent labels form recurring units across sections; propose a held-out prediction
(pairs on pages not used) before any semantic reading.  LABEL_ENRICH_REAL alone is not named by the rule: reported,
lead decides.

PROCESS: 1 worker, BelowNormal, waits while free RAM < 4 GB.  --planted runs only the fixture (runs/s109/fixture_N.txt,
never overwriting).  A real run refuses unless s109_label_network.prereg.sha256 verifies and covers every loaded local
module and data file.  Never overwrites: if results_s109.txt exists the run refuses.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT)]

PLANTED = "--planted" in sys.argv
LIST_INPUTS = "--list-inputs" in sys.argv
SELF = ROOT / "s109_label_network.py"
STUB = ROOT / "s109_label_network.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s109"
RESULT = ROOT / "results_s109.txt"

SEED = 109018
N_SHUF = 10000
ALPHA = 0.01
N_PLANT = 10
MIN_FREE_GB = 4.0
DATE_EXE = Path(r"C:\Program Files\Git\usr\bin\date.exe")
FREQ_EDGES = [1, 2, 3, 4, 5, 6, 8, 12, 20, 50, 100]   # bin i = [edge_i, edge_{i+1})
LEN_EDGES = [0, 4, 5, 6, 7, 8, 9, 11]                 # <=3 is [0,4)

SECTION_RANGES = [  # (section, first page, last page) in ZL file order; see header
    ("T", "f1r", "f1r"), ("H", "f1v", "f57r"), ("C", "f57v", "f57v"), ("S", "f58r", "f58v"),
    ("H", "f65r", "f65v"), ("T", "f66r", "f66r"), ("H", "f66v", "f66v"), ("A", "f67r1", "f67r2"),
    ("C", "f67v2", "f67v2"), ("A", "f67v1", "f68r3"), ("C", "f68v3", "f68v3"), ("A", "f68v2", "f68v1"),
    ("C", "f69r", "f70r2"), ("Z", "f70v2", "f73v"), ("B", "f75r", "f75v"), ("T", "f76r", "f76r"),
    ("B", "f76v", "f84v"), ("T", "f85r1", "f85r1"), ("C", "f85r2", "f86v4"), ("T", "f86v6", "f86v5"),
    ("C", "f86v3", "f86v3"), ("H", "f87r", "f87v"), ("P", "f88r", "f89v1"), ("H", "f90r1", "f96v"),
    ("P", "f99r", "f102v1"), ("S", "f103r", "f116r"), ("T", "f116v", "f116v"),
]

log: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def clock():
    try:
        r = subprocess.run([str(DATE_EXE)], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now; `date` unavailable)"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def below_normal_wait_ram():
    import psutil
    try:
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:  # noqa: BLE001
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    waited = 0
    while True:
        free = psutil.virtual_memory().available / 2 ** 30
        if free >= MIN_FREE_GB:
            return free, waited
        if waited >= 7200:
            print(f"ABORT: free RAM stayed below {MIN_FREE_GB} GB for {waited}s; nothing scored.", flush=True)
            sys.exit(2)
        print(f"free RAM {free:.2f} GB < {MIN_FREE_GB}; waiting", flush=True)
        time.sleep(30)
        waited += 30


def binidx(x, edges):
    i = 0
    for k, e in enumerate(edges):
        if x >= e:
            i = k
    return i


def okot(s):
    return s.split(".")[0].startswith(("ok", "ot"))


# ============================================================ test 1
def cmh(types):
    """types: list of (string, n, n_sections). Returns dict with OR, CI, p, strata used, raw table."""
    from statsmodels.stats.contingency_tables import StratifiedTable
    strata = defaultdict(lambda: np.zeros((2, 2)))
    for s, n, nsec in types:
        L = len(s.replace(".", ""))
        k = (binidx(n, FREQ_EDGES), binidx(L, LEN_EDGES))
        strata[k][0 if nsec >= 2 else 1, 0 if okot(s) else 1] += 1
    tabs = [t for t in strata.values() if t.sum(0).min() > 0 and t.sum(1).min() > 0]
    out = {"strata_used": len(tabs), "strata_all": len(strata), "types_used": int(sum(t.sum() for t in tabs))}
    if not tabs:
        out.update(OR=float("nan"), lo=float("nan"), hi=float("nan"), p=1.0)
        return out
    st = StratifiedTable(tabs)
    lo, hi = st.oddsratio_pooled_confint(0.05)
    out.update(OR=float(st.oddsratio_pooled), lo=float(lo), hi=float(hi),
               p=float(st.test_null_odds(correction=True).pvalue))
    return out


def label_types(loci):
    by = defaultdict(list)
    for x in loci:
        by[x["s"]].append(x["sec"])
    return [(s, len(v), len(set(v))) for s, v in by.items()]


def para_types(tokens):
    by = defaultdict(list)
    for w, sec in tokens:
        by[w].append(sec)
    return [(w, len(v), len(set(v))) for w, v in by.items()]


def enrich_call(lab, par):
    return bool(lab["p"] < ALPHA and lab["OR"] > par["hi"])


# ============================================================ test 2
def pair_stat(pages):
    """pages: list of (section, [strings]). Returns number of distinct unordered pairs adjacent in >= 2 sections."""
    secs = defaultdict(set)
    for sec, seq in pages:
        for a, b in zip(seq, seq[1:]):
            if a != b:
                secs[frozenset((a, b))].add(sec)
    return sum(1 for v in secs.values() if len(v) >= 2), secs


def pair_test(pages, n_shuf, seed):
    obs, secs = pair_stat(pages)
    rng = random.Random(seed)
    work = [(sec, list(seq)) for sec, seq in pages if len(seq) >= 2]
    null = np.empty(n_shuf)
    for i in range(n_shuf):
        for _sec, seq in work:
            rng.shuffle(seq)
        null[i] = pair_stat(work)[0]
    p = (1 + int((null >= obs).sum())) / (n_shuf + 1)
    return dict(X=obs, null_mean=float(null.mean()), null_sd=float(null.std()), p=p,
                pairs=sorted([(tuple(sorted(k)), sorted(v)) for k, v in secs.items() if len(v) >= 2]))


def plant_pairs(pages, n_pairs, rng, pool):
    """Overwrite two adjacent loci on two pages of different sections with planted pair (a,b) / (b,a)."""
    pages = [(sec, list(seq)) for sec, seq in pages]
    elig = [i for i, (_s, seq) in enumerate(pages) if len(seq) >= 2]
    names = rng.sample(pool, 2 * n_pairs)
    used = set()
    for k in range(n_pairs):
        a, b = names[2 * k], names[2 * k + 1]
        while True:
            i, j = rng.sample(elig, 2)
            if pages[i][0] != pages[j][0] and i not in used and j not in used:
                break
        used |= {i, j}
        for idx, (x, y) in ((i, (a, b)), (j, (b, a))):
            seq = pages[idx][1]
            q = rng.randrange(len(seq) - 1)
            seq[q], seq[q + 1] = x, y
    return pages


# ============================================================ fixture
def synth(mode, rng):
    """Synthetic labels: 7 sections x 22 pages x 7 labels (about the real label count); Zipf(1.0) vocabulary of 3000
    types, so most labels are hapax as in the manuscript; returns (loci, pages, para_tokens)."""
    secs = list("HACZBPS")
    V = 3000
    zipf = np.array([1.0 / (r + 1) ** 1.0 for r in range(V)])
    names = []
    for r in range(V):
        stem = "".join(rng.choice("aeoydlrkchs") for _ in range(rng.randint(2, 5)))
        if mode == "enrich":
            pfx = None
        else:
            p_ok = 0.15 + 0.5 * (1 - r / V) ** 4          # frequent types are more often ok/ot (frequency only)
            pfx = rng.choice(("ok", "ot")) if rng.random() < p_ok else rng.choice(("ch", "sh", "da", "qo", "y"))
        names.append((pfx, stem + f"{r}"))
    home = {r: rng.choice(secs) for r in range(V)}
    shared = {r for r in range(V) if r % 2 == 0}
    if mode == "enrich":   # strong plant (code check): shared (multi-section) types ok/ot 90%, section-local 5%
        names = [((rng.choice(("ok", "ot")) if rng.random() < (0.9 if r in shared else 0.05)
                   else rng.choice(("ch", "sh", "da", "qo", "y"))), st) for r, (_p, st) in enumerate(names)]
    word = [p + s for p, s in names]
    loci, pages = [], []
    nrng = np.random.default_rng(rng.randint(0, 2 ** 31))
    for sec in secs:
        if mode == "enrich":
            allowed = np.array([1.0 if (r in shared or home[r] == sec) else 0.0 for r in range(V)])
        else:
            allowed = np.ones(V)
        pr = zipf * allowed
        pr /= pr.sum()
        for pg in range(22):
            seq = [word[r] for r in nrng.choice(V, size=7, p=pr)]
            pages.append((sec, seq))
    if mode == "pairs":
        pages = plant_pairs(pages, N_PLANT, rng, sorted(set(word) - {s for _x, q in pages for s in q}))
    if mode == "shuffled":
        allw = [s for _x, q in pages for s in q]
        rng.shuffle(allw)
        it = iter(allw)
        pages = [(sec, [next(it) for _ in q]) for sec, q in pages]
    for sec, seq in pages:
        for s in seq:
            loci.append(dict(s=s, sec=sec))
    # paragraph control: frequency-only ok/ot, no section structure
    para = []
    pr = zipf / zipf.sum()
    base = [p + s for p, s in names] if mode != "enrich" else \
        [(rng.choice(("ok", "ot")) if rng.random() < 0.3 else "ch") + s for _p, s in names]
    for sec in secs:
        for r in nrng.choice(V, size=3000, p=pr):
            para.append((base[r], sec))
    return loci, pages, para


def run_fixture(n_shuf, rng_seed):
    rng = random.Random(rng_seed)
    res = {}
    for mode in ("freqonly", "enrich", "pairs", "shuffled"):
        loci, pages, para = synth(mode, rng)
        lab, par = cmh(label_types(loci)), cmh(para_types(para))
        pt = pair_test(pages, n_shuf, rng_seed + 7)
        res[mode] = dict(lab=lab, par=par, enrich=enrich_call(lab, par), pair=pt, pair_call=pt["p"] < ALPHA)
    ok = (not res["freqonly"]["enrich"] and res["enrich"]["enrich"] and res["pairs"]["pair_call"]
          and not res["shuffled"]["enrich"] and not res["shuffled"]["pair_call"])
    return res, ok


def fmt_c(name, c):
    return (f"[{name}] OR={c['OR']:.3f} 95%CI=({c['lo']:.3f},{c['hi']:.3f}) CMH_p={c['p']:.4g} "
            f"strata={c['strata_used']}/{c['strata_all']} types_used={c['types_used']}")


def fmt_p(name, p):
    return f"[{name}] X={p['X']} null_mean={p['null_mean']:.3f} null_sd={p['null_sd']:.3f} p={p['p']:.5f}"


def print_fixture(res, ok):
    for m, r in res.items():
        emit(fmt_c(f"fix_{m}_label", r["lab"]) + f"  para_hi={r['par']['hi']:.3f} enrich_call={r['enrich']}")
        emit(fmt_p(f"fix_{m}_pairs", r["pair"]) + f" pair_call={r['pair_call']}")
    emit(f"FIXTURE_PASS={ok}")


# ============================================================ real data
def section_map(recs):
    order = []
    for r in recs:
        if not order or order[-1] != r["page"]:
            if r["page"] not in order:
                order.append(r["page"])
    ill = {r["page"]: r["illus"] for r in recs}
    pos = {p: i for i, p in enumerate(order)}
    sec = {}
    for s, a, b in SECTION_RANGES:
        for p in order[pos[a]:pos[b] + 1]:
            sec[p] = s
    bad = [p for p in order if sec.get(p) != ill[p]]
    return {p: (None if s == "T" else s) for p, s in sec.items()}, bad, order


def load_real():
    import vparse
    recs = vparse.load()
    sec, bad, order = section_map(recs)
    loci = []
    for r in recs:
        if r["unit"][0] in "LR":
            ws = [w for w in r["words"] if "?" not in w]
            if ws:
                loci.append(dict(page=r["page"], line=r["line"], unit=r["unit"], illus=r["illus"],
                                 sec=sec.get(r["page"]), words=ws, s=".".join(ws)))
    para = [(w, sec.get(r["page"])) for r in recs if r["unit"].startswith("P")
            for w in r["words"] if "?" not in w]
    return recs, sec, bad, loci, para


def pages_of(loci):
    by = defaultdict(list)
    for x in loci:
        by[x["page"]].append(x)
    out = []
    for p, xs in by.items():           # loci already in ZL file order
        out.append((xs[0]["sec"], [x["s"] for x in xs]))
    return out


def chi2_2x2(a, b, c, d):
    from scipy.stats import chi2_contingency
    t = [[a, b], [c, d]]
    if min(a + b, c + d, a + c, b + d) == 0:
        return float("nan"), float("nan")
    chi2, p, _dof, _e = chi2_contingency(t, correction=False)
    return float(chi2), float(p)


def argon_raw(loci, key, label):
    by = defaultdict(list)
    for x in loci:
        by[x["s"]].append(x[key])
    cross = [s for s, v in by.items() if len(set(v)) >= 2]
    local_rep = [s for s, v in by.items() if len(set(v)) == 1 and len(v) >= 2]
    local_all = [s for s, v in by.items() if len(set(v)) == 1]
    a = sum(map(okot, cross))
    for nm, loc in (("local_repeated", local_rep), ("local_all", local_all)):
        c = sum(map(okot, loc))
        chi2, p = chi2_2x2(a, len(cross) - a, c, len(loc) - c)
        emit(f"  ARGON_RAW[{label}; vs {nm}] cross {a}/{len(cross)}={a / max(1, len(cross)):.3f}  "
             f"local {c}/{len(loc)}={c / max(1, len(loc)):.3f}  chi2(1df, uncorrected)={chi2:.2f} p={p:.3g}")


def local_inputs():
    mods = set()
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f:
            continue
        p = Path(f).resolve()
        try:
            rel = p.relative_to(ROOT)
        except ValueError:
            continue
        if p.suffix == ".py":
            mods.add(rel.as_posix())
    mods.add(SELF.name)
    return sorted(mods), ["data/ZL3b-n.txt"]


def stub_match(required):
    if not STUB.exists():
        return False, "NO STUB"
    raw = STUB.read_bytes()
    if b"\r" in raw or raw.startswith(b"\xef\xbb\xbf"):
        return False, "stub has CR or BOM"
    want = {}
    for ln in raw.decode("utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    missing = [f for f in required if f not in want]
    return bool(want) and not bad and not missing, f"bad={bad} missing={missing}"


def write_out(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as fh:   # 'x': never overwrite
        fh.write("\n".join(log) + "\n")


def main():
    t0 = time.time()
    if LIST_INPUTS:
        load_real()
        import scipy.stats  # noqa: F401
        from statsmodels.stats.contingency_tables import StratifiedTable  # noqa: F401
        mods, data = local_inputs()
        print("\n".join(mods + data))
        return
    if not PLANTED and RESULT.exists():
        print("REFUSED: results_s109.txt exists; a change is a new run id.")
        sys.exit(4)
    free, waited = below_normal_wait_ram()
    emit("S109 - cross-section label network: ok-/ot- enrichment (CMH) and recurring adjacent pairs (D-066 (n))")
    emit(f"started {clock()}  priority=BelowNormal workers=1  free_RAM_GB={free:.2f} waited_s={waited}")
    emit(f"thresholds: ALPHA={ALPHA} N_SHUF={N_SHUF} N_PLANT={N_PLANT} SEED={SEED} FREQ_EDGES={FREQ_EDGES} "
         f"LEN_EDGES={LEN_EDGES}")
    if PLANTED:
        res, ok = run_fixture(2000, SEED)
        print_fixture(res, ok)
        emit(f"finished {clock()} runtime_s={time.time() - t0:.1f}")
        k = 0
        while (RUN_DIR / f"fixture_{k}.txt").exists():
            k += 1
        write_out(RUN_DIR / f"fixture_{k}.txt")
        return
    recs, sec, bad, loci_all, para_all = load_real()
    import scipy.stats  # noqa: F401
    from statsmodels.stats.contingency_tables import StratifiedTable  # noqa: F401
    mods, data = local_inputs()
    ok, why = stub_match(mods + data)
    emit(f"stub_match={ok} ({len(mods)} modules, {len(data)} data files) {'' if ok else why}")
    emit(f"section_map_vs_ZL_$I mismatches={len(bad)} {bad[:5]}")
    if not ok or bad:
        emit("REFUSED: stub does not verify or section map disagrees with ZL $I; no real scoring.")
        write_out(RUN_DIR / "refused.txt")
        sys.exit(3)
    fx, fx_ok = run_fixture(2000, SEED)
    print_fixture(fx, fx_ok)
    emit(f"CALL_FIXTURE={fx_ok}")

    loci = [x for x in loci_all if x["sec"] is not None]
    para = [(w, s) for w, s in para_all if s is not None]
    lt = label_types(loci)
    emit(f"data: label_loci={len(loci)} (dropped on text-only pages: {len(loci_all) - len(loci)}) "
         f"label_types={len(lt)} pages_with_labels={len({x['page'] for x in loci})} "
         f"sections={len({x['sec'] for x in loci})} per_section={dict(sorted(Counter(x['sec'] for x in loci).items()))}")
    emit(f"      cross-section label types={sum(1 for t in lt if t[2] >= 2)}  section-local={sum(1 for t in lt if t[2] == 1)}"
         f"  (of which repeated={sum(1 for t in lt if t[2] == 1 and t[1] >= 2)})  paragraph tokens={len(para)} "
         f"types={len(set(w for w, _ in para))}")

    emit("ARGON RAW NUMBERS, recomputed descriptively (unstratified; not part of any call):")
    argon_raw(loci, "sec", "frozen map, L+R, T pages dropped")
    argon_raw(loci_all, "illus", "ZL $I as-is incl T, L+R")
    l12 = [x for x in loci_all if len(x["words"]) <= 2]
    argon_raw(l12, "illus", "ZL $I as-is, L+R, 1-2 word loci")

    emit("TEST 1 (CMH, stratified by frequency x length):")
    lab = cmh(lt)
    par = cmh(para_types(para))
    emit(fmt_c("labels", lab))
    emit(fmt_c("paragraph_control", par))
    enrich = enrich_call(lab, par)
    emit(f"LABEL_ENRICH_REAL={enrich}  (CMH p={lab['p']:.4g} < {ALPHA} and OR {lab['OR']:.3f} > paragraph 95% upper "
         f"{par['hi']:.3f})")

    emit("TEST 2 (unordered adjacent label pairs recurring across sections; within-page shuffles):")
    pages = pages_of(loci)
    pt = pair_test(pages, N_SHUF, SEED + 2)
    emit(fmt_p("pairs", pt))
    pair_excess = pt["p"] < ALPHA
    emit(f"PAIR_EXCESS={pair_excess}  (p={pt['p']:.5f} < {ALPHA})")
    emit("  recurring pairs (pair : sections): " + "; ".join(f"{'/'.join(k)}:{''.join(v)}" for k, v in pt["pairs"][:40])
         + (" ..." if len(pt["pairs"]) > 40 else ""))
    emit(f"  okolo/okary recurs: {any(set(k) == {'okolo', 'okary'} for k, _v in pt['pairs'])}")

    emit("CONTROLS on real data:")
    rng = random.Random(SEED + 3)
    lab_counts = Counter(x["s"] for x in loci)
    hapax = sorted(s for s, n in lab_counts.items() if n == 1)
    planted = plant_pairs(pages, N_PLANT, rng, hapax)
    pos = pair_test(planted, N_SHUF, SEED + 4)
    emit(fmt_p("positive_control_10_planted_pairs", pos))
    pos_ok = pos["p"] < ALPHA
    emit(f"  POSITIVE_CONTROL_DETECTED={pos_ok}")
    strings = [x["s"] for x in loci]
    rng.shuffle(strings)
    shl = [dict(x, s=s) for x, s in zip(loci, strings)]
    nl = cmh(label_types(shl))
    npair = pair_test(pages_of(shl), N_SHUF, SEED + 5)
    n_enrich, n_pair = enrich_call(nl, par), npair["p"] < ALPHA
    emit(fmt_c("negative_control_shuffled_labels", nl) + f" enrich_call={n_enrich}")
    emit(fmt_p("negative_control_shuffled_labels", npair) + f" pair_call={n_pair}")
    neg_ok = not n_enrich and not n_pair
    emit(f"  NEGATIVE_CONTROL_NO_CALL={neg_ok}")
    controls = fx_ok and pos_ok and neg_ok
    emit(f"CONTROLS_OK={controls}")

    if not controls:
        verdict = "INCONCLUSIVE (a control failed; no call is filed)"
    elif pair_excess:
        verdict = ("PAIR_EXCESS: adjacent labels form recurring units across sections; propose a held-out prediction "
                   "(pairs on pages not used) before any semantic reading" + ("; LABEL_ENRICH_REAL also True" if enrich else ""))
    elif enrich:
        verdict = "LABEL_ENRICH_ONLY: enrichment beyond frequency and paragraph morphology; stopping rule names no step, lead decides"
    else:
        verdict = "NEITHER: the network is word frequency and position; record and stop"
    emit(f"CALL: LABEL_ENRICH_REAL={enrich} PAIR_EXCESS={pair_excess} CONTROLS_OK={controls}")
    emit(f"VERDICT={verdict}")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    summ = RUN_DIR / "summary.json"
    if not summ.exists():
        with open(summ, "x", encoding="utf-8", newline="\n") as fh:
            json.dump(dict(label=lab, paragraph=par, pairs={k: v for k, v in pt.items() if k != "pairs"},
                           recurring_pairs=pt["pairs"], positive={k: v for k, v in pos.items() if k != "pairs"},
                           negative_cmh=nl, negative_pairs={k: v for k, v in npair.items() if k != "pairs"},
                           calls=dict(LABEL_ENRICH_REAL=enrich, PAIR_EXCESS=pair_excess, CONTROLS_OK=controls)),
                      fh, indent=1)
    emit(f"sidecar: runs/s109/summary.json")
    emit(f"finished {clock()} runtime_s={time.time() - t0:.1f}")
    write_out(RESULT)


if __name__ == "__main__":
    main()
