"""Score the four filed streams on the frozen v1 board.

Streams, regenerated from the filed code, not from a new theory:
  c2_tuned_l200_post_s4  C2 main: section, seed 4, p_seed 0.6, L=200,
                         post=True, rule_p=0.088, rule_m=0.21
  d3_verbose_seed1       d3.encipher(seed=1) of Caesar, its own line lengths
  naibbe_skeleton        c4.skeleton of the cached Zenodo sampler
  b4_simcal_global       b4.generate global, seed 3, p_samecol=0.05,
                         p_mut=0.97, recent_lines=99
  b4_simcal_seeded       same, variant="seeded" (real first line kept)

b4 SIMcal is generated before c2 is imported. c2 replaces
b4.build_neighbours at import, which would change a later SIMcal draw.

Metrics are score.score_corpus. Bands are the frozen PREREG v1 gates.
This script does not change those gates. It appends rows to
scoreboard/scoreboard.json and leaves the original four entrants and
reproduction_pass as they were.
"""
import importlib.util
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    "scoreboard_score", ROOT / "scoreboard" / "score.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

import b4_selfcite_sim as b4
import corpora
import d3_verbose_forward as d3

OUT = ROOT / "results_g0.txt"
BOARD = ROOT / "scoreboard" / "scoreboard.json"
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flatten(by):
    lines = [r["words"] for recs in by.values() for r in recs]
    return [w for line in lines for w in line], lines


def bands(row):
    checks = {
        "h2": 1.98 <= row["h2"] <= 2.28,
        "sd_len": 1.41 <= row["sd_len"] <= 2.11,
        "jsd_first_fg": row["jsd_first_fg"] >= 0.10,
        "p_init_enrich": row["p_init_enrich"] >= 8,
        "m_final_enrich": row["m_final_enrich"] >= 8,
        "cross_excess_eva": row["cross_excess_eva"] >= 0.09,
        "redup_pct": 0.4 <= row["redup_pct"] <= 1.8,
    }
    return checks


def show(name, row):
    checks = bands(row)
    failed = [k for k, ok in checks.items() if not ok]
    emit(f"{name}")
    emit(f"  h2={row['h2']:.3f} sd={row['sd_len']:.3f} "
         f"JSDf={row['jsd_first_fg']:.4f} p=x{row['p_init_enrich']} "
         f"m=x{row['m_final_enrich']} excess={row['cross_excess_eva']:+.4f} "
         f"redup={row['redup_pct']}%  tokens={row['tokens']}")
    emit(f"  joint={'PASS' if not failed else 'FAIL'}  failed={failed or '-'}")
    return row


def main():
    by = b4.pages()
    streams = []

    sim_g = b4.generate("global", 3, by, p_samecol=0.05, p_mut=0.97, recent_lines=99)
    sim_s = b4.generate("seeded", 3, by, p_samecol=0.05, p_mut=0.97, recent_lines=99)
    streams.append(("b4_simcal_global", *flatten(sim_g)))
    streams.append(("b4_simcal_seeded", *flatten(sim_s)))

    import c2_section_generator as c2
    import c4_naibbe_lines as c4

    g = c2.Gen(by)
    c2_by = g.generate("section", 4, p_seed=0.6, lex_size=200, post=True,
                       rule_p=0.088, rule_m=0.21)
    streams.append(("c2_tuned_l200_post_s4", *flatten(c2_by)))

    nb = c4.skeleton(c4.naibbe_tokens(), by)
    streams.append(("naibbe_skeleton", *flatten(nb)))

    vlines = [r["words"] for r in corpora.voynich_lines()]
    lengths = [len(line) for line in vlines if line]
    words, lines, meta = d3.encipher(1, corpora.control("latin_caesar"), lengths)
    streams.append(("d3_verbose_seed1", [w for line in lines for w in line], lines))
    emit(f"d3 seed 1 meta: {meta}")
    emit("Bands: h2 1.98-2.28, sd 1.41-2.11, JSDf>=0.10, p>=x8, m>=x8, "
         "excess>=+0.09, redup 0.4-1.8%")
    emit("score.py line metrics use every line. b4.report dropped page-first lines.")
    emit()

    rows = []
    for name, words, lines in streams:
        rows.append(show(name, score.score_corpus(name, words, lines)))

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    kept = [e for e in board["entrants"] if e["name"] not in {r["name"] for r in rows}]
    board["entrants"] = kept + rows
    BOARD.write_text(json.dumps(board, indent=2), encoding="utf-8")
    emit()
    emit(f"board entrants: {[e['name'] for e in board['entrants']]}")
    emit(f"reproduction_pass left as {board.get('reproduction_pass')}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
