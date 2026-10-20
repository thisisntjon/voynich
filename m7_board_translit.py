"""m7: score the five converted transliterations on the frozen v1 board.

Each data/translit/*.meta.json corpus is passed as the "target" entrant
(words + lines in its own page skeleton) through the identical code path
g0_score_filed.py uses: scoreboard/score.py v1 loaded by path,
score.score_corpus(name, words, lines). PREREG.md bands are not changed.

GC2a uses the v101 alphabet. score.py hard-codes EVA 'p' (line-initial) and
'm' (line-final). The v101 glyphs that correspond were derived by aligning
ZL3b_eva and GC2a tokens on lines of equal length (2311 lines):
EVA p -> v101 'g' (234/285; 'j' 37 is the p-variant), EVA m -> v101 'p'
(434/482; 'P' 17 variant). No correspondence table exists in
data/external/voynich-nu-ivtff/ (README, ivtff_format: none found).
GC2a is scored twice: as-is (identical path; p/m there are the wrong
glyphs) and with the bijective 3-cycle relabel g->p, p->m, m->g, under
which every other metric is invariant (entropy, lengths, JSD, MI are
relabel-invariant; checked in the output). Seed 20261017 (score.py's
own fixed seeds are used inside the scorer; nothing here draws).
Writes results_m7_board_translit.txt. Modifies no existing file.
"""
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    "scoreboard_score", ROOT / "scoreboard" / "score.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

SEED = 20261017
OUT = ROOT / "results_m7_board_translit.txt"
TRANSLIT = ROOT / "data" / "translit"
FILES = ["ZL3b_eva", "RF1b", "IT2a", "ZL3b_glyphplus", "GC2a"]
EVA_BASED = ["ZL3b_eva", "RF1b", "IT2a", "ZL3b_glyphplus"]
BANDS = ["h2", "sd_len", "jsd_first_fg", "p_init_enrich", "m_final_enrich",
         "cross_excess_eva", "redup_pct"]
PREREG = {  # PREREG.md v1 (frozen); (lo, hi)
    "h2": (1.98, 2.28), "sd_len": (1.41, 2.11), "jsd_first_fg": (0.10, None),
    "p_init_enrich": (8, None), "m_final_enrich": (8, None),
    "cross_excess_eva": (0.09, None), "redup_pct": (0.4, 1.8),
}
FMT = {"h2": "{:.3f}", "sd_len": "{:.3f}", "jsd_first_fg": "{:.4f}",
       "p_init_enrich": "x{}", "m_final_enrich": "x{}",
       "cross_excess_eva": "{:+.4f}", "redup_pct": "{}%"}
GC_RELABEL = str.maketrans({"g": "p", "p": "m", "m": "g"})
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def load(name):
    d = json.loads((TRANSLIT / f"{name}.meta.json").read_text(encoding="utf-8"))
    lines = [ws for p in d["pages"] for ws in p["lines"]]
    return [w for ws in lines for w in ws], lines, d


def fmt(k, v):
    return FMT[k].format(v)


def in_band(k, v):
    lo, hi = PREREG[k]
    return lo <= v and (hi is None or v <= hi)


def margin(k, v):
    lo, hi = PREREG[k]
    m = v - lo
    if hi is not None:
        m = min(m, hi - v)
    return m


def main():
    emit(f"m7 board x transliteration  seed={SEED}  "
         f"run={time.strftime('%Y-%m-%d %H:%M %Z')}")
    emit("scorer: scoreboard/score.py v1 via score_corpus(name, words, lines), "
         "same call as g0_score_filed.py")
    emit("Bands (PREREG v1): h2 1.98-2.28, sd 1.41-2.11, JSDf>=0.10, p>=x8, "
         "m>=x8, excess>=+0.09, redup 0.4-1.8%")
    emit()
    rows = {}
    for name in FILES:
        words, lines, d = load(name)
        emit(f"{name}: alphabet={d['alphabet']} collapse={d['collapse']} "
             f"pages={len(d['pages'])} lines={len(lines)} tokens={len(words)} "
             f"dropped_unreadable={d['dropped_unreadable_tokens']}")
        rows[name] = score.score_corpus(name, words, lines)
    words, lines, _ = load("GC2a")
    rl = [[w.translate(GC_RELABEL) for w in ws] for ws in lines]
    rows["GC2a_v101pm"] = score.score_corpus(
        "GC2a_v101pm", [w for ws in rl for w in ws], rl)
    emit("GC2a_v101pm: GC2a relabelled g->p, p->m, m->g so score.py's p/m "
         "read v101 g (=EVA p) line-initial and v101 p (=EVA m) line-final")
    inv = [k for k in BANDS if k not in ("p_init_enrich", "m_final_enrich")
           and rows["GC2a"][k] != rows["GC2a_v101pm"][k]]
    emit(f"relabel invariance of other bands: {'OK' if not inv else 'BROKEN ' + str(inv)}")
    emit()

    hdr = f"{'translit':16}" + "".join(f"{k:>18}" for k in BANDS) + f"{'tokens':>8}"
    emit(hdr)
    for name, r in rows.items():
        emit(f"{name:16}" + "".join(f"{fmt(k, r[k]):>18}" for k in BANDS)
             + f"{r['tokens']:>8}")
    emit()

    board = json.loads((ROOT / "scoreboard" / "scoreboard.json").read_text(encoding="utf-8"))
    voy = next(e for e in board["entrants"] if e["name"] == "voynich_eva")
    g0 = (ROOT / "results_g0.txt").read_text(encoding="utf-8")
    emit("ZL3b_eva vs scoreboard.json voynich_eva (filed; PREREG Voynich column):")
    diffs = []
    for k in BANDS:
        a, b = rows["ZL3b_eva"][k], voy[k]
        same = fmt(k, a) == fmt(k, b)
        if not same:
            diffs.append(k)
        emit(f"  {k:18} m7={fmt(k, a):>10} filed={fmt(k, b):>10} raw_equal={a == b} "
             f"printed_equal={same}")
    emit(f"  tokens m7={rows['ZL3b_eva']['tokens']} filed={voy['tokens']}")
    emit(f"  result: {'MATCH at printed precision' if not diffs else 'DIFFERENCE in ' + str(diffs)}")
    emit("  (results_g0.txt holds no Voynich row itself; its Bands line is the "
         "same PREREG gates: "
         f"{'found' if 'Bands: h2 1.98-2.28' in g0 else 'NOT found'})")
    emit()

    emit("Spread across EVA-based files (ZL3b_eva, RF1b, IT2a, ZL3b_glyphplus) "
         "and GC2a separately:")
    emit(f"{'band':18}{'eva_min':>10}{'eva_max':>10}{'GC2a':>10}{'GC2a_v101pm':>13}"
         f"{'PREREG band':>16}")
    verdicts = []
    for k in BANDS:
        vals = {n: rows[n][k] for n in EVA_BASED}
        lo_n, hi_n = min(vals, key=vals.get), max(vals, key=vals.get)
        lo, hi = vals[lo_n], vals[hi_n]
        gc = rows["GC2a"][k]
        gcpm = rows["GC2a_v101pm"][k]
        blo, bhi = PREREG[k]
        band = f"{blo}-{bhi}" if bhi is not None else f">={blo}"
        emit(f"{k:18}{fmt(k, lo):>10}{fmt(k, hi):>10}{fmt(k, gc):>10}"
             f"{fmt(k, gcpm):>13}{band:>16}   (min {lo_n}, max {hi_n})")
        gcv = gcpm if k in ("p_init_enrich", "m_final_enrich") else gc
        allv = dict(vals, GC2a=gcv)
        out = [n for n, v in allv.items() if not in_band(k, v)]
        mins = min(margin(k, v) for v in allv.values())
        if bhi is not None:
            width = bhi - blo
            near = mins < 0.15 * width
            marg = f"closest value {mins:+.3f} from an edge ({mins / width:.0%} of band width)"
        else:
            near = mins < 0.25 * blo
            marg = f"closest value {mins:+.3f} above threshold ({mins / blo:.0%} of it)"
        spread = (f"EVA spread {fmt(k, lo)}..{fmt(k, hi)}, GC2a {fmt(k, gcv)} "
                  f"vs band {band}; {marg}")
        if out:
            v = f"{k}: PAST band edge for {out}; {spread}"
        elif near:
            v = f"{k}: inside band but NEAR an edge; {spread}"
        else:
            v = f"{k}: comfortably inside; {spread}"
        verdicts.append(v)
    emit()
    emit("Per-band verdict (GC2a uses the v101-mapped p/m for the enrichment bands):")
    for v in verdicts:
        emit("  " + v)
    pure = ["ZL3b_eva", "RF1b", "IT2a"]
    emit()
    emit("Note: h2 and sd_len are measured per alphabet unit. ZL3b_glyphplus and "
         "GC2a (v101) write multi-letter EVA glyphs (ch, sh, cth, iin, ...) as one "
         "symbol, so their h2 rises and sd_len falls by construction; the PREREG "
         "h2/sd_len bands were set at EVA character level and only the three "
         "plain-EVA files are on that scale. Plain-EVA spread: "
         + ", ".join(f"{k} {fmt(k, min(rows[n][k] for n in pure))}..{fmt(k, max(rows[n][k] for n in pure))}"
                     for k in ("h2", "sd_len")))
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    emit(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
