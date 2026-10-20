"""r15b.py -- quire drift beyond hand and section (voynich-91b, Roach; blind).

Answers SSR-COMMS-VOYNICH-LEAD-b379-TO-ROACH-VOYNICH91-R15-20261019T025432Z.
Own code. Does not import the lead's scripts or voynich-91's scripts.
The R_within(1) ratio follows the published r10 definition (in-line identity
divided by the exact within-page coincidence). The core inventory below is
this run's own. Cadence excess follows the r12 definition (pooled in-line
lag-1 length correlation minus the within-line-shuffle mean).

LAYOUT, from the IVTFF page header of the transliteration itself
(Zandbergen, IVTFF format 2.0; $H is Lisa Fagin Davis's hand, $I is the
illustration section, $Q is the quire):
  hand    = $H in {1,2,3,4,5}. '@' and missing hands are dropped.
  section = $I in {A,B,C,H,P,S,T,Z}.
  quire   = $Q.
UNIT: a folio with at least 100 word tokens. Tokens are locus type P only
(paragraph running text). Labels, circular text and radial text are out.

WORDS: strip <...> tags and braces, resolve [a:b] to the first alternative,
split on '.' ',' and whitespace. Drop a word that contains '?' or that the
glyph parser cannot consume.
GLYPHS, longest match: cth, ckh, cph, cfh, ch, sh, then one EVA letter in
acdefghiklmnopqrsty.
FEATURES, 40, chosen without reference to quire:
  shares of the 19 most common word-initial glyphs,
  shares of the 19 most common word-final glyphs
  (ties broken by glyph name; the complement is not a feature),
  mean word length in glyphs,
  unigram glyph entropy in bits (log2).
  Ranking uses the pooled tokens of the folios that enter the test.
  It does not depend on the quire labels, so it stays fixed under the null.

TEST A. Residualize each feature by its hand x section cell mean.
Omnibus = sum over features of eta-squared of quire on those residuals.
eta^2 = SS_between(quire) / SS_total. A feature with SS_total ~ 0 contributes 0.
Null: 10,000 permutations of the quire labels within each hand x section cell.
p = (1 + #{null >= observed}) / 10001.
DRIFT if p < 0.01 on ZL3b and p < 0.05 on both RF1b-e and IT2a.

TEST B. The same omnibus on two folio quantities:
  R_within(1) and cadence excess (200 within-line shuffles).
  A folio with either quantity undefined is dropped.
  No DRIFT call is pre-registered for Test B.
MDE: smallest delta in {0.25,0.50,0.75,1.00,1.50,2.00,3.00} such that at
least 8 of 10 synthetic books have p < 0.01. Synthetic model, both quantities:
  y = hand effect N(0, 0.5) + section effect N(0, 0.5) + noise N(0, 1)
      + quire offset N(0, delta).
  SD in the brief is this noise SD (the scale that remains after the
  hand x section residualization). If no grid point reaches 8/10, MDE > 3.

FIXTURE, before any confirmatory statistic on the real tokens.
  Layout = the ZL folios that pass the rules above (labels and the 100-token
  cut). That cut counts tokens; it does not compute Test A or Test B.
  40 Gaussian features. Hand and section effects N(0, 0.5), noise N(0, 1).
  Planted: quire offsets N(0, 0.8) on features 0..12 (13 of 40, one third).
  10 planted books (seeds 15001..15010) and 10 null books (seeds 16001..16010).
  PASS if planted p < 0.01 on at least 8 of 10, and null p < 0.01 on at most 1.
  A separate sanity book (seed 14000) plants N(0, 5) on all 40 features and
  must have p < 0.01. If the sanity book fails, the run is a bug, not
  UNDERPOWERED. If sanity passes and the gate fails, stop and report
  UNDERPOWERED. Do not run the real text.

CORES for R_within(1), one prefix and one suffix, longest match, remainder
must be non-empty (else the whole word is the core):
  prefixes qo ch sh ol or ot ok op yk q o y d s l k
  suffixes iin in dy ey y m n r l s
R_within(1) = (adjacent in-line core matches) / (n_pairs * page coincidence),
page coincidence = sum v(v-1) / (N(N-1)) on that folio. Undefined if the
denominator is 0.
Cadence excess = Pearson correlation of glyph-lengths over adjacent in-line
pairs, minus the mean of 200 within-line shuffles. Undefined if fewer than
20 pairs or a correlation is undefined.

PARALLEL: up to 4 processes, below-normal priority. voynich-91 is already
using 12 workers on r14; 4 keeps this run inside the cap of 12.
MODES: python -I r15b.py selftest | fixture OUT | freeze OUT | real OUT
freeze writes r15b.prereg.sha256 and must run after a passing fixture and
before real. real refuses to start if the stub is missing or does not match,
and refuses to overwrite a results file.
"""
import collections
import ctypes
import datetime
import hashlib
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, ".."))
PATHS = {
    "ZL": os.path.join(DATA, "dl_ZL", "ZL3b-n.txt"),
    "IT": os.path.join(DATA, "dl_IT", "IT2a-n.txt"),
    "RF": os.path.join(DATA, "dl_RF", "RF1b-e.txt"),
}
STUB_REL = {
    "ZL": "../dl_ZL/ZL3b-n.txt",
    "IT": "../dl_IT/IT2a-n.txt",
    "RF": "../dl_RF/RF1b-e.txt",
}
NPERM = 10000
NSHUF = 200
MIN_TOKENS = 100
MIN_PAIRS = 20
N_FEAT = 40
N_EDGE = 19
PLANTED_FEATURES = list(range(13))
WORKERS = 4
BELOW_NORMAL = 0x00004000
SECTIONS = set("ABCHPSTZ")
HANDS = set("12345")
MULTIS = ("cth", "ckh", "cph", "cfh", "ch", "sh")
LETTERS = set("acdefghiklmnopqrsty")
PREFIXES = ("qo", "ch", "sh", "ol", "or", "ot", "ok", "op", "yk",
            "q", "o", "y", "d", "s", "l", "k")
SUFFIXES = ("iin", "in", "dy", "ey", "y", "m", "n", "r", "l", "s")
MDE_GRID = (0.25, 0.50, 0.75, 1.00, 1.50, 2.00, 3.00)
HDR_RE = re.compile(r"^<([A-Za-z0-9]+)>\s*(.*)$")
LOC_RE = re.compile(r"^<([A-Za-z0-9]+)\.([0-9]+),([^>]+)>\s?(.*)$")
TAG_RE = re.compile(r"<[^>]*>")
KNOWN_LINE = "<%>fachys.ykal.ar.ataiin.shol.shory.[cth:oto]res.y.kor.sholdy<!@254;>"
KNOWN_WORDS = ["fachys", "ykal", "ar", "ataiin", "shol", "shory", "cthres", "y", "kor", "sholdy"]


def set_below_normal():
    ctypes.windll.kernel32.SetPriorityClass(
        ctypes.windll.kernel32.GetCurrentProcess(), BELOW_NORMAL)


def now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def refuse_overwrite(path):
    if os.path.exists(path):
        raise SystemExit("refusing to overwrite " + path)


def write_new(path, text):
    refuse_overwrite(path)
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        f.write(text)


# ---------------------------------------------------------------- parsing
def glyphs_of(word):
    out = []
    i = 0
    n = len(word)
    while i < n:
        hit = None
        for m in MULTIS:
            if word.startswith(m, i):
                hit = m
                break
        if hit is not None:
            out.append(hit)
            i += len(hit)
            continue
        c = word[i]
        if c not in LETTERS:
            return None
        out.append(c)
        i += 1
    return out or None


def words_of(text):
    text = TAG_RE.sub("", text).replace("{", "").replace("}", "").replace("'", "")
    buf = []
    i = 0
    while i < len(text):
        if text[i] == "[":
            j = text.find("]", i)
            if j < 0:
                break
            buf.append(text[i + 1:j].split(":")[0])
            i = j + 1
        else:
            buf.append(text[i])
            i += 1
    raw = "".join(buf)
    words = []
    for w in re.split(r"[.,\s]+", raw):
        if not w or "?" in w:
            continue
        if glyphs_of(w) is None:
            continue
        words.append(w)
    return words


def core_of(word):
    rest = word
    for p in PREFIXES:
        if rest.startswith(p) and len(rest) > len(p):
            rest = rest[len(p):]
            break
    for s in SUFFIXES:
        if rest.endswith(s) and len(rest) > len(s):
            rest = rest[:-len(s)]
            break
    return rest if rest else word


def locus_type(code):
    code = code.split(";")[0]
    return code[1] if len(code) >= 2 else ""


def load_translit(path):
    """Return (folios, notes). folios: list of dicts in file order."""
    meta = {}
    lines = collections.defaultdict(list)
    for raw in open(path, encoding="utf-8", errors="replace"):
        s = raw.rstrip("\r\n")
        if not s or s.startswith("#"):
            continue
        m = LOC_RE.match(s)
        if m:
            if locus_type(m.group(3)) == "P":
                lines[m.group(1)].append(words_of(m.group(4)))
            continue
        m = HDR_RE.match(s)
        if m:
            fields = dict(re.findall(r"\$([A-Za-z])=([^ \t<>]+)", m.group(2)))
            meta[m.group(1)] = fields
    folios = []
    dropped = collections.Counter()
    for folio, fields in meta.items():
        hand = fields.get("H", "")
        section = fields.get("I", "")
        quire = fields.get("Q", "")
        if hand not in HANDS or section not in SECTIONS or not quire:
            dropped["label"] += 1
            continue
        word_lines = lines.get(folio, [])
        n_tok = sum(len(w) for w in word_lines)
        item = {
            "folio": folio,
            "hand": hand,
            "section": section,
            "quire": quire,
            "lines": word_lines,
            "n_tok": n_tok,
        }
        if n_tok < MIN_TOKENS:
            dropped["short"] += 1
            continue
        folios.append(item)
        dropped["kept"] += 1
    return folios, dropped


# ---------------------------------------------------------------- quantities
def r_within_1(folio):
    seqs = []
    counts = collections.Counter()
    for words in folio["lines"]:
        cores = [core_of(w) for w in words]
        cores = [c for c in cores if c]
        seqs.append(cores)
        counts.update(cores)
    n = sum(counts.values())
    if n < 2:
        return np.nan
    e = sum(v * (v - 1) for v in counts.values()) / (n * (n - 1))
    if e <= 0:
        return np.nan
    hits = 0
    pairs = 0
    for cores in seqs:
        for a, b in zip(cores, cores[1:]):
            pairs += 1
            hits += (a == b)
    if pairs == 0:
        return np.nan
    return hits / (pairs * e)


def _pearson(left, right):
    if len(left) < 3:
        return np.nan
    x = left - left.mean()
    y = right - right.mean()
    den = np.sqrt(np.dot(x, x) * np.dot(y, y))
    if den <= 0:
        return np.nan
    return float(np.dot(x, y) / den)


def cadence_excess(folio, rng):
    lengths = []
    for words in folio["lines"]:
        lens = []
        for w in words:
            g = glyphs_of(w)
            if g:
                lens.append(len(g))
        if len(lens) >= 2:
            lengths.append(np.asarray(lens, dtype=float))
    if not lengths:
        return np.nan
    left = np.concatenate([a[:-1] for a in lengths])
    right = np.concatenate([a[1:] for a in lengths])
    if len(left) < MIN_PAIRS:
        return np.nan
    obs = _pearson(left, right)
    if np.isnan(obs):
        return np.nan
    nulls = np.empty(NSHUF, dtype=float)
    for i in range(NSHUF):
        shuf = [rng.permutation(a) for a in lengths]
        nulls[i] = _pearson(
            np.concatenate([a[:-1] for a in shuf]),
            np.concatenate([a[1:] for a in shuf]),
        )
    nulls = nulls[~np.isnan(nulls)]
    if len(nulls) == 0:
        return np.nan
    return obs - float(nulls.mean())


def feature_matrix(folios):
    parsed = []
    init_counts = collections.Counter()
    fin_counts = collections.Counter()
    for folio in folios:
        glyph_lines = []
        for words in folio["lines"]:
            gs = []
            for w in words:
                g = glyphs_of(w)
                if g:
                    gs.append(g)
            if gs:
                glyph_lines.append(gs)
                for g in gs:
                    init_counts[g[0]] += 1
                    fin_counts[g[-1]] += 1
        parsed.append(glyph_lines)
    init_keep = [g for g, _ in sorted(init_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:N_EDGE]]
    fin_keep = [g for g, _ in sorted(fin_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:N_EDGE]]
    init_ix = {g: i for i, g in enumerate(init_keep)}
    fin_ix = {g: i for i, g in enumerate(fin_keep)}
    y = np.zeros((len(folios), N_FEAT), dtype=float)
    for r, glyph_lines in enumerate(parsed):
        words = [g for line in glyph_lines for g in line]
        n = len(words)
        if n == 0:
            continue
        for g in words:
            i = init_ix.get(g[0])
            j = fin_ix.get(g[-1])
            if i is not None:
                y[r, i] += 1
            if j is not None:
                y[r, N_EDGE + j] += 1
        y[r, :2 * N_EDGE] /= n
        y[r, 2 * N_EDGE] = float(np.mean([len(g) for g in words]))
        bag = collections.Counter(gly for g in words for gly in g)
        total = sum(bag.values())
        p = np.array(list(bag.values()), dtype=float) / total
        y[r, 2 * N_EDGE + 1] = float(-(p * np.log2(p)).sum())
    names = ["I:" + g for g in init_keep] + ["F:" + g for g in fin_keep] + ["mean_len", "entropy"]
    return y, names


# ---------------------------------------------------------------- omnibus
def residualize(y, hands, sections):
    resid = y.copy()
    cells = collections.defaultdict(list)
    for i, (h, s) in enumerate(zip(hands, sections)):
        cells[(h, s)].append(i)
    for idx in cells.values():
        resid[idx] -= resid[idx].mean(axis=0)
    return resid, cells


def omnibus_p(resid, quires, cells, nperm, seed):
    labels = sorted(set(quires))
    code = {q: i for i, q in enumerate(labels)}
    q = np.array([code[v] for v in quires], dtype=np.int32)
    n, nfeat = resid.shape
    nq = len(labels)
    counts = np.bincount(q, minlength=nq).astype(float)
    ss_tot = np.sum(resid * resid, axis=0)

    def statistics(assign):
        # assign: (m, n) int
        m = assign.shape[0]
        sums = np.zeros((m, nq, nfeat), dtype=float)
        rows = np.arange(m)
        for i in range(n):
            np.add.at(sums, (rows, assign[:, i]), resid[i])
        ss_b = np.sum((sums * sums) / counts[None, :, None], axis=1)
        eta = np.zeros_like(ss_b)
        ok = ss_tot > 1e-18
        eta[:, ok] = ss_b[:, ok] / ss_tot[ok]
        return eta.sum(axis=1)

    obs = float(statistics(q[None, :])[0])
    rng = np.random.default_rng(seed)
    assign = np.tile(q, (nperm, 1))
    for idx in cells.values():
        idx = np.asarray(idx, dtype=int)
        if len(idx) < 2:
            continue
        base = q[idx]
        order = np.argsort(rng.random((nperm, len(idx))), axis=1)
        assign[:, idx] = base[order]
    null = statistics(assign)
    ge = int(np.sum(null >= obs - 1e-12))
    p = (1 + ge) / (nperm + 1)
    return obs, p, ge


def layout_of(folios):
    return [(f["hand"], f["section"], f["quire"]) for f in folios]


def synthetic(layout, nfeat, seed, plant_idx, offset_sd):
    rng = np.random.default_rng(seed)
    n = len(layout)
    y = rng.normal(0.0, 1.0, size=(n, nfeat))
    hands = sorted({h for h, _, _ in layout})
    sections = sorted({s for _, s, _ in layout})
    quires = sorted({q for _, _, q in layout})
    a = {h: rng.normal(0.0, 0.5, size=nfeat) for h in hands}
    b = {s: rng.normal(0.0, 0.5, size=nfeat) for s in sections}
    for i, (h, s, _) in enumerate(layout):
        y[i] += a[h] + b[s]
    if offset_sd > 0 and plant_idx:
        delta = {q: rng.normal(0.0, offset_sd, size=len(plant_idx)) for q in quires}
        plant = np.asarray(plant_idx, dtype=int)
        for i, (_, _, q) in enumerate(layout):
            y[i, plant] += delta[q]
    return y


def eval_book(layout, nfeat, seed, plant_idx, offset_sd, nperm):
    y = synthetic(layout, nfeat, seed, plant_idx, offset_sd)
    hands = [h for h, _, _ in layout]
    sections = [s for _, s, _ in layout]
    quires = [q for _, _, q in layout]
    resid, cells = residualize(y, hands, sections)
    obs, p, ge = omnibus_p(resid, quires, cells, nperm, seed + 17)
    return {"seed": seed, "obs": obs, "p": p, "ge": ge, "drift": int(p < 0.01)}


def _worker(task):
    set_below_normal()
    return eval_book(
        task["layout"], task["nfeat"], task["seed"], task["plant"],
        task["offset"], task["nperm"])


def run_books(layout, jobs):
    tasks = []
    for seed, plant, offset in jobs:
        tasks.append({
            "layout": layout, "nfeat": N_FEAT, "seed": seed,
            "plant": plant, "offset": offset, "nperm": NPERM,
        })
    if len(tasks) == 1:
        return [_worker(tasks[0])]
    with ProcessPoolExecutor(max_workers=WORKERS, initializer=set_below_normal) as pool:
        return list(pool.map(_worker, tasks))


def describe_layout(folios):
    cells = collections.defaultdict(set)
    for f in folios:
        cells[(f["hand"], f["section"])].add(f["quire"])
    multi = sum(1 for qs in cells.values() if len(qs) >= 2)
    folios_multi = 0
    for f in folios:
        if len(cells[(f["hand"], f["section"])]) >= 2:
            folios_multi += 1
    quires = sorted({f["quire"] for f in folios})
    return {
        "n": len(folios),
        "quires": len(quires),
        "cells": len(cells),
        "cells_multi_quire": multi,
        "folios_in_multi": folios_multi,
    }


# ---------------------------------------------------------------- self test
def selftest():
    got = words_of(KNOWN_LINE)
    if got != KNOWN_WORDS:
        raise SystemExit("parser self-test failed: %r" % (got,))
    # eta^2 = 1 when two quires are perfectly separated inside one cell.
    y = np.array([[1.0], [1.0], [-1.0], [-1.0]])
    resid, cells = residualize(y, ["1", "1", "1", "1"], ["H", "H", "H", "H"])
    obs, p, _ = omnibus_p(resid, ["A", "A", "B", "B"], cells, 200, 1)
    if abs(obs - 1.0) > 1e-9:
        raise SystemExit("eta self-test failed: obs=%s" % obs)
    if not (0.2 < p < 0.8):
        raise SystemExit("toy permutation self-test failed: p=%s" % p)
    # a large quire shift on 30 folios must be detected
    layout = [("1", "H", "A" if i < 15 else "B") for i in range(30)]
    y = np.zeros((30, 1))
    y[:15, 0] = 3
    y[15:, 0] = -3
    y += np.random.default_rng(2).normal(0, 0.1, size=y.shape)
    resid, cells = residualize(y, [h for h, _, _ in layout], [s for _, s, _ in layout])
    obs, p, _ = omnibus_p(resid, [q for _, _, q in layout], cells, 500, 3)
    if p >= 0.01:
        raise SystemExit("power self-test failed: p=%s obs=%s" % (p, obs))
    print("selftest OK", now())


# ---------------------------------------------------------------- modes
def load_ready(which):
    folios, dropped = load_translit(PATHS[which])
    return folios, dropped


def fixture(out):
    os.makedirs(out, exist_ok=True)
    selftest()
    folios, dropped = load_ready("ZL")
    info = describe_layout(folios)
    layout = layout_of(folios)
    lines = ["r15b fixture", "clock " + now(), "dropped " + str(dict(dropped)), "layout " + str(info)]
    print("\n".join(lines), flush=True)
    sanity = run_books(layout, [(14000, list(range(N_FEAT)), 5.0)])[0]
    lines.append("sanity seed 14000 all-features offset 5: p=%.6f obs=%.6f drift=%d" % (
        sanity["p"], sanity["obs"], sanity["drift"]))
    print(lines[-1], flush=True)
    if sanity["drift"] != 1:
        lines.append("VERDICT: BUG sanity control did not call DRIFT. Not UNDERPOWERED.")
        write_new(os.path.join(out, "results_fixture.txt"), "\n".join(lines) + "\n")
        raise SystemExit(3)
    planted_jobs = [(15001 + i, PLANTED_FEATURES, 0.8) for i in range(10)]
    null_jobs = [(16001 + i, [], 0.0) for i in range(10)]
    planted = run_books(layout, planted_jobs)
    nulls = run_books(layout, null_jobs)
    for kind, rows in (("planted", planted), ("null", nulls)):
        for row in rows:
            lines.append("%s seed %d p=%.6f obs=%.6f drift=%d" % (
                kind, row["seed"], row["p"], row["obs"], row["drift"]))
    n_plant = sum(r["drift"] for r in planted)
    n_null = sum(r["drift"] for r in nulls)
    lines.append("planted DRIFT %d of 10 (need >= 8)" % n_plant)
    lines.append("null DRIFT %d of 10 (need <= 1)" % n_null)
    ok = n_plant >= 8 and n_null <= 1
    lines.append("VERDICT: %s" % ("PASS" if ok else "UNDERPOWERED"))
    path = os.path.join(out, "results_fixture.txt")
    write_new(path, "\n".join(lines) + "\n")
    print(lines[-3])
    print(lines[-2])
    print(lines[-1])
    if not ok:
        raise SystemExit(2)


def freeze(out):
    stub = os.path.join(out, "r15b.prereg.sha256")
    refuse_overwrite(stub)
    fixture_path = os.path.join(out, "results_fixture.txt")
    text = open(fixture_path, encoding="utf-8").read()
    if "VERDICT: PASS" not in text.splitlines()[-1] and "VERDICT: PASS" not in text:
        raise SystemExit("refusing to freeze: fixture did not PASS")
    code = os.path.join(HERE, "r15b.py")
    lines = [
        "# r15b pre-registration, voynich-91b (Roach). Frozen at (clock): %s" % now(),
        "# Message: SSR-COMMS-VOYNICH-LEAD-b379-TO-ROACH-VOYNICH91-R15-20261019T025432Z",
        "# Fixture PASS before this freeze. See results_fixture.txt.",
        "# Test A: sum of eta^2 of quire on hand x section residuals, 10000 within-cell quire permutations.",
        "# DRIFT if p<0.01 on ZL3b and p<0.05 on RF1b-e and on IT2a.",
        "# Test B: same omnibus on R_within(1) and cadence excess. Report MDE at 80% (p<0.01 on >=8/10) and p. No DRIFT call.",
        "# Verify: grep -v \"^#\" r15b.prereg.sha256 | tr -d '\\r' | sha256sum -c -",
    ]
    files = [("r15b.py", code)]
    for key in ("ZL", "IT", "RF"):
        files.append((STUB_REL[key], PATHS[key]))
    body = []
    for rel, path in files:
        body.append("%s  %s" % (sha256_file(path), rel))
    write_new(stub, "\n".join(lines + body) + "\n")
    log = os.path.join(out, "R15B_PREREG_LOG.txt")
    write_new(log, "FREEZE %s\n%s\n" % (now(), sha256_file(code)))
    print("froze", stub)


def check_stub(out):
    stub = os.path.join(out, "r15b.prereg.sha256")
    if not os.path.isfile(stub):
        raise SystemExit("no stub; refuse real run")
    bad = []
    for line in open(stub, encoding="utf-8"):
        line = line.rstrip("\n").rstrip("\r")
        if not line or line.startswith("#"):
            continue
        digest, rel = line.split(None, 1)
        path = os.path.normpath(os.path.join(out, rel))
        got = sha256_file(path)
        if got != digest:
            bad.append(rel)
    if bad:
        raise SystemExit("stub mismatch: " + " ".join(bad))
    return sha256_file(stub)


def mde_curve(layout):
    rows = []
    for d in MDE_GRID:
        jobs = [(17000 + int(d * 100) * 100 + i, [0, 1], d) for i in range(10)]
        # Test B has 2 features. Plant both. N_FEAT is 40 in eval_book, so use a
        # dedicated 2-column path via synthetic + omnibus directly.
        books = []
        tasks = []
        for seed, _, offset in jobs:
            tasks.append({"layout": layout, "seed": seed, "offset": offset})
        if WORKERS == 1:
            books = [_mde_one(t) for t in tasks]
        else:
            with ProcessPoolExecutor(max_workers=WORKERS, initializer=set_below_normal) as pool:
                books = list(pool.map(_mde_one, tasks))
        hits = sum(b["drift"] for b in books)
        rows.append((d, hits, books))
    mde = None
    for d, hits, _ in rows:
        if hits >= 8:
            mde = d
            break
    return mde, rows


def _mde_one(task):
    set_below_normal()
    layout = task["layout"]
    y = synthetic(layout, 2, task["seed"], [0, 1], task["offset"])
    hands = [h for h, _, _ in layout]
    sections = [s for _, s, _ in layout]
    quires = [q for _, _, q in layout]
    resid, cells = residualize(y, hands, sections)
    obs, p, ge = omnibus_p(resid, quires, cells, NPERM, task["seed"] + 17)
    return {"seed": task["seed"], "obs": obs, "p": p, "drift": int(p < 0.01)}


def real(out):
    stub_hash = check_stub(out)
    lines = [
        "r15b real",
        "clock start " + now(),
        "stub %s" % stub_hash,
        "stub match YES",
    ]
    call_ok = True
    summaries = []
    for key in ("ZL", "IT", "RF"):
        folios, dropped = load_ready(key)
        info = describe_layout(folios)
        lines.append("== %s dropped %s layout %s" % (key, dict(dropped), info))
        y, names = feature_matrix(folios)
        lines.append("%s features %s" % (key, " ".join(names)))
        resid, cells = residualize(
            y, [f["hand"] for f in folios], [f["section"] for f in folios])
        obs, p, ge = omnibus_p(
            resid, [f["quire"] for f in folios], cells, NPERM, 18000 + ord(key[0]))
        thr = 0.01 if key == "ZL" else 0.05
        hit = p < thr
        call_ok = call_ok and hit
        lines.append("TEST A %s obs=%.6f p=%.6f ge=%d threshold=%.2f %s" % (
            key, obs, p, ge, thr, "HIT" if hit else "MISS"))
        # Test B quantities. Shuffles are seeded per folio, independent of Test A.
        b_rows = []
        b_layout = []
        rng = np.random.default_rng(19000 + ord(key[0]))
        for folio in folios:
            rw = r_within_1(folio)
            # dedicated generator so cadence shuffles do not depend on loop order
            # beyond the folio name.
            seed = 20000 + (zlib_crc(folio["folio"]) % 100000) + ord(key[0]) * 1000
            cad = cadence_excess(folio, np.random.default_rng(seed))
            if np.isnan(rw) or np.isnan(cad):
                continue
            b_rows.append((rw, cad))
            b_layout.append((folio["hand"], folio["section"], folio["quire"]))
        lines.append("%s test B folios %d" % (key, len(b_rows)))
        if len(b_rows) < 10:
            lines.append("TEST B %s UNDEFINED too few folios" % key)
            summaries.append((key, p, None, None))
            continue
        yb = np.asarray(b_rows, dtype=float)
        resid_b, cells_b = residualize(
            yb, [h for h, _, _ in b_layout], [s for _, s, _ in b_layout])
        mde, curve = mde_curve(b_layout)
        for d, hits, _ in curve:
            lines.append("MDE grid %s delta %.2f hits %d of 10" % (key, d, hits))
        lines.append("MDE %s %s" % (key, ("%.2f" % mde) if mde is not None else ">3"))
        obs_b, p_b, ge_b = omnibus_p(
            resid_b, [q for _, _, q in b_layout], cells_b, NPERM, 21000 + ord(key[0]))
        lines.append("TEST B %s obs=%.6f p=%.6f ge=%d" % (key, obs_b, p_b, ge_b))
        summaries.append((key, p, p_b, mde))
        del rng
    lines.append("CALL Test A: %s" % ("DRIFT" if call_ok else "NO DRIFT"))
    lines.append("clock end " + now())
    write_new(os.path.join(out, "results_r15b.txt"), "\n".join(lines) + "\n")
    print(lines[-2])
    print(lines[-1])


def zlib_crc(text):
    import zlib
    return zlib.crc32(text.encode("utf-8")) & 0xFFFFFFFF


def main():
    set_below_normal()
    if len(sys.argv) < 2:
        raise SystemExit("mode required")
    mode = sys.argv[1]
    if mode == "selftest":
        selftest()
        return
    if len(sys.argv) != 3:
        raise SystemExit("usage: r15b.py selftest|fixture OUT|freeze OUT|real OUT")
    out = sys.argv[2]
    if mode == "fixture":
        fixture(out)
    elif mode == "freeze":
        freeze(out)
    elif mode == "real":
        real(out)
    else:
        raise SystemExit("unknown mode " + mode)


if __name__ == "__main__":
    main()
