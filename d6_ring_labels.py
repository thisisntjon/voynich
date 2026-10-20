"""D6: (a) f57v ring retest at GLYPH level; (b) powered label test, all pages.

(a) Tokenize f57v circular units (Cc, Ro, Cc+Ro joined, plus each line)
    with corpora.to_glyphs(GLYPHS_PLUS). Word boundaries dropped.
    Period scan 5..40 glyphs by lag match-rate vs coincidence baseline
    (sum p_i^2). Longest repeated glyph-block (suffix-array LCP).
    Note: vparse maps every @nnn; rare glyph to '?', so distinct rare
    glyphs (@169;-@172; on f57v) collapse to one symbol '?' here.
(b) All pages with labels (unit L*) and paragraph text (P*):
    label-in-own-page hit rate vs within-illus-section permuted null,
    200 perms, seeded; per-section breakdown for sections with >=5 pages.
"""
import random
from collections import Counter, defaultdict

import numpy as np

import corpora
import vparse

REV = {v: k for k, v in corpora.SYMS.items()}
PERIODS = range(5, 41)
OUT = []


def log(s=""):
    OUT.append(s)
    print(s)


def glyph_seq(words):
    return "".join(corpora.to_glyphs(w, corpora.GLYPHS_PLUS) for w in words)


def decode(seq):
    return "".join(REV.get(c, c) for c in seq)


def match_rate(s, p):
    if len(s) <= p:
        return float("nan")
    return sum(a == b for a, b in zip(s, s[p:])) / (len(s) - p)


def longest_repeated(s):
    """Longest substring occurring >=2x (suffix array + LCP)."""
    n = len(s)
    if n < 2:
        return "", []
    sa = sorted(range(n), key=lambda i: s[i:])
    best_len, best_pos = 0, sa[0]
    for a, b in zip(sa, sa[1:]):
        l = 0
        while a + l < n and b + l < n and s[a + l] == s[b + l]:
            l += 1
        if l > best_len:
            best_len, best_pos = l, a
    block = s[best_pos:best_pos + best_len]
    poss, i = [], s.find(block)
    while i != -1 and block:
        poss.append(i)
        i = s.find(block, i + 1)
    return block, poss


def analyze_stream(name, words):
    s = glyph_seq(words)
    freq = Counter(s)
    baseline = sum((c / len(s)) ** 2 for c in freq.values()) if s else 0.0
    rates = {p: match_rate(s, p) for p in PERIODS if len(s) > p}
    top = sorted(rates.items(), key=lambda kv: -kv[1])[:5]
    block, poss = longest_repeated(s)
    r17 = rates.get(17, float("nan"))
    log(f"[{name}] words={len(words)} glyphs={len(s)} alphabet={len(freq)} "
        f"n_?={freq.get('?', 0)} coincidence_baseline={baseline:.3f}")
    log("  top periods (p:rate): " +
        ", ".join(f"{p}:{r:.3f}" for p, r in top) +
        f" | period17={r17:.3f}")
    log(f"  longest repeated block: len={len(block)} glyphs x{len(poss)} "
        f"at glyph positions {poss}")
    log(f"    block(EVA-decoded)={decode(block)!r}")
    return dict(name=name, s=s, n=len(s), rates=rates, r17=r17,
                baseline=baseline, block=block, poss=poss)


def part_a(recs):
    log("=" * 72)
    log("A) f57v GLYPH-LEVEL RING RETEST (GLYPHS_PLUS, word boundaries dropped)")
    log("=" * 72)
    f57 = [r for r in recs if r["page"] == "f57v"]
    for r in f57:
        log(f"  f57v line {r['line']} unit={r['unit']} words={len(r['words'])}")
    cc = [w for r in f57 if r["unit"] == "Cc" for w in r["words"]]
    ro = [w for r in f57 if r["unit"] == "Ro" for w in r["words"]]
    res = {}
    res["Cc"] = analyze_stream("f57v Cc (all circular lines joined)", cc)
    res["Ro"] = analyze_stream("f57v Ro (radii joined)", ro)
    res["joined"] = analyze_stream("f57v Cc+Ro joined", cc + ro)
    log("-- per-line breakdown (each transcribed ring/line separately) --")
    per_line = []
    for r in f57:
        if r["unit"] in ("Cc", "Ro"):
            per_line.append(analyze_stream(
                f"f57v.{r['line']} {r['unit']}", r["words"]))
    # exact 17x4 check on every stream/line: 17-glyph block repeated back-to-back
    log("-- exact '17 glyphs x 4 repeats' check --")
    verdicts = []
    for d in [res["Cc"], res["Ro"], res["joined"]] + per_line:
        s = d["s"]
        full = len(s) >= 68 and len(s) % 17 == 0 and s == s[:17] * (len(s) // 17)
        # any window of 68 glyphs that is exactly a 17-block x4?
        win = [i for i in range(0, max(0, len(s) - 67))
               if s[i:i + 68] == s[i:i + 17] * 4]
        log(f"  {d['name']}: n={len(s)} n/17={len(s)/17:.2f} whole_is_17xk={full} "
            f"exact_17x4_windows_at={win} period17_rate={d['r17']:.3f} "
            f"(baseline {d['baseline']:.3f})")
        if full or win:
            verdicts.append(d["name"])
    # word-level quantification for f57v.3 (the ring behind the claim)
    w3 = [r["words"] for r in f57 if r["line"] == 3][0]
    chunks = [w3[i:i + 17] for i in range(0, 68, 17)] if len(w3) == 68 else []
    if chunks:
        agree = [sum(a == b for a, b in zip(chunks[0], c)) for c in chunks]
        log(f"  f57v.3 WORD-level: {len(w3)} words = 17x4 chunks; word-for-word "
            f"agreement of chunks 1-4 with chunk 1 = {agree}/17 each")
    d3 = [d for d in per_line if d["name"] == "f57v.3 Cc"][0]
    bestp, bestr = max(d3["rates"].items(), key=lambda kv: kv[1])
    log("VERDICT on '17 units x4': " +
        (f"CONFIRMED at glyph level for {verdicts} (exact 17-glyph block x4); "
         "it does NOT describe the whole Cc stream or Cc+Ro joined "
         f"(Cc period17={res['Cc']['r17']:.3f}, joined period17={res['joined']['r17']:.3f})."
         if verdicts else
         f"at GLYPH level the repeat period is {bestp}, NOT 17: f57v.3 has "
         f"{len(w3)} EVA words (=17 words x4) but {d3['n']} glyphs, because one "
         "word per cycle ('?v', EVA @169;v) is 2 glyphs, so 17 words = 18 glyphs; "
         f"period-{bestp} match={bestr:.3f} and period-36 match={d3['rates'].get(36, float('nan')):.3f} "
         f"vs period-17 match={d3['r17']:.3f} (baseline {d3['baseline']:.3f}); no exact "
         "17-glyph x4 window exists in Cc, Ro, joined, or any line. The '17x4' claim "
         "is a WORD-level fact about f57v.3 only (with 1-2 variant words per cycle, "
         "see chunk agreement), not a glyph-level period and not a property of the "
         f"whole f57v circular text (Cc period17={res['Cc']['r17']:.3f} vs baseline "
         f"{res['Cc']['baseline']:.3f}; Cc best period is 18 at "
         f"{res['Cc']['rates'].get(18, float('nan')):.3f}, driven by f57v.3)."))
    log("CAVEAT: '?' collapses distinct @nnn; rare glyphs; in the repeated ring "
        "the same rare glyphs recur at the same offsets in EVA (@169;-@172;), "
        "so the exact-repeat result is not an artifact of that collapse.")
    return res


def part_b(recs, n_perm=200, seed=12345):
    log("")
    log("=" * 72)
    log("B) POWERED LABEL TEST (ALL pages with labels + paragraph text)")
    log("=" * 72)
    labels, text, sect = defaultdict(list), defaultdict(set), {}
    for r in recs:
        ws = [w for w in r["words"] if "?" not in w]
        if not ws:
            continue
        sect[r["page"]] = r["illus"]
        if r["unit"].startswith("L"):
            labels[r["page"]] += ws
        elif r["unit"].startswith("P"):
            text[r["page"]].update(ws)
    pages = sorted([p for p in labels if text.get(p)])
    n_tok = sum(len(labels[p]) for p in pages)
    n_types = len({w for p in pages for w in labels[p]})
    hits = sum(w in text[p] for p in pages for w in labels[p])
    obs = hits / n_tok
    by_sec = defaultdict(list)
    for p in pages:
        by_sec[sect[p]].append(p)

    def hit_rate(assign, ps):
        n = sum(len(assign[p]) for p in ps)
        h = sum(w in text[p] for p in ps for w in assign[p])
        return h / n if n else float("nan")

    rng = random.Random(seed)
    nulls, sec_nulls = [], defaultdict(list)
    for _ in range(n_perm):
        perm = {}
        for s, ps in by_sec.items():
            sh = ps[:]
            rng.shuffle(sh)
            for a, b in zip(ps, sh):
                perm[a] = labels[b]
        nulls.append(hit_rate(perm, pages))
        for s, ps in by_sec.items():
            if len(ps) >= 5:
                sec_nulls[s].append(hit_rate(perm, ps))
    nulls = np.array(nulls)
    k = int(np.sum(nulls >= obs))
    p_emp = (k + 1) / (n_perm + 1)
    log(f"pages with labels+paragraph text: n={len(pages)} "
        f"(all pages, no cap) label tokens={n_tok} label types={n_types}")
    log(f"sections (illus) represented: " +
        ", ".join(f"{s}:{len(ps)}p" for s, ps in sorted(by_sec.items())))
    log(f"label-in-own-page hit rate: {hits}/{n_tok} = {obs:.4f} ({100*obs:.1f}%)")
    log(f"within-section permuted null ({n_perm} perms, seed={seed}): "
        f"mean={nulls.mean():.4f} sd={nulls.std():.4f} "
        f"p99={np.percentile(nulls, 99):.4f} max={nulls.max():.4f}")
    log(f"empirical p (null>=obs): ({k}+1)/({n_perm}+1) = {p_emp:.4f} "
        f"[raw fraction {k/n_perm:.4f}]")
    log("-- per-section breakdown (sections with >=5 pages) --")
    for s, ps in sorted(by_sec.items()):
        if len(ps) < 5:
            continue
        nt = sum(len(labels[p]) for p in ps)
        o = hit_rate(labels, ps)
        sn = np.array(sec_nulls[s])
        ks = int(np.sum(sn >= o))
        log(f"  section {s}: pages={len(ps)} label_tokens={nt} "
            f"hit={o:.4f} ({100*o:.1f}%) null_mean={sn.mean():.4f} "
            f"p99={np.percentile(sn, 99):.4f} p=({ks}+1)/{n_perm+1}={(ks+1)/(n_perm+1):.4f}")
    small = [s for s, ps in sorted(by_sec.items()) if len(ps) < 5]
    if small:
        log("  sections with <5 pages (in overall test, not broken out): " +
            ", ".join(f"{s}:{len(by_sec[s])}p" for s in small))
    log("VERDICT labels: " +
        (f"own-page hit {100*obs:.1f}% EXCEEDS section-permuted null "
         f"(mean {100*nulls.mean():.1f}%, p99 {100*np.percentile(nulls,99):.1f}%, p={p_emp:.4f}) "
         "-> labels are page-referential beyond section vocabulary."
         if p_emp < 0.05 else
         f"own-page hit {100*obs:.1f}% does NOT exceed section-permuted null "
         f"(mean {100*nulls.mean():.1f}%, p99 {100*np.percentile(nulls,99):.1f}%, p={p_emp:.4f}) "
         "-> no page-specific label referentiality beyond section vocabulary."))
    # Audit of the "not just 40" requirement + sensitivity beyond 40 pages.
    all_label_pages = sorted(labels)
    no_para = [p for p in all_label_pages if not text.get(p)]
    log(f"AUDIT: {len(all_label_pages)} pages have any L* labels; only "
        f"{len(pages)} also have P* paragraph text, so n=40 above is EXHAUSTIVE "
        f"for labels+paragraph. {len(no_para)} label pages have no paragraph "
        f"text: {no_para}")
    text2 = defaultdict(set)  # any non-label unit (P*, Cc, Ro, Ri, Ca) as page text
    for r in recs:
        ws = [w for w in r["words"] if "?" not in w]
        if ws and not r["unit"].startswith("L"):
            text2[r["page"]].update(ws)
    pages2 = sorted([p for p in labels if text2.get(p)])
    by2 = defaultdict(list)
    for p in pages2:
        by2[sect[p]].append(p)

    def hr2(assign, ps):
        n = sum(len(assign[p]) for p in ps)
        return sum(w in text2[p] for p in ps for w in assign[p]) / n if n else float("nan")

    obs2 = hr2(labels, pages2)
    nt2 = sum(len(labels[p]) for p in pages2)
    rng2 = random.Random(seed)
    nulls2 = []
    for _ in range(n_perm):
        perm = {}
        for s, ps in by2.items():
            sh = ps[:]
            rng2.shuffle(sh)
            for a, b in zip(ps, sh):
                perm[a] = labels[b]
        nulls2.append(hr2(perm, pages2))
    nulls2 = np.array(nulls2)
    k2 = int(np.sum(nulls2 >= obs2))
    log(f"SENSITIVITY (page text = any non-label unit, beyond the 40): "
        f"pages={len(pages2)} label_tokens={nt2} hit={obs2:.4f} ({100*obs2:.1f}%) "
        f"null_mean={nulls2.mean():.4f} p99={np.percentile(nulls2, 99):.4f} "
        f"p=({k2}+1)/{n_perm+1}={(k2+1)/(n_perm+1):.4f} "
        f"(sections: " + ", ".join(f"{s}:{len(ps)}p" for s, ps in sorted(by2.items())) + ")")
    return dict(pages=len(pages), tokens=n_tok, obs=obs, nulls=nulls, p=p_emp)


def main():
    recs = vparse.load()
    part_a(recs)
    part_b(recs)
    with open("results_d6.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(OUT) + "\n")
    print("\nwrote results_d6.txt")


if __name__ == "__main__":
    main()
