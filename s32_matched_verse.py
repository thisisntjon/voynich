"""s32 — OPEN register row O-047: Voynich line-initial JSD excess vs verse / formulaic Latin at matched line counts.

PRE-REGISTERED QUESTION (verbatim; frozen in s32_matched_verse.prereg.sha256 before the run):
"Does Voynich's line-initial JSD excess exceed verse and formulaic Latin at matched line counts? Rows:
LaurPlut33.31 (Priapea, 201 lines, excess +0.137), Egerton821 (Sortes sanctorum/charms, 114 lines, +0.132),
LaurPlut39.34 (Priapea, 131 lines, +0.102), CCCC-MSS-236 (Martial, 160 lines, +0.064) — values from
results_s18.txt; plus a pooled Latin-verse row (LaurPlut33.31 + LaurPlut39.34 + CCCC-MSS-236 sidecars
concatenated in memory). For each row: 200 random draws of ZL3b with the same number of lines (seed 20261017),
reporting median and 2.5/97.5 % of raw jsd_first, null and excess; and the difference Voynich-median minus
manuscript excess with the 2.5/97.5 % interval of (draw excess − manuscript excess). Reading: 'A1 holds
against verse' if every manuscript's excess is below the 2.5 % Voynich draw excess at its line count; 'verse
reaches Voynich at small counts' if any manuscript's excess is inside or above the draw interval; report
which. Also repeat for the four s17 verse/epic corpora (nibelungenlied, roland, croisade, dante) at 200-line
and 773-line subsamples of their own lines (first N lines of a random page order, seed 20261017), so verse vs
Voynich is compared at equal size both ways."

Method (fixed before the run)
  Voynich lines: ZL3b exactly as run_v2 --voynich loads them (R2.M.voynich_pages("eva"), run_v2 imported by
    path), all paragraph lines, no cap — the same loader as s18's matched-size reference.
  Draws: for each row size k, rng = random.Random(20261017) re-seeded per k; 200 x rng.sample(voy_lines, k);
    per draw raw jsd_first = a2_position.stats(draw, w[0])[0], null = mean of a2_position.null(draw, w[0], n=30)
    [:, 0] (30 within-line shuffles, random.Random(i), lines with >= 3 words), excess = raw - null.  Sizes
    that coincide (none expected) would re-use the same draws.
  Manuscript excesses: the four named values are taken from results_s18.txt (pooling-guard table) and are
    the comparison numbers; each is also recomputed in memory from its sidecar (load_meta + subsample(25000),
    same a2 estimator) and printed as a check — the s18 value stays the comparison number.
  Pooled Latin-verse row: the pages of cremma_LaurPlut33.31, cremma_LaurPlut39.34, cremma_CCCC-MSS-236 (base
    family) concatenated in memory in that order, subsample(25000), raw / null / excess by the same estimator;
    its line count sets its own Voynich draw size.
  Per row: diff = Voynich draw-excess median - manuscript excess; interval = [2.5 %, 97.5 %] of
    (draw excess - manuscript excess) = the draw interval shifted by the manuscript excess.
  Reading rule (five rows: four manuscripts + pooled verse): 'A1 holds against verse' if every row's excess is
    below the 2.5 % Voynich draw excess at its line count; otherwise 'verse reaches Voynich at small counts'
    and the rows inside or above the interval are named.  The four-manuscript-only reading is printed beside
    in case the pooled row alone decides it.
  s17 corpora: mhg_nibelungenlied, oldfrench_roland, occitan_croisade, italian_dante sidecars via load_meta +
    subsample(25000) (the pages s17 scored); page order shuffled by random.Random(20261017).shuffle (re-seeded
    per corpus); lines concatenated in that order; the first 200 and the first 773 lines scored (raw / null /
    excess, one value each, no re-draws).  Voynich draws at k = 200 and k = 773 (200 draws each) give the
    equal-size reference; a corpus value is flagged "inside/above" if >= the 2.5 % draw excess, else "below".

Run:    python -I s32_matched_verse.py
Writes: results_s32.txt only.  No other file is touched.
"""
from __future__ import annotations

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
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

SIDECARS = ROOT / "data" / "controls_realline"
OUT = ROOT / "results_s32.txt"
STUB = ROOT / "s32_matched_verse.prereg.sha256"
SELF = ROOT / "s32_matched_verse.py"
N_SAMPLE = 25000
JSD_NULL_N = 30
SEED = 20261017
DRAWS = 200
# (label, sidecar name, lines per results_s18.txt, jsd_first_exc per results_s18.txt, text type)
MANUSCRIPTS = [
    ("LaurPlut33.31", "cremma_LaurPlut33.31", 201, 0.1370, "Priapea 12-45, verse"),
    ("Egerton821", "cremma_Egerton821", 114, 0.1324, "Sortes sanctorum, charms (formulaic prose)"),
    ("LaurPlut39.34", "cremma_LaurPlut39.34", 131, 0.1017, "Priapea 1-16, verse"),
    ("CCCC-MSS-236", "cremma_CCCC-MSS-236", 160, 0.0642, "Martial, Epigrams I, verse"),
]
POOL_MEMBERS = ["cremma_LaurPlut33.31", "cremma_LaurPlut39.34", "cremma_CCCC-MSS-236"]
S17_VERSE = ["mhg_nibelungenlied", "oldfrench_roland", "occitan_croisade", "italian_dante"]
S17_SIZES = [200, 773]
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
    except Exception:  # noqa: BLE001
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


def pct(vals, q):
    import numpy as np
    return float(np.percentile(np.array(vals, dtype=float), q))


FEAT = (lambda w: w[0])


def jsd_first(a2, lines) -> dict:
    raw, _ = a2.stats(lines, FEAT)
    nf = a2.null(lines, FEAT, n=JSD_NULL_N)[:, 0]
    return dict(raw=float(raw), null=float(nf.mean()), null_sd=float(nf.std()), exc=float(raw - nf.mean()),
                lines=len(lines), lines_ge3=sum(1 for ws in lines if len(ws) >= 3))


def voy_draws(a2, voy_lines, k) -> dict:
    rng = random.Random(SEED)
    raws, nulls, excs = [], [], []
    for _ in range(DRAWS):
        d = rng.sample(voy_lines, k)
        jb = jsd_first(a2, d)
        raws.append(jb["raw"]); nulls.append(jb["null"]); excs.append(jb["exc"])
    return dict(k=k, raw_med=pct(raws, 50), raw_lo=pct(raws, 2.5), raw_hi=pct(raws, 97.5),
                null_med=pct(nulls, 50), null_lo=pct(nulls, 2.5), null_hi=pct(nulls, 97.5),
                exc_med=pct(excs, 50), exc_lo=pct(excs, 2.5), exc_hi=pct(excs, 97.5))


def verdict_of(exc, v) -> str:
    if exc < v["exc_lo"]:
        return "below"
    if exc > v["exc_hi"]:
        return "above"
    return "inside"


def main() -> int:
    for req in (ROOT / "scoreboard" / "run_v2.py", ROOT / "a2_position.py"):
        if not req.exists():
            raise SystemExit(f"STOP: missing {req}")
    for _, n, _, _, _ in MANUSCRIPTS:
        if not (SIDECARS / f"{n}.meta.json").exists():
            raise SystemExit(f"STOP: missing sidecar {n}.meta.json")
    for n in S17_VERSE:
        if not (SIDECARS / f"{n}.meta.json").exists():
            raise SystemExit(f"STOP: missing sidecar {n}.meta.json")

    started = clock()
    emit("S32: O-047 — Voynich line-initial JSD excess vs verse / formulaic Latin at matched line counts")
    emit(f"run started {started}")
    emit(f"s32_matched_verse.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit(f"manuscript excess values and line counts: results_s18.txt pooling-guard table (sha256 {sha256(ROOT / 'results_s18.txt')[:16]}…)")
    emit(f"estimator: a2_position.stats (feat w[0]) raw jsd_first; null = mean of a2_position.null n={JSD_NULL_N}; "
         f"excess = raw - null; Voynich = ZL3b via run_v2 M.voynich_pages('eva'); {DRAWS} draws per size, random.Random({SEED}).sample")
    emit()

    R2 = load_by_path("run_v2_s32", ROOT / "scoreboard" / "run_v2.py")
    a2 = load_by_path("a2_position", ROOT / "a2_position.py")
    voy_lines = [ln for q in R2.M.voynich_pages("eva") for ln in q["lines"]]
    full = jsd_first(a2, voy_lines)
    emit(f"ZL3b full: {full['lines']} lines ({full['lines_ge3']} with >=3 words); jsd_first raw {full['raw']:.4f} "
         f"null {full['null']:.4f} excess {full['exc']:+.4f}")
    emit()

    # ---- manuscript rows (+ pooled verse)
    rows = []
    for label, n, k18, exc18, ttype in MANUSCRIPTS:
        _, pages = R2.load_meta(SIDECARS / f"{n}.meta.json")
        pages = R2.subsample(pages, N_SAMPLE)
        lines = [ln for q in pages for ln in q["lines"]]
        chk = jsd_first(a2, lines)
        rows.append(dict(label=label, k=k18, exc=exc18, ttype=ttype, src="results_s18.txt", chk=chk,
                         k_ok=(len(lines) == k18), exc_ok=(round(chk["exc"], 4) == exc18)))
    pool_pages = []
    for n in POOL_MEMBERS:
        _, pages = R2.load_meta(SIDECARS / f"{n}.meta.json")
        pool_pages += pages
    pool_pages = R2.subsample(pool_pages, N_SAMPLE)
    pool_lines = [ln for q in pool_pages for ln in q["lines"]]
    pool = jsd_first(a2, pool_lines)
    rows.append(dict(label="Latin-verse-pool", k=pool["lines"], exc=pool["exc"], ttype="LaurPlut33.31 + LaurPlut39.34 + CCCC-MSS-236, in memory",
                     src="computed here", chk=pool, k_ok=True, exc_ok=True))
    emit("=== manuscript rows: s18 value used; in-memory recomputation from the sidecar as a check ===")
    emit(f"{'row':18} | {'lines':>5} | {'exc used':>9} | {'recomputed raw':>14} {'null':>13} {'exc':>8} | lines match / exc match | source; text type")
    for r in rows:
        c = r["chk"]
        emit(f"{r['label']:18} | {r['k']:5d} | {r['exc']:+9.4f} | {c['raw']:14.4f} {c['null']:.4f}±{c['null_sd']:.4f} {c['exc']:+8.4f} | "
             f"{r['k_ok']} / {r['exc_ok']} | {r['src']}; {r['ttype']}")
    emit(f"pooled Latin verse: {len(pool_pages)} pages, {pool['lines']} lines ({pool['lines_ge3']} with >=3 words), "
         f"{sum(len(ln) for ln in pool_lines)} tokens; members {', '.join(POOL_MEMBERS)}")
    emit()

    # ---- Voynich draws at every needed size
    sizes = sorted({r["k"] for r in rows} | set(S17_SIZES))
    emit(f"=== Voynich ZL3b draws: {DRAWS} per size, rng re-seeded per size; median [2.5 %, 97.5 %] ===")
    emit(f"{'k':>5} | {'jsd_first raw':>28} | {'null':>28} | {'excess':>31}")
    V = {}
    for k in sizes:
        v = voy_draws(a2, voy_lines, k)
        V[k] = v
        emit(f"{k:5d} | {v['raw_med']:.4f} [{v['raw_lo']:.4f}, {v['raw_hi']:.4f}] | {v['null_med']:.4f} [{v['null_lo']:.4f}, {v['null_hi']:.4f}] | "
             f"{v['exc_med']:+.4f} [{v['exc_lo']:+.4f}, {v['exc_hi']:+.4f}]")
    emit()

    # ---- rows table
    emit("=== rows: manuscript excess vs matched-size Voynich draw excess; diff = Voynich median - manuscript; interval = 2.5/97.5 % of (draw excess - manuscript excess) ===")
    emit(f"{'row':18} | {'lines':>5} | {'ms exc':>8} | {'voy exc med [2.5, 97.5]':>29} | {'diff':>8} {'[2.5, 97.5]':>20} | position")
    pos = {}
    for r in rows:
        v = V[r["k"]]
        diff = v["exc_med"] - r["exc"]
        lo, hi = v["exc_lo"] - r["exc"], v["exc_hi"] - r["exc"]
        p = verdict_of(r["exc"], v)
        pos[r["label"]] = p
        emit(f"{r['label']:18} | {r['k']:5d} | {r['exc']:+8.4f} | {v['exc_med']:+.4f} [{v['exc_lo']:+.4f}, {v['exc_hi']:+.4f}] | "
             f"{diff:+8.4f} [{lo:+.4f}, {hi:+.4f}] | {p}")
    emit()

    # ---- s17 verse corpora at 200 and 773 lines
    emit(f"=== s17 verse/epic corpora at {S17_SIZES} lines: first N lines of a random page order (random.Random({SEED}).shuffle on "
         f"load_meta+subsample(25000) pages, re-seeded per corpus); vs Voynich draws at the same N ===")
    emit(f"{'corpus':20} | {'N':>4} | {'pages used':>10} | {'raw':>7} {'null':>13} {'exc':>8} | {'voy exc med [2.5, 97.5]':>29} | {'diff':>8} | position")
    s17pos = {}
    for n in S17_VERSE:
        _, pages = R2.load_meta(SIDECARS / f"{n}.meta.json")
        pages = R2.subsample(pages, N_SAMPLE)
        order = list(range(len(pages)))
        random.Random(SEED).shuffle(order)
        all_lines = [ln for i in order for ln in pages[i]["lines"]]
        for N in S17_SIZES:
            if len(all_lines) < N:
                emit(f"{n:20} | {N:4d} | corpus has only {len(all_lines)} lines; skipped")
                continue
            sub = all_lines[:N]
            # pages used = how many pages (in shuffled order) the first N lines span
            cnt, used = 0, 0
            for i in order:
                if cnt >= N:
                    break
                cnt += len(pages[i]["lines"]); used += 1
            jb = jsd_first(a2, sub)
            v = V[N]
            p = verdict_of(jb["exc"], v)
            s17pos[(n, N)] = (jb["exc"], p)
            emit(f"{n:20} | {N:4d} | {used:10d} | {jb['raw']:7.4f} {jb['null']:.4f}±{jb['null_sd']:.4f} {jb['exc']:+8.4f} | "
                 f"{v['exc_med']:+.4f} [{v['exc_lo']:+.4f}, {v['exc_hi']:+.4f}] | {v['exc_med'] - jb['exc']:+8.4f} | {p}")
    emit()

    # ---- reading
    emit("=== READING (pre-registered rule) ===")
    hits5 = [lab for lab, p in pos.items() if p != "below"]
    hits4 = [lab for lab, p in pos.items() if p != "below" and lab != "Latin-verse-pool"]
    reading = "A1 holds against verse" if not hits5 else "verse reaches Voynich at small counts"
    reading4 = "A1 holds against verse" if not hits4 else "verse reaches Voynich at small counts"
    emit(f"five rows (4 manuscripts + pooled verse): {reading}" + (f" — inside/above: {', '.join(hits5)}" if hits5 else " — every row below the 2.5 % Voynich draw excess at its line count"))
    emit(f"four manuscripts only: {reading4}" + (f" — inside/above: {', '.join(hits4)}" if hits4 else ""))
    s17hits = [f"{n}@{N}" for (n, N), (_, p) in s17pos.items() if p != "below"]
    emit(f"s17 verse corpora at equal size: {'inside/above the Voynich draw interval: ' + ', '.join(s17hits) if s17hits else 'all below the 2.5 % Voynich draw excess at 200 and 773 lines'}")
    emit(f"largest manuscript excess {max(r['exc'] for r in rows):+.4f} ({max(rows, key=lambda r: r['exc'])['label']}); "
         f"smallest 2.5 % Voynich draw excess over the row sizes {min(V[r['k']]['exc_lo'] for r in rows):+.4f} (k={min(rows, key=lambda r: V[r['k']]['exc_lo'])['k']})")
    emit()
    emit(f"done-when: 5 manuscript/pooled rows + 4 s17 corpora x 2 sizes with matched Voynich draws and the pre-registered reading -> "
         f"{'MET' if len(rows) == 5 and len(s17pos) == len(S17_VERSE) * len(S17_SIZES) else 'NOT MET'}; reading = {reading}")
    emit(f"run finished {clock()}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
