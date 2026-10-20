#!/usr/bin/env python
"""
S65: drawing-gap ('<->') robustness of A1 and A5, a space-fitting test, and Steckley's BEFORE length.

PRE-REGISTRATION (frozen in s65_drawing_gap_robustness.prereg.sha256 before the real run; the stub
covers this file and its local imports tools/ivtff_to_meta.py, tools/boxes.py and vparse.py).

Source: workflow/research/literature-2026-10-18.md section 2 (Steckley & Steckley 2024) and
follow-ups 4 and 5; results_s35_physical_codicology_quire_network.txt part 2C (n = 744 gaps).

DATA. ZL3b = data/ZL3b-n.txt, RF1b = data/external/voynich-nu-ivtff/RF1b-er.txt,
IT2a = data/external/voynich-nu-ivtff/IT2a-n.txt; P* loci; tokens cleaned with
tools/ivtff_to_meta.py clean() (the scoreboard meta rules) applied per '<->' segment, tokens containing
'?' dropped.  Each line keeps its segment structure.  A token is "gap-adjacent" if it is the last
kept token of a segment followed by '<->' or the first kept token of a segment preceded by '<->'.

(a) A1 = line-initial first-glyph JSD excess (a2_position.stats feature w[0]: JSD(first glyph of
    line-initial words, first glyph of mid-line words) over lines with >= 3 tokens) minus the mean of
    a within-line shuffle null.  A5 = s21 within-line lag-1 word-length (EVA chars) Moran I minus
    the median of the within-line shuffle null.  Versions: BASE (segments joined, = meta.json lines),
    EXCL (gap-adjacent tokens removed, line kept), SPLIT (each non-empty segment is its own line).
    Point estimates on all pages, null 200 shuffles.  Interval: 500 draws of 80 % of pages without
    replacement, null 20 shuffles per draw (the same permutation serves both statistics); 95 % =
    2.5/97.5 percentiles of the per-draw excess.
    CALL: "A1/A5 robust to drawing gaps" iff on all three files, for EXCL and SPLIT, both A1 and A5
    excess intervals have lower bound > 0, AND the EXCL point estimate of each is within +/-25 % of
    BASE.  Otherwise the failing (file, version, statistic, condition) items are named.
(b) Space fitting on ZL3b with the Rozanova voynichese boxes (tools/boxes.align_all on vparse
    records, s35 part 2 alignment).  Lines used: P lines that are aligned AND n_box == n_zl (word k
    = box k) with box centres increasing in x.  Glyph length: EVA with cth/ckh/cph/cfh/ch/sh as one
    glyph.  Page glyph width g = median over used tokens of box w / glyph length.
    Page right margin M = 95th percentile of the right edges of the last box of used lines.
    For a target word t with previous word t-1 in the same segment:
      PRE-GAP  t = last word before '<->'; boundary = left edge of the first word after the gap
               (the obstacle edge itself is not in the boxes; this is an upper bound);
      MARGIN   t = last word of the line; boundary = M;
      MID      t not first/last of line, not gap-adjacent; boundary = left edge of word t+1.
    S = (boundary - right edge of word t-1) / g.  OLS slope of glyph length on S per class;
    OBSTACLE = PRE-GAP + MARGIN pooled.  95 % intervals: 1000 page-cluster bootstrap draws.
    CALL: "length tracks space" iff the OBSTACLE slope interval is above 0 AND the interval of
    (OBSTACLE slope - MID slope) lies above 0; else "no space fitting".  If fewer than 60 % of ZL3b
    pages with P text are aligned (>= 50 % of their P lines usable), part (b) is "not testable".
(c) Steckley replication on ZL3b, descriptive: mean length (EVA chars and glyphs) of BEFORE words
    (last token before an internal '<->', both sides non-empty) vs MIDDLE words (interior tokens,
    not gap-adjacent, of lines without the <%> paragraph-start mark); all hands and hand 1 Herbal;
    95 % page-cluster bootstrap (1000) interval of the difference.

Usage: python s65_drawing_gap_robustness.py --make-fixture
       python s65_drawing_gap_robustness.py --fixture runs/s65/fixture.txt
       python s65_drawing_gap_robustness.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import boxes as box_mod  # noqa: E402
import ivtff_to_meta  # noqa: E402
import vparse  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

SELF = ROOT / "s65_drawing_gap_robustness.py"
STUB = ROOT / "s65_drawing_gap_robustness.prereg.sha256"
OUT_REAL = ROOT / "results_s65.txt"
RUNDIR = ROOT / "runs" / "s65"
LOCAL = [SELF, ROOT / "tools" / "ivtff_to_meta.py", ROOT / "tools" / "boxes.py", ROOT / "vparse.py"]
SEED = 20261018
N_SUB = 500
FRAC = 0.80
N_NULL_SUB = 20
N_NULL_FULL = 200
N_BOOT = 1000
SOURCES = [("ZL3b", ROOT / "data" / "ZL3b-n.txt"),
           ("RF1b", ROOT / "data" / "external" / "voynich-nu-ivtff" / "RF1b-er.txt"),
           ("IT2a", ROOT / "data" / "external" / "voynich-nu-ivtff" / "IT2a-n.txt")]
META = {"ZL3b": "ZL3b_eva.meta.json", "RF1b": "RF1b.meta.json", "IT2a": "IT2a.meta.json"}
GLYPH_RE = re.compile(r"cth|ckh|cph|cfh|ch|sh|.")

LOG: list[str] = []


def emit(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return time.strftime("%Y-%m-%d %H:%M:%S") + " (time.strftime)"


def stub_match() -> str:
    if not STUB.exists():
        return "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    return "True" if want and not bad else f"False (mismatch: {', '.join(bad) or 'empty stub'})"


def glen(w: str) -> int:
    return len(GLYPH_RE.findall(w))


# ------------------------------------------------------------------ parsing
def parse_segments(path: Path) -> list[dict]:
    """Pages of P lines; each line = dict(segs=[[kept tokens], ...], top=bool, raw_segs_all=[[all]])."""
    pages, cur, meta = [], None, {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        m = ivtff_to_meta.PAGE_RE.match(raw)
        if m:
            meta = dict(ivtff_to_meta.VAR_RE.findall(m.group(2)))
            cur = dict(id=m.group(1), hand=meta.get("H", "?"), lang=meta.get("L", "?"),
                       sec=meta.get("I", "?"), lines=[])
            pages.append(cur)
            continue
        m = ivtff_to_meta.LINE_RE.match(raw)
        if not m or cur is None:
            continue
        page, n, _c, unit, text = m.groups()
        if not unit.startswith("P") or page != cur["id"]:
            continue
        top = "<%>" in text
        t = re.sub(r"<![^>]*>", "", text)
        segs_all = [ivtff_to_meta.clean(s) for s in t.split("<->")]
        segs = [[w for w in s if "?" not in w] for s in segs_all]
        if sum(len(s) for s in segs) == 0:
            continue
        cur["lines"].append(dict(segs=segs, top=top, line=int(n), unit=unit))
    return [p for p in pages if p["lines"]]


def line_tokens(ln):
    """Joined tokens with gap-adjacency flags."""
    toks, adj = [], []
    S = ln["segs"]
    for i, s in enumerate(S):
        for j, w in enumerate(s):
            a = (j == len(s) - 1 and i < len(S) - 1) or (j == 0 and i > 0)
            toks.append(w)
            adj.append(a)
    return toks, adj


def version_lines(page, version):
    out = []
    for ln in page["lines"]:
        if version == "SPLIT":
            out.extend([s for s in ln["segs"] if s])
            continue
        toks, adj = line_tokens(ln)
        if version == "EXCL":
            toks = [w for w, a in zip(toks, adj) if not a]
        if toks:
            out.append(toks)
    return out


# ------------------------------------------------------------------ fast A1 / A5
class Corpus:
    def __init__(self, pages, version):
        codes, lens, lid, pos, llen, page_of_line = [], [], [], [], [], []
        alpha = {}
        self.page_lines = []
        L = 0
        for pi, p in enumerate(pages):
            mine = []
            for ws in version_lines(p, version):
                mine.append(L)
                for j, w in enumerate(ws):
                    codes.append(alpha.setdefault(w[0], len(alpha)))
                    lens.append(len(w))
                    lid.append(L); pos.append(j); llen.append(len(ws))
                page_of_line.append(pi)
                L += 1
            self.page_lines.append(mine)
        self.codes = np.array(codes, np.int64); self.lens = np.array(lens, np.float64)
        self.lid = np.array(lid, np.int64); self.pos = np.array(pos, np.int64)
        self.llen = np.array(llen, np.int64); self.n_alpha = len(alpha)
        self.n_lines = L
        starts = np.zeros(L + 1, np.int64)
        np.add.at(starts, self.lid + 1, 1)
        self.line_start = np.cumsum(starts)
        self.n_tok = len(codes)

    def subset(self, line_ids):
        idx = np.concatenate([np.arange(self.line_start[i], self.line_start[i + 1]) for i in line_ids]) \
            if len(line_ids) else np.zeros(0, np.int64)
        return idx


def jsd_counts(P, Q):
    P = P / P.sum(); Q = Q / Q.sum(); M = (P + Q) / 2
    def kl(a, b):
        m = a > 0
        return float(np.sum(a[m] * np.log2(a[m] / b[m])))
    return (kl(P, M) + kl(Q, M)) / 2


def stats_on(codes, lens, pos, llen, nA, left, right):
    ok3 = llen >= 3
    first = np.bincount(codes[ok3 & (pos == 0)], minlength=nA).astype(float)
    mid = np.bincount(codes[ok3 & (pos > 0) & (pos < llen - 1)], minlength=nA).astype(float)
    a1 = jsd_counts(first, mid)
    z = lens - lens.mean()
    a5 = float(len(lens) / len(left) * np.dot(z[left], z[right]) / np.dot(z, z))
    return a1, a5


def excess(C: Corpus, idx, n_null, rng):
    codes, lens, lid, pos, llen = C.codes[idx], C.lens[idx], C.lid[idx], C.pos[idx], C.llen[idx]
    pair = np.nonzero((llen[:-1] >= 2) & (lid[:-1] == lid[1:]))[0]
    left, right = pair, pair + 1
    a1, a5 = stats_on(codes, lens, pos, llen, C.n_alpha, left, right)
    n1, n5 = [], []
    for _ in range(n_null):
        perm = np.lexsort((rng.random(len(idx)), lid))
        b1, b5 = stats_on(codes[perm], lens[perm], pos, llen, C.n_alpha, left, right)
        n1.append(b1); n5.append(b5)
    return a1 - float(np.mean(n1)), a5 - float(np.median(n5)), a1, a5


def part_a(label, pages, rng):
    emit(f"\n--- (a) {label}: {len(pages)} pages, P lines {sum(len(p['lines']) for p in pages)}, "
         f"lines with '<->' {sum(1 for p in pages for ln in p['lines'] if len(ln['segs']) > 1)}, "
         f"'<->' marks {sum(len(ln['segs']) - 1 for p in pages for ln in p['lines'])}, "
         f"internal gaps (both sides non-empty) "
         f"{sum(1 for p in pages for ln in p['lines'] for i in range(len(ln['segs']) - 1) if ln['segs'][i] and any(ln['segs'][i+1:]))}")
    out = {}
    for v in ("BASE", "EXCL", "SPLIT"):
        C = Corpus(pages, v)
        allidx = np.arange(C.n_tok)
        e1, e5, r1, r5 = excess(C, allidx, N_NULL_FULL, rng)
        draws = np.empty((N_SUB, 2))
        npg = len(pages)
        k = max(1, int(round(FRAC * npg)))
        for d in range(N_SUB):
            pg = rng.choice(npg, size=k, replace=False)
            lines = [li for pi in sorted(pg) for li in C.page_lines[pi]]
            idx = C.subset(lines)
            a, b, _, _ = excess(C, idx, N_NULL_SUB, rng)
            draws[d] = (a, b)
        lo = np.percentile(draws, 2.5, axis=0); hi = np.percentile(draws, 97.5, axis=0)
        out[v] = dict(a1=e1, a5=e5, a1_lo=lo[0], a1_hi=hi[0], a5_lo=lo[1], a5_hi=hi[1],
                      tok=C.n_tok, lines=C.n_lines)
        emit(f"  {v:5s} tokens {C.n_tok:6d} lines {C.n_lines:5d} | A1 raw {r1:.4f} excess {e1:+.4f} "
             f"[{lo[0]:+.4f}, {hi[0]:+.4f}] | A5 I {r5:+.4f} excess {e5:+.4f} [{lo[1]:+.4f}, {hi[1]:+.4f}]")
    for s in ("a1", "a5"):
        for v in ("EXCL", "SPLIT"):
            emit(f"    {s.upper()} {v}/BASE = {out[v][s] / out['BASE'][s]:.3f}")
    return out


# ------------------------------------------------------------------ part (b)
def part_b(zl_path, box_dir, rng):
    emit("\n--- (b) space fitting (ZL3b + voynichese boxes) ---")
    recs = vparse.load(path=zl_path)
    raw = {}
    for r in zl_path.read_text(encoding="ascii", errors="replace").splitlines():
        m = vparse.LINE_RE.match(r)
        if m:
            raw[(m.group(1), int(m.group(2)), m.group(4))] = m.group(5)
    pages, _st = box_mod.align_all(recs, box_dir)
    p_pages = sorted({r["page"] for r in recs if r["unit"].startswith("P") and r["words"]})
    rows = []  # (page, cls, L, S, hand, sec)
    n_aligned_pages = 0
    seg_mismatch = nonmono = 0
    page_hand = {}
    for folio, pairs in pages.items():
        plines = [(r, ln) for r, ln in pairs if r["unit"].startswith("P") and r["words"]]
        if not plines:
            continue
        use = []
        for r, ln in plines:
            if not (ln["aligned"] and ln["n_box"] == ln["n_zl"]):
                continue
            xs = [t["cx"] for t in ln["tokens"]]
            if any(b <= a for a, b in zip(xs, xs[1:])):
                nonmono += 1
                continue
            txt = re.sub(r"<![^>]*>", "", raw.get((folio, r["line"], r["unit"]), ""))
            segl = [len(vparse.clean(s)) for s in txt.split("<->")]
            if sum(segl) != len(r["words"]):
                seg_mismatch += 1
                continue
            use.append((r, ln, segl))
        if len(use) >= 0.5 * len(plines):
            n_aligned_pages += 1
        if not use:
            continue
        page_hand[folio] = (use[0][0]["hand"], use[0][0]["illus"])
        ppc = [t["w"] / glen(t["word"]) for _, ln, _ in use for t in ln["tokens"]
               if "?" not in t["word"] and glen(t["word"]) >= 1]
        g = float(np.median(ppc))
        M = float(np.percentile([ln["tokens"][-1]["cx"] + ln["tokens"][-1]["w"] / 2 for _, ln, _ in use], 95))
        for r, ln, segl in use:
            T = ln["tokens"]
            right = [t["cx"] + t["w"] / 2 for t in T]
            left = [t["cx"] - t["w"] / 2 for t in T]
            bounds = np.cumsum(segl)  # end index (exclusive) of each segment
            seg_of = np.repeat(np.arange(len(segl)), segl)
            n = len(T)
            for i in range(1, n):
                if seg_of[i - 1] != seg_of[i]:
                    continue  # previous word must be in the same segment
                w = T[i]["word"]
                if "?" in w or "?" in T[i - 1]["word"]:
                    continue
                s = seg_of[i]
                last_in_seg = i == bounds[s] - 1
                if i == n - 1:
                    cls, bnd = "MARGIN", M
                elif last_in_seg:
                    nxt = int(bounds[s])
                    if nxt >= n:
                        continue
                    cls, bnd = "PREGAP", left[nxt]
                else:
                    first_in_seg = i == (bounds[s - 1] if s > 0 else 0)
                    if first_in_seg:
                        continue
                    cls, bnd = "MID", left[i + 1]
                S = (bnd - right[i - 1]) / g
                rows.append((folio, cls, glen(w), S))
    frac = n_aligned_pages / max(len(p_pages), 1)
    emit(f"  ZL3b pages with P text {len(p_pages)}; box folios aligned {len(pages)}; pages with >=50 % usable "
         f"P lines {n_aligned_pages} ({100*frac:.1f} %); lines skipped: non-monotone x {nonmono}, "
         f"segment/token mismatch {seg_mismatch}")
    if frac < 0.60:
        emit("  part (b): not testable (fewer than 60 % of pages aligned)")
        return "not testable", None
    cnt = Counter(r[1] for r in rows)
    emit(f"  events: MID {cnt['MID']}, PREGAP {cnt['PREGAP']}, MARGIN {cnt['MARGIN']}")
    folios = sorted({r[0] for r in rows})
    by_page = defaultdict(list)
    for r in rows:
        by_page[r[0]].append(r)

    def slopes(sel_rows):
        out = {}
        for name, classes in (("MID", {"MID"}), ("PREGAP", {"PREGAP"}), ("MARGIN", {"MARGIN"}),
                              ("OBSTACLE", {"PREGAP", "MARGIN"})):
            a = np.array([(r[3], r[2]) for r in sel_rows if r[1] in classes], float)
            if len(a) < 3 or a[:, 0].std() == 0:
                out[name] = float("nan"); continue
            out[name] = float(np.polyfit(a[:, 0], a[:, 1], 1)[0])
        return out

    pt = slopes(rows)
    bs = defaultdict(list)
    for _ in range(N_BOOT):
        pick = rng.choice(len(folios), size=len(folios), replace=True)
        sel = [r for i in pick for r in by_page[folios[i]]]
        s = slopes(sel)
        for k, v in s.items():
            bs[k].append(v)
        bs["DIFF"].append(s["OBSTACLE"] - s["MID"])
        bs["DIFF_PREGAP"].append(s["PREGAP"] - s["MID"])
    pt["DIFF"] = pt["OBSTACLE"] - pt["MID"]
    pt["DIFF_PREGAP"] = pt["PREGAP"] - pt["MID"]
    ci = {k: (float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))) for k, v in bs.items()}
    emit(f"  {'class':12s} {'n':>6s} {'mean L':>7s} {'mean S':>7s} {'slope dL/dS':>12s}  95% CI")
    for k in ("MID", "PREGAP", "MARGIN", "OBSTACLE"):
        cl = {"OBSTACLE": {"PREGAP", "MARGIN"}}.get(k, {k})
        a = np.array([(r[3], r[2]) for r in rows if r[1] in cl], float)
        emit(f"  {k:12s} {len(a):6d} {a[:,1].mean():7.3f} {a[:,0].mean():7.3f} {pt[k]:+12.4f}  [{ci[k][0]:+.4f}, {ci[k][1]:+.4f}]")
    emit(f"  OBSTACLE - MID slope {pt['DIFF']:+.4f} [{ci['DIFF'][0]:+.4f}, {ci['DIFF'][1]:+.4f}];  "
         f"PREGAP - MID {pt['DIFF_PREGAP']:+.4f} [{ci['DIFF_PREGAP'][0]:+.4f}, {ci['DIFF_PREGAP'][1]:+.4f}]")
    call = "length tracks space" if (ci["OBSTACLE"][0] > 0 and ci["DIFF"][0] > 0) else "no space fitting"
    emit(f"  part (b) call: {call}")
    return call, dict(pt=pt, ci=ci)


# ------------------------------------------------------------------ part (c)
def part_c(pages, rng):
    emit("\n--- (c) Steckley BEFORE vs MIDDLE word length, ZL3b ---")
    for lab, sel in (("all hands", pages),
                     ("hand 1 Herbal", [p for p in pages if p["hand"] == "1" and p["sec"] == "H"])):
        per = []
        for p in sel:
            bef, mid = [], []
            for ln in p["lines"]:
                S = ln["segs"]
                for i in range(len(S) - 1):
                    if S[i] and any(S[i + 1:]):
                        bef.append(S[i][-1])
                if ln["top"]:
                    continue
                toks, adj = line_tokens(ln)
                for j in range(1, len(toks) - 1):
                    if not adj[j]:
                        mid.append(toks[j])
            per.append((bef, mid))
        def stat(pp, f):
            b = [f(w) for bb, _ in pp for w in bb]; m = [f(w) for _, mm in pp for w in mm]
            return (np.mean(b) if b else float("nan")), (np.mean(m) if m else float("nan")), len(b), len(m)
        for unit, f in (("EVA chars", len), ("glyphs", glen)):
            mb, mm, nb, nm = stat(per, f)
            diffs = []
            for _ in range(N_BOOT):
                pick = rng.choice(len(per), size=len(per), replace=True)
                b2, m2, _, _ = stat([per[i] for i in pick], f)
                diffs.append(b2 - m2)
            lo, hi = np.nanpercentile(diffs, [2.5, 97.5])
            emit(f"  {lab:14s} {unit:9s}: BEFORE {mb:.3f} (n {nb}) vs MIDDLE {mm:.3f} (n {nm}); "
                 f"diff {mb - mm:+.3f} [{lo:+.3f}, {hi:+.3f}]  (pages {len(per)}, with BEFORE "
                 f"{sum(1 for b, _ in per if b)})")


# ------------------------------------------------------------------ fixture
def make_fixture() -> None:
    rng = np.random.default_rng(11)
    vocab_short = ["dy", "dam", "s", "ar", "or", "ol", "am"]
    vocab = ["daiin", "chol", "chor", "qokeedy", "shedy", "okaiin", "otedy", "chedy", "qokain", "lchedy",
             "sheol", "cthor", "ykeey", "dar", "okal"] + vocab_short
    lines_out = ["#=IVTFF Eva- 2.0 M 3", "# s65 synthetic fixture (pages with drawing gaps and boxes)"]
    box_dir = RUNDIR / "fixture_boxes"
    box_dir.mkdir(parents=True, exist_ok=True)
    for pg in range(1, 61):
        pid = f"f{pg}r"
        hand = "1" if pg <= 30 else "2"
        lines_out.append(f"<{pid}>      <! $Q=A $P=A $F=a $B=1 $I={'H' if pg <= 40 else 'B'} $L={'A' if hand == '1' else 'B'} $H={hand}>")
        voc, bx = {}, []
        for li in range(1, 21):
            x = 30.0
            y = 40 + 30 * li
            nseg = 2 if rng.random() < 0.25 else 1
            parts = []
            for s in range(nseg):
                ws = []
                n = int(rng.integers(3, 6)) if nseg == 2 else int(rng.integers(5, 11))
                for j in range(n):
                    if s == 0 and nseg == 2 and j == n - 1:
                        w = str(rng.choice(vocab_short))
                    elif j > 0 and rng.random() < 0.5 and ws and len(ws[-1]) > 4:
                        w = str(rng.choice(vocab[:8]))
                    else:
                        w = str(rng.choice(vocab))
                    ws.append(w)
                    wpx = int(9 * glen(w) + rng.integers(-3, 4))
                    vi = voc.setdefault(w, len(voc))
                    bx.append([vi, int(x), int(y), max(wpx, 6), 18])
                    x += wpx + 7
                if s == 0 and nseg == 2:
                    x += 90
                parts.append(".".join(ws))
            mark = "<%>" if li in (1, 11) else ""
            sep = "@" if li in (1, 11) else "+"
            lines_out.append(f"<{pid}.{li},{sep}P0>      {mark}" + "<->".join(parts))
        vlist = [[w, 1, 1, [pid]] for w, _ in sorted(voc.items(), key=lambda kv: kv[1])]
        (box_dir / f"{pid}.js").write_text(json.dumps([vlist, bx]), encoding="utf-8", newline="\n")
    (RUNDIR / "fixture.txt").write_text("\n".join(lines_out) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {RUNDIR / 'fixture.txt'} and {box_dir}")


# ------------------------------------------------------------------ main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default=None)
    ap.add_argument("--make-fixture", action="store_true")
    a = ap.parse_args()
    if a.make_fixture:
        make_fixture()
        return
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    emit("S65: drawing-gap robustness of A1/A5, space fitting, Steckley BEFORE length")
    emit(f"start: {clock()}")
    emit(f"stub_match: {stub_match()}")
    for p in LOCAL:
        emit(f"  sha256 {sha256(p)}  {p.relative_to(ROOT).as_posix()}")
    if a.fixture:
        srcs = [("FIXTURE", Path(a.fixture))]
        box_dir = RUNDIR / "fixture_boxes"
        out = RUNDIR / "fixture_results.txt"
    else:
        srcs = SOURCES
        box_dir = box_mod.BOX_DIR
        out = OUT_REAL
    for lab, p in srcs:
        emit(f"  source {lab}: sha256 {sha256(p)}")
    parsed = {lab: parse_segments(p) for lab, p in srcs}
    if not a.fixture:
        for lab, pages in parsed.items():
            d = json.loads((ROOT / "data" / "translit" / META[lab]).read_text(encoding="utf-8"))
            mt = [w for p in d["pages"] for ln in p["lines"] for w in ln]
            ot = [w for p in pages for ln in p["lines"] for s in ln["segs"] for w in s]
            emit(f"  check {lab}: BASE tokens {len(ot)} vs meta.json {len(mt)} -> {'MATCH' if ot == mt else 'DIFFER'}")
    res = {lab: part_a(lab, pages, rng) for lab, pages in parsed.items()}
    fails = []
    for lab, r in res.items():
        for v in ("EXCL", "SPLIT"):
            for s in ("a1", "a5"):
                if not r[v][f"{s}_lo"] > 0:
                    fails.append(f"{lab} {v} {s.upper()} interval not above 0")
        for s in ("a1", "a5"):
            ratio = r["EXCL"][s] / r["BASE"][s]
            if not (0.75 <= ratio <= 1.25):
                fails.append(f"{lab} EXCL {s.upper()} moved {100*(ratio-1):+.1f} % vs BASE")
    call_a = "A1/A5 robust to drawing gaps" if not fails else "not robust: " + "; ".join(fails)
    emit(f"\n  part (a) call: {call_a}")
    first_lab, first_path = srcs[0]
    call_b, _ = part_b(first_path, box_dir, rng)
    part_c(parsed[first_lab], rng)
    emit("\n=== VERDICT ===")
    emit(f"VERDICT s65 (a): {call_a}")
    emit(f"VERDICT s65 (b): {call_b}")
    emit(f"end: {clock()}  (elapsed {time.time() - t0:.0f} s)")
    out.write_text("\n".join(LOG) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
