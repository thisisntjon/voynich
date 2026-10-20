#!/usr/bin/env python
"""s54: do pharmacy-section labels share text with the herbal page of the SAME plant, beyond chance?

PRE-REGISTERED: this file's sha256 is frozen in s54_label_partner_text.prereg.sha256 before any scoring run on real
data.  Before freezing, only the --selftest path (a synthetic fixture, no ZL data read) was run.

Run (project root, CPU, stdlib + numpy):
    python -I s54_label_partner_text.py --selftest DIR   # synthetic fixture only, writes only to DIR
    python -I s54_label_partner_text.py --run            # real data -> results_s54.txt, runs/s54/
Inputs (read only): data/ZL3b-n.txt (via vparse.clean / vparse.load), scoreboard/metrics_new.py (SlotSegmenter,
edit1_neighbours; imported, unchanged).

DESIGN (fixed before hashing)
(1) Units: the 13 page-level ZL pairs of s48/s53 (pharma page(s) <- herbal page), with the ZL cell of each comment:
      f102r1 <- f1v [3,2] ; f100v <- f3v [1,1] ; f102r2 <- f18v [3,1] ; f102v1 <- f19r [2,2] ; f102r2 <- f23r [3,1] ;
      f102r2 <- f32v [1,2] ; f102r1 <- f37v [3,1] ; f102r2 <- f47v [1,1] ; f89v2 <- f48r [3,4] ;
      f89v1+f89v2 <- f48v "f89v[1,4]" (cell read on f89v1, the first panel) ; f100r <- f90v2 [1,3] ;
      f100r <- f90v1 [1,3] ; f99r <- f96v [4,1].
(2) Label sets.  Label loci = ZL units whose type starts with "L"; tokens = vparse.clean (first reading of
    alternatives, ',' -> break); tokens made only of '?' are dropped; other '?' glyphs are kept as a literal symbol.
    Variant (a): every label token on the pharma page(s) of the pair.
    Variant (b): the ZL cell.  Cell rule (from the file layout, unverified on the scans): on each pharma page, a
      "row" is a maximal run of consecutive label lines not interrupted by a non-label locus, a '#' comment line
      or a page change; rows are numbered 1.. in file order.  Within a row, an "item" starts at each label line
      whose locus marker is not '+' ('+' lines continue the previous item); items are numbered 1.. in locus order,
      container (Lc) labels included.  Cell [r,c] = item c of row r.  If row r has fewer than c items, the whole
      row r is used (flagged "row fallback"); if the page has fewer than r rows, variant (a) is used (flagged).
    Variant (b_row): the whole row r (descriptive only, no decision).
(3) Herbal pool: every page with $I=H and >= 30 paragraph (P*) tokens.  H = the multiset of paragraph tokens of the
    page (P* units, same cleaning); matching uses the page's type set.  A pair whose herbal page is not in the pool
    is not scored (reported).
(4) Scores.  hit_m(t, h) in {0,1} for label token t and pool page h, method m:
      ed1   (PRIMARY)   t, or a string at Levenshtein distance 1 from t, is a paragraph type of h;
      exact (secondary) t is a paragraph type of h;
      core  (secondary) the SlotSegmenter core of t equals the core of some paragraph type of h; the segmenter is
                        fitted once on all tokens of all ZL loci (every page, every unit type), default parameters.
    S(L, h) = mean over the tokens of L (with multiplicity) of hit(t, h).
    Length-matched expectation: E(Q, h) = mean of hit(t, h) over the comparison pool = every label token on every
    $I=P page except the pair's own pharma page(s).  This is the expected S of a same-size label set drawn from
    other pharma labels against h, so it absorbs herbal page length / vocabulary size (subtracting the mean of S(L,.)
    over the pool, the literal per-L expectation, is a constant per pair and cannot change a rank; it is applied too).
    Score(L, h) = [S(L, h) - E(Q, h)] - mean_h' [S(L, h') - E(Q, h')].
(5) Statistic: rank of the true herbal page among the pool per pair, mid-rank for ties (1 + #pages strictly higher
    + 0.5 * #other pages tied; scores rounded to 1e-12; s48 used 1 + #strictly higher, which lets an all-zero row rank
    the true page first), MRR, median percentile (rank-1)/(N-1), top-5 and top-1 counts.
    Null: 10,000 random permutations of the herbal page labels (pool indices), one per draw applied jointly to all
    scored pairs, seed 20261017; P = (1 + #null MRR >= obs) / 10,001; q99 and q99.5 reported.
(6) Positive control (run first): in memory, each pair's label set (one per pair, used for every variant) is replaced
    by 3 tokens sampled with replacement from the true herbal page's paragraph tokens; each sampled token is, with
    probability 0.3, mutated by one glyph substitution (uniform position, uniform different glyph from the ZL glyph
    alphabet); rng seed 20261017 + 1.  The comparison pool E stays the real one.  Control passes if the primary
    (ed1) MRR exceeds the null 99th percentile.  If it fails the verdict is TEST INVALID.
(7) Decision (primary method ed1 only): "labels name their herbal partner" if MRR of variant (a) OR (b) exceeds the
    null 99.5th percentile (Bonferroni over the two variants); otherwise "no label-text link".  Secondary methods
    and b_row are reported without decision.
Outputs: results_s54.txt (header: `date`, sha256, stub_match, elapsed), runs/s54/pairs_table.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STUB = ROOT / "s54_label_partner_text.prereg.sha256"
OUT = ROOT / "runs" / "s54"
RESULTS = ROOT / "results_s54.txt"
SEED, NPERM = 20261017, 10000
MIN_TOK, PLANT_K, MUT_RATE = 30, 3, 0.3
METHODS = ["ed1", "exact", "core"]
VARIANTS = ["a", "b", "b_row"]

PAIRS = [  # (pharma pages, herbal page, cell page, (row, col), source)
    (["f102r1"], "f1v", "f102r1", (3, 2), "ZL f102r1[3,2] (Petersen, Stolfi)"),
    (["f100v"], "f3v", "f100v", (1, 1), "ZL f100v[1,1] root (Petersen)"),
    (["f102r2"], "f18v", "f102r2", (3, 1), "ZL f102r2[3,1] ? (FSG, Stolfi)"),
    (["f102v1"], "f19r", "f102v1", (2, 2), "ZL f102v1[2,2] ? (Stolfi)"),
    (["f102r2"], "f23r", "f102r2", (3, 1), "ZL f102r2[3,1] (FSG, GL)"),
    (["f102r2"], "f32v", "f102r2", (1, 2), "ZL f102r2[1,2] ? (FSG, Stolfi)"),
    (["f102r1"], "f37v", "f102r1", (3, 1), "ZL f102r1[3,1] ? (Stolfi)"),
    (["f102r2"], "f47v", "f102r2", (1, 1), "ZL f102r2[1,1] (Petersen)"),
    (["f89v2"], "f48r", "f89v2", (3, 4), "ZL f89v2[3,4] ? (Stolfi)"),
    (["f89v1", "f89v2"], "f48v", "f89v1", (1, 4), "ZL f89v[1,4] ? (Stolfi)"),
    (["f100r"], "f90v2", "f100r", (1, 3), "ZL f100r[1,3] ? (Stolfi)"),
    (["f100r"], "f90v1", "f100r", (1, 3), "ZL f100r[1,3] ? (Stolfi)"),
    (["f99r"], "f96v", "f99r", (4, 1), "ZL f99r[4,1] ? (GL)"),
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def now():
    try:
        return subprocess.run(["date"], capture_output=True, text=True).stdout.strip() or time.ctime()
    except OSError:
        return time.ctime()


def keep(w):
    return bool(w) and set(w) != {"?"}


# ------------------------------------------------------------------ real-data parsing
def parse_zl():
    """Returns pages{pid: dict(illus, para=[tok], rows=[[ [tok,...] per item ] per row ])}, all_tokens."""
    import vparse
    page_re = re.compile(r"^<(f\w+)>\s+<!(.*)>")
    line_re = re.compile(r"^<(f\w+)\.(\d+),(.)(\w+)>\s+(.*)$")
    var_re = re.compile(r"\$(\w)=(\w+)")
    pages, cur, run_open, all_tokens = {}, None, False, []
    for raw in vparse.DATA.read_text(encoding="ascii", errors="replace").splitlines():
        if raw.startswith("#"):
            run_open = False
            continue
        if not raw.strip():
            continue
        m = page_re.match(raw)
        if m:
            meta = dict(var_re.findall(m.group(2)))
            cur = pages.setdefault(m.group(1), dict(illus=meta.get("I", "?"), para=[], rows=[]))
            run_open = False
            continue
        m = line_re.match(raw)
        if not m or cur is None:
            continue
        _, _, marker, unit, text = m.groups()
        words = [w for w in vparse.clean(text) if keep(w)]
        all_tokens.extend(words)
        if unit.startswith("L"):
            if not run_open:
                cur["rows"].append([])
                run_open = True
            row = cur["rows"][-1]
            if marker == "+" and row:
                row[-1].extend(words)
            else:
                row.append(list(words))
        else:
            run_open = False
            if unit.startswith("P"):
                cur["para"].extend(words)
    return pages, all_tokens


def build_real():
    pages, all_tokens = parse_zl()
    pool = [p for p, d in pages.items() if d["illus"] == "H" and len(d["para"]) >= MIN_TOK]
    herb = {p: pages[p]["para"] for p in pool}
    pharma = [p for p, d in pages.items() if d["illus"] == "P"]
    labs = {p: [t for row in pages[p]["rows"] for it in row for t in it] for p in pharma}
    units = []
    for ph, hp, cp, (r, c), src in PAIRS:
        a = [t for p in ph for t in labs.get(p, [])]
        rows = pages[cp]["rows"] if cp in pages else []
        if len(rows) >= r:
            row = rows[r - 1]
            brow = [t for it in row for t in it]
            if len(row) >= c and row[c - 1]:
                b, flag = list(row[c - 1]), "cell"
            else:
                b, flag = list(brow), "row fallback"
        else:
            brow, b, flag = list(a), list(a), "page fallback"
        comp = [t for p in pharma if p not in ph for t in labs[p]]
        units.append(dict(pharma=ph, herbal=hp, src=src, cell=f"{cp}[{r},{c}]", cell_flag=flag,
                          labels=dict(a=a, b=b, b_row=brow), comp=comp))
    return dict(herb=herb, units=units, all_tokens=all_tokens, n_pharma=len(pharma))


# ------------------------------------------------------------------ core scoring (shared by fixture and real run)
class Matcher:
    def __init__(self, herb, all_tokens):
        from scoreboard.metrics_new import SlotSegmenter, edit1_neighbours
        self.e1 = edit1_neighbours
        self.pool = list(herb)
        self.alph = sorted({ch for w in all_tokens for ch in w})
        self.seg = SlotSegmenter(all_tokens)
        self.types = [set(herb[p]) for p in self.pool]
        self.cores = [{self.seg.segment(w)[1] for w in s} for s in self.types]
        self.idx = {}
        for j, s in enumerate(self.types):
            for w in s:
                self.idx.setdefault(w, set()).add(j)
        self.cidx = {}
        for j, s in enumerate(self.cores):
            for c in s:
                self.cidx.setdefault(c, set()).add(j)
        self.cache = {}

    def hits(self, t):
        r = self.cache.get(t)
        if r is not None:
            return r
        N = len(self.pool)
        ex = np.zeros(N)
        ex[list(self.idx.get(t, ()))] = 1
        ed = ex.copy()
        for n in self.e1(t, self.alph):
            js = self.idx.get(n)
            if js:
                ed[list(js)] = 1
        co = np.zeros(N)
        co[list(self.cidx.get(self.seg.segment(t)[1], ()))] = 1
        r = dict(ed1=ed, exact=ex, core=co)
        self.cache[t] = r
        return r

    def mean_hits(self, toks, m):
        if not toks:
            return np.zeros(len(self.pool))
        return np.mean([self.hits(t)[m] for t in toks], axis=0)


def ranks(sc, true_idx):
    sc = np.round(sc, 12)
    tv = sc[np.arange(len(true_idx)), true_idx][:, None]
    return 1 + (sc > tv).sum(1) + 0.5 * ((sc == tv).sum(1) - 1)


def null_dist(sc, true_idx, seed):
    rng = np.random.default_rng(seed)
    sc = np.round(sc, 12)
    n, N = sc.shape
    rank_all = np.stack([1 + (sc[i][None, :] > sc[i][:, None]).sum(1)
                         + 0.5 * ((sc[i][None, :] == sc[i][:, None]).sum(1) - 1) for i in range(n)])
    out = np.empty(NPERM)
    ti = np.asarray(true_idx)
    for k in range(NPERM):
        perm = rng.permutation(N)
        out[k] = np.mean(1.0 / rank_all[np.arange(n), perm[ti]])
    return out


def evaluate(M, units, label_key, m, seed=SEED):
    """units: scored units; label_key(u) -> token list.  Returns stats dict."""
    true_idx = [M.pool.index(u["herbal"]) for u in units]
    rows = []
    for u in units:
        s = M.mean_hits(label_key(u), m)
        e = M.mean_hits(u["comp"], m)
        d = s - e
        rows.append(d - d.mean())
    sc = np.stack(rows)
    rk = ranks(sc, true_idx)
    N = len(M.pool)
    mrr = float(np.mean(1.0 / rk))
    nd = null_dist(sc, true_idx, seed)
    return dict(ranks=[float(x) for x in rk], N=N, mrr=mrr, null_mean=float(nd.mean()),
                q99=float(np.quantile(nd, 0.99)), q995=float(np.quantile(nd, 0.995)),
                P=float((1 + (nd >= mrr - 1e-15).sum()) / (NPERM + 1)),
                median_pct=float(np.median((rk - 1) / (N - 1))), top5=int((rk <= 5).sum()), top1=int((rk <= 1).sum()),
                n_tokens=[len(label_key(u)) for u in units])


def plant(M, herb, units, seed):
    rng = np.random.default_rng(seed)
    out = {}
    for u in units:
        src = herb[u["herbal"]]
        toks = []
        for _ in range(PLANT_K):
            w = src[int(rng.integers(len(src)))]
            if rng.random() < MUT_RATE:
                i = int(rng.integers(len(w)))
                choices = [a for a in M.alph if a != w[i]]
                w = w[:i] + choices[int(rng.integers(len(choices)))] + w[i + 1:]
            toks.append(w)
        out[u["herbal"]] = toks
    return out


def run_all(data, log):
    herb, units_all = data["herb"], data["units"]
    M = Matcher(herb, data["all_tokens"])
    units = [u for u in units_all if u["herbal"] in herb]
    dropped = [u["herbal"] for u in units_all if u["herbal"] not in herb]
    log(f"herbal pool: {len(M.pool)} pages ($I=H, >= {MIN_TOK} paragraph tokens); pharma ($I=P) pages: "
        f"{data['n_pharma']}; pairs scored {len(units)}/{len(units_all)}" + (f"; not in pool: {dropped}" if dropped else ""))
    log(f"SlotSegmenter fitted on all {len(data['all_tokens'])} corpus tokens (real run: every ZL locus, all pages): "
        f"{len(M.seg.prefixes)} prefixes {sorted(M.seg.prefixes)}, {len(M.seg.suffixes)} suffixes {sorted(M.seg.suffixes)}")
    res = {}
    # positive control first
    pl = plant(M, herb, units, SEED + 1)
    log("")
    log(f"POSITIVE CONTROL (planted: {PLANT_K} true-page tokens per pair, 1-glyph mutation rate {MUT_RATE}):")
    for m in METHODS:
        r = evaluate(M, units, lambda u: pl[u["herbal"]], m)
        res[f"planted/{m}"] = r
        log(f"  [{m:5s}] MRR={r['mrr']:.4f} null mean={r['null_mean']:.4f} q99={r['q99']:.4f} P={r['P']:.4f} "
            f"top1={r['top1']} top5={r['top5']}/{len(units)} median pct={r['median_pct']:.3f}")
    ctrl = res["planted/ed1"]["mrr"] > res["planted/ed1"]["q99"]
    log(f"  control (ed1 MRR > null q99): {'PASS' if ctrl else 'FAIL -> TEST INVALID'}")
    log("")
    log("REAL LABELS (score = [S - E_comparison] - mean over pool; rank among pool; null = 10,000 joint perms):")
    for v in VARIANTS:
        for m in METHODS:
            r = evaluate(M, units, lambda u, v=v: u["labels"][v], m)
            res[f"{v}/{m}"] = r
            tag = "PRIMARY " if (m == "ed1" and v in ("a", "b")) else "descr.  "
            log(f"  {tag}[{v:5s}/{m:5s}] MRR={r['mrr']:.4f} null mean={r['null_mean']:.4f} q99={r['q99']:.4f} "
                f"q99.5={r['q995']:.4f} P={r['P']:.4f} top1={r['top1']} top5={r['top5']} median pct={r['median_pct']:.3f}")
    log("")
    log(f"per-pair ranks (/{len(M.pool)}); columns: " + ", ".join(f"{v}/{m}" for v in VARIANTS for m in METHODS)
        + ", planted/ed1")
    table = []
    for i, u in enumerate(units):
        rk = [res[f"{v}/{m}"]["ranks"][i] for v in VARIANTS for m in METHODS]
        j = M.pool.index(u["herbal"])
        hitw = {v: sorted({t for t in u["labels"][v] if M.hits(t)["ed1"][j]}) for v in ("a", "b")}
        log(f"  {'+'.join(u['pharma']):12s} <- {u['herbal']:6s} " + " ".join(f"{x:5.1f}" for x in rk)
            + f" | {res['planted/ed1']['ranks'][i]:5.1f}  nA={len(u['labels']['a'])} cell {u['cell']} ({u['cell_flag']}) "
            f"b={u['labels']['b']} ed1-hits on true page: a={hitw['a']} b={hitw['b']}")
        table.append(dict(pharma=u["pharma"], herbal=u["herbal"], src=u["src"], cell=u["cell"],
                          cell_flag=u["cell_flag"], labels=u["labels"], planted=pl[u["herbal"]],
                          ed1_hits_true=hitw, ranks={k: res[k]["ranks"][i] for k in res}))
    pos = any(res[f"{v}/ed1"]["mrr"] > res[f"{v}/ed1"]["q995"] for v in ("a", "b"))
    if not ctrl:
        verdict = "TEST INVALID (planted control failed)"
    else:
        verdict = "labels name their herbal partner" if pos else "no label-text link"
    log("")
    log(f"DECISION (ed1, variant a or b MRR > null q99.5, Bonferroni over 2 variants): "
        f"a {res['a/ed1']['mrr']:.4f} vs {res['a/ed1']['q995']:.4f}; b {res['b/ed1']['mrr']:.4f} vs "
        f"{res['b/ed1']['q995']:.4f} -> VERDICT: {verdict}")
    return dict(results=res, table=table, pool=M.pool, control_pass=ctrl, verdict=verdict)


# ------------------------------------------------------------------ synthetic fixture
def fixture(seed, linked):
    rng = np.random.default_rng(seed)
    alph = list("acdehiklnoqrsty")

    def word():
        return "".join(alph[int(i)] for i in rng.integers(len(alph), size=int(rng.integers(3, 8))))
    common = [word() for _ in range(300)]
    herb = {}
    for k in range(80):
        rare = [word() for _ in range(30)]
        n = int(rng.integers(40, 300))
        herb[f"h{k}"] = [common[int(rng.integers(300))] if rng.random() < 0.7 else rare[int(rng.integers(30))]
                         for _ in range(n)]
    units = []
    for k in range(13):
        hp = f"h{k * 5}"
        a = [word() for _ in range(int(rng.integers(5, 30)))]
        if linked:
            a[:3] = list(rng.choice(herb[hp], 3))
        units.append(dict(pharma=[f"p{k % 7}"], herbal=hp, src="fixture", cell="fixture", cell_flag="cell",
                          labels=dict(a=a, b=a[:2], b_row=a[:5]), comp=[word() for _ in range(150)]))
    all_tokens = [t for v in herb.values() for t in v] + [t for u in units for t in u["labels"]["a"]]
    return dict(herb=herb, units=units, all_tokens=all_tokens, n_pharma=7)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", metavar="DIR")
    g.add_argument("--run", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    if a.selftest:
        d = Path(a.selftest)
        d.mkdir(parents=True, exist_ok=True)
        for linked in (False, True):
            L = []
            out = run_all(fixture(7, linked), lambda s: (L.append(s), print(s)))
            (d / f"selftest_{'linked' if linked else 'random'}.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
            print(f"selftest linked={linked}: verdict={out['verdict']}\n")
        return
    me = sha(__file__)
    stub_match = STUB.exists() and any(line.split()[:2] == [me, Path(__file__).name]
                                       for line in STUB.read_text(encoding="utf-8").splitlines()
                                       if not line.startswith("#") and line.strip())
    L = []
    out = run_all(build_real(), lambda s: (L.append(s), print(s)))
    el = time.time() - t0
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pairs_table.json").write_text(json.dumps(dict(script_sha256=me, stub_match=stub_match, **out), indent=1),
                                          encoding="utf-8")
    head = [f"date: {now()}", f"s54_label_partner_text.py sha256={me}", f"stub_match={stub_match}",
            f"elapsed: {el:.1f}s", ""]
    tail = ["", f"paths: {RESULTS.name}, runs/s54/pairs_table.json, {STUB.name}"]
    RESULTS.write_text("\n".join(head + L + tail) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
