"""Q1 (Top-10 #9): label <-> image-class crib test v2.
Prior tests (a3/D6) asked label-in-own-page-text (null/marginal). This asks
the crib question properly: do label WORDS associate with what they label?
Image class proxy = IVTFF label unit (Lz zodiac, Lf figure, Ls star,
Ln nymph, Lt tube/pool, Lc circle, Lp plant, L0 other) + illustration code.
Tests (all with permutation nulls, seed 20261017):
 A repeat concentration: pairs of same label type sharing unit class,
   vs free-shuffled and within-illus-shuffled unit assignments.
 B held-out: predict unit class from word (page-half split), accuracy +
   log-loss vs majority baseline and shuffled-word control.
 C zodiac positions: Lz label repeats at same within-page line index
   across zodiac pages vs index-permuted null.
Run: uv run python q1_label_crib.py -> results_q1.txt
"""
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import vparse

OUT = Path(__file__).parent / "results_q1.txt"
SEED = 20261017
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def z_of(obs, nulls):
    m, sd = float(np.mean(nulls)), float(np.std(nulls)) or 1e-9
    p = (1 + sum(x >= obs for x in nulls)) / (len(nulls) + 1)
    return m, (obs - m) / sd, p


def main():
    recs = vparse.load()
    lab = [r for r in recs if r["unit"].startswith("L")]
    toks = [(w, r["unit"], r["illus"], r["page"], r["line"])
            for r in lab for w in r["words"] if "?" not in w]
    emit(f"Q1 label crib: {len(lab)} label lines, {len(toks)} tokens, "
         f"{len(set(t[0] for t in toks))} types")
    emit(f"units: {Counter(t[1] for t in toks).most_common()}")
    rng = random.Random(SEED)

    # --- A: repeat concentration by unit class ---
    byword = defaultdict(list)
    for i, t in enumerate(toks):
        byword[t[0]].append(i)
    pairs = [(i, j) for idxs in byword.values() if len(idxs) > 1
             for a, i in enumerate(idxs) for j in idxs[a + 1:]]
    def frac_same(unit_of):
        return float(np.mean([unit_of[i] == unit_of[j] for i, j in pairs])) if pairs else float("nan")
    units = [t[1] for t in toks]
    obs = frac_same(units)
    free = []
    for _ in range(200):
        u = units[:]; rng.shuffle(u); free.append(frac_same(u))
    m, z, p = z_of(obs, free)
    emit(f"A repeat-in-same-unit: obs {obs:.3f} vs free-shuffle {m:.3f} (z={z:+.1f}, p={p:.3f}, pairs={len(pairs)})")
    # within-illus shuffle (controls section vocabulary)
    illus_idx = defaultdict(list)
    for i, t in enumerate(toks):
        illus_idx[t[2]].append(i)
    win = []
    for _ in range(200):
        u = units[:]
        for idxs in illus_idx.values():
            vals = [u[i] for i in idxs]
            rng.shuffle(vals)
            for i, v in zip(idxs, vals):
                u[i] = v
        win.append(frac_same(u))
    m2, z2, p2 = z_of(obs, win)
    emit(f"A vs within-illus shuffle: {m2:.3f} (z={z2:+.1f}, p={p2:.3f})")

    # --- B: held-out unit prediction from word ---
    pages = sorted(set(t[3] for t in toks))
    rng.shuffle(pages)
    half = set(pages[:len(pages) // 2])
    train = [t for t in toks if t[3] in half]
    test = [t for t in toks if t[3] not in half]
    word_unit = defaultdict(Counter)
    prior = Counter()
    for w, u, *_ in train:
        word_unit[w][u] += 1
        prior[u] += 1
    classes = sorted(prior)
    maj = prior.most_common(1)[0][0]
    def predict(w):
        return word_unit[w].most_common(1)[0][0] if w in word_unit else maj
    acc = float(np.mean([predict(w) == u for w, u, *_ in test]))
    base = float(np.mean([u == maj for _, u, *_ in test]))
    seen = [t for t in test if t[0] in word_unit]
    acc_seen = float(np.mean([predict(w) == u for w, u, *_ in seen])) if seen else float("nan")
    emit(f"B predict unit from word (page-half held-out): acc {acc:.3f} "
         f"(seen-words {acc_seen:.3f}, n_seen={len(seen)}/{len(test)}) vs majority {base:.3f}")

    # --- C: zodiac Lz positional repeats ---
    zpages = defaultdict(list)
    for r in lab:
        if r["unit"] == "Lz":
            zpages[r["page"]].append(r)
    for p_ in zpages:
        zpages[p_].sort(key=lambda r: r["line"])
    pos_words = defaultdict(list)  # position index -> words across pages
    allw = Counter()
    for p_, rs in zpages.items():
        for k, r in enumerate(rs):
            for w in r["words"]:
                if "?" not in w:
                    pos_words[k].append(w)
                    allw[w] += 1
    def pos_repeat_rate(pw):
        hits = tot = 0
        for ws in pw.values():
            c = Counter(ws)
            hits += sum(v * (v - 1) // 2 for v in c.values())
            tot += len(ws) * (len(ws) - 1) // 2
        return hits / tot if tot else float("nan")
    obs_c = pos_repeat_rate(pos_words)
    flat = [(k, w) for k, ws in pos_words.items() for w in ws]
    null_c = []
    for _ in range(200):
        ws_only = [w for _, w in flat]
        rng.shuffle(ws_only)
        pw = defaultdict(list)
        for (k, _), w in zip(flat, ws_only):
            pw[k].append(w)
        null_c.append(pos_repeat_rate(pw))
    m3, z3, p3 = z_of(obs_c, null_c)
    emit(f"C zodiac same-position repeat rate: obs {obs_c:.4f} vs permuted {m3:.4f} "
         f"(z={z3:+.1f}, p={p3:.3f}; {len(zpages)} zodiac pages)")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    emit("Wrote results_q1.txt")


if __name__ == "__main__":
    main()
