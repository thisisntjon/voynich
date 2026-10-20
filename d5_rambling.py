"""D5: 'single disordered/obsessive rambler' signatures.

Builds on (does not duplicate):
  a4/a4b: P(word has exact/d<=1 neighbour in PRECEDING W=10/40 vs far window) ratio.
          D5-1 instead measures FORWARD next-repeat distance distribution (k=1,5,20,100)
          and its excess over a frequency-preserving shuffle.
  b5:     NMF topics vs section/hand/lang (NMI). D5-4 instead measures direct
          rare-word Jaccard between pages as a function of page distance,
          overall and WITHIN Currier language, vs a page-size-preserving shuffle.

Predictions of a single rambler / perseverating glossolalia:
  P1 extreme local perseveration (esp. k=1) far above controls & shuffle,
     decaying quickly with k.
  P2 saturating tiny vocabulary: low Heaps exponent beta, low late-text beta,
     small type count at matched N.
  P3 repeats clustered in bursts (gap CV >> shuffle) OR, in the obsessive
     variant, metronomic (CV << 1); either way unlike topical prose controls.
  P4 no stable long-range topical structure: rare-word overlap for adjacent
     pages ~ far pages ~ shuffled (no distance decay), within language too.
"""
import random
from collections import Counter, defaultdict

import numpy as np

import corpora

KS = [1, 5, 20, 100]
CTRLS = ["latin_caesar", "latin_augustine", "italian_dante"]
RNG = random.Random(42)


def next_gaps(words):
    """Distance to next occurrence of same word (np.inf if none)."""
    nxt = {}
    gaps = np.full(len(words), np.inf)
    for i in range(len(words) - 1, -1, -1):
        w = words[i]
        if w in nxt:
            gaps[i] = nxt[w] - i
        nxt[w] = i
    return gaps


def perseveration(words):
    g = next_gaps(words)
    return {k: float(np.mean(g <= k)) for k in KS}


def heaps(words):
    seen, types = set(), []
    for i, w in enumerate(words, 1):
        seen.add(w)
        if i % 100 == 0 or i == len(words):
            types.append((i, len(seen)))
    ns = np.array([t[0] for t in types], float)
    vs = np.array([t[1] for t in types], float)
    m = ns >= 100
    beta, logk = np.polyfit(np.log(ns[m]), np.log(vs[m]), 1)
    half = ns >= ns[-1] / 2
    beta_late, _ = np.polyfit(np.log(ns[half]), np.log(vs[half]), 1)
    at = {int(n): int(v) for n, v in types if n in (5000, 10000, 20000)}
    return beta, beta_late, len(seen), at


def burstiness(words, topn=50):
    pos = defaultdict(list)
    for i, w in enumerate(words):
        pos[w].append(i)
    top = [w for w, _ in Counter(words).most_common(topn)]
    cvs, bs, means = [], [], []
    for w in top:
        g = np.diff(pos[w]).astype(float)
        if len(g) < 5:
            continue
        cv = g.std() / g.mean()
        cvs.append(cv); means.append(g.mean())
        bs.append((cv - 1) / (cv + 1))  # Goh-Barabasi B: 0=Poisson, >0 bursty
    return float(np.mean(means)), float(np.mean(cvs)), float(np.median(cvs)), float(np.mean(bs))


def jaccard_bins(pages_rare):
    """pages_rare: list of sets in order. Mean Jaccard by page-distance bin."""
    bins = {"d=1": [], "d2-5": [], "d6-20": [], "d>20": []}
    n = len(pages_rare)
    for i in range(n):
        for j in range(i + 1, n):
            d = j - i
            key = "d=1" if d == 1 else "d2-5" if d <= 5 else "d6-20" if d <= 20 else "d>20"
            a, b = pages_rare[i], pages_rare[j]
            if a or b:
                bins[key].append(len(a & b) / len(a | b))
    return {k: (float(np.mean(v)) if v else float("nan")) for k, v in bins.items()}


def rare_pages(page_words, lo=2, hi=10):
    freq = Counter(w for ws in page_words for w in ws)
    rare = {w for w, c in freq.items() if lo <= c <= hi}
    return [set(ws) & rare for ws in page_words]


def main():
    out = []
    def p(s=""):
        out.append(s); print(s)

    vms_lines = corpora.voynich_lines()
    vms = [w for r in vms_lines for w in r["words"]]
    N = len(vms)
    # page aggregation in folio (file) order
    page_order, page_words_d, page_lang = [], {}, {}
    for r in vms_lines:
        pg = r["page"]
        if pg not in page_words_d:
            page_order.append(pg); page_words_d[pg] = []; page_lang[pg] = r["lang"]
        page_words_d[pg].extend(r["words"])
    pages = [page_words_d[pg] for pg in page_order if len(page_words_d[pg]) >= 20]
    page_sizes = [len(ws) for ws in pages]
    langs_kept = [page_lang[pg] for pg in page_order if len(page_words_d[pg]) >= 20]
    med_page = int(np.median(page_sizes))

    texts = {"VMS": vms}
    for c in CTRLS:
        texts[c] = corpora.control(c)[:N]  # matched length
    shuf = vms[:]; RNG.shuffle(shuf)
    texts["VMS-shuffled"] = shuf

    p("D5 RAMBLING SIGNATURES  (controls truncated to VMS length)")
    p(f"VMS paragraph tokens N={N} types={len(set(vms))} pages(>=20 tok)={len(pages)} median page={med_page} tok")
    for name, w in texts.items():
        p(f"  {name:16} N={len(w)} types={len(set(w))}")
    p("\nPrior (not duplicated): a4b VMS W=10 exact-local/far=1.69 (controls 0.96-1.53); "
      "b5 NMF NMI(section)~0.28-0.38 >> perm-null, i.e. SOME page-level structure exists.")

    # ---- 1 perseveration decay
    p("\n[1] PERSEVERATION: P(same word recurs within next k tokens)")
    p(f"{'text':16} " + " ".join(f"k={k:<6}" for k in KS) + "  excess@k5/shuf* k=1/k=100")
    pers = {}
    for name, w in texts.items():
        pers[name] = perseveration(w)
    for name in texts:
        r = pers[name]
        p(f"{name:16} " + " ".join(f"{r[k]:.4f} " for k in KS) +
          f"  {r[5]/pers['VMS-shuffled'][5]:.2f}            {r[1]/r[100]:.3f}")
    p("*self-ratio=1 for shuffled row. k=1 = immediate reduplication.")

    # ---- 2 Heaps
    p("\n[2] VOCABULARY GROWTH (Heaps V=K*N^beta, log-log fit N>=100; folio/order order)")
    p(f"{'text':16} {'beta':>6} {'beta_late(2nd half)':>20} {'V@5k':>6} {'V@10k':>6} {'V@20k':>6} {'V@full':>7}")
    hp = {}
    for name, w in texts.items():
        b, bl, vfull, at = heaps(w); hp[name] = (b, bl, vfull)
        p(f"{name:16} {b:6.3f} {bl:20.3f} {at.get(5000,'-'):>6} {at.get(10000,'-'):>6} {at.get(20000,'-'):>6} {vfull:7d}")

    # ---- 3 burstiness
    p("\n[3] BURSTINESS: inter-repeat gaps of top-50 words (CV=std/mean; B=(CV-1)/(CV+1), 0=Poisson)")
    p(f"{'text':16} {'mean_gap':>9} {'meanCV':>7} {'medCV':>6} {'meanB':>6}")
    bu = {}
    for name, w in texts.items():
        bu[name] = burstiness(w)
        mg, mcv, medcv, mb = bu[name]
        p(f"{name:16} {mg:9.1f} {mcv:7.3f} {medcv:6.3f} {mb:6.3f}")

    # ---- 4 long-range coherence
    p("\n[4] LONG-RANGE COHERENCE: rare-word (global freq 2-10) Jaccard between pages by page distance")
    hdr = f"{'text':26} {'d=1':>7} {'d2-5':>7} {'d6-20':>7} {'d>20':>7} {'adj/far':>8}"
    p(hdr)
    jb = {}
    rp = rare_pages(pages); jb["VMS"] = jaccard_bins(rp)
    for lang in ("A", "B"):
        sub = [pages[i] for i in range(len(pages)) if langs_kept[i] == lang]
        if len(sub) >= 10:
            jb[f"VMS lang{lang} only (n={len(sub)})"] = jaccard_bins(rare_pages(sub))
    # shuffled null: same page sizes, tokens permuted (avg of 20)
    acc = defaultdict(list)
    flat = [w for ws in pages for w in ws]
    for s in range(20):
        rng = random.Random(100 + s); f = flat[:]; rng.shuffle(f)
        sp, idx = [], 0
        for sz in page_sizes:
            sp.append(f[idx:idx + sz]); idx += sz
        for k, v in jaccard_bins(rare_pages(sp)).items():
            acc[k].append(v)
    jb["VMS shuffled-pages null"] = {k: float(np.mean(v)) for k, v in acc.items()}
    for c in CTRLS:  # pseudo-pages of median VMS page size
        w = texts[c]
        chunks = [w[i:i + med_page] for i in range(0, len(w) - med_page + 1, med_page)]
        jb[c] = jaccard_bins(rare_pages(chunks))
    for name, r in jb.items():
        p(f"{name:26} {r['d=1']:7.4f} {r['d2-5']:7.4f} {r['d6-20']:7.4f} {r['d>20']:7.4f} {r['d=1']/r['d>20']:8.2f}")

    # ---- verdicts (computed from measured values)
    p("\nVERDICTS vs 'single disordered/obsessive rambler' predictions")
    v, s = pers["VMS"], pers["VMS-shuffled"]
    ctrl_k1 = max(pers[c][1] for c in CTRLS); ctrl_k5 = max(pers[c][5] for c in CTRLS)
    p(f"P1 perseveration: VMS k=1 {v[1]:.4f} vs shuffled {s[1]:.4f} ({v[1]/s[1]:.2f}x), vs max control {ctrl_k1:.4f} ({v[1]/ctrl_k1:.2f}x); "
      f"k=5 {v[5]:.4f} vs shuf {s[5]:.4f} ({v[5]/s[5]:.2f}x), max ctrl {ctrl_k5:.4f} ({v[5]/ctrl_k5:.2f}x); "
      f"k=100 excess {v[100]/s[100]:.2f}x. -> {'SUPPORTED at k=1 specifically (immediate reduplication is the outlier; by k=5 VMS is near the top control)' if v[1]/s[1]>1.5 and v[1]>ctrl_k1*3 else 'NOT extreme vs controls/shuffle (see numbers)'}; "
      f"decay k1->k100 excess {v[1]/s[1]:.2f}->{v[100]/s[100]:.2f} {'(localised, rambling-like)' if v[1]/s[1]>v[100]/s[100] else '(not localised)'}")
    b, bl, vf = hp["VMS"]
    ctrl_b = [hp[c][0] for c in CTRLS]; ctrl_bl = [hp[c][1] for c in CTRLS]
    matched = [c for c in CTRLS if len(texts[c]) >= N]  # caesar corpus is shorter than VMS
    ctrl_v = [hp[c][2] for c in matched]
    p(f"P2 vocab saturation: VMS beta={b:.3f} (controls {min(ctrl_b):.3f}-{max(ctrl_b):.3f}), beta_late={bl:.3f} (controls {min(ctrl_bl):.3f}-{max(ctrl_bl):.3f}), "
      f"types@N={vf} (length-matched controls {min(ctrl_v)}-{max(ctrl_v)}; caesar exhausted at {len(texts['latin_caesar'])} tok). "
      f"-> {'REFUTED as saturation: overall beta is only marginally lowest and beta_late is the HIGHEST, i.e. new types still arrive fastest late in the book (partly A->B dialect turnover)' if bl>=max(ctrl_bl) else 'SUPPORTED: slowest/saturating growth' if b<=min(ctrl_b) and bl<=min(ctrl_bl) else 'MIXED (see numbers)'}")
    mg, mcv, medcv, mb = bu["VMS"]; smcv = bu["VMS-shuffled"][1]
    ctrl_cv = [bu[c][1] for c in CTRLS]
    p(f"P3 burstiness: VMS meanCV={mcv:.3f} medCV={medcv:.3f} B={mb:.3f} vs shuffled CV={smcv:.3f}, controls CV {min(ctrl_cv):.3f}-{max(ctrl_cv):.3f}. "
      f"-> {'MORE bursty than every control (consistent with topical clustering AND with perseverative bursts; does not separate them)' if mcv>max(ctrl_cv) else 'BURSTY within control range' if mcv>=min(ctrl_cv) else 'LESS bursty than all controls'}; "
      f"{'not metronomic (CV>>shuffle)' if mcv>smcv*1.2 else 'near-random spacing'}")
    r, rn = jb["VMS"], jb["VMS shuffled-pages null"]
    p(f"P4 long-range coherence: VMS Jaccard adj={r['d=1']:.4f} far={r['d>20']:.4f} ratio={r['d=1']/r['d>20']:.2f}; shuffled adj={rn['d=1']:.4f} far={rn['d>20']:.4f} ratio={rn['d=1']/rn['d>20']:.2f}; "
      f"adj excess over null {r['d=1']/rn['d=1']:.2f}x, far excess {r['d>20']/rn['d>20']:.2f}x. "
      f"-> {'REFUTED: real distance-decaying topical locality (consistent with b5)' if r['d=1']/r['d>20']>1.3 and r['d=1']>rn['d=1']*1.3 else 'SUPPORTED/flat: no decay beyond null (rambling-like)'}"
      f" (check within-lang rows above for A/B confound)")
    p("\nNote: EVA word types are the unit throughout; controls are surface word forms at matched N. "
      "P1/P3 local clustering can also arise from self-citation/copying (a4/b4), so P1 alone does not isolate 'rambling'.")

    open("results_d5.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
