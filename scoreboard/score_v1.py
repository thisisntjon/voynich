"""Shared scoreboard v1 (PLAN Gate 0): one pipeline, identical metrics for
real text, controls, nulls and generators. Definitions copied from the filed
experiments so filed numbers reproduce:
  profile h1/h2/h3, zipf, redup  <- a1_profile.py (N=25000 cap, space symbol)
  line JSDs                      <- a2_position.py stats/null conventions
  cross-space MI                 <- c3_edge_coupling.py (plug-in, 20-rep null)
  perseveration P(recur<=k)      <- d5_rambling.py (forward next-gap)
NMI/topic metrics are intentionally NOT in v1 (B5 control contamination;
add in v2 with C1 quire null). Held-out bits/token belongs to entrant models,
not corpora, and stays with d2-style scripts.

Run: uv run python scoreboard/score.py  -> scoreboard/scoreboard.json
"""
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np  # noqa: E402

import corpora  # noqa: E402
from a1_profile import char_entropies, zipf_slope  # noqa: E402
from a2_position import jsd  # noqa: E402

OUT = Path(__file__).parent / "scoreboard.json"
N_PROFILE = 25000
SEED = 20261017

TARGETS = {  # filed values the v1 pipeline must reproduce (Voynich EVA)
    "h2": (2.126, 0.01, "results_a1.txt"),
    "jsd_first_fg": (0.1759, 0.005, "results_a2.txt"),
    "cross_mi_eva": (0.1950, 0.005, "results_c3.txt"),
    "cross_excess_eva": (0.1809, 0.01, "results_c3.txt"),
}


def profile_metrics(words):
    w = words[:N_PROFILE]
    c = Counter(w)
    ce = char_entropies(w)
    lens = [len(x) for x in w]
    redup = sum(a == b for a, b in zip(w, w[1:])) / max(len(w) - 1, 1)
    return {
        "tokens": len(w), "types": len(c),
        "hapax_rate": round(sum(v == 1 for v in c.values()) / len(c), 4),
        "mean_len": round(float(np.mean(lens)), 3),
        "sd_len": round(float(np.std(lens)), 3),
        "h1": round(ce["h1"], 4), "h2": round(ce["h2"], 4), "h3": round(ce["h3"], 4),
        "zipf": round(float(zipf_slope(w)), 4),
        "redup_pct": round(100 * redup, 3),
    }


def line_metrics(lines):
    """a2 conventions: lines with >=3 words; first/last vs mid distributions."""
    first_fg, mid_fg, last_lg, mid_lg = Counter(), Counter(), Counter(), Counter()
    for ws in lines:
        if len(ws) < 3:
            continue
        first_fg[ws[0][0]] += 1
        last_lg[ws[-1][-1]] += 1
        for w in ws[1:-1]:
            mid_fg[w[0]] += 1
            mid_lg[w[-1]] += 1
    def rate(cnt, g):
        return cnt[g] / max(sum(cnt.values()), 1)
    p_enr = rate(first_fg, "p") / rate(mid_fg, "p") if rate(mid_fg, "p") else float("inf")
    m_enr = rate(last_lg, "m") / rate(mid_lg, "m") if rate(mid_lg, "m") else float("inf")
    return {
        "jsd_first_fg": round(float(jsd(first_fg, mid_fg)), 4),
        "jsd_last_lg": round(float(jsd(last_lg, mid_lg)), 4),
        "p_init_enrich": round(float(p_enr), 2),
        "m_final_enrich": round(float(m_enr), 2),
    }


def _mi(pairs):
    n = len(pairs)
    pj = Counter(pairs)
    pa = Counter(a for a, _ in pairs)
    pb = Counter(b for _, b in pairs)
    return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in pj.items())


def edge_metrics(lines, unit, nrep=20):
    def pairs(ls):
        out = []
        for ws in ls:
            g = [unit(w) for w in ws]
            out += [(a[-1], b[0]) for a, b in zip(g, g[1:]) if a and b]
        return out
    obs = _mi(pairs(lines))
    rng = random.Random(0)
    nul = []
    for _ in range(nrep):
        sh = []
        for ws in lines:
            ws = ws[:]
            rng.shuffle(ws)
            sh.append(ws)
        nul.append(_mi(pairs(sh)))
    m = sum(nul) / nrep
    return {"mi": round(obs, 4), "null": round(m, 4), "excess": round(obs - m, 4)}


def perseveration(words, ks=(1, 5, 20, 100)):
    pos = {}
    for i, w in enumerate(words):
        pos.setdefault(w, []).append(i)
    out = {}
    for k in ks:
        hits = 0
        for idxs in pos.values():
            hits += sum(1 for a, b in zip(idxs, idxs[1:]) if b - a <= k)
        # P(recur<=k) over tokens that have a successor occurrence is biased;
        # use D5-style forward rate over all tokens except final occurrences
        # approximated by repeat-gap counts / tokens. Filed D5 numbers used
        # its own definition; v1 records this definition explicitly.
        out[f"recur_le_{k}"] = round(hits / max(len(words), 1), 4)
    return out


def score_corpus(name, words, lines):
    eva = edge_metrics(lines, lambda w: w)
    gly = edge_metrics(lines, lambda w: corpora.to_glyphs(w, corpora.GLYPHS_PLUS))
    return {
        "name": name,
        **profile_metrics(words),
        **line_metrics(lines),
        "cross_mi_eva": eva["mi"], "cross_excess_eva": eva["excess"],
        "cross_mi_glyph": gly["mi"], "cross_excess_glyph": gly["excess"],
        **perseveration(words),
    }


def prose_lines(name, n=33000, width=9):
    ws = corpora.control(name, n)
    return ws, [ws[i:i + width] for i in range(0, len(ws), width)]


def main():
    vlines = [r["words"] for r in corpora.voynich_lines()]
    vwords = [w for ls in vlines for w in ls]
    shuffled = vwords[:]
    random.Random(SEED).shuffle(shuffled)
    it = iter(shuffled)
    shuf_lines = [[next(it) for _ in ls] for ls in vlines]
    entrants = [
        ("voynich_eva", vwords, vlines),
        ("null_token_shuffled", shuffled, shuf_lines),
    ]
    for ctrl in ("latin_caesar", "italian_dante"):
        ws, ls = prose_lines(ctrl)
        entrants.append((f"ctrl_{ctrl}", ws, ls))
    board = {"version": 1, "seed": SEED, "n_profile": N_PROFILE, "entrants": []}
    for name, words, lines in entrants:
        row = score_corpus(name, words, lines)
        board["entrants"].append(row)
        print(f"{name:22} h2={row['h2']:.3f} sd={row['sd_len']:.2f} "
              f"JSDf={row['jsd_first_fg']:.4f} p=x{row['p_init_enrich']} "
              f"m=x{row['m_final_enrich']} crossMI={row['cross_mi_eva']:.4f} "
              f"excess={row['cross_excess_eva']:+.4f} redup={row['redup_pct']}%")
    voy = board["entrants"][0]
    print("\nReproduction checks (Voynich EVA vs filed):")
    ok = True
    for key, (want, tol, src) in TARGETS.items():
        got = voy[key]
        passed = abs(got - want) <= tol
        ok &= passed
        print(f"  {'PASS' if passed else 'FAIL'} {key}: got {got} want {want}±{tol} ({src})")
    board["reproduction_pass"] = bool(ok)
    OUT.write_text(json.dumps(board, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT}  reproduction_pass={bool(ok)}")


if __name__ == "__main__":
    main()
