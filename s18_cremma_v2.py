"""s18 — CREMMA Medii Aevi real-line Latin on the v2 scorer (workflow/phases/phase-1.md, step s18,
with the "Amendments from the independent audit" items 1 and 4 folded in).

PRE-REGISTRATION (frozen in s18_cremma_v2.prereg.sha256 together with tools/cremma_to_meta.py before
any scoring run; nothing below changes after results are seen).

Inputs
  data/controls_realline/cremma_*.meta.json   54 sidecars built by `python -I tools/cremma_to_meta.py`
                                              (CREMMA_MANIFEST.md): 21 per-manuscript x 2 families
                                              (base, _marks) + 3 pooled (prose15, c15, all) x 2 +
                                              3 pooled _relined8 x 2.  The folder is shared with s17;
                                              its non-cremma sidecars are listed, not scored.
  s15_ranges.json                             s15's ranges file (n7 ranges + `within_manuscript`
                                              {metric: {median, lo95, hi95, min, max, n_splits}}).
                                              REQUIRED: the script stops (exit 1) before any scoring,
                                              and before any dry-run summary is accepted, if absent.

Scoring (unchanged scorer, scoreboard/PREREG-v2.sha256), one call per sidecar, `--reuse` skips those
whose results_s18_<name>.json exists:
  python -I scoreboard/run_v2.py --meta <sidecar> --family L --ranges s15_ranges.json --out results_s18_<name>.txt

Per native sidecar (every file that is not a _relined8 twin), on the same load_meta+subsample(25000)
pages run_v2 scored:
  jsd_first_fg, jsd_last_lg (from the .json; jsd_last_lg is JSON-only), x_moran_I, x_edge_mi_word,
  cross_excess_eva, plus
  jsd_first_null / jsd_last_null   a2_position.null(lines, feat, n=30) — 30 within-line shuffles,
                                   random.Random(i) i=0..29, lines with >=3 words — exactly as s17;
  jsd_first_exc / jsd_last_exc     raw - null mean (support-phase1-audit.md item 4: raw JSD is biased
                                   upward at small line counts);
  CHARWIN                          n5_signature_discrimination.score (imported by path; same estimator
                                   as s17), NA with the error text where n5 cannot split the pages.
  Feature lambdas: base family = w[0] / w[-1] by code point (score.py line_metrics convention; a2.stats
  must reproduce run_v2's rounded jsd_first_fg / jsd_last_lg, checked and printed).  _marks family =
  first / last GLYPH UNIT (tools/cremma_to_meta.glyph_units: base code point + following Mn marks),
  per CREMMA_MANIFEST.md ("scorers must segment _marks tokens with that unit"); run_v2's own
  code-point rows for _marks files are kept in their .json but the summary uses the glyph-unit JSDs,
  and the _marks family is a sensitivity, never the decision (audit item 3).
  _relined8 twins get the same JSD null/excess so that s19 can difference the excesses too.

Pooling guard (audit item 1), for the pools prose15 and c15 (members = the `hand` values of the pooled
sidecar; cross-checked with CREMMA_MANIFEST.md):
  (i)   per-manuscript calibrated excess rows for all 21 manuscripts (from the per-manuscript sidecars);
  (ii)  manuscript-weighted mean of the members' jsd_first_exc and jsd_last_exc, weights = scored line
        counts;
  (iii) leave-one-manuscript-out pooled excess: the pooled sidecar's pages minus the held-out
        manuscript's pages (filter on `hand`), subsample(25000), then a2.stats raw and a2.null n=30 on
        the concatenated lines, in memory (no new files);
  (iv)  heterogeneity = max - min of the members' per-manuscript jsd_first_exc within each pool.
  Guard rule: if any member's calibrated jsd_first_exc >= the matched-size Voynich jsd_first excess
  median of its pool (prose15 members vs the 773-line reference, c15 members vs the 1,398-line
  reference), print "GUARD: pooled low does not establish HOLDS"; a verdict of U1 HOLDS then becomes
  "PARTLY INVALIDATED (guard)" (a stricter verdict is left as it is).

Matched-size Voynich reference (audit item 4): ZL3b lines exactly as run_v2 --voynich loads them
(metrics_new.voynich_pages("eva") through run_v2 imported by path; all paragraph lines, no cap).
For k in (lines of cremma_prose15 as scored, lines of cremma_c15 as scored; 773 and 1,398 per the
manifest): 200 draws, rng = random.Random(20261017) re-seeded per k, draw = rng.sample(lines, k);
per draw raw jsd_first (a2.stats, feat w[0]), its null (a2.null n=30 mean) and excess; report the
median and the 2.5 / 97.5 percentiles of each.  The full-ZL3b row (all lines) is printed beside.

s19 (results_s19.txt): for prose15, c15 and all (base family; _marks beside as sensitivity),
native minus _relined8 per metric; flag `>hw` where |difference| exceeds the s15_ranges.json
`within_manuscript` 95 % half-width (hi95 - lo95)/2 for that metric; "n/a" where no width exists.
Re-wrap clause: if the prose15 native-minus-relined8 jsd_first_fg exceeds that half-width, the
real-line effect is reported as that difference.

DECISION (printed verbatim by decision_block(); thresholds in excess terms with the numbers used):
  primary statistic  E = pooled cremma_prose15 jsd_first EXCESS (jsd_first_fg - within-line null mean)
  null_level         = median of the matched-size (prose15 line count) Voynich jsd_first NULL
  lower_bound        = s15_ranges.json within_manuscript.jsd_first_fg.lo95
                       (fallback 0.145, the s2 3B provisional value, printed as a caveat if absent)
  T_hold             = 0.10        - null_level
  T_inval            = lower_bound - null_level
  outcome            "U1 HOLDS"             if E <  T_hold
                     "PARTLY INVALIDATED"   if T_hold <= E < T_inval
                     "INVALIDATED"          if E >= T_inval
  pooling guard      as above; "PARTLY INVALIDATED (guard)" replaces a HOLDS verdict only.
  sensitivity        the same rule applied to cremma_prose15_marks (glyph-unit JSD), printed beside,
                     never the decision.
  kill rule          prose15 >= 5,000 tokens and c15 >= 8,000 tokens as scored (manifest: 6,890 and
                     10,190); if either fails, the verdict line reads "KILL RULE: U1 stays unverified".
  secondary          jsd_last excess and the s15 widths (reported, no threshold).
  caveats            prose15 column count unverified; paragraph proxy = ALTO TextBlock, block-initial
                     (column proxy); abbreviations unresolved so Latin h2/types rows carry no weight.

Run:   python -I s18_cremma_v2.py [--reuse] [--dry-run]
       --dry-run lists what would be done and validates inputs; it scores nothing and writes nothing.
Writes: results_s18_<name>.txt/.json (run_v2), results_s18.txt (everything above), results_s19.txt
        (the re-wrap table only).  Nothing else.  No writes to scoreboard/scoreboard.json or any data/ folder.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _stream in (sys.stdout, sys.stderr):  # -I ignores PYTHONIOENCODING; the console may be cp1252
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

SIDECARS = ROOT / "data" / "controls_realline"
RANGES = ROOT / "s15_ranges.json"
MANIFEST = SIDECARS / "CREMMA_MANIFEST.md"
OUT18 = ROOT / "results_s18.txt"
OUT19 = ROOT / "results_s19.txt"
STUB = ROOT / "s18_cremma_v2.prereg.sha256"
SELF = ROOT / "s18_cremma_v2.py"
BUILDER = ROOT / "tools" / "cremma_to_meta.py"
N_SAMPLE = 25000
RELINE = "_relined8"
MARKS = "_marks"
JSD_NULL_N = 30          # a2_position.null default; random.Random(i), i = 0..29
VOY_SEED = 20261017
VOY_DRAWS = 200
POOLS = ["cremma_prose15", "cremma_c15", "cremma_all"]
GUARD_POOLS = ["cremma_prose15", "cremma_c15"]
# manifest cross-check (CREMMA_MANIFEST.md, pooled sidecars table)
MANIFEST_MEMBERS = {
    "cremma_prose15": {"PalLat373", "LaurPlut53.08", "LaurPlut53.09"},
    "cremma_c15": {"PalLat373", "LaurPlut53.08", "LaurPlut53.09", "LaurPlut39.34", "SBB_PK_Hdschr25",
                   "BGO-511", "Latin8236"},
}
MANIFEST_LINES = {"cremma_prose15": 773, "cremma_c15": 1398}
KILL_TOKENS = {"cremma_prose15": 5000, "cremma_c15": 8000}
HOLD_RAW = 0.10          # stub: "below 0.10 -> U1 holds", restated in excess terms
LOWER_BOUND_FALLBACK = 0.145  # s2 Part 3B provisional jsd_first lower bound
V2_COLS = ["jsd_first_fg", "jsd_first_null", "jsd_first_exc", "jsd_last_lg", "jsd_last_null", "jsd_last_exc",
           "p_init_enrich", "m_final_enrich", "cross_excess_eva", "x_edge_mi_word", "x_position_entropy",
           "x_moran_I", "CHARWIN", "h2", "types_25k"]
S19_COLS = ["jsd_first_fg", "jsd_first_exc", "jsd_last_lg", "jsd_last_exc", "p_init_enrich", "m_final_enrich",
            "cross_excess_eva", "x_edge_mi_word", "x_position_entropy", "x_moran_I", "CHARWIN", "h2", "sd_len",
            "redup_pct", "types_25k"]
log18: list[str] = []
log19: list[str] = []


def emit(s="", also19=False):
    print(s, flush=True)
    log18.append(s)
    if also19:
        log19.append(s)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now; `date` unavailable)"


def load_by_path(modname: str, path: Path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stub_match() -> str:
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
    return "True" if want and not bad else f"False (mismatch: {', '.join(bad) or 'empty stub'})"


def fmt(v, nd=4):
    if v is None:
        return "NA"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def sidecar_name(p: Path) -> str:
    return p.name[: -len(".meta.json")]


def is_marks(name: str) -> bool:
    return name.endswith(MARKS)


def is_relined(name: str) -> bool:
    return name.endswith(RELINE) or name.endswith(RELINE + MARKS)


def base_of(name: str) -> str:
    """cremma_X_relined8_marks -> cremma_X (the native base-family sidecar of any twin)."""
    for suf in (RELINE + MARKS, RELINE, MARKS):
        if name.endswith(suf):
            return name[: -len(suf)]
    return name


# ----------------------------------------------------------------------------- scoring helpers
def run_v2_cmd(sidecar: Path, out_txt: Path) -> list[str]:
    return [sys.executable, "-I", str(ROOT / "scoreboard" / "run_v2.py"), "--meta", str(sidecar),
            "--family", "L", "--ranges", str(RANGES), "--out", str(out_txt)]


def run_v2(sidecar: Path, out_txt: Path):
    cmd = run_v2_cmd(sidecar, out_txt)
    emit(f"  $ {' '.join(Path(c).name if i == 0 else c for i, c in enumerate(cmd))}")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        emit(r.stdout[-2000:])
        emit(r.stderr[-2000:])
        raise SystemExit(f"run_v2 failed on {sidecar.name} (exit {r.returncode})")
    head = [ln for ln in r.stdout.splitlines() if ln.startswith("# pages=")]
    emit(f"    {head[0] if head else '(no page header line)'}")


def jsd_block(a2, lines, feat_first, feat_last) -> dict:
    """raw / null mean / null sd / excess for jsd_first and jsd_last on `lines`, a2_position conventions."""
    f_raw, _ = a2.stats(lines, feat_first)
    _, l_raw = a2.stats(lines, feat_last)
    nf = a2.null(lines, feat_first, n=JSD_NULL_N)[:, 0]
    nl = a2.null(lines, feat_last, n=JSD_NULL_N)[:, 1]
    return dict(jsd_first_raw=float(f_raw), jsd_first_null=float(nf.mean()), jsd_first_null_sd=float(nf.std()),
                jsd_first_exc=float(f_raw - nf.mean()),
                jsd_last_raw=float(l_raw), jsd_last_null=float(nl.mean()), jsd_last_null_sd=float(nl.std()),
                jsd_last_exc=float(l_raw - nl.mean()),
                lines=len(lines), lines_ge3=sum(1 for ws in lines if len(ws) >= 3))


def features(glyph_units, marks: bool):
    if marks:
        return (lambda w: glyph_units(w)[0]), (lambda w: glyph_units(w)[-1])
    return (lambda w: w[0]), (lambda w: w[-1])


def pct(vals, q):
    import numpy as np
    return float(np.percentile(np.array(vals, dtype=float), q))


# ----------------------------------------------------------------------------- decision
def outcome_of(E: float, t_hold: float, t_inval: float) -> str:
    if E < t_hold:
        return "U1 HOLDS"
    if E < t_inval:
        return "PARTLY INVALIDATED"
    return "INVALIDATED"


def decision_block(E, E_marks, null_level, lower_bound, lower_bound_source, guard_hits, kill, widths_note,
                   secondary, rewrap):
    t_hold = HOLD_RAW - null_level
    t_inval = lower_bound - null_level
    emit("=== DECISION (pre-registered rule, s18_cremma_v2.prereg.sha256; phase-1.md stub as amended) ===")
    emit("primary statistic: E = pooled cremma_prose15 jsd_first EXCESS = jsd_first_fg - within-line null mean "
         "(a2_position.null n=30)")
    emit(f"null_level  = {null_level:.4f}  (median matched-size Voynich jsd_first NULL, {VOY_DRAWS} draws of "
         f"{secondary['k_prose15']} ZL3b lines, seed {VOY_SEED})")
    emit(f"lower_bound = {lower_bound:.4f}  ({lower_bound_source})")
    emit(f"thresholds in excess terms: T_hold = 0.10 - {null_level:.4f} = {t_hold:.4f};  "
         f"T_inval = {lower_bound:.4f} - {null_level:.4f} = {t_inval:.4f}")
    emit("rule: E < T_hold -> \"U1 HOLDS\";  T_hold <= E < T_inval -> \"PARTLY INVALIDATED\";  "
         "E >= T_inval -> \"INVALIDATED\"")
    emit(f"E (cremma_prose15, base family) = {E:.4f}  "
         f"(raw {secondary['prose15_raw']:.4f}, null {secondary['prose15_null']:.4f}±{secondary['prose15_null_sd']:.4f}, "
         f"{secondary['prose15_lines']} lines, {secondary['prose15_tokens']} tokens)")
    verdict = outcome_of(E, t_hold, t_inval)
    emit(f"outcome before guard: {verdict}")
    emit(f"pooling guard: any prose15 / c15 member calibrated jsd_first_exc >= its pool's matched-size Voynich "
         f"excess median? {'YES: ' + ', '.join(guard_hits) if guard_hits else 'no'}")
    if guard_hits:
        emit("GUARD: pooled low does not establish HOLDS")
        if verdict == "U1 HOLDS":
            verdict = "PARTLY INVALIDATED (guard)"
    emit(f"kill rule: prose15 tokens {kill['cremma_prose15']} >= 5,000: {'met' if kill['cremma_prose15'] >= 5000 else 'NOT met'};  "
         f"c15 tokens {kill['cremma_c15']} >= 8,000: {'met' if kill['cremma_c15'] >= 8000 else 'NOT met'}")
    if kill["cremma_prose15"] < 5000 or kill["cremma_c15"] < 8000:
        emit("KILL RULE: U1 stays unverified (s17 stands alone); the verdict below is void")
        verdict = "KILL RULE: U1 stays unverified"
    emit(f"VERDICT: {verdict}")
    if E_marks is None:
        emit("sensitivity (_marks family, glyph-unit JSD, same thresholds): NA")
    else:
        emit(f"sensitivity (_marks family, glyph-unit JSD, same thresholds, NOT the decision): E_marks = {E_marks:.4f} -> "
             f"{outcome_of(E_marks, t_hold, t_inval)}")
    emit(f"secondary: cremma_prose15 jsd_last excess = {secondary['prose15_last_exc']:.4f} "
         f"(raw {secondary['prose15_last_raw']:.4f}, null {secondary['prose15_last_null']:.4f}); s15 widths: {widths_note}")
    emit(f"re-wrap clause: prose15 native - relined8 jsd_first_fg = {fmt(rewrap['diff'])}, s15 half-width = "
         f"{fmt(rewrap['hw'])} -> {rewrap['verdict']}")
    emit("caveats carried: prose15 column count unverified; paragraph proxy = ALTO TextBlock, block-initial (column "
         "proxy); abbreviations unresolved so Latin h2/types rows carry no weight; _marks under-represents detached "
         "signs (manifest).")
    return verdict


# ----------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reuse", action="store_true", help="skip run_v2 where results_s18_<name>.json exists")
    ap.add_argument("--dry-run", action="store_true", help="list what would be done, validate inputs, score nothing")
    args = ap.parse_args(argv)

    # ---- inputs
    all_sidecars = sorted(SIDECARS.glob("*.meta.json"))
    cremma = [p for p in all_sidecars if p.name.startswith("cremma_")]
    others = [p.name for p in all_sidecars if not p.name.startswith("cremma_")]
    names = [sidecar_name(p) for p in cremma]
    native = [n for n in names if not is_relined(n)]
    relined = [n for n in names if is_relined(n)]
    per_ms = sorted(n for n in native if not is_marks(n) and n not in POOLS)
    problems = []
    if len(cremma) != 54:
        problems.append(f"expected 54 cremma_*.meta.json sidecars, found {len(cremma)}")
    for pool in POOLS:
        for suf in ("", MARKS, RELINE, RELINE + MARKS):
            if pool + suf not in names:
                problems.append(f"missing sidecar {pool}{suf}.meta.json")
    if len(per_ms) != 21:
        problems.append(f"expected 21 per-manuscript base sidecars, found {len(per_ms)}: {per_ms}")
    for n in per_ms:
        if n + MARKS not in names:
            problems.append(f"missing {n}{MARKS}.meta.json")
    for req in (BUILDER, ROOT / "scoreboard" / "run_v2.py", ROOT / "a2_position.py",
                ROOT / "n5_signature_discrimination.py", MANIFEST):
        if not req.exists():
            problems.append(f"missing {req.relative_to(ROOT)}")

    if args.dry_run:
        print("S18 DRY RUN: nothing is scored, nothing is written.")
        print(f"cwd/root = {ROOT}")
        print(f"script sha256={sha256(SELF)}  builder tools/cremma_to_meta.py sha256={sha256(BUILDER) if BUILDER.exists() else 'absent'}  "
              f"stub_match={stub_match()}")
        print(f"sidecars in {SIDECARS.relative_to(ROOT)}: {len(all_sidecars)} total, {len(cremma)} cremma_* "
              f"({len(native)} native incl. {sum(1 for n in native if is_marks(n))} _marks; {len(relined)} _relined8 twins), "
              f"{len(others)} non-cremma (s17's, not scored): {', '.join(others)}")
        print(f"per-manuscript base sidecars ({len(per_ms)}): {', '.join(per_ms)}")
        print(f"pools: {', '.join(POOLS)}; guard pools: {', '.join(GUARD_POOLS)}")
        # validate the pooled sidecars' members and line/token counts against the manifest
        try:
            R2 = load_by_path("run_v2_s18", ROOT / "scoreboard" / "run_v2.py")
            for pool in GUARD_POOLS:
                _, pages = R2.load_meta(SIDECARS / f"{pool}.meta.json")
                pages = R2.subsample(pages, N_SAMPLE)
                hands = {p["hand"] for p in pages}
                nl = sum(len(p["lines"]) for p in pages)
                nt = sum(len(ln) for p in pages for ln in p["lines"])
                ok_m = hands == MANIFEST_MEMBERS[pool]
                ok_l = nl == MANIFEST_LINES[pool]
                print(f"  {pool}: members={sorted(hands)} manifest_match={ok_m}; lines={nl} (manifest {MANIFEST_LINES[pool]}) "
                      f"match={ok_l}; tokens={nt} kill-bar {KILL_TOKENS[pool]}: {'met' if nt >= KILL_TOKENS[pool] else 'NOT met'}")
                if not ok_m:
                    problems.append(f"{pool} members differ from the manifest")
                if not ok_l:
                    problems.append(f"{pool} line count differs from the manifest")
            a2 = load_by_path("a2_position", ROOT / "a2_position.py")
            cm = load_by_path("cremma_to_meta", BUILDER)
            print(f"  imports ok: run_v2 (load_meta, subsample, M.voynich_pages), a2_position (stats, null), "
                  f"cremma_to_meta.glyph_units('a\\u0303x')={ascii(cm.glyph_units('ãx'))}; n5 is imported at scoring time only")
            nvoy = len([ln for p in R2.M.voynich_pages("eva") for ln in p["lines"]])
            print(f"  Voynich ZL3b lines as loaded by run_v2 --voynich: {nvoy} (draws of 773 and 1,398 lines, {VOY_DRAWS} each, seed {VOY_SEED})")
            _ = a2
        except Exception as e:  # noqa: BLE001
            problems.append(f"import/validation error: {e!r}")
        print("would run, in this order:")
        for n in names:
            print(f"  python -I scoreboard/run_v2.py --meta data/controls_realline/{n}.meta.json --family L "
                  f"--ranges s15_ranges.json --out results_s18_{n}.txt"
                  + ("   [reuse: json exists]" if args.reuse and (ROOT / f"results_s18_{n}.json").exists() else ""))
        print("then: JSD null/excess + CHARWIN per sidecar; pooling guard (per-manuscript, weighted mean, LOO, "
              "heterogeneity); matched-size Voynich reference; s19 table; decision block; write results_s18.txt and results_s19.txt")
        if problems:
            print("input problems: " + "; ".join(problems))
        if not RANGES.exists():
            print(f"STOP: {RANGES.name} is absent (s15 has not written it yet). s18 scores with --ranges {RANGES.name} "
                  f"and reads its within_manuscript block; run s15_band_widths.py first. Nothing was scored or written.")
            return 1
        print(f"s15_ranges.json present, sha256={sha256(RANGES)}")
        return 1 if problems else 0

    if not RANGES.exists():
        raise SystemExit(f"STOP: {RANGES.name} is absent (s15 has not written it yet). s18 scores with --ranges "
                         f"{RANGES.name} and reads its within_manuscript block; run s15_band_widths.py first. "
                         f"Nothing was scored or written.")
    if problems:
        raise SystemExit("STOP: input problems: " + "; ".join(problems))

    started = clock()
    hdr = [
        "S18: CREMMA Medii Aevi real-line Latin on the v2 scorer (phase-1.md step s18, audit items 1 and 4 folded)",
        f"run started {started}",
        f"s18_cremma_v2.py sha256={sha256(SELF)}  tools/cremma_to_meta.py sha256={sha256(BUILDER)}  prereg stub_match={stub_match()}",
        f"ranges file {RANGES.name} sha256={sha256(RANGES)}  scorer scoreboard/run_v2.py sha256={sha256(ROOT / 'scoreboard' / 'run_v2.py')[:16]}…",
        f"sidecars scored: {len(cremma)} cremma_* ({len(native)} native incl. _marks, {len(relined)} _relined8 twins); "
        f"non-cremma sidecars present and NOT scored (s17's): {', '.join(others) or 'none'}",
    ]
    for h in hdr:
        emit(h, also19=True)
    emit("", also19=True)

    # ---- run_v2 on every cremma sidecar
    emit("=== run_v2 --family L --ranges s15_ranges.json, one call per sidecar ===")
    for p, n in zip(cremma, names):
        out_txt = ROOT / f"results_s18_{n}.txt"
        if args.reuse and out_txt.with_suffix(".json").exists():
            emit(f"  reuse {out_txt.with_suffix('.json').name}")
            continue
        run_v2(p, out_txt)
    emit()

    # ---- collect rows; JSD null/excess; CHARWIN
    R2 = load_by_path("run_v2_s18", ROOT / "scoreboard" / "run_v2.py")
    a2 = load_by_path("a2_position", ROOT / "a2_position.py")
    cm = load_by_path("cremma_to_meta", BUILDER)
    n5 = load_by_path("n5_signature_discrimination", ROOT / "n5_signature_discrimination.py")
    R = json.loads(RANGES.read_text(encoding="utf-8"))
    wm = R.get("within_manuscript") or {}

    def half_width(metric):
        w = wm.get(metric)
        if isinstance(w, dict) and w.get("lo95") is not None and w.get("hi95") is not None:
            return (float(w["hi95"]) - float(w["lo95"])) / 2.0
        return None

    rows, pages_of, checks = {}, {}, []
    emit(f"=== per sidecar: JSD within-line permutation null (a2_position.null, n={JSD_NULL_N}) and excess, CHARWIN (n5), "
         "on load_meta+subsample(25000) pages; _marks JSDs use glyph units ===")
    emit(f"{'sidecar':36} | {'lines':>5} {'tokens':>6} | {'jsd_f raw':>9} {'null':>13} {'excess':>8} | "
         f"{'jsd_l raw':>9} {'null':>13} {'excess':>8} | {'CHARWIN':>8} | a2==run_v2 (cp)")
    for p, n in zip(cremma, names):
        js = json.loads((ROOT / f"results_s18_{n}.json").read_text(encoding="utf-8"))
        row = js["row"]
        row["jsd_last_lg"] = (row.get("v1_full") or {}).get("jsd_last_lg")
        _, pages = R2.load_meta(p)
        pages = R2.subsample(pages, N_SAMPLE)
        pages_of[n] = pages
        lines = [ln for q in pages for ln in q["lines"]]
        # consistency: a2.stats by code point must reproduce run_v2's rounded jsd (both families)
        f_cp, _ = a2.stats(lines, lambda w: w[0])
        _, l_cp = a2.stats(lines, lambda w: w[-1])
        same_f = row.get("jsd_first_fg") is not None and round(float(f_cp), 4) == row["jsd_first_fg"]
        same_l = row.get("jsd_last_lg") is not None and round(float(l_cp), 4) == row["jsd_last_lg"]
        checks.append((n, same_f, same_l))
        ff, fl = features(cm.glyph_units, is_marks(n))
        jb = jsd_block(a2, lines, ff, fl)
        if is_marks(n):
            row["jsd_first_fg_codepoint"], row["jsd_last_lg_codepoint"] = row.get("jsd_first_fg"), row.get("jsd_last_lg")
            row["jsd_first_fg"], row["jsd_last_lg"] = jb["jsd_first_raw"], jb["jsd_last_raw"]
        for k in ("jsd_first_null", "jsd_first_null_sd", "jsd_first_exc", "jsd_last_null", "jsd_last_null_sd", "jsd_last_exc"):
            row[k] = jb[k]
        row["lines_ge3"] = jb["lines_ge3"]
        try:
            s = n5.score(pages)
            row["CHARWIN"] = s["CHARWIN"]
            row["n5_error"] = None
        except Exception as e:  # noqa: BLE001
            row["CHARWIN"] = None
            row["n5_error"] = repr(e)
        rows[n] = row
        emit(f"{n:36} | {len(lines):5d} {row['tokens']:6d} | {jb['jsd_first_raw']:9.4f} "
             f"{jb['jsd_first_null']:.4f}±{jb['jsd_first_null_sd']:.4f} {jb['jsd_first_exc']:+8.4f} | "
             f"{jb['jsd_last_raw']:9.4f} {jb['jsd_last_null']:.4f}±{jb['jsd_last_null_sd']:.4f} {jb['jsd_last_exc']:+8.4f} | "
             f"{fmt(row['CHARWIN']):>8} | {same_f}/{same_l}" + (f"  n5: {row['n5_error']}" if row["n5_error"] else ""))
    badj = [n for n, a, b in checks if not (a and b)]
    emit(f"a2_position.stats(code point) vs run_v2 raw JSD: {'all equal' if not badj else 'MISMATCH on ' + ', '.join(badj)}")
    emit()

    # ---- full metric table
    emit("=== v2 metrics per sidecar (run_v2 rows + JSD null/excess + n5 CHARWIN; _marks JSDs = glyph unit) ===")
    emit(f"{'sidecar':36} | {'lines':>5} {'tokens':>6} | " + " ".join(f"{c:>12}" for c in V2_COLS))
    for n in names:
        r = rows[n]
        emit(f"{n:36} | {r['lines']:5d} {r['tokens']:6d} | " + " ".join(f"{fmt(r.get(k)):>12}" for k in V2_COLS))
    emit()

    # ---- matched-size Voynich reference (audit item 4)
    emit(f"=== matched-size Voynich reference: ZL3b lines as run_v2 --voynich loads them, {VOY_DRAWS} draws per size, "
         f"random.Random({VOY_SEED}).sample, a2.stats / a2.null n={JSD_NULL_N} ===")
    voy_lines = [ln for q in R2.M.voynich_pages("eva") for ln in q["lines"]]
    full = jsd_block(a2, voy_lines, lambda w: w[0], lambda w: w[-1])
    emit(f"ZL3b full: {len(voy_lines)} lines; jsd_first raw {full['jsd_first_raw']:.4f} null {full['jsd_first_null']:.4f} "
         f"excess {full['jsd_first_exc']:+.4f}; jsd_last raw {full['jsd_last_raw']:.4f} null {full['jsd_last_null']:.4f} "
         f"excess {full['jsd_last_exc']:+.4f}")
    k_of = {pool: rows[pool]["lines"] for pool in GUARD_POOLS}
    voy_ref = {}
    for pool in GUARD_POOLS:
        k = k_of[pool]
        if k != MANIFEST_LINES[pool]:
            emit(f"  note: {pool} scored lines {k} != manifest {MANIFEST_LINES[pool]}; draws use the scored count")
        rng = random.Random(VOY_SEED)
        raws, nulls, excs = [], [], []
        for _ in range(VOY_DRAWS):
            draw = rng.sample(voy_lines, k)
            jb = jsd_block(a2, draw, lambda w: w[0], lambda w: w[-1])
            raws.append(jb["jsd_first_raw"]); nulls.append(jb["jsd_first_null"]); excs.append(jb["jsd_first_exc"])
        voy_ref[pool] = dict(k=k, raw_med=pct(raws, 50), raw_lo=pct(raws, 2.5), raw_hi=pct(raws, 97.5),
                             null_med=pct(nulls, 50), null_lo=pct(nulls, 2.5), null_hi=pct(nulls, 97.5),
                             exc_med=pct(excs, 50), exc_lo=pct(excs, 2.5), exc_hi=pct(excs, 97.5))
        v = voy_ref[pool]
        emit(f"  matched to {pool} ({k} lines): jsd_first raw median {v['raw_med']:.4f} [{v['raw_lo']:.4f}, {v['raw_hi']:.4f}]; "
             f"null median {v['null_med']:.4f} [{v['null_lo']:.4f}, {v['null_hi']:.4f}]; "
             f"excess median {v['exc_med']:+.4f} [{v['exc_lo']:+.4f}, {v['exc_hi']:+.4f}]")
    emit()

    # ---- pooling guard (audit item 1)
    emit("=== pooling guard (audit item 1): per-manuscript calibrated excess, weighted mean, leave-one-out, heterogeneity ===")
    emit(f"{'manuscript':22} | {'lines':>5} {'tokens':>6} | {'jsd_first_exc':>13} {'jsd_last_exc':>12} | "
         f"{'marks_first_exc':>15} | pools")
    members = {pool: sorted({q["hand"] for q in pages_of[pool]}) for pool in GUARD_POOLS}
    for pool in GUARD_POOLS:
        if set(members[pool]) != MANIFEST_MEMBERS[pool]:
            emit(f"  WARNING: {pool} members {members[pool]} differ from the manifest {sorted(MANIFEST_MEMBERS[pool])}")
    for n in per_ms:
        ms = n[len("cremma_"):]
        r, rm = rows[n], rows.get(n + MARKS, {})
        pools = [pool for pool in GUARD_POOLS if ms in members[pool]]
        emit(f"{ms:22} | {r['lines']:5d} {r['tokens']:6d} | {r['jsd_first_exc']:+13.4f} {r['jsd_last_exc']:+12.4f} | "
             f"{fmt(rm.get('jsd_first_exc')):>15} | {', '.join(p[len('cremma_'):] for p in pools) or '-'}")
    emit()
    guard_hits = []
    for pool in GUARD_POOLS:
        mem = [f"cremma_{m}" for m in members[pool]]
        wts = {m: rows[m]["lines"] for m in mem}
        W = sum(wts.values())
        wmean_f = sum(rows[m]["jsd_first_exc"] * wts[m] for m in mem) / W
        wmean_l = sum(rows[m]["jsd_last_exc"] * wts[m] for m in mem) / W
        excs = {m: rows[m]["jsd_first_exc"] for m in mem}
        het = max(excs.values()) - min(excs.values())
        emit(f"{pool}: pooled jsd_first_exc {rows[pool]['jsd_first_exc']:+.4f} (raw {rows[pool]['jsd_first_fg']:.4f}, "
             f"null {rows[pool]['jsd_first_null']:.4f}); members {', '.join(members[pool])}")
        emit(f"  (ii) manuscript-weighted mean (weights = scored lines, total {W}): jsd_first_exc {wmean_f:+.4f}, "
             f"jsd_last_exc {wmean_l:+.4f}")
        emit("  (iii) leave-one-manuscript-out pooled excess (pooled sidecar pages minus that hand, in memory):")
        for m in mem:
            ms = m[len("cremma_"):]
            keep = [q for q in pages_of[pool] if q["hand"] != ms]
            keep = R2.subsample(keep, N_SAMPLE)
            lines = [ln for q in keep for ln in q["lines"]]
            jb = jsd_block(a2, lines, lambda w: w[0], lambda w: w[-1])
            emit(f"    without {ms:16} lines={len(lines):5d}  jsd_first raw {jb['jsd_first_raw']:.4f} null {jb['jsd_first_null']:.4f} "
                 f"excess {jb['jsd_first_exc']:+.4f}  | jsd_last excess {jb['jsd_last_exc']:+.4f}")
        top = max(excs, key=excs.get)
        emit(f"  (iv) heterogeneity (max - min member jsd_first_exc) = {het:.4f}  "
             f"(max {excs[top]:+.4f} {top[len('cremma_'):]}, min {min(excs.values()):+.4f} {min(excs, key=excs.get)[len('cremma_'):]})")
        bar = voy_ref[pool]["exc_med"]
        hits = [m[len("cremma_"):] for m in mem if excs[m] >= bar]
        emit(f"  guard vs matched-size Voynich excess median {bar:+.4f} ({voy_ref[pool]['k']} lines): "
             f"{'HIT: ' + ', '.join(hits) if hits else 'no member reaches it'}")
        guard_hits += [f"{h} ({pool[len('cremma_'):]})" for h in hits]
        emit()

    # ---- s19: native minus relined8
    emit("=== s19: native minus _relined8 per metric; flag >hw where |diff| exceeds the s15 within_manuscript 95 % "
         "half-width (hi95-lo95)/2; n/a where no width ===", also19=True)
    hw_avail = {k: half_width(k) for k in S19_COLS}
    emit("half-widths: " + ", ".join(f"{k}={fmt(v)}" for k, v in hw_avail.items() if v is not None) or "none", also19=True)
    emit(f"{'pool':24} | {'family':6} | {'lines n/r':>11} | " + " ".join(f"{c:>13}" for c in S19_COLS), also19=True)
    s19 = {}
    for pool in POOLS:
        for fam, suf in (("base", ""), ("marks", MARKS)):
            a = rows[pool + suf]
            b = rows[pool + RELINE + suf]
            cells, diffs = [], {}
            for k in S19_COLS:
                if a.get(k) is None or b.get(k) is None:
                    cells.append(f"{'NA':>13}")
                    diffs[k] = None
                    continue
                d = a[k] - b[k]
                diffs[k] = d
                hwk = hw_avail[k]
                flag = "n/a" if hwk is None else (">hw" if abs(d) > hwk else "<=hw")
                cells.append(f"{d:+.4f} {flag:>4}".rjust(13))
            s19[(pool, fam)] = diffs
            emit(f"{pool:24} | {fam:6} | {a['lines']:5d}/{b['lines']:5d} | " + " ".join(cells), also19=True)
    emit("(_marks rows: glyph-unit JSDs; sensitivity only, not comparable to an EVA band without that qualification)",
         also19=True)
    emit("", also19=True)

    # ---- decision
    lb = wm.get("jsd_first_fg", {}).get("lo95") if isinstance(wm.get("jsd_first_fg"), dict) else None
    if lb is None:
        lower_bound, lb_src = LOWER_BOUND_FALLBACK, "CAVEAT: s15_ranges.json carries no within_manuscript.jsd_first_fg.lo95; provisional s2 3B value used"
    else:
        lower_bound, lb_src = float(lb), "s15_ranges.json within_manuscript.jsd_first_fg.lo95"
    pr = rows["cremma_prose15"]
    prm = rows.get("cremma_prose15" + MARKS)
    hw_j = hw_avail["jsd_first_fg"]
    d_j = s19[("cremma_prose15", "base")]["jsd_first_fg"]
    rewrap = dict(diff=d_j, hw=hw_j,
                  verdict=("n/a (no s15 width)" if hw_j is None or d_j is None else
                           (f"exceeds: real-line effect reported as {d_j:+.4f}" if abs(d_j) > hw_j else "within the s15 width")))
    secondary = dict(k_prose15=voy_ref["cremma_prose15"]["k"], prose15_raw=pr["jsd_first_fg"],
                     prose15_null=pr["jsd_first_null"], prose15_null_sd=pr["jsd_first_null_sd"],
                     prose15_lines=pr["lines"], prose15_tokens=pr["tokens"],
                     prose15_last_exc=pr["jsd_last_exc"], prose15_last_raw=pr["jsd_last_lg"], prose15_last_null=pr["jsd_last_null"])
    kill = {pool: rows[pool]["tokens"] for pool in GUARD_POOLS}
    widths_note = ", ".join(f"{k} hw={fmt(v)}" for k, v in hw_avail.items() if v is not None) or "none in s15_ranges.json"
    verdict = decision_block(E=pr["jsd_first_exc"], E_marks=(prm or {}).get("jsd_first_exc"),
                             null_level=voy_ref["cremma_prose15"]["null_med"], lower_bound=lower_bound,
                             lower_bound_source=lb_src, guard_hits=guard_hits, kill=kill, widths_note=widths_note,
                             secondary=secondary, rewrap=rewrap)
    emit()
    errs = {n: r["errors"] for n, r in rows.items() if r.get("errors")}
    if errs:
        emit(f"run_v2 step errors: {json.dumps(errs)}")
    n5e = {n: r["n5_error"] for n, r in rows.items() if r.get("n5_error")}
    if n5e:
        emit(f"n5 CHARWIN errors: {json.dumps(n5e)}")
    emit(f"done-when (s18): pooled prose15 row ({pr['tokens']} tokens), cremma_c15, cremma_all and {len(per_ms)} per-manuscript rows "
         f"with the pre-registered verdict -> {'MET' if pr['tokens'] >= 5000 and len(per_ms) == 21 else 'NOT MET'}; verdict = {verdict}")
    emit(f"done-when (s19): results_s19.txt for prose15, c15 and all -> MET")
    fin = f"run finished {clock()}"
    emit(fin, also19=True)
    OUT18.write_text("\n".join(log18) + "\n", encoding="utf-8", newline="\n")
    OUT19.write_text("\n".join(log19) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT18} and {OUT19}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
