"""s40 — the prefix stream as a text: entropy, Zipf slope and held-out next-prefix predictability, against Latin, human
gibberish and two generators put through the same pipeline.

PRE-REGISTERED QUESTION (verbatim; frozen in s40_prefix_stream_as_text.prereg.sha256 before the run):
"Treated as a text of its own (one symbol per word = the word's SlotSegmenter prefix class), is the Voynich prefix
stream language-like (held-out bigram gain over unigram inside the Latin range and above every generator) or
habit-like (inside the generator range)?"

Method (fixed before the run)
  Corpora and page splits (train 80 % / held-out 20 % of pages, names shuffled by random.Random(20261017) exactly as
  g1_edge_joint.split_names: for Voynich this is the 166 / 41 g1_heldout_41 split):
    Voynich ZL3b (decides), RF1b, IT2a via n1_habit_table.load (by path);
    (a) Latin: the 21 CREMMA manuscripts (data/controls_realline/cremma_<ms>.meta.json, base family, run_v2.load_meta
        by path) with >= 1000 tokens, each with its OWN SlotSegmenter fitted on its training pages, plus the pooled
        cremma_all sidecar (own segmenter) printed beside; the "Latin range" = min..max of the held-out prefix bigram
        gain over the qualifying manuscripts;
    (b) gib_realline_pooled (own segmenter);
    (c) generators c2_best and timm_schinner (data/controls_synthetic, own segmenters); "generator range" = min..max
        over the two.
    Every non-Voynich corpus is cut to its first 25,000 tokens (run_v2.subsample) as the board does.
  Segmenter: scoreboard/metrics_new.SlotSegmenter(min_share 0.01, max_len 3, ent_frac 0.5) fitted on the training
    pages' tokens of that corpus, applied to all its pages; empty prefix -> class "∅" (kept as a symbol).
  Streams: prefix stream = per line the sequence of prefix classes; core stream = per line the sequence of cores.
  Descriptives (all pages): unigram entropy H1 (bits/symbol); bigram conditional entropy H(next | prev) over
    within-line adjacent pairs (plug-in); Zipf slope = least-squares slope of log10(freq) on log10(rank) over all
    classes; number of classes.
  Held-out predictability: models fitted on the training pages: unigram p(w) = (c(w) + 0.5) / (N + 0.5 (V + 1));
    bigram p(w | prev) = Witten-Bell interpolation of the within-line pair counts with the unigram
    ((c(prev, w) + T_prev * p(w)) / (c(prev) + T_prev), T_prev = number of distinct followers of prev; unseen prev ->
    unigram).  Evaluated on every within-line adjacent pair (prev, w) of the held-out pages: bits/target for the
    unigram and the bigram; GAIN = unigram bits - bigram bits (>= 0 means the previous symbol helps).
  Within-line shuffle null: 20 draws (random.Random(20261017)); the symbols of every line of train and test are
    permuted within the line; GAIN recomputed; null mean / sd; EXCESS = GAIN - null mean; z.
  The same pipeline on the core stream of every corpus (printed beside; not in the rule).
  Prediction / rule (ZL3b prefix-stream GAIN decides; RF1b / IT2a beside):
    "language-like" if Latin_min <= GAIN_voy <= Latin_max AND GAIN_voy > max(GAIN of c2_best, timm_schinner);
    "habit-like" if gen_min <= GAIN_voy <= gen_max;
    otherwise "neither" (position stated: above Latin max / between the ranges / below both).
    Margins printed: GAIN_voy - Latin_min, Latin_max - GAIN_voy, GAIN_voy - gen_max.
  Gibberish row printed beside (no rule).

Run:    python -I s40_prefix_stream_as_text.py
Writes: results_s40.txt only.
"""
from __future__ import annotations

import hashlib
import importlib.util
import math
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
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

OUT = ROOT / "results_s40.txt"
STUB = ROOT / "s40_prefix_stream_as_text.prereg.sha256"
SELF = ROOT / "s40_prefix_stream_as_text.py"
REAL = ROOT / "data" / "controls_realline"
SYNTH = ROOT / "data" / "controls_synthetic"
TRANSLITS = {"ZL3b": "ZL3b_eva", "RF1b": "RF1b", "IT2a": "IT2a"}
SEED = 20261017
N_SAMPLE = 25000
N_NULL = 20
MIN_TOK = 1000
EMPTY = "∅"
CREMMA = ["Arras-861", "BGO-511", "BIS-193", "CCCC-MSS-165", "CCCC-MSS-236", "CLM13027", "Egerton821", "H318", "Latin16195",
          "Latin6395", "Latin8236", "LaurPlut33.31", "LaurPlut39.34", "LaurPlut53.08", "LaurPlut53.09", "Mazarine915",
          "PalLat373", "Phi_10a135", "SBB_PK_Hdschr25", "UBL758", "WettF0015"]
GENS = ["c2_best", "timm_schinner"]
log: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
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
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now)"


def load_by_path(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


def split_pages(pages):
    """g1.split_names convention on page ids."""
    names = [p["id"] for p in pages]
    rng = random.Random(SEED)
    rng.shuffle(names)
    n = int(round(0.8 * len(names)))
    tr = set(names[:n])
    return [p for p in pages if p["id"] in tr], [p for p in pages if p["id"] not in tr]


def entropy(c):
    n = sum(c.values())
    return -sum(v / n * math.log2(v / n) for v in c.values())


def descriptives(lines):
    uni = Counter(s for ln in lines for s in ln)
    pairs = Counter((a, b) for ln in lines for a, b in zip(ln, ln[1:]))
    prev = Counter(a for a, _ in pairs.elements())
    h1 = entropy(uni)
    h2 = entropy(pairs) - entropy(prev) if pairs else float("nan")
    f = np.array(sorted(uni.values(), reverse=True), dtype=float)
    r = np.arange(1, len(f) + 1)
    slope = float(np.polyfit(np.log10(r), np.log10(f), 1)[0]) if len(f) >= 3 else float("nan")
    return dict(h1=h1, h2=h2, zipf=slope, classes=len(uni), tokens=sum(uni.values()))


class Bigram:
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


def gain(train_lines, test_lines):
    m = Bigram(train_lines)
    bu = bb = 0.0; n = 0
    for ln in test_lines:
        for a, b in zip(ln, ln[1:]):
            bu -= math.log2(m.pu(b)); bb -= math.log2(m.pb(a, b)); n += 1
    return (bu / n, bb / n, (bu - bb) / n) if n else (float("nan"),) * 3


def shuffled(lines, rng):
    out = []
    for ln in lines:
        ln = ln[:]; rng.shuffle(ln); out.append(ln)
    return out


def analyse(name, pages, M, R2):
    tr, te = split_pages(pages)
    seg = M.SlotSegmenter([w for p in tr for ln in p["lines"] for w in ln])
    res = {}
    for stream, slot in (("prefix", 0), ("core", 1)):
        conv = lambda w: (seg.segment(w)[slot] or EMPTY)
        L_all = [[conv(w) for w in ln] for p in pages for ln in p["lines"]]
        L_tr = [[conv(w) for w in ln] for p in tr for ln in p["lines"]]
        L_te = [[conv(w) for w in ln] for p in te for ln in p["lines"]]
        d = descriptives(L_all)
        bu, bb, g = gain(L_tr, L_te)
        rng = random.Random(SEED)
        nul = [gain(shuffled(L_tr, rng), shuffled(L_te, rng))[2] for _ in range(N_NULL)]
        mu, sd = float(np.mean(nul)), float(np.std(nul))
        res[stream] = dict(d, bits_uni=bu, bits_bi=bb, gain=g, null_mu=mu, null_sd=sd, exc=g - mu, z=(g - mu) / sd if sd > 0 else float("inf"),
                           test_pairs=sum(max(0, len(ln) - 1) for ln in L_te))
    res["pages"] = (len(tr), len(te))
    res["inv"] = (len(seg.prefixes), len(seg.suffixes))
    return res


def row(name, r):
    p, c = r["prefix"], r["core"]
    emit(f"  {name:22} | {r['pages'][0]:3d}/{r['pages'][1]:3d} | {p['classes']:4d} {p['h1']:5.2f} {p['h2']:5.2f} {p['zipf']:6.2f} | "
         f"{p['bits_uni']:6.3f} {p['bits_bi']:6.3f} {p['gain']:+7.4f} {p['null_mu']:+7.4f} {p['exc']:+7.4f} {p['z']:+6.1f} | "
         f"{c['classes']:5d} {c['h1']:5.2f} {c['gain']:+7.4f} {c['exc']:+7.4f} {c['z']:+6.1f} | {p['test_pairs']:6d}")


def main() -> int:
    t0 = time.time()
    emit("S40: the prefix stream as a text — entropy, Zipf, held-out next-prefix bigram gain; Voynich vs CREMMA Latin, gibberish, generators")
    emit(f"run started {clock()}")
    emit(f"s40_prefix_stream_as_text.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit(f"split: 80/20 pages, random.Random({SEED}) (g1.split_names convention); segmenter fitted on training pages per corpus; "
         f"GAIN = held-out unigram bits - Witten-Bell bigram bits per within-line target; null = within-line shuffle x{N_NULL}")
    emit("rule (ZL3b prefix GAIN): language-like if inside the Latin per-manuscript range AND above both generators; habit-like if inside the generator range; else neither")
    emit()
    N = load_by_path("n1_habit_table_s40", ROOT / "n1_habit_table.py")
    M = load_by_path("metrics_new_s40", ROOT / "scoreboard" / "metrics_new.py")
    R2 = load_by_path("run_v2_s40", ROOT / "scoreboard" / "run_v2.py")
    hdr = (f"  {'corpus':22} | {'tr/te':>7} | {'pfxC':>4} {'H1':>5} {'H2|':>5} {'zipf':>6} | {'uni':>6} {'bi':>6} {'GAIN':>7} {'null':>7} {'EXCESS':>7} {'z':>6} | "
           f"{'coreC':>5} {'H1':>5} {'GAIN':>7} {'EXCESS':>7} {'z':>6} | {'tePair':>6}")
    results = {}
    emit("=== Voynich (prefix stream | core stream) ===")
    emit(hdr)
    for T, meta in TRANSLITS.items():
        by = N.load(meta)
        pages = [dict(id=p, lines=[r["words"] for r in recs]) for p, recs in by.items()]
        r = analyse(T, pages, M, R2)
        results[T] = r
        row(T, r)
        emit(f"    {T} segmenter (training pages): {r['inv'][0]} prefix candidates, {r['inv'][1]} suffix candidates")
    flush()
    emit()
    emit("=== (a) Latin CREMMA manuscripts, own segmenter each (>= 1000 tokens qualify for the range) ===")
    emit(hdr)
    latin = {}
    for ms in CREMMA:
        _, pages = R2.load_meta(REAL / f"cremma_{ms}.meta.json")
        pages = R2.subsample(pages, N_SAMPLE)
        ntok = sum(len(ln) for p in pages for ln in p["lines"])
        if ntok < MIN_TOK or len(pages) < 5:
            emit(f"  {ms:22} | skipped: {ntok} tokens, {len(pages)} pages")
            continue
        r = analyse(ms, pages, M, R2)
        latin[ms] = r
        row(ms, r)
    _, pool = R2.load_meta(REAL / "cremma_all.meta.json")
    pool_r = analyse("cremma_all", R2.subsample(pool, N_SAMPLE), M, R2)
    row("cremma_all (pool)", pool_r)
    flush()
    emit()
    emit("=== (b) human gibberish on real lines; (c) generators ===")
    emit(hdr)
    _, gp = R2.load_meta(REAL / "gib_realline_pooled.meta.json")
    gib = analyse("gib_realline_pooled", R2.subsample(gp, N_SAMPLE), M, R2)
    row("gib_realline_pooled", gib)
    gens = {}
    for g in GENS:
        _, gpages = R2.load_meta(SYNTH / f"{g}.meta.json")
        gens[g] = analyse(g, R2.subsample(gpages, N_SAMPLE), M, R2)
        row(g, gens[g])
    emit()
    emit("=== READING (pre-registered rule) ===")
    lat = [r["prefix"]["gain"] for r in latin.values()]
    lmin, lmax = min(lat), max(lat)
    gg = {g: r["prefix"]["gain"] for g, r in gens.items()}
    gmin, gmax = min(gg.values()), max(gg.values())
    emit(f"Latin range (prefix GAIN, {len(lat)} manuscripts): [{lmin:+.4f}, {lmax:+.4f}] (pool {pool_r['prefix']['gain']:+.4f}); "
         f"generator range: [{gmin:+.4f}, {gmax:+.4f}] ({', '.join(f'{g} {v:+.4f}' for g, v in gg.items())}); gibberish {gib['prefix']['gain']:+.4f}")
    calls = {}
    for T, r in results.items():
        v = r["prefix"]["gain"]
        if lmin <= v <= lmax and v > gmax:
            c = "language-like"
        elif gmin <= v <= gmax:
            c = "habit-like"
        else:
            pos = "above the Latin max" if v > lmax else ("below both ranges" if v < min(lmin, gmin) else "between the ranges")
            c = f"neither ({pos})"
        calls[T] = c
        emit(f"  {T}: prefix GAIN {v:+.4f} (excess over shuffle {r['prefix']['exc']:+.4f}, z {r['prefix']['z']:+.1f}) -> {c}; "
             f"margins: - Latin min {v - lmin:+.4f}, Latin max - {lmax - v:+.4f}, - gen max {v - gmax:+.4f}; core GAIN {r['core']['gain']:+.4f}")
    z = calls["ZL3b"]
    flips = [T for T in ("RF1b", "IT2a") if calls[T].split(" ")[0] != z.split(" ")[0]]
    emit(f"reading: {z} (ZL3b); {'UNSTABLE on ' + ', '.join(flips) if flips else 'same call on RF1b, IT2a'}")
    gen_core = ", ".join("%s %+.4f" % (g, r["core"]["gain"]) for g, r in gens.items())
    lat_core = [r["core"]["gain"] for r in latin.values()]
    emit(f"core-stream comparison (no rule): Voynich core GAIN {results['ZL3b']['core']['gain']:+.4f}; Latin core GAIN range "
         f"[{min(lat_core):+.4f}, {max(lat_core):+.4f}]; generators {gen_core}; gibberish {gib['core']['gain']:+.4f}")
    emit()
    emit(f"elapsed {time.time() - t0:.1f} s")
    emit(f"run finished {clock()}")
    flush()
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
