#!/usr/bin/env python
"""s128 (P-72, D-066 ee, D-073 external-anchor direction): do pharma-sketch labels appear in the text of their
EYE-MATCHED herbal page more often than in other herbal pages?

PRE-REGISTERED: sha256 of this file and of every input is frozen in s128_p72_label_partner.prereg.sha256 (repo root)
before any Voynich herbal-page text is read.  Before freezing only `--selftest DIR` was run (synthetic fixture +
Egerton 747 calibration + VKB label-line tokens; no Voynich herbal text read).  Outputs: runs/s128/p72/ and
results_s128_<ts>.txt.  Run-id note: runs/s128/ also holds an unrelated Grok Bot s128 study (name-slot prereg,
01:25-02:53 PDT); every file of this study carries the `p72` tag so none of those files is touched.

Run (repo root, CPU, numpy):  python -I tools/s128_p72_label_partner.py --selftest DIR   |   --run

PRIOR ART (reused, not edited): s54_label_partner_text.py (13 pairs, rank of partner among 128 herbal pages, ed1 /
exact / core hit, E-corrected score, MRR, 10,000 joint pool perms, planted control) -> no label-text link
(results_s54.txt).  s53 Part 1 (12 ZL + 7 Stolfi pairs, mean percentile) -> NULL.  VKB page_facts (queried 2026-10-19)
holds no published label-in-partner-text test for the pharma folios.  s128-P72 ADDS: 18 primary pairs whose plant
match was checked by eye and whose label was assigned by eye (pairs.tsv, label_confidence=likely); a planted power gate
calibrated on a real herbal; a real-language positive control (Egerton 747 chapter headings vs their own chapters);
shuffled-Voynich control; RF1b / IT2a replications.

DESIGN (fixed before hashing)
(1) Pairs.  PRIMARY = pairs.tsv rows with eye_verdict in {same, plausible} and label_confidence = likely (18 pairs,
    listed in PRIMARY below with the ZL3b label text read from VKB tokens of label_line_id).  SECONDARY = PRIMARY + the
    rows with eye_verdict in {same, plausible} and label_confidence = unclear that have a label_line_id (P10, P21, P30;
    P38 has no line id, unscorable).  The script asserts these lists against pairs.tsv.
(2) Herbal pool (per transliteration): VKB folios illus_type='H' whose paragraph tokens (loci locus_type 'P') number
    >= 30.  Page = multiset of those tokens; matching uses the page type set (as s54).  ZL3b primary; RF1b, IT2a
    replications with their own page texts and their own readings of the same label line_ids.
(3) Label tokens: VKB tokens of the pair's label line_id(s) in that transliteration; tokens made only of '?' dropped,
    other '?' kept as a literal symbol (s54 rule).  Comparison pool E for a pair = every token of every L locus on every
    illus_type='P' folio except the pair's own pharma folio (s54 rule).
(4) Hit per label token t and pool page h (s54 definitions): exact (variant a) t is a type of h; ed1 (variant b,
    PRIMARY) some type of h is at Levenshtein distance <= 1 from t; core (variant c, secondary; SlotSegmenter at risk
    under X-01 / vx01 A1) SlotSegmenter core of t equals the core of some type of h (segmenter fitted on all tokens of
    all loci of that transliteration, default parameters).  S(L,h) = mean hit over label tokens; E(Q,h) = same over the
    comparison pool; score(L,h) = [S - E] - mean_h'[S - E] (s54).  Rank of the partner among pool pages with mid-ranks,
    scores rounded to 1e-12 (checked against s54 `ranks`, imported).
(5) Aggregates: PRIMARY = MRR of the partner rank under ed1 (s54's primary, chosen because the alternative "k of n
    labels name their plant" is sparse).  Also reported: mean percentile (rank-1)/(N-1) (s53 / lead brief), number of
    pairs with partner rank 1, with an exact hit, with an ed1 hit on the partner, each with its null.
    Nulls (10,000 each, both required): N1 = partner pages permuted across pairs; N2 = uniform random pool pages (one
    pool permutation applied jointly, s54).  P = (1 + #null >= obs) / 10,001 (<= for mean percentile).
    p_primary = max(P_N1, P_N2) of ed1 MRR.  A set "links" iff p_primary < 0.01.
(6) Calibration (real herbal, Egerton 747 Tractatus de herbis, Ventura 2009 TEI): chapters `N. DE <NAME> ...`, name word
    = first heading word after DE (normalised: NFKD, lower, v->u, j->i, a-z only, length >= 3); eligible = chapter text
    (heading removed) >= 30 tokens, heading without '(MARG'.  c = number of chapter tokens within Levenshtein 1 of the
    name word.  INSERT_DIST = distribution of min(c, 3) given c >= 1.  Printed with P(c = 0).
(7) Fixture (synthetic, run first; gate): 128 synthetic pages (Voynich-like slot words, Zipf + page topics, lengths
    30-400), 18 pairs on 8 synthetic pharma pages, single rare-word labels, comparison pool of 60 other label words per
    pharma page.  Linked pair: the label word appended m ~ INSERT_DIST times to the partner page, each copy mutated
    by one glyph substitution with prob 0.3.  Conditions strong (18/18 linked), k5 (5/18), absent (0/18), 10 reps
    each, seed 20261019.  Gate: strong NAME_LINK >= 8/10 and absent NO_LINK >= 8/10, else CALL TEST_INVALID, stop.
(8) Real-language control (D-066 v): 200 subsamples of Egerton: 128 eligible chapters as pool, 18 of them as pairs,
    caption = name word, comparison pool = name words of all other eligible chapters; same statistic (exact, ed1; no
    core).  Control shows NAME_LINK iff share(p_primary < 0.01) >= 0.8.  If not: CALL UNPOWERED (real control), stop.
    (Data note: the A0 corpus, data/anchor_A0, holds captions but no entry text - s115-A0 CALL_C=NOT_RUN - so Egerton
    747 headings, the on-disk herbal that has both a name per entry and the entry text, are the real control.)
(9) Power gate (ZL3b, before the real comparison): 400 reps per k.  Each rep: every pair gets a decoy partner drawn
    uniformly from the pool minus its true partner (so the real partner relation is absent); k random pairs are linked
    by appending m ~ INSERT_DIST copies of one of its label tokens (1-glyph substitution with prob 0.3) to the decoy
    page; scores, ranks and both nulls recomputed.  Power(k) = share p_primary < 0.01.  If power(5) < 0.8: scan
    k = 6..n for the smallest k with power >= 0.8, CALL UNPOWERED, stop before the real comparison.
(10) Real comparison on ZL3b primary set; shuffled Voynich (labels with their comparison pools permuted across the
    primary pairs, 10 seeds) must give NO_LINK in >= 9/10, else CALL TEST_INVALID (shuffle); replications RF1b, IT2a
    (primary set); secondary set (ZL3b) descriptive only.  Per-pair ranks printed as a descriptive table, no call.
(11) CALL NAME_LINK iff ZL3b p_primary < 0.01 AND (RF1b or IT2a ed1 MRR > its N2 null mean) AND median Egerton
    control MRR > ZL3b ed1 N2 null q99 AND the shuffle check passes.  Else CALL NO_LINK.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from s54_label_partner_text import ranks as s54_ranks  # noqa: E402  (reused, unchanged)
from scoreboard.metrics_new import SlotSegmenter, edit1_neighbours  # noqa: E402  (reused, unchanged)

STUB = ROOT / "s128_p72_label_partner.prereg.sha256"
OUT = ROOT / "runs" / "s128" / "p72"
PAIRS_TSV = ROOT / "data" / "external" / "page-facts" / "eyecheck" / "pairs.tsv"
VKB = ROOT / "data" / "vkb" / "vkb.sqlite"
EGERTON = ROOT / "data" / "external" / "ventura_egerton747" / "tractatus-de-herbis-egerton-747-ventura2009-tei.xml"
SEED, NPERM = 20261019, 10000
MIN_TOK, MUT_RATE = 30, 0.3
N_FIX, R_CTRL, R_POW, N_SHUF = 10, 200, 400, 10
K_POW = 5
TRANSLITS = ["ZL3b", "RF1b", "IT2a"]
METHODS = ["ed1", "exact", "core"]  # b, a, c

# (pair_id, pharma folio, herbal folio, label line_ids, ZL3b label text)  -- frozen from pairs.tsv + VKB tokens
PRIMARY = [
    ("P05", "f102r2", "f18v", ["f102r2.21"], "koldarod"),
    ("P06", "f102r2", "f23r", ["f102r2.22"], "odalydary"),
    ("P09", "f102v1", "f19r", ["f102v1.18"], "opchdard"),
    ("P11", "f89v2", "f48v", ["f89v2.6"], "chokam"),
    ("P13", "f89v2", "f40v", ["f89v2.4"], "chokaro"),
    ("P18", "f89r1", "f57r", ["f89r1.4"], "otoldy"),
    ("P22", "f89r2", "f35v", ["f89r2.4"], "saloiinsheol"),
    ("P23", "f89r2", "f87v", ["f89r2.16"], "korainy"),
    ("P24", "f89r2", "f87r", ["f89r2.16"], "korainy"),
    ("P25", "f99r", "f51r", ["f99r.20"], "oaro"),
    ("P26", "f99r", "f96v", ["f99r.46"], "tolsasy"),
    ("P27", "f99v", "f44r", ["f99v.2"], "otoldy"),
    ("P28", "f99v", "f34v", ["f99v.28"], "chor olekor"),
    ("P29", "f99v", "f90v1", ["f99v.28"], "chor olekor"),
    ("P31", "f100r", "f96v", ["f100r.2"], "sochorcfhy"),
    ("P32", "f100v", "f13v", ["f100v.3"], "opchor"),
    ("P33", "f100v", "f90v2", ["f100v.6"], "ykchochdy"),
    ("P39", "f102v2", "f36r", ["f102v2.14"], "sarol"),
]
SECONDARY_EXTRA = [
    ("P10", "f89v2", "f48r", ["f89v2.27", "f89v2.28"], "sada? daseky"),
    ("P21", "f89r1", "f33r", ["f89r1.25", "f89r1.26"], "saldam sydarary"),
    ("P30", "f99v", "f55r", ["f99v.31"], "doldam"),
]
UNSCORABLE = [("P38", "f101v", "f37r", "label_confidence=unclear, no label_line_id")]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def clock():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def low_priority():
    try:
        import psutil
        p = psutil.Process()
        if hasattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS"):
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        else:
            p.nice(10)
        return True
    except Exception:
        return False


def free_gb():
    try:
        import psutil
        return psutil.virtual_memory().available / 2**30
    except Exception:
        return float("nan")


def keep(w):
    return bool(w) and set(w) != {"?"}


# ------------------------------------------------------------------ pairs assertion
def check_pairs():
    rows = [ln.split("\t") for ln in PAIRS_TSV.read_text(encoding="utf-8").splitlines()]
    hdr, rows = rows[0], rows[1:]
    H = {h: i for i, h in enumerate(hdr)}
    by = {r[H["pair_id"]]: r for r in rows}
    prim = sorted(r[H["pair_id"]] for r in rows if r[H["eye_verdict"]] in ("same", "plausible")
                  and r[H["label_confidence"]] == "likely")
    sec = sorted(r[H["pair_id"]] for r in rows if r[H["eye_verdict"]] in ("same", "plausible")
                 and r[H["label_confidence"]] == "unclear")
    assert prim == sorted(p[0] for p in PRIMARY), (prim, [p[0] for p in PRIMARY])
    assert sec == sorted([p[0] for p in SECONDARY_EXTRA] + [u[0] for u in UNSCORABLE]), sec
    for pid, ph, hb, lids, _ in PRIMARY + SECONDARY_EXTRA:
        r = by[pid]
        assert r[H["pharma_folio"]] == ph and r[H["herbal_folio"]] == hb, pid
        assert [x.strip() for x in r[H["label_line_id"]].split("/")] == lids, pid
    return len(prim), len(sec)


# ------------------------------------------------------------------ scoring core
class Pool:
    def __init__(self, pages, all_tokens, use_core=True):
        self.names = list(pages)
        self.N = len(self.names)
        self.alph = sorted({ch for w in all_tokens for ch in w})
        self.seg = SlotSegmenter(all_tokens) if use_core else None
        self.methods = METHODS if use_core else ["ed1", "exact"]
        self.idx, self.cidx = defaultdict(set), defaultdict(set)
        self.types = [set(pages[p]) for p in self.names]
        for j, s in enumerate(self.types):
            for w in s:
                self.idx[w].add(j)
                if self.seg:
                    self.cidx[self.core(w)].add(j)
        self._h, self._nb, self._E = {}, {}, {}

    def core(self, w):
        return self.seg.segment(w)[1]

    def nb(self, w):
        r = self._nb.get(w)
        if r is None:
            r = edit1_neighbours(w, self.alph) | {w}
            self._nb[w] = r
        return r

    def hits(self, t):
        r = self._h.get(t)
        if r is None:
            ex = np.zeros(self.N)
            ex[list(self.idx.get(t, ()))] = 1
            ed = ex.copy()
            for n in self.nb(t):
                js = self.idx.get(n)
                if js:
                    ed[list(js)] = 1
            r = dict(exact=ex, ed1=ed)
            if self.seg:
                co = np.zeros(self.N)
                co[list(self.cidx.get(self.core(t), ()))] = 1
                r["core"] = co
            self._h[t] = r
        return r

    def rel(self, m, q, w):
        if m == "exact":
            return q == w
        if m == "ed1":
            return q in self.nb(w)
        return self.core(q) == self.core(w)

    def mean_hits(self, toks, m, ins=None, key=None):
        if not toks:
            return np.zeros(self.N)
        if key is not None and (key, m) in self._E:
            base = self._E[(key, m)]
        else:
            base = np.mean([self.hits(t)[m] for t in toks], axis=0)
            if key is not None:
                self._E[(key, m)] = base
        if not ins:
            return base
        out = base.copy()
        cnt = Counter(toks)
        for j, words in ins.items():
            tot = 0
            for t, c in cnt.items():
                h = self.hits(t)[m][j] > 0 or any(self.rel(m, t, w) for w in words)
                tot += c * h
            out[j] = tot / len(toks)
        return out


def score_matrix(P, units, m, ins=None):
    rows = []
    for u in units:
        s = P.mean_hits(u["labels"], m, ins)
        e = P.mean_hits(u["comp"], m, ins, key=u["comp_key"])
        d = s - e
        rows.append(d - d.mean())
    return np.stack(rows)


def rank_all(sc):
    sc = np.round(sc, 12)
    out = np.empty_like(sc)
    for i, row in enumerate(sc):
        srt = np.sort(row)
        lo = np.searchsorted(srt, row, "left")
        hi = np.searchsorted(srt, row, "right")
        out[i] = 1 + (len(row) - hi) + 0.5 * (hi - lo - 1)
    return out


class Perms:
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.pool, self.pairs = {}, {}

    def get_pool(self, N):
        if N not in self.pool:
            self.pool[N] = np.argsort(self.rng.random((NPERM, N)), axis=1)
        return self.pool[N]

    def get_pairs(self, n):
        if n not in self.pairs:
            self.pairs[n] = np.argsort(self.rng.random((NPERM, n)), axis=1)
        return self.pairs[n]


def evaluate(P, units, m, perms, ins=None, true=None, want_hits=False):
    ti = np.array([u["true"] for u in units]) if true is None else np.asarray(true)
    n, N = len(units), P.N
    sc = score_matrix(P, units, m, ins)
    RA = rank_all(sc)
    rk = RA[np.arange(n), ti]
    assert np.allclose(rk, s54_ranks(sc, list(ti)))
    ar = np.arange(n)[None, :]
    null_idx = {"N1": ti[perms.get_pairs(n)], "N2": perms.get_pool(N)[:, ti]}
    res = dict(n=n, N=N, ranks=[float(x) for x in rk], mrr=float(np.mean(1 / rk)),
               mpct=float(np.mean((rk - 1) / (N - 1))), top1=int((rk <= 1).sum()))
    for k, idx in null_idx.items():
        nr = RA[ar, idx]
        nm = (1 / nr).mean(1)
        npct = ((nr - 1) / (N - 1)).mean(1)
        res[k] = dict(mrr_mean=float(nm.mean()), mrr_q99=float(np.quantile(nm, 0.99)),
                      p_mrr=float((1 + (nm >= res["mrr"] - 1e-12).sum()) / (NPERM + 1)),
                      pct_mean=float(npct.mean()),
                      p_pct=float((1 + (npct <= res["mpct"] + 1e-12).sum()) / (NPERM + 1)))
    res["p_primary"] = max(res["N1"]["p_mrr"], res["N2"]["p_mrr"])
    if want_hits:
        for hm in ("exact", "ed1"):
            Hm = np.stack([(P.mean_hits(u["labels"], hm, ins) > 0).astype(float) for u in units])
            obs = int(Hm[np.arange(n), ti].sum())
            d = dict(obs=obs)
            for k, idx in null_idx.items():
                nh = Hm[ar, idx].sum(1)
                d[k] = dict(mean=float(nh.mean()), p=float((1 + (nh >= obs).sum()) / (NPERM + 1)))
            res[f"partner_{hm}_hits"] = d
    return res


def fmt(tag, r):
    s = (f"{tag} MRR={r['mrr']:.4f} [N1 mean {r['N1']['mrr_mean']:.4f} q99 {r['N1']['mrr_q99']:.4f} P={r['N1']['p_mrr']:.4f}]"
         f" [N2 mean {r['N2']['mrr_mean']:.4f} q99 {r['N2']['mrr_q99']:.4f} P={r['N2']['p_mrr']:.4f}] p_primary={r['p_primary']:.4f}"
         f" | mean pct={r['mpct']:.3f} (N1 {r['N1']['pct_mean']:.3f} P={r['N1']['p_pct']:.4f}; N2 {r['N2']['pct_mean']:.3f}"
         f" P={r['N2']['p_pct']:.4f}) top1={r['top1']}/{r['n']}")
    for hm in ("exact", "ed1"):
        d = r.get(f"partner_{hm}_hits")
        if d:
            s += (f" | partner {hm}-hit {d['obs']}/{r['n']} (N1 mean {d['N1']['mean']:.2f} P={d['N1']['p']:.4f};"
                  f" N2 mean {d['N2']['mean']:.2f} P={d['N2']['p']:.4f})")
    return s


def mutate(w, alph, rng):
    i = int(rng.integers(len(w)))
    ch = [a for a in alph if a != w[i]]
    return w[:i] + ch[int(rng.integers(len(ch)))] + w[i + 1:]


def draw_m(dist, rng):
    return int(rng.choice([1, 2, 3], p=dist))


def plant(P, units, linked, partners, dist, rng):
    ins = defaultdict(list)
    for i in linked:
        toks = units[i]["labels"]
        w = toks[int(rng.integers(len(toks)))]
        for _ in range(draw_m(dist, rng)):
            ins[int(partners[i])].append(mutate(w, P.alph, rng) if rng.random() < MUT_RATE else w)
    return dict(ins)


# ------------------------------------------------------------------ Egerton (real-language control)
def lnorm(w):
    w = unicodedata.normalize("NFKD", w)
    w = "".join(c for c in w if not unicodedata.combining(c)).lower().replace("v", "u").replace("j", "i")
    return re.sub(r"[^a-z]", "", w)


def ltoks(s):
    return [t for t in (lnorm(x) for x in re.split(r"[\s\-,.;:()\[\]]+", s)) if t]


def load_egerton():
    t = EGERTON.read_text(encoding="utf-8")
    body = t[t.find("<body"):]
    out = []
    for m in re.finditer(r"<div2[^>]*>(.*?)</div2>", body, re.S):
        blk = m.group(1)
        h = re.search(r"<head>(.*?)</head>", blk, re.S)
        if not h:
            continue
        head = " ".join(re.sub(r"<[^>]+>", " ", h.group(1)).split())
        mm = re.match(r"\d+\.\s*DE\s+(.+)", head, re.I)
        if not mm or "(MARG" in head.upper():
            continue
        hw = ltoks(mm.group(1))
        if not hw or len(hw[0]) < 3:
            continue
        txt = re.sub(r"<head>.*?</head>", " ", blk, flags=re.S)
        txt = re.sub(r"<[^>]+>", " ", txt).replace("&lt;", " ").replace("&gt;", " ").replace("&amp;", " ")
        tk = ltoks(txt)
        if len(tk) >= MIN_TOK:
            out.append(dict(head=head, name=hw[0], toks=tk))
    return out


def calibrate(ch, log):
    alph = sorted({c for d in ch for w in d["toks"] for c in w})
    cs = []
    for d in ch:
        nb = edit1_neighbours(d["name"], alph) | {d["name"]}
        cs.append(sum(1 for w in d["toks"] if w in nb))
    cs = np.array(cs)
    pos = np.minimum(cs[cs >= 1], 3)
    dist = np.array([(pos == k).mean() for k in (1, 2, 3)])
    lens = np.array([len(d["toks"]) for d in ch])
    log(f"CALIBRATION (Egerton 747, {len(ch)} eligible chapters, median length {int(np.median(lens))} tokens): "
        f"name-word occurrences (Levenshtein <= 1) in own chapter: P(c=0)={np.mean(cs == 0):.3f}, median c={np.median(cs):.0f}, "
        f"mean c={cs.mean():.2f}, per-100-token median {np.median(100 * cs / lens):.2f}; "
        f"INSERT_DIST P(m=1,2,3 | c>=1, clipped at 3) = {dist.round(3).tolist()}")
    return dist, cs


def egerton_control(ch, n_pairs, perms, log):
    rng = np.random.default_rng(SEED + 7)
    all_tok = [w for d in ch for w in d["toks"]]
    res = []
    for r in range(R_CTRL):
        pool_i = rng.choice(len(ch), 128, replace=False)
        pages = {f"c{j}": ch[j]["toks"] for j in pool_i}
        P = Pool(pages, all_tok, use_core=False)
        pairs = rng.choice(128, n_pairs, replace=False)
        units = []
        for k in pairs:
            j = pool_i[k]
            comp = [ch[x]["name"] for x in range(len(ch)) if x != j]
            units.append(dict(labels=[ch[j]["name"]], comp=comp, comp_key=f"own{j}", true=int(k)))
        res.append(evaluate(P, units, "ed1", perms))
    share = float(np.mean([x["p_primary"] < 0.01 for x in res]))
    med = float(np.median([x["mrr"] for x in res]))
    log(f"REAL CONTROL (Egerton headings -> own chapter; {R_CTRL} subsamples, pool 128, n={n_pairs}): "
        f"share p_primary<0.01 = {share:.3f}; median ed1 MRR = {med:.4f}; median mean pct = "
        f"{np.median([x['mpct'] for x in res]):.3f}; median top1 = {np.median([x['top1'] for x in res]):.0f}/{n_pairs}")
    return share, med


# ------------------------------------------------------------------ synthetic fixture
def synth(rng, dist, cond, n_pairs=18, n_pages=128):
    pre = ["", "qo", "o", "ch", "sh", "d", "y", "ok", "ot", "qok", "s"]
    suf = ["", "y", "dy", "aiin", "ain", "ol", "or", "ar", "al", "am", "ey", "edy", "hy"]
    gl = list("acdeiklmnopqrsty")
    vocab = set()
    while len(vocab) < 4000:
        core = "".join(rng.choice(gl, int(rng.integers(1, 4))))
        vocab.add(pre[int(rng.integers(len(pre)))] + core + suf[int(rng.integers(len(suf)))])
    vocab = sorted(vocab)
    rng.shuffle(vocab)
    zipf = 1 / np.arange(1, len(vocab) + 1) ** 1.05
    zipf /= zipf.sum()
    pages, all_tok = {}, []
    for p in range(n_pages):
        L = int(np.exp(rng.uniform(np.log(30), np.log(400))))
        topic = rng.choice(len(vocab), 40, replace=False)
        g = rng.choice(len(vocab), L, p=zipf)
        tp = topic[rng.integers(0, 40, L)]
        toks = [vocab[a if rng.random() < 0.8 else b] for a, b in zip(g, tp)]
        pages[f"s{p}"] = toks
        all_tok += toks
    rare = vocab[300:]
    n_ph = 8
    lab_pages = {k: [rare[int(rng.integers(len(rare)))] for _ in range(60)] for k in range(n_ph)}
    units = []
    for i in range(n_pairs):
        ph = i % n_ph
        lab = rare[int(rng.integers(len(rare)))]
        comp = [w for k, ws in lab_pages.items() if k != ph for w in ws]
        units.append(dict(labels=[lab], comp=comp, comp_key=f"ph{ph}", true=int(rng.integers(n_pages))))
    all_tok += [w for ws in lab_pages.values() for w in ws] + [u["labels"][0] for u in units]
    P = Pool(pages, all_tok, use_core=True)
    k = {"strong": n_pairs, "k5": 5, "absent": 0}[cond]
    linked = rng.choice(n_pairs, k, replace=False)
    ins = plant(P, units, linked, [u["true"] for u in units], dist, rng)
    return P, units, ins


def fixture(dist, log):
    perms = Perms(SEED + 11)
    calls = {}
    for cond in ("strong", "k5", "absent"):
        rng = np.random.default_rng(SEED + {"strong": 1, "k5": 2, "absent": 3}[cond])
        out = []
        for _ in range(N_FIX):
            P, units, ins = synth(rng, dist, cond)
            out.append(evaluate(P, units, "ed1", perms, ins=ins))
        nl = sum(r["p_primary"] < 0.01 for r in out)
        calls[cond] = nl
        log(f"  fixture {cond:6s}: NAME_LINK {nl}/{N_FIX}; median ed1 MRR {np.median([r['mrr'] for r in out]):.4f}; "
            f"median p_primary {np.median([r['p_primary'] for r in out]):.4f}")
    ok = calls["strong"] >= 8 and (N_FIX - calls["absent"]) >= 8
    log(f"FIXTURE GATE (strong NAME_LINK >= 8/10 and absent NO_LINK >= 8/10): {'PASS' if ok else 'FAIL'}")
    return ok, calls


# ------------------------------------------------------------------ Voynich data
def folio_key(f):
    m = re.match(r"f(\d+)([rv])(\d*)", f)
    return (int(m.group(1)), m.group(2), int(m.group(3) or 0)) if m else (9999, f, 0)


def load_voynich(T, pair_sets):
    con = sqlite3.connect(f"file:{VKB}?mode=ro", uri=True)
    illus = dict(con.execute("SELECT folio, illus_type FROM folios"))
    rows = con.execute("SELECT t.folio, t.line_id, t.word, l.locus_type FROM tokens t JOIN loci l "
                       "ON l.translit = t.translit AND l.line_id = t.line_id WHERE t.translit = ? "
                       "ORDER BY t.folio, l.line_no, t.pos", (T,)).fetchall()
    con.close()
    para, lab_line, lab_page, all_tok = defaultdict(list), defaultdict(list), defaultdict(list), []
    for folio, lid, w, lt in rows:
        if not keep(w):
            continue
        all_tok.append(w)
        if lt == "P" and illus.get(folio) == "H":
            para[folio].append(w)
        if lt == "L":
            lab_line[lid].append(w)
            if illus.get(folio) == "P":
                lab_page[folio].append(w)
    pool = {p: para[p] for p in sorted(para, key=folio_key) if len(para[p]) >= MIN_TOK}
    P = Pool(pool, all_tok, use_core=True)
    sets, skipped = {}, []
    for name, plist in pair_sets.items():
        units = []
        for pid, ph, hb, lids, zl in plist:
            labels = [w for lid in lids for w in lab_line.get(lid, [])]
            if not labels or hb not in pool:
                skipped.append((name, pid, "no label tokens" if not labels else "partner not in pool"))
                continue
            comp = [w for f, ws in lab_page.items() if f != ph for w in ws]
            units.append(dict(pid=pid, pharma=ph, herbal=hb, labels=labels, comp=comp, comp_key=ph,
                              true=P.names.index(hb), zl=zl))
        sets[name] = units
    return P, sets, skipped, len(pool)


def power(P, units, dist, k, perms, rng):
    n = len(units)
    hits = 0
    for _ in range(R_POW):
        dec = []
        for u in units:
            j = int(rng.integers(P.N - 1))
            dec.append(j if j < u["true"] else j + 1)
        linked = rng.choice(n, k, replace=False)
        ins = plant(P, units, linked, dec, dist, rng)
        r = evaluate(P, units, "ed1", perms, ins=ins, true=dec)
        hits += r["p_primary"] < 0.01
    return hits / R_POW


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", metavar="DIR")
    g.add_argument("--run", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    prio = low_priority()
    L = []

    def log(s=""):
        L.append(s)
        print(s, flush=True)

    n_prim, n_sec = check_pairs()
    log(f"pairs.tsv check: primary {n_prim} pairs, unclear-label (secondary extra) {n_sec} rows (1 unscorable: P38)")
    log(f"BelowNormal priority set: {prio}; free RAM {free_gb():.1f} GB")
    if free_gb() < 4:
        log("STOP: free RAM < 4 GB")
        return
    ch = load_egerton()
    dist, _ = calibrate(ch, log)
    log("")
    log("FIXTURE (synthetic, seed 20261019; NAME_LINK = p_primary < 0.01):")
    ok, fcalls = fixture(dist, log)
    if a.selftest:
        d = Path(a.selftest)
        d.mkdir(parents=True, exist_ok=True)
        # exercise the VKB label side only (no herbal page text): label tokens of the frozen line_ids
        con = sqlite3.connect(f"file:{VKB}?mode=ro", uri=True)
        for T in TRANSLITS:
            labs = {pid: [w for lid in lids for (w,) in con.execute(
                "SELECT word FROM tokens WHERE translit=? AND line_id=? ORDER BY pos", (T, lid))]
                for pid, _, _, lids, _ in PRIMARY + SECONDARY_EXTRA}
            log(f"  labels {T}: " + "; ".join(f"{k}={' '.join(v)}" for k, v in labs.items()))
        con.close()
        log(f"selftest elapsed {time.time() - t0:.1f}s")
        (d / "s128_p72_selftest.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
        return

    # ---------------- real run
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    results = ROOT / f"results_s128_{ts}.txt"
    assert not results.exists()
    OUT.mkdir(parents=True, exist_ok=True)
    me = sha(__file__)
    stub_lines = [ln.split() for ln in STUB.read_text(encoding="utf-8").splitlines()
                  if ln.strip() and not ln.startswith("#")] if STUB.exists() else []
    stub_ok = bool(stub_lines) and all(len(x) == 2 and (ROOT / x[1]).exists() and sha(ROOT / x[1]) == x[0]
                                      for x in stub_lines)
    head = [f"s128 (P-72) label -> eye-matched herbal partner text; run start {clock()}",
            f"script tools/s128_p72_label_partner.py sha256={me}; stub {STUB.name} all_match={stub_ok}",
            f"vkb sha256={sha(VKB)}", ""]
    table = dict(start=clock(), script_sha256=me, stub_match=stub_ok, fixture=fcalls)
    calls = []

    def finish():
        log("")
        for c in calls:
            log(c)
        log(f"run end {clock()}; elapsed {time.time() - t0:.1f}s")
        results.write_text("\n".join(head + L) + "\n", encoding="utf-8")
        (OUT / f"s128_p72_pairs_table_{ts}.json").write_text(json.dumps(table, indent=1, default=str), encoding="utf-8")

    if not ok:
        calls.append("CALL TEST_INVALID (fixture gate failed)")
        return finish()
    perms = Perms(SEED)
    log("")
    share, ctrl_med = egerton_control(ch, len(PRIMARY), perms, log)
    table["control"] = dict(share=share, median_mrr=ctrl_med, insert_dist=dist.tolist())
    if share < 0.8:
        calls.append(f"CALL UNPOWERED (real control: Egerton headings show NAME_LINK in {share:.3f} < 0.8 of subsamples)")
        return finish()

    sets = {"primary": PRIMARY, "secondary": PRIMARY + SECONDARY_EXTRA}
    P, S, skipped, npool = load_voynich("ZL3b", sets)
    units = S["primary"]
    log("")
    log(f"ZL3b herbal pool {npool} pages (illus H, >= {MIN_TOK} paragraph tokens); primary pairs scored "
        f"{len(units)}/{len(PRIMARY)}; skipped {skipped}")
    rng = np.random.default_rng(SEED + 5)
    pw = power(P, units, dist, K_POW, perms, rng)
    log(f"POWER GATE (ZL3b, decoy partners, {R_POW} reps): power(k={K_POW}) = {pw:.3f}")
    table["power"] = {K_POW: pw}
    if pw < 0.8:
        need = None
        for k in range(K_POW + 1, len(units) + 1):
            pk = power(P, units, dist, k, perms, rng)
            table["power"][k] = pk
            log(f"  power(k={k}) = {pk:.3f}")
            if pk >= 0.8:
                need = k
                break
        calls.append(f"CALL UNPOWERED (power at k={K_POW} = {pw:.3f} < 0.8; k needed for 0.8 = "
                     f"{need if need else f'> {len(units)}'} of n={len(units)})")
        return finish()

    # real comparison
    log("")
    log("REAL (ZL3b primary):")
    real = {}
    for m in METHODS:
        real[m] = evaluate(P, units, m, perms, want_hits=(m == "ed1"))
        log(fmt(f"  {'PRIMARY' if m == 'ed1' else 'descr. '} [{m:5s}]", real[m]))
    table["real_ZL3b"] = real
    log("")
    log(f"per-pair ranks (/{P.N}) descriptive, no call: pid pharma <- herbal | label | ed1 exact core | partner ed1 matches")
    for i, u in enumerate(units):
        j = u["true"]
        mt = sorted({w for t in u["labels"] for w in P.types[j] if w in P.nb(t)})
        log(f"  {u['pid']} {u['pharma']:7s} <- {u['herbal']:6s} | {' '.join(u['labels']):14s} | "
            + " ".join(f"{real[m]['ranks'][i]:6.1f}" for m in METHODS) + f" | {mt}")
    # shuffled Voynich
    log("")
    srng = np.random.default_rng(SEED + 9)
    shuf_nl = 0
    for s in range(N_SHUF):
        perm = srng.permutation(len(units))
        su = [dict(u, labels=units[perm[i]]["labels"], comp=units[perm[i]]["comp"], comp_key=units[perm[i]]["comp_key"])
              for i, u in enumerate(units)]
        r = evaluate(P, su, "ed1", perms)
        shuf_nl += r["p_primary"] < 0.01
        log(f"  shuffle {s}: ed1 MRR={r['mrr']:.4f} p_primary={r['p_primary']:.4f}")
    log(f"SHUFFLED VOYNICH: NAME_LINK in {shuf_nl}/{N_SHUF} (check: NO_LINK in >= 9/10)")
    # replications
    rep_dir = {}
    for T in ("RF1b", "IT2a"):
        if free_gb() < 4:
            log("STOP: free RAM < 4 GB")
            break
        PT, ST, skT, npT = load_voynich(T, sets)
        r = evaluate(PT, ST["primary"], "ed1", perms, want_hits=True)
        rep_dir[T] = r["mrr"] > r["N2"]["mrr_mean"]
        log(f"REPLICATION {T}: pool {npT}; pairs {len(ST['primary'])}; skipped {skT}")
        log(fmt(f"  [{T} ed1]", r) + f" | same direction (MRR > N2 null mean): {rep_dir[T]}")
        table[f"rep_{T}"] = r
    # secondary
    sec = S["secondary"]
    log("")
    for m in METHODS:
        r = evaluate(P, sec, m, perms, want_hits=(m == "ed1"))
        log(fmt(f"SECONDARY ZL3b n={len(sec)} descr. [{m:5s}]", r))
        table[f"secondary_{m}"] = r
    q99 = real["ed1"]["N2"]["mrr_q99"]
    ctrl_above = ctrl_med > q99
    log("")
    log(f"real control median MRR {ctrl_med:.4f} vs ZL3b ed1 N2 null q99 {q99:.4f}: above = {ctrl_above}")
    if shuf_nl > 1:
        calls.append(f"CALL TEST_INVALID (shuffled Voynich NAME_LINK {shuf_nl}/{N_SHUF})")
    elif real["ed1"]["p_primary"] < 0.01 and any(rep_dir.values()) and ctrl_above:
        calls.append(f"CALL NAME_LINK (ZL3b p_primary={real['ed1']['p_primary']:.4f}; replications same direction "
                     f"{rep_dir}; control above null)")
    else:
        calls.append(f"CALL NO_LINK (ZL3b p_primary={real['ed1']['p_primary']:.4f}; replications same direction "
                     f"{rep_dir}; control above null {ctrl_above})")
    return finish()


if __name__ == "__main__":
    main()
