"""K4: Lossy (Many-to-One + One-to-Many) Shared-Codeword Nomenclator with Flow + M5 Line Layer.

Implements the exact registered test from K_RESULTS.md §Next:
  Each plaintext word maps to k candidate codewords drawn from a shared Voynich-sized
  codeword pool (~8,500 types, matching Voynich's 7,025 observed types after finite-sample
  draws), so codewords are SHARED across plaintext words (many-to-one ambiguity +
  one-to-many flow choice).
  During encryption, the scribe chooses among a plaintext word's k allowed codewords
  weighted by:
    base_weight * (R_flow[prev_last, cw[0]] ** beta) * k1.pos_factor(cw, i, n, Qi, Qe)

Pre-registered Pass Criterion (from K_RESULTS.md):
  Within 25% of Voynich on:
    - within-hand section NMI (h1 target 0.275 -> >= 0.206; h2 target 0.333 -> >= 0.250)
    - word-order residual MI (target +0.042 -> in [+0.031, +0.053])
    - cross-boundary MI (target +0.181 -> >= +0.136)
    - line-start JSD (para target 0.549 -> >= 0.412; other target 0.147 -> >= 0.110)
  with:
    - types in 7,025 +/- 15% ([5,971, 8,079])
    - h2 in 2.11 +/- 0.15 ([1.96, 2.26])
  all on one run.

Output: results_k4.txt
"""
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import c2_section_generator as c2
import f3_flow_choice as f3
import k1_joint_producer as k1
import k2_nomenclator as k2

OUT = Path(__file__).parent / "results_k4.txt"
log = k1.log


def build_shared_codebook(all_plain_words, v_freq, pool_cap=8200, k_choices=6, rank_window=180, seed=20261017):
    """Map each plaintext word type to `k_choices` codewords drawn from a shared
    Voynich-sized pool (`pool_cap` types, ranked by Voynich frequency), where a
    plaintext word of rank `r` samples its `k_choices` allowed surface forms from
    a local frequency-rank window around `r * (pool_cap / n_plain_types)` plus
    diverse initial-glyph options so flow choice has distinct first-glyph options.
    """
    rng = random.Random(seed)
    v_types = [w for w, _ in v_freq.most_common(pool_cap)]
    v_weights = [v_freq[w] for w in v_types]

    # Group pool by first glyph so each plaintext word gets diverse initial glyphs
    by_init = defaultdict(list)
    for idx, w in enumerate(v_types):
        by_init[w[0]].append((idx, w, v_freq[w]))

    p_cnt = Counter(all_plain_words)
    p_types = [w for w, _ in p_cnt.most_common()]
    n_p = max(len(p_types), 1)
    n_v = len(v_types)

    book = {}
    codeword_owners = defaultdict(list)
    for r_idx, pw in enumerate(p_types):
        center = int(round((r_idx / n_p) * (n_v - 1)))
        lo = max(0, center - rank_window)
        hi = min(n_v, center + rank_window + 1)
        window = v_types[lo:hi]
        w_weights = v_weights[lo:hi]

        chosen = []
        seen_init = set()
        # Try to pick k_choices codewords from the rank window with distinct initial glyphs
        indices = list(range(len(window)))
        rng.shuffle(indices)
        # Sort by closeness to center + random jitter
        for idx in indices:
            cand = window[idx]
            if cand[0] not in seen_init:
                chosen.append((cand, v_freq[cand]))
                seen_init.add(cand[0])
                if len(chosen) >= k_choices:
                    break
        while len(chosen) < k_choices and window:
            cand = rng.choices(window, w_weights)[0]
            if all(cand != c for c, _ in chosen):
                chosen.append((cand, v_freq[cand]))
            else:
                break
        book[pw] = chosen
        for cw, _ in chosen:
            codeword_owners[cw].append(pw)

    mean_owners = float(np.mean([len(v) for v in codeword_owners.values()])) if codeword_owners else 0.0
    return book, len(codeword_owners), mean_owners


def encrypt_shared(by, streams, book, R, Qi, Qe, para, beta=1.8, seed=1):
    rng = random.Random(seed)
    its = {k: iter(v) for k, v in streams.items()}
    ptypes, pw = list(para), list(para.values())
    out = {}
    for page, recs in by.items():
        lines = []
        for r in recs:
            n = len(r["words"])
            line = []
            for i in range(n):
                if i == 0 and r["para_start"]:
                    line.append(rng.choices(ptypes, pw)[0])
                    continue
                plain_w = next(its[(r["hand"], r["illus"])])
                cands = book[plain_w]
                prev_last = line[-1][-1] if line else None
                weights = []
                for cw, base_w in cands:
                    flow_w = (R(prev_last, cw[0]) ** beta) if prev_last else 1.0
                    pos_w = k1.pos_factor(cw, i, n, Qi, Qe)
                    weights.append(max(base_w * flow_w * pos_w, 1e-9))
                line.append(rng.choices([cw for cw, _ in cands], weights)[0])
            lines.append(dict(r, words=line))
        out[page] = lines
    return out


def main():
    rng = np.random.default_rng(0)
    k1.emit("K4: Lossy (Many-to-One + Flow) Shared-Codeword Nomenclator + M5 Line Layer")
    k1.emit("Pass bar: within 25% of Voynich on NMI, residual, crossMI, JSDf, with types in [5971, 8079] and h2 in [1.96, 2.26]")
    k1.emit()

    by = k1.layout()
    Qi, Qe, para = k1.line_tables(by)
    R = f3.ratio_table(by)
    g = c2.Gen(by)

    k1.bench("VOYNICH (target)", by, rng)

    streams = k2.plaintext_streams(by, shuffle=False)
    shuf_streams = k2.plaintext_streams(by, shuffle=True)
    allw = [w for v in streams.values() for w in v]

    configs = [
        (7025, 4, 120, 1.5),
        (7025, 6, 180, 1.8),
        (7025, 8, 260, 2.0),
        (7025, 12, 400, 2.2),
    ]
    for pool_cap, k_ch, win, beta in configs:
        book, n_used, mean_col = build_shared_codebook(
            allw, g.freq, pool_cap=pool_cap, k_choices=k_ch, rank_window=win, seed=20261017
        )
        enc = encrypt_shared(by, streams, book, R, Qi, Qe, para, beta=beta, seed=1)
        label = f"K4 k={k_ch:2d} w={win:3d} b={beta:.1f} (col={mean_col:.1f}x)"
        k1.bench(label, enc, rng)

    # Shuffled-plaintext null at the k=6, w=180, b=1.8 setting
    book6, _, mean_col6 = build_shared_codebook(
        allw, g.freq, pool_cap=7025, k_choices=6, rank_window=180, seed=20261017
    )
    enc_null = encrypt_shared(by, shuf_streams, book6, R, Qi, Qe, para, beta=1.8, seed=1)
    k1.bench("K4 k= 6 NULL (shuffled plain)", enc_null, rng)

    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
