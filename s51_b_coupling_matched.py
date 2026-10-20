"""s51 — O-052: Voynich Currier B cross-space coupling (cross_excess_eva) vs short Latin verse at matched size.

PRE-REGISTERED QUESTION (verbatim; frozen in s51_b_coupling_matched.prereg.sha256 before the run):
"At matched size, is Voynich Currier B's cross-space coupling (cross_excess_eva, B 0.232 on ZL3b) separable
from the short Latin verse manuscripts that reach it in this project's own s18 per-manuscript rows
(LaurPlut33.31 Priapea 0.248 at 1,267 tokens; LaurPlut39.34 Priapea 0.209 at 770; Latin8236 0.178 at 1,403;
Egerton821 0.160 at 1,088; files results_s18_cremma_<ms>.json)?"

DESIGN (verbatim from the step brief):
"for each verse/formulaic manuscript m above, draw 500 random contiguous-line blocks from Voynich Currier B
with the same token count as m (and separately from Currier A), compute cross_excess_eva the same way as m's
row, and report the B (and A) draw median and 2.5/97.5 % bounds. Also compute each verse manuscript's own
sampling spread by 500 half-size contiguous-block resamples of m and of Voynich B at the same half size, so
the comparison is like-for-like. Check: the full-B value reproduces s20 (0.2321 ZL3b) to four decimals or
stop. Fixed prediction: "B separable from short Latin verse" if, for every verse manuscript, m's value lies
below B's matched 2.5 % bound; "not separable" if any m lies inside B's matched interval; report per
manuscript with margins. Same on RF1b and IT2a."

Method (fixed before the run)
  Metric: cross_excess_eva exactly as scoreboard/run_v2.py score_one -> score.score_corpus computes it:
    score.edge_metrics(lines, identity, nrep=20)["excess"] (plug-in MI of (last glyph of word i, first glyph of
    word i+1) within lines, minus the mean of 20 within-line word shuffles with random.Random(0); rounded to 4
    decimals by edge_metrics).  score is the module object run_v2 loads by path (R2.score), so the code is the
    scorer's own.  Only this one metric is computed per draw (the other run_v2 metrics do not enter it).
  Voynich text:
    ZL3b = R2.M.voynich_pages("eva") (run_v2 --voynich loader; vparse default strict_spaces=False, i.e. the
      comma ',' (uncertain space) is a WORD BREAK — this is the convention run_v2 uses).
    RF1b, IT2a = R2.load_meta(data/translit/<t>.meta.json), lang subset, R2.subsample(pages, 40000) as the
      s20 calls (--n-sample 40000; B and A are under the cap so whole).
    Currier B = pages with lang "B"; Currier A = pages with lang "A"; lines in manuscript page order,
      concatenated across page boundaries.
  Verse rows: m in LaurPlut33.31, LaurPlut39.34, Latin8236, Egerton821.  m's value = the "row"
    cross_excess_eva in results_s18_cremma_<m>.json (the comparison number).  It is also recomputed from
    data/controls_realline/cremma_<m>.meta.json via R2.load_meta + R2.subsample(25000) (the s18 run_v2 call;
    whole, all are < 25k) and must equal the s18 value to 4 decimals, else STOP.  T_m = that row's token count.
  Checks (STOP if any fails; results file then says STOPPED and nothing is read): full-B and full-A
    cross_excess_eva per transliteration equal s20 to 4 decimals: ZL3b B 0.2321 A 0.1203; RF1b B 0.2259
    A 0.1071; IT2a B 0.2181 A 0.0968.
  Contiguous block of T tokens from a line list L (in order): start line s drawn uniformly from the starts
    whose remaining text holds >= T tokens; take whole lines from s until the running count reaches >= T;
    the last line is cut so the block has exactly T tokens.  rng = random.Random(20261017) re-seeded for every
    (transliteration, convention, source, manuscript, size) cell.
  Matched draws: for each m and transliteration, 500 B blocks and 500 A blocks of T_m tokens -> median and
    2.5 / 97.5 % (numpy percentile, linear).
  Half-size like-for-like: H_m = T_m // 2; 500 contiguous H_m-token blocks of m's own lines (sidecar order)
    and 500 of Voynich B at H_m -> median and 2.5 / 97.5 % for each.  Reported beside, with the half-size
    margin (m half median - B half 2.5 % bound) and whether the two half-size intervals overlap; it does not
    enter the decision rule.  Done on ZL3b and on RF1b / IT2a.
  Decision rule per transliteration (ZL3b is the decision row; RF1b and IT2a are agreement rows):
    position of m vs B's matched [2.5 %, 97.5 %]: "below" if m < 2.5 % bound, "inside", or "above" if
    m > 97.5 % bound; margin = m - B 2.5 % bound (negative = below).
    "B separable from short Latin verse" if every m is below; otherwise "not separable", naming the rows that
    are inside (or above; above also counts as not separable, as it is not below).
    A's matched interval and m's position against it are printed beside (no decision weight).
  Comma-convention sensitivity (reported, no decision weight):
    ZL3b with vparse strict_spaces=True (comma = no break; the two sides are joined) via
    R2.M.voynich_pages("eva", strict_spaces=True): full B and A values, then the same 500 matched B and A
    draws per m and the same rule, printed as a sensitivity row.
    RF1b: the sidecar is pre-tokenised, so its comma convention cannot be switched in place; RF1b's source
    data/external/voynich-nu-ivtff/RF1b-er.txt is re-parsed with vparse.load(path=..) through the same
    voynich_pages logic under the default convention, and ONLY if that rebuild reproduces s20 RF1b B 0.2259
    to 4 decimals is the strict_spaces=True RF1b sensitivity row run; otherwise it is printed as "not run"
    with the rebuilt value.  IT2a: counted commas in the sidecar tokens are printed; if 0, its sensitivity row
    equals its main row by construction and is not re-run.
  Output: results_s51.txt (header with `date`, sha256 of this file, stub_match, elapsed) and
    runs/s51/draws.tsv (one line per draw: translit, convention, source, manuscript, size, draw, start line,
    lines used, value).

Run:    python -I s51_b_coupling_matched.py
Writes: results_s51.txt, runs/s51/draws.tsv.  No other file is touched.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import subprocess
import sys
import time
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

OUT = ROOT / "results_s51.txt"
RUNS = ROOT / "runs" / "s51"
STUB = ROOT / "s51_b_coupling_matched.prereg.sha256"
SELF = ROOT / "s51_b_coupling_matched.py"
SEED = 20261017
DRAWS = 500
MSS = ["LaurPlut33.31", "LaurPlut39.34", "Latin8236", "Egerton821"]
S20 = {"ZL3b": {"B": 0.2321, "A": 0.1203}, "RF1b": {"B": 0.2259, "A": 0.1071}, "IT2a": {"B": 0.2181, "A": 0.0968}}
RF1B_SRC = ROOT / "data" / "external" / "voynich-nu-ivtff" / "RF1b-er.txt"
log: list[str] = []
tsv: list[str] = []


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


class Ctx:
    R2 = None


def cee(lines) -> float:
    return float(Ctx.R2.score.edge_metrics(lines, lambda w: w)["excess"])


def block(lines, cum, T, rng):
    """cum[i] = tokens in lines[i:] ; pick start uniformly among starts with cum >= T."""
    starts = [i for i in range(len(lines)) if cum[i] >= T]
    s = rng.choice(starts)
    out, k, i = [], 0, s
    while k < T:
        ln = lines[i]
        need = T - k
        take = ln if len(ln) <= need else ln[:need]
        out.append(take)
        k += len(take)
        i += 1
    return out, s


def suffix_counts(lines):
    cum = [0] * (len(lines) + 1)
    for i in range(len(lines) - 1, -1, -1):
        cum[i] = cum[i + 1] + len(lines[i])
    return cum[:-1]


def draw_set(lines, T, tag):
    rng = random.Random(SEED)
    cum = suffix_counts(lines)
    vals, nlines = [], []
    for d in range(DRAWS):
        b, s = block(lines, cum, T, rng)
        assert sum(len(x) for x in b) == T
        v = cee(b)
        vals.append(v)
        nlines.append(len(b))
        tsv.append("\t".join(map(str, (*tag, T, d, s, len(b), f"{v:.4f}"))))
    return dict(T=T, med=pct(vals, 50), lo=pct(vals, 2.5), hi=pct(vals, 97.5), lines_med=pct(nlines, 50))


def pos(v, d):
    return "below" if v < d["lo"] else ("above" if v > d["hi"] else "inside")


def fmt(d):
    return f"{d['med']:.4f} [{d['lo']:.4f}, {d['hi']:.4f}]"


def lines_of(pages, lang=None):
    return [ln for p in pages if lang is None or p["lang"] == lang for ln in p["lines"]]


def voy_pages_from(path, strict):
    """R2.M.voynich_pages logic with an explicit IVTFF path (RF1b sensitivity rebuild)."""
    vp = Ctx.R2.M.vparse
    recs = vp.paragraph_text(vp.load(strict_spaces=strict, path=path))
    pages, cur = [], None
    for r in recs:
        ws = [w for w in r["words"] if "?" not in w]
        if cur is None or cur["id"] != r["page"]:
            cur = dict(id=r["page"], section=r["illus"], hand=r["hand"], quire=r["quire"], lang=r["lang"], lines=[])
            pages.append(cur)
        if ws:
            cur["lines"].append(ws)
    return [p for p in pages if p["lines"]]


def finish(t0, status):
    emit()
    emit(f"status: {status}")
    emit(f"elapsed {time.time() - t0:.1f} s")
    emit(f"run finished {clock()}")
    emit(f"paths: {OUT}  {RUNS / 'draws.tsv'}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "draws.tsv").write_text("translit\tconvention\tsource\tms\tT\tdraw\tstart_line\tlines\tcross_excess_eva\n"
                                    + "\n".join(tsv) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")


def compare_block(tr, conv, AB, verse, half=None):
    """Matched draws for every m; returns per-m dict."""
    res = {}
    for m in MSS:
        T, mv = verse[m]["T"], verse[m]["v"]
        dB = draw_set(AB["B"], T, (tr, conv, "B", m))
        dA = draw_set(AB["A"], T, (tr, conv, "A", m))
        res[m] = dict(B=dB, A=dA)
        if half is not None:
            H = T // 2
            res[m]["mh"] = draw_set(verse[m]["lines"], H, (tr, conv, "m_half", m))
            res[m]["Bh"] = draw_set(AB["B"], H, (tr, conv, "B_half", m))
    return res


def report(tr, conv, res, verse, decision):
    emit(f"--- {tr} [{conv}] matched-size draws ({DRAWS} contiguous blocks of T_m tokens); margin = m - B 2.5 % bound ---")
    emit(f"{'manuscript':14} {'T_m':>5} {'m value':>8} | {'B matched median [2.5, 97.5]':>30} {'lines':>5} {'B pos':>6} {'margin':>8} | "
         f"{'A matched median [2.5, 97.5]':>30} {'A pos':>6}")
    nonbelow = []
    for m in MSS:
        r, mv = res[m], verse[m]["v"]
        p = pos(mv, r["B"])
        if p != "below":
            nonbelow.append(f"{m} ({p}, margin {mv - r['B']['lo']:+.4f})")
        emit(f"{m:14} {verse[m]['T']:5d} {mv:8.4f} | {fmt(r['B']):>30} {r['B']['lines_med']:5.0f} {p:>6} {mv - r['B']['lo']:+8.4f} | "
             f"{fmt(r['A']):>30} {pos(mv, r['A']):>6}")
    if "mh" in res[MSS[0]]:
        emit(f"  half-size like-for-like ({DRAWS} contiguous blocks of H_m = T_m//2 tokens each side; reported, no decision weight)")
        emit(f"  {'manuscript':14} {'H_m':>5} | {'m half median [2.5, 97.5]':>30} | {'B half median [2.5, 97.5]':>30} | "
             f"{'m med - B lo':>12} {'overlap':>7}")
        for m in MSS:
            mh, bh = res[m]["mh"], res[m]["Bh"]
            ov = "yes" if mh["hi"] >= bh["lo"] and bh["hi"] >= mh["lo"] else "no"
            emit(f"  {m:14} {mh['T']:5d} | {fmt(mh):>30} | {fmt(bh):>30} | {mh['med'] - bh['lo']:+12.4f} {ov:>7}")
    reading = "B separable from short Latin verse" if not nonbelow else "not separable"
    emit(f"  reading {tr} [{conv}]{' (DECISION ROW)' if decision else ''}: {reading}"
         + (f"; not below B's matched 2.5 % bound: {'; '.join(nonbelow)}" if nonbelow else "; all four below B's matched 2.5 % bound"))
    emit()
    return reading


def main() -> int:
    t0 = time.time()
    emit("s51: O-052 Currier B cross_excess_eva vs short Latin verse at matched token count (contiguous-line blocks)")
    emit(f"run started {clock()}")
    emit(f"s51_b_coupling_matched.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit(f"metric: run_v2's score.edge_metrics(lines, identity, nrep=20)['excess'] (= cross_excess_eva); "
         f"{DRAWS} draws per cell, random.Random({SEED}) re-seeded per cell")
    emit("comma convention (decision): vparse strict_spaces=False -> ',' is a word break (run_v2 --voynich default); "
         "sensitivity: strict_spaces=True -> ',' removed, sides joined")
    R2 = load_by_path("run_v2_s51", ROOT / "scoreboard" / "run_v2.py")
    Ctx.R2 = R2
    emit(f"scorer sha256: run_v2.py {sha256(ROOT / 'scoreboard' / 'run_v2.py')[:16]}  score.py {sha256(ROOT / 'scoreboard' / 'score.py')[:16]}")
    emit()

    # verse rows
    verse = {}
    emit("--- verse rows: s18 json value (comparison) and in-memory recompute (check) ---")
    ok = True
    for m in MSS:
        js = json.loads((ROOT / f"results_s18_cremma_{m}.json").read_text(encoding="utf-8"))["row"]
        _, pages = R2.load_meta(ROOT / "data" / "controls_realline" / f"cremma_{m}.meta.json")
        pages = R2.subsample(pages, 25000)
        ls = lines_of(pages)
        rv = cee(ls)
        T = sum(len(x) for x in ls)
        good = round(rv, 4) == round(float(js["cross_excess_eva"]), 4) and T == int(js["tokens"])
        ok &= good
        verse[m] = dict(v=float(js["cross_excess_eva"]), T=int(js["tokens"]), lines=ls)
        emit(f"  {m:14} s18 {js['cross_excess_eva']:.4f} tokens {js['tokens']} lines {js['lines']} | recompute {rv:.4f} "
             f"tokens {T} lines {len(ls)} -> {'MATCH' if good else 'MISMATCH'}")
    if not ok:
        emit("STOP: a verse-row recompute does not reproduce s18")
        finish(t0, "STOPPED (verse check)")
        return 2
    emit()

    # Voynich texts
    texts = {}
    zp = R2.M.voynich_pages("eva")
    texts["ZL3b"] = {L: lines_of(zp, L) for L in ("A", "B")}
    for tr in ("RF1b", "IT2a"):
        _, pages = R2.load_meta(ROOT / "data" / "translit" / f"{tr}.meta.json")
        texts[tr] = {L: lines_of(R2.subsample(R2.subset_lang(pages, L), 40000)) for L in ("A", "B")}
    emit("--- check: full-B / full-A cross_excess_eva vs s20 (4 decimals or STOP) ---")
    ok = True
    for tr in ("ZL3b", "RF1b", "IT2a"):
        for L in ("B", "A"):
            v = cee(texts[tr][L])
            good = round(v, 4) == S20[tr][L]
            ok &= good
            emit(f"  {tr} {L}: tokens {sum(len(x) for x in texts[tr][L])} lines {len(texts[tr][L])} -> {v:.4f} vs s20 {S20[tr][L]:.4f} "
                 f"{'MATCH' if good else 'MISMATCH'}")
    if not ok:
        emit("STOP: full-text value does not reproduce s20")
        finish(t0, "STOPPED (s20 check)")
        return 2
    emit()

    readings = {}
    for tr in ("ZL3b", "RF1b", "IT2a"):
        res = compare_block(tr, "comma=break", texts[tr], verse, half=True)
        readings[tr] = report(tr, "comma=break", res, verse, decision=(tr == "ZL3b"))
        emit(f"  [elapsed so far {time.time() - t0:.0f} s]")
        emit()

    # sensitivity
    emit("=== comma-convention sensitivity (strict_spaces=True: ',' joined; no decision weight) ===")
    zs = R2.M.voynich_pages("eva", strict_spaces=True)
    ts = {L: lines_of(zs, L) for L in ("A", "B")}
    for L in ("B", "A"):
        emit(f"  ZL3b {L} comma=join: tokens {sum(len(x) for x in ts[L])} lines {len(ts[L])} -> full {cee(ts[L]):.4f} "
             f"(comma=break {S20['ZL3b'][L]:.4f})")
    res = compare_block("ZL3b", "comma=join", ts, verse)
    readings["ZL3b comma=join"] = report("ZL3b", "comma=join", res, verse, decision=False)
    rp = voy_pages_from(RF1B_SRC, False)
    rb = cee(lines_of(rp, "B"))
    if round(rb, 4) == S20["RF1b"]["B"]:
        emit(f"  RF1b rebuild from {RF1B_SRC.name} (comma=break) B {rb:.4f} reproduces s20 -> running comma=join")
        rs = voy_pages_from(RF1B_SRC, True)
        rt = {L: lines_of(rs, L) for L in ("A", "B")}
        for L in ("B", "A"):
            emit(f"  RF1b {L} comma=join: tokens {sum(len(x) for x in rt[L])} -> full {cee(rt[L]):.4f}")
        res = compare_block("RF1b", "comma=join", rt, verse)
        readings["RF1b comma=join"] = report("RF1b", "comma=join", res, verse, decision=False)
    else:
        emit(f"  RF1b sensitivity not run: rebuild from {RF1B_SRC.name} (comma=break) gives B {rb:.4f}, s20 sidecar value "
             f"{S20['RF1b']['B']:.4f} -> not reproduced")
    nc = sum(1 for L in ("A", "B") for ln in texts["IT2a"][L] for w in ln if "," in w)
    emit(f"  IT2a: tokens containing ',' in the sidecar A+B = {nc}"
         + (" -> sensitivity row equals the main row by construction (not re-run)" if nc == 0 else " (commas present; not re-run)"))
    emit()

    emit("=== READING (pre-registered rule; ZL3b comma=break is the decision row) ===")
    for k, v in readings.items():
        emit(f"  {k:18}: {v}")
    emit(f"O-052 reading: {readings['ZL3b']} (ZL3b); agreement RF1b={readings['RF1b']}, IT2a={readings['IT2a']}")
    finish(t0, "DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
