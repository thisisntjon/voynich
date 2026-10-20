"""M5: anatomy of line-initial and line-final words.

Every generator with a "p at line start" rule misses the line-start profile
(results_c2.txt, G_RESULTS.md). This script asks what line-initial and
line-final words actually ARE, with within-line-shuffle nulls, for all
paragraph text and separately for Currier A and B:

 1. prefix-strip: is a line-initial token "marker glyph + attested mid-line word"?
 2. suffix-strip mirror for line-final tokens (m, g, am, ag; and m -> usual finals)
 3. are line-initial tokens otherwise ordinary (length, suffix, mid-line freq, hapax)?
 4. word 2 of each line, and paragraph-initial vs other line-initial words
 5. first-glyph entropy / gallows share by word index 1..8 and from the end 1..4
 6. verdict lines

Seed 20261017. Does not modify any existing file.
Writes results_m5_line_anatomy.txt.
"""
import math
import random
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np

import corpora
import vparse

SEED = 20261017
NREP = 100          # within-line shuffle reps for nulls
HERE = Path(__file__).parent
OUT = HERE / "results_m5_line_anatomy.txt"

UNITS = sorted(corpora.GLYPHS, key=len, reverse=True)   # cth ckh cph cfh ch sh
GALLOWS = set("ptkf")
INIT_CLASSES = ["p", "t", "k", "f", "y", "d", "s", "o"]

lines_out = []


def say(s=""):
    print(s)
    lines_out.append(s)


# ----------------------------------------------------------------- data ----
def load_lines():
    """Paragraph lines with page/lang/hand and a paragraph-start flag.

    vparse.load drops the IVTFF '<%>' paragraph-start marker, so the raw file
    is re-read with the same regexes and the same cleaner.
    """
    meta = {}
    recs = []
    for raw in vparse.DATA.read_text(encoding="ascii", errors="replace").splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        m = vparse.PAGE_RE.match(raw)
        if m:
            meta = dict(vparse.VAR_RE.findall(m.group(2)))
            meta["page"] = m.group(1)
            continue
        m = vparse.LINE_RE.match(raw)
        if not m:
            continue
        page, n, mark, unit, text = m.groups()
        if not unit.startswith("P"):
            continue
        words = vparse.clean(text)
        words = [w for w in words if "?" not in w]      # same convention as corpora.voynich_lines
        if not words:
            continue
        recs.append(dict(page=page, line=int(n), mark=mark, unit=unit,
                         lang=meta.get("L", "?"), hand=meta.get("H", "?"),
                         para_start=("<%>" in text), para_end=("<$>" in text),
                         words=words))
    return recs


def units(w):
    """Split an EVA word into glyph units (ch, sh, cth... as one unit)."""
    out, i = [], 0
    while i < len(w):
        for u in UNITS:
            if w.startswith(u, i):
                out.append(u); i += len(u); break
        else:
            out.append(w[i]); i += 1
    return out


def entropy(c):
    n = sum(c.values())
    return -sum(v / n * math.log2(v / n) for v in c.values() if v) if n else float("nan")


def jsd(p, q):
    keys = set(p) | set(q)
    P = np.array([p.get(k, 0) for k in keys], float); P /= P.sum()
    Q = np.array([q.get(k, 0) for k in keys], float); Q /= Q.sum()
    M = (P + Q) / 2
    def kl(a, b):
        m = a > 0
        return float(np.sum(a[m] * np.log2(a[m] / b[m])))
    return (kl(P, M) + kl(Q, M)) / 2


def positions(lines):
    """first tokens, last tokens, mid tokens, second tokens of lines with >=3 words."""
    first, last, mid, second = [], [], [], []
    for ws in lines:
        if len(ws) < 3:
            continue
        first.append(ws[0]); last.append(ws[-1]); second.append(ws[1])
        mid.extend(ws[1:-1])
    return first, last, mid, second


def shuffled(lines, rng):
    out = []
    for ws in lines:
        ws = ws[:]; rng.shuffle(ws); out.append(ws)
    return out


def fmt_null(vals):
    a = np.array(vals, float)
    return f"{a.mean():.3f}±{a.std():.3f}"


# ------------------------------------------------------------- 1. strip ----
def strip_rates(first, midset):
    """Per first-glyph class: share of tokens whose 1-unit / 2-unit / either
    remainder is an attested mid-line type. Returns {class: (n, r1, r2, rany)}."""
    res = {}
    for cls in INIT_CLASSES + ["gallows", "all"]:
        if cls == "gallows":
            toks = [w for w in first if w[0] in GALLOWS]
        elif cls == "all":
            toks = first
        else:
            toks = [w for w in first if w[0] == cls]
        n = len(toks)
        if n == 0:
            res[cls] = (0, float("nan"), float("nan"), float("nan")); continue
        r1 = r2 = ra = 0
        for w in toks:
            u = units(w)
            s1 = "".join(u[1:]); s2 = "".join(u[2:]) if len(u) > 2 else ""
            a1 = bool(s1) and s1 in midset
            a2 = bool(s2) and s2 in midset
            r1 += a1; r2 += a2; ra += (a1 or a2)
        res[cls] = (n, r1 / n, r2 / n, ra / n)
    return res


def section_strip(lines, rng):
    first, last, mid, second = positions(lines)
    midset = set(mid)
    obs = strip_rates(first, midset)
    # null A: within-line shuffle (line-initial slot filled by a random word of the line)
    nullacc = {cls: ([], [], []) for cls in obs}
    for _ in range(NREP):
        f2, l2, m2, s2 = positions(shuffled(lines, rng))
        r = strip_rates(f2, set(m2))
        for cls in obs:
            for k in range(3):
                if r[cls][0] > 0:
                    nullacc[cls][k].append(r[cls][k + 1])
    # null B: the same strip applied to mid-line tokens of the same first glyph
    # (remainder attested among mid-line types other than the token itself is
    # not required; a mid-line token's own remainder is checked against the
    # same mid-line type set)
    midrates = strip_rates(mid, midset)
    say("  note: the per-class shuffle null is near-degenerate for p (most p-tokens are line-initial, so the shuffled line-initial p-tokens are largely"
        " the same tokens); the informative baselines are the 'all' row null and the mid-line same-class column.")
    say("  class   n_init  1-strip  [shuffle null]  2-strip  [null]   any  [null]   | mid-line same-class: n  1-strip  2-strip  any")
    for cls in INIT_CLASSES + ["gallows", "all"]:
        n, r1, r2, ra = obs[cls]
        nn = nullacc[cls]
        mn, m1, m2_, ma = midrates[cls]
        if n == 0:
            say(f"  {cls:7} {n:6}  (none)"); continue
        say(f"  {cls:7} {n:6}  {r1:.3f}    [{fmt_null(nn[0])}]     {r2:.3f}    [{fmt_null(nn[1])}]  {ra:.3f} [{fmt_null(nn[2])}]"
            f"   | {mn:6}  {m1:.3f}    {m2_:.3f}    {ma:.3f}")
    # detail for p: what the remainders are, and how frequent they are mid-line
    midc = Counter(mid)
    for cls in ["p", "t", "y", "d"]:
        toks = [w for w in first if w[0] == cls]
        rem = Counter("".join(units(w)[1:]) for w in toks)
        att = [(r, c) for r, c in rem.most_common() if r in midset]
        medfreq = np.median([midc[r] for r, c in rem.items() if r in midset]) if att else float("nan")
        say(f"  {cls}-initial remainders: {len(rem)} types, attested {len(att)} types; median mid-line count of attested remainder {medfreq:.0f};"
            f" top: {', '.join(f'{r}({c})' for r, c in att[:8])}")
    return obs, nullacc, midrates


# ----------------------------------------------------------- 2. suffix ----
FINAL_REPL = ["n", "in", "iin", "r", "l", "y", "s", "d"]


def suffix_rates(last, midset):
    out = {}
    for cls in ["m", "g", "am", "ag", "y", "n", "l", "r", "all"]:
        if cls == "all":
            toks = last
        else:
            toks = [w for w in last if w.endswith(cls) and len(w) > len(cls)]
        n = len(toks)
        if n == 0:
            out[cls] = (0, float("nan"), {}); continue
        k = len(cls)
        strip_ok = sum(w[:-k] in midset for w in toks) / n
        repl = {}
        if cls in ("m", "g", "am", "ag"):
            for r in FINAL_REPL:
                repl[r] = sum((w[:-1] + r) in midset for w in toks) / n
            # 'am' -> 'a'+r is the same as m->r; add 'am'/'ag' -> 'y' and -> 'o'
            if cls in ("am", "ag"):
                for r in ["y", "o", "aiin", "ar", "al"]:
                    repl["am->" + r] = sum((w[:-2] + r) in midset for w in toks) / n
        out[cls] = (n, strip_ok, repl)
    return out


def section_suffix(lines, rng):
    first, last, mid, second = positions(lines)
    midset = set(mid)
    obs = suffix_rates(last, midset)
    nullacc = {cls: {"strip": [], "repl": {}} for cls in obs}
    for _ in range(NREP):
        f2, l2, m2, s2 = positions(shuffled(lines, rng))
        r = suffix_rates(l2, set(m2))
        for cls in obs:
            if r[cls][0] > 0:
                nullacc[cls]["strip"].append(r[cls][1])
                for k, v in r[cls][2].items():
                    nullacc[cls]["repl"].setdefault(k, []).append(v)
    midrates = suffix_rates(mid, midset)
    say("  note: as in section 1, the per-ending shuffle null is near-degenerate for m/g (most m/g tokens are line-final); compare with the 'all' row and the mid-line column.")
    say("  ending   n_final  strip-attested [shuffle null]  | mid-line same ending: n  strip-attested")
    for cls in ["m", "g", "am", "ag", "y", "n", "l", "r", "all"]:
        n, s, repl = obs[cls]
        if n == 0:
            say(f"  {cls:7} {n:7}  (none)"); continue
        say(f"  {cls:7} {n:7}  {s:.3f}          [{fmt_null(nullacc[cls]['strip'])}]      | {midrates[cls][0]:6}  {midrates[cls][1]:.3f}")
    for cls in ["m", "g"]:
        n, s, repl = obs[cls]
        if n == 0:
            continue
        say(f"  {cls}-final: replace the final '{cls}' by a usual final and test attestation mid-line (observed [shuffle null]):")
        say("    " + "  ".join(f"{cls}->{r}: {repl[r]:.3f} [{fmt_null(nullacc[cls]['repl'].get(r, [float('nan')]))}]" for r in FINAL_REPL))
        best = max(FINAL_REPL, key=lambda r: repl[r])
        anyrep = sum(any((w[:-1] + r) in midset for r in FINAL_REPL) for w in last if w.endswith(cls) and len(w) > 1) / n
        say(f"    best single replacement {cls}->{best} {repl[best]:.3f}; any of the {len(FINAL_REPL)} replacements attested: {anyrep:.3f}")
        toks = [w for w in last if w.endswith(cls) and len(w) > 1]
        c = Counter(toks)
        say("    top " + cls + "-final tokens: " + ", ".join(f"{w}({k})" for w, k in c.most_common(10)))
    return obs, nullacc


# ---------------------------------------------------------- 3. ordinary ----
def token_stats(toks, midc, allc, midset):
    n = len(toks)
    if n == 0:
        return None
    L = np.mean([len(w) for w in toks])
    midfreq = np.array([midc[w] for w in toks], float)
    return dict(n=n, len=L,
                mid_zero=float(np.mean(midfreq == 0)),
                mid_med=float(np.median(midfreq)),
                mid_logmean=float(np.mean(np.log10(midfreq + 1))),
                hapax=float(np.mean([allc[w] == 1 for w in toks])),
                last=Counter(w[-1] for w in toks),
                suffix2=Counter(w[-2:] for w in toks))


def section_ordinary(lines, rng):
    first, last, mid, second = positions(lines)
    allc = Counter(w for ws in lines for w in ws)
    midc = Counter(mid)
    midset = set(mid)
    groups = {
        "line-initial (all)": first,
        "line-initial p/t/f/k": [w for w in first if w[0] in GALLOWS],
        "line-initial y/d/s": [w for w in first if w[0] in "yds"],
        "line-initial other": [w for w in first if w[0] not in GALLOWS and w[0] not in "yds"],
        "line-final (all)": last,
        "line-final m/g": [w for w in last if w[-1] in "mg"],
        "mid-line (reference)": mid,
    }
    obs = {k: token_stats(v, midc, allc, midset) for k, v in groups.items()}
    # shuffle null for the line-initial (all) and line-final (all) rows
    nulls = {"line-initial (all)": [], "line-final (all)": []}
    for _ in range(NREP):
        f2, l2, m2, s2 = positions(shuffled(lines, rng))
        mc2 = Counter(m2)
        nulls["line-initial (all)"].append(token_stats(f2, mc2, allc, set(m2)))
        nulls["line-final (all)"].append(token_stats(l2, mc2, allc, set(m2)))
    midref = obs["mid-line (reference)"]
    say("  group                       n   mean_len  type_never_mid  median_mid_count  mean_log10(mid+1)  hapax   JSD(last glyph vs mid)  JSD(last 2 vs mid)")
    for k, s in obs.items():
        if s is None:
            say(f"  {k:26} 0"); continue
        jl = jsd(s["last"], midref["last"]) if k != "mid-line (reference)" else 0.0
        j2 = jsd(s["suffix2"], midref["suffix2"]) if k != "mid-line (reference)" else 0.0
        say(f"  {k:26} {s['n']:6}  {s['len']:.2f}      {s['mid_zero']:.3f}           {s['mid_med']:4.0f}             {s['mid_logmean']:.3f}         {s['hapax']:.3f}    {jl:.4f}                  {j2:.4f}")
        if k in nulls:
            ns = nulls[k]
            say(f"    shuffle null              {'':6}  {fmt_null([x['len'] for x in ns])}  {fmt_null([x['mid_zero'] for x in ns])}     {fmt_null([x['mid_med'] for x in ns])}        {fmt_null([x['mid_logmean'] for x in ns])}   {fmt_null([x['hapax'] for x in ns])}"
                f"  {fmt_null([jsd(x['last'], midref['last']) for x in ns])}            {fmt_null([jsd(x['suffix2'], midref['suffix2']) for x in ns])}")
    # suffix (last glyph) table for line-initial vs mid
    say("  last glyph of line-initial tokens vs mid-line (share, ratio):")
    fi, mi = obs["line-initial (all)"]["last"], midref["last"]
    nf, nm = sum(fi.values()), sum(mi.values())
    say("    " + "  ".join(f"{g}:{fi[g]/nf:.3f}/{mi[g]/nm:.3f}(x{(fi[g]/nf)/max(mi[g]/nm,1e-9):.2f})" for g, _ in mi.most_common(8)))
    # is the line-initial type a hapax more often? also for the remainder of p/t words
    return obs, nulls


# ------------------------------------------------------- 4. word 2, para ----
def glyph_table(label, c, ref, nref=None):
    n = sum(c.values()); nr = sum(ref.values())
    top = [g for g, _ in (c + ref).most_common(10)]
    say(f"    {label:28} n={n:5}  " + "  ".join(f"{g}:{c[g]/n:.3f}(x{(c[g]/n)/max(ref[g]/nr,1e-9):.2f})" for g in top))


def section_word2_para(recs, lines, rng):
    first, last, mid, second = positions(lines)
    midc = Counter(w[0] for w in mid)
    fc = Counter(w[0] for w in first)
    sc = Counter(w[0] for w in second)
    j1, j2 = jsd(fc, midc), jsd(sc, midc)
    n1 = []; n2 = []
    for _ in range(NREP):
        f2, l2, m2, s2 = positions(shuffled(lines, rng))
        mc = Counter(w[0] for w in m2)
        n1.append(jsd(Counter(w[0] for w in f2), mc)); n2.append(jsd(Counter(w[0] for w in s2), mc))
    say(f"  first-glyph JSD vs mid-line: word 1 = {j1:.4f} [null {fmt_null(n1)}]   word 2 = {j2:.4f} [null {fmt_null(n2)}]")
    gal = lambda c: sum(c[g] for g in GALLOWS) / sum(c.values())
    say(f"  gallows-initial share: word1 {gal(fc):.3f}  word2 {gal(sc):.3f}  mid {gal(midc):.3f};  p-initial: word1 {fc['p']/sum(fc.values()):.3f} word2 {sc['p']/sum(sc.values()):.3f} mid {midc['p']/sum(midc.values()):.3f}")
    say("  first-glyph shares (ratio vs mid-line):")
    glyph_table("word 2", sc, midc)
    # paragraph-initial vs other line-initial
    pf = Counter(); of = Counter(); pw = []; ow = []
    for r in recs:
        ws = r["words"]
        if len(ws) < 3:
            continue
        if r["para_start"]:
            pf[ws[0][0]] += 1; pw.append(ws[0])
        else:
            of[ws[0][0]] += 1; ow.append(ws[0])
    say(f"  paragraph-initial lines n={sum(pf.values())}, other line-initial n={sum(of.values())}")
    glyph_table("paragraph-initial word 1", pf, midc)
    glyph_table("other line-initial word 1", of, midc)
    say(f"    gallows share: para-initial {gal(pf):.3f}  other-initial {gal(of):.3f}  mid {gal(midc):.3f};"
        f"  p/f share: para {(pf['p']+pf['f'])/sum(pf.values()):.3f}  other {(of['p']+of['f'])/sum(of.values()):.3f}  mid {(midc['p']+midc['f'])/sum(midc.values()):.3f}")
    say(f"    JSD(first glyph) vs mid: para-initial {jsd(pf, midc):.4f}  other line-initial {jsd(of, midc):.4f}  para vs other {jsd(pf, of):.4f}")
    # strip-attestation of para-initial vs other-initial
    midset = set(mid)
    for lab, toks in [("para-initial", pw), ("other line-initial", ow)]:
        r = strip_rates(toks, midset)
        say(f"    {lab:20} 1-strip attested: p {r['p'][1]:.3f} (n={r['p'][0]})  t {r['t'][1]:.3f} (n={r['t'][0]})  gallows {r['gallows'][1]:.3f}  all {r['all'][1]:.3f};  type never mid-line: {np.mean([w not in midset for w in toks]):.3f}")
    return j1, j2, gal(fc), gal(sc), gal(midc), pf, of


# --------------------------------------------------------- 5. positions ----
def section_shape(lines, rng):
    long = [ws for ws in lines if len(ws) >= 8]
    say(f"  lines with >= 8 words: {len(long)}")
    def table(ls):
        rows = {}
        for idx in range(8):
            c = Counter(ws[idx][0] for ws in ls)
            n = sum(c.values())
            rows[f"w{idx+1}"] = (entropy(c), sum(c[g] for g in GALLOWS) / n, c["p"] / n, c["y"] / n, c["d"] / n, c["q"] / n, c["c"] / n,
                                 sum(1 for ws in ls if ws[idx][-1] in "mg") / n)
        for k in range(1, 5):
            c = Counter(ws[-k][0] for ws in ls)
            n = sum(c.values())
            rows[f"end-{k}"] = (entropy(c), sum(c[g] for g in GALLOWS) / n, c["p"] / n, c["y"] / n, c["d"] / n, c["q"] / n, c["c"] / n,
                                sum(1 for ws in ls if ws[-k][-1] in "mg") / n)
        return rows
    obs = table(long)
    nulls = [table(shuffled(long, rng)) for _ in range(min(NREP, 50))]
    say("  index   H(first glyph) [null]     gallows%  [null]     p%     y%     d%     q%    ch/c%  | ends m/g% [null]")
    for k, v in obs.items():
        H = [t[k][0] for t in nulls]; G = [t[k][1] for t in nulls]; M = [t[k][7] for t in nulls]
        say(f"  {k:6}  {v[0]:.3f} [{fmt_null(H)}]   {v[1]:.3f} [{fmt_null(G)}]   {v[2]:.3f}  {v[3]:.3f}  {v[4]:.3f}  {v[5]:.3f}  {v[6]:.3f}  | {v[7]:.3f} [{fmt_null(M)}]")
    return obs


# ---------------------------------------------------------- 6. verdict ----
def section_verdict(lines, rng, strip_obs, strip_mid, suf_obs, suf_null):
    first, last, mid, second = positions(lines)
    midset = set(mid)
    midc = Counter(w[0] for w in mid)
    n = len(first)
    attested = [w for w in first if w in midset]
    unatt = [w for w in first if w not in midset]
    pre_ok = [w for w in unatt if ("".join(units(w)[1:]) in midset) or (len(units(w)) > 2 and "".join(units(w)[2:]) in midset)]
    neither = len(unatt) - len(pre_ok)
    # null for the three shares and for the JSD among attested
    na, np_, nn, nj = [], [], [], []
    for _ in range(NREP):
        f2, l2, m2, s2 = positions(shuffled(lines, rng))
        ms = set(m2); mc = Counter(w[0] for w in m2)
        a = [w for w in f2 if w in ms]; u = [w for w in f2 if w not in ms]
        p = [w for w in u if ("".join(units(w)[1:]) in ms) or (len(units(w)) > 2 and "".join(units(w)[2:]) in ms)]
        na.append(len(a) / len(f2)); np_.append(len(p) / len(f2)); nn.append((len(u) - len(p)) / len(f2))
        nj.append(jsd(Counter(w[0] for w in a), mc))
    j_att = jsd(Counter(w[0] for w in attested), midc)
    j_all = jsd(Counter(w[0] for w in first), midc)
    gal_att = sum(w[0] in GALLOWS for w in attested) / max(len(attested), 1)
    gal_mid = sum(midc[g] for g in GALLOWS) / sum(midc.values())
    p_att = sum(w[0] == "p" for w in attested) / max(len(attested), 1)
    p_mid = midc["p"] / sum(midc.values())
    say(f"  line-initial tokens n={n}: type attested mid-line {len(attested)/n:.3f} [null {fmt_null(na)}];"
        f" unattested but 1-/2-unit prefix strip attested {len(pre_ok)/n:.3f} [null {fmt_null(np_)}]; neither {neither/n:.3f} [null {fmt_null(nn)}]")
    cond = len(pre_ok) / max(len(unatt), 1)
    cond_null = [p / (p + q) for p, q in zip(np_, nn) if p + q > 0]
    say(f"  rarity-controlled: among line-initial tokens NOT attested mid-line, share whose prefix-strip remainder is attested = {cond:.3f} [null {fmt_null(cond_null)}]"
        f"  (line-initial tokens are rarer types, so the unconditional excess above is partly rarity)")
    # token-weighted frequency of the 1-unit remainder, line-initial vs mid-line tokens of the same class
    midc_tok = Counter(mid)
    for cls in ["p", "t", "y", "d"]:
        a = [math.log10(midc_tok["".join(units(w)[1:])] + 1) for w in first if w[0] == cls]
        b = [math.log10(midc_tok["".join(units(w)[1:])] + 1) for w in mid if w[0] == cls]
        if a and b:
            say(f"  mean log10(mid-line count+1) of the 1-unit remainder, {cls}-initial: line-initial {np.mean(a):.3f} (n={len(a)}) vs mid-line {np.mean(b):.3f} (n={len(b)});"
                f" whole mid-line tokens {np.mean([math.log10(midc_tok[w]+1) for w in mid]):.3f}")
    say(f"  among line-initial tokens whose type IS attested mid-line: first-glyph JSD vs mid {j_att:.4f} [null {fmt_null(nj)}] (all line-initial {j_all:.4f});"
        f" gallows share {gal_att:.3f} vs mid {gal_mid:.3f}; p share {p_att:.3f} vs mid {p_mid:.3f}")
    # same for p specifically
    pt = [w for w in first if w[0] == "p"]
    if pt:
        pa = sum(w in midset for w in pt) / len(pt)
        pp = sum((w not in midset) and ("".join(units(w)[1:]) in midset) for w in pt) / len(pt)
        say(f"  p-initial line-initial tokens n={len(pt)}: type attested mid-line {pa:.3f}; unattested-but-remainder-attested {pp:.3f}; neither {1-pa-pp:.3f}")
    # line-final
    m = len(last)
    att_l = [w for w in last if w in midset]
    unatt_l = [w for w in last if w not in midset]
    suf_ok = [w for w in unatt_l if (w[:-1] in midset) or any((w[:-1] + r) in midset for r in FINAL_REPL)]
    nal, nsl, nnl, njl = [], [], [], []
    lastc = Counter(w[-1] for w in last); midl = Counter(w[-1] for w in mid)
    for _ in range(NREP):
        f2, l2, m2, s2 = positions(shuffled(lines, rng))
        ms = set(m2); ml = Counter(w[-1] for w in m2)
        a = [w for w in l2 if w in ms]; u = [w for w in l2 if w not in ms]
        p = [w for w in u if (w[:-1] in ms) or any((w[:-1] + r) in ms for r in FINAL_REPL)]
        nal.append(len(a) / len(l2)); nsl.append(len(p) / len(l2)); nnl.append((len(u) - len(p)) / len(l2))
        njl.append(jsd(Counter(w[-1] for w in a), ml))
    j_att_l = jsd(Counter(w[-1] for w in att_l), midl)
    say(f"  line-final tokens n={m}: type attested mid-line {len(att_l)/m:.3f} [null {fmt_null(nal)}];"
        f" unattested but final-glyph strip/replace attested {len(suf_ok)/m:.3f} [null {fmt_null(nsl)}]; neither {(len(unatt_l)-len(suf_ok))/m:.3f} [null {fmt_null(nnl)}]")
    say(f"  among line-final tokens whose type IS attested mid-line: last-glyph JSD vs mid {j_att_l:.4f} [null {fmt_null(njl)}] (all line-final {jsd(lastc, midl):.4f});"
        f" m/g share {sum(w[-1] in 'mg' for w in att_l)/max(len(att_l),1):.3f} vs mid {sum(midl[g] for g in 'mg')/sum(midl.values()):.3f}")
    cond_l = len(suf_ok) / max(len(unatt_l), 1)
    cond_l_null = [p / (p + q) for p, q in zip(nsl, nnl) if p + q > 0]
    say(f"  rarity-controlled: among line-final tokens NOT attested mid-line, share attested after final-glyph strip/replace = {cond_l:.3f} [null {fmt_null(cond_l_null)}]")
    mt = [w for w in last if w[-1] == "m" and len(w) > 1]
    m_r = sum((w[:-1] + "r") in midset for w in mt) / max(len(mt), 1)
    mm = [w for w in mid if w[-1] == "m" and len(w) > 1]
    m_r_mid = sum((w[:-1] + "r") in midset for w in mm) / max(len(mm), 1)
    return dict(att=len(attested) / n, att_null=np.mean(na), pre=len(pre_ok) / n, pre_null=np.mean(np_),
                cond=cond, cond_null=np.mean(cond_null),
                j_att=j_att, j_att_null=np.mean(nj), j_all=j_all,
                p_strip=strip_obs["p"][1], p_strip_mid=strip_mid["p"][1], n_p=strip_obs["p"][0], n_p_mid=strip_mid["p"][0],
                att_l=len(att_l) / m, att_l_null=np.mean(nal), suf=len(suf_ok) / m, suf_null=np.mean(nsl),
                cond_l=cond_l, cond_l_null=np.mean(cond_l_null), m_r=m_r, m_r_mid=m_r_mid, n_m=len(mt), n_m_mid=len(mm),
                j_att_l=j_att_l, j_att_l_null=np.mean(njl), j_all_l=jsd(lastc, midl))


# ------------------------------------------------------------------ main ----
def run(label, recs, rng):
    lines = [r["words"] for r in recs]
    ntok = sum(len(ws) for ws in lines)
    say("=" * 100)
    say(f"SUBSET {label}: {len(recs)} paragraph lines, {ntok} tokens, {sum(len(ws) >= 3 for ws in lines)} lines with >= 3 words, "
        f"{sum(r['para_start'] for r in recs)} paragraph-initial lines")
    say("=" * 100)
    say("\n--- 1. prefix strip: line-initial token minus its first 1 or 2 glyph units; is the remainder an attested mid-line type? ---")
    s_obs, s_null, s_mid = section_strip(lines, rng)
    say("\n--- 2. suffix strip: line-final token minus its final glyph(s); and final m/g replaced by a usual final ---")
    f_obs, f_null = section_suffix(lines, rng)
    say("\n--- 3. are line-initial / line-final tokens otherwise ordinary? ---")
    section_ordinary(lines, rng)
    say("\n--- 4. word 2 of each line, and paragraph-initial vs other line-initial words ---")
    section_word2_para(recs, lines, rng)
    say("\n--- 5. shape of the edge effect: lines with >= 8 words, by word index and from the end ---")
    section_shape(lines, rng)
    say("\n--- 6. decomposition: ordinary word (attested mid-line) / marker+ordinary word / neither ---")
    v = section_verdict(lines, rng, s_obs, s_mid, f_obs, f_null)
    say()
    return v


def main():
    t0 = time.time()
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    say(f"M5 line anatomy  (seed {SEED}, NREP={NREP} within-line shuffles, run {stamp})")
    say("data: ZL3b-n paragraph lines (units P*), tokens containing '?' dropped, positions on lines with >= 3 words;"
        " 'mid-line' = word 2..n-1; paragraph start = IVTFF <%> marker in the raw locus text")
    say("glyph units for stripping: cth ckh cph cfh ch sh count as one unit, every other EVA letter is one unit")
    recs = load_lines()
    say(f"loaded {len(recs)} paragraph lines; Currier lang counts {dict(Counter(r['lang'] for r in recs))}")
    verd = {}
    for label, sub in [("ALL", recs), ("Currier A", [r for r in recs if r["lang"] == "A"]),
                       ("Currier B", [r for r in recs if r["lang"] == "B"])]:
        verd[label] = run(label, sub, random.Random(SEED))

    say("=" * 100)
    say("VERDICT")
    say("=" * 100)
    for label, v in verd.items():
        say(f"[{label}]")
        vs = v["j_att"] / v["j_all"]
        pex = v["cond"] - v["cond_null"]
        say(f"  (a) line-initial. VOCABULARY: restricting to line-initial tokens whose type is an ordinary mid-line word keeps {vs:.0%} of the"
            f" first-glyph JSD ({v['j_att']:.3f} of {v['j_all']:.3f}; null {v['j_att_null']:.3f}); {v['att']:.1%} of line-initial tokens are such ordinary types (null {v['att_null']:.1%}).")
        say(f"      PREFIX MARKER: among line-initial tokens never seen mid-line, {v['cond']:.1%} become an attested word after removing 1-2 leading glyphs"
            f" (null {v['cond_null']:.1%}, excess {pex*100:+.1f} pp); line-initial p-words: 1-glyph strip attested {v['p_strip']:.1%} (n={v['n_p']})"
            f" vs {v['p_strip_mid']:.1%} for mid-line p-words (n={v['n_p_mid']}).")
        if vs >= 0.6 and pex < 0.10 and v["p_strip"] <= v["p_strip_mid"] + 0.05:
            say("      -> mostly VOCABULARY (ordinary words chosen with a line-start profile); the prefix-marker component is small and"
                " line-initial p-words are no more 'p + ordinary word' than mid-line p-words.")
        elif vs >= 0.6:
            say("      -> BOTH: vocabulary dominant, with a measurable prefix-marker component.")
        else:
            say("      -> mostly PREFIX MARKER on ordinary words.")
        vsl = v["j_att_l"] / v["j_all_l"]
        sex = v["cond_l"] - v["cond_l_null"]
        say(f"  (b) line-final. VOCABULARY: ordinary attested types keep {vsl:.0%} of the last-glyph JSD ({v['j_att_l']:.3f} of {v['j_all_l']:.3f}; null {v['j_att_l_null']:.3f});"
            f" {v['att_l']:.1%} of line-final tokens are ordinary types (null {v['att_l_null']:.1%}).")
        say(f"      FINAL FLOURISH: among line-final tokens never seen mid-line, {v['cond_l']:.1%} become attested after stripping/replacing the final glyph"
            f" (null {v['cond_l_null']:.1%}, excess {sex*100:+.1f} pp); m-final words with m->r attested: line-final {v['m_r']:.1%} (n={v['n_m']})"
            f" vs mid-line m-words {v['m_r_mid']:.1%} (n={v['n_m_mid']}).")
        if vsl >= 0.6 and sex < 0.10:
            say("      -> mostly VOCABULARY: specific recurring m/g types are placed line-finally; they are not decomposable above the baseline.")
        elif vsl >= 0.6:
            say("      -> BOTH: vocabulary dominant, with a measurable final-flourish component (unattested m/g tokens resolve to attested stems above null).")
        else:
            say("      -> mostly FINAL FLOURISH on ordinary words.")
    say(f"\nruntime {time.time()-t0:.1f} s")
    OUT.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
