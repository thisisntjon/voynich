"""M1: same-column copying test (b1 T2) with physical x-coordinates.

Replaces the word-index "column" proxy of b1_docx_tests.py T2 with the voynichese.com
per-token bounding boxes (tools/boxes.py). For each token on paragraph line n (n>=2 of a
page) with an aligned previous line n-1 on the same page:
  same-column : the token on line n-1 whose horizontal centre is nearest, if |dx| <= 0.5 W
  off-column  : the token on line n-1 with 3 W <= |dx| <= 5 W, the one closest to 4 W
  far         : nearest-centre token on a random aligned paragraph line >= 5 lines away on
                the same page, if |dx| <= 0.5 W
(W = mean token width of the page's aligned paragraph boxes.)  Hit = exact match, edit
distance == 1, or edit <= 1.  Cluster bootstrap over pages for CIs.  Also: hit rate vs
|dx|/W profile for lines n-1, n-2 and far; two nulls (within-line word shuffle with boxes
fixed; previous line replaced by a random line of the page); f57v ring retest.

Run: python m1_coordinates.py  -> results_m1_coordinates.txt
"""
import math
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / "tools"))
import vparse  # noqa: E402
import boxes   # noqa: E402

OUT = HERE / "results_m1_coordinates.txt"
SEED = 20261017
N_BOOT = 1000
N_NULL = 20
BINS = np.arange(0, 6.01, 0.25)
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def lev_le1(a, b):
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) <= 1
    if la > lb:
        a, b = b, a; la, lb = lb, la
    i = j = diff = 0
    while i < la and j < lb:
        if a[i] == b[j]:
            i += 1; j += 1
        else:
            diff += 1; j += 1
            if diff > 1:
                return False
    return True


def ok_word(w):
    return bool(w) and "?" not in w


# ---------------------------------------------------------------- data assembly

def build_pages():
    """pages[folio] -> dict(meta, W, lines=[(zl_line_no, [tok,...]), ...]) paragraph lines
    that aligned; tok = dict(word, cx, cy, w)."""
    recs = vparse.load()
    aligned, stats = boxes.align_all(recs)
    pages = {}
    for folio, pairs in aligned.items():
        plines = []
        meta = None
        widths = []
        for r, ln in pairs:
            if not r["unit"].startswith("P"):
                continue
            meta = meta or dict(lang=r["lang"], illus=r["illus"], hand=r["hand"])
            if not ln["aligned"]:
                continue
            toks = [t for t in ln["tokens"]]
            widths.extend(t["w"] for t in toks)
            plines.append((r["line"], toks))
        if len(plines) >= 2 and widths:
            pages[folio] = dict(meta=meta, W=float(np.mean(widths)), lines=plines)
    return pages, stats


def line_pairs(pages, back=1):
    """(folio, cur_tokens, prev_tokens) for consecutive aligned paragraph lines n, n-back."""
    out = []
    for folio, pg in pages.items():
        by_no = {no: toks for no, toks in pg["lines"]}
        for no, toks in pg["lines"]:
            prev = by_no.get(no - back)
            if prev is None:
                continue
            if np.median([t["cy"] for t in toks]) <= np.median([t["cy"] for t in prev]):
                continue   # ordering sanity: previous line must sit above
            out.append((folio, toks, prev))
    return out


# ---------------------------------------------------------------- core test

def nearest(tok, cands):
    best = None
    for c in cands:
        d = abs(c["cx"] - tok["cx"])
        if best is None or d < best[0]:
            best = (d, c)
    return best


def off_column(tok, cands, W):
    best = None
    for c in cands:
        d = abs(c["cx"] - tok["cx"])
        if 3 * W <= d <= 5 * W and (best is None or abs(d - 4 * W) < abs(best[0] - 4 * W)):
            best = (d, c)
    return best


def score(w, c):
    ex = w == c
    e1 = (not ex) and lev_le1(w, c)
    return ex, e1


def collect(pages, rng, word_of=lambda t: t["word"], prev_of=None):
    """Per-token outcomes. Returns dict(cond -> list of (folio, exact, edit1)) for the
    three conditions, plus the page-cluster keys.  prev_of(folio, no, by_no) overrides the
    previous-line choice (used by the line-swap null)."""
    res = {"same": [], "off": [], "far": [], "off_far": []}
    for folio, pg in pages.items():
        W = pg["W"]
        by_no = {no: toks for no, toks in pg["lines"]}
        nos = sorted(by_no)
        for no in nos:
            cur = by_no[no]
            if prev_of is not None:
                prev = prev_of(folio, no, by_no, rng)
            else:
                prev = by_no.get(no - 1)
            if prev is None:
                continue
            far_nos = [m for m in nos if abs(m - no) >= 5]
            far = by_no[rng.choice(far_nos)] if far_nos else None
            pcands = [t for t in prev if ok_word(word_of(t))]
            fcands = [t for t in far if ok_word(word_of(t))] if far else []
            for tok in cur:
                w = word_of(tok)
                if not ok_word(w) or not pcands:
                    continue
                d, c = nearest(tok, pcands)
                if d <= 0.5 * W:
                    res["same"].append((folio,) + score(w, word_of(c)))
                o = off_column(tok, pcands, W)
                if o:
                    res["off"].append((folio,) + score(w, word_of(o[1])))
                if fcands:
                    d, c = nearest(tok, fcands)
                    if d <= 0.5 * W:
                        res["far"].append((folio,) + score(w, word_of(c)))
                    o = off_column(tok, fcands, W)
                    if o:
                        res["off_far"].append((folio,) + score(w, word_of(o[1])))
    return res


def rates(rows):
    n = len(rows)
    if n == 0:
        return dict(n=0, exact=float("nan"), e1=float("nan"), le1=float("nan"))
    ex = sum(r[1] for r in rows); e1 = sum(r[2] for r in rows)
    return dict(n=n, exact=100 * ex / n, e1=100 * e1 / n, le1=100 * (ex + e1) / n)


def boot(res, rng, n_boot=N_BOOT):
    """Cluster bootstrap over pages. Returns dict(cond -> dict(metric -> (lo, hi))) and
    CIs for the same-off and same-far differences in edit<=1."""
    folios = sorted({r[0] for rows in res.values() for r in rows})
    idx = {f: i for i, f in enumerate(folios)}
    per = {}
    for cond, rows in res.items():
        acc = defaultdict(lambda: np.zeros(3))
        for f, ex, e1 in rows:
            acc[f] += (1, ex, e1)
        M = np.zeros((len(folios), 3))
        for f, v in acc.items():
            M[idx[f]] = v
        per[cond] = M
    draws = {c: [] for c in res}
    diffs = {"same-off": [], "same-far": [], "off-far": [], "off-off_far": [], "column-specific": []}
    for _ in range(n_boot):
        pick = rng.integers(0, len(folios), len(folios))
        est = {}
        for c, M in per.items():
            s = M[pick].sum(0)
            n = max(s[0], 1)
            est[c] = (100 * s[1] / n, 100 * s[2] / n, 100 * (s[1] + s[2]) / n)
            draws[c].append(est[c])
        diffs["same-off"].append(est["same"][2] - est["off"][2])
        diffs["same-far"].append(est["same"][2] - est["far"][2])
        diffs["off-far"].append(est["off"][2] - est["far"][2])
        if "off_far" in est:
            diffs["off-off_far"].append(est["off"][2] - est["off_far"][2])
            diffs["column-specific"].append((est["same"][2] - est["far"][2]) - (est["off"][2] - est["off_far"][2]))
    ci = {}
    for c, d in draws.items():
        a = np.array(d)
        ci[c] = {m: (np.percentile(a[:, k], 2.5), np.percentile(a[:, k], 97.5))
                 for k, m in enumerate(("exact", "e1", "le1"))}
    dci = {k: (np.percentile(v, 2.5), np.percentile(v, 97.5), float(np.mean(np.array(v) <= 0)))
           for k, v in diffs.items() if v}
    return ci, dci


def report_block(title, res, rng, with_ci=True):
    emit(f"\n--- {title} ---")
    emit(f"{'condition':<12}{'n':>7}{'exact%':>9}{'edit=1%':>9}{'edit<=1%':>10}   95% CI (edit<=1)")
    ci = dci = None
    if with_ci and all(len(v) for v in res.values()):
        ci, dci = boot(res, rng)
    for c in ("same", "off", "far", "off_far"):
        if c not in res:
            continue
        r = rates(res[c])
        s = f"{c:<12}{r['n']:>7}{r['exact']:>9.2f}{r['e1']:>9.2f}{r['le1']:>10.2f}"
        if ci:
            lo, hi = ci[c]["le1"]; s += f"   [{lo:.2f}, {hi:.2f}]"
        emit(s)
    rs, ro, rf = rates(res["same"]), rates(res["off"]), rates(res["far"])
    if ro["le1"] and rf["le1"] and rs["n"]:
        emit(f"ratios (edit<=1): same/far = {rs['le1']/rf['le1']:.2f}, same/off = {rs['le1']/ro['le1']:.2f}, "
             f"off/far = {ro['le1']/rf['le1']:.2f}")
    rof = rates(res.get("off_far", []))
    if rof["n"] and rs["n"] and rf["n"] and ro["n"]:
        emit(f"column-specific excess = (same-far) - (off-off_far) = "
             f"{(rs['le1']-rf['le1'])-(ro['le1']-rof['le1']):+.2f} pp  "
             f"[recency at same x {rs['le1']-rf['le1']:+.2f}; recency at 3-5 W offset {ro['le1']-rof['le1']:+.2f}]")
    if dci:
        for k, (lo, hi, p) in dci.items():
            emit(f"diff {k:<15} edit<=1: [{lo:+.2f}, {hi:+.2f}] pp   P(diff<=0) = {p:.3f}")
    return rs, ro, rf


# ---------------------------------------------------------------- profile

def profile(pairs, W_of):
    n = np.zeros(len(BINS) - 1); h = np.zeros(len(BINS) - 1); ex = np.zeros(len(BINS) - 1)
    for folio, cur, prev in pairs:
        W = W_of(folio)
        pc = [t for t in prev if ok_word(t["word"])]
        for tok in cur:
            if not ok_word(tok["word"]):
                continue
            for c in pc:
                d = abs(c["cx"] - tok["cx"]) / W
                if d >= BINS[-1]:
                    continue
                k = min(int(d / 0.25), len(n) - 1)
                n[k] += 1
                e, e1 = score(tok["word"], c["word"])
                h[k] += e or e1; ex[k] += e
    return n, h, ex


def profile_table(prof):
    emit("hit rate (edit<=1 %) by horizontal offset |dx|/W between the token and every token of the "
         "comparison line; diff = n-1 minus far, with ~1 SE")
    emit(f"{'|dx|/W bin':<12}{'n(n-1)':>8}{'n-1':>7}{'n-2':>7}{'far':>7}{'n-1 - far':>14}{'exact n-1':>10}{'exact far':>10}")
    for k in range(len(BINS) - 1):
        (n1, h1, e1), (n2, h2, e2), (nf, hf, ef) = (prof[t] for t in ("n-1", "n-2", "far"))
        if not (n1[k] and n2[k] and nf[k]):
            continue
        r1, r2, rf = 100 * h1[k] / n1[k], 100 * h2[k] / n2[k], 100 * hf[k] / nf[k]
        se = math.sqrt(r1 * (100 - r1) / n1[k] + rf * (100 - rf) / nf[k])
        emit(f"{BINS[k]:.2f}-{BINS[k+1]:.2f}   {int(n1[k]):>8}{r1:>7.2f}{r2:>7.2f}{rf:>7.2f}"
             f"{r1-rf:>+9.2f}+-{se:.2f}{100*e1[k]/n1[k]:>10.2f}{100*ef[k]/nf[k]:>10.2f}")


# ---------------------------------------------------------------- f57v ring

GLYPH_SUBS = [("cth", "T"), ("ckh", "K"), ("cph", "P"), ("cfh", "F"), ("ch", "C"), ("sh", "S"),
              ("aiin", "A"), ("iin", "N"), ("in", "I")]


def glyphs(tok):
    for a, b in GLYPH_SUBS:
        tok = tok.replace(a, b)
    return tok


def f57v_ring(rng):
    emit("\n=== f57v ring retest (boxes ordered by angle) ===")
    recs = [r for r in vparse.load() if r["page"] == "f57v"]
    bx = boxes.load_boxes("f57v")
    if bx is None:
        emit("no boxes for f57v"); return
    lines, st = boxes.align_page(recs, bx)
    emit(f"f57v: boxes {st['n_box']} matched {st['n_matched']} lines {st['n_lines']} aligned {st['n_aligned']}")
    ring = [(r, ln) for r, ln in zip(recs, lines) if r["unit"].startswith("C") and ln["tokens"]]
    allc = [(t["cx"], t["cy"]) for _, ln in ring for t in ln["tokens"]]
    # least-squares circle fit for the centre
    A = np.array([[2 * x, 2 * y, 1] for x, y in allc]); b = np.array([x * x + y * y for x, y in allc])
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx0, cy0 = sol[0], sol[1]
    emit(f"ring centre (circle fit over {len(allc)} C-unit boxes): ({cx0:.0f}, {cy0:.0f})")
    # the sequence aligner attaches ring boxes to the wrong ring where the transcriptions
    # diverge (rare glyphs); re-assign every C-unit box to the ring whose median radius is nearest
    med_r = [float(np.median([math.hypot(t["cx"] - cx0, t["cy"] - cy0) for t in ln["tokens"]]))
             for _, ln in ring]
    pool = [t for _, ln in ring for t in ln["tokens"]]
    reassigned = [[] for _ in ring]
    for t in pool:
        rr = math.hypot(t["cx"] - cx0, t["cy"] - cy0)
        reassigned[min(range(len(ring)), key=lambda i: abs(med_r[i] - rr))].append(t)
    emit("ring radii (median px): " + ", ".join(f"line {r['line']}: {m:.0f}" for (r, _), m in zip(ring, med_r)))
    emit("boxes re-assigned by radius; words are the voynichese reading where the ZL string match failed")
    for (r, ln0), toks in zip(ring, reassigned):
        ln = dict(ln0, tokens=toks, n_box=len(toks))
        if not toks:
            continue
        ang = [math.atan2(t["cy"] - cy0, t["cx"] - cx0) for t in toks]
        rad = [math.hypot(t["cx"] - cx0, t["cy"] - cy0) for t in toks]
        order = sorted(range(len(toks)), key=lambda i: ang[i])
        # rotate so the sequence starts after the largest angular gap (ring start)
        gaps = [(ang[order[(i + 1) % len(order)]] - ang[order[i]]) % (2 * math.pi) for i in range(len(order))]
        start = (max(range(len(order)), key=lambda i: gaps[i]) + 1) % len(order)
        order = order[start:] + order[:start]
        pos = {k: i for i, k in enumerate(sorted(order))}
        mono = sum(1 for a, b2 in zip(order, order[1:]) if pos[b2] == pos[a] + 1)
        words = [toks[i]["word"] for i in order]
        emit(f"\nline {r['line']} unit {r['unit']}: ZL n={ln['n_zl']} boxes={ln['n_box']} matched={ln['n_matched']} "
             f"radius mean {np.mean(rad):.0f} sd {np.std(rad):.0f}; angle order agrees with box order at "
             f"{mono}/{len(toks)-1} steps")
        emit("  tokens by angle: " + " ".join(words))
        if len(words) < 20:
            continue
        # token-level periodicity: fraction of positions i with word[i]==word[i+p]
        emit("  token-level period p -> match rate (exact / edit<=1):")
        best = []
        for p in range(2, len(words) // 2 + 1):
            m = [(words[i] == words[i + p], lev_le1(words[i], words[i + p])) for i in range(len(words) - p)]
            best.append((sum(x for x, _ in m) / len(m), sum(y for _, y in m) / len(m), p))
        for ex, le, p in sorted(best, reverse=True)[:5]:
            emit(f"    p={p:3d}: exact {ex:.2f}  edit<=1 {le:.2f}")
        # glyph level: concatenate collapsed tokens with '.' separators
        g = ".".join(glyphs(w) for w in words)
        emit(f"  glyph string length {len(g)} (collapsed ch/sh/cth/ckh/cph/cfh/aiin/iin/in)")
        ac = []
        for lag in range(2, len(g) // 2):
            ac.append((sum(g[i] == g[i + lag] for i in range(len(g) - lag)) / (len(g) - lag), lag))
        emit("  glyph-level lag -> match rate, top 8: " +
             ", ".join(f"lag {lag}: {v:.2f}" for v, lag in sorted(ac, reverse=True)[:8]))
        # null: shuffle tokens 200 times, record max token-level exact rate over p in 10..30
        mx = []
        pmax = min(30, len(words) // 2)
        for _ in range(200):
            ws = words[:]; rng.shuffle(ws)
            mx.append(max(sum(ws[i] == ws[i + p] for i in range(len(ws) - p)) / (len(ws) - p)
                          for p in range(10, pmax + 1)))
        obs = max(sum(words[i] == words[i + p] for i in range(len(words) - p)) / (len(words) - p)
                  for p in range(10, pmax + 1))
        emit(f"  max exact match rate over p=10..{pmax}: observed {obs:.2f}; token-shuffle null mean "
             f"{np.mean(mx):.2f}, 95th pct {np.percentile(mx, 95):.2f}, P(null>=obs) = {np.mean(np.array(mx) >= obs):.3f}")
        # explicit 4x17 chunks if n == 68
        for per in (13, 17):
            if len(words) >= 3 * per:
                ch = [words[k * per:(k + 1) * per] for k in range(len(words) // per)]
                emit(f"  chunks of {per} (angle order): " + "; ".join(
                    f"chunk {k+1} vs 1 = {sum(a == b2 for a, b2 in zip(ch[0], ch[k]))}/{per}"
                    for k in range(1, len(ch))))


# ---------------------------------------------------------------- main

def main():
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    emit(f"M1 same-column copying with physical x-coordinates  (seed {SEED}, run {stamp})")
    emit("boxes: voynichese.com scrape via Rozanova & Temerev (3-px grid, ~600-px layout)")
    rng = random.Random(SEED)
    nrng = np.random.default_rng(SEED)
    pages, stats = build_pages()

    emit("\n=== alignment ===")
    tb = sum(s["n_box"] for s in stats.values()); tm = sum(s["n_matched"] for s in stats.values())
    tl = sum(s["n_lines"] for s in stats.values()); ta = sum(s["n_aligned"] for s in stats.values())
    ts = sum(s["n_strict"] for s in stats.values())
    emit(f"folios with boxes and ZL text: {len(stats)}; boxes {tb}, string-matched to ZL {tm} ({100*tm/tb:.1f}%)")
    emit(f"ZL lines (all units) {tl}: aligned within 1 token {ta} ({100*ta/tl:.1f}%), "
         f"strict (>= n-1 string matches) {ts} ({100*ts/tl:.1f}%)")
    npl = sum(len(p["lines"]) for p in pages.values())
    ntok = sum(len(t) for p in pages.values() for _, t in p["lines"])
    emit(f"paragraph (P-unit) lines kept: {npl} on {len(pages)} pages, {ntok} tokens; "
         f"mean token width W per page: median {np.median([p['W'] for p in pages.values()]):.1f} px "
         f"(range {min(p['W'] for p in pages.values()):.1f}-{max(p['W'] for p in pages.values()):.1f}); "
         f"3-px grid = {3/np.median([p['W'] for p in pages.values()]):.2f} W")
    emit("per-folio alignment (folio: boxes matched% | lines aligned/total):")
    row = []
    for f in sorted(stats, key=lambda f: (int("".join(ch for ch in f[1:4] if ch.isdigit()) or 0), f)):
        s = stats[f]
        row.append(f"{f}:{100*s['n_matched']/max(s['n_box'],1):.0f}%|{s['n_aligned']}/{s['n_lines']}")
        if len(row) == 6:
            emit("  " + "  ".join(row)); row = []
    if row:
        emit("  " + "  ".join(row))
    low = [f for f, s in stats.items() if s["n_matched"] / max(s["n_box"], 1) < 0.6]
    emit(f"folios with < 60% boxes matched: {len(low)}: {' '.join(sorted(low))}")

    emit("\n=== T2 with coordinates (paragraph lines; prev = line n-1 on the same page) ===")
    emit("word-index version (results_b1.txt T2): same 10.69%  off 8.79%  far 8.80%  (exact 2.57 / 1.96 / 1.94)")
    res = collect(pages, rng)
    report_block("all paragraph text", res, nrng)

    emit("\n=== by section ($I illustration code) ===")
    by_sec = defaultdict(dict)
    for f, pg in pages.items():
        by_sec[pg["meta"]["illus"]][f] = pg
    for sec in sorted(by_sec, key=lambda s: -sum(len(p["lines"]) for p in by_sec[s].values())):
        r = collect(by_sec[sec], random.Random(SEED))
        report_block(f"section I={sec} ({len(by_sec[sec])} pages)", r, nrng, with_ci=len(by_sec[sec]) >= 3)

    emit("\n=== by Currier language ($L) ===")
    by_lang = defaultdict(dict)
    for f, pg in pages.items():
        by_lang[pg["meta"]["lang"]][f] = pg
    for lg in sorted(by_lang):
        r = collect(by_lang[lg], random.Random(SEED))
        report_block(f"language {lg} ({len(by_lang[lg])} pages)", r, nrng)

    emit("\n=== horizontal-offset profile ===")
    W_of = lambda f: pages[f]["W"]
    p1 = line_pairs(pages, 1); p2 = line_pairs(pages, 2)
    prof = {"n-1": profile(p1, W_of), "n-2": profile(p2, W_of)}
    frng = random.Random(SEED + 1)
    pf = []
    for folio, pg in pages.items():
        by_no = {no: t for no, t in pg["lines"]}; nos = sorted(by_no)
        for no in nos:
            fn = [m for m in nos if abs(m - no) >= 5]
            if fn:
                pf.append((folio, by_no[no], by_no[frng.choice(fn)]))
    prof["far"] = profile(pf, W_of)
    profile_table(prof)

    emit("\n=== nulls ===")
    emit("null 1: words shuffled within each line, boxes fixed (20 reps)")
    acc = defaultdict(list)
    for rep in range(N_NULL):
        srng = random.Random(SEED + 100 + rep)
        shuffled = {}
        for f, pg in pages.items():
            nl = []
            for no, toks in pg["lines"]:
                ws = [t["word"] for t in toks]; srng.shuffle(ws)
                nl.append((no, [dict(t, word=w) for t, w in zip(toks, ws)]))
            shuffled[f] = dict(pg, lines=nl)
        r = collect(shuffled, random.Random(SEED + rep))
        for c in r:
            acc[c].append(rates(r[c])["le1"])
    for c in ("same", "off", "far"):
        emit(f"  {c:<6} edit<=1: mean {np.mean(acc[c]):.2f}%  sd {np.std(acc[c]):.2f}  "
             f"range {min(acc[c]):.2f}-{max(acc[c]):.2f}")
    emit(f"  observed same {rates(res['same'])['le1']:.2f}% vs null-1 same max {max(acc['same']):.2f}%")

    emit("null 2: previous line replaced by a random other aligned paragraph line of the page (20 reps)")
    acc2 = defaultdict(list)
    for rep in range(N_NULL):
        def prev_of(folio, no, by_no, rng_, rep=rep):
            others = [m for m in by_no if m != no]
            return by_no[rng_.choice(others)] if others else None
        r = collect(pages, random.Random(SEED + 200 + rep), prev_of=prev_of)
        for c in r:
            acc2[c].append(rates(r[c])["le1"])
    for c in ("same", "off", "far"):
        emit(f"  {c:<6} edit<=1: mean {np.mean(acc2[c]):.2f}%  sd {np.std(acc2[c]):.2f}  "
             f"range {min(acc2[c]):.2f}-{max(acc2[c]):.2f}")
    emit(f"  observed same {rates(res['same'])['le1']:.2f}% vs null-2 same max {max(acc2['same']):.2f}%")

    emit("\n=== secondary: word-index-style multi-candidate version on the same aligned lines ===")
    emit("(same = any of the 3 nearest prev-line tokens within 1.5 W; off = any of 3 tokens nearest to 4 W "
         "within 3-5 W; far = 3 nearest on far line within 1.5 W) - comparable to b1 T2 j-1..j+1 / j+4..j+6")
    res3 = {"same": [], "off": [], "far": []}
    r3 = random.Random(SEED + 7)
    for folio, pg in pages.items():
        W = pg["W"]; by_no = {no: t for no, t in pg["lines"]}; nos = sorted(by_no)
        for no in nos:
            prev = by_no.get(no - 1)
            if prev is None:
                continue
            fn = [m for m in nos if abs(m - no) >= 5]
            far = by_no[r3.choice(fn)] if fn else None
            pc = [t for t in prev if ok_word(t["word"])]
            fc = [t for t in far if ok_word(t["word"])] if far else []
            for tok in by_no[no]:
                w = tok["word"]
                if not ok_word(w) or not pc:
                    continue
                def best3(cands, target, lim):
                    cs = sorted(cands, key=lambda c: abs(abs(c["cx"] - tok["cx"]) - target))[:3]
                    cs = [c for c in cs if abs(abs(c["cx"] - tok["cx"]) - target) <= lim]
                    if not cs:
                        return None
                    ex = any(w == c["word"] for c in cs)
                    return (ex, (not ex) and any(lev_le1(w, c["word"]) for c in cs))
                for cond, cands, target, lim in (("same", pc, 0, 1.5 * W), ("off", pc, 4 * W, W), ("far", fc, 0, 1.5 * W)):
                    s = best3(cands, target, lim) if cands else None
                    if s:
                        res3[cond].append((folio,) + s)
    report_block("multi-candidate", res3, nrng)

    f57v_ring(random.Random(SEED))
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
