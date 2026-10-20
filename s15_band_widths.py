"""s15: within-manuscript widths for every v2 metric (phase-1.md s15).

200 random 41-page subsets of ZL3b (seeds 1000..1199, s2 Part 3B / l1 convention:
`random.Random(seed).sample(page_ids, 41)` over the 207 paragraph pages in manuscript order,
subset kept in manuscript order), each scored with scoreboard/run_v2.py's `score_one`
(edge-null nrep at run_v2's / score.py's default, 20), plus the g1 held-out split
(Random(20261017), 41 test pages) as an extra labelled row, plus one full-size row each for
ZL3b, RF1b and IT2a from data/translit/*.meta.json (no token cap, as n7 did).

Writes: results_s15.txt, s15_ranges.json (project root) and a per-split scratch log
(JSON lines, appended as each split finishes; re-running resumes from it).
Run: python -I s15_band_widths.py [--log <scratch.jsonl>] [--smoke N]
     --smoke N scores N splits into the scratch log only and writes no project file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from scoreboard import run_v2 as R2  # noqa: E402
from scoreboard import metrics_new as M  # noqa: E402

SEEDS = list(range(1000, 1200))
G1_SEED = 20261017
N_SUB = 41
KEYS = R2.V1_KEYS + R2.NEW_NUMERIC
N7 = ROOT / "n7_gibberish_ranges.json"
S2 = ROOT / "results_s2_u123_controls.txt"
OUT_TXT = ROOT / "results_s15.txt"
OUT_JSON = ROOT / "s15_ranges.json"
TRL = ROOT / "data" / "translit"
FULL_ROWS = [("ZL3b", "ZL3b_eva.meta.json"), ("RF1b", "RF1b.meta.json"), ("IT2a", "IT2a.meta.json")]
X_ARTEFACT = ["x_moran_I", "lex_beta", "lex_rate_late_early", "lex_edit1_excess", "slot_occupancy_pc",
              "slot_table_likeness", "slot_core_crowding", "bake_char3_minus_unigram"]
X_REASON = "X range is a 10k-token pooled jackknife sliver (n7; O-046)"
TOL = {"h2": 0.01, "sd_len": 0.01, "jsd_first_fg": 0.01, "cross_excess_eva": 0.01, "redup_pct": 0.01,
       "p_init_enrich": 1.0, "m_final_enrich": 1.0}
MAX_FIRST5_SEC = 15.0


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now_str():
    try:
        return subprocess.run(["date"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        from datetime import datetime
        return datetime.now().strftime("%a %b %d %H:%M:%S %Y") + " (datetime fallback)"


def subset_ids(page_ids, seed, g1=False):
    rng = random.Random(seed)
    if g1:
        pick = set(rng.sample(page_ids, N_SUB))
    else:
        pick = set(rng.sample(page_ids, N_SUB))
    return [p for p in page_ids if p in pick]


def score_pages(name, pages):
    row = R2.score_one(name, pages, lambda s: None)
    return {k: R2.fin(row.get(k)) for k in KEYS} | {
        "tokens": row["tokens"], "types": row["types"], "pages": row["pages"], "lines": row["lines"],
        "bake_winner": row.get("bake_winner"), "errors": row["errors"]}


def read_log(path):
    done = {}
    if path.exists():
        for ln in path.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                d = json.loads(ln)
                done[d["label"]] = d
    return done


def append_log(path, rec):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def stats(vals):
    v = np.array([x for x in vals if x is not None], dtype=float)
    if len(v) == 0:
        return dict(median=None, lo95=None, hi95=None, min=None, max=None, n_splits=0)
    q = np.percentile(v, [2.5, 50, 97.5])
    return dict(median=float(q[1]), lo95=float(q[0]), hi95=float(q[2]), min=float(v.min()),
                max=float(v.max()), n_splits=int(len(v)))


def parse_s2_3b():
    """Part 3B lines: '  h2 | median= x | 95%_CI=[ a, b] | min..max=[ c, d]'."""
    out = {}
    txt = S2.read_text(encoding="utf-8").splitlines()
    on = False
    for ln in txt:
        if ln.startswith("=== PART 3B"):
            on = True
            continue
        if on:
            if ln.startswith("===") or (not ln.strip() and out):
                break
            if "median=" in ln:
                k = ln.split("|")[0].strip()
                med = float(ln.split("median=")[1].split("|")[0])
                ci = ln.split("95%_CI=[")[1].split("]")[0].split(",")
                mm = ln.split("min..max=[")[1].split("]")[0].split(",")
                out[k] = dict(median=med, lo95=float(ci[0]), hi95=float(ci[1]), min=float(mm[0]), max=float(mm[1]))
    return out


def f(v, d=4):
    return "nan" if v is None else f"{v:.{d}f}"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", type=Path, required=True, help="scratch JSON-lines log (appended per split)")
    ap.add_argument("--smoke", type=int, default=0, help="score N splits into the log only; write no project file")
    args = ap.parse_args(argv)
    t_start = time.time()
    run_time = now_str()
    script_sha = sha256(__file__)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    done = read_log(args.log)
    print(f"s15 start {run_time}; script sha256 {script_sha}; log {args.log}; {len(done)} rows already logged", flush=True)

    pages = M.voynich_pages("eva")
    page_ids = [p["id"] for p in pages]
    by = {p["id"]: p for p in pages}
    print(f"ZL3b via vparse: {len(pages)} pages, {len(M.flat_tokens(pages))} tokens", flush=True)

    jobs = [(f"g1_{G1_SEED}", G1_SEED, True)] + [(f"seed_{s}", s, False) for s in SEEDS]
    if args.smoke:
        jobs = jobs[1:1 + args.smoke]
    elapsed = []
    for label, seed, g1 in jobs:
        if label in done:
            continue
        ids = subset_ids(page_ids, seed, g1)
        t = time.time()
        r = score_pages(label, [by[i] for i in ids])
        dt = time.time() - t
        elapsed.append(dt)
        rec = dict(label=label, seed=seed, kind="g1_heldout" if g1 else "split", elapsed_s=round(dt, 2),
                   page_ids=ids, **r)
        append_log(args.log, rec)
        done[label] = rec
        print(f"  {label}: {r['tokens']} tok, {dt:.1f}s, h2={f(r['h2'])} jsdf={f(r['jsd_first_fg'])} "
              f"cross={f(r['cross_excess_eva'])} errors={list(r['errors']) or '-'}", flush=True)
        if len(elapsed) == 5 and not g1:
            avg = sum(elapsed) / 5
            if avg > MAX_FIRST5_SEC:
                print(f"STOP: first 5 scored splits average {avg:.1f}s > {MAX_FIRST5_SEC}s", flush=True)
                return 2
    if args.smoke:
        print(f"smoke done: {len(elapsed)} splits, mean {sum(elapsed)/max(1,len(elapsed)):.1f}s", flush=True)
        return 0

    # full-size rows (one corpus in memory at a time)
    full = {}
    for label, fn in FULL_ROWS:
        key = f"full_{label}"
        if key in done:
            full[label] = done[key]
            continue
        _, pg = R2.load_meta(TRL / fn)
        t = time.time()
        r = score_pages(f"voynich_{label}", pg)
        dt = time.time() - t
        rec = dict(label=key, seed=None, kind="full", elapsed_s=round(dt, 2), source=str(TRL / fn), **r)
        append_log(args.log, rec)
        done[key] = full[label] = rec
        print(f"  {key}: {r['tokens']} tok, {dt:.1f}s", flush=True)
        del pg

    splits = [done[f"seed_{s}"] for s in SEEDS]
    g1row = done[f"g1_{G1_SEED}"]
    wm = {k: stats([d[k] for d in splits]) for k in KEYS}
    tok_st = stats([d["tokens"] for d in splits])
    el = [d["elapsed_s"] for d in splits]

    # ---- results_s15.txt ----
    L = []
    L.append("S15: within-manuscript widths for every v2 metric (200 random 41-page splits of ZL3b, run_v2.score_one)")
    L.append(f"run: {run_time}")
    L.append(f"script: s15_band_widths.py sha256={script_sha}")
    L.append(f"seeds: {SEEDS[0]}..{SEEDS[-1]} (n={len(SEEDS)}; random.Random(seed).sample(page_ids, 41), manuscript order kept); "
             f"extra row g1 held-out Random({G1_SEED})")
    L.append(f"scorer: scoreboard/run_v2.py score_one (sha256[:16] {sha256(ROOT/'scoreboard'/'run_v2.py')[:16]}; "
             f"score.py {sha256(ROOT/'scoreboard'/'score.py')[:16]}; metrics_new.py {sha256(ROOT/'scoreboard'/'metrics_new.py')[:16]}); "
             f"edge-null nrep = score.py default (20); lexicon n_shuffles={R2.N_SHUFFLES}")
    L.append(f"source: ZL3b EVA paragraphs via vparse ({len(pages)} pages, {len(M.flat_tokens(pages))} tokens); "
             f"full rows: data/translit/{{ZL3b_eva,RF1b,IT2a}}.meta.json, no token cap")
    L.append(f"subset tokens: median {tok_st['median']:.0f}, range {tok_st['min']:.0f}..{tok_st['max']:.0f}; "
             f"elapsed per split: mean {np.mean(el):.1f}s, min {min(el):.1f}s, max {max(el):.1f}s, total {sum(el)/60:.1f} min")
    errs = {}
    for d in splits:
        for k in d["errors"]:
            errs[k] = errs.get(k, 0) + 1
    L.append(f"score_one step errors over the 200 splits: {errs or 'none'}; "
             f"metrics with NaN in some split: " + (", ".join(f"{k}({200 - wm[k]['n_splits']})" for k in KEYS if wm[k]['n_splits'] < 200) or "none"))
    L.append("")
    L.append("=== within-manuscript widths (200 splits) and full-size rows ===")
    hdr = f"{'metric':28} {'median':>9} {'2.5%':>9} {'97.5%':>9} {'min':>9} {'max':>9} {'n':>4} | {'g1_41':>9} | {'ZL3b':>9} {'RF1b':>9} {'IT2a':>9}"
    L.append(hdr)
    for k in KEYS:
        s = wm[k]
        L.append(f"{k:28} {f(s['median']):>9} {f(s['lo95']):>9} {f(s['hi95']):>9} {f(s['min']):>9} {f(s['max']):>9} {s['n_splits']:>4} | "
                 f"{f(g1row[k]):>9} | {f(full['ZL3b'][k]):>9} {f(full['RF1b'][k]):>9} {f(full['IT2a'][k]):>9}")
    L.append(f"{'tokens':28} {tok_st['median']:>9.0f} {tok_st['lo95']:>9.0f} {tok_st['hi95']:>9.0f} {tok_st['min']:>9.0f} {tok_st['max']:>9.0f} {tok_st['n_splits']:>4} | "
             f"{g1row['tokens']:>9} | {full['ZL3b']['tokens']:>9} {full['RF1b']['tokens']:>9} {full['IT2a']['tokens']:>9}")
    L.append("(x_hapax_10k is NaN below 10k tokens; types_25k on a 41-page subset is just the type count; "
             "bake-off folds are leave-one-quire-out.)")
    L.append("")
    L.append("=== full-size rows (data/translit sidecars, whole) ===")
    for lab in ("ZL3b", "RF1b", "IT2a"):
        d = full[lab]
        L.append(f"  {lab:6} pages={d['pages']} lines={d['lines']} tokens={d['tokens']} types={d['types']} "
                 f"bake_winner={d['bake_winner']} elapsed={d['elapsed_s']}s errors={d['errors'] or '-'}")
    L.append("")
    L.append("=== reconciliation with results_s2_u123_controls.txt Part 3B (v1 estimator, same 200 splits) ===")
    s2 = parse_s2_3b()
    L.append(f"{'metric':18} {'s15 med':>9} {'s2 med':>9} {'d_med':>8} | {'s15 lo':>8} {'s2 lo':>8} {'d_lo':>8} | {'s15 hi':>8} {'s2 hi':>8} {'d_hi':>8} | tol    verdict")
    all_pass = True
    n_pass = 0
    for k in R2.V1_KEYS:
        a, b = wm[k], s2.get(k)
        if b is None:
            L.append(f"{k:18} s2 row missing -> FAIL")
            all_pass = False
            continue
        dm, dl, dh = a["median"] - b["median"], a["lo95"] - b["lo95"], a["hi95"] - b["hi95"]
        ok = abs(dm) <= TOL[k]
        ci_note = "" if (abs(dl) <= TOL[k] and abs(dh) <= TOL[k]) else "  (CI differs beyond tol)"
        all_pass &= ok
        n_pass += ok
        L.append(f"{k:18} {a['median']:>9.4f} {b['median']:>9.4f} {dm:>+8.4f} | {a['lo95']:>8.4f} {b['lo95']:>8.4f} {dl:>+8.4f} | "
                 f"{a['hi95']:>8.4f} {b['hi95']:>8.4f} {dh:>+8.4f} | {TOL[k]:<5} {'PASS' if ok else 'FAIL'}{ci_note}")
    L.append(f"reconciliation: {'PASS' if all_pass else 'FAIL'} ({n_pass}/7 medians within tolerance; "
             "tolerance 0.01 for h2, sd_len, jsd, cross, redup; 1.0x for the enrichments; CI differences reported, not gated)")
    L.append("")
    L.append(f"total wall time {(time.time() - t_start)/60:.1f} min this invocation; per-split log: {args.log}")
    OUT_TXT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L), flush=True)

    # ---- s15_ranges.json ----
    n7 = json.loads(N7.read_text(encoding="utf-8"))
    nw = list(n7["no_weight"])
    reasons = {}
    for k in X_ARTEFACT:
        if k not in nw:
            nw.append(k)
        reasons[k] = X_REASON
    out = {
        "run": f"s15 {run_time}",
        "seed": n7.get("seed"), "n_sample": n7.get("n_sample"), "n_shuffles": n7.get("n_shuffles"),
        "extend": n7.get("extend"),
        "ranges": n7["ranges"], "tight": n7["tight"], "no_weight": nw, "no_weight_reasons": reasons,
        "x_family": n7["x_family"],
        "within_manuscript": {k: wm[k] for k in KEYS},
        "within_manuscript_note": "ZL3b EVA via vparse; 200 random 41-page subsets, seeds 1000..1199, "
                                   "random.Random(seed).sample(page_ids, 41); run_v2.score_one, edge-null nrep 20; "
                                   "lo95/hi95 = 2.5/97.5 percentiles. run_v2 ignores this key; s18 reads it.",
        "within_manuscript_tokens": tok_st,
        "g1_heldout_41": {k: g1row[k] for k in KEYS} | {"tokens": g1row["tokens"], "seed": G1_SEED},
        "full_rows": {lab: {k: full[lab][k] for k in KEYS} | {"tokens": full[lab]["tokens"], "source": full[lab]["source"]}
                      for lab in full},
        "provenance": {
            "run_time": run_time,
            "script": "s15_band_widths.py", "script_sha256": script_sha,
            "ranges_source": str(N7.name), "ranges_source_sha256": sha256(N7),
            "ranges_source_run": n7.get("run"), "n7": n7.get("n7"),
            "scorer": {p: sha256(ROOT / "scoreboard" / p) for p in ("run_v2.py", "score.py", "metrics_new.py")},
            "s2_reference": str(S2.name), "s2_reference_sha256": sha256(S2),
            "reconciliation_pass": bool(all_pass),
            "source_files": ["data/ZL3b-n.txt (via vparse)"] + [f"data/translit/{fn}" for _, fn in FULL_ROWS],
        },
    }
    OUT_JSON.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"wrote {OUT_TXT} and {OUT_JSON}", flush=True)
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
