"""s84 -- is the s73 word-stem graph alignment of Voynich above null when scored order-free (leave-one-quire-out)
against >= 100 matched nulls, and is it specific to one reference language?

BACKGROUND: s73 (s73_word_code_solver_and_syllabary.py, results_s73.txt Part 3) aligned Voynich core-transition
graphs to six reference stem graphs (latin, italian, german, occitan, czech, catalan) and scored held-out
half-B stem-transition LL gain per 1,000 pairs: +60.1/+81.6/+35.3 (ZL3b/RF1b/IT2a) vs a null upper bound of +8.4
from only 6 null texts, with a first-half/second-half split in page order and a best language that changes with
transliteration.

QUESTION (frozen): is the Voynich stem-graph alignment above null robustly (order-free, many nulls), and is it
specific to one language?

DESIGN (fixed before any real-data run)
 Solver: s73.solve_stem_code imported unchanged (frequency + transition-graph QAP, fitted on the training side,
   scored on the held-out side: off-diagonal stem-bigram/skip-gram excess LL under the aligned reference lift
   minus 0.11 x unigram KL, per 1,000 pairs).  Reference models: s73.StemLanguageModel on
   s73.load_solver_language_data(lang)[1] (the disjoint 38k LM tokens), M = 200, for the six s73 SOLVER_LANGS.
   Every call uses is_homophonic=True (as s73 Part 3), word_lines_a=None and seg_a=None for EVERY text
   [CHOICE: s73 gave real Voynich ending features but not its core-level nulls; here all texts get core
   transitions + frequencies only, so Voynich, nulls and controls are scored identically], and
   seed = 20261017 + 500 + language index (common random numbers across texts).  s73._STREAM_CACHE is
   cleared before each (text, fold) because it is keyed on id() of the line lists.
 Folds: leave-one-quire-out over the 15 quires with >= 4 pages in ZL3b (quire field of the meta.json, as s67):
   A B C D E F G H I M N O Q S T.  Each fold fits on the other quires (all other pages, quire J included)
   and scores the held-out quire.  Transitions are within line and pooled, so no page or line order enters.
 Segmentation (per transliteration T, per fold q): seg_Tq = s73.SlotSegmenter fitted on the Voynich T words of
   the training quires; applied to every word-level text derived from T (Voynich, shuffles, s57, P4-D1) and,
   for the planted controls, the ZL3b seg_ZL3b,q.  Core-level texts (s67) are used as cores (identity).
 Texts (per transliteration T in ZL3b, RF1b, IT2a; all on T's own page / line / quire skeleton so per-fold
   token counts equal Voynich's exactly):
   VOY_T          the transliteration (s73.load_voynich_meta).
   LSHUF  x 20    words permuted within each line (GPU: argsort of line id + uniform keys, torch cuda Generator).
   BSHUF  x 20    all words of the book permuted (GPU randperm) and poured into T's line skeleton.
                  (Shuffles keep T's core-type count exactly.)
   S67    x 20    s73.generate_s67_core_stream (p_rep 0.15, tau 7, W 20) from T's whole-book core counts
                  (SlotSegmenter on all T words) on T's pages; core level.
   S57    x 20    s57.Producer fitted on all T pages with T's published s57 parameters (runs/s57/fit_T.json),
                  text(seed, T's page line counts), flattened and poured into T's skeleton.
   P4D1   x 25    the 25 s82 P4-D1 letter-in-core / chunk-in-core instances that MATCHED the matched-K core-order
                  curve (runs/s82/calls.json 'P4D1' 'matches'), regenerated with s82.p4_text, flattened and poured
                  into T's skeleton.
   -> 105 null texts per transliteration (315 in all), five families.  Core-type counts of every text are
   recorded (whole text, whole-book T segmenter); S67/S57/P4D1 type counts are NOT forced equal to Voynich's
   [deviation, reported per family]; the solver only aligns the 200 most frequent training cores.
 Positive controls: s73 planted W3 stem codes (s73.generate_stem_cipher('W3', ...), seed 20261017 + 100 x
   (language index + 1) as s73) of the six reference languages, wrapper tables s73.build_voynich_wrapper_tables
   on all ZL3b pages with a whole-ZL3b SlotSegmenter, laid on the exact ZL3b skeleton (34,857 tokens); scored on
   the same folds with seg_ZL3b,q and compared with the ZL3b null pool.
 Per (text, fold): gains g[lang] for the 6 languages; max gain G = max_lang g; best language argmax.
 Text-level language statistics: modal best language L (most folds; tie -> higher mean gain over folds);
   n_L = folds where L is best; margin = mean over the 15 folds of (g[L] - max_{l != L} g[l]).
 Null percentiles: torch.quantile (linear, q = 0.95) on the GPU over the 105 null texts of the same T.

PRE-REGISTERED CALLS
 C1 (above null): for each T, fold f passes iff G_VOY_T,f > p95_f(null max gains of T).  C1 TRUE iff passes on
    >= 10/15 folds on all three transliterations.
 C2 (language specificity): TRUE iff there is a language L that is the modal best language with n_L >= 10/15 on
    at least 2 of the 3 transliterations AND on each of those transliterations Voynich's margin (as defined above)
    exceeds the 95th percentile of the null texts' margins (same T).
 C3 (controls): a planted control passes iff it passes the C1 fold rule (>= 10/15 folds above the ZL3b null p95)
    AND its modal best language is its own language with n_L >= 10/15 AND its margin > ZL3b null margin p95.
    C3 TRUE iff >= 5 of the 6 controls pass [CHOICE, disclosed: s73's planted W3 latin had a full-size margin of
    only +4.38 (results_s73.txt), so one weak control is tolerated; the all-6 count is printed beside].
 Readings (exactly one):
   C3 false            -> "inconclusive: controls failed"
   C1 and C2 true      -> "Voynich stems align with <language> above every null: candidate for word-level decoding"
   C1 true, C2 false   -> "language-like stem structure, no specific language"
   C1 false            -> "stem alignment not above null when order-free"
 If C1 and C2 pass: the top 30 aligned Voynich-core -> reference-stem pairs for L (count = folds x
   transliterations in which the pair was assigned), descriptive only.

FIXTURE (--synth84; own flag because s55 parses "--fixture" from argv at import; synthetic; reads no manuscript, corpus or cipher file; writes only runs/s84/fixture.txt):
  6 synthetic languages, each 260 four-letter stems + Latin endings, first-order chain: with prob 0.5 one of 6
  language-specific successors, else a Zipf(1.0) draw; reference LM 38k tokens per language; 15 quires x 13
  pages x 20 lines x (6..12) words; identity segmentation (core-level texts).  Planted: languages 0 and 3 encoded
  by a fixed stem -> core substitution (fresh plaintext).  Null families (10 each): within-line shuffle, book
  shuffle of the planted language-0 text, i.i.d. unigram draws of its cores (s67 stand-in), a local-copy producer
  (p_copy 0.15 from the last 20 tokens, else unigram; s57 stand-in).  Checks: FA each planted text exceeds EVERY
  family's per-fold p95 on >= 12/15 folds; FB its own language is best on >= 10/15 folds; FC a fresh within-line
  shuffle of the planted text does NOT meet FA.  FIXTURE PASS iff FA, FB (both planted texts) and FC.
  Fixture history before the freeze: pass 1 used 3 successors per stem: FA 15/15 and 15/15, FC 2/15, but FB failed
  for language 0 (own language best on 9/15; wrong languages scored +250..+370 vs own +280..+380: with sparse random
  graphs the QAP fits ANY structured reference graph, so held-out gain is largely not language-specific).  A scratchpad
  probe of the planted texts only (successor prob/count 0.3/3, 0.3/6, 0.5/6: own best 12,6 / 6,3 / 13,13 of 15) chose
  0.5/6.  Only the fixture's chain changed; no real-data rule changed.  This solver property is why C2 compares the
  margin with the null margins rather than with zero.
COMPUTE: 4 worker processes (BelowNormal, single-threaded BLAS).  GPU (torch cuda): shuffle permutations and
  the null percentile / permutation scoring; s73's solver (alignment search) runs on CPU numpy because it is
  imported unchanged (the brief forbids reimplementing it).  On any GPU error torch CPU is used and recorded.
Disclosed pre-freeze looks: a scratchpad timing probe loaded the three transliterations (printed per-quire page /
  token counts), fitted one fold's segmenter and timed solve_stem_code on ZL3b fold A vs latin printing only time
  and n_pairs_b (no gain); a smoke test generated one P4-D1 text (s82.p4_text K1 latin_caesar 1) printing sizes.
Constraints: python -I; writes ONLY results_s84.txt and runs/s84/*.
Run: python -I s84_stem_alignment_loqo.py   Fixture: --synth84   Stub helper: --list-locals
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
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import s73_word_code_solver_and_syllabary as S73  # noqa: E402
import s57_local_memory_model as S57  # noqa: E402
import s82_cipher_rescore_matched_k as S82  # noqa: E402

SELF = ROOT / "s84_stem_alignment_loqo.py"
STUB = ROOT / "s84_stem_alignment_loqo.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s84"
FIXTURE = "--synth84" in sys.argv
LIST_LOCALS = "--list-locals" in sys.argv
OUT = RUN_DIR / "fixture.txt" if FIXTURE else ROOT / "results_s84.txt"
SEED = 20261017
WORKERS = 4
TRANSLITS = OrderedDict([("ZL3b", "ZL3b_eva.meta.json"), ("RF1b", "RF1b.meta.json"), ("IT2a", "IT2a.meta.json")])
LANGS = list(S73.SOLVER_LANGS.keys())
N_FAM = OrderedDict([("LSHUF", 20), ("BSHUF", 20), ("S67", 20), ("S57", 20)])  # + P4D1 (25 from s82)
MIN_FOLDS_C1 = 10
MIN_FOLDS_LANG = 10
Q95 = 0.95
log: list[str] = []
T0 = time.time()


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
    return time.strftime("%Y-%m-%d %H:%M:%S") + " (time.strftime)"


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
        if p.suffix == ".py" and p.is_file():
            out.append(rel.as_posix())
    return sorted(set(out))


def stub_match():
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
    missing = [m for m in local_modules() if m not in want]
    ok = bool(want) and not bad and not missing
    return "True" if ok else f"False (mismatch: {', '.join(bad) or '-'}; loaded but not in stub: {', '.join(missing) or '-'})"


def set_low_priority():
    try:
        import psutil
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if sys.platform == "win32" else 10)
        return "BelowNormal (psutil)"
    except Exception as e:  # noqa: BLE001
        return f"priority not set ({e})"


# ======================================================================= GPU helpers (torch)
DEVICE_NOTES: list[str] = []


def torch_dev():
    import torch
    try:
        if torch.cuda.is_available():
            torch.zeros(1, device="cuda")
            return torch, torch.device("cuda")
    except Exception as e:  # noqa: BLE001
        DEVICE_NOTES.append(f"cuda init failed ({type(e).__name__}: {e}); torch CPU used")
    return torch, torch.device("cpu")


def _gen(torch, dev, seed):
    g = torch.Generator(device=dev)
    g.manual_seed(int(seed))
    return g


def gpu_line_shuffle(pages, seed):
    """Permute words within each line: argsort(line id + U(0,1)) on the GPU."""
    torch, dev = torch_dev()
    words = [w for p in pages for ln in p["lines"] for w in ln]
    lid = [i for i, ln in enumerate(ln for p in pages for ln in p["lines"]) for _ in ln]
    try:
        g = _gen(torch, dev, seed)
        key = torch.tensor(lid, dtype=torch.float64, device=dev) + torch.rand(len(lid), generator=g, device=dev, dtype=torch.float64)
        perm = torch.argsort(key).cpu().numpy()
    except Exception as e:  # noqa: BLE001
        DEVICE_NOTES.append(f"line shuffle GPU error ({type(e).__name__}); torch CPU")
        g = _gen(torch, torch.device("cpu"), seed)
        key = torch.tensor(lid, dtype=torch.float64) + torch.rand(len(lid), generator=g, dtype=torch.float64)
        perm = torch.argsort(key).numpy()
    flat = [words[i] for i in perm]
    return pour(flat, pages)


def gpu_book_shuffle(pages, seed):
    torch, dev = torch_dev()
    words = [w for p in pages for ln in p["lines"] for w in ln]
    try:
        perm = torch.randperm(len(words), generator=_gen(torch, dev, seed), device=dev).cpu().numpy()
    except Exception as e:  # noqa: BLE001
        DEVICE_NOTES.append(f"book shuffle GPU error ({type(e).__name__}); torch CPU")
        perm = torch.randperm(len(words), generator=_gen(torch, torch.device("cpu"), seed)).numpy()
    return pour([words[i] for i in perm], pages)


def gpu_quantile(rows, q=Q95):
    """rows: list of equal-length lists -> per-column quantile (torch.quantile, linear)."""
    torch, dev = torch_dev()
    try:
        t = torch.tensor(rows, dtype=torch.float64, device=dev)
        return torch.quantile(t, q, dim=0).cpu().numpy()
    except Exception as e:  # noqa: BLE001
        DEVICE_NOTES.append(f"quantile GPU error ({type(e).__name__}); torch CPU")
        return torch.quantile(torch.tensor(rows, dtype=torch.float64), q, dim=0).numpy()


def gpu_exceed_p(obs, null_vals):
    """(1 + #{null >= obs}) / (n + 1), counted on the GPU."""
    torch, dev = torch_dev()
    try:
        t = torch.tensor(null_vals, dtype=torch.float64, device=dev)
        k = int((t >= float(obs)).sum().item())
    except Exception:  # noqa: BLE001
        k = int(np.sum(np.asarray(null_vals) >= obs))
    return (1 + k) / (len(null_vals) + 1)


# ======================================================================= text helpers
def pour(flat, skel_pages):
    out, i = [], 0
    n = len(flat)
    for p in skel_pages:
        lines = []
        for ln in p["lines"]:
            lines.append([flat[(i + k) % n] for k in range(len(ln))])
            i += len(ln)
        out.append(dict(id=p["id"], quire=p["quire"], lines=lines))
    return out


def lines_to_pages(core_lines, skel_pages):
    out, i = [], 0
    for p in skel_pages:
        k = len(p["lines"])
        out.append(dict(id=p["id"], quire=p["quire"], lines=core_lines[i:i + k]))
        i += k
    return out


def fold_quires(pages):
    c = Counter(p["quire"] for p in pages)
    return sorted(q for q, n in c.items() if n >= 4)


# ======================================================================= scoring (worker side)
_W: dict = {}


def worker_init():
    set_low_priority()
    try:
        from threadpoolctl import threadpool_limits
        _W["tpl"] = threadpool_limits(1)
    except ImportError:
        pass


def lang_models():
    if "lm" not in _W:
        lm = OrderedDict()
        for lang in LANGS:
            _, lm_w = S73.load_solver_language_data(lang)
            lm[lang] = S73.StemLanguageModel(lang, lm_w, m_stems=S73.M_STEMS_SOLVE)
        _W["lm"] = lm
    return _W["lm"]


def voy(T):
    key = ("voy", T)
    if key not in _W:
        inv = _W.setdefault("inv", S73.load_folio_inventory())
        pages, _, _ = S73.load_voynich_meta(TRANSLITS[T], inv)
        pages = [dict(id=p["id"], quire=p["quire"], lines=p["lines"]) for p in pages]
        allw = [w for p in pages for ln in p["lines"] for w in ln]
        _W[key] = dict(pages=pages, seg_all=S73.SlotSegmenter(allw), segs={})
    return _W[key]


def fold_seg(T, q):
    v = voy(T)
    if q not in v["segs"]:
        v["segs"][q] = S73.SlotSegmenter([w for p in v["pages"] if p["quire"] != q for ln in p["lines"] for w in ln])
    return v["segs"][q]


def score_text(pages, kind, folds, seg_for_fold, lms, want_map=False):
    """-> dict(gains: {q: [6]}, held_tok: {q: n}, maps: {q: {lang: [(core, stem, freq_a)]}})."""
    gains, held, maps = OrderedDict(), OrderedDict(), OrderedDict()
    for q in folds:
        tr = [ln for p in pages if p["quire"] != q for ln in p["lines"]]
        te = [ln for p in pages if p["quire"] == q for ln in p["lines"]]
        if kind == "words":
            seg = seg_for_fold(q)
            ca = [[seg.segment(w)[1] for w in ln] for ln in tr]
            cb = [[seg.segment(w)[1] for w in ln] for ln in te]
        else:
            ca, cb = [list(ln) for ln in tr], [list(ln) for ln in te]
        held[q] = sum(len(ln) for ln in te)
        S73._STREAM_CACHE.clear()
        row, mp = [], {}
        for c_idx, (lang, lm) in enumerate(lms.items()):
            r = S73.solve_stem_code(ca, cb, lm, word_lines_a=None, seg_a=None, n_active_cores=S73.M_STEMS_SOLVE,
                                    is_homophonic=True, seed=SEED + 500 + c_idx)
            row.append(float(r["heldout_ll_gain_per_1k"]))
            if want_map:
                st = S73._STREAM_CACHE[next(iter(S73._STREAM_CACHE))]
                mp[lang] = [(c, lm.top_stems[int(r["best_pi"][u])], float(st["freq_a"][u]))
                            for u, c in enumerate(st["prim_cores"]) if not c.startswith("__pad_")]
        S73._STREAM_CACHE.clear()
        gains[q] = row
        if want_map:
            maps[q] = mp
    return dict(gains=gains, held_tok=held, maps=maps)


def core_types(pages, kind, seg):
    if kind == "words":
        return len({seg.segment(w)[1] for p in pages for ln in p["lines"] for w in ln})
    return len({c for p in pages for ln in p["lines"] for c in ln})


def build_text(spec):
    """spec = (T, family, idx, payload) -> (pages, kind)."""
    T, fam, idx, payload = spec
    v = voy(T)
    sk = v["pages"]
    if fam == "VOY":
        return sk, "words"
    if fam in ("LSHUF", "BSHUF"):
        return payload, "words"  # built on the GPU in the main process
    if fam == "S67":
        cl = S73.generate_s67_core_stream([dict(lines=p["lines"]) for p in sk], v["seg_all"], sk, seed=SEED + 3000 + idx)
        return lines_to_pages(cl, sk), "cores"
    if fam == "S57":
        prm = json.loads((ROOT / "runs" / "s57" / f"fit_{T}.json").read_text(encoding="utf-8"))["params"]
        prod = S57.Producer([p["lines"] for p in sk], v["seg_all"])
        prod.set_params(prm)
        txt = prod.text(SEED + 4000 + idx, [len(p["lines"]) for p in sk])
        return pour([w for lines in txt for ln in lines for w in ln], sk), "words"
    if fam == "P4D1":
        f, name, seed = payload
        pg = S82.p4_text(f, name, seed)
        return pour([w for _, ls in pg for ln in ls for w in ln], sk), "words"
    if fam == "CTRL":
        lang = payload
        if "ctrl_wtab" not in _W:
            _W["ctrl_wtab"] = S73.build_voynich_wrapper_tables(sk, v["seg_all"])
        lm = lang_models()[lang]
        pt_w, _ = S73.load_solver_language_data(lang)
        ciph = S73.generate_stem_cipher("W3", pt_w, lm, [dict(p, hand="1", lang="A") for p in sk], _W["ctrl_wtab"],
                                        seed=SEED + 100 * (LANGS.index(lang) + 1))
        return [dict(id=p["id"], quire=p["quire"], lines=p["lines"]) for p in ciph["pages"]], "words"
    raise ValueError(fam)


def job(spec):
    t = time.time()
    T, fam, idx, _ = spec
    pages, kind = build_text(spec)
    folds = fold_quires(voy("ZL3b")["pages"])
    res = score_text(pages, kind, folds, lambda q: fold_seg(T, q), lang_models(), want_map=(fam == "VOY"))
    res.update(name=spec_name(spec), T=T, fam=fam, idx=idx, kind=kind, secs=time.time() - t,
               types=core_types(pages, kind, voy(T)["seg_all"]), tokens=sum(len(ln) for p in pages for ln in p["lines"]))
    return res


def spec_name(spec):
    T, fam, idx, payload = spec
    if fam == "VOY":
        return f"VOY_{T}"
    if fam == "P4D1":
        return f"P4D1_{T}_{payload[0]}_{payload[1]}_s{payload[2]}"
    if fam == "CTRL":
        return f"CTRL_W3_{payload}"
    return f"{fam}_{T}_{idx:02d}"


def run_jobs(specs, fn=None):
    from concurrent.futures import ProcessPoolExecutor
    out = []
    with ProcessPoolExecutor(max_workers=WORKERS, initializer=worker_init) as ex:
        for r in ex.map(fn or job, specs):
            out.append(r)
            emit(f"  done {r['name']:40s} [{r['secs']:.0f}s, types {r['types']}, tokens {r['tokens']}]  t+{time.time() - T0:.0f}s")
            flush()
    return out


# ======================================================================= statistics
def text_stats(gains, folds, langs):
    G = np.array([gains[q] for q in folds])  # folds x langs
    best = G.argmax(axis=1)
    cnt = Counter(best.tolist())
    top = max(cnt.values())
    cands = [k for k, v in cnt.items() if v == top]
    L = max(cands, key=lambda k: G[:, k].mean())
    others = np.delete(G, L, axis=1).max(axis=1)
    return dict(G=G, gmax=G.max(axis=1), best=[langs[b] for b in best], modal=langs[L], n_modal=int(cnt[L]),
                margin=float(np.mean(G[:, L] - others)), fold_margin=(G[:, L] - others))


def null_summary(nulls, folds):
    st = [text_stats(r["gains"], folds, LANGS) for r in nulls]
    p95 = gpu_quantile([s["gmax"].tolist() for s in st])
    m95 = float(gpu_quantile([[s["margin"]] for s in st])[0])
    return st, p95, m95


# ======================================================================= fixture
FX_LETTERS_C = "bcdfgklmnprstvz"
FX_LETTERS_V = "aeiou"
FX_ENDS = ["us", "um", "is", "em", "am", "as"]
FX_PSUCC = 0.5
FX_NSUCC = 6


def fx_world():
    if "fx" in _W:
        return _W["fx"]
    rng = random.Random(7)
    stems = []
    seen = set()
    while len(stems) < 260:
        s = rng.choice(FX_LETTERS_C) + rng.choice(FX_LETTERS_V) + rng.choice(FX_LETTERS_C) + rng.choice(FX_LETTERS_C)
        if s in seen or any(S73.stem_and_ending(s + e) != (s, e) for e in FX_ENDS):
            continue
        seen.add(s)
        stems.append(s)
    zipf = np.array([1.0 / (i + 1.0) for i in range(260)])
    zipf /= zipf.sum()
    langs = []
    for li in range(6):
        r = np.random.default_rng(100 + li)
        succ = r.integers(0, 260, size=(260, FX_NSUCC))
        langs.append(succ)

    def gen(li, n, seed):
        r = np.random.default_rng(seed)
        succ = langs[li]
        cur = int(r.choice(260, p=zipf))
        out = []
        draws = r.choice(260, size=n, p=zipf)
        u = r.random(n)
        k = r.integers(0, FX_NSUCC, size=n)
        for i in range(n):
            cur = int(succ[cur, k[i]]) if u[i] < FX_PSUCC else int(draws[i])
            out.append(cur)
        return out

    lms = OrderedDict()
    for li in range(6):
        ids = gen(li, 38000, 1000 + li)
        er = random.Random(2000 + li)
        lms[f"fx{li}"] = S73.StemLanguageModel(f"fx{li}", [stems[i] + er.choice(FX_ENDS) for i in ids], m_stems=200)
    sr = random.Random(11)
    pages = []
    for qi in range(15):
        q = chr(ord("A") + qi)
        for pi in range(13):
            pages.append(dict(id=f"{q}{pi}", quire=q, lines=[[None] * sr.randint(6, 12) for _ in range(20)]))
    n_tok = sum(len(ln) for p in pages for ln in p["lines"])
    cr = random.Random(13)
    codes = [f"k{x:03d}" for x in cr.sample(range(1000), 260)]
    planted = {}
    for li in (0, 3):
        ids = gen(li, n_tok, 5000 + li)
        planted[li] = pour([codes[i] for i in ids], pages)
    _W["fx"] = dict(lms=lms, pages=pages, planted=planted)
    return _W["fx"]


def fx_build(spec):
    fam, idx = spec
    W_ = fx_world()
    base = W_["planted"][0]
    if fam == "PLANT":
        return W_["planted"][idx]
    if fam == "LSHUF":
        return gpu_line_shuffle(base, 70000 + idx)
    if fam == "BSHUF":
        return gpu_book_shuffle(base, 71000 + idx)
    toks = [c for p in base for ln in p["lines"] for c in ln]
    cnt = Counter(toks)
    vals, wts = list(cnt), np.array(list(cnt.values()), dtype=float)
    wts /= wts.sum()
    r = np.random.default_rng(72000 + idx)
    if fam == "IID":
        return pour([vals[i] for i in r.choice(len(vals), size=len(toks), p=wts)], base)
    if fam == "COPY":
        out = []
        for i in range(len(toks)):
            if out and r.random() < 0.15:
                out.append(out[-int(r.integers(1, min(20, len(out)) + 1))])
            else:
                out.append(vals[int(r.choice(len(vals), p=wts))])
        return pour(out, base)
    raise ValueError(fam)


def fx_job(spec):
    t = time.time()
    pages = fx_build(spec)
    W_ = fx_world()
    folds = fold_quires(W_["pages"])
    res = score_text(pages, "cores", folds, None, W_["lms"])
    res.update(name=f"FX_{spec[0]}_{spec[1]}", fam=spec[0], idx=spec[1], secs=time.time() - t,
               types=len({c for p in pages for ln in p["lines"] for c in ln}), tokens=sum(len(ln) for p in pages for ln in p["lines"]))
    return res


def run_fixture():
    emit("s84 synthetic fixture (no real data read)")
    emit(f"Run timestamp: {clock()}; priority {set_low_priority()}")
    torch, dev = torch_dev()
    emit(f"device: {dev} (shuffles, quantiles); solver: s73 numpy on CPU")
    fams = ["LSHUF", "BSHUF", "IID", "COPY"]
    specs = [(f, i) for f in fams for i in range(10)] + [("PLANT", 0), ("PLANT", 3), ("LSHUF", 999)]
    res = run_jobs(specs, fn=fx_job)
    folds = fold_quires(fx_world()["pages"])
    fxl = [f"fx{i}" for i in range(6)]
    by = defaultdict(list)
    for r in res:
        if r["fam"] in fams and r["idx"] != 999:
            by[r["fam"]].append(r)
    p95 = {f: gpu_quantile([text_stats(r["gains"], folds, fxl)["gmax"].tolist() for r in by[f]]) for f in fams}

    def beats_all(r):
        g = text_stats(r["gains"], folds, fxl)["gmax"]
        return int(sum(all(g[i] > p95[f][i] for f in fams) for i in range(len(folds))))

    ok = True
    for r in res:
        if r["fam"] == "PLANT":
            s = text_stats(r["gains"], folds, fxl)
            nb = beats_all(r)
            own = sum(b == f"fx{r['idx']}" for b in s["best"])
            fa, fb = nb >= 12, own >= 10
            ok &= fa and fb
            emit(f"  planted fx{r['idx']}: beats every family p95 on {nb}/15 folds (FA {'PASS' if fa else 'FAIL'}); "
                 f"own language best on {own}/15 (FB {'PASS' if fb else 'FAIL'}); median max gain {np.median(s['gmax']):+.1f}")
        if r["fam"] == "LSHUF" and r["idx"] == 999:
            nb = beats_all(r)
            fc = nb < 12
            ok &= fc
            emit(f"  fresh line-shuffled planted text: beats every family p95 on {nb}/15 folds (FC {'PASS' if fc else 'FAIL'})")
    for f in fams:
        emit(f"  family {f}: per-fold p95 median {np.median(p95[f]):+.1f}")
    if DEVICE_NOTES:
        emit("  device notes: " + "; ".join(sorted(set(DEVICE_NOTES))))
    emit(f"FIXTURE {'PASS' if ok else 'FAIL'}  (elapsed {time.time() - T0:.0f}s)")
    flush()


# ======================================================================= main run
def p4d1_matches():
    d = json.loads((ROOT / "runs" / "s82" / "calls.json").read_text(encoding="utf-8"))
    out = []
    for nm in d["calls"]["P4D1"]["matches"]:
        fam, rest = nm.split("_", 1)
        name, s = rest.rsplit("_s", 1)
        out.append((fam, name, int(s)))
    return out


def main():
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    prio = set_low_priority()
    torch, dev = torch_dev()
    emit("s84 -- s73 word-stem alignment, leave-one-quire-out, >= 100 matched nulls per transliteration, language call")
    emit(f"Run timestamp : {clock()}")
    emit(f"Python        : {sys.version.split()[0]} (isolated -I={sys.flags.isolated}); torch {torch.__version__}")
    emit(f"device        : {dev}{' (' + torch.cuda.get_device_name(0) + ')' if dev.type == 'cuda' else ''} for shuffles, "
         f"quantiles and exceedance counts; s73 solver (alignment search) on CPU numpy, imported unchanged")
    emit(f"workers       : {WORKERS} processes, {prio}, single-threaded BLAS")
    emit(f"{SELF.name} sha256={sha256(SELF)}")
    emit(f"prereg stub {STUB.name} sha256={sha256(STUB) if STUB.exists() else '-'}  stub_match={stub_match()}")
    for m in local_modules():
        emit(f"  local import {m} sha256={sha256(ROOT / m)[:16]}")
    emit()
    flush()

    # ---- build the specs (shuffles on the GPU in this process)
    zl = voy("ZL3b")
    folds = fold_quires(zl["pages"])
    emit(f"folds (quires with >= 4 ZL3b pages): {' '.join(folds)} ({len(folds)})")
    p4 = p4d1_matches()
    emit(f"P4-D1 instances (s82 curve matches): {len(p4)}")
    specs = []
    for ti, T in enumerate(TRANSLITS):
        sk = voy(T)["pages"]
        specs.append((T, "VOY", 0, None))
        for i in range(N_FAM["LSHUF"]):
            specs.append((T, "LSHUF", i, gpu_line_shuffle(sk, SEED + 10000 + 1000 * ti + i)))
        for i in range(N_FAM["BSHUF"]):
            specs.append((T, "BSHUF", i, gpu_book_shuffle(sk, SEED + 20000 + 1000 * ti + i)))
        for i in range(N_FAM["S67"]):
            specs.append((T, "S67", i, None))
        for i in range(N_FAM["S57"]):
            specs.append((T, "S57", i, None))
        for i, pl in enumerate(p4):
            specs.append((T, "P4D1", i, pl))
    for lang in LANGS:
        specs.append(("ZL3b", "CTRL", LANGS.index(lang), lang))
    emit(f"jobs: {len(specs)}  (per transliteration: 1 Voynich + {sum(N_FAM.values()) + len(p4)} nulls; 6 planted W3 controls on ZL3b)")
    emit()
    flush()
    res = run_jobs(specs)

    # ---- values.csv
    with open(RUN_DIR / "values.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh, lineterminator="\n")
        wr.writerow(["text", "translit", "family", "fold", "held_tokens"] + LANGS + ["types", "device"])
        for r in res:
            for q in folds:
                wr.writerow([r["name"], r["T"], r["fam"], q, r["held_tok"][q]] + [f"{x:.4f}" for x in r["gains"][q]]
                            + [r["types"], str(dev)])

    # ---- matching check
    emit()
    emit("=== MATCHING (held-out tokens per fold equal Voynich's; core types, whole text) ===")
    vt = {T: next(r for r in res if r["T"] == T and r["fam"] == "VOY") for T in TRANSLITS}
    for T in TRANSLITS:
        bad = [r["name"] for r in res if r["T"] == T and r["held_tok"] != vt[T]["held_tok"]]
        fam_types = defaultdict(list)
        for r in res:
            if r["T"] == T:
                fam_types[r["fam"]].append(r["types"])
        emit(f"  {T}: fold token mismatches {len(bad)}{(' ' + ','.join(bad[:5])) if bad else ''}; core types "
             + "  ".join(f"{f} {np.mean(v):.0f}" for f, v in fam_types.items()))

    # ---- statistics per transliteration
    calls = dict(device=str(dev), folds=folds, per_T={}, controls={})
    voy_st = {}
    null_p95, null_m95, null_st_all = {}, {}, {}
    for T in TRANSLITS:
        nulls = [r for r in res if r["T"] == T and r["fam"] not in ("VOY", "CTRL")]
        st, p95, m95 = null_summary(nulls, folds)
        null_p95[T], null_m95[T], null_st_all[T] = p95, m95, (nulls, st)
        voy_st[T] = text_stats(vt[T]["gains"], folds, LANGS)

    emit()
    emit("=== PER-FOLD TABLE (gain = held-out stem-transition LL gain per 1,000 pairs, bits; max over 6 languages) ===")
    c1_T, c2_info = {}, {}
    for T in TRANSLITS:
        s = voy_st[T]
        nulls, st = null_st_all[T]
        fam_p95 = {f: gpu_quantile([x["gmax"].tolist() for r, x in zip(nulls, st) if r["fam"] == f])
                   for f in ["LSHUF", "BSHUF", "S67", "S57", "P4D1"]}
        emit(f"--- {T}: {len(nulls)} null texts; Voynich modal language {s['modal']} ({s['n_modal']}/15), "
             f"margin {s['margin']:+.2f} vs null margin p95 {null_m95[T]:+.2f}")
        emit(f"  {'fold':>4} {'tok':>6} {'best':>8} {'gain':>8} {'null_p95':>9} {'margin':>8} {'above':>6} | "
             + " ".join(f"{f + '_p95':>10}" for f in fam_p95) + " | " + " ".join(f"{l[:7]:>8}" for l in LANGS))
        n_above = 0
        for i, q in enumerate(folds):
            g = s["gmax"][i]
            above = g > null_p95[T][i]
            n_above += int(above)
            srt = sorted(s["G"][i], reverse=True)
            emit(f"  {q:>4} {vt[T]['held_tok'][q]:>6} {s['best'][i]:>8} {g:+8.2f} {null_p95[T][i]:+9.2f} {srt[0] - srt[1]:+8.2f} "
                 f"{'yes' if above else 'no':>6} | " + " ".join(f"{fam_p95[f][i]:+10.2f}" for f in fam_p95)
                 + " | " + " ".join(f"{x:+8.2f}" for x in s["G"][i]))
        p_text = gpu_exceed_p(float(np.mean(s["gmax"])), [float(np.mean(x["gmax"])) for x in st])
        null_modal10 = sum(x["n_modal"] >= MIN_FOLDS_LANG for x in st)
        emit(f"  folds above null p95: {n_above}/15;  mean max gain {np.mean(s['gmax']):+.2f} vs null text means "
             f"(p95 {float(gpu_quantile([[float(np.mean(x['gmax']))] for x in st])[0]):+.2f}), exceedance p = {p_text:.4f}")
        emit(f"  null texts with a modal language on >= 10/15 folds: {null_modal10}/{len(st)}; "
             f"Voynich margin exceedance p = {gpu_exceed_p(s['margin'], [x['margin'] for x in st]):.4f}")
        c1_T[T] = n_above
        c2_info[T] = dict(modal=s["modal"], n_modal=s["n_modal"], margin=s["margin"], m95=null_m95[T],
                          ok=(s["n_modal"] >= MIN_FOLDS_LANG and s["margin"] > null_m95[T]))
        calls["per_T"][T] = dict(folds_above=n_above, best=s["best"], gmax=s["gmax"].tolist(), p95=null_p95[T].tolist(),
                                 modal=s["modal"], n_modal=s["n_modal"], margin=s["margin"], null_margin_p95=null_m95[T],
                                 p_text=p_text, null_modal10=null_modal10)
        emit()

    # ---- controls
    emit("=== PLANTED W3 CONTROLS (ZL3b skeleton; vs ZL3b null pool) ===")
    n_ctrl_pass = 0
    for r in [r for r in res if r["fam"] == "CTRL"]:
        lang = LANGS[r["idx"]]
        s = text_stats(r["gains"], folds, LANGS)
        n_ab = int(sum(s["gmax"][i] > null_p95["ZL3b"][i] for i in range(len(folds))))
        own = sum(b == lang for b in s["best"])
        ok = n_ab >= MIN_FOLDS_C1 and s["modal"] == lang and s["n_modal"] >= MIN_FOLDS_LANG and s["margin"] > null_m95["ZL3b"]
        n_ctrl_pass += int(ok)
        emit(f"  {lang:8s} folds above null p95 {n_ab:2d}/15; own language best {own:2d}/15 (modal {s['modal']} {s['n_modal']}/15); "
             f"margin {s['margin']:+7.2f} vs p95 {null_m95['ZL3b']:+.2f}; median max gain {np.median(s['gmax']):+7.2f} -> {'PASS' if ok else 'fail'}")
        calls["controls"][lang] = dict(folds_above=n_ab, own=own, modal=s["modal"], margin=s["margin"], ok=ok)

    # ---- calls
    C1 = all(c1_T[T] >= MIN_FOLDS_C1 for T in TRANSLITS)
    lang_ok = Counter(c2_info[T]["modal"] for T in TRANSLITS if c2_info[T]["ok"])
    c2_lang = next((l for l, n in lang_ok.most_common() if n >= 2), None)
    C2 = c2_lang is not None
    C3 = n_ctrl_pass >= 5
    emit()
    emit("=== CALLS ===")
    emit(f"C1 above null (>= 10/15 folds on all three): " + ", ".join(f"{T} {c1_T[T]}/15" for T in TRANSLITS) + f" -> {C1}")
    emit("C2 language specificity: " + "; ".join(
        f"{T} modal {c2_info[T]['modal']} {c2_info[T]['n_modal']}/15, margin {c2_info[T]['margin']:+.2f} vs p95 {c2_info[T]['m95']:+.2f}"
        f" ({'ok' if c2_info[T]['ok'] else 'no'})" for T in TRANSLITS) + f" -> {C2}{' (' + c2_lang + ')' if C2 else ''}")
    emit(f"C3 planted controls pass C1+C2 rules: {n_ctrl_pass}/6 (need >= 5; all-6 {'yes' if n_ctrl_pass == 6 else 'no'}) -> {C3}")
    if not C3:
        verdict = "inconclusive: controls failed"
    elif C1 and C2:
        verdict = f"Voynich stems align with {c2_lang} above every null: candidate for word-level decoding"
    elif C1:
        verdict = "language-like stem structure, no specific language"
    else:
        verdict = "stem alignment not above null when order-free"
    emit(f"VERDICT: {verdict}")
    calls.update(C1=C1, C2=C2, C2_lang=c2_lang, C3=C3, n_ctrl_pass=n_ctrl_pass, verdict=verdict)

    if C1 and C2 and C3:
        emit()
        emit(f"=== TOP 30 ALIGNED VOYNICH CORE -> {c2_lang} STEM PAIRS (descriptive; count = folds x transliterations) ===")
        pc, fq = Counter(), Counter()
        for T in TRANSLITS:
            for q in folds:
                for c, stem, f in vt[T]["maps"][q][c2_lang]:
                    pc[(c, stem)] += 1
                    fq[(c, stem)] += f
        for (c, stem), n in pc.most_common(30):
            emit(f"  {c:>10} -> {stem:<10} {n:3d}  (training-core tokens summed {fq[(c, stem)]:.0f})")
    if DEVICE_NOTES:
        emit("device notes: " + "; ".join(sorted(set(DEVICE_NOTES))))
    emit(f"finished {clock()}; elapsed {time.time() - T0:.0f}s")
    (RUN_DIR / "calls.json").write_text(json.dumps(calls, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)),
                                        encoding="utf-8", newline="\n")
    flush()


if __name__ == "__main__":
    if LIST_LOCALS:
        print("\n".join(local_modules()))
    elif FIXTURE:
        run_fixture()
    else:
        main()
