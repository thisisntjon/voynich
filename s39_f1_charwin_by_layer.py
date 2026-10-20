"""s39 — F1 (held-out word-order residual) and CHARWIN by layer: prefix-only, core-only, suffix-only token streams.

PRE-REGISTERED QUESTION (verbatim; frozen in s39_f1_charwin_by_layer.prereg.sha256 before the run):
"Does the held-out word-order residual F1 (+0.046 [+0.036, +0.056] on ZL3b, results_n6.txt) and the character-model
win CHARWIN (+0.094, results_n5.txt) live in the affix layer (prefix / suffix) or in the core layer of the word?"

Method (fixed before the run)
  Data: n1_habit_table.load (by path) for ZL3b_eva, RF1b, IT2a (page -> records with words, hand, illus, quire, lang).
  Segmenter: scoreboard/metrics_new.SlotSegmenter fitted on the tokens of the 166 TRAINING pages = all pages minus
    g1_edge_joint.split_names(by)[1] (the g1_heldout_41 split, random.Random(20261017)), then applied to every token
    of every page (the held-out pages are segmented with the training inventory).  Inventory printed per
    transliteration (prefix and suffix candidate lists, number of cores).
  Streams (same page / line structure as the full text):
    full        : the tokens as loaded;
    prefix-only : token -> its prefix slot; empty slot -> the token "∅" (KEEP variant) or removed (DROP variant);
    core-only   : token -> its core (never empty by construction of SlotSegmenter);
    suffix-only : token -> its suffix slot; empty -> "∅" (KEEP) or removed (DROP).
    In DROP variants a line that becomes empty is removed; pages with no lines left are removed.
  F1: n1_habit_table.residual(by_stream, "quires") exactly as n4_habit7k.py:336-364 calls it (quire split, TOPN=300
    mapper, within-line-shuffle baseline, 1000-draw page bootstrap over test pages, [2.5 %, 97.5 %] interval).
  CHARWIN: n5_signature_discrimination.score(pages) (loaded by path): unigram-GT-renorm bits/token minus char3-WB
    bits/token on the m3.page_split(seed 20261017) held-out pages (one fold); positive = character model wins.
  Moran I of each stream's slot lengths (cross-check of s33): s21 within-line lag-1 Moran I on x = slot length
    (KEEP variant: empty slot = length 0; DROP variant: only non-empty slots), line-shuffle null 999 draws
    (np.random.default_rng(20261017)), median, q99, one-sided p.
  Checks: full-text F1 and CHARWIN on ZL3b reproduce results_n6 / n5 (+0.046 and +0.094) within 0.005.
  Predictions (fixed), decided on ZL3b with the KEEP variant; DROP variant and RF1b / IT2a printed beside:
    (i)  "F1 in the affix layer": prefix-only or suffix-only F1 interval excludes zero (lower bound > 0) AND the
         core-only interval includes zero;
    (ii) "F1 in the core layer": core-only interval excludes zero AND both prefix-only and suffix-only include zero;
    otherwise "F1 in both / neither layer" (which intervals exclude zero is listed).
    CHARWIN has no interval from n5.score; its sign and value per stream are reported, and the layer with the
    larger positive CHARWIN is named (no pass/fail).
  Margins printed: every interval's lower bound (distance from zero) and the value relative to the full-text value.

Run:    python -I s39_f1_charwin_by_layer.py
Writes: results_s39.txt only.
"""
from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
import time
from collections import OrderedDict
from datetime import datetime
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

OUT = ROOT / "results_s39.txt"
STUB = ROOT / "s39_f1_charwin_by_layer.prereg.sha256"
SELF = ROOT / "s39_f1_charwin_by_layer.py"
TRANSLITS = {"ZL3b": "ZL3b_eva", "RF1b": "RF1b", "IT2a": "IT2a"}
SEED = 20261017
N_DRAWS = 999
EMPTY = "∅"
log: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


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


def load_by_path(modname, path):
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


def stream_by(by, seg, slot, drop):
    """slot: 0 prefix, 1 core, 2 suffix, None full.  Returns (by_stream, lengths_by_line)."""
    out = OrderedDict()
    for page, recs in by.items():
        nr = []
        for r in recs:
            if slot is None:
                ws = list(r["words"]); ls = [len(w) for w in ws]
            else:
                parts = [seg.segment(w)[slot] for w in r["words"]]
                if drop:
                    ws = [p for p in parts if p]; ls = [len(p) for p in ws]
                else:
                    ws = [p if p else EMPTY for p in parts]; ls = [len(p) for p in parts]
            if ws:
                nr.append(dict(r, words=ws, _lens=ls))
        if nr:
            out[page] = nr
    return out


def by_to_pages(by):
    return [dict(id=p, section=recs[0]["illus"], hand=recs[0]["hand"], quire=recs[0]["quire"], lang=recs[0]["lang"],
                 lines=[r["words"] for r in recs]) for p, recs in by.items()]


def moran(by_stream):
    lengths, lid, left, right = [], [], [], []
    nl = 0
    for recs in by_stream.values():
        for r in recs:
            x = r["_lens"]
            if not x:
                continue
            s = len(lengths)
            lengths.extend(x); lid.extend([nl] * len(x))
            if len(x) > 1:
                idx = np.arange(s, s + len(x)); left.append(idx[:-1]); right.append(idx[1:])
            nl += 1
    x = np.asarray(lengths, dtype=float); lid = np.asarray(lid); left = np.concatenate(left); right = np.concatenate(right)

    def I(v):
        z = v - v.mean()
        d = np.dot(z, z)
        return float(len(v) / len(left) * np.dot(z[left], z[right]) / d) if d > 0 else float("nan")
    obs = I(x)
    rng = np.random.default_rng(SEED)
    out = np.empty(N_DRAWS)
    for d in range(N_DRAWS):
        perm = np.lexsort((rng.random(len(x)), lid))
        out[d] = I(x[perm])
    return dict(I=obs, median=float(np.median(out)), q99=float(np.quantile(out, 0.99)),
                p=float((1 + int(np.count_nonzero(out >= obs))) / (N_DRAWS + 1)), tokens=len(x), pairs=len(left))


def main() -> int:
    t0 = time.time()
    emit("S39: F1 held-out word-order residual and CHARWIN by layer (prefix-only / core-only / suffix-only streams), 3 transliterations")
    emit(f"run started {clock()}")
    emit(f"s39_f1_charwin_by_layer.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit("F1 = n1_habit_table.residual(by, 'quires') (as n4_habit7k.py:336-364); CHARWIN = n5_signature_discrimination.score(pages)['CHARWIN']; "
         "SlotSegmenter fitted on the 166 training pages (g1_edge_joint.split_names, Random(20261017)); Moran = s21 within-line lag-1 on slot lengths, 999-draw line-shuffle null")
    emit("predictions: (i) affix layer = prefix-only or suffix-only F1 interval excludes zero and core-only includes zero; (ii) core layer = the reverse (ZL3b, KEEP-∅ variant decides)")
    emit()
    N = load_by_path("n1_habit_table_s39", ROOT / "n1_habit_table.py")
    g1 = load_by_path("g1_edge_joint_s39", ROOT / "g1_edge_joint.py")
    M = load_by_path("metrics_new_s39", ROOT / "scoreboard" / "metrics_new.py")
    n5 = load_by_path("n5_signature_discrimination_s39", ROOT / "n5_signature_discrimination.py")
    results = {}
    for T, meta in TRANSLITS.items():
        by = N.load(meta)
        train, held = g1.split_names(by)
        toks_tr = [w for p in train for r in by[p] for w in r["words"]]
        seg = M.SlotSegmenter(toks_tr)
        all_toks = [w for recs in by.values() for r in recs for w in r["words"]]
        segs = {w: seg.segment(w) for w in set(all_toks)}
        n_pre = len({s[0] for s in segs.values()}); n_core = len({s[1] for s in segs.values()}); n_suf = len({s[2] for s in segs.values()})
        emp_p = sum(1 for w in all_toks if not segs[w][0]) / len(all_toks); emp_s = sum(1 for w in all_toks if not segs[w][2]) / len(all_toks)
        emit(f"=== {T}: {len(by)} pages, {len(all_toks)} tokens; training pages {len(train)} ({len(toks_tr)} tokens), held-out {len(held)} ===")
        emit(f"  SlotSegmenter (166-page fit): {len(seg.prefixes)} prefix candidates {sorted(seg.prefixes)}; {len(seg.suffixes)} suffix candidates {sorted(seg.suffixes)}; "
             f"applied everywhere -> {n_pre} prefix classes (incl. empty), {n_core} cores, {n_suf} suffix classes (incl. empty); empty prefix {100 * emp_p:.1f} % of tokens, empty suffix {100 * emp_s:.1f} %")
        emit(f"  {'stream':22} | {'tokens':>6} {'types':>5} | {'F1 residual':>12} {'[2.5, 97.5]':>20} {'lo-0':>7} | {'CHARWIN':>8} | {'Moran I':>8} {'null med':>8} {'q99':>7} {'p':>6}")
        rows = {}
        variants = [("full", None, False), ("prefix-only (keep ∅)", 0, False), ("core-only", 1, False), ("suffix-only (keep ∅)", 2, False),
                    ("prefix-only (drop ∅)", 0, True), ("suffix-only (drop ∅)", 2, True)]
        for name, slot, drop in variants:
            bs = stream_by(by, seg, slot, drop)
            f1v, f1ci = N.residual(bs, "quires")
            sc = n5.score(by_to_pages(bs))
            mo = moran(bs)
            ntok = sum(len(r["words"]) for recs in bs.values() for r in recs)
            ntyp = len({w for recs in bs.values() for r in recs for w in r["words"]})
            rows[name] = dict(f1=f1v, lo=f1ci[0], hi=f1ci[1], cw=sc["CHARWIN"], mo=mo, tokens=ntok, types=ntyp)
            emit(f"  {name:22} | {ntok:6d} {ntyp:5d} | {f1v:+12.4f} [{f1ci[0]:+.4f}, {f1ci[1]:+.4f}] {f1ci[0]:+7.4f} | {sc['CHARWIN']:+8.4f} | "
                 f"{mo['I']:+8.4f} {mo['median']:+8.4f} {mo['q99']:+7.4f} {mo['p']:6.3f}")
            flush()
        if T == "ZL3b":
            f = rows["full"]
            emit(f"  check: full F1 {f['f1']:+.4f} vs results_n6 +0.0461 ({'OK' if abs(f['f1'] - 0.0461) <= 0.005 else 'MISMATCH'}); "
                 f"full CHARWIN {f['cw']:+.4f} vs results_n5 +0.094 ({'OK' if abs(f['cw'] - 0.094) <= 0.005 else 'MISMATCH'}); full Moran {f['mo']['I']:.4f} vs s21 0.157")
        results[T] = rows
        emit(f"  elapsed {time.time() - t0:.0f}s")
        emit()

    def call(rows, pk, sk):
        ex = lambda r: rows[r]["lo"] > 0
        inc = lambda r: rows[r]["lo"] <= 0 <= rows[r]["hi"] or rows[r]["hi"] < 0
        if (ex(pk) or ex(sk)) and inc("core-only"):
            return "F1 in the affix layer"
        if ex("core-only") and inc(pk) and inc(sk):
            return "F1 in the core layer"
        return "F1 in both / neither layer"

    emit("=== READING (pre-registered rule; ZL3b KEEP-∅ decides) ===")
    calls = {}
    for T, rows in results.items():
        ck = call(rows, "prefix-only (keep ∅)", "suffix-only (keep ∅)")
        cd = call(rows, "prefix-only (drop ∅)", "suffix-only (drop ∅)")
        calls[T] = ck
        excl = [n for n, r in rows.items() if r["lo"] > 0]
        cwpos = sorted(((r["cw"], n) for n, r in rows.items() if n != "full"), reverse=True)
        emit(f"  {T}: KEEP -> {ck}; DROP -> {cd}; intervals excluding zero: {excl}; "
             f"CHARWIN full {rows['full']['cw']:+.4f}, largest stream {cwpos[0][1]} {cwpos[0][0]:+.4f}, "
             f"core-only {rows['core-only']['cw']:+.4f}, prefix-keep {rows['prefix-only (keep ∅)']['cw']:+.4f}, suffix-keep {rows['suffix-only (keep ∅)']['cw']:+.4f}")
        emit(f"    Moran cross-check (s33): core-only I {rows['core-only']['mo']['I']:+.4f} (p {rows['core-only']['mo']['p']:.3f}); "
             f"prefix-keep {rows['prefix-only (keep ∅)']['mo']['I']:+.4f} (p {rows['prefix-only (keep ∅)']['mo']['p']:.3f}); "
             f"suffix-keep {rows['suffix-only (keep ∅)']['mo']['I']:+.4f} (p {rows['suffix-only (keep ∅)']['mo']['p']:.3f}); full {rows['full']['mo']['I']:+.4f}")
    z = calls["ZL3b"]
    flips = [T for T in ("RF1b", "IT2a") if calls[T] != z]
    emit(f"reading: {z} (ZL3b); prediction (i) affix layer {'HOLDS' if z == 'F1 in the affix layer' else 'does not hold'}; "
         f"prediction (ii) core layer {'HOLDS' if z == 'F1 in the core layer' else 'does not hold'}; {'UNSTABLE on ' + ', '.join(flips) if flips else 'same call on RF1b, IT2a'}")
    emit()
    emit(f"elapsed {time.time() - t0:.1f} s")
    emit(f"run finished {clock()}")
    flush()
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
