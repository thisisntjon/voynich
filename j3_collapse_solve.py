"""J3: crack attempt — collapse J1v2 homophone classes, then solve.

Logic: if J2 classes are homophones (same plaintext unit, spelling/flow
variants), collapsing each class to its most frequent type should (a) move
scoreboard metrics toward natural language and (b) improve a6 homophonic
solver score toward the Latin ceiling, paired at equal solver budget vs
raw Voynich and vs pseudo null. If classes are mere spelling families,
collapsing destroys information and (b) will not improve.
Filed references: a6 Latin ceiling -3.084, Voynich k0 -3.891 (full budget;
here reduced budget, paired comparison is primary).
Run: uv run python j3_collapse_solve.py -> results_j3.txt
"""
import importlib.util
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
spec = importlib.util.spec_from_file_location("score", ROOT / "scoreboard" / "score.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

import corpora  # noqa: E402
import b4_selfcite_sim as b4  # noqa: E402
import f4_homophone_classes as f4  # noqa: E402
import a6_solver as a6  # noqa: E402
from j2_voynich_classes import j1v2_cluster  # noqa: E402

OUT = ROOT / "results_j3.txt"
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def solve_sample(words, lm, label):
    seqs = [list(w) for w in words[:2500]]
    arr, inv = a6.encode_units(seqs)
    best, m = a6.solve(arr, len(inv), lm, iters=15000, restarts=2, seed=0)
    dec = a6.decode(m, inv, seqs, n=14)
    emit(f"{label}: solver score {best:.3f} bits/char (units={len(inv)}) decode: {' '.join(dec)}")
    return best


def main():
    by = b4.pages()
    L = f4.lines_of(by)
    kfull = f4.k_for(L, 0.5)
    assign = j1v2_cluster(L, kfull, 0)
    cnt = Counter(w for l in L for w in l)
    byclass = {}
    for t, c in assign.items():
        byclass.setdefault(c, []).append(t)
    rep = {c: max(ts, key=lambda t: cnt[t]) for c, ts in byclass.items()}
    collapsed_lines = [[rep[assign[w]] if w in assign else w for w in l] for l in L]
    collapsed_words = [w for l in collapsed_lines for w in l]
    raw_words = [w for l in L for w in l]
    emit(f"J3 collapse: K={kfull} classes over {len(assign)} types; "
         f"types raw={len(set(raw_words))} collapsed={len(set(collapsed_words))}")
    for name, words, lines in (("voynich_raw", raw_words, L),
                               ("voynich_class_collapsed", collapsed_words, collapsed_lines)):
        row = score.score_corpus(name, words, lines)
        emit(f"{name:26} h2={row['h2']:.3f} sd={row['sd_len']:.2f} types={row['types']} "
             f"JSDf={row['jsd_first_fg']:.4f} excess={row['cross_excess_eva']:+.4f} redup={row['redup_pct']}%")
    lm = a6.train_lm(corpora.control("latin_caesar"))
    emit(f"Latin LM self-score (reference): {a6.lm_score(lm, corpora.control('latin_caesar')[:2500]):.3f}")
    solve_sample(raw_words, lm, "raw Voynich -> Latin")
    solve_sample(collapsed_words, lm, "collapsed Voynich -> Latin")
    pseudo_seqs = a6.pseudo([list(w) for w in raw_words[:2500]], 2500, 1)
    pseudo_words = ["".join(s) for s in pseudo_seqs]
    solve_sample(pseudo_words, lm, "pseudo-Voynich null -> Latin")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    emit("Wrote results_j3.txt")


if __name__ == "__main__":
    main()
