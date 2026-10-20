"""S55: word-level code vs procedural generator on wrapper-free, layer-split statistics only.

QUESTION (frozen): using only statistics that a shared wrapper or handed line-edge pools do NOT fix, can a
word-level code be told from a procedural generator on known texts, and where does the Voynich manuscript fall?
Background: s49 (results_s49.txt) put Voynich between the CODE (K4) and GEN centroids, unassigned; its CIPH+CODE vs
GEN+GIB separation rests on line-edge features (jsd_first_fg, line_init_excess, AUC 0.965) that the entrants'
handed edge pools fix by construction (A17, CONSTRAINTS-MAP dot 14).

PRE-REGISTRATION (frozen in s55_code_vs_generator.prereg.sha256 = sha256 of this file and of every local module it
imports, BEFORE any real-text scoring; before the freeze the script ran only on its synthetic fixture
(--fixture <scratch dir>), which reads no real data and writes nothing in the project).

TEXTS (read-only from runs/s49, labels from runs/s49/labels.json, sha256 printed):
  CODE (6): the s49 CODE class, code_k4_<plaintext> (K4 shared-codeword nomenclator on the ZL3b skeleton).
  GEN  (6): the s49 GEN class: gen_s28_ZL3b_s1, gen_c2_section, gen_timm_schinner, gen_schwartz_reuse,
            gen_rugg_grille, gen_G2layer_ZL3b_s1.
  Reported-only extras (never in training): the remaining two-layer producers of s49 = ciph_L2layer_ZL3b_s1 and the
    18 twin-panel texts (twin_G2layer_* / twin_L2layer_*, ZL3b s2-s4, RF1b s1-s3, IT2a s1-s3).
  Voynich x3: data/translit/{ZL3b_eva, RF1b, IT2a}.meta.json via n1_habit_table.load (as s39/s40), section = page
    section label.  Voynich is scored on its full text (~34.4-34.9k tokens; the s49 texts are 38k).

SPLIT AND SEGMENTER (per text): pages shuffled by random.Random(20261017), first round(0.8 n) = training, rest =
  held-out (g1_edge_joint.split_names / s40 convention; for Voynich this is the 166/41 g1_heldout_41 split).
  scoreboard/metrics_new.SlotSegmenter (defaults: min_share 0.01, max_len 3, ent_frac 0.5) fitted on the training
  pages' tokens only and applied to every token.  prefix stream = prefix class or "∅"; core stream = cores;
  frame = prefix + "+" + suffix.  EVERY feature is measured on the held-out pages (models fitted on training pages
  where a model is needed).

FEATURES (8; no line-edge, line-position, glyph-edge-pool or cross-space coupling statistic is used):
  f1_core_F1      core-stream held-out word-order residual (s39 core-only F1): n1_habit_table.page_sums (f1 models,
                  TOPN 300, a/k grid) with training-page core lines as train and held-out core lines as test, minus
                  the same with every line shuffled within itself (random.Random(3), as n1.residual).
                  [DEVIATION from s39: the 80/20 page split replaces n1's quire split so that all features share one
                  held-out set.]
  f2_core_core    A14 core->core ordering excess on held-out lines: plug-in MI(C_t; C_t+1) over within-line adjacent
                  pairs minus the mean of 200 within-line shuffles (np.random.default_rng(20261017)).
                  [DEVIATION from p4d1.core_excess: held-out lines with the training-fit segmenter, not all tokens.]
  f3_core_gain    core-stream held-out bigram gain (s40 pipeline on cores): unigram add-0.5 bits minus Witten-Bell
                  bigram bits per held-out within-line target, models fitted on training pages.
  f4_prefix_gain  the same on the prefix stream (s40's GAIN).  (For f3/f4 the within-line-shuffle excess, 20 draws
                  random.Random(20261017) as s40, is printed beside but is not a classifier feature.)
  f5a_core_cover  share of held-out core TYPES that occur among training cores.
  f5b_core_heaps  Heaps exponent of the held-out core stream (pages in held-out order): least-squares slope of
                  log V(N) on log N at 30 log-spaced N from 100 to the stream length.
  f6_core_sec_nmi NMI(core type; page section) over held-out tokens, NMI = I / sqrt(H(C) H(S)), minus the mean of
                  200 permutations of the section labels across held-out pages (rng 20261017).  A text with one
                  section on its held-out pages scores 0.
                  CAVEAT stated before the run: section labels are part of the text construction (CODE texts and the
                  skeleton generators carry Voynich section labels over non-Voynich content; timm_schinner has one
                  label, rugg_grille layout blocks), so f6 can separate the classes by corpus construction; a
                  sensitivity without f6 is reported (not gating).
  f7_frame_core   within-word MI(frame; core) on held-out tokens minus the mean of 200 global core shuffles
                  (s51 Part 1 statistic, rng 20261017).
  NaN (error / undefined) -> training-fold median (classifiers) [CHOICE].

CLASSIFIERS (no tuning): leave-one-text-out over the 12 (CODE 6, GEN 6); z from the training fold's mean / sd
  (sd 0 -> 1).
  NC = nearest of the two class centroids, Euclidean in z; margin = |d(CODE) - d(GEN)|.
  LR = sklearn LogisticRegression(C=1.0, solver='lbfgs', max_iter=10000), L2 penalty (the default; sklearn 1.8 deprecates
       the explicit penalty argument, so it is left at its default); margin = |decision function|
       (log-odds).
PREDICTIONS (fixed):
  P1 discriminability: LOO accuracy >= 10/12 on BOTH NC and LR -> "wrapper-free features can separate code from
     generator".  Otherwise the reading is "code and generator are not separable without line-edge features; the
     question cannot be settled by these statistics", and no Voynich assignment counts.
  P2 (only if P1 passes): models fitted on all 12 (z on the 12).  A transliteration's assignment counts when NC and
     LR name the same class AND on each classifier its margin exceeds that classifier's median LOO margin over the
     correctly classified texts.  If it holds on one classifier only: "counts on <clf> only, not robust".
     The reading names the class (CODE or GEN) per transliteration.
REPORTED, NOT GATING: per-feature class means and sds, univariate AUC (CODE positive vs GEN), Voynich values with
  page-bootstrap 95 % intervals (B = 500 resamples of the held-out pages with replacement, np.random.default_rng
  (20261017); MI-type features recompute their shuffle null with 20 draws per resample; f5b uses the distinct drawn
  pages in drawn order because duplicated pages add no types), the share of bootstrap draws each classifier assigns
  to CODE, LOO without f6 and without f7, and the projection of the extras (twin pairs: does L_2layer lean more
  CODE than its G_2layer twin under LR?).
Constraints: python -I, one CPU process, no new data; writes ONLY results_s55.txt and runs/s55/; runs/s49 read-only.
Run: python -I s55_code_vs_generator.py            Fixture (pre-freeze only): --fixture <scratch dir>
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import subprocess
import sys
import time
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

import n1_habit_table as N  # noqa: E402
from scoreboard.metrics_new import SlotSegmenter  # noqa: E402

SELF = ROOT / "s55_code_vs_generator.py"
STUB = ROOT / "s55_code_vs_generator.prereg.sha256"
S49 = ROOT / "runs" / "s49"
SEED = 20261017
N_SHUF = 200
N_NULL_GAIN = 20
B_BOOT = 500
N_SHUF_BOOT = 20
WALL = 60 * 60
EMPTY = "∅"
FEATS = ["f1_core_F1", "f2_core_core", "f3_core_gain", "f4_prefix_gain", "f5a_core_cover", "f5b_core_heaps",
         "f6_core_sec_nmi", "f7_frame_core"]
CLS = ["CODE", "GEN"]
TRANSLITS = {"ZL3b": "ZL3b_eva", "RF1b": "RF1b", "IT2a": "IT2a"}
FIXTURE = "--fixture" in sys.argv
if FIXTURE:
    OUT_DIR = Path(sys.argv[sys.argv.index("--fixture") + 1])
    OUT = OUT_DIR / "results_s55_fixture.txt"
    RUN_DIR = OUT_DIR / "runs_s55"
    B_BOOT = 50
else:
    OUT = ROOT / "results_s55.txt"
    RUN_DIR = ROOT / "runs" / "s55"

log: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now; `date` unavailable)"


def local_modules():
    out = []
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f:
            continue
        p = Path(f).resolve()
        try:
            rel = p.relative_to(ROOT)
        except ValueError:
            continue
        if p.suffix == ".py":
            out.append(rel.as_posix())
    return sorted(set(out))


def stub_match():
    if not STUB.exists():
        return "NO STUB", []
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    missing = [m for m in local_modules() + ["s55_code_vs_generator.py"] if m not in want]
    ok = bool(want) and not bad and not missing
    msg = "True" if ok else f"False (mismatch: {', '.join(bad) or '-'}; loaded but not in stub: {', '.join(missing) or '-'})"
    return msg, sorted(want)


# ------------------------------------------------------------------ helpers
def split_pages(pages):
    names = [p["id"] for p in pages]
    rng = random.Random(SEED)
    rng.shuffle(names)
    n = int(round(0.8 * len(names)))
    tr = set(names[:n])
    return [p for p in pages if p["id"] in tr], [p for p in pages if p["id"] not in tr]


def mi_codes(a, b):
    """Plug-in MI (bits) of two non-negative int arrays."""
    n = len(a)
    if n == 0:
        return float("nan")
    kb = int(b.max()) + 1
    j, cj = np.unique(a.astype(np.int64) * kb + b, return_counts=True)
    ca = np.bincount(a); cb = np.bincount(b)
    ja, jb = j // kb, j % kb
    p = cj / n
    return float(np.sum(p * np.log2(cj * n / (ca[ja].astype(float) * cb[jb]))))


def entropy_codes(a):
    c = np.bincount(a)
    c = c[c > 0] / len(a)
    return float(-(c * np.log2(c)).sum())


class Bigram:
    """s40.Bigram: add-0.5 unigram, Witten-Bell bigram."""
    def __init__(self, lines):
        self.uni = Counter(s for ln in lines for s in ln)
        self.N = sum(self.uni.values()); self.V = len(self.uni)
        self.big = defaultdict(Counter)
        for ln in lines:
            for a, b in zip(ln, ln[1:]):
                self.big[a][b] += 1
        self.tot = {a: sum(c.values()) for a, c in self.big.items()}

    def pu(self, w):
        return (self.uni.get(w, 0) + 0.5) / (self.N + 0.5 * (self.V + 1))

    def pb(self, a, w):
        c = self.big.get(a)
        if not c:
            return self.pu(w)
        T = len(c)
        return (c.get(w, 0) + T * self.pu(w)) / (self.tot[a] + T)


def gain_pages(train_lines, test_pl):
    """per test page: (n targets, unigram bits, bigram bits)."""
    m = Bigram(train_lines)
    out = defaultdict(lambda: np.zeros(3))
    for pid, ln in test_pl:
        for a, b in zip(ln, ln[1:]):
            out[pid] += (1, -math.log2(m.pu(b)), -math.log2(m.pb(a, b)))
    return out


def gain_stat(arr):
    s = arr.sum(0)
    return (s[1] - s[2]) / s[0] if s[0] else float("nan")


def shuffled_pl(pl, rng):
    out = []
    for pid, ln in pl:
        ln = list(ln); rng.shuffle(ln); out.append((pid, ln))
    return out


def f1_stat(arr):
    r = arr.sum(0)
    return (r[1] - r[2]) / r[0] - (r[4] - r[5]) / r[3]


def heaps(codes):
    n = len(codes)
    if n < 200:
        return float("nan")
    _, first = np.unique(codes, return_index=True)
    first = np.sort(first)
    Ns = np.unique(np.logspace(2, math.log10(n), 30).astype(int))
    V = np.searchsorted(first, Ns, side="left")
    return float(np.polyfit(np.log(Ns), np.log(V), 1)[0])


# ------------------------------------------------------------------ per-text measurement
class TextData:
    def __init__(self, name, pages):
        self.name = name
        pages = [dict(id=str(p["id"]), section=str(p.get("section", "?")), lines=[[w for w in ln if w] for ln in p["lines"]])
                 for p in pages]
        pages = [dict(p, lines=[ln for ln in p["lines"] if ln]) for p in pages]
        self.pages = [p for p in pages if p["lines"]]
        self.tr, self.te = split_pages(self.pages)
        self.seg = SlotSegmenter([w for p in self.tr for ln in p["lines"] for w in ln])
        segc = {}

        def sg(w):
            s = segc.get(w)
            if s is None:
                s = segc[w] = self.seg.segment(w)
            return s
        self.sg = sg
        core_id, frame_id, sec_id = {}, {}, {}
        enc = lambda d, k: d.setdefault(k, len(d))
        self.tr_core_set = set()
        for p in self.tr:
            for ln in p["lines"]:
                for w in ln:
                    self.tr_core_set.add(enc(core_id, sg(w)[1]))
        # per held-out page arrays
        self.hp = []
        for p in self.te:
            cores, frames, lid = [], [], []
            for li, ln in enumerate(p["lines"]):
                for w in ln:
                    pp, cc, ss = sg(w)
                    cores.append(enc(core_id, cc)); frames.append(enc(frame_id, f"{pp}+{ss}")); lid.append(li)
            self.hp.append(dict(id=p["id"], sec=enc(sec_id, p["section"]), cores=np.array(cores, dtype=np.int64),
                                frames=np.array(frames, dtype=np.int64), lid=np.array(lid, dtype=np.int64)))
        self.tr_core_arr = np.array(sorted(self.tr_core_set), dtype=np.int64)
        self.n_core_types = len(core_id)
        # stream lines (strings) for F1 and gain
        self.tr_core_lines = [[sg(w)[1] for w in ln] for p in self.tr for ln in p["lines"]]
        self.te_core_pl = [(p["id"], [sg(w)[1] for w in ln]) for p in self.te for ln in p["lines"]]
        self.tr_pre_lines = [[sg(w)[0] or EMPTY for w in ln] for p in self.tr for ln in p["lines"]]
        self.te_pre_pl = [(p["id"], [sg(w)[0] or EMPTY for w in ln]) for p in self.te for ln in p["lines"]]
        self.tokens = sum(len(ln) for p in self.pages for ln in p["lines"])
        self.te_tokens = sum(len(h["cores"]) for h in self.hp)

    # ---- page-level sufficient rows
    def f1_rows(self):
        real = N.page_sums(self.tr_core_lines, self.te_core_pl)
        rng = random.Random(3)
        sh_tr = [rng.sample(l, len(l)) for l in self.tr_core_lines]
        sh_te = [(p, rng.sample(l, len(l))) for p, l in self.te_core_pl]
        shuf = N.page_sums(sh_tr, sh_te)
        return {p: np.concatenate([real[p], shuf[p]]) for p in real}

    def gain_rows(self, which):
        trl, tepl = (self.tr_core_lines, self.te_core_pl) if which == "core" else (self.tr_pre_lines, self.te_pre_pl)
        rows = gain_pages(trl, tepl)
        rng = random.Random(SEED)
        nul = []
        for _ in range(N_NULL_GAIN):
            str_ = [rng.sample(l, len(l)) for l in trl]
            nul.append(gain_stat(np.array(list(gain_pages(str_, shuffled_pl(tepl, rng)).values()))))
        return rows, float(np.mean(nul)), float(np.std(nul))

    # ---- statistics on a list of held-out page records (point: all held-out pages)
    @staticmethod
    def concat(hps):
        cores = np.concatenate([h["cores"] for h in hps]); frames = np.concatenate([h["frames"] for h in hps])
        lid, off = [], 0
        for h in hps:
            lid.append(h["lid"] + off); off += int(h["lid"].max()) + 1 if len(h["lid"]) else 0
        lid = np.concatenate(lid)
        secs = np.concatenate([np.full(len(h["cores"]), h["sec"], dtype=np.int64) for h in hps])
        pg = np.concatenate([np.full(len(h["cores"]), i, dtype=np.int64) for i, h in enumerate(hps)])
        return cores, frames, lid, secs, pg

    @staticmethod
    def core_core(cores, lid, n_shuf, rng):
        same = lid[1:] == lid[:-1]
        left = np.nonzero(same)[0]; right = left + 1
        if len(left) < 2:
            return float("nan")
        obs = mi_codes(cores[left], cores[right])
        null = []
        for _ in range(n_shuf):
            perm = np.lexsort((rng.random(len(cores)), lid))
            x = cores[perm]
            null.append(mi_codes(x[left], x[right]))
        return obs - float(np.mean(null))

    @staticmethod
    def sec_nmi(cores, secs, pg, n_perm, rng):
        def nmi(s):
            hc, hs = entropy_codes(cores), entropy_codes(s)
            if hs <= 0 or hc <= 0:
                return 0.0
            return mi_codes(cores, s) / math.sqrt(hc * hs)
        if len(np.unique(secs)) < 2:
            return 0.0, 0.0
        obs = nmi(secs)
        page_sec = np.zeros(int(pg.max()) + 1, dtype=np.int64)
        page_sec[pg] = secs
        null = []
        for _ in range(n_perm):
            ps = rng.permutation(page_sec)
            null.append(nmi(ps[pg]))
        return obs - float(np.mean(null)), obs

    @staticmethod
    def frame_core(frames, cores, n_shuf, rng):
        obs = mi_codes(frames, cores)
        null = [mi_codes(frames, rng.permutation(cores)) for _ in range(n_shuf)]
        return obs - float(np.mean(null))

    def cover(self, hps):
        u = np.unique(np.concatenate([h["cores"] for h in hps]))
        return float(np.isin(u, self.tr_core_arr).mean())

    def measure(self, boot=False):
        t = time.time()
        f = {}
        info = {}
        f1r = self.f1_rows()
        f["f1_core_F1"] = f1_stat(np.array(list(f1r.values())))
        gc, gc_mu, gc_sd = self.gain_rows("core")
        gp, gp_mu, gp_sd = self.gain_rows("prefix")
        f["f3_core_gain"] = gain_stat(np.array(list(gc.values())))
        f["f4_prefix_gain"] = gain_stat(np.array(list(gp.values())))
        info["core_gain_excess"] = f["f3_core_gain"] - gc_mu
        info["prefix_gain_excess"] = f["f4_prefix_gain"] - gp_mu
        info["core_gain_z"] = info["core_gain_excess"] / gc_sd if gc_sd > 0 else float("nan")
        info["prefix_gain_z"] = info["prefix_gain_excess"] / gp_sd if gp_sd > 0 else float("nan")
        cores, frames, lid, secs, pg = self.concat(self.hp)
        rng = np.random.default_rng(SEED)
        f["f2_core_core"] = self.core_core(cores, lid, N_SHUF, rng)
        f["f5a_core_cover"] = self.cover(self.hp)
        f["f5b_core_heaps"] = heaps(cores)
        rng = np.random.default_rng(SEED)
        f["f6_core_sec_nmi"], info["sec_nmi_raw"] = self.sec_nmi(cores, secs, pg, N_SHUF, rng)
        rng = np.random.default_rng(SEED)
        f["f7_frame_core"] = self.frame_core(frames, cores, N_SHUF, rng)
        info["n_sections_heldout"] = len(np.unique(secs))
        info["pfx_classes"] = len(self.seg.prefixes); info["sfx_classes"] = len(self.seg.suffixes)
        info["core_types"] = self.n_core_types
        info["secs"] = time.time() - t
        bootarr = None
        if boot:
            ids = [h["id"] for h in self.hp]
            F1 = np.array([f1r.get(i, np.zeros(6)) for i in ids])
            GC = np.array([gc.get(i, np.zeros(3)) for i in ids])
            GP = np.array([gp.get(i, np.zeros(3)) for i in ids])
            brng = np.random.default_rng(SEED)
            bootarr = np.full((B_BOOT, len(FEATS)), np.nan)
            n = len(self.hp)
            for b in range(B_BOOT):
                ix = brng.integers(0, n, n)
                hps = [self.hp[i] for i in ix]
                c_, fr_, l_, s_, p_ = self.concat(hps)
                row = {}
                row["f1_core_F1"] = f1_stat(F1[ix])
                row["f3_core_gain"] = gain_stat(GC[ix])
                row["f4_prefix_gain"] = gain_stat(GP[ix])
                row["f2_core_core"] = self.core_core(c_, l_, N_SHUF_BOOT, brng)
                row["f5a_core_cover"] = self.cover(hps)
                seen, uniq = set(), []
                for i in ix:
                    if i not in seen:
                        seen.add(i); uniq.append(self.hp[i])
                row["f5b_core_heaps"] = heaps(np.concatenate([h["cores"] for h in uniq]))
                row["f6_core_sec_nmi"] = self.sec_nmi(c_, s_, p_, N_SHUF_BOOT, brng)[0]
                row["f7_frame_core"] = self.frame_core(fr_, c_, N_SHUF_BOOT, brng)
                bootarr[b] = [row[k] for k in FEATS]
        return f, info, bootarr


# ------------------------------------------------------------------ classifiers
def prep(Xtr, Xte):
    Xtr = np.array(Xtr, dtype=float); Xte = np.array(Xte, dtype=float)
    if Xte.ndim == 1:
        Xte = Xte[None, :]
    with np.errstate(all="ignore"):
        med = np.nanmedian(np.where(np.isfinite(Xtr), Xtr, np.nan), axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    Xtr = np.where(np.isfinite(Xtr), Xtr, med); Xte = np.where(np.isfinite(Xte), Xte, med)
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    return (Xtr - mu) / sd, (Xte - mu) / sd


def nc_fit_predict(Ztr, ytr, Zte):
    cents = {c: Ztr[[i for i, t in enumerate(ytr) if t == c]].mean(0) for c in CLS}
    out = []
    for z in Zte:
        d = {c: float(np.linalg.norm(z - m)) for c, m in cents.items()}
        out.append((min(d, key=d.get), abs(d["CODE"] - d["GEN"]), d))
    return out


def lr_fit(Ztr, ytr):
    from sklearn.linear_model import LogisticRegression
    m = LogisticRegression(C=1.0, solver="lbfgs", max_iter=10000)  # L2 = the default penalty (sklearn >= 1.8: l1_ratio 0)
    m.fit(Ztr, ytr)
    return m


def lr_predict(m, Zte):
    dfn = m.decision_function(Zte)
    pos = m.classes_[1]
    neg = m.classes_[0]
    pr = m.predict_proba(Zte)
    ic = list(m.classes_).index("CODE")
    return [((pos if v > 0 else neg), abs(float(v)), float(p[ic])) for v, p in zip(dfn, pr)]


def loo(X, y, cols):
    n = len(y)
    res = []
    for i in range(n):
        tr = [j for j in range(n) if j != i]
        Ztr, Zte = prep(X[tr][:, cols], X[i][cols])
        ytr = [y[j] for j in tr]
        nc = nc_fit_predict(Ztr, ytr, Zte)[0]
        lr = lr_predict(lr_fit(Ztr, ytr), Zte)[0]
        res.append(dict(nc=nc[0], ncm=nc[1], lr=lr[0], lrm=lr[1], lrp=lr[2]))
    return res


def auc(pos, neg):
    pos = [x for x in pos if math.isfinite(x)]; neg = [x for x in neg if math.isfinite(x)]
    if not pos or not neg:
        return float("nan")
    s = sum(1.0 if a > b else (0.5 if a == b else 0.0) for a in pos for b in neg)
    return s / (len(pos) * len(neg))


# ------------------------------------------------------------------ data
def load_sidecar(name):
    d = json.loads((S49 / f"{name}.meta.json").read_text(encoding="utf-8"))
    return d["pages"]


def voynich_pages(T):
    by = N.load(TRANSLITS[T])
    return [dict(id=p, section=recs[0]["illus"], lines=[r["words"] for r in recs]) for p, recs in by.items()]


def fixture_corpus():
    """Synthetic only (no real data read): CODE-like = Markov plaintext through a fixed word->codeword book;
    GEN-like = codewords drawn independently from a page-topic-biased pool; a 'VOY' text of each kind."""
    pre = ["qo", "ch", "sh", "o", "d", ""]; suf = ["y", "dy", "in", "aiin", "ol", ""]
    cores = ["k", "t", "ke", "te", "ee", "ckh", "p", "f", "l", "r", "kee", "tch", "cth", "ok", "ot"]
    rng0 = random.Random(1)
    lex = sorted({rng0.choice(pre) + rng0.choice(cores) + rng0.choice(cores) + rng0.choice(suf) for _ in range(3000)})

    def pages_from(words, sec_of):
        pages, k = [], 0
        for pi in range(60):
            lines = []
            for _ in range(10):
                lines.append(words[k:k + 8]); k += 8
            pages.append(dict(id=f"p{pi:03d}", section=sec_of(pi), lines=lines))
        return pages

    def code_text(seed):
        r = random.Random(seed)
        V = 400
        trans = {i: [r.randrange(V) for _ in range(5)] for i in range(V)}
        book = {i: [r.choice(lex) for _ in range(3)] for i in range(V)}
        s, out = 0, []
        for _ in range(4800):
            s = r.choice(trans[s]) if r.random() < 0.7 else r.randrange(V)
            out.append(r.choice(book[s]))
        return pages_from(out, lambda pi: "AB"[pi % 2])

    def gen_text(seed):
        r = random.Random(seed)
        out = []
        for i in range(4800):
            pi = i // 80
            pool = lex[(pi % 3) * 300:(pi % 3) * 300 + 900]
            out.append(r.choice(pool))
        return pages_from(out, lambda pi: "ABC"[pi % 3])
    texts = OrderedDict()
    for i in range(6):
        texts[f"fx_code_{i}"] = ("CODE", code_text(100 + i))
        texts[f"fx_gen_{i}"] = ("GEN", gen_text(200 + i))
    texts["fx_extra_code"] = ("EXTRA", code_text(300))
    voy = OrderedDict([("FX_voy_code", code_text(400)), ("FX_voy_gen", gen_text(401))])
    return texts, voy


# ------------------------------------------------------------------ main
def main():
    t0 = time.time()
    emit("S55: word-level code (K4) vs procedural generator on wrapper-free, layer-split statistics; where does Voynich fall?"
         + (" [SYNTHETIC FIXTURE, not reported]" if FIXTURE else ""))
    emit(f"date: {clock()}")
    sm, stub_files = stub_match()
    emit(f"{SELF.name} sha256={sha256(SELF)}")
    emit(f"prereg stub {STUB.name}" + (f" sha256={sha256(STUB)}" if STUB.exists() else " (absent)") + f"  stub_match={sm}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)}")
    import sklearn
    emit(f"numpy {np.__version__}; sklearn {sklearn.__version__}")
    emit(f"python -I; one CPU process; no new data; seed {SEED}; shuffles {N_SHUF}; gain null {N_NULL_GAIN}; page bootstrap B={B_BOOT} "
         f"({N_SHUF_BOOT} null draws per resample); split 80/20 pages random.Random({SEED})")
    emit()
    if FIXTURE:
        texts, voy_pages = fixture_corpus()
        labels = {n: c for n, (c, _) in texts.items()}
        pages_of = {n: p for n, (_, p) in texts.items()}
        twins = []
    else:
        lab_path = S49 / "labels.json"
        emit(f"labels: {lab_path} sha256={sha256(lab_path)} (s49 printed c7ee6ee63a24b7902bbc44af9236b422a1f1a418e1c94584deb560c2a659300f)")
        lj = json.loads(lab_path.read_text(encoding="utf-8"))
        lab49 = lj["labels"]
        labels = OrderedDict()
        for n, c in lab49.items():
            if c in CLS:
                labels[n] = c
        for n, c in lab49.items():
            if c in ("TWIN_G", "TWIN_L") or n == "ciph_L2layer_ZL3b_s1":
                labels[n] = "EXTRA"
        twins = [tuple(t) for t in lj["twins"]]
        pages_of = {}
        for n in labels:
            p = S49 / f"{n}.meta.json"
            emit(f"  sidecar {p.name} sha256={sha256(p)[:16]}")
            pages_of[n] = load_sidecar(n)
        voy_pages = OrderedDict((f"Voynich_{T}", voynich_pages(T)) for T in TRANSLITS)
        for T, meta in TRANSLITS.items():
            p = ROOT / "data" / "translit" / f"{meta}.meta.json"
            emit(f"  translit {p.name} sha256={sha256(p)[:16]}")
    core12 = [n for n in labels if labels[n] in CLS]
    extras = [n for n in labels if labels[n] == "EXTRA"]
    emit(f"texts: CODE {sum(labels[n] == 'CODE' for n in core12)}, GEN {sum(labels[n] == 'GEN' for n in core12)}, extras {len(extras)}, Voynich {len(voy_pages)}")
    emit()
    flush()

    # ---------------- features
    emit("=== features (held-out pages; segmenter fitted on training pages) ===")
    F, INFO, BOOT = OrderedDict(), {}, {}
    hdr = f"  {'text':30s} {'cls':5s} {'tok':>6s} {'teTok':>5s} {'tr/te':>7s} {'pfx':>3s} {'cores':>5s} " + " ".join(f"{k[:14]:>14s}" for k in FEATS)
    emit(hdr)
    for name in core12 + extras + list(voy_pages):
        if time.time() - t0 > WALL:
            emit(f"STOPPED: wall limit {WALL} s exceeded at {clock()}; partial")
            flush(); sys.exit(2)
        pages = voy_pages[name] if name in voy_pages else pages_of[name]
        td = TextData(name, pages)
        f, info, b = td.measure(boot=name in voy_pages)
        F[name], INFO[name] = f, info
        if b is not None:
            BOOT[name] = b
        cls = labels.get(name, "VOY")
        emit(f"  {name:30s} {cls:5s} {td.tokens:6d} {td.te_tokens:5d} {len(td.tr):3d}/{len(td.te):3d} {info['pfx_classes']:3d} {info['core_types']:5d} "
             + " ".join(f"{f[k]:+14.4f}" for k in FEATS) + f"  [{time.time() - t0:.0f}s]")
        flush()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    with (RUN_DIR / "features.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "class"] + FEATS + ["core_gain_excess", "prefix_gain_excess", "sec_nmi_raw", "n_sections_heldout", "core_types"])
        for n, f in F.items():
            i = INFO[n]
            w.writerow([n, labels.get(n, "VOYNICH")] + [f"{f[k]:.6g}" for k in FEATS]
                       + [f"{i['core_gain_excess']:.6g}", f"{i['prefix_gain_excess']:.6g}", f"{i['sec_nmi_raw']:.6g}", i["n_sections_heldout"], i["core_types"]])
    with (RUN_DIR / "voynich_bootstrap.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "draw"] + FEATS)
        for v, arr in BOOT.items():
            for bi, row in enumerate(arr):
                w.writerow([v, bi] + [f"{x:.6g}" for x in row])
    emit(f"tables: {RUN_DIR / 'features.csv'}; {RUN_DIR / 'voynich_bootstrap.csv'}")
    emit("beside (not features): within-line-shuffle EXCESS of the gains and raw section NMI")
    for n in core12 + list(voy_pages):
        i = INFO[n]
        emit(f"  {n:30s} core gain excess {i['core_gain_excess']:+.4f} (z {i['core_gain_z']:+.1f}); prefix gain excess {i['prefix_gain_excess']:+.4f} "
             f"(z {i['prefix_gain_z']:+.1f}); raw NMI(core;sec) {i['sec_nmi_raw']:.4f} over {i['n_sections_heldout']} held-out sections")
    emit()

    # ---------------- class means, AUC, Voynich values
    emit("=== per-feature class means (sd), AUC (CODE positive vs GEN), Voynich values [page-bootstrap 95 %] ===")
    vn = list(voy_pages)
    emit(f"  {'feature':16s} {'CODE mean (sd)':>20s} {'GEN mean (sd)':>20s} {'AUC':>6s}   " + "   ".join(f"{v:>34s}" for v in vn))
    AUC = {}
    for k in FEATS:
        a = [F[n][k] for n in core12 if labels[n] == "CODE"]; g = [F[n][k] for n in core12 if labels[n] == "GEN"]
        AUC[k] = auc(a, g)
        vs = []
        for v in vn:
            col = BOOT[v][:, FEATS.index(k)]
            col = col[np.isfinite(col)]
            lo, hi = (np.percentile(col, [2.5, 97.5]) if len(col) else (float("nan"), float("nan")))
            vs.append(f"{F[v][k]:+.4f} [{lo:+.4f}, {hi:+.4f}]")
        emit(f"  {k:16s} {np.nanmean(a):+10.4f} ({np.nanstd(a):.4f}) {np.nanmean(g):+10.4f} ({np.nanstd(g):.4f}) {AUC[k]:6.3f}   " + "   ".join(f"{s:>34s}" for s in vs))
    emit("  per-text GEN values (to see which generator sits where):")
    for k in FEATS:
        emit(f"    {k:16s} " + "; ".join(f"{n.replace('gen_', '')} {F[n][k]:+.4f}" for n in core12 if labels[n] == "GEN"))
    emit()
    flush()

    # ---------------- classification
    emit("=== P1: leave-one-text-out over the 12 (CODE 6, GEN 6) ===")
    X = np.array([[F[n][k] for k in FEATS] for n in core12], dtype=float)
    y = [labels[n] for n in core12]
    allc = list(range(len(FEATS)))
    res = loo(X, y, allc)
    k_nc = sum(r["nc"] == t for r, t in zip(res, y)); k_lr = sum(r["lr"] == t for r, t in zip(res, y))
    for n, r, t in zip(core12, res, y):
        emit(f"  {n:30s} true {t:4s}  NC {r['nc']:4s} margin {r['ncm']:.3f} {'ok' if r['nc'] == t else 'WRONG'}   "
             f"LR {r['lr']:4s} |logit| {r['lrm']:.3f} P(CODE) {r['lrp']:.3f} {'ok' if r['lr'] == t else 'WRONG'}")
    p1 = k_nc >= 10 and k_lr >= 10
    emit(f"  NC {k_nc}/12, LR {k_lr}/12 (bar >= 10/12 on both) -> P1 {'PASS' if p1 else 'FAIL'}")
    med_nc = float(np.median([r["ncm"] for r, t in zip(res, y) if r["nc"] == t])) if k_nc else float("nan")
    med_lr = float(np.median([r["lrm"] for r, t in zip(res, y) if r["lr"] == t])) if k_lr else float("nan")
    emit(f"  median LOO margin of correctly classified texts: NC {med_nc:.3f}; LR |logit| {med_lr:.3f}")
    sens = {}
    for drop in ("f6_core_sec_nmi", "f7_frame_core"):
        cols = [i for i, k in enumerate(FEATS) if k != drop]
        rs = loo(X, y, cols)
        sens[drop] = (sum(r["nc"] == t for r, t in zip(rs, y)), sum(r["lr"] == t for r, t in zip(rs, y)))
        emit(f"  sensitivity (reported, not gating) without {drop}: NC {sens[drop][0]}/12, LR {sens[drop][1]}/12; wrong NC: "
             + (", ".join(n for n, r, t in zip(core12, rs, y) if r["nc"] != t) or "none") + "; wrong LR: "
             + (", ".join(n for n, r, t in zip(core12, rs, y) if r["lr"] != t) or "none"))
    emit()

    # ---------------- Voynich + extras
    emit("=== P2: Voynich landing (models fitted on all 12; z on the 12) ===")
    Z12, ZV = prep(X, np.array([[F[v][k] for k in FEATS] for v in vn]))
    m_lr = lr_fit(Z12, y)
    ncv = nc_fit_predict(Z12, y, ZV); lrv = lr_predict(m_lr, ZV)
    emit("  LR coefficients (z units, positive -> " + str(m_lr.classes_[1]) + "): " + ", ".join(f"{k} {c:+.3f}" for k, c in zip(FEATS, m_lr.coef_[0])))
    calls = {}
    for i, v in enumerate(vn):
        nc, lr = ncv[i], lrv[i]
        ok_nc = nc[1] > med_nc; ok_lr = lr[1] > med_lr
        # bootstrap assignment shares
        Xb = BOOT[v]
        _, Zb = prep(X, Xb)
        bnc = Counter(p[0] for p in nc_fit_predict(Z12, y, Zb)); blr = Counter(p[0] for p in lr_predict(m_lr, Zb))
        if not p1:
            c = "does not count (P1 failed)"
        elif nc[0] == lr[0] and ok_nc and ok_lr:
            c = f"COUNTS: {nc[0]}"
        elif ok_nc and not ok_lr:
            c = f"counts on NC only, not robust ({nc[0]})"
        elif ok_lr and not ok_nc:
            c = f"counts on LR only, not robust ({lr[0]})"
        else:
            c = "does not count (margin at or below the median, or classifiers disagree)"
        calls[v] = c
        emit(f"  {v}: NC nearest {nc[0]} margin {nc[1]:.3f} (median {med_nc:.3f}; d CODE {nc[2]['CODE']:.3f}, d GEN {nc[2]['GEN']:.3f});  "
             f"LR {lr[0]} |logit| {lr[1]:.3f} (median {med_lr:.3f}) P(CODE) {lr[2]:.3f}")
        emit(f"      z-vector: " + ", ".join(f"{k} {z:+.2f}" for k, z in zip(FEATS, ZV[i])))
        emit(f"      page bootstrap (B={B_BOOT}) share assigned CODE: NC {bnc['CODE'] / B_BOOT:.3f}, LR {blr['CODE'] / B_BOOT:.3f}")
        emit(f"      assignment: {c}")
    emit()
    if extras:
        emit("=== extras (reported only; projected with the 12-text models) ===")
        ZE = prep(X, np.array([[F[n][k] for k in FEATS] for n in extras]))[1]
        nce = nc_fit_predict(Z12, y, ZE); lre = lr_predict(m_lr, ZE)
        pc = {}
        for n, a, b in zip(extras, nce, lre):
            pc[n] = b[2]
            emit(f"  {n:30s} NC {a[0]:4s} margin {a[1]:.3f};  LR {b[0]:4s} |logit| {b[1]:.3f} P(CODE) {b[2]:.3f}")
        allp = dict(pc)
        for n in core12:
            allp[n] = None
        okc = 0; rows = []
        for g, l in twins:
            pg_ = pc.get(g, lre_p(m_lr, X, F, g) if g in core12 else None)
            pl_ = pc.get(l)
            if pg_ is None or pl_ is None:
                continue
            ok = pl_ > pg_
            okc += ok
            rows.append(f"    {g:24s} P(CODE) {pg_:.3f}  vs  {l:24s} P(CODE) {pl_:.3f} -> {'L more CODE' if ok else 'G more CODE'}")
        if rows:
            emit(f"  twin pairs: L_2layer leans more CODE than its G_2layer twin in {okc}/{len(rows)} pairs (LR P(CODE); gen_G2layer_ZL3b_s1 is a training text, its P from the all-12 model)")
            for r in rows:
                emit(r)
        emit()

    # ---------------- reading
    emit("=== READING (frozen rules) ===")
    if not p1:
        emit(f"P1 FAIL (NC {k_nc}/12, LR {k_lr}/12): code and generator are not separable without line-edge features; "
             "the question cannot be settled by these statistics.")
    else:
        emit(f"P1 PASS (NC {k_nc}/12, LR {k_lr}/12): wrapper-free features can separate the two.")
        for v in vn:
            emit(f"  P2 {v}: {calls[v]}")
    emit(f"VERDICT|s55|p1={'PASS' if p1 else 'FAIL'}|nc={k_nc}/12|lr={k_lr}/12|" + "|".join(f"{v}={calls[v]}" for v in vn))
    emit()
    emit(f"elapsed {time.time() - t0:.0f}s; run ended {clock()}")
    emit(f"outputs: {OUT}; {RUN_DIR}")
    sm2, _ = stub_match()
    emit(f"stub_match at end (all local modules loaded by now): {sm2}")
    flush()


def lre_p(m, X, F, n):
    Z12, Zn = prep(X, np.array([F[n][k] for k in FEATS]))
    return lr_predict(m, Zn)[0][2]


if __name__ == "__main__":
    main()
