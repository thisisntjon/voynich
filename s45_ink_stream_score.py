#!/usr/bin/env python
"""s45: Ink-derived line and word boundaries from the Yale scans — the SCORING step (O-048).

PRE-REGISTRATION (frozen in s45_ink_stream_score.prereg.sha256 before the first scoring run; the
segmentation itself is a pipeline step, tools/segment_scans.py, whose parameters are logged in
runs/s45/segment_params.json and are not part of this stub).

  Inputs (read only):
    runs/s45/segment_summary.json   per-page line-count agreement; clean = |detected - ZL3b loci| <= 2
    runs/s45/ink_ZL3b.meta.json     ink-resegmented tokens (ZL3b glyph strings re-cut by the ink gaps)
    runs/s45/ink_lines_ZL3b.meta.json  ink-relined (ink line breaks, tokens unchanged)
    data/ZL3b-n.txt via scoreboard.metrics_new.voynich_pages('eva') (the run_v2 --voynich loader)
  Streams, all restricted to the clean page set (same ids, same order):
    S0 ZL3b as transliterated; S1 ink-resegmented; S2 ink-relined.  Sidecars via run_v2.load_meta.
    No 25k token cap: the streams are scored whole (types_25k is still the first 25,000 tokens).
  Estimators, loaded by path:
    line-initial first-glyph JSD excess = a2_position.stats(lines, w[0])[0] - mean of
      a2_position.null(lines, w[0], n=30)[:, 0], lines with >= 3 words (as s32_matched_verse.py);
    within-line word-length Moran I and its line-shuffle null = s21_moran_realline.py materialize /
      moran_for_pairs / line_shuffle_null (999 draws, seed 20261017) / summarize;
    cross_excess_eva, types_25k, h2 = scoreboard/run_v2.py score_one (ranges s15_ranges.json for IN/OUT).
  Fixed predictions (verbatim from the 22:29 commission):
    (P1) the line-initial excess on the ink-relined stream stays within the s15 width of the
         transliteration value (+0.173 ± 0.036) — "the line signatures are the scribe's lines";
    (P2) within-line Moran I on the ink-resegmented stream stays above the line-shuffle 99th
         percentile and within [0.109, 0.170];
    (P3) cross_excess on the ink-resegmented stream stays positive and within [0.148, 0.209];
    report types_25k/h2 of the ink stream beside the s30 convention rows (c-326: standard 6,572
    types; merge 7,426; split 4,525).
  Reading rule: all three hold → "line and word signatures are properties of the ink, not of the
    transcription conventions"; any fails → name which and by how much.
  Quality block: the per-page line-count agreement table and the overall token merge/split rate;
    if fewer than 150 pages segment cleanly (|Δ lines| <= 2), the result is PARTIAL and the pages
    used are listed.

Run: python -I s45_ink_stream_score.py [--run runs/s45]  -> results_s45.txt (the --run override exists
only for a mechanical dry run on a scratch copy before the stub is frozen; the filed result uses runs/s45).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SELF = ROOT / "s45_ink_stream_score.py"
STUB = ROOT / "s45_ink_stream_score.prereg.sha256"
OUT = ROOT / "results_s45.txt"
RUN = ROOT / "runs" / "s45"
RANGES = ROOT / "s15_ranges.json"

JSD_NULL_N = 30
MORAN_SEED = 20261017
P1_CENTER, P1_HALF = 0.173, 0.036
P2_LO, P2_HI = 0.109, 0.170
P3_LO, P3_HI = 0.148, 0.209
MIN_CLEAN = 150
S30_ROWS = "c-326: standard 6,572 types; merge 7,426; split 4,525"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        return subprocess.run(["date"], capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:  # noqa: BLE001
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now)"


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


FEAT = (lambda w: w[0])


def jsd_excess(a2, pages):
    lines = [ln for p in pages for ln in p["lines"]]
    raw, _ = a2.stats(lines, FEAT)
    nf = a2.null(lines, FEAT, n=JSD_NULL_N)[:, 0]
    return dict(raw=float(raw), null=float(nf.mean()), null_sd=float(nf.std()), exc=float(raw - nf.mean()),
                lines=len(lines), lines_ge3=sum(1 for ws in lines if len(ws) >= 3))


def moran(s21, pages):
    data = s21.materialize(pages)
    obs = s21.moran_for_pairs(data["x"], data["left"], data["right"])
    null = s21.summarize(s21.line_shuffle_null(data, MORAN_SEED), obs)
    return dict(I=obs, tokens=int(len(data["x"])), lines=data["n_lines"], pairs=int(len(data["left"])), **null)


def restrict(pages, ids):
    order = {pid: k for k, pid in enumerate(ids)}
    keep = [p for p in pages if p["id"] in order]
    keep.sort(key=lambda p: order[p["id"]])
    return keep


def ink_word_ratio(run_dir, pid):
    """ink tokens / ZL3b words over the ink-aligned P-lines of the page (from runs/s45/pages/<id>.json)."""
    pj = run_dir / "pages" / f"{pid}.json"
    if not pj.exists():
        return None
    al = json.loads(pj.read_text(encoding="utf-8")).get("alignment", [])
    ni = sum(a.get("n_ink", 0) for a in al if a.get("det")); nw = sum(a.get("n_words", 0) for a in al if a.get("det"))
    return ni / nw if nw else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, default=RUN)
    args = ap.parse_args()
    run_dir = args.run
    out_path = OUT if run_dir == RUN else run_dir / "results_dryrun.txt"
    out = []

    def emit(s=""):
        print(s, flush=True); out.append(s)

    def flush():
        OUT.write_text("\n".join(out) + "\n", encoding="utf-8")

    emit(f"s45_ink_stream_score.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit(f"run: {clock()}")
    emit("estimators by path: a2_position.stats/null (feat w[0], n=30; lines >= 3 words), s21_moran_realline "
         f"(999 draws, seed {MORAN_SEED}), scoreboard/run_v2.score_one (ranges s15_ranges.json)")
    a2 = load_by_path("a2_position", ROOT / "a2_position.py")
    s21 = load_by_path("s21_moran_realline", ROOT / "s21_moran_realline.py")
    rv = load_by_path("run_v2", ROOT / "scoreboard" / "run_v2.py")
    M = rv.M

    summ = json.loads((run_dir / "segment_summary.json").read_text(encoding="utf-8"))
    recs = summ["pages"]
    clean_ids = [r["id"] for r in recs if r["clean"]]
    emit(f"segmentation: {run_dir / 'segment_summary.json'}; pages segmented={len(recs)} clean(|d|<=2)={len(clean_ids)} "
         f"unmatched canvases={len(summ['unmatched_canvases'])} ZL3b pages without canvas={len(summ['zl_pages_without_canvas'])}")
    partial = len(clean_ids) < MIN_CLEAN
    if partial:
        emit(f"PARTIAL: only {len(clean_ids)} pages segment cleanly (< {MIN_CLEAN}); pages used: {' '.join(clean_ids)}")
    emit()

    # ---- quality block
    emit("=== quality block: per-page line-count agreement (det = ink lines after merge/filter; loci = all ZL3b loci "
         "on the page; P = paragraph loci; flag if |d| > 2) ===")
    emit(f"{'page':8} {'det':>4} {'loci':>4} {'P':>4} {'d':>4} {'flag':4} {'thr_px':>6} {'src':4} {'merge':>5} {'split':>5} "
         f"{'1to1/P':>8} {'ink/word':>8} {'conf':>5}")
    T = dict(merge=0, split=0, lines_P=0, lines_1to1=0, lines_aligned=0, drop_ink=0)
    n_words_aligned = 0
    for r in recs:
        t = r["totals"]
        for k in T:
            T[k] += t.get(k, 0)
        ratio = ink_word_ratio(run_dir, r["id"])
        emit(f"{r['id']:8} {r['n_detected']:4d} {r['n_loci']:4d} {r['n_P']:4d} {r['delta']:+4d} {'ok' if r['clean'] else 'FLAG':4} "
             f"{r['threshold']['thr']:6.1f} {r['threshold']['source'][:4]:4} {t['merge']:5d} {t['split']:5d} "
             f"{t['lines_1to1']:3d}/{t['lines_P']:3d}  {'' if ratio is None else f'{ratio:8.2f}'} {1 - r['line_align_cost']:5.2f}")
    deltas = np.array([r["delta"] for r in recs])
    emit(f"line agreement: pages={len(recs)} |d|<=2: {int((np.abs(deltas) <= 2).sum())}  |d|<=1: {int((np.abs(deltas) <= 1).sum())}  "
         f"d==0: {int((deltas == 0).sum())}  median d={float(np.median(deltas)):+.1f}  mean |d|={float(np.abs(deltas).mean()):.2f}")
    emit()

    # ---- streams on the clean pages
    name_s1, s1 = rv.load_meta(run_dir / "ink_ZL3b.meta.json")
    name_s2, s2 = rv.load_meta(run_dir / "ink_lines_ZL3b.meta.json")
    s0 = M.voynich_pages("eva")
    S = [("S0 ZL3b transliterated", restrict(s0, clean_ids)),
         ("S1 ink-resegmented", restrict(s1, clean_ids)),
         ("S2 ink-relined", restrict(s2, clean_ids))]
    tok0 = len(M.flat_tokens(S[0][1])); tok1 = len(M.flat_tokens(S[1][1]))
    merged_clean = sum(r["totals"]["merge"] for r in recs if r["clean"])
    split_clean = sum(r["totals"]["split"] for r in recs if r["clean"])
    emit("=== token merge/split (ZL3b tokens on ink-aligned P-lines; all segmented pages / clean pages) ===")
    emit(f"all pages : merges={T['merge']} splits={T['split']} on P-lines={T['lines_P']} (aligned {T['lines_aligned']}, "
         f"1:1 line matches {T['lines_1to1']}); ink tokens without glyphs dropped={T['drop_ink']}")
    emit(f"clean pages: merges={merged_clean} splits={split_clean}; S0 tokens={tok0} S1 tokens={tok1} "
         f"(merge rate {merged_clean / max(tok0, 1):.3f}, split rate {split_clean / max(tok0, 1):.3f} per S0 token; "
         f"S1/S0 = {tok1 / max(tok0, 1):.3f})")
    emit()

    rows = {}
    for label, pages in S:
        emit(f"--- {label}: pages={len(pages)} lines={sum(len(p['lines']) for p in pages)} tokens={len(M.flat_tokens(pages))}")
        j = jsd_excess(a2, pages)
        m = moran(s21, pages)
        row = rv.score_one(label, pages, lambda s: None)
        rows[label] = dict(jsd=j, moran=m, row=row)
        emit(f"    line-initial JSD(first,mid) raw={j['raw']:.4f} null={j['null']:.4f}±{j['null_sd']:.4f} excess={j['exc']:+.4f} "
             f"(lines>=3: {j['lines_ge3']}/{j['lines']})")
        emit(f"    within-line Moran I={m['I']:.4f} null median={m['median']:.4f} q99={m['q99']:.4f} p={m['p']:.3f} "
             f"(tokens {m['tokens']}, pairs {m['pairs']})")
        emit(f"    run_v2: cross_excess_eva={rv.fmt(row.get('cross_excess_eva'))} types={row['types']} types_25k={row['types_25k']} "
             f"h2={rv.fmt(row.get('h2'))} sd_len={rv.fmt(row.get('sd_len'))} jsd_first_fg={rv.fmt(row.get('jsd_first_fg'))} "
             f"errors={row['errors'] or '-'}")
        flush()
    emit()

    # ---- predictions
    emit("=== fixed predictions ===")
    j2 = rows["S2 ink-relined"]["jsd"]["exc"]
    p1 = (P1_CENTER - P1_HALF) <= j2 <= (P1_CENTER + P1_HALF)
    emit(f"P1 line-initial excess, ink-relined: {j2:+.4f} vs [{P1_CENTER - P1_HALF:+.3f}, {P1_CENTER + P1_HALF:+.3f}] "
         f"(transliteration on the same pages {rows['S0 ZL3b transliterated']['jsd']['exc']:+.4f}) -> {'HOLDS' if p1 else 'FAILS'}"
         + ("" if p1 else f" by {min(abs(j2 - (P1_CENTER - P1_HALF)), abs(j2 - (P1_CENTER + P1_HALF))):.4f}"))
    m1 = rows["S1 ink-resegmented"]["moran"]
    p2a = m1["I"] > m1["q99"]; p2b = P2_LO <= m1["I"] <= P2_HI
    emit(f"P2 within-line Moran I, ink-resegmented: {m1['I']:.4f} > q99 {m1['q99']:.4f}: {p2a}; in [{P2_LO}, {P2_HI}]: {p2b} "
         f"(transliteration on the same pages {rows['S0 ZL3b transliterated']['moran']['I']:.4f}) -> {'HOLDS' if p2a and p2b else 'FAILS'}"
         + ("" if p2b else f" by {min(abs(m1['I'] - P2_LO), abs(m1['I'] - P2_HI)):.4f} outside the band"))
    c1 = rows["S1 ink-resegmented"]["row"].get("cross_excess_eva")
    p3 = c1 is not None and c1 > 0 and P3_LO <= c1 <= P3_HI
    emit(f"P3 cross_excess_eva, ink-resegmented: {rv.fmt(c1)} positive and in [{P3_LO}, {P3_HI}] "
         f"(transliteration on the same pages {rv.fmt(rows['S0 ZL3b transliterated']['row'].get('cross_excess_eva'))}) -> {'HOLDS' if p3 else 'FAILS'}"
         + ("" if p3 or c1 is None else f" by {min(abs(c1 - P3_LO), abs(c1 - P3_HI)):.4f}"))
    r1 = rows["S1 ink-resegmented"]["row"]; r0 = rows["S0 ZL3b transliterated"]["row"]
    emit(f"types_25k/h2: ink-resegmented types_25k={r1['types_25k']} (types {r1['types']}) h2={rv.fmt(r1.get('h2'))}; "
         f"transliteration same pages types_25k={r0['types_25k']} (types {r0['types']}) h2={rv.fmt(r0.get('h2'))}; "
         f"s30 convention rows {S30_ROWS}")
    if RANGES.exists():
        rg = json.loads(RANGES.read_text(encoding="utf-8"))["ranges"]
        for k in ("cross_excess_eva", "h2", "jsd_first_fg", "x_moran_I"):
            if k in rg:
                emit(f"  s15 IN/OUT {k}: " + "; ".join(
                    f"{lab[:2]}={rv.fmt(rows[lab]['row'].get(k))} L:{rv.in_out(rows[lab]['row'].get(k), rg[k].get('L'))}"
                    for lab, _ in S))
    emit()
    held = [p1, p2a and p2b, p3]
    names = ["P1", "P2", "P3"]
    if all(held):
        reading = "line and word signatures are properties of the ink, not of the transcription conventions"
    else:
        reading = "fails: " + ", ".join(n for n, h in zip(names, held) if not h)
    emit(f"READING ({'PARTIAL, ' if partial else ''}{len(clean_ids)} clean pages): {reading}")
    emit(f"end: {clock()}")
    flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
