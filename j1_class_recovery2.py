"""J1: powered homophone-class recovery — GATE TEST ONLY (no Voynich run).

Plan gate (frozen before run): procedure may touch Voynich only if truth
type-ARI >= 0.15 at I1 inflation m=3 (Voynich-like types/hapax), where the
F4 frozen procedure scored 0.044 (results_i1.txt). F4 baseline re-measured
here on identical controls for a paired comparison.

J1 joint features per type (count>=10):
  (a) F4 context block: f4.features (±1 neighbours, edge-corrected, SVD60)
  (b) spelling block: char 2-3gram TF-IDF of the type itself, SVD30
      (I1 variants are spelling alternations; real homophones may share form)
  (c) position block: P(line-initial), P(line-final), mean rel. position
Blocks L2-normalised per row-block, concatenated, KMeans (n_init=4).
K in {73, 96} (I1 m=3 / m=1 chosen K). Truth via f4.score_truth.
Run: uv run python j1_class_recovery2.py -> results_j1.txt
"""
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

import f4_homophone_classes as f4
import i1_power_inflation as i1

OUT = Path(__file__).parent / "results_j1.txt"
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def norm_rows(X):
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(n == 0, 1, n)


def j1_cluster(lines, k, seed=0):
    cnt = Counter(w for l in lines for w in l)
    types = sorted(t for t, c in cnt.items() if c >= f4.P["MINC"])
    top = [t for t, _ in cnt.most_common(f4.P["NB"])]
    tix = {t: i for i, t in enumerate(top)}
    ctx = norm_rows(f4.features(lines, types, lambda n: tix.get(n), len(top), f4.P))
    tf = TfidfVectorizer(analyzer="char", ngram_range=(2, 3), min_df=2)
    S = tf.fit_transform(types)
    d = min(30, S.shape[1] - 1, S.shape[0] - 1)
    spell = norm_rows(TruncatedSVD(d, random_state=0).fit_transform(S))
    ti = {t: i for i, t in enumerate(types)}
    pos = np.zeros((len(types), 3))
    tot = np.zeros(len(types))
    for l in lines:
        for j, w in enumerate(l):
            if w in ti:
                pos[ti[w], 0] += (j == 0)
                pos[ti[w], 1] += (j == len(l) - 1)
                pos[ti[w], 2] += j / max(len(l) - 1, 1)
                tot[ti[w]] += 1
    pos = pos / np.maximum(tot, 1)[:, None]
    pos = (pos - pos.mean(0)) / (pos.std(0) + 1e-9)
    X = np.hstack([ctx, spell, 0.5 * pos])
    lab = KMeans(k, n_init=4, random_state=seed).fit_predict(X)
    return dict(zip(types, lab))


def main():
    emit("J1 gate: truth type-ARI >= 0.15 at m=3 required before any Voynich run")
    emit("F4 filed references (results_i1.txt): m=1 ARI 0.190, m=3 ARI 0.044")
    for m in (1, 3, 2):
        by = i1.control(m)
        lines = f4.lines_of(by)
        nt, hs, nn = i1.type_stats(by)
        for k in (73, 96):
            base = f4.cluster(lines, k, 0)
            b_ari, b_nmi, b_tok = f4.score_truth(by, base)
            j1 = j1_cluster(lines, k, 0)
            j_ari, j_nmi, j_tok = f4.score_truth(by, j1)
            emit(f"m={m} K={k} types={nt} hapax={hs:.3f} tok={nn} | "
                 f"F4 ARI={b_ari:.3f} NMI={b_nmi:.3f} tokARI={b_tok:.3f} | "
                 f"J1 ARI={j_ari:.3f} NMI={j_nmi:.3f} tokARI={j_tok:.3f}")
        OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    # Declared v2 (control-side only, logged as config 2): spelling x2, no position
    # block (position hurt at m=1 where J1 < F4). Gate unchanged: ARI>=0.15 at m=3.
    emit("J1v2 declared: context + 2.0*spelling, no position block, K=96")
    for m in (3, 2):
        by = i1.control(m)
        lines = f4.lines_of(by)
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
        lab = KMeans(96, n_init=4, random_state=0).fit_predict(X)
        ari, nmi, tok = f4.score_truth(by, dict(zip(types, lab)))
        emit(f"m={m} K=96 J1v2 ARI={ari:.3f} NMI={nmi:.3f} tokARI={tok:.3f}")
        OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    emit("Gate applies at m=3 (either K). See verdict in chat/handoff, not here.")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
