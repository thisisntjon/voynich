"""s17 — real-line control corpora on the v2 scorer (workflow/phases/phase-1.md, step s17).

PRE-REGISTRATION (frozen in s17_realline_v2.prereg.sha256 together with tools/realline_to_meta.py
before any scoring run; nothing below changes after results are seen).

Inputs
  data/controls_realline/*.meta.json   built by `python -I tools/realline_to_meta.py`: five real-line
                                       corpora (gib_realline_pooled, mhg_nibelungenlied, oldfrench_roland,
                                       occitan_croisade, italian_dante) and their `_relined8` twins
                                       (same tokens, 8-token lines).
  s15_ranges.json                      the s15 ranges file (n7's L/C/G/X ranges + `within_manuscript`).
                                       REQUIRED: this script stops before any scoring if it is absent.
  results_s2_u123_controls.txt         s2 Part 1 (v1 estimator, native vs 8-word) lines 5-16, cited as prior.

Scoring (unchanged scorer, scoreboard/PREREG-v2.sha256):
  for every sidecar:  python -I scoreboard/run_v2.py --meta <sidecar> --family L --ranges s15_ranges.json
                                                     --out results_s17_<name>.txt
  (25k-token cap, whole lines, corpus order = run_v2.subsample; no --lang: every page has lang "?").

Summary results_s17.txt, per corpus, native beside relined8:
  jsd_first_fg, p_init_enrich, m_final_enrich, cross_excess_eva   printed row keys of run_v2;
  jsd_last_lg                                                     from results_s17_<name>.json
                                                                  ["row"]["v1_full"]["jsd_last_lg"]
                                                                  (phase-1-instrument.md §1: JSON only);
  jsd_first_null, jsd_first_exc, jsd_last_null, jsd_last_exc      within-line permutation null and excess
                                                                  (raw minus null mean) for the two JSDs
                                                                  (support-phase1-audit.md item 4: raw JSD is
                                                                  biased upward at small line counts).  score.py
                                                                  computes NO null for the JSDs (only cross_excess
                                                                  has one), so no such key exists in the run_v2
                                                                  .json; the null is a2_position.null(lines, feat,
                                                                  n=30) — the convention score.py's docstring cites
                                                                  and whose `jsd` score.py imports — on the same
                                                                  subsampled lines: 30 within-line shuffles,
                                                                  random.Random(i) i=0..29, lines with >=3 words,
                                                                  feat = first glyph of the line-initial word vs
                                                                  mid-line words / last glyph of the line-final
                                                                  word vs mid-line words.  null sd (over the 30)
                                                                  is printed as uncertainty.  a2_position.stats on
                                                                  the same lines must reproduce run_v2's rounded
                                                                  jsd_first_fg / jsd_last_lg (checked, printed).
  lines, tokens                                                   per corpus as scored (after the 25k cap).
  x_edge_mi_word, x_position_entropy, x_moran_I                    run_v2 extras;
  CHARWIN                                                          n5's estimator: n5_signature_discrimination.score
                                                                  (imported by path; = bits/token(unigram-GT-renorm)
                                                                  - bits/token(char3-WB), m3.page_split(pages, 20261017)
                                                                  one 80/20 fold, m3.score_folds), computed on the same
                                                                  load_meta+subsample(25000) pages run_v2 scored.
                                                                  This is NOT run_v2's bake_char3_minus_unigram
                                                                  (different estimator, opposite sign); both are shown.
  plus s2 Part 1's v1 numbers (JSDf, JSDl, p_init, m_fin, lines, toks) for the same text, native and 8-word.
Consistency check printed: n5's POSLOCK/MORAN on the same pages must equal run_v2's x_position_entropy /
x_moran_I (same metrics_new.extra_signatures call); a mismatch is reported, not hidden.

Descriptive lines (no new decision; s17's done-when is the table itself):
  * max native jsd_first_fg over the non-Voynich real-line corpora, and whether it stays < 0.10 (the s2
    Part 1 outcome-A threshold re-read on v2);
  * native-minus-relined8 difference per metric, flagged `>width` where s15_ranges.json carries a
    `within_manuscript` width for that metric (s15 §; absent -> "n/a").

Scope: only the five corpora above and their twins (10 files).  data/controls_realline/ is shared with
s18, whose cremma_*.meta.json sidecars are scored by s18_cremma_v2.py, not here; they are listed in the
header as present-and-not-scored.

Run:  python -I s17_realline_v2.py [--reuse]      (--reuse skips run_v2 for sidecars whose
                                                     results_s17_<name>.json already exists)
Writes: results_s17_<name>.txt/.json (run_v2), results_s17.txt (this summary). Nothing else.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SIDECARS = ROOT / "data" / "controls_realline"
RANGES = ROOT / "s15_ranges.json"
S2 = ROOT / "results_s2_u123_controls.txt"
OUT = ROOT / "results_s17.txt"
STUB = ROOT / "s17_realline_v2.prereg.sha256"
N_SAMPLE = 25000
RELINE = "_relined8"
CORPORA = ["gib_realline_pooled", "mhg_nibelungenlied", "oldfrench_roland", "occitan_croisade", "italian_dante"]
S2_LABELS = {"Gibberish_38": "gib_realline_pooled", "MHG_Nibelung": "mhg_nibelungenlied",
             "OldFrench_Rol": "oldfrench_roland", "Occitan_Crois": "occitan_croisade",
             "Dante_Verse": "italian_dante", "Voynich_ZL3b": "voynich_ZL3b"}
V2_COLS = ["jsd_first_fg", "jsd_first_null", "jsd_first_exc", "jsd_last_lg", "jsd_last_null", "jsd_last_exc",
           "p_init_enrich", "m_final_enrich", "cross_excess_eva",
           "x_edge_mi_word", "x_position_entropy", "x_moran_I", "CHARWIN", "bake_char3_minus_unigram"]
JSD_NULL_N = 30  # a2_position.null default; random.Random(i), i = 0..29
log: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


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


# ----------------------------------------------------------------------------- s2 Part 1 prior
S2_RE = re.compile(r"^\s*(?P<label>\S+(?: \S+)?)\s*\((?P<mode>native|8-word)\)\s*\|\s*lines=\s*(?P<lines>\d+)\s+toks=\s*(?P<toks>\d+)"
                   r"\s*\|\s*JSDf=(?P<jsdf>[\d.]+).*?JSDl=(?P<jsdl>[\d.]+)\s*\|\s*p_init=x\s*(?P<pinit>[\d.]+)\s+m_fin=x\s*(?P<mfin>[\d.]+)")


def parse_s2() -> dict:
    """{corpus: {native|relined: {lines,toks,jsdf,jsdl,pinit,mfin}}} from results_s2_u123_controls.txt lines 5-16."""
    out = {}
    if not S2.exists():
        return out
    lines = S2.read_text(encoding="utf-8").splitlines()
    for ln in lines[4:16]:
        m = S2_RE.match(ln)
        if not m:
            continue
        label = m.group("label").replace("(", "").strip()
        key = next((v for k, v in S2_LABELS.items() if label.startswith(k)), None)
        if key is None:
            continue
        mode = "native" if m.group("mode") == "native" else "relined"
        out.setdefault(key, {})[mode] = dict(lines=int(m.group("lines")), toks=int(m.group("toks")),
                                             jsdf=float(m.group("jsdf")), jsdl=float(m.group("jsdl")),
                                             pinit=float(m.group("pinit")), mfin=float(m.group("mfin")))
    return out


# ----------------------------------------------------------------------------- scoring
def run_v2(sidecar: Path, out_txt: Path):
    cmd = [sys.executable, "-I", str(ROOT / "scoreboard" / "run_v2.py"), "--meta", str(sidecar),
           "--family", "L", "--ranges", str(RANGES), "--out", str(out_txt)]
    emit(f"  $ {' '.join(Path(c).name if i == 0 else c for i, c in enumerate(cmd))}")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        emit(r.stdout[-2000:])
        emit(r.stderr[-2000:])
        raise SystemExit(f"run_v2 failed on {sidecar.name} (exit {r.returncode})")
    head = [ln for ln in r.stdout.splitlines() if ln.startswith("# pages=")]
    emit(f"    {head[0] if head else '(no page header line)'}")


def fmt(v, nd=4):
    if v is None:
        return "NA"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reuse", action="store_true", help="skip run_v2 where results_s17_<name>.json exists")
    args = ap.parse_args(argv)

    if not RANGES.exists():
        raise SystemExit(f"STOP: {RANGES.name} is absent (s15 has not written it yet). s17 scores with "
                         f"--ranges {RANGES.name}; run s15_band_widths.py first. Nothing was scored or written.")
    # s17's own sidecars only: data/controls_realline/ is shared with s18, whose cremma_*.meta.json
    # files are scored by s18_cremma_v2.py after its own stub is hashed, not here.
    names = [n for c in CORPORA for n in (c, c + RELINE)]
    sidecars = [SIDECARS / f"{n}.meta.json" for n in names]
    missing = [p.name for p in sidecars if not p.exists()]
    if missing:
        raise SystemExit(f"STOP: sidecar(s) missing in {SIDECARS}: {missing}; run `python -I tools/realline_to_meta.py`.")
    others = sorted(p.name for p in SIDECARS.glob("*.meta.json") if p.name not in {q.name for q in sidecars})

    started = clock()
    emit("S17: real-line control corpora, native vs 8-word re-lined, on the v2 scorer (phase-1.md step s17)")
    emit(f"run started {started}")
    emit(f"s17_realline_v2.py sha256={sha256(ROOT / 's17_realline_v2.py')}  "
         f"tools/realline_to_meta.py sha256={sha256(ROOT / 'tools' / 'realline_to_meta.py')}  "
         f"prereg stub_match={stub_match()}")
    emit(f"ranges file {RANGES.name} sha256={sha256(RANGES)}  scorer scoreboard/run_v2.py sha256={sha256(ROOT / 'scoreboard' / 'run_v2.py')[:16]}…")
    emit(f"sidecars ({len(sidecars)}): {', '.join(names)}")
    emit(f"other sidecars present in {SIDECARS.name}/ and NOT scored here (s18's): {', '.join(others) or 'none'}")
    emit()

    # --- run_v2 on every sidecar
    emit("=== run_v2 --family L --ranges s15_ranges.json, one call per sidecar ===")
    for p, name in zip(sidecars, names):
        out_txt = ROOT / f"results_s17_{name}.txt"
        if args.reuse and out_txt.with_suffix(".json").exists():
            emit(f"  reuse {out_txt.with_suffix('.json').name}")
            continue
        run_v2(p, out_txt)
    emit()

    # --- collect rows, CHARWIN via n5
    from scoreboard import run_v2 as R2  # noqa: E402  (n7 idiom: ROOT on sys.path, then package import)
    n5 = load_by_path("n5_signature_discrimination", ROOT / "n5_signature_discrimination.py")
    a2 = load_by_path("a2_position", ROOT / "a2_position.py")
    rows, checks, jsd_checks = {}, [], []
    emit("=== CHARWIN (n5_signature_discrimination.score) and JSD within-line permutation null "
         f"(a2_position.null, n={JSD_NULL_N}) on load_meta+subsample(25000) pages ===")
    for p, name in zip(sidecars, names):
        js = json.loads((ROOT / f"results_s17_{name}.json").read_text(encoding="utf-8"))
        row = js["row"]
        row["jsd_last_lg"] = (row.get("v1_full") or {}).get("jsd_last_lg")
        _, pages = R2.load_meta(p)
        pages = R2.subsample(pages, N_SAMPLE)
        lines = [ln for q in pages for ln in q["lines"]]
        # JSD null: same lines, same feature lambdas as score.py line_metrics (ws[0][0], ws[-1][-1])
        f_raw, l_raw = a2.stats(lines, lambda w: w[0])
        _, l_raw2 = a2.stats(lines, lambda w: w[-1])
        nl_first = a2.null(lines, lambda w: w[0], n=JSD_NULL_N)[:, 0]
        nl_last = a2.null(lines, lambda w: w[-1], n=JSD_NULL_N)[:, 1]
        row["jsd_first_null"] = float(nl_first.mean())
        row["jsd_first_null_sd"] = float(nl_first.std())
        row["jsd_last_null"] = float(nl_last.mean())
        row["jsd_last_null_sd"] = float(nl_last.std())
        row["jsd_first_exc"] = (row["jsd_first_fg"] - row["jsd_first_null"]) if row.get("jsd_first_fg") is not None else None
        row["jsd_last_exc"] = (row["jsd_last_lg"] - row["jsd_last_null"]) if row.get("jsd_last_lg") is not None else None
        same_f = row.get("jsd_first_fg") is not None and round(float(f_raw), 4) == row["jsd_first_fg"]
        same_l = row.get("jsd_last_lg") is not None and round(float(l_raw2), 4) == row["jsd_last_lg"]
        jsd_checks.append((name, same_f, same_l))
        s = n5.score(pages)
        row["CHARWIN"] = s["CHARWIN"]
        same_pos = row.get("x_position_entropy") is not None and abs(s["POSLOCK"] - row["x_position_entropy"]) < 1e-9
        same_mor = row.get("x_moran_I") is not None and abs(s["MORAN"] - row["x_moran_I"]) < 1e-9
        checks.append((name, same_pos, same_mor))
        emit(f"  {name:32} lines={len(lines):5d} tokens={s['tokens']:6d} CHARWIN={s['CHARWIN']:+.4f}  "
             f"jsd_first null={row['jsd_first_null']:.4f}±{row['jsd_first_null_sd']:.4f} "
             f"jsd_last null={row['jsd_last_null']:.4f}±{row['jsd_last_null_sd']:.4f}  "
             f"a2.stats==run_v2 jsd (first/last): {same_f}/{same_l}  "
             f"n5 POSLOCK==x_position_entropy: {same_pos}  n5 MORAN==x_moran_I: {same_mor}")
        rows[name] = row
    emit()

    # --- s2 prior
    s2 = parse_s2()
    emit(f"s2 Part 1 prior parsed from {S2.name} lines 5-16: {len(s2)} corpora "
         f"({', '.join(sorted(s2))}); sha256={sha256(S2)[:16] if S2.exists() else 'absent'}…")
    emit()

    # --- widths (optional)
    R = json.loads(RANGES.read_text(encoding="utf-8"))
    wm = R.get("within_manuscript") or {}

    def width(metric):
        w = wm.get(metric)
        if isinstance(w, dict):
            if "width" in w:
                return float(w["width"])
            if "lo" in w and "hi" in w:
                return float(w["hi"]) - float(w["lo"])
        return None

    # --- table
    emit("=== v2 metrics, native vs relined8 (25k-token cap; run_v2 rows + n5 CHARWIN) ===")
    emit("corpus                   | mode    | lines  toks  | " + " ".join(f"{c:>12}" for c in V2_COLS))
    emit("-" * (56 + 13 * len(V2_COLS)))
    for c in CORPORA:
        for mode, name in (("native", c), ("relined", c + RELINE)):
            r = rows[name]
            emit(f"{c:24} | {mode:7} | {r['lines']:5d} {r['tokens']:6d} | "
                 + " ".join(f"{fmt(r.get(k)):>12}" for k in V2_COLS))
    emit()
    emit("=== native minus relined8 per metric (flag >width where s15_ranges.json within_manuscript gives one) ===")
    emit("corpus                   | " + " ".join(f"{c:>12}" for c in V2_COLS))
    for c in CORPORA:
        a, b = rows[c], rows[c + RELINE]
        cells = []
        for k in V2_COLS:
            if a.get(k) is None or b.get(k) is None:
                cells.append(f"{'NA':>12}")
                continue
            d = a[k] - b[k]
            w = width(k)
            flag = "" if w is None else (">w" if abs(d) > w else "<=w")
            cells.append(f"{d:+.4f}{flag:>4}"[-12:].rjust(12))
        emit(f"{c:24} | " + " ".join(cells))
    emit(f"within_manuscript widths available for: {', '.join(k for k in V2_COLS if width(k) is not None) or 'none'}")
    emit()

    emit("=== s2 Part 1 prior (v1 estimator, score.py line_metrics, 25k cap, no 5% skip) beside v2 ===")
    emit("corpus                   | mode    | s2 lines toks  JSDf    JSDl    p_init  m_fin  | v2 jsd_first jsd_last p_init  m_fin")
    for c in ["voynich_ZL3b"] + CORPORA:
        for mode in ("native", "relined"):
            p = s2.get(c, {}).get(mode)
            s2s = (f"{p['lines']:5d} {p['toks']:6d}  {p['jsdf']:.4f}  {p['jsdl']:.4f}  {p['pinit']:6.2f}  {p['mfin']:6.2f}"
                   if p else "(not in s2)".ljust(44))
            r = rows.get(c if mode == "native" else c + RELINE)
            v2s = (f"{fmt(r.get('jsd_first_fg'))} {fmt(r.get('jsd_last_lg'))} {fmt(r.get('p_init_enrich'), 2):>6} "
                   f"{fmt(r.get('m_final_enrich'), 2):>6}" if r else "(v1 reference only)")
            emit(f"{c:24} | {mode:7} | {s2s} | {v2s}")
    emit()

    # --- descriptive lines
    nat = {c: rows[c].get("jsd_first_fg") for c in CORPORA}
    valid = {c: v for c, v in nat.items() if v is not None}
    if valid:
        top = max(valid, key=valid.get)
        emit(f"max native jsd_first_fg over the {len(valid)} real-line corpora on v2 = {valid[top]:.4f} ({top}); "
             f"{'< 0.10' if valid[top] < 0.10 else '>= 0.10'} (s2 Part 1 outcome-A threshold, re-read on v2; "
             f"Voynich s2 v1 native = {s2.get('voynich_ZL3b', {}).get('native', {}).get('jsdf', 'NA')})")
    emit(f"gibberish row on real lines: {rows['gib_realline_pooled']['lines']} volunteer lines, "
         f"{rows['gib_realline_pooled']['tokens']} tokens (gib_pooled was 8x20-wrapped, phase-1.md §4)")
    bad = [n for n, a, b in checks if not (a and b)]
    emit(f"n5-vs-run_v2 extras consistency: {'all equal' if not bad else 'MISMATCH on ' + ', '.join(bad)}")
    badj = [n for n, a, b in jsd_checks if not (a and b)]
    emit(f"a2_position.stats-vs-run_v2 raw JSD consistency (null estimator applies to the same lines): "
         f"{'all equal' if not badj else 'MISMATCH on ' + ', '.join(badj)}")
    emit("jsd_*_null = mean of 30 within-line shuffles (a2_position.null, Random(0..29)); jsd_*_exc = raw - null; "
         "null sd printed in the CHARWIN/JSD block above")
    errs = {n: r["errors"] for n, r in rows.items() if r.get("errors")}
    if errs:
        emit(f"run_v2 step errors: {json.dumps(errs)}")
    emit(f"done-when: results_s17.txt lists {len(CORPORA)} real-line corpora native and relined8 on v2 metrics, "
         f"gibberish row on real lines -> {'MET' if len(CORPORA) >= 4 else 'NOT MET'}")
    emit(f"run finished {clock()}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
