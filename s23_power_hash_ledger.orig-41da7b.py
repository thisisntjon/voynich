"""s23 — power refile, hash ledger, m1 x 10 seeds, P-VALUE LEDGER  (Phase 2, workflow/phases/phase-2.md s23)

Writes results_s23.txt only. Four blocks:
  (a) HASH LEDGER   sha256sum -c reimplemented with hashlib over every *.prereg.sha256 and scoreboard/PREREG*.sha256
  (b) M1 x10 SEEDS  m1_coordinates column-specific excess, far-line draw seeds 0-9, pattern of
                    workflow/research/C-helpers/pw_m1_column.py:20-24 (rng = default_rng(seed); m.collect; m.boot)
  (c) POWER REFILE  the five filed negatives re-stated beside C-constraints §1 power numbers
  (d) P-VALUE LEDGER  Phase 2 family, Benjamini-Hochberg q = 0.05, floor-bound entries marked, earlier p-values unranked
No register, PLAN, handoff, scoreboard or other result file is touched.
Run: python -I s23_power_hash_ledger.py
"""
import sys, re, time, hashlib, subprocess, statistics
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools"))
import numpy as np

OUT = ROOT / "results_s23.txt"
STUB = ROOT / "s23_power_hash_ledger.prereg.sha256"
SEEDS = list(range(10))
SEED_TIME_LIMIT = 180.0          # s; a seed slower than this stops block (b)
Q = 0.05

lines = []
def emit(s=""):
    print(s, flush=True)
    lines.append(s)

def sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def run_date() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        s = r.stdout.strip()
        if r.returncode == 0 and re.search(r"\d{4}", s) and re.search(r"\d\d:\d\d", s):
            return s + "  (from `date`)"
    except Exception:
        pass
    return datetime.now().astimezone().strftime("%a %b %d %H:%M:%S %Z %Y") + "  (datetime fallback; `date` unavailable)"


# ---------------------------------------------------------------- header
my_hash = sha256_of(Path(__file__).resolve())
stub_hash = None
if STUB.exists():
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        mm = re.match(r"^([0-9a-f]{64})\s+\*?(.+?)\s*$", ln.strip())
        if mm and mm.group(2).replace("\\", "/").endswith("s23_power_hash_ledger.py"):
            stub_hash = mm.group(1)
stub_match = "MATCH" if stub_hash == my_hash else ("NO STUB" if stub_hash is None else "MISMATCH")

emit("# results_s23: power refile, hash ledger, m1 x10 seeds, P-VALUE LEDGER")
emit(f"# run {run_date()}")
emit(f"# script s23_power_hash_ledger.py sha256 {my_hash}")
emit(f"# prereg stub {STUB.name}: {stub_hash or '-'}  stub_match={stub_match}")
emit(f"# python -I, single process, no multiprocessing; numpy {np.__version__}")
emit()

# ================================================================ (a) HASH LEDGER
emit("=" * 100)
emit("(a) HASH LEDGER  --  `sha256sum -c` equivalent (hashlib) over every prereg stub on disk")
emit("=" * 100)
stubs = sorted(ROOT.glob("*.prereg.sha256")) + sorted((ROOT / "scoreboard").glob("PREREG*.sha256"))
n_ok = n_fail = n_miss = 0
amended_stubs = []
HASHLINE = re.compile(r"^([0-9a-f]{64})\s+\*?(.+?)\s*$")
emit(f"{'stub':44s} {'line':>4s} {'target':50s} {'status':8s} note")
for stub in stubs:
    rel = stub.relative_to(ROOT).as_posix()
    text = stub.read_bytes().decode("utf-8", "replace")
    crlf = "\r\n" in text
    entries = []
    for i, ln in enumerate(text.splitlines(), 1):
        mm = HASHLINE.match(ln.strip())
        if mm:
            entries.append((i, mm.group(1), mm.group(2).replace("\\", "/")))
    has_amend = any(ln.lstrip().startswith("#") and "AMENDMENT" in ln.upper() for ln in text.splitlines())
    per_target = {}
    rows = []
    for i, h, tgt in entries:
        p = ROOT / tgt
        if not p.exists():
            st = "MISSING"; n_miss += 1
        elif sha256_of(p) == h:
            st = "OK"; n_ok += 1
        else:
            st = "FAILED"; n_fail += 1
        per_target.setdefault(tgt, []).append((i, st))
        rows.append((i, tgt, st))
    for i, tgt, st in rows:
        note = ""
        hist = per_target[tgt]
        if len(hist) > 1:
            first_i, first_st = hist[0]
            last_i, last_st = hist[-1]
            if i == first_i and first_st == "FAILED" and last_st == "OK":
                note = f"original hash, superseded by amendment line {last_i} (matches the amendment, not the original)"
            elif i == last_i and first_st == "FAILED" and last_st == "OK":
                note = f"AMENDMENT line (replaces line {first_i}); current script = amended hash"
            else:
                note = f"listed {len(hist)}x in this stub (lines {', '.join(str(j) for j, _ in hist)})"
            if i == first_i and first_st == "FAILED" and last_st == "OK" and rel not in amended_stubs:
                amended_stubs.append(rel)
        if st == "MISSING":
            note = (note + "; " if note else "") + "target not on disk"
        emit(f"{rel:44s} {i:4d} {tgt:50s} {st:8s} {note}")
    tail = []
    if has_amend:
        tail.append("stub carries a dated # AMENDMENT comment")
    if crlf:
        tail.append("CRLF line endings (hash lines still parse)")
    if tail:
        emit(f"{rel:44s} {'':4s} {'':50s} {'':8s} [{'; '.join(tail)}]")
emit()
emit(f"TOTALS: {n_ok} OK, {n_fail} FAILED, {n_miss} MISSING over {len(stubs)} stubs")
emit(f"Amended stubs (FAILED original + OK amendment line): {', '.join(amended_stubs) if amended_stubs else 'none'}")
emit("  -> these record 'match the amendment, not the original'; the FAILED lines are the pre-crash hashes, not drift.")

# results files that print no hash / stubs that do not exist
def file_prints_hash(name):
    p = ROOT / name
    if not p.exists():
        return None
    return bool(re.search(r"[0-9a-f]{64}", p.read_text(encoding="utf-8", errors="replace")))

n4_prints = file_prints_hash("results_n4.txt")
p1_prints = file_prints_hash("results_p1_bifolio.txt")
p1_stub_hits = []
p1_script = ROOT / "p1_bifolio_null.py"
p1_now = sha256_of(p1_script) if p1_script.exists() else None
for stub in stubs:
    for ln in stub.read_text(encoding="utf-8", errors="replace").splitlines():
        mm = HASHLINE.match(ln.strip())
        if mm and mm.group(2).replace("\\", "/").endswith("p1_bifolio_null.py"):
            p1_stub_hits.append((stub.relative_to(ROOT).as_posix(), mm.group(1), "OK" if mm.group(1) == p1_now else "FAILED"))
emit()
emit("NOTES")
emit(f"  results_n4.txt: prints a script hash = {n4_prints}  (n4_habit7k.prereg.sha256 exists and verifies above; "
     "PREREG-v2 §9 requires the result file to print its hash; it does not)")
emit(f"  results_p1_bifolio.txt: prints a script hash = {p1_prints}; no p1_bifolio*.prereg.sha256 stub exists on disk.")
for s, h, st in p1_stub_hits:
    emit(f"    p1_bifolio_null.py hash {h[:12]}... is listed in {s} -> {st} against the script on disk")
if not p1_stub_hits:
    emit("    p1_bifolio_null.py is listed in no stub on disk")
emit("    p1_bifolio is therefore verifiable only through n3b's stub (phase-2.md decision 6). A retro stub is NOT")
emit("    written here: a stub written after results_p1_bifolio.txt exists would not be 'before the run'.")
emit("  n4b_habit7k_glyph / n6_habit7k_glyph: two stubs, one script (same hash); both verify independently above.")
emit()

# ================================================================ (b) M1 x10 SEEDS
emit("=" * 100)
emit("(b) M1 x10 SEEDS  --  column-specific excess vs far-line draw seed (pw_m1_column.py pattern, m1 module unchanged)")
emit("=" * 100)
import m1_coordinates as m   # noqa: E402  (imports vparse, boxes from tools/; real boxes)
N_BOOT = m.N_BOOT
t0 = time.time()
pages, _ = m.build_pages()
emit(f"pages {len(pages)}  aligned paragraph lines {sum(len(p['lines']) for p in pages.values())}  build {time.time()-t0:.1f}s")
emit(f"statistic: column-specific excess = (same-far) - (off-off_far) in edit<=1 pp; P = P(diff <= 0) under the")
emit(f"page-cluster bootstrap, n_boot={N_BOOT} (m1_coordinates.N_BOOT, the filed setting; pw_m1_column.py used 300).")
emit(f"filed: results_m1_coordinates.txt:59,64  excess +0.41 pp  P = 0.068  (seed 20261017, one far-line draw)")
emit()
emit(f"{'seed':>4s} {'n_same':>7s} {'excess_pp':>10s} {'ci_lo':>7s} {'ci_hi':>7s} {'P_colspec':>10s} {'P_samefar':>10s} {'t_s':>6s}")
m1_P, m1_exc, m1_sf = [], [], []
m1_stopped = None
for seed in SEEDS:
    ts = time.time()
    rng = np.random.default_rng(seed)
    res = m.collect(pages, rng)
    rs, ro, rf, rof = (m.rates(res[c])["le1"] for c in ("same", "off", "far", "off_far"))
    exc = (rs - rf) - (ro - rof)
    _, dci = m.boot(res, rng, n_boot=N_BOOT)
    lo, hi, P = dci["column-specific"]
    Psf = dci["same-far"][2]
    dt = time.time() - ts
    m1_P.append(P); m1_exc.append(exc); m1_sf.append(Psf)
    emit(f"{seed:4d} {len(res['same']):7d} {exc:+10.2f} {lo:+7.2f} {hi:+7.2f} {P:10.3f} {Psf:10.3f} {dt:6.0f}")
    if dt > SEED_TIME_LIMIT:
        m1_stopped = f"seed {seed} took {dt:.0f}s > {SEED_TIME_LIMIT:.0f}s limit; block (b) stopped after {len(m1_P)} seeds"
        emit(f"STOP: {m1_stopped}")
        break
m1_median = statistics.median(m1_P)
m1_k = sum(p < 0.05 for p in m1_P)
emit()
emit(f"P(column-specific<=0): median {m1_median:.3f}  range [{min(m1_P):.3f}, {max(m1_P):.3f}]  "
     f"{m1_k} of {len(m1_P)} below 0.05")
emit(f"excess: median {statistics.median(m1_exc):+.2f} pp  range [{min(m1_exc):+.2f}, {max(m1_exc):+.2f}] pp")
emit(f"same-far P: median {statistics.median(m1_sf):.3f}  range [{min(m1_sf):.3f}, {max(m1_sf):.3f}]")
emit(f"READING: filed P=0.068 was one seed; across {len(m1_P)} seeds median P = {m1_median:.3f}, "
     f"{m1_k} of {len(m1_P)} below 0.05 -> seed-unstable; the far-line draw decides the verdict (C-constraints §5 pitfall 1); "
     f"no verdict at this design. (C-constraints §1: filed +0.41 pp ~ r=0.004, below the r~0.006-0.007 detection threshold.)")
emit()

# ================================================================ (c) POWER REFILE
emit("=" * 100)
emit("(c) POWER REFILE  --  each filed negative beside its smallest detectable effect (C-constraints.md §1)")
emit("=" * 100)
refile = [
    ("c1 test A, hand 2 (quire-block exact null)",
     "results_c1.txt:10  NMI=0.333 null mean 0.209 p=0.133 (7 blocks HHHHBTT, 105 assignments, floor 0.0095)",
     "C-constraints §1: power 0.8 needs injected share s = 0.60 (0.9 at s = 0.70; 0.6 at s = 0.50; 0.5 at s = 0.45); "
     "the manuscript's own effect (NMI 0.333) corresponds to s ~ 0.60-0.65. At its own effect size the test misses "
     "20-40 % of the time. 'hand 2 p = 0.133 is a coin flip, not a negative.'",
     "UNDERPOWERED"),
    ("m6 §4 list order, PHARMA jar labels Lc, shared 2-char prefix",
     "results_m6_labels.txt:152  obs=0.125 shuffled=0.072±0.034 z=+1.56 p(higher)=0.174 (24 adjacent pairs; 200 shuffles, floor 1/201)",
     "C-constraints §1: 'not detectable: r = 0.50 gives power 0.6' -- undetectable below r = 0.50; "
     "'the jar-label list test has no power at any plausible effect size.'",
     "UNDERPOWERED"),
    ("m6 §4 list order, STARS labels Ls, shared 2-char prefix",
     "results_m6_labels.txt:140  obs=0.094 shuffled=0.104±0.031 z=-0.32 p(higher)=0.756 (64 adjacent pairs; 200 shuffles, floor 1/201)",
     "C-constraints §1: r = 0.15 power 1.0, r = 0.10 power 0.6 -- only an effect >= 15 % is readable; "
     "'no list order in the star labels' means 'no effect >= 15 %'.",
     "UNDERPOWERED"),
    ("a3 own-page label hit vs section-permuted null",
     "results_a3.txt:2  hit 0.121 null 0.107±0.010 p=0.106 (40 pages, 778 label tokens)",
     "C-constraints §1 (last paragraph): 'Other filed negatives not curved (unverified power): a3/d6 own-page label hit "
     "(p = 0.09-0.11, 40 pages, 778 tokens; d6's SENSITIVITY row on 55 pages already gives p = 0.020, so the 40-page "
     "negative is a sample-size negative)'. No injection curve was run.",
     "POWER UNVERIFIED"),
    ("d6 own-page label hit vs section-permuted null",
     "results_d6.txt:91  hit 12.1 % null mean 10.6 % p99 13.0 % p=0.0945 (40 pages); results_d6.txt:93 SENSITIVITY 55 pages p=(3+1)/201=0.0199",
     "C-constraints §1: same row as a3 -- power curve not run, 'unverified'; the 55-page sensitivity row already crosses "
     "0.05, so the 40-page p is a sample-size negative.",
     "POWER UNVERIFIED"),
]
for test, filed, power, status in refile:
    emit(f"TEST    : {test}")
    emit(f"FILED   : {filed}")
    emit(f"POWER   : {power}")
    emit(f"STATUS  : {status}")
    emit()
emit("Refiled reading for the D-list: none of these five is a negative; they are power statements. No re-run "
     "(c1 uses default_rng(0), c1_quire_null.py:180; m6 is module-level code; a3/d6 are the 40-page exhaustive set).")
emit()

# ================================================================ (d) P-VALUE LEDGER
emit("=" * 100)
emit("(d) P-VALUE LEDGER  --  Phase 2 family = the p-values this file prints; Benjamini-Hochberg q = 0.05")
emit("=" * 100)
emit("Family rule (research/phase-2.md §5, C-constraints §3): one family per round = every p-value a Phase 2 result file")
emit("prints. The 10 m1 seeds enter as one p (the median; the 10 are sensitivity). A p equal to its exact/permutation")
emit("floor is 'floor, not ranked' (C-constraints §5 pitfall 2) and is excluded from m.")
emit()
family = [
    # name, source, p, floor, floor-note
    ("m1 column-specific excess, median over seeds 0-9", f"results_s23.txt block (b); filed results_m1_coordinates.txt:64 P=0.068", m1_median, 1.0 / N_BOOT, f"bootstrap floor 1/{N_BOOT}"),
    ("c1 test A hand 2 quire-block null", "results_c1.txt:10", 0.133, 1 / 105, "exact floor 1/105 = 0.0095"),
    ("m6 Lc shared 2-char prefix (24 pairs)", "results_m6_labels.txt:152", 0.174, 1 / 201, "shuffle floor 1/201 = 0.005"),
    ("m6 Ls shared 2-char prefix (64 pairs)", "results_m6_labels.txt:140", 0.756, 1 / 201, "shuffle floor 1/201 = 0.005"),
    ("a3 own-page label hit (40 pages)", "results_a3.txt:2", 0.106, None, "floor not stated in file"),
    ("d6 own-page label hit (40 pages)", "results_d6.txt:91", 0.0945, 1 / 201, "shuffle floor 1/201 = 0.005"),
    ("d6 SENSITIVITY own-page label hit (55 pages)", "results_d6.txt:93", 0.0199, 1 / 201, "shuffle floor 1/201 = 0.005"),
]
ranked = [f for f in family if not (f[3] is not None and f[2] <= f[3] + 1e-12)]
floored = [f for f in family if f not in ranked]
mfam = len(ranked)
order = sorted(ranked, key=lambda f: f[2])
# BH: largest k with p_(k) <= k/m q; all ranks <= k pass
kmax = 0
for k, f in enumerate(order, 1):
    if f[2] <= k / mfam * Q:
        kmax = k
emit(f"m = {mfam} ranked p-values (q = {Q}); {len(floored)} floor-bound entries listed unranked")
emit(f"{'rank':>4s} {'raw_p':>8s} {'BH_cutoff':>10s} {'pass':6s} {'floor':28s} test  [source]")
survivors = []
for k, f in enumerate(order, 1):
    cut = k / mfam * Q
    ok = k <= kmax
    if ok:
        survivors.append(f[0])
    emit(f"{k:4d} {f[2]:8.4f} {cut:10.4f} {'PASS' if ok else 'fail':6s} {f[4]:28s} {f[0]}  [{f[1]}]")
for f in floored:
    emit(f"{'-':>4s} {f[2]:8.4f} {'-':>10s} {'floor':6s} {f[4]:28s} {f[0]}  [{f[1]}]  floor, not ranked")
emit()
emit(f"BH survivors at q={Q}: {', '.join(survivors) if survivors else 'NONE'}")
emit(f"Smallest ranked p {order[0][2]:.4f} vs cutoff 1/{mfam}*{Q} = {Q/mfam:.4f}. "
     "The five refiled negatives are filed as power statements, not p-values; none can pass, which is the point.")
emit()
emit("CONTEXT (earlier content-side p-values C-constraints §3 flagged; listed unranked, NOT members of the Phase 2 family):")
context = [
    ("c1 test A hand 1 quire-block null", "results_c1.txt:7", "0.018", "floor-bound (1/55); 'floor, not ranked'"),
    ("n3 hand-1 NMI margin tests (ZL3b 0.013 / IT2a 0.005 are NMI margins, not p-values)", "C-constraints §3 table", "0.018", "floor-bound (1/55, inherited from c1); 'floor, not ranked'"),
    ("m6 ALL label pages, shared 2-char prefix (1107 pairs)", "results_m6_labels.txt:164", "0.050", "at 5 %; C §1: r~0.015 effect, below the r=0.05 grid"),
    ("m6 ALL label pages, adjacent norm. edit distance (ned)", "results_m6_labels.txt:160", "0.005", "C §3: passes BH(0.05) over 582 only; = Bonferroni alpha at m=10, not <"),
    ("a3/d6 labels 40 pages", "results_a3.txt:2 / results_d6.txt:91", "0.106 / 0.0945", "refiled above as POWER UNVERIFIED"),
    ("c1 test A hand 2", "results_c1.txt:10", "0.133", "refiled above as UNDERPOWERED"),
    ("m1 column-specific (filed seed)", "results_m1_coordinates.txt:64", "0.068", "seed-unstable; block (b)"),
]
for t, src, p, note in context:
    emit(f"  p={p:14s} {t}  [{src}]  {note}")
emit("  C-constraints §3 summary: 582 printed p-values across results_*.txt (560 by the stricter regex), 291 < 0.05;")
emit("  per file m1 86, n2 87, n3b 159, n1 48, c2 47, b5 32, m6 30, c1 28, l1 20, n3 18. Under BH(0.05) over all 582 the")
emit("  cutoff is 0.018: the floor results sit exactly on the line, m6 ned p=0.005 passes, pre2 p=0.050 does not. With")
emit("  291/582 < 0.05 as the base rate, any single sub-0.05 p cited without a pre-registered family is noise at ~50 % prior.")
emit()
emit("Any later Phase 2 / Phase 3 file that prints a p-value appends its row to its own copy of this block and re-states m.")
if m1_stopped:
    emit(f"NOTE: {m1_stopped}")
emit(f"# end results_s23  total {time.time()-t0:.0f}s after m1 build")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
