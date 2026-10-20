"""N6: Currier A vs B on the frozen PREREG-v2 board (OPEN O-010).

PRE-REGISTRATION (written and hashed before any n6 run; stamp 2026-10-17 19:37 PDT from `date`;
hash of this file and its inputs in n6_ab_split.prereg.sha256).  Run once, no tuning.

Question.  Do Currier A and B behave like the same system on the frozen v2 board, and does
either half fall inside a natural-language (L) family range that the whole text misses?
(O-010: the audit noticed only B shows anomalous cross-space coupling; A sits in Dante's range.)

Not blind.  results_m4_phase1_board already printed voynich_A / voynich_B values and their
full-size in/out (A: x_edge_mi_word 0.1265 IN L; jsd_first_fg 0.1392 OUT L).  What is new
here and was not seen before the freeze of this docstring: the run_v2 (PREREG-v2 scorer) rows,
the A/B rule applied as written, the §2 RF1b/IT2a rows for each half, and the matched-size
control ranges.

Instrument (nothing tuned; all from PREREG-v2.md, frozen 19:27, sha256 f8c42d76...):
  * scorer = scoreboard/run_v2.py, called as a subprocess with the §9 commands, project root,
    system Python 3.11.  Voynich halves: `--voynich --lang A|B`, whole text: `--voynich`.
  * ranges = results_m4_phase1_board.json (full-size controls, 25k-token cut, m4 members,
    m4 tight flags, m4 no-weight list).  X (gibberish) is NA: that file has no
    "x_family": "gibberish" flag and no gibberish ranges file exists in n6's inputs.
  * §2 robustness: each half is also scored on RF1b and IT2a
    (`--meta data/translit/<F>.meta.json --lang A|B`; the sidecars carry per-page lang).
    The whole text on RF1b/IT2a is scored with --n-sample 40000 (whole, like --voynich).
  * Controls at full size: C and G sidecars re-scored with `run_v2 --meta <sidecar>` (25k
    cut) and L controls in-process with run_v2.score_one on m4's own loaders
    (m4_phase1_board.natural_from_control / natural_from_ext, 8 x 20 wrap).  These rows are a
    code check against m4's rows; the full-size verdict uses the m4 ranges file as filed.
  * Matched size (decided here, unconditionally, not "if size-sensitive"): every L/C/G
    control used in the m4 ranges is ALSO scored at its first 11,231 tokens (A size) and its
    first 23,078 tokens (B size), whole lines, run_v2.subsample on the 25k-cut pages.  From
    those rows two ranges files are written, results_n6_ranges_A11k.json and
    results_n6_ranges_B23k.json: min/max per family over the same member corpora as m4
    (timm_schinner excluded from G on m4's line-edge keys), types_25k from the matched rows,
    tight flags and no-weight list copied unchanged from the m4 file.  A is then scored
    against the 11k file and B against the 23k file (ZL3b, RF1b, IT2a).  Controls shorter
    than the target are used at their full length and listed.

Per-half family verdict (PREREG-v2 §7, computed from per-metric in/out, which is checked
against run_v2's own printed counts):
  * weighted metrics = v1 bands + WEIGHTED extras (run_v2 NEW_KEYS classes) minus the ranges
    file's no-weight list;
  * §2: a weighted metric whose in/out (any of L, C, G) differs between ZL3b, RF1b and IT2a is
    dropped (weight 0) for that half's verdict;
  * outs[F] = surviving weighted metrics OUT for family F on ZL3b; tight-outs as run_v2;
  * kill-candidate F: >= 3 tight weighted outs (the "no single parameter change" clause of
    §7 is not tested here, so this is "kill-candidate", not "killed");
  * favoured F: outs[F] + 2 <= outs[G] for every rival G; else "undecided";
  * family verdict = (favoured-or-undecided, set of kill-candidates).

Decision rule (fixed in advance, PREREG-v2 §6 applied to the halves):
  SPLIT if  (1) family verdict(A) != family verdict(B),
        or  (2) A is IN the L range on BOTH edge coupling (x_edge_mi_word) AND line-edge JSD
            (jsd_first_fg) on all three transliterations, while B is not IN on both.
  Otherwise SAME.
  The headline is the FULL-SIZE verdict (the frozen board).  The matched-size verdict is
  reported next to it; if they differ the headline carries "(size-fragile)".  cross_excess_eva
  (the other cross-space coupling measure) is reported, not part of clause (2).
  Also reported: every weighted metric where a half is IN L while the whole text is OUT L
  (ZL3b, full-size ranges), and each half's v1 band pass/fail on all three files.

Caveat printed with the result: Currier A is mostly hand 1 and herbal pages, so A vs B is
confounded with scribe and section.  This test cannot show two languages, and a SPLIT says
only that the two halves score differently on this board.

Code check before the run (`--check`): run_v2 --voynich (whole) into a scratch path must
reproduce m4's voynich_all row (every numeric key, |diff| <= 1e-6).  The main run repeats
the check on its own whole-text row and on the full-size control rows vs m4.

Usage (project root):
    python n6_ab_split.py --check <scratch_dir>
    python n6_ab_split.py --run
Writes results_n6_*.txt/.json only.  Never touches scoreboard/scoreboard.json.
"""
import argparse
import hashlib
import json
import math
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

M4J = ROOT / "results_m4_phase1_board.json"
STUB = ROOT / "n6_ab_split.prereg.sha256"
OUT = ROOT / "results_n6_ab_split.txt"
N_A, N_B = 11231, 23078
TRANSLIT = {"ZL3b": None, "RF1b": "data/translit/RF1b.meta.json", "IT2a": "data/translit/IT2a.meta.json"}
FAMS = ["L", "C", "G"]
EDGE, LJSD, XCOUP = "x_edge_mi_word", "jsd_first_fg", "cross_excess_eva"
WORKERS = 4


def sh(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run_v2(args):
    cmd = [sys.executable, "-m", "scoreboard.run_v2"] + args
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\n{r.stderr[-2000:]}")
    return " ".join(args)


def row_of(txt):
    return json.loads(Path(txt).with_suffix(".json").read_text(encoding="utf-8"))["row"]


# ---------------------------------------------------------------------------
# ranges (replicates run_v2.main's reading of a ranges file)
# ---------------------------------------------------------------------------
def load_ranges(path, n_sample=25000):
    R = json.loads(Path(path).read_text(encoding="utf-8"))
    ranges, tight, noweight = R["ranges"], R.get("tight", {}), set(R.get("no_weight", []))
    if "types_25k" not in ranges and R.get("rows"):
        ranges["types_25k"] = {}
        for f in FAMS:
            vals = [r["types"] for r in R["rows"] if r.get("family") == f and r.get("types")
                    and r.get("tokens") and r["tokens"] >= n_sample]
            if vals:
                ranges["types_25k"][f] = dict(min=min(vals), max=max(vals), n=len(vals))
    return ranges, tight, noweight


def weighted_keys(noweight):
    from scoreboard import run_v2 as RV
    cls = {a: b for a, b, _ in RV.NEW_KEYS}
    return [k for k in RV.V1_KEYS + RV.NEW_NUMERIC if k not in noweight and cls.get(k, "WEIGHTED") != "REPORT"]


def io_row(row, ranges):
    from scoreboard import run_v2 as RV
    return {k: {f: RV.in_out(RV.fin(row.get(k)), ranges.get(k, {}).get(f)) for f in FAMS}
            for k in RV.V1_KEYS + RV.NEW_NUMERIC}


# ---------------------------------------------------------------------------
# controls (in-process, run_v2.score_one on m4 loaders)
# ---------------------------------------------------------------------------
def control_pages(name, fam):
    import m4_phase1_board as m4
    from scoreboard import run_v2 as RV
    if fam == "L":
        import corpora
        if name in corpora.CONTROLS:
            pg, _ = m4.natural_from_control(name)
        else:
            pg, _ = m4.natural_from_ext(name)
    else:
        _, pg = RV.load_meta(ROOT / "data" / "controls_synthetic" / f"{name}.meta.json")
        pg = RV.subsample(pg, 25000)
    return pg


def score_control(job):
    name, fam, n = job
    from scoreboard import run_v2 as RV
    pg = control_pages(name, fam)
    if n:
        pg = RV.subsample(pg, n)
    row = RV.score_one(name, pg, lambda s: None)
    row.pop("v1_full", None)
    row["family"], row["n_target"] = fam, n
    return row


def fam_members(R4):
    """m4 member corpora per family (union over keys)."""
    mem = {f: set() for f in FAMS}
    for k, d in R4["ranges"].items():
        for f in FAMS:
            if isinstance(d.get(f), dict):  # bake_winner carries lists, not ranges
                mem[f].update(d[f]["members"])
    return mem


def build_matched_ranges(rows, R4, n, path):
    import m4_phase1_board as m4
    from scoreboard import run_v2 as RV
    rr = [dict(r, name=r["name"]) for r in rows]
    ranges = {}
    for k in RV.V1_KEYS + RV.NEW_NUMERIC:
        ranges[k] = {}
        for f in FAMS:
            rg = m4.fam_range(rr, f, k)
            if rg:
                ranges[k][f] = rg
    short = sorted(r["name"] for r in rows if r["tokens"] < n)
    out = dict(run=f"n6 matched {n}", extend=0.10, n_target=n, ranges=ranges,
               tight=R4["tight"], no_weight=R4["no_weight"], rows=[], short_controls=short,
               note="n6 matched-size ranges; tight/no_weight copied from results_m4_phase1_board.json")
    Path(path).write_text(json.dumps(out, indent=1), encoding="utf-8")
    return short


# ---------------------------------------------------------------------------
# verdict
# ---------------------------------------------------------------------------
def half_verdict(ios, weighted, tight):
    """ios: {translit: io_row}.  Returns dict with §2-surviving metrics, outs, verdict."""
    flips = [k for k in weighted if len({json.dumps(ios[t][k], sort_keys=True) for t in ios}) > 1]
    keep = [k for k in weighted if k not in flips]
    z = ios["ZL3b"]
    outs = {f: [k for k in keep if z[k][f] == "OUT"] for f in FAMS}
    na = {f: [k for k in keep if z[k][f] == "NA"] for f in FAMS}
    tout = {f: [k for k in outs[f] if tight.get(k, {}).get(f)] for f in FAMS}
    kill = sorted(f for f in FAMS if len(tout[f]) >= 3)
    fav = [f for f in FAMS if all(len(outs[f]) + 2 <= len(outs[g]) for g in FAMS if g != f)]
    fav = fav[0] if fav else "undecided"
    return dict(flipped=flips, kept=keep, outs=outs, na=na, tight_outs=tout, kill=kill,
                favoured=fav, verdict=[fav, kill])


def in_L_both(ios):
    return all(ios[t][EDGE]["L"] == "IN" and ios[t][LJSD]["L"] == "IN" for t in ios)


def decide(vA, vB, iosA, iosB):
    c1 = vA["verdict"] != vB["verdict"]
    a_in, b_in = in_L_both(iosA), in_L_both(iosB)
    c2 = a_in and not b_in
    return dict(split=c1 or c2, clause1=c1, clause2=c2, A_in_L_edge_and_jsd=a_in, B_in_L_edge_and_jsd=b_in,
                label="SPLIT" if (c1 or c2) else "SAME")


# ---------------------------------------------------------------------------
def check(scratch):
    scratch = Path(scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    out = scratch / "n6_check_voy_all.txt"
    run_v2(["--voynich", "--ranges", str(M4J), "--out", str(out)])
    return repro(row_of(out), "voynich_all")


def repro(row, m4name, tol=1e-6):
    from scoreboard import run_v2 as RV
    R4 = json.loads(M4J.read_text(encoding="utf-8"))
    m = next(r for r in R4["rows"] if r["name"] == m4name)
    bad = []
    for k in RV.V1_KEYS + RV.NEW_NUMERIC:
        if k == "types_25k" or k not in m:
            continue
        a, b = RV.fin(row.get(k)), RV.fin(m.get(k))
        if (a is None) != (b is None) or (a is not None and abs(a - b) > tol):
            bad.append((k, a, b))
    for k in ("tokens", "types"):
        if row.get(k) != m.get(k):
            bad.append((k, row.get(k), m.get(k)))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", metavar="SCRATCH")
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.check:
        bad = check(a.check)
        print("CODE CHECK whole-text vs m4 voynich_all:", "PASS" if not bad else f"FAIL {bad}")
        sys.exit(0 if not bad else 1)
    if not a.run:
        ap.error("--check or --run")

    log = []

    def emit(s=""):
        print(s, flush=True)
        log.append(s)

    me = sh(__file__)
    stub = STUB.read_text(encoding="utf-8") if STUB.exists() else ""
    hash_ok = me in stub
    emit(f"# results_n6_ab_split: Currier A vs B on the frozen PREREG-v2 board (O-010)")
    emit(f"# run {datetime.now().strftime('%Y-%m-%d %H:%M')} (system clock); script sha256 {me}; "
         f"stub {STUB.name}: {'MATCH' if hash_ok else 'MISMATCH -> reported, not scored'}")
    emit(f"# ranges: {M4J.name} (full size); results_n6_ranges_A11k.json / results_n6_ranges_B23k.json (matched)")
    emit(f"# PREREG-v2.md sha256 {sh(ROOT / 'PREREG-v2.md')[:16]}  run_v2.py {sh(ROOT / 'scoreboard' / 'run_v2.py')[:16]}")
    emit("# CAVEAT: Currier A is mostly hand 1 and herbal pages, so A vs B is confounded with scribe and")
    emit("#         section. This test does not and cannot show two languages.")
    emit()

    R4 = json.loads(M4J.read_text(encoding="utf-8"))
    mem = fam_members(R4)
    jobs_full = [(n, "L", None) for n in sorted(mem["L"])]
    jobs_m = [(n, f, sz) for sz in (N_A, N_B) for f in FAMS for n in sorted(mem[f])]

    # --- 1. subprocess run_v2 runs: Voynich halves/whole on three files, C/G full size ---
    sub = {}
    for t, meta in TRANSLIT.items():
        for lang in ("A", "B", None):
            tag = f"voy_{lang or 'all'}" if t == "ZL3b" else f"{t.lower()}_{lang or 'all'}"
            out = f"results_n6_{tag}.txt"
            src = ["--voynich"] if meta is None else ["--meta", meta, "--name", t]
            if meta is not None and lang is None:
                src += ["--n-sample", "40000"]
            sub[(t, lang, "full")] = (src + (["--lang", lang] if lang else []) +
                                      ["--ranges", str(M4J.name), "--out", out], out)
    for f in ("C", "G"):
        for n in sorted(mem[f]):
            sub[("ctl", n, "full")] = (["--meta", f"data/controls_synthetic/{n}.meta.json",
                                        "--ranges", M4J.name, "--out", f"results_n6_{n}.txt"],
                                       f"results_n6_{n}.txt")
    with ThreadPoolExecutor(WORKERS) as ex:
        for done in ex.map(lambda v: run_v2(v[0]), sub.values()):
            print("done:", done, flush=True)

    # --- 2. in-process controls: L full, all matched ---
    with ProcessPoolExecutor(WORKERS) as ex:
        rows_full = list(ex.map(score_control, jobs_full))
        rows_m = list(ex.map(score_control, jobs_m))
    rows_full += [dict(row_of(ROOT / sub[("ctl", n, "full")][1]), family=f, name=n)
                  for f in ("C", "G") for n in sorted(mem[f])]
    rmA = [r for r in rows_m if r["n_target"] == N_A]
    rmB = [r for r in rows_m if r["n_target"] == N_B]
    shortA = build_matched_ranges(rmA, R4, N_A, ROOT / "results_n6_ranges_A11k.json")
    shortB = build_matched_ranges(rmB, R4, N_B, ROOT / "results_n6_ranges_B23k.json")

    # --- 3. matched-size Voynich halves on three files ---
    msub = {}
    for t, meta in TRANSLIT.items():
        for lang, rf in (("A", "results_n6_ranges_A11k.json"), ("B", "results_n6_ranges_B23k.json")):
            tag = f"voy_{lang}" if t == "ZL3b" else f"{t.lower()}_{lang}"
            out = f"results_n6_{tag}_matched.txt"
            src = ["--voynich"] if meta is None else ["--meta", meta, "--name", t]
            msub[(t, lang, "matched")] = (src + ["--lang", lang, "--ranges", rf, "--out", out], out)
    with ThreadPoolExecutor(WORKERS) as ex:
        for done in ex.map(lambda v: run_v2(v[0]), msub.values()):
            print("done:", done, flush=True)
    sub.update(msub)

    # --- 4. code checks ---
    emit("=== 0. CODE CHECKS ===")
    bad = repro(row_of(ROOT / sub[("ZL3b", None, "full")][1]), "voynich_all")
    emit(f"whole-text ZL3b vs m4 voynich_all: {'PASS' if not bad else 'FAIL ' + str(bad)}")
    for lang in ("A", "B"):
        b = repro(row_of(ROOT / sub[("ZL3b", lang, "full")][1]), f"voynich_{lang}")
        emit(f"ZL3b {lang} vs m4 voynich_{lang}: {'PASS' if not b else 'FAIL ' + str(b)}")
    nb = 0
    for r in rows_full:
        b = repro(r, r["name"])
        if b:
            nb += 1
            emit(f"  control {r['name']} full-size vs m4 row: DIFF {b}")
    emit(f"full-size controls vs m4 rows: {len(rows_full) - nb}/{len(rows_full)} reproduce (|diff|<=1e-6)")

    # --- 5. per-half in/out ---
    rng = {"full": load_ranges(M4J),
           ("matched", "A"): load_ranges(ROOT / "results_n6_ranges_A11k.json"),
           ("matched", "B"): load_ranges(ROOT / "results_n6_ranges_B23k.json")}
    from scoreboard import run_v2 as RV
    res = {}
    cons_bad = []
    for size in ("full", "matched"):
        for lang in ("A", "B", None):
            if size == "matched" and lang is None:
                continue
            ranges, tight, noweight = rng["full"] if size == "full" else rng[("matched", lang)]
            W = weighted_keys(noweight)
            ios, rows = {}, {}
            for t in TRANSLIT:
                row = row_of(ROOT / sub[(t, lang, size)][1])
                rows[t] = row
                ios[t] = io_row(row, ranges)
                for f in FAMS:  # consistency with run_v2's own count
                    mine = sum(1 for k in W if ios[t][k][f] == "OUT")
                    if row.get("in_out", {}).get(f, {}).get("outs") != mine:
                        cons_bad.append((t, lang, size, f, mine, row.get("in_out", {}).get(f)))
            v = half_verdict(ios, W, tight)
            res[(size, lang)] = dict(v=v, ios=ios, rows=rows, W=W)
    emit(f"per-metric in/out recomputation vs run_v2 printed out-counts: "
         f"{'PASS' if not cons_bad else 'FAIL ' + str(cons_bad)}")
    emit(f"matched controls shorter than target: A11k {shortA or '-'}; B23k {shortB or '-'}")
    emit()

    emit("=== 1. v1 SEVEN BANDS per half (PASS/FAIL), ZL3b | RF1b | IT2a ===")
    for lang in ("A", "B", None):
        rs = res[("full", lang)]["rows"]
        emit(f"[{lang or 'all'}]  " + "  ".join(
            f"{t}: joint {'PASS' if rs[t].get('v1_pass') else 'FAIL'} missed {','.join(rs[t].get('v1_missed') or []) or '-'}"
            for t in TRANSLIT))
    emit()

    for size in ("full", "matched"):
        emit(f"=== 2{'a' if size == 'full' else 'b'}. PER-METRIC IN/OUT ({size}-size ranges), L C G on ZL3b; "
             f"'*' = flips between ZL3b/RF1b/IT2a (weight 0 by §2) ===")
        langs = ("A", "B", None) if size == "full" else ("A", "B")
        hdr = f"{'metric':30}" + "".join(f" {('V' + (l or 'all')):>9} {'L':>4}{'C':>4}{'G':>4}" for l in langs)
        emit(hdr)
        W = res[(size, "A")]["W"]
        for k in W:
            cells = ""
            for l in langs:
                R = res[(size, l)]
                val = RV.fin(R["rows"]["ZL3b"].get(k))
                fl = "*" if k in R["v"]["flipped"] else " "
                cells += f" {RV.fmt(val):>9}" + "".join(f"{R['ios']['ZL3b'][k][f]:>4}" for f in FAMS) + fl
            emit(f"{k:30}{cells}")
        emit(f"report-only: {XCOUP} is weighted above; edge clause uses {EDGE} and {LJSD} only")
        for l in langs:
            v = res[(size, l)]["v"]
            emit(f"  [{l or 'all'}] §2-dropped: {', '.join(v['flipped']) or '-'}")
            for f in FAMS:
                emit(f"     {f}: outs={len(v['outs'][f]):2} na={len(v['na'][f])} tight-outs={len(v['tight_outs'][f])}"
                     f"  out: {', '.join(v['outs'][f]) or '-'}")
            emit(f"     favoured: {v['favoured']}   kill-candidates (>=3 tight outs): {', '.join(v['kill']) or '-'}")
        emit()

    emit("=== 3. HALF IN L WHERE WHOLE TEXT IS OUT L (ZL3b, full-size ranges, weighted metrics) ===")
    zall = res[("full", None)]["ios"]["ZL3b"]
    for lang in ("A", "B"):
        R = res[("full", lang)]
        hits = [k for k in R["W"] if R["ios"]["ZL3b"][k]["L"] == "IN" and zall[k]["L"] == "OUT"]
        rob = [k for k in hits if all(R["ios"][t][k]["L"] == "IN" for t in TRANSLIT)]
        emit(f"  {lang}: {', '.join(hits) or '-'}   (IN on all three files: {', '.join(rob) or '-'})")
    for lang in ("A", "B"):
        R = res[("matched", lang)]
        hits = [k for k in R["W"] if R["ios"]["ZL3b"][k]["L"] == "IN" and zall[k]["L"] == "OUT"]
        emit(f"  {lang} matched-size: {', '.join(hits) or '-'}")
    emit()

    emit("=== 4. VERDICT (rule fixed in the docstring) ===")
    dec = {}
    for size in ("full", "matched"):
        A, B = res[(size, "A")], res[(size, "B")]
        d = decide(A["v"], B["v"], A["ios"], B["ios"])
        dec[size] = d
        emit(f"  {size:7}: {d['label']}   clause1 (family verdicts differ): {d['clause1']}  "
             f"[A {A['v']['verdict']} vs B {B['v']['verdict']}]   clause2 (A in L on edge+JSD, B not): {d['clause2']}  "
             f"[A in: {d['A_in_L_edge_and_jsd']}, B in: {d['B_in_L_edge_and_jsd']}]")
        for lang in ("A", "B"):
            io3 = res[(size, lang)]["ios"]
            emit(f"           {lang} L in/out  {EDGE}: " + " ".join(f"{t}={io3[t][EDGE]['L']}" for t in TRANSLIT)
                 + f"   {LJSD}: " + " ".join(f"{t}={io3[t][LJSD]['L']}" for t in TRANSLIT)
                 + f"   {XCOUP} (report): " + " ".join(f"{t}={io3[t][XCOUP]['L']}" for t in TRANSLIT))
    head = dec["full"]["label"] + ("" if dec["full"]["label"] == dec["matched"]["label"] else " (size-fragile)")
    if not hash_ok:
        head += "  [SCRIPT HASH MISMATCH: reported, not scored]"
    emit()
    emit(f"VERDICT n6: {head}   (full-size {dec['full']['label']}, matched-size {dec['matched']['label']})")
    emit("CAVEAT: A is mostly hand 1 / herbal; A vs B = scribe + section + language label together. "
         "No two-language claim follows from this test.")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple, set)):
            return [clean(v) for v in o]
        if isinstance(o, float) and not math.isfinite(o):
            return None
        return o if isinstance(o, (bool, int, float, str)) or o is None else str(o)
    js = dict(verdict=head, decisions=dec,
              halves={f"{s}_{l or 'all'}": dict(v=r["v"], ios=r["ios"]) for (s, l), r in res.items()},
              controls_full=rows_full, controls_matched=rows_m, script_sha256=me, hash_ok=hash_ok)
    OUT.with_suffix(".json").write_text(json.dumps(clean(js), indent=1), encoding="utf-8")
    print(f"wrote {OUT}", flush=True)


if __name__ == "__main__":
    main()
