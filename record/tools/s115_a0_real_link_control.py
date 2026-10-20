#!/usr/bin/env python
"""s115-A0 (D-066 (t)): real-manuscript positive control for the project's text-to-picture link tests.

QUESTION (frozen).  Can the project's link statistics (s78 partial Mantel picture-vs-text; s48/s53 known-pair image
retrieval; db-s109 label-to-own-page retrieval) recover a KNOWN label-to-picture relation in real, captioned, illustrated
period herbals, at Voynich-like size and transcription noise?  Every past link null (F-20, F-33, F-44) was calibrated
only on planted links.  If these tests cannot see a real link at Voynich size, those nulls say nothing about meaning.

CORPUS (all read-only; every file is sha256-checked against data/anchor_A0/MANIFEST.sha256 before use)
  ljs419     Penn LJS 419 'Erbario' (N. Italy, 15th c.), images Public Domain Mark 1.0; captions = data/herbals_period/
             ljs419/captions_s103.json (agent transcriptions of the written names, unverified; s103).  One unit = one
             captioned plant: image = its bbox (fractions of the page), padded 5 % of the box size per side.
  sloane4016 BL Sloane MS 4016 (Lombardy c.1440), 'Public Domain in most countries other than the UK'; captions as above
             (sloane4016/captions_s103.json).  Units as for ljs419 (several plants per page).
  bod408     Bodleian MS. Canon. Misc. 408 (alchemical herbal, Italy, late 15th c.), CC BY-NC 4.0; images fetched by
             tools/s115_a0_fetch_408.py to data/anchor_A0/bodleian_canon_misc_408/images (IIIF, height 1024); caption =
             the Bodleian range label (data/herbals_alchemical/bodleian_canon_misc_408/canvases_structures.tsv): text after
             'fol. X: ', or the quoted name after "Plant: '", else cut at the first , . ; ( ; tokens 'and', 'or' dropped
             (cataloguer English); a canvas whose caption starts 'Text page' is dropped.  One unit = one canvas (whole image).
  Units with an empty caption are dropped.

TEXT.  Caption -> lowercase, brackets removed, j->i, v->u, y->i, tokens = runs of a-z.  Page text vector = token counts;
  tf-idf: idf = ln((1+N)/(1+df)) + 1 over the N units analysed, rows L2-normalised; text similarity = cosine (s78).
  Voynich-like noise (NOISE = 0.15, fixed a priori, not measured): each token independently, with probability NOISE, gets
  one random edit (substitution, deletion or insertion of a random a-z letter at a random position; deletion only if
  length >= 2).  Representation variant (descriptive): tokens cut to their first 4 letters (crude core analog).

PICTURES (same embedding as s48/s78).  Crop -> padded square with the median colour of the outer 5 % frame of the page
  image -> 224 px bicubic; DINOv2 ViT-B/14 CLS and SigLIP B/16-224 image features (data/external/models), 8 views
  (4 rotations x hflip), L2 per view, averaged, renormalised.  GPU if available.  Captions are NOT masked (no caption
  boxes exist); cross-manuscript caption ink is in different hands and cannot carry same-name similarity.

TEST (a), s78 analog: picture-similar units share caption vocabulary.
  Per model: cosine matrix z-scored over the off-diagonal upper triangle of the full corpus; picture similarity = mean of
  the two z matrices.  Over all unit pairs i<j: partial Mantel r = Pearson r of the residuals of picture and text
  similarity after OLS on [1, same ms, same ms & same leaf side (r/v), same page, same ms & adjacent page (|page index
  difference| == 1)]; constant columns dropped.  Null: NPERM = 999 permutations of unit labels within ms x side strata,
  applied to the text matrix (covariates stay with positions); one-sided p = (1 + #{r* >= r}) / (NPERM + 1).
  Voynich-like size: N_A = 119 units (s78 herbal N) drawn uniformly without replacement, R = 200 subsamples (seeded),
  text with NOISE.  Shuffled-label control: same subsamples, captions deranged within ms x side strata before the text
  matrix is built (fresh noise).

TEST (b), s48/s53 analog: label-defined same-subject partners retrieved by pictures.
  Known pairs: query unit q in ms A, partner set = units of ms B naming the same plant, A before B in the order
  (ljs419, bod408, sloane4016).  ljs419 <-> sloane4016: equal non-empty name_key.  bod408 <-> either: name tokens =
  caption tokens minus the stoplist STOP below, first two kept, each normalised (doubled letters collapsed, ch->c,
  ph->f, th->t, k->c, ae->e); match if the first tokens are equal or (both length >= 5 and Levenshtein <= 1), and, when
  both have a second token, the second tokens match by the same rule.  For ljs419/sloane4016 the name tokens are
  built from name_key when it is non-empty, else from the caption.
  Score (s53 PRIMARY mean_cls_centred): raw = (cos_dino + cos_siglip) / 2; hubness-centred C(q, h) = raw(q, h) - mean over
  all units of ms A of raw(., h) (label-free); per-query z does not change ranks.  Rank of a pair = 1 + #pool units with
  a strictly higher score than the best-scoring partner.  MRR, top-1, top-5, median percentile.  Null: NPERM joint
  permutations of the pool unit labels (one per draw per pool ms, applied to every pair); p = (1 + #{MRR* >= MRR}) /
  (NPERM + 1).  Voynich-like size: N_PAIRS = 13 pairs (s48/s53), drawn uniformly without replacement; per pool ms, pool =
  union of the drawn pairs' partners + uniform fill to POOL = 123 units (s48 herbal pool); R = 200 subsamples.  Shuffled
  control: each drawn pair's partner set replaced by a random same-size set from its pool excluding the true partners.
  (Text noise does not enter (b): the pairs are the known truth.)  Descriptive: full-corpus (b) on exact-name pairs only
  (no Levenshtein step; the edit-distance rule admits some wrong pairs, e.g. Lunaria ~ Linaria, seen in the pair list
  before freezing, no scores seen; kept, since wrong truth pairs only make the control harder).

TEST (c), db-s109 analog: labels retrieve their own page's body text.  NOT RUN: no transcribed body text exists for
  these witnesses (none reachable; recorded in the results).  CALL_C = NOT_RUN.

DECISION THRESHOLDS (frozen before the real run)
  ALPHA = 0.05, POWER_MIN = 0.80, SHUFFLE_MAX = 0.10.
  CALL_A = (share of the R Voynich-size noisy subsamples with p < ALPHA) >= POWER_MIN and (share of the R shuffled-label
           subsamples with p < ALPHA) <= SHUFFLE_MAX.
  CALL_B = the same rule for test (b) at 13 pairs / pool 123.
  REAL_LINK_RECOVERED = CALL_A and CALL_B (on the tests that could run; CALL_C NOT_RUN is printed).
  If a test's CALL is False because its power share < POWER_MIN, the matching past Voynich null (a -> F-33 / s78;
  b -> F-20 image side / s48, s53) is uninformative about meaning at Voynich size.  A shuffled share > SHUFFLE_MAX makes
  that test INVALID (null not null).
  Descriptive (no call): full-corpus p and effect sizes; clean-text and 4-letter variants at N_A; N = 240 power; s53's own
  P1 rule (MRR > null q99 and >= 5/13 top-5) share; same-name cross-ms pairs' mean picture z vs other cross-ms pairs.
FIXTURE GATE (synthetic, no real data; --fixture): 3 synthetic ms, 600 units, 150 subjects; planted fixture must give
  power >= POWER_MIN on (a) and (b); no-relation fixture <= SHUFFLE_MAX on both (R = 50).  The real run refuses to start
  unless runs/s115_a0/fixture.txt says FIXTURE_PASS=True.

PROCESS.  python -I tools/s115_a0_real_link_control.py --fixture | --real.  The real run verifies the prereg stub
  (s115_a0_real_link_control.prereg.sha256) and every MANIFEST line, sets BelowNormal priority, <= 4 CPU threads, writes
  results_s115_a0_<YYYYmmddTHHMMSS>.txt (never overwrites) and runs/s115_a0/<same stamp>_*.npz.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "s115_a0_real_link_control.prereg.sha256"
MANIFEST = ROOT / "data" / "anchor_A0" / "MANIFEST.sha256"
MODELS = ROOT / "data" / "external" / "models"
RUNS = ROOT / "runs" / "s115_a0"
LJS = ROOT / "data" / "herbals_period" / "ljs419"
SLO = ROOT / "data" / "herbals_period" / "sloane4016"
B408_TSV = ROOT / "data" / "herbals_alchemical" / "bodleian_canon_misc_408" / "canvases_structures.tsv"
B408_DIR = ROOT / "data" / "anchor_A0" / "bodleian_canon_misc_408"
MS_ORDER = ["ljs419", "bod408", "sloane4016"]

SEED = 20261018
ALPHA, POWER_MIN, SHUFFLE_MAX = 0.05, 0.80, 0.10
NPERM, R = 999, 200
N_A, N_A2 = 119, 240
N_PAIRS, POOL = 13, 123
NOISE = 0.15
STOP = {"herba", "erba", "herbe", "de", "et", "sive", "siue", "seu", "aut", "alio", "nomine", "uel", "ouer", "o", "alii",
        "uocant", "multi", "di", "la", "minor", "maior", "maiior", "mazor", "greca", "greci", "magna", "romana", "and", "or",
        "sine", "fine", "aliter", "alia", "id", "est"}
LETTERS = "abcdefghijklmnopqrstuvwxyz"


# ----------------------------------------------------------------------------------------------------------- text
def tokens(s: str) -> list[str]:
    s = s.lower().replace("[", "").replace("]", "")
    s = s.replace("j", "i").replace("v", "u").replace("y", "i")
    return re.findall(r"[a-z]+", s)


def norm2(w: str) -> str:
    w = w.replace("ch", "c").replace("ph", "f").replace("th", "t").replace("k", "c").replace("ae", "e")
    return re.sub(r"(.)\1+", r"\1", w)


def lev(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def tok_match(a: str, b: str, exact: bool = False) -> bool:
    return a == b or (not exact and len(a) >= 5 and len(b) >= 5 and lev(a, b) <= 1)


def name_tokens(u: dict) -> list[str]:
    src = u["key"] if u.get("key") else u["caption"]
    return [norm2(t) for t in tokens(src) if t not in STOP][:2]


def names_match(a: list[str], b: list[str], exact: bool = False) -> bool:
    if not a or not b or not tok_match(a[0], b[0], exact):
        return False
    if len(a) >= 2 and len(b) >= 2:
        return tok_match(a[1], b[1], exact)
    return True


def add_noise(toks: list[str], rng) -> list[str]:
    out = []
    for t in toks:
        if rng.random() < NOISE:
            k = rng.integers(3) if len(t) >= 2 else rng.integers(2) * 2  # 0 sub, 1 del, 2 ins
            pos = int(rng.integers(len(t) + (1 if k == 2 else 0)))
            c = LETTERS[int(rng.integers(26))]
            if k == 0:
                t = t[:pos] + c + t[pos + 1:] if pos < len(t) else t[:-1] + c
            elif k == 1:
                pos = min(pos, len(t) - 1)
                t = t[:pos] + t[pos + 1:]
            else:
                t = t[:pos] + c + t[pos:]
        out.append(t)
    return out


def tfidf_sim(docs: list[list[str]]) -> np.ndarray:
    vocab = {}
    for d in docs:
        for t in d:
            vocab.setdefault(t, len(vocab))
    n = len(docs)
    M = np.zeros((n, max(1, len(vocab))))
    for i, d in enumerate(docs):
        for t in d:
            M[i, vocab[t]] += 1
    df = (M > 0).sum(0)
    M = M * (np.log((1 + n) / (1 + df)) + 1)
    nr = np.linalg.norm(M, axis=1, keepdims=True)
    M = M / np.maximum(nr, 1e-12)
    return M @ M.T


# ----------------------------------------------------------------------------------------------------------- test (a)
def covariates(units: list[dict]) -> list[np.ndarray]:
    ms = np.array([u["ms"] for u in units])
    side = np.array([u["side"] for u in units])
    page = np.array([u["ms"] + "|" + u["page"] for u in units])
    pidx = np.array([u["page_idx"] for u in units])
    same_ms = ms[:, None] == ms[None, :]
    same_side = same_ms & (side[:, None] == side[None, :])
    same_page = page[:, None] == page[None, :]
    adj = same_ms & (np.abs(pidx[:, None] - pidx[None, :]) == 1)
    return [same_ms.astype(float), same_side.astype(float), same_page.astype(float), adj.astype(float)]


def strata_of(units: list[dict]) -> np.ndarray:
    keys = {}
    return np.array([keys.setdefault((u["ms"], u["side"]), len(keys)) for u in units])


def strat_perm(strata: np.ndarray, rng) -> np.ndarray:
    p = np.arange(len(strata))
    for s in np.unique(strata):
        idx = np.where(strata == s)[0]
        p[idx] = rng.permutation(idx)
    return p


def strat_derange(strata: np.ndarray, rng) -> np.ndarray:
    p = np.arange(len(strata))
    for s in np.unique(strata):
        idx = np.where(strata == s)[0]
        if len(idx) < 2:
            continue
        shift = rng.permutation(idx)
        p[shift] = np.roll(shift, 1)
    return p


def partial_mantel(P: np.ndarray, T: np.ndarray, covs: list[np.ndarray], strata: np.ndarray, rng, nperm=NPERM):
    n = P.shape[0]
    iu0, iu1 = np.triu_indices(n, 1)
    cols = [np.ones(len(iu0))]
    for c in covs:
        v = c[iu0, iu1]
        if v.std() > 0:
            cols.append(v)
    Q, _ = np.linalg.qr(np.column_stack(cols))
    ep = P[iu0, iu1] - Q @ (Q.T @ P[iu0, iu1])
    nep = np.linalg.norm(ep)

    def rvec(tm):  # tm (B, m)
        E = tm - (tm @ Q) @ Q.T
        ne = np.linalg.norm(E, axis=1)
        return np.where(ne > 1e-12, (E @ ep) / np.maximum(nep * ne, 1e-12), 0.0)

    Tf = T.ravel()
    r_obs = float(rvec(T[iu0, iu1][None, :])[0])
    rs = []
    B = max(1, int(3e6 // max(1, len(iu0))))
    done = 0
    while done < nperm:
        b = min(B, nperm - done)
        perms = np.stack([strat_perm(strata, rng) for _ in range(b)])
        idx = perms[:, iu0] * n + perms[:, iu1]
        rs.append(rvec(Tf[idx]))
        done += b
    rs = np.concatenate(rs)
    p = (1 + int((rs >= r_obs).sum())) / (nperm + 1)
    return r_obs, p, float(rs.mean()), float(np.quantile(rs, 0.99))


def run_a(units, Pz, rng, n_sub, reps, noise=True, shuffle=False, stem=False, nperm=NPERM):
    rs, ps = [], []
    for _ in range(reps):
        sub = np.sort(rng.choice(len(units), size=min(n_sub, len(units)), replace=False))
        us = [units[i] for i in sub]
        st = strata_of(us)
        docs = [list(u["toks"]) for u in us]
        if shuffle:
            perm = strat_derange(st, rng)
            docs = [docs[j] for j in perm]
        if noise:
            docs = [add_noise(d, rng) for d in docs]
        if stem:
            docs = [[t[:4] for t in d] for d in docs]
        T = tfidf_sim(docs)
        r, p, _, _ = partial_mantel(Pz[np.ix_(sub, sub)], T, covariates(us), st, rng, nperm)
        rs.append(r)
        ps.append(p)
    return np.array(rs), np.array(ps)


# ----------------------------------------------------------------------------------------------------------- test (b)
def make_pairs(units: list[dict], exact: bool = False):
    """[(q, msB, partner index array)] with ms(q) before msB in MS_ORDER."""
    by_ms = {m: [i for i, u in enumerate(units) if u["ms"] == m] for m in MS_ORDER}
    nt = [name_tokens(u) for u in units]
    pairs = []
    for ai, A in enumerate(MS_ORDER):
        for B in MS_ORDER[ai + 1:]:
            for q in by_ms[A]:
                if {A, B} == {"ljs419", "sloane4016"}:
                    k = units[q].get("key", "")
                    part = [h for h in by_ms[B] if k and units[h].get("key", "") == k]
                else:
                    part = [h for h in by_ms[B] if names_match(nt[q], nt[h], exact)]
                if part:
                    pairs.append((q, B, np.array(part)))
    return pairs


def centred_scores(units, raw: np.ndarray):
    """C[q, h] = raw[q, h] - mean over units u of ms(q) of raw[u, h] (label-free hubness centring)."""
    ms = np.array([u["ms"] for u in units])
    C = np.empty_like(raw)
    for A in np.unique(ms):
        rows = ms == A
        C[rows] = raw[rows] - raw[rows].mean(0, keepdims=True)
    return C


def mrr_test(C, pairs, pools, rng, nperm=NPERM):
    """pairs: [(q, msB, partners)], pools: {msB: array of unit ids}.  Returns stats + null."""
    pos = {B: {int(h): k for k, h in enumerate(pool)} for B, pool in pools.items()}
    rstrict, tpos = [], []
    for q, B, part in pairs:
        s = C[q, pools[B]]
        rstrict.append(1 + (s[None, :] > s[:, None]).sum(1))
        tpos.append(np.array([pos[B][int(h)] for h in part]))
    ranks = np.array([r[t].min() for r, t in zip(rstrict, tpos)])
    M = {B: len(pool) for B, pool in pools.items()}
    obs = float((1.0 / ranks).mean())
    null = np.empty(nperm)
    for d in range(nperm):
        pi = {B: rng.permutation(M[B]) for B in M}
        null[d] = np.mean([1.0 / r[pi[B][t]].min() for r, t, (_, B, _) in zip(rstrict, tpos, pairs)])
    p = (1 + int((null >= obs).sum())) / (nperm + 1)
    pct = np.array([(rk - 1) / max(1, M[B] - 1) for rk, (_, B, _) in zip(ranks, pairs)])
    return dict(mrr=obs, p=p, null_mean=float(null.mean()), q99=float(np.quantile(null, 0.99)),
                top1=int((ranks == 1).sum()), top5=int((ranks <= 5).sum()), n=len(pairs),
                med_pct=float(np.median(pct)))


def run_b(units, C, pairs, rng, reps, shuffle=False, nperm=NPERM):
    by_ms = {m: np.array([i for i, u in enumerate(units) if u["ms"] == m]) for m in MS_ORDER}
    out = []
    for _ in range(reps):
        sel = rng.choice(len(pairs), size=min(N_PAIRS, len(pairs)), replace=False)
        sp = [pairs[i] for i in sel]
        pools = {}
        for B in {b for _, b, _ in sp}:
            need = np.unique(np.concatenate([p for _, b, p in sp if b == B]))
            rest = np.setdiff1d(by_ms[B], need)
            fill = rng.choice(rest, size=max(0, min(len(rest), POOL - len(need))), replace=False)
            pools[B] = np.concatenate([need, fill])
        if shuffle:
            sp2 = []
            for q, B, part in sp:
                cand = np.setdiff1d(pools[B], part)
                sp2.append((q, B, rng.choice(cand, size=min(len(part), len(cand)), replace=False)))
            sp = sp2
        out.append(mrr_test(C, sp, pools, rng, nperm))
    return out


# ----------------------------------------------------------------------------------------------------------- images
class Embedder:
    def __init__(self):
        import torch
        from transformers import AutoModel, SiglipModel
        torch.set_num_threads(4)
        self.t = torch
        self.dev = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.dino = AutoModel.from_pretrained(str(MODELS / "dinov2-base"), use_safetensors=True).to(self.dev).eval()
        self.sig = SiglipModel.from_pretrained(str(MODELS / "siglip-base-patch16-224"),
                                               use_safetensors=True).to(self.dev).eval()
        self.norms = {"dino": ((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)), "siglip": ((0.5,) * 3, (0.5,) * 3)}

    def __call__(self, imgs, model, bs=16):
        from PIL import Image
        t = self.t
        m, s = self.norms[model]
        mt = t.tensor(m, device=self.dev).view(1, 3, 1, 1)
        st = t.tensor(s, device=self.dev).view(1, 3, 1, 1)
        out = []
        with t.no_grad():
            for i in range(0, len(imgs), bs):
                chunk = imgs[i:i + bs]
                arr = []
                for im in chunk:
                    for rot in (0, 90, 180, 270):
                        r = im.rotate(rot) if rot else im
                        arr.append(np.asarray(r, np.float32) / 255.0)
                        arr.append(np.asarray(r.transpose(Image.FLIP_LEFT_RIGHT), np.float32) / 255.0)
                x = t.from_numpy(np.stack(arr)).permute(0, 3, 1, 2).to(self.dev)
                x = (x - mt) / st
                f = self.dino(pixel_values=x).last_hidden_state[:, 0] if model == "dino" else \
                    self.sig.get_image_features(pixel_values=x)
                f = t.nn.functional.normalize(f.float(), dim=-1).view(len(chunk), 8, -1).mean(1)
                out.append(t.nn.functional.normalize(f, dim=-1).cpu().numpy())
        return np.concatenate(out)


def unit_image(u: dict):
    from PIL import Image
    im = Image.open(u["img"]).convert("RGB")
    a = np.asarray(im)
    h, w = a.shape[:2]
    fh, fw = max(1, h // 20), max(1, w // 20)
    frame = np.concatenate([a[:fh].reshape(-1, 3), a[-fh:].reshape(-1, 3), a[:, :fw].reshape(-1, 3),
                            a[:, -fw:].reshape(-1, 3)])
    bg = tuple(int(v) for v in np.median(frame, 0))
    if u.get("bbox"):
        x0, y0, x1, y1 = u["bbox"]
        px, py = 0.05 * (x1 - x0), 0.05 * (y1 - y0)
        box = (int(max(0, x0 - px) * w), int(max(0, y0 - py) * h), int(min(1, x1 + px) * w), int(min(1, y1 + py) * h))
        if box[2] - box[0] >= 8 and box[3] - box[1] >= 8:
            im = im.crop(box)
    cw, ch = im.size
    s = max(cw, ch)
    can = Image.new("RGB", (s, s), bg)
    can.paste(im, ((s - cw) // 2, (s - ch) // 2))
    return can.resize((224, 224), Image.BICUBIC)


# ----------------------------------------------------------------------------------------------------------- data
def side_of(folio: str) -> str:
    f = folio.lower()
    if f.endswith("verso") or f.endswith("v"):
        return "v"
    if f.endswith("recto") or f.endswith("r"):
        return "r"
    return "x"


def load_units() -> list[dict]:
    units = []
    for ms, d, sub in (("ljs419", LJS, "iiif"), ("sloane4016", SLO, "")):
        caps = json.load(open(d / "captions_s103.json", encoding="utf-8"))
        for pi, rec in enumerate(caps):
            folio = rec["file"].split("_", 1)[1].rsplit(".", 1)[0]
            for p in rec["plants"]:
                cap = (p.get("caption") or "").strip()
                if not tokens(cap):
                    continue
                units.append(dict(ms=ms, page=rec["file"], page_idx=pi, side=side_of(folio), caption=cap,
                                  key=(p.get("name_key") or "").strip().lower(), bbox=p.get("bbox"),
                                  img=str((d / sub / rec["file"]) if sub else (d / rec["file"]))))
    rows = list(csv.DictReader(open(B408_TSV, encoding="utf-8"), delimiter="\t"))
    fm = {r["idx"]: r for r in csv.DictReader(open(B408_DIR / "fetch_manifest.tsv", encoding="utf-8"), delimiter="\t")}
    for r in rows:
        s = re.sub(r"^fol\.[^:]*:\s*", "", r["structure_labels"].strip())
        if s.lower().startswith("text page"):
            continue
        m = re.search(r"Plant:\s*'([^']+)'", s)
        cap = m.group(1) if m else re.split(r"[,.;(]", s)[0].strip()
        if not [t for t in tokens(cap) if t not in ("and", "or")] or r["idx"] not in fm:
            continue
        units.append(dict(ms="bod408", page=r["canvas_label"] + "#" + r["idx"], page_idx=int(r["idx"]),
                          side=side_of(r["canvas_label"]), caption=cap, key="", bbox=None,
                          img=str(B408_DIR / "images" / fm[r["idx"]]["file"])))
    for u in units:
        t = tokens(u["caption"])
        if u["ms"] == "bod408":
            t = [x for x in t if x not in ("and", "or")]
        u["toks"] = t
    return units


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def verify_lines(path: Path) -> tuple[bool, list[str]]:
    ok, msgs = True, []
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        hx, fn = line.rstrip("\r\n").split(None, 1)
        fn = fn.lstrip("*")
        good = (ROOT / fn).exists() and sha(ROOT / fn) == hx
        ok &= good
        if not good:
            msgs.append(f"MISMATCH {fn}")
    return ok, msgs


# ----------------------------------------------------------------------------------------------------------- fixture
def fixture_units(rng, related: bool):
    ms_names = MS_ORDER
    n_subj, n = 150, 600
    subj = rng.integers(n_subj, size=n)
    msi = rng.integers(3, size=n)
    names = ["".join(LETTERS[int(c)] for c in rng.integers(26, size=7)) for _ in range(n_subj)]
    formula = [["herba"], ["alio", "nomine"], ["erba", "di"]]
    units = []
    for i in range(n):
        s = subj[i] if related else int(rng.integers(n_subj))
        units.append(dict(ms=ms_names[msi[i]], page=f"p{i}", page_idx=i, side="r" if i % 2 else "v",
                          caption="", key=names[s], toks=formula[msi[i]] + [names[s]]))
    d = 64
    S = rng.normal(size=(n_subj, d))
    Mv = rng.normal(size=(3, d))
    E = []
    for _ in range(2):
        e = 0.9 * S[subj] + 0.8 * Mv[msi] + rng.normal(size=(n, d))
        E.append(e / np.linalg.norm(e, axis=1, keepdims=True))
    return units, E


def picture_matrices(E):
    zs = []
    n = E[0].shape[0]
    iu = np.triu_indices(n, 1)
    for e in E:
        c = e @ e.T
        v = c[iu]
        zs.append((c - v.mean()) / v.std())
    raw = (E[0] @ E[0].T + E[1] @ E[1].T) / 2
    return (zs[0] + zs[1]) / 2, raw


def do_fixture():
    RUNS.mkdir(parents=True, exist_ok=True)
    lines = []
    res = {}
    for related in (True, False):
        rng = np.random.default_rng(SEED + int(related))
        units, E = fixture_units(rng, related)
        Pz, raw = picture_matrices(E)
        C = centred_scores(units, raw)
        pairs = make_pairs(units)
        _, pa = run_a(units, Pz, rng, N_A, 50)
        bo = run_b(units, C, pairs, rng, 50)
        pb = np.array([o["p"] for o in bo])
        res[related] = ((pa < ALPHA).mean(), (pb < ALPHA).mean())
        lines.append(f"fixture related={related}: pairs={len(pairs)} (a) share p<{ALPHA} = {res[related][0]:.2f}; "
                     f"(b) share = {res[related][1]:.2f}; (b) median MRR {np.median([o['mrr'] for o in bo]):.3f}")
    ok = res[True][0] >= POWER_MIN and res[True][1] >= POWER_MIN and res[False][0] <= SHUFFLE_MAX and \
        res[False][1] <= SHUFFLE_MAX
    lines.append(f"FIXTURE_PASS={ok}")
    (RUNS / "fixture.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


# ----------------------------------------------------------------------------------------------------------- real
def set_low_priority():
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
        except Exception:  # noqa: BLE001
            pass


def do_real():
    set_low_priority()
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_path = ROOT / f"results_s115_a0_{stamp}.txt"
    fx = RUNS / "fixture.txt"
    if not fx.exists() or "FIXTURE_PASS=True" not in fx.read_text(encoding="utf-8"):
        sys.exit("fixture not passed; refusing to run")
    ok_stub, m1 = verify_lines(STUB)
    ok_man, m2 = verify_lines(MANIFEST)
    if not (ok_stub and ok_man):
        sys.exit("verification failed: " + "; ".join(m1 + m2))
    f = open(out_path, "x", encoding="utf-8", newline="\n")

    def w(s=""):
        print(s, flush=True)
        f.write(s + "\n")

    w(f"s115-A0 real-manuscript link control; script sha256={sha(Path(__file__))}")
    w(f"run start {dt.datetime.now().isoformat(timespec='seconds')} (datetime.now); stub_match={ok_stub} "
      f"manifest_match={ok_man}")
    w((RUNS / 'fixture.txt').read_text(encoding='utf-8').strip())
    units = load_units()
    cnt = {m: sum(u["ms"] == m for u in units) for m in MS_ORDER}
    w(f"units: {len(units)} {cnt}")
    t0 = time.time()
    emb = Embedder()
    imgs = [unit_image(u) for u in units]
    E = [emb(imgs, "dino"), emb(imgs, "siglip")]
    w(f"embedded on {emb.dev} in {time.time() - t0:.0f}s")
    del emb
    RUNS.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(RUNS / f"{stamp}_embed.npz", dino=E[0], siglip=E[1])
    Pz, raw = picture_matrices(E)
    C = centred_scores(units, raw)
    pairs = make_pairs(units)
    by = {}
    for _, B, _ in pairs:
        by[B] = by.get(B, 0) + 1
    w(f"known pairs (b): {len(pairs)}; by pool ms {by}")
    rng = np.random.default_rng(SEED)

    # ---- descriptive: same-name cross-ms picture similarity
    ms = np.array([u["ms"] for u in units])
    same = np.zeros_like(Pz, bool)
    for q, B, part in pairs:
        same[q, part] = same[part, q] = True
    cross = (ms[:, None] != ms[None, :])
    iu = np.triu_indices(len(units), 1)
    a_s, a_o = Pz[iu][same[iu]], Pz[iu][(cross & ~same)[iu]]
    d = (a_s.mean() - a_o.mean()) / np.sqrt((a_s.var() + a_o.var()) / 2)
    w(f"same-name cross-ms pairs: n={len(a_s)} mean picture z {a_s.mean():+.3f} vs other cross-ms {a_o.mean():+.3f} "
      f"(Cohen d {d:+.3f})")

    # ---- test (a)
    w("\n=== TEST (a) s78 analog: partial Mantel picture similarity vs caption tf-idf similarity ===")
    st = strata_of(units)
    for lab, noise, stem in (("clean", False, False), ("noisy", True, False)):
        docs = [list(u["toks"]) for u in units]
        if noise:
            docs = [add_noise(x, rng) for x in docs]
        r, p, nm, q99 = partial_mantel(Pz, tfidf_sim(docs), covariates(units), st, rng, NPERM)
        w(f"[a full {lab}] N={len(units)} r={r:+.4f} p={p:.4f} null mean {nm:+.4f} q99 {q99:+.4f}")
    res = {}
    for lab, kw in (("voynich_noisy", dict(noise=True)), ("voynich_shuffled", dict(noise=True, shuffle=True)),
                    ("voynich_clean", dict(noise=False)), ("voynich_stem4", dict(noise=True, stem=True))):
        rs, ps = run_a(units, Pz, rng, N_A, R, **kw)
        res[lab] = (rs, ps)
        w(f"[a N={N_A} {lab}] R={R} share p<{ALPHA} = {(ps < ALPHA).mean():.3f}; r median {np.median(rs):+.4f} "
          f"IQR [{np.quantile(rs, .25):+.4f}, {np.quantile(rs, .75):+.4f}]; p median {np.median(ps):.4f}")
    rs2, ps2 = run_a(units, Pz, rng, N_A2, 50, noise=True)
    w(f"[a N={N_A2} noisy, descriptive] R=50 share p<{ALPHA} = {(ps2 < ALPHA).mean():.3f}; r median {np.median(rs2):+.4f}")
    pow_a = (res["voynich_noisy"][1] < ALPHA).mean()
    sh_a = (res["voynich_shuffled"][1] < ALPHA).mean()
    call_a = bool(pow_a >= POWER_MIN and sh_a <= SHUFFLE_MAX)

    # ---- test (b)
    w("\n=== TEST (b) s48/s53 analog: label-defined partners retrieved by pictures (mean_cls_centred) ===")
    pools_full = {B: np.array([i for i, u in enumerate(units) if u["ms"] == B]) for B in {b for _, b, _ in pairs}}
    o = mrr_test(C, pairs, pools_full, rng, NPERM)
    w(f"[b full] pairs={o['n']} pools={ {b: len(v) for b, v in pools_full.items()} } MRR={o['mrr']:.4f} null mean "
      f"{o['null_mean']:.4f} q99 {o['q99']:.4f} p={o['p']:.4f} top1={o['top1']} top5={o['top5']} median pct "
      f"{o['med_pct']:.3f}")
    pex = make_pairs(units, exact=True)
    o = mrr_test(C, pex, pools_full, rng, NPERM)
    w(f"[b full, exact-name pairs only, descriptive] pairs={o['n']} MRR={o['mrr']:.4f} null mean {o['null_mean']:.4f} "
      f"p={o['p']:.4f} top1={o['top1']} top5={o['top5']}")
    ob = run_b(units, C, pairs, rng, R)
    osh = run_b(units, C, pairs, rng, R, shuffle=True)
    pb = np.array([x["p"] for x in ob])
    psh = np.array([x["p"] for x in osh])
    p1 = np.mean([x["mrr"] > x["q99"] and x["top5"] >= 5 for x in ob])
    w(f"[b {N_PAIRS} pairs / pool {POOL}] R={R} share p<{ALPHA} = {(pb < ALPHA).mean():.3f}; MRR median "
      f"{np.median([x['mrr'] for x in ob]):.4f} IQR [{np.quantile([x['mrr'] for x in ob], .25):.4f}, "
      f"{np.quantile([x['mrr'] for x in ob], .75):.4f}]; null mean median {np.median([x['null_mean'] for x in ob]):.4f}; "
      f"top5 median {np.median([x['top5'] for x in ob]):.1f}/13; s53-P1 rule share {p1:.3f}")
    w(f"[b shuffled] R={R} share p<{ALPHA} = {(psh < ALPHA).mean():.3f}; MRR median "
      f"{np.median([x['mrr'] for x in osh]):.4f}")
    pow_b = (pb < ALPHA).mean()
    sh_b = (psh < ALPHA).mean()
    call_b = bool(pow_b >= POWER_MIN and sh_b <= SHUFFLE_MAX)

    # ---- calls
    w("\n=== CALLS (thresholds frozen in the docstring) ===")
    w(f"CALL_A={call_a} (power {pow_a:.3f} >= {POWER_MIN}? shuffled {sh_a:.3f} <= {SHUFFLE_MAX}?)"
      + ("" if sh_a <= SHUFFLE_MAX else " INVALID: shuffled control not null"))
    w(f"CALL_B={call_b} (power {pow_b:.3f} >= {POWER_MIN}? shuffled {sh_b:.3f} <= {SHUFFLE_MAX}?)"
      + ("" if sh_b <= SHUFFLE_MAX else " INVALID: shuffled control not null"))
    w("CALL_C=NOT_RUN (no transcribed body text for these witnesses)")
    overall = call_a and call_b
    w(f"REAL_LINK_RECOVERED={overall}")
    w(f"OVERALL_CALL={'REAL_LINK_RECOVERED' if overall else 'REAL_LINK_NOT_RECOVERED'} (tests a, b; c not run)")
    w(f"run end {dt.datetime.now().isoformat(timespec='seconds')}")
    f.close()
    np.savez_compressed(RUNS / f"{stamp}_stats.npz", a_noisy_r=res["voynich_noisy"][0], a_noisy_p=res["voynich_noisy"][1],
                        a_shuf_p=res["voynich_shuffled"][1], b_p=pb, b_shuf_p=psh,
                        b_mrr=np.array([x["mrr"] for x in ob]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fixture", action="store_true")
    g.add_argument("--real", action="store_true")
    a = ap.parse_args()
    do_fixture() if a.fixture else do_real()
