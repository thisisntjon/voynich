"""J2: J1v2 (gate-passing) homophone classes on Voynich + held-out class test.

Frozen procedure = J1v2 exactly: F4 context block + 2.0 * spelling TF-IDF
(char 2-3gram, SVD30), NO position block, KMeans n_init=4.
Gate record: results_j1.txt (m=3 truth ARI 0.171 >= 0.15; F4 0.039).
CAVEAT (must accompany any claim): I1 inflation creates homophones BY
spelling alternation, so the spelling block may exploit the control's
construction. Voynich held-out prediction (this file) is the transfer test.

Held-out protocol mirrors f4.heldout (page halves, shuffle-calibrated,
class_eval from f4) with J1v2 clustering substituted. K: f=0.5 rule as F4
Voynich (K=244 expected) plus K=96 for control comparability.
Run: uv run python j2_voynich_classes.py -> results_j2.txt
"""
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

import b4_selfcite_sim as b4
import f1_residual_order as f1
import f4_homophone_classes as f4

OUT = Path(__file__).parent / "results_j2.txt"
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def norm_rows(X):
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(n == 0, 1, n)


def j1v2_cluster(lines, k, seed=0):
    cnt = Counter(w for l in lines for w in l)
    types = sorted(t for t, c in cnt.items() if c >= f4.P["MINC"])
    top = [t for t, _ in cnt.most_common(f4.P["NB"])]
    tix = {t: i for i, t in enumerate(top)}
    ctx = norm_rows(f4.features(lines, types, lambda n: tix.get(n), len(top), f4.P))
    tf = TfidfVectorizer(analyzer="char", ngram_range=(2, 3), min_df=2)
    S = tf.fit_transform(types)
    d = min(30, S.shape[1] - 1, S.shape[0] - 1)
    spell = norm_rows(TruncatedSVD(d, random_state=0).fit_transform(S))
    X = np.hstack([ctx, 2.0 * spell])
    lab = KMeans(k, n_init=4, random_state=seed).fit_predict(X)
    return dict(zip(types, lab))


def heldout_j(train_by, test_by, k, seed=0):
    tr, te = f4.lines_of(train_by), f4.lines_of(test_by)
    out = {}
    for tag, (a_tr, a_te) in (("real", (tr, te)), ("shuf", (f1.shuffled(tr), f1.shuffled(te)))):
        assign = j1v2_cluster(a_tr, k, seed)
        out[tag] = f4.class_eval(a_tr, a_te, assign)
    (E2, W, C, CW), (sE2, sW, sC, sCW) = out["real"], out["shuf"]
    return dict(cls=(E2 - C) - (sE2 - sC), tok=(E2 - W) - (sE2 - sW),
                cot=(W - CW) - (sW - sCW))


def main():
    emit("J2 Voynich J1v2 classes (gate passed results_j1.txt m=3 ARI 0.171)")
    emit("F4 Voynich reference: honest cot mean -0.0052 (seeds +0.0006/-0.0122/-0.0039), null -0.0044")
    by = b4.pages()
    A, B = f4.page_halves(by)
    lines_a = f4.lines_of(A)
    k_half = f4.k_for(lines_a, 0.5)
    for k in (k_half, 96):
        rev = [heldout_j(B, A, k, s) for s in (0, 1, 2)]
        cots = [r["cot"] for r in rev]
        emit(f"K={k} held-out odd->even (honest): cot mean {np.mean(cots):+.4f} "
             f"({', '.join(f'{x:+.4f}' for x in cots)}) cls {np.mean([r['cls'] for r in rev]):+.4f} "
             f"tok {np.mean([r['tok'] for r in rev]):+.4f}")
        fwd = heldout_j(A, B, k, 0)
        emit(f"K={k} held-out even->odd (seed0): cot {fwd['cot']:+.4f} cls {fwd['cls']:+.4f} tok {fwd['tok']:+.4f}")
        OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    # Full-book clusters for inspection (largest classes, seed 0, K=k_half*2 approx F4 K)
    L = f4.lines_of(by)
    kfull = f4.k_for(L, 0.5)
    assign = j1v2_cluster(L, kfull, 0)
    cnt = Counter(w for l in L for w in l)
    byclass = {}
    for t, c in assign.items():
        byclass.setdefault(c, []).append(t)
    ranked = sorted(byclass.values(), key=lambda ts: -sum(cnt[t] for t in ts))[:8]
    emit(f"Full-book K={kfull}; largest classes by tokens:")
    for ts in ranked:
        emit("  " + " ".join(sorted(ts, key=lambda t: -cnt[t])[:14]) + f"  [{len(ts)} types]")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    emit("Wrote results_j2.txt")


if __name__ == "__main__":
    main()
