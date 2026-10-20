"""One row: the filed F3 flow cipher, plus the two line rules already measured.

Declared before the run. Do not edit these constants after results_h1.txt exists.

BETA = 1.5 is the value already printed in results_f3.txt. It is not refit,
and no other beta is scored as a candidate.
Line rules are c2's filed RULE_P and RULE_M, applied after the cipher
stream is poured into the Voynich page/line skeleton (c4.skeleton).
Cipher seed = 1, as f3.cipher_stream. Rule seed = 20261017.

The unruled stream is printed only as a reproduction check against
results_f3.txt. The decision is the ruled row, on the seven PREREG v1 bands.
"""
import importlib.util
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
import c4_naibbe_lines as c4
import f3_flow_choice as f3

OUT = ROOT / "results_h1.txt"
BETA = 1.5
CIPHER_SEED = 1
RULE_SEED = 20261017
RULE_P = 0.088
RULE_M = 0.148
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flatten(by):
    lines = [r["words"] for recs in by.values() for r in recs]
    return [w for line in lines for w in line], lines


def apply_rules(lines):
    rng = random.Random(RULE_SEED)
    out = []
    for src in lines:
        line = src[:]
        if line and rng.random() < RULE_P:
            w = line[0]
            line[0] = "p" + (w[1:] if w[0] in "ktfq" else w)
        if line and rng.random() < RULE_M:
            w = line[-1]
            line[-1] = (w[:-1] if w[-1] in "ynlrs" else w) + "m"
        out.append(line)
    return out


def fails(row):
    checks = {
        "h2": 1.98 <= row["h2"] <= 2.28,
        "sd_len": 1.41 <= row["sd_len"] <= 2.11,
        "jsd_first_fg": row["jsd_first_fg"] >= 0.10,
        "p_init_enrich": row["p_init_enrich"] >= 8,
        "m_final_enrich": row["m_final_enrich"] >= 8,
        "cross_excess_eva": row["cross_excess_eva"] >= 0.09,
        "redup_pct": 0.4 <= row["redup_pct"] <= 1.8,
    }
    return [k for k, ok in checks.items() if not ok]


def show(name, words, lines):
    row = score.score_corpus(name, words, lines)
    missed = fails(row)
    emit(f"{name}")
    emit(f"  tokens={row['tokens']} types={row['types']} "
         f"h2={row['h2']:.3f} sd={row['sd_len']:.3f} "
         f"JSDf={row['jsd_first_fg']:.4f} p=x{row['p_init_enrich']} "
         f"m=x{row['m_final_enrich']} excess={row['cross_excess_eva']:+.4f} "
         f"redup={row['redup_pct']}%")
    emit(f"  joint={'PASS' if not missed else 'FAIL'}  missed={missed or '-'}")
    return missed


def main():
    emit("H1 one row  BETA=1.5 (from results_f3.txt, not refit)  "
         f"rules p={RULE_P} m={RULE_M} after skeleton")
    emit("bands: h2 1.98-2.28, sd 1.41-2.11, JSDf>=0.10, p>=x8, m>=x8, "
         "excess>=+0.09, redup 0.4-1.8%")
    emit()
    by = b4.pages()
    seq, tab = f3.naibbe_chunks()
    toks = f3.cipher_stream(seq, tab, f3.ratio_table(by), BETA, CIPHER_SEED)
    sk = c4.skeleton(toks, by)
    words, lines = flatten(sk)
    emit(f"cipher tokens poured={len(words)}  source chunks={len(seq)}")
    emit("unruled row is a reproduction check, not a candidate")
    show("unruled beta=1.5", words, lines)
    ruled = apply_rules(lines)
    missed = show("RULED beta=1.5", [w for line in ruled for w in line], ruled)
    emit()
    emit("DECISION: " + ("JOINT PASS" if not missed else
                         "NO JOINT PASS  missed=" + ",".join(missed)))
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
