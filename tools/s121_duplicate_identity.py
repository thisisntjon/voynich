#!/usr/bin/env python
"""s121 (D-066 (aa)), duplicate identity: when the same object is drawn twice on different Voynich pages, do the two
drawings carry the same label?  An exact-identity referent, chosen because graded label-to-object similarity is
unpowered at Voynich label length (s116, L-342).

QUESTION (frozen).  Rivals: labels name the object they sit on (content-bearing; H-06/H-14/H-16), so two drawings of
the same specific object/variety carry the same (or a one-edit variant) label more often than matched non-duplicate
pairs; vs labels carry no object identity (H-05/H-07, or a reference too indirect for this test).

STEP 1, BLIND (no label text, transliteration or token table is opened by these stages; units.tsv is read with the
  zl_text, n_glyph and n_tok columns dropped).
  --embed       s116 masked object crops (runs/s116/crops/<uid>.png, 378 units, sha256 checked against units.tsv) ->
                DINOv2 ViT-B/14 CLS + SigLIP B/16-224, 8 views (Embedder imported unchanged from
                tools/s115_a0_real_link_control.py; CUDA) -> runs/s121/voy_embed.npz.  Picture similarity S = mean of the
                two per-model cosine matrices z-scored over the off-diagonal upper triangle (A0 picture_matrices).
                Herbal/pharma plant parts: the only crop source (s53, runs/s53/embed.npz + sketches.json) holds unmasked
                pharma sketches and herbal windows with no label locus, so they cannot form a pair with two labels and
                are not used (a label-identity test needs a label on both members).
  --calibrate   A0 real-herbal corpus (820 captioned units, runs/s115_a0/20261018T203952_embed.npz, read-only), S as
                above.  Candidate pair = mutual top-1 over units on a different page (i's best partner off i's page is
                j and vice versa).  Same-name truth: both units have a non-empty name_key -> keys equal; otherwise A0
                names_match(name_tokens) (Levenshtein rule).  Threshold T = smallest score such that the mutual pairs
                with S >= T have precision >= 0.90 for same-name, with >= 20 such pairs.  Recall reported two ways:
                same-name pairs found / all cross-page same-name unit pairs, and units in a found same-name pair /
                units having any cross-page same-name partner.  Written to runs/s121/calibration.txt.  The z-scale
                transfer from A0 (unmasked bbox crops) to Voynich (masked crops) is an assumption, not measured.
  --candidates  Voynich: mutual top-1 across pages, S >= T -> runs/s121/candidates.tsv and side-by-side images
                runs/s121/pairs/<k>.png (A left, B right).
  --qwen        local qwen2.5vl:7b (Ollama, temperature 0, the two crops as two images) answers the question below ->
                runs/s121/votes_qwen.tsv.  The second model is Claude (the run agent) viewing each pair image, written
                by hand to runs/s121/votes_claude.tsv (columns k, vote, note) before any text is read.
                Question: "same object type and same specific drawn object/variety?"  YES or NO.
  --freeze      duplicates.tsv = candidates with YES from both models; sha256 printed and written to
                runs/s121/duplicates.sha256.  D = number of confirmed duplicate pairs.

STEP 2, POWER GATE (--power; A0 only, no Voynich text).  At D pairs: R_POW = 200 replicates; each replicate samples D
  pairs (without replacement) from the A0 detected pairs (mutual top-1, S >= T, unconfirmed, so ~10 % are wrong),
  gives every A0 unit a label = its caption cut to Voynich label length (s116 cut_to_label_length: k drawn from the s116
  token-count distribution) plus A0 NOISE edits, and runs the identity test below with the null pool = pairs on
  different pages, not detected pairs, matched (unordered) on manuscript and leaf side of the two members.  Shuffled
  control: the D pairs replaced by D random matched null pairs.  POWER = share p < 0.05 (exact identity).
  POWER_PASS = D >= 10 and POWER >= 0.80 and shuffled share <= 0.10.  If not, the run stops: UNPOWERED, no Voynich label
  text is read.  Written to runs/s121/power.txt.

STEP 3, FIXTURE (--fixture; synthetic labels on the real duplicate list and real unit strata, no real text).
  Labels drawn from a Zipf(1.1) vocabulary of 300 random strings (so chance identity happens).  Planted: the second
  member of each duplicate pair copies the first member's label with probability 0.6 (else independent), then NOISE.
  No identity: all labels independent.  R_FIX = 200 each.  FIXTURE_PASS = planted share p < 0.05 >= 0.80 and no-identity
  share p < 0.05 <= 0.10.  Written to runs/s121/fixture.txt.

IDENTITY TEST (all stages).  A unit's label = list of tokens (cores or words, empty strings dropped).  Exact identity
  of a pair = the labels share at least one token.  ED1 identity = some token pair has Levenshtein <= 1.  Statistic =
  number of duplicate pairs with identity.  Null: M draws; each draw takes, for every duplicate pair, one pair drawn
  uniformly from its matched null pool; null count = number with identity.  One-sided p = (1 + #{null >= obs}) /
  (M + 1).  M = 1999 (power, fixture), 9999 (real).
  Voynich null pool for duplicate pair (i, j): unit pairs (a, b) on different pages, not a candidate pair, with
  (quire, hand, section) equal to those of (i, j) under some member alignment and, under that same alignment,
  |n_glyph(a) - n_glyph(i)| <= 1 and |n_glyph(b) - n_glyph(j)| <= 1 (label length; n_glyph from units.tsv).  If that pool
  has < 20 pairs, quire is dropped; if still < 20, hand is dropped (the level used is reported per pair).

STEP 5, REAL (--real).  Refuses to start unless the stub s121_duplicate_identity.prereg.sha256 verifies (this script,
  runs/s121/duplicates.tsv, runs/s121/fixture.txt), power.txt says POWER_PASS=True and fixture.txt FIXTURE_PASS=True.
  Transliterations ZL3b (data/ZL3b-n.txt), RF1b (data/external/voynich-nu-ivtff/RF1b-er.txt), IT2a (.../IT2a-n.txt)
  via vparse.load(path=...); a unit's label = tokens (a-z only) of the same locus (page, line, unit code).
  Representations: SlotSegmenter cores (scoreboard/metrics_new.py, defaults, fitted on all P-unit tokens of that
  transliteration) and raw whole word.

DECISION RULE (frozen before any Voynich label text is read; printed CALL line)
  IDENTITY if exact-identity p < 0.05 in all six cells: {ZL3b, RF1b, IT2a} x {cores, raw words}.
  NULL otherwise.
  Reported beside the call, not part of it: ED1 p per cell, identity counts and null means, per-pair fallback level.

PROCESS.  python -I tools/s121_duplicate_identity.py --embed | --calibrate | --candidates | --qwen | --freeze | --power |
  --fixture | --real.  BelowNormal priority, <= 4 CPU threads, GPU for embedding.  Output files are never overwritten.
"""
from __future__ import annotations

import argparse
import base64
import csv
import datetime as dt
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scoreboard"))

STUB = ROOT / "s121_duplicate_identity.prereg.sha256"
RUNS = ROOT / "runs" / "s121"
S116_UNITS = ROOT / "runs" / "s116" / "units.tsv"
S116_CROPS = ROOT / "runs" / "s116" / "crops"
A0_SCRIPT = ROOT / "tools" / "s115_a0_real_link_control.py"
A0_EMBED = ROOT / "runs" / "s115_a0" / "20261018T203952_embed.npz"
TRANSLITS = [("ZL3b", ROOT / "data" / "ZL3b-n.txt"),
             ("RF1b", ROOT / "data" / "external" / "voynich-nu-ivtff" / "RF1b-er.txt"),
             ("IT2a", ROOT / "data" / "external" / "voynich-nu-ivtff" / "IT2a-n.txt")]
TEXT_COLS = ("zl_text", "n_glyph", "n_tok")

SEED = 121_20261018
PREC_MIN = 0.90
MIN_ABOVE = 20
D_MIN = 10
POWER_MIN = 0.80
SHUF_MAX = 0.10
ALPHA = 0.05
R_POW = 200
R_FIX = 200
M_POW = 1999
M_REAL = 9999
POOL_MIN = 20
QWEN = "qwen2.5vl:7b"
OLLAMA = "http://localhost:11434/api/generate"
QUESTION = ("These are two drawings, A (first image) and B (second image), cut from different pages of one illustrated "
            "manuscript. Question: do A and B show the same object type AND the same specific drawn object or "
            "variety (for example the same plant species, the same vessel, the same figure drawn twice), not merely "
            "two things of the same general kind? Answer with exactly one word, YES or NO.")


# ======================================================================================================== utilities
def load_a0():
    spec = importlib.util.spec_from_file_location("s115_a0", A0_SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def set_low_priority():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:  # noqa: BLE001
        pass


def clock() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def write_new(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


def units_meta(keep_length=False):
    """s116 unit table without label text (and without length columns unless keep_length)."""
    with open(S116_UNITS, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    drop = ("zl_text",) if keep_length else TEXT_COLS
    for r in rows:
        for c in drop:
            r.pop(c, None)
    return rows


def lev(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def mutual_top1(S: np.ndarray, page: np.ndarray):
    """[(i, j, s)] i<j with j = best off-page partner of i and i = best off-page partner of j."""
    X = S.copy()
    X[page[:, None] == page[None, :]] = -np.inf
    best = X.argmax(1)
    out = []
    for i, j in enumerate(best):
        if np.isfinite(X[i, j]) and best[j] == i and i < j:
            out.append((i, int(j), float(S[i, j])))
    return out


# ======================================================================================================== identity test
def ident_matrix(labels, ed1=False):
    n = len(labels)
    I = np.zeros((n, n), bool)
    if not ed1:
        vocab = {}
        rows, cols = [], []
        for i, d in enumerate(labels):
            for t in set(d):
                rows.append(i)
                cols.append(vocab.setdefault(t, len(vocab)))
        if vocab:
            Mx = np.zeros((n, len(vocab)), np.int32)
            Mx[rows, cols] = 1
            I = (Mx @ Mx.T) > 0
    else:
        sets = [sorted(set(d)) for d in labels]
        cache = {}
        for i in range(n):
            for j in range(i + 1, n):
                hit = False
                for a in sets[i]:
                    for b in sets[j]:
                        if abs(len(a) - len(b)) > 1:
                            continue
                        k = (a, b) if a < b else (b, a)
                        v = cache.get(k)
                        if v is None:
                            v = cache[k] = lev(a, b) <= 1
                        if v:
                            hit = True
                            break
                    if hit:
                        break
                I[i, j] = I[j, i] = hit
    np.fill_diagonal(I, False)
    return I


def identity_test(I, dups, pools, rng, M):
    """dups: list of (i, j); pools: list of (a_arr, b_arr) per dup.  Returns obs, null mean, p."""
    obs = int(sum(I[i, j] for i, j in dups))
    null = np.zeros(M, int)
    for (a, b) in pools:
        k = rng.integers(len(a), size=M)
        null += I[a[k], b[k]]
    p = (1 + int((null >= obs).sum())) / (M + 1)
    return obs, float(null.mean()), p


# ======================================================================================================== step 1
def do_embed():
    set_low_priority()
    out = RUNS / "voy_embed.npz"
    if out.exists():
        sys.exit(f"{out} exists; never overwritten")
    from PIL import Image
    a0 = load_a0()
    units = units_meta()
    imgs = []
    for u in units:
        p = S116_CROPS / f"{u['uid']}.png"
        if sha(p) != u["crop_sha"]:
            sys.exit(f"crop sha mismatch {p}")
        imgs.append(Image.open(p).convert("RGB").resize((224, 224), Image.BICUBIC))
    emb = a0.Embedder()
    print("device", emb.dev, flush=True)
    dino, sig = emb(imgs, "dino"), emb(imgs, "siglip")
    RUNS.mkdir(parents=True, exist_ok=True)
    with open(out, "xb") as f:
        np.savez(f, uid=np.array([u["uid"] for u in units]), dino=dino, siglip=sig)
    print("wrote", out, dino.shape, sig.shape, emb.dev)


def a0_same_name(a0, units):
    n = len(units)
    nt = [a0.name_tokens(u) for u in units]
    keys = [u.get("key", "") for u in units]

    def same(i, j):
        if keys[i] and keys[j]:
            return keys[i] == keys[j]
        return a0.names_match(nt[i], nt[j])
    return same


def a0_detect():
    a0 = load_a0()
    au = a0.load_units()
    d = np.load(A0_EMBED)
    S, _ = a0.picture_matrices([d["dino"], d["siglip"]])
    page = np.array([u["ms"] + "|" + u["page"] for u in au])
    return a0, au, S, page, mutual_top1(S, page)


def read_threshold():
    for ln in (RUNS / "calibration.txt").read_text(encoding="utf-8").splitlines():
        if ln.startswith("THRESHOLD="):
            return float(ln.split("=", 1)[1].split()[0])
    sys.exit("no THRESHOLD in calibration.txt")


def do_calibrate():
    set_low_priority()
    out = RUNS / "calibration.txt"
    if out.exists():
        sys.exit(f"{out} exists; never overwritten")
    a0, au, S, page, mt = a0_detect()
    same = a0_same_name(a0, au)
    mt.sort(key=lambda x: -x[2])
    lab = np.array([same(i, j) for i, j, _ in mt])
    sc = np.array([s for _, _, s in mt])
    cum = np.cumsum(lab) / np.arange(1, len(lab) + 1)
    T, kT = None, None
    for k in range(len(mt) - 1, MIN_ABOVE - 2, -1):  # largest k (lowest threshold) with precision >= PREC_MIN
        if cum[k] >= PREC_MIN:
            T, kT = sc[k], k + 1
            break
    n = len(au)
    allsame = [(i, j) for i in range(n) for j in range(i + 1, n) if page[i] != page[j] and same(i, j)]
    has_partner = {x for p in allsame for x in p}
    lines = [f"s121 A0 duplicate-threshold calibration; {clock()}; script sha256 {sha(Path(__file__))}",
             f"A0 units {n}; mutual top-1 cross-page pairs {len(mt)} (same-name {int(lab.sum())}, "
             f"precision at no threshold {lab.mean():.3f}); cross-page same-name unit pairs {len(allsame)}; "
             f"units with a same-name partner {len(has_partner)}"]
    for q in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0):
        m = sc >= q
        if m.any():
            lines.append(f"  S >= {q:.1f}: pairs {m.sum()}, precision {lab[m].mean():.3f}")
    if T is None:
        lines.append("THRESHOLD=NONE (no threshold reaches precision 0.90 with >= 20 pairs)")
    else:
        found = [(i, j) for (i, j, s), l in zip(mt, lab) if s >= T and l]
        fu = {x for p in found for x in p}
        prec = lab[:kT].mean()
        z = 1.96
        lo = (prec + z * z / (2 * kT) - z * np.sqrt(prec * (1 - prec) / kT + z * z / (4 * kT * kT))) / (1 + z * z / kT)
        by_ms = Counter(tuple(sorted((au[i]["ms"], au[j]["ms"]))) for i, j, _ in mt[:kT])
        lines += [f"THRESHOLD={T:.4f} (z-scored mean DINOv2+SigLIP cosine)",
                  f"PRECISION={prec:.3f} on {kT} pairs above threshold (Wilson 95% lower {lo:.3f})",
                  f"RECALL_PAIRS={len(found) / max(1, len(allsame)):.3f} ({len(found)}/{len(allsame)} cross-page "
                  f"same-name unit pairs)",
                  f"RECALL_UNITS={len(fu) / max(1, len(has_partner)):.3f} ({len(fu)}/{len(has_partner)} units with a "
                  f"partner)",
                  f"detected pairs by manuscript pair: {dict(by_ms)}"]
    lines.append(f"end {clock()}")
    print("\n".join(lines))
    write_new(out, "\n".join(lines) + "\n")


def voy_S():
    a0 = load_a0()
    d = np.load(RUNS / "voy_embed.npz")
    units = units_meta()
    assert list(d["uid"]) == [u["uid"] for u in units]
    S, _ = a0.picture_matrices([d["dino"], d["siglip"]])
    return units, S


def do_candidates():
    out = RUNS / "candidates.tsv"
    if out.exists():
        sys.exit(f"{out} exists; never overwritten")
    from PIL import Image, ImageDraw
    T = read_threshold()
    units, S = voy_S()
    page = np.array([u["page"] for u in units])
    mt = mutual_top1(S, page)
    cand = sorted([x for x in mt if x[2] >= T], key=lambda x: -x[2])
    (RUNS / "pairs").mkdir(parents=True, exist_ok=True)
    rows = ["k\tuid_a\tuid_b\tpage_a\tpage_b\tsection_a\tsection_b\tscore"]
    for k, (i, j, s) in enumerate(cand):
        A, B = units[i], units[j]
        rows.append(f"{k}\t{A['uid']}\t{B['uid']}\t{A['page']}\t{B['page']}\t{A['section']}\t{B['section']}\t{s:.4f}")
        can = Image.new("RGB", (470, 250), (255, 255, 255))
        can.paste(Image.open(S116_CROPS / f"{A['uid']}.png").convert("RGB"), (8, 22))
        can.paste(Image.open(S116_CROPS / f"{B['uid']}.png").convert("RGB"), (240, 22))
        dr = ImageDraw.Draw(can)
        dr.text((8, 4), f"A  (pair {k})", fill=(0, 0, 0))
        dr.text((240, 4), "B", fill=(0, 0, 0))
        can.save(RUNS / "pairs" / f"{k:03d}.png")
    write_new(out, "\n".join(rows) + "\n")
    print(f"threshold {T:.4f}; mutual top-1 cross-page pairs {len(mt)}; candidates >= T: {len(cand)}")
    print(f"score quantiles of all mutual pairs: {np.quantile([x[2] for x in mt], [0, .25, .5, .75, 1]).round(3)}")
    print("candidate sections:", Counter(tuple(sorted((units[i]['section'], units[j]['section']))) for i, j, _ in cand))


def read_tsv(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def do_qwen():
    out = RUNS / "votes_qwen.tsv"
    if out.exists():
        sys.exit(f"{out} exists; never overwritten")
    cand = read_tsv(RUNS / "candidates.tsv")
    rows = ["k\tvote\traw"]
    for c in cand:
        imgs = [base64.b64encode((S116_CROPS / f"{c[x]}.png").read_bytes()).decode() for x in ("uid_a", "uid_b")]
        body = json.dumps({"model": QWEN, "prompt": QUESTION, "images": imgs, "stream": False,
                           "options": {"temperature": 0, "seed": 121, "num_predict": 8}}).encode()
        req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
        raw = json.loads(urllib.request.urlopen(req, timeout=600).read())["response"].strip()
        up = raw.upper()
        vote = "YES" if up.startswith("YES") else ("NO" if up.startswith("NO") else "UNCLEAR")
        rows.append(f"{c['k']}\t{vote}\t{raw.replace(chr(9), ' ').replace(chr(10), ' ')}")
        print(c["k"], vote, raw, flush=True)
    write_new(out, "\n".join(rows) + "\n")


def do_freeze():
    out = RUNS / "duplicates.tsv"
    if out.exists():
        sys.exit(f"{out} exists; never overwritten")
    cand = read_tsv(RUNS / "candidates.tsv")
    q = {r["k"]: r["vote"] for r in read_tsv(RUNS / "votes_qwen.tsv")}
    c = {r["k"]: r["vote"].strip().upper() for r in read_tsv(RUNS / "votes_claude.tsv")}
    missing = [r["k"] for r in cand if r["k"] not in q or r["k"] not in c]
    if missing:
        sys.exit(f"votes missing for {missing}")
    keep = [r for r in cand if q[r["k"]] == "YES" and c[r["k"]] == "YES"]
    cols = list(cand[0].keys())
    write_new(out, "\t".join(cols) + "\n" + "".join("\t".join(r[x] for x in cols) + "\n" for r in keep))
    h = sha(out)
    write_new(RUNS / "duplicates.sha256", f"{h}  runs/s121/duplicates.tsv\n")
    print(f"candidates {len(cand)}; qwen YES {sum(v == 'YES' for v in q.values())}; claude YES "
          f"{sum(v == 'YES' for v in c.values())}; both YES (D) = {len(keep)}; sha256 {h}")


def read_dups(units):
    idx = {u["uid"]: i for i, u in enumerate(units)}
    return [(idx[r["uid_a"]], idx[r["uid_b"]]) for r in read_tsv(RUNS / "duplicates.tsv")]


# ======================================================================================================== step 2
def do_power():
    set_low_priority()
    out = RUNS / "power.txt"
    if out.exists():
        sys.exit(f"{out} exists; never overwritten")
    T = read_threshold()
    D = len(read_tsv(RUNS / "duplicates.tsv"))
    a0, au, S, page, mt = a0_detect()
    det = [(i, j) for i, j, s in mt if s >= T]
    detset = {(min(i, j), max(i, j)) for i, j in det}
    kdist = np.array([int(u["n_tok"]) for u in units_meta(keep_length=True)])
    st = [(u["ms"], u["side"]) for u in au]
    by_st = defaultdict(list)
    for i, s in enumerate(st):
        by_st[s].append(i)
    pool_cache = {}

    def pool(i, j):
        key = tuple(sorted((st[i], st[j])))
        if key not in pool_cache:
            A, B = by_st[key[0]], by_st[key[1]]
            aa, bb = [], []
            for a in A:
                for b in B:
                    if a != b and page[a] != page[b] and (min(a, b), max(a, b)) not in detset:
                        aa.append(a)
                        bb.append(b)
            pool_cache[key] = (np.array(aa), np.array(bb))
        return pool_cache[key]

    rng = np.random.default_rng(SEED)
    lines = [f"s121 power gate on the s115-A0 real-herbal corpus; {clock()}; script sha256 {sha(Path(__file__))}",
             f"threshold {T:.4f}; A0 detected pairs {len(det)}; Voynich confirmed duplicates D = {D}; label token-count "
             f"distribution {dict(sorted(Counter(kdist.tolist()).items()))}; NOISE {a0.NOISE}; R {R_POW}; M {M_POW}"]
    if D < D_MIN or D > len(det):
        lines += [f"POWER=NA (D={D} {'< ' + str(D_MIN) if D < D_MIN else '> A0 detected pairs'})", "POWER_PASS=False",
                  f"end {clock()}"]
        print("\n".join(lines))
        write_new(out, "\n".join(lines) + "\n")
        return
    res = {}
    for shuffle in (False, True):
        ps, obs_l, nm_l = [], [], []
        for _ in range(R_POW):
            labels = [a0.add_noise(cut_label(u["toks"], kdist, rng), rng) for u in au]
            I = ident_matrix(labels)
            pick = rng.choice(len(det), size=D, replace=False)
            dups = [det[k] for k in pick]
            pools = [pool(i, j) for i, j in dups]
            if shuffle:
                dd = []
                for (a, b) in pools:
                    k = rng.integers(len(a))
                    dd.append((int(a[k]), int(b[k])))
                dups = dd
            o, nm, p = identity_test(I, dups, pools, rng, M_POW)
            ps.append(p)
            obs_l.append(o)
            nm_l.append(nm)
        ps = np.array(ps)
        res[shuffle] = (ps < ALPHA).mean()
        s = (f"[{'shuffled' if shuffle else 'real'}] D={D} share p<{ALPHA} = {res[shuffle]:.3f}; identity count median "
             f"{np.median(obs_l):.1f} vs null mean median {np.median(nm_l):.2f}")
        print(s, flush=True)
        lines.append(s)
    ok = bool(D >= D_MIN and res[False] >= POWER_MIN and res[True] <= SHUF_MAX)
    lines += [f"POWER={res[False]:.3f}; SHUFFLED={res[True]:.3f}", f"POWER_PASS={ok}", f"end {clock()}"]
    print("\n".join(lines[-3:]))
    write_new(out, "\n".join(lines) + "\n")


def cut_label(toks, kdist, rng):
    k = int(rng.choice(kdist))
    k = max(1, min(k, len(toks)))
    keep = np.sort(rng.choice(len(toks), size=k, replace=False))
    return [toks[i] for i in keep]


# ======================================================================================================== Voynich pools
def voy_pools(units, dups, cand_pairs):
    n = len(units)
    page = [u["page"] for u in units]
    ng = np.array([float(u["n_glyph"]) for u in units])
    keys = [(u["quire"], u["hand"], u["section"]) for u in units]
    ex = {(min(a, b), max(a, b)) for a, b in cand_pairs}
    allp = [(a, b) for a in range(n) for b in range(a + 1, n) if page[a] != page[b] and (a, b) not in ex]
    pools, levels = [], []
    for i, j in dups:
        for lvl, sel in (("quire+hand+section", (0, 1, 2)), ("hand+section", (1, 2)), ("section", (2,))):
            ki = tuple(keys[i][s] for s in sel)
            kj = tuple(keys[j][s] for s in sel)
            aa, bb = [], []
            for a, b in allp:
                ka = tuple(keys[a][s] for s in sel)
                kb = tuple(keys[b][s] for s in sel)
                if (ka == ki and kb == kj and abs(ng[a] - ng[i]) <= 1 and abs(ng[b] - ng[j]) <= 1) or \
                   (kb == ki and ka == kj and abs(ng[b] - ng[i]) <= 1 and abs(ng[a] - ng[j]) <= 1):
                    aa.append(a)
                    bb.append(b)
            if len(aa) >= POOL_MIN or lvl == "section":
                break
        pools.append((np.array(aa), np.array(bb)))
        levels.append(f"{lvl}:{len(aa)}")
    return pools, levels


def cand_pairs_of(units):
    idx = {u["uid"]: i for i, u in enumerate(units)}
    return [(idx[r["uid_a"]], idx[r["uid_b"]]) for r in read_tsv(RUNS / "candidates.tsv")]


# ======================================================================================================== step 3
def do_fixture():
    set_low_priority()
    out = RUNS / "fixture.txt"
    if out.exists():
        sys.exit(f"{out} exists; never overwritten")
    a0 = load_a0()
    units = units_meta(keep_length=True)
    dups = read_dups(units)
    pools, levels = voy_pools(units, dups, cand_pairs_of(units))
    rng = np.random.default_rng(SEED + 3)
    letters = "acdehiklmnopqrsty"
    V = 300
    vocab = list({"".join(rng.choice(list(letters), size=int(rng.integers(2, 7)))) for _ in range(V * 2)})[:V]
    w = 1.0 / np.arange(1, V + 1) ** 1.1
    w /= w.sum()
    n = len(units)
    lines = [f"s121 fixture (synthetic labels, real duplicate list and strata); {clock()}; script sha256 "
             f"{sha(Path(__file__))}", f"units {n}; D {len(dups)}; R {R_FIX}; M {M_POW}; pool levels {levels}"]
    res = {}
    for planted in (True, False):
        ps = []
        for _ in range(R_FIX):
            lab = [[vocab[int(rng.choice(V, p=w))]] for _ in range(n)]
            if planted:
                for i, j in dups:
                    if rng.random() < 0.6:
                        lab[j] = list(lab[i])
            lab = [a0.add_noise(x, rng) for x in lab]
            _, _, p = identity_test(ident_matrix(lab), dups, pools, rng, M_POW)
            ps.append(p)
        res[planted] = (np.array(ps) < ALPHA).mean()
        s = f"[{'planted' if planted else 'no-identity'}] share p<{ALPHA} = {res[planted]:.3f}"
        print(s, flush=True)
        lines.append(s)
    ok = bool(res[True] >= 0.80 and res[False] <= 0.10)
    lines += [f"FIXTURE_PASS={ok}", f"end {clock()}"]
    write_new(out, "\n".join(lines) + "\n")
    print(lines[-2])


# ======================================================================================================== step 5
def verify_stub():
    if not STUB.exists():
        return False, ["stub missing"]
    ok, msgs = True, []
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        h, p = ln.split(None, 1)
        good = sha(ROOT / p.strip().lstrip("*")) == h
        ok &= good
        msgs.append(f"{p.strip()}: {'OK' if good else 'FAILED'}")
    return ok, msgs


def az_tokens(words):
    import re
    return [w for w in words if re.fullmatch(r"[a-z]+", w)]


def do_real():
    set_low_priority()
    ok, msgs = verify_stub()
    if not ok:
        sys.exit("stub does not verify: " + "; ".join(msgs))
    if "POWER_PASS=True" not in (RUNS / "power.txt").read_text(encoding="utf-8"):
        sys.exit("power gate not passed: UNPOWERED, no text read")
    if "FIXTURE_PASS=True" not in (RUNS / "fixture.txt").read_text(encoding="utf-8"):
        sys.exit("fixture not passed")
    import vparse
    from metrics_new import SlotSegmenter
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out = ROOT / f"results_s121_{stamp}.txt"
    units = units_meta(keep_length=True)
    dups = read_dups(units)
    pools, levels = voy_pools(units, dups, cand_pairs_of(units))
    lines = [f"s121 duplicate identity, real run {clock()}; script sha256 {sha(Path(__file__))}",
             "stub: " + "; ".join(msgs), f"units {len(units)}; D {len(dups)}; M {M_REAL}; pool levels {levels}"]
    pex = {}
    for name, path in TRANSLITS:
        recs = vparse.load(path=path)
        loc = {(r["page"], int(r["line"]), r["unit"]): az_tokens(r["words"]) for r in recs}
        seg = SlotSegmenter([t for r in recs if r["unit"].startswith("P") for t in az_tokens(r["words"])])
        words = [loc.get((u["page"], int(u["line"]), u["unit"]), []) for u in units]
        reps = {"cores": [[c for c in (seg.segment(t)[1] for t in d) if c] for d in words], "words": words}
        for rep, lab in reps.items():
            for metric, ed1 in (("exact", False), ("ed1", True)):
                rng = np.random.default_rng(SEED + 5)
                o, nm, p = identity_test(ident_matrix(lab, ed1), dups, pools, rng, M_REAL)
                if metric == "exact":
                    pex[(name, rep)] = p
                s = (f"[{name} {rep} {metric}] identity {o}/{len(dups)} vs null mean {nm:.2f}; p = {p:.4f}; "
                     f"empty labels {sum(not d for d in lab)}")
                print(s, flush=True)
                lines.append(s)
    call = "IDENTITY" if all(p < ALPHA for p in pex.values()) else "NULL"
    lines += [f"CALL={call} (exact-identity p per cell: " +
              ", ".join(f"{k[0]}/{k[1]} {v:.4f}" for k, v in pex.items()) + ")", f"end {clock()}"]
    write_new(out, "\n".join(lines) + "\n")
    print(lines[-2])
    print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    for s in ("embed", "calibrate", "candidates", "qwen", "freeze", "power", "fixture", "real"):
        ap.add_argument(f"--{s}", action="store_true")
    a = ap.parse_args()
    for s in ("embed", "calibrate", "candidates", "qwen", "freeze", "power", "fixture", "real"):
        if getattr(a, s):
            globals()[f"do_{s}"]()


if __name__ == "__main__":
    main()
