"""J4 (Top-10 #7): context-ONLY homophone recovery, wider window, no spelling.
Gate (frozen from J1): truth type-ARI >= 0.15 at I1 m=3 before Voynich use.
J1v2 passed via spelling (circular on I1); J3 collapse then failed. Question:
can pure distributional context (offsets -2..+2, SVD80, iterative class
refinement as in f4.features) reach the gate honestly?
Run: uv run python j4_context_only.py -> results_j4.txt
"""
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans

import f4_homophone_classes as f4
import i1_power_inflation as i1

OUT = Path(__file__).parent / "results_j4.txt"
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def cluster_ctx(lines, k, seed=0, offs=(-2, -1, 1, 2), dims=80):
    cnt = Counter(w for l in lines for w in l)
    types = sorted(t for t, c in cnt.items() if c >= f4.P["MINC"])
    top = [t for t, _ in cnt.most_common(f4.P["NB"])]
    tix = {t: i for i, t in enumerate(top)}
    p = dict(f4.P, OFFS=offs, DIMS=dims)
    X = f4.features(lines, types, lambda n: tix.get(n), len(top), p)
    lab = KMeans(k, n_init=4, random_state=seed).fit_predict(X)
    return dict(zip(types, lab))


def main():
    emit("J4 context-only gate: ARI>=0.15 at m=3 (refs: F4 0.039, J1ctx+pos 0.101, J1v2+spelling 0.171)")
    for m in (3, 2, 1):
        by = i1.control(m)
        lines = f4.lines_of(by)
        for offs, dims, tag in (( (-2, -1, 1, 2), 80, "ctx4"), ((-1, 1), 80, "ctx2dim80")):
            a = cluster_ctx(lines, 96, 0, offs, dims)
            ari, nmi, tok = f4.score_truth(by, a)
            emit(f"m={m} {tag} K=96 ARI={ari:.3f} NMI={nmi:.3f} tokARI={tok:.3f}")
        OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    emit("Gate verdict in summary; no Voynich run unless m=3 clears 0.15.")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
