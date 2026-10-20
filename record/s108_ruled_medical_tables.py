"""S108 (D-066 (m), approved by Jon 2026-10-18 14:08, frozen there): do REAL RULED period medical tables show the F-40 core
behaviour -- in-line core reuse with cross-line avoidance, and the full signature?

FROZEN DESIGN (D-066 (m), copied; nothing here changes a rule, gate or call):
 Texts: Al-Kindi De rerum gradibus compound-degree tables and the Tacuinum sanitatis table rows from the 1531 Strasbourg
 Schott volume (archive.org BIUSante_00188x01 and bub_gb_9lIU1a_-ddAC OCR), and Ibn Jazlah Tacuini aegritudinum 1532
 (b14562455_0002).  Argon's line ranges are pointers only.  Each table row becomes one line, cell order as printed.  Rows
 are selected by layout rule (a ruled row with >= 3 cells), written down before any statistic is computed, and every row
 meeting the rule is kept.  Legibility gate: a text enters only if it has >= 1,300 tokens after s107's cleaning rules, and a
 hand-checked sample of 20 rows matches the page image on >= 90% of tokens; otherwise it is reported as illegible, not
 scored.  Scoring: s107's code and constants imported unchanged (hash-checked against the 13:49 s107 stub); CALL =
 SHOWS_F40_CORE for ANY admitted text, printed True/False, plus (b)+(c) separately.  Stopping rule: none shows it -> ruled
 period medical tables do not produce the core behaviour, and the tabular-content reading loses its strongest form; any
 shows it -> F-40 is restated (not unique among texts) and a tabular source becomes a live rival for G2.  Compute: 2 CPU
 workers below-normal, 2 CPU-hours.  Brief: if no text passes the legibility gate, CALL is printed NOT ASSESSABLE.

MACHINERY (imported, unchanged): s107_tabular_medical_reference as S107 (its file sha256 must equal the hash recorded for it
 in s107_tabular_medical_reference.prereg.sha256, frozen 13:49; else STOP).  Used from S107: tok (s107 cleaning:
 S87.tokens_norm after removing the ordinal signs), profile_safe, bc, ntok, measure_job_safe (already installed in S97 by
 S107's import: a battery job that raises returns None -> battery NOT ASSESSABLE, not patched), SEED.  Used through S107:
 S97 (profile_g, flags, fmt, SEGS, MIN_CORE_SHARE, battery: ref_jobs / ctl_jobs / run_pool / battery_score / bat_line,
 PC1_MIN, SEED, TRANSLITS, N_TOT/NB/N_MATCH, MIN_FREE_GB), S87, S91, S67, S80.  The gate (PC1 planted LP91 on >= 2/3 seeds;
 PC2 IT2a as control FULL; NC Augustine FULL = False) and the Voynich locality band are re-composed exactly as s107's main()
 does (s107's main is not a function), with the same seeds and indices.  S107 redirects S97.emit / S97.flush to itself at
 import (its flush writes results_s107.txt); s108 re-points S97.emit / S97.flush, S107.emit / S107.flush and S107.OUT to its
 own log before anything runs, and checks at the end that results_s107.txt is byte-identical to its start.

ROW-SELECTION RULE (written 2026-10-18 before any statistic on these texts; applied to EVERY page of each volume):
 Inputs per page: the archive.org page image (page/n<k>_w1200.jpg as served) and the archive.org OCR word boxes (djvu.xml,
 same page index k).  Word boxes are scaled to the image by (image size / djvu page size).
 1. Ink: grey < 115 (black type) or red ink (R-G > 45, R-B > 35, G < 185; the 1531 tables are printed in red); the dark scan
    surround is masked (paper = rows/columns more than half bright, grey > 150; 15 px inset).
 2. Printed rules: straight strokes that survive a morphological opening with a line of length max(30, W/40) px (horizontal)
    or max(30, H/40) px (vertical), are thin (<= 10 px + 2.5 % of their length, i.e. a slight tilt is allowed), and, for
    horizontal strokes, have clear paper 4-9 px above or below (mean ink < 0.12 on one side, < 0.45 on both) and, for
    vertical strokes, beside them (< 0.20 on one side, < 0.60 on both).  Strokes are clustered (horizontal: centres within
    20 px; vertical: within 8 px).
 3. A ruled table exists on a page if at least two horizontal rule clusters each run >= 30 % of the paper width; the table
    spans x from the median left end to the median right end of those rules.  Ruled bands = the spaces between consecutive
    such rules that are >= 40 px apart.  Column rules = vertical clusters inside the table with total length
    >= max(150 px, 25 % of the table height).
 4. Cells of a band = the intervals between consecutive column rules (and the table edges); an interval narrower than 15 px
    is ignored.  An OCR word belongs to the cell that contains its box centre.  A cell is text-bearing if one of its OCR
    words contains a letter.
 5. A RULED ROW = a band with >= 3 text-bearing cells.  EVERY such row is kept, in page order then top to bottom.
 6. One row = one line; cells left to right as printed; inside a cell, words in OCR line order, then left to right; a word
    ending in - = ^ or the not-sign is joined to the next word of the same cell; the line is cleaned with S107.tok.
 7. Type set at 90 degrees: the OCR reads only horizontal type, so a cell whose type is rotated is left out of the line (its
    OCR is noise).  Orientation is measured on the image, without the OCR: the ink connected components (letters, 3-60 px)
    of the cell (8 px inset); for each, its nearest neighbour; horizontal type <=> the share of components whose nearest
    neighbour lies more horizontally than vertically is >= 0.5.  A cell with < 3 components cannot be measured and is left
    out.  Rotated cells still count as cells for rule 5.  A row whose horizontal cells give no token is counted as a ruled
    row but adds no line.
 Texts (one per source, as frozen; the second archive.org copy of the 1531 volume, bub_gb_9lIU1a_-ddAC, is the same edition
 and is not scored a second time; BIUSante_00188x01 is used, the copy Argon's pointers cite):
  T1_alkindi_1531   Al-Kindi, De rerum gradibus (1531 volume, pages whose running head reads ALKINDI / DE GRADIBVS: OCR
                    pages n141-n164).  Its tables have horizontal rules and NO column rules (columns stand apart by space),
                    so rule 4 is replaced for this text only: cells = groups of OCR words in a band separated by a
                    horizontal gap > 3 % of the paper width; rules 1-3, 5-7 unchanged (orientation is not needed: all its
                    type is horizontal).
  T2_tacuinum_1531  every other ruled row of the 1531 volume (BIUSante_00188x01): the Tacuinum sanitatis tables (cells set
                    horizontally: Melius ex re ipsa, Iuvamentum, Nocumentum, Remotio nocumenti; the Nomina / Naturae /
                    Gradus and complexion / age / season / region columns are set at 90 degrees) and any other page that
                    meets the rule.
  T3_ibnjazlah_1532 every ruled row of b14562455_0002 (Tabula universalis; particular tables: Nomina, Causa, Signum,
                    Evacuatio, Cura regalis, Cura levis inventionis set horizontally; Complexio / Aetas / Tempus / Regio /
                    Salus set at 90 degrees).

LEGIBILITY GATE (per text, as frozen; a text that fails is reported ILLEGIBLE and not scored):
 (i)  >= 1,300 tokens after S107.tok over all its lines;
 (ii) 20 rows sampled with numpy default_rng(SEED108 + text index) without replacement from its lines (rows with >= 1
      token), each checked by the running agent against the page image (the row's crop, written to runs/s108/legibility/),
      recorded row by row in runs/s108/legibility_check.tsv BEFORE the freeze (hashed in the stub, with the
      --extract row files runs/s108/rows_<text>.tsv, which the run must reproduce).  Token match: the agent
      reads the printed tokens of the row's horizontally set cells (long s read as f, as the OCR does; abbreviation marks
      dropped, as S87.tokens_norm drops them; u/v and i/j as printed), counts n_printed, n_extracted (the line's tokens) and
      n_matched (extracted tokens that equal a printed token at its place in the row).  Match = sum n_matched / sum
      max(n_printed, n_extracted) over the 20 rows; the text passes iff match >= 0.90.  A row whose band is not one printed
      row is noted in the check and scored by the same token count.
 If no text passes, every call is printed NOT ASSESSABLE and no signature statistic is computed on these texts.

PRE-REGISTERED CALLS (D-066 (m), s107 definitions, unchanged):
 SHOWS_F40_CORE(X) = for at least one APPLICABLE segmenter of {identity, slot, affix2} (core share >= 0.5): (b) R_within(1)
   > 1 with p < 0.05 AND (c) R_cross(1) < R_within(1)  (S107.bc).  Printed per text with (b) and (c) separately.
 SIGNATURE(X) = every applicable segmenter has all four parts (S87.c1); FULL_VOYNICH_LIKE(X) = SIGNATURE and battery holds on
   ZL3b, RF1b and IT2a (>= 4/6 on >= 8/15 folds each); the battery is reported NOT ASSESSABLE where a job raises (not
   patched; the call does not depend on it).
 CALL_SHOWS_F40_CORE = SHOWS_F40_CORE(X) for ANY admitted X.  Printed '= True/False' (or '= NOT ASSESSABLE' if no text is
   admitted).  GATE (PC1, PC2, NC, as s107) is printed beside it; if GATE fails the VERDICT reads 'uninformative'.
 VERDICT (stopping rule): CALL True -> "F-40 restated (not unique among texts): <texts>; a tabular source becomes a live
   rival for G2"; CALL False -> "ruled period medical tables do not produce the core behaviour; the tabular-content reading
   loses its strongest form"; NOT ASSESSABLE -> "no ruled table text passed the legibility gate".
DESCRIPTIVE (no call): all signature parts per text and segmenter, D, POWER rows (planted LP91 identity and IT2a slot cut to
 each admitted text's size, as s107), size flags (below 22,500; pages < 15).
FIXTURE (--fx108; synthetic only): (FXa) a drawn grid with black and red rules, one cell of rotated type, OCR boxes placed
 in cells -> the row/cell rule returns the planted rows, cells, order and orientation; (FXb) hyphen join and S107.tok;
 (FXc) the whitespace-cell rule of T1; (FXd) planted LP91 (b)+(c) detected at 1,300 and 10,000 tokens, Markov prose not
 (as s107's FXd).  Writes runs/s108/fixture_<stamp>.txt only.
COMPUTE: profiles on the GPU (torch cuda) in the main process; battery in 2 spawn workers (S97.N_WORKERS), BelowNormal; page
 extraction single process BelowNormal; free RAM >= 4 GB checked before the statistics and before the pool (else STOP).  Budget 2 CPU-h.
Modes: --extract (rows, token counts, legibility sample and crops; no statistic), --fx108, --list-files, default = the run.
Writes ONLY results_s108.txt (never overwritten; if it exists the run stops), runs/s108/ sidecars and fixture files.
Run: python -I s108_ruled_medical_tables.py
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import csv  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import OrderedDict  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402
import defusedxml.ElementTree as ET  # noqa: E402  (untrusted downloaded XML)

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

import torch  # noqa: E402

import s107_tabular_medical_reference as S107  # noqa: E402

S97 = S107.S97
S87, S91, S67, S80 = S97.S87, S97.S91, S97.S67, S97.S80
SlotSegmenter = S97.SlotSegmenter

SELF = ROOT / "s108_ruled_medical_tables.py"
STUB = ROOT / "s108_ruled_medical_tables.prereg.sha256"
S107_STUB = ROOT / "s107_tabular_medical_reference.prereg.sha256"
S107_RESULTS = ROOT / "results_s107.txt"
RUN_DIR = ROOT / "runs" / "s108"
LEG_DIR = RUN_DIR / "legibility"
LEG_CHECK = RUN_DIR / "legibility_check.tsv"
DATA = ROOT / "data" / "controls_tabular_ruled"
FIXTURE = "--fx108" in sys.argv
EXTRACT = "--extract" in sys.argv
LIST_FILES = "--list-files" in sys.argv
OUT = ((RUN_DIR / f"fixture_{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt") if FIXTURE
       else (RUN_DIR / f"extract_{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt") if EXTRACT
       else ROOT / "results_s108.txt")
SEED108 = 20261108
N_TOT, NB, N_MATCH = S97.N_TOT, S97.NB, S97.N_MATCH
MIN_FREE_GB = S97.MIN_FREE_GB
TRANSLITS = S97.TRANSLITS
MIN_TOKENS, N_SAMPLE, MIN_MATCH = 1300, 20, 0.90
SRC = OrderedDict([
    ("T1_alkindi_1531", dict(xml=DATA / "schott1531_biusante" / "BIUSante_00188x01_djvu.xml",
                             img=DATA / "schott1531_biusante" / "pages", part="alkindi", idx=1,
                             lab="Al-Kindi De rerum gradibus tables (1531, BIU Sante copy), one ruled row per line")),
    ("T2_tacuinum_1531", dict(xml=DATA / "schott1531_biusante" / "BIUSante_00188x01_djvu.xml",
                              img=DATA / "schott1531_biusante" / "pages", part="rest", idx=2,
                              lab="Tacuinum sanitatis 1531 ruled rows (BIU Sante copy), one ruled row per line")),
    ("T3_ibnjazlah_1532", dict(xml=DATA / "ibnjazlah1532" / "b14562455_0002_djvu.xml",
                               img=DATA / "ibnjazlah1532" / "pages", part="all", idx=3,
                               lab="Ibn Jazlah Tacuini aegritudinum 1532, one ruled row per line")),
])
MANIFESTS = [DATA / "schott1531_biusante" / "pages_manifest.sha256", DATA / "ibnjazlah1532" / "pages_manifest.sha256"]
DATA_FILES = ([f"data/translit/{f}.meta.json" for f in TRANSLITS.values()]
              + ["data/controls/latin_augustine.txt", "runs/s97/profiles.csv", "results_s97.txt", "results_s107.txt",
                 "s107_tabular_medical_reference.prereg.sha256", "data/controls_tabular_ruled/README.md",
                 "data/controls_tabular_ruled/schott1531_biusante/BIUSante_00188x01_djvu.xml",
                 "data/controls_tabular_ruled/ibnjazlah1532/b14562455_0002_djvu.xml"]
              + [p.relative_to(ROOT).as_posix() for p in MANIFESTS]
              + ["runs/s108/legibility_check.tsv"] + [f"runs/s108/rows_{n}.tsv" for n in SRC])
log: list[str] = []
T0 = time.time()


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


# s107 installed its own emit/flush in S97 at import (its flush writes results_s107.txt): re-point everything to s108.
S97.emit, S97.flush = emit, flush
S107.emit, S107.flush = emit, flush
S107.OUT = RUN_DIR / "_s107_out_redirect_never_written.txt"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def s107_hash_check():
    want = None
    for ln in S107_STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            h, f = ln.split(None, 1)
            if f.lstrip("*").strip() == "s107_tabular_medical_reference.py":
                want = h
    have = sha256(ROOT / "s107_tabular_medical_reference.py")
    return want, have, (want is not None and want == have)


def stub_files():
    mods = set(S97.local_modules()) | {SELF.name, "s107_tabular_medical_reference.py"}
    return sorted(mods) + list(DATA_FILES)


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
    missing = [m for m in stub_files() if m not in want]
    ok = bool(want) and not bad and not missing
    return "True" if ok else f"False (mismatch: {', '.join(bad) or '-'}; not in stub: {', '.join(missing) or '-'})"


def manifest_ok(man: Path):
    bad = []
    for ln in man.read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        p = man.parent / f.lstrip("*").strip()
        if not p.exists() or sha256(p) != h:
            bad.append(f)
    return bad


# ======================================================================= row-selection rule (docstring rules 1-7)
def ink_of(a):
    a = a.astype(np.int32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    gray = (r * 299 + g * 587 + b * 114) // 1000
    red = (r - g > 45) & (r - b > 35) & (g < 185)
    ink = (gray < 115) | red
    br = gray > 150
    rows = np.where(br.mean(1) > 0.5)[0]
    cols = np.where(br.mean(0) > 0.5)[0]
    if len(rows) == 0 or len(cols) == 0:
        return ink & False, (0, 1, 0, 1)
    y0, y1, x0, x1 = int(rows[0]), int(rows[-1]), int(cols[0]), int(cols[-1])
    pad = 15
    ink[:y0 + pad] = False
    ink[y1 - pad:] = False
    ink[:, :x0 + pad] = False
    ink[:, x1 - pad:] = False
    return ink, (x0, x1, y0, y1)


def strokes(m, axis, minlen):
    st = np.ones((1, minlen), bool) if axis == 1 else np.ones((minlen, 1), bool)
    lab, _ = ndi.label(ndi.binary_opening(m, structure=st))
    out = []
    for ys, xs in ndi.find_objects(lab):
        a, b, c, d = ys.start, ys.stop, xs.start, xs.stop
        if axis == 1:
            if b - a > 10 + 0.025 * (d - c):
                continue
            up = m[max(0, a - 9):max(0, a - 4), c:d].mean() if a > 9 else 0.0
            dn = m[b + 4:b + 9, c:d].mean()
            if not (min(up, dn) < 0.12 and max(up, dn) < 0.45):
                continue
            out.append(((a + b) / 2, c, d))
        else:
            if d - c > 10 + 0.025 * (b - a):
                continue
            lf = m[a:b, max(0, c - 9):max(0, c - 4)].mean() if c > 9 else 0.0
            rt = m[a:b, d + 4:d + 9].mean()
            if not (min(lf, rt) < 0.20 and max(lf, rt) < 0.60):
                continue
            out.append(((c + d) / 2, a, b))
    return out


def clusters(items, tol):
    out = []
    for it in sorted(items):
        if out and it[0] - out[-1][0][0] <= tol:
            out[-1].append(it)
        else:
            out.append([it])
    return out


def rules_of(m, box):
    x0, x1, y0, y1 = box
    W, H = x1 - x0, y1 - y0
    hc = [(float(np.mean([s[0] for s in c])), min(s[1] for s in c), max(s[2] for s in c), sum(s[2] - s[1] for s in c), c)
          for c in clusters(strokes(m, 1, max(30, W // 40)), 20)]
    vc = [(float(np.mean([s[0] for s in c])), min(s[1] for s in c), max(s[2] for s in c), sum(s[2] - s[1] for s in c), c)
          for c in clusters(strokes(m, 0, max(30, H // 40)), 8)]
    return hc, vc


def orientation(m, x0, x1, y0, y1):
    c = m[int(y0) + 8:int(y1) - 8, int(x0) + 8:int(x1) - 8]
    if c.size == 0:
        return "none", float("nan")
    lab, n = ndi.label(c)
    if n < 3:
        return "none", float("nan")
    pts = []
    for sl in ndi.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if (h < 3 and w < 3) or h > 60 or w > 60:
            continue
        pts.append(((sl[0].start + sl[0].stop) / 2, (sl[1].start + sl[1].stop) / 2))
    if len(pts) < 3:
        return "none", float("nan")
    P = np.array(pts)
    _, k = cKDTree(P).query(P, k=2)
    v = P[k[:, 1]] - P
    hs = float(np.mean(np.abs(v[:, 1]) > np.abs(v[:, 0])))
    return ("hor" if hs >= 0.5 else "rot"), hs


def ocr_pages(xml_path):
    root = ET.parse(xml_path).getroot()
    pages = []
    for obj in root.iter("OBJECT"):
        W, H = int(obj.get("width")), int(obj.get("height"))
        lines = []
        for ln in obj.iter("LINE"):
            ws = []
            for wd in ln.iter("WORD"):
                c = [int(x) for x in wd.get("coords").split(",")[:4]]
                ws.append((c[0], c[3], c[2], c[1], wd.text or ""))   # left, top, right, bottom
            if ws:
                lines.append(ws)
        pages.append((W, H, lines))
    return pages


def page_words(lines, sx, sy):
    out = []
    for li, ln in enumerate(lines):
        for (l, t, r, b, txt) in ln:
            out.append(dict(cx=(l + r) / 2 * sx, cy=(t + b) / 2 * sy, l=l * sx, r=r * sx, li=li, t=txt))
    return out


def cell_text(ws):
    """rule 6: OCR line order, then left to right; a word ending in - = ^ or the not-sign joins the next word."""
    out, join = [], False
    for w in sorted(ws, key=lambda w: (w["li"], w["l"])):
        t = w["t"].strip()
        if not t:
            continue
        if join and out:
            out[-1] = out[-1][:-1] + t
        else:
            out.append(t)
        join = out[-1][-1] in "-=^¬"
    return " ".join(out)


def bands_of(hc, PW):
    hfull = [h for h in hc if h[3] >= 0.30 * PW]
    if len(hfull) < 2:
        return None, None, None
    tx0 = float(np.median([h[1] for h in hfull]))
    tx1 = float(np.median([h[2] for h in hfull]))
    ys = [h[0] for h in hfull]
    bands = [(a, b) for a, b in zip(ys, ys[1:]) if b - a >= 40]
    return bands, tx0, tx1


def page_rows(a, W, H, lines, whitespace_cells=False):
    """docstring rules 1-7 on one page: a = RGB image array; W, H = djvu page size; lines = OCR lines."""
    m, box = ink_of(a)
    ih, iw = m.shape
    sx, sy = iw / W, ih / H
    PW = box[1] - box[0]
    hc, vc = rules_of(m, box)
    bands, tx0, tx1 = bands_of(hc, PW)
    if not bands:
        return []
    words = page_words(lines, sx, sy)
    rows = []
    if whitespace_cells:
        gap = 0.03 * PW
        for ya, yb in bands:
            ws = sorted([w for w in words if ya <= w["cy"] < yb and tx0 - 20 <= w["cx"] <= tx1 + 20], key=lambda w: w["l"])
            groups, last_r = [], None
            for w in ws:
                if last_r is None or w["l"] - last_r > gap:
                    groups.append([w])
                    last_r = w["r"]
                else:
                    groups[-1].append(w)
                    last_r = max(last_r, w["r"])
            cells = [dict(x=(g[0]["l"], g[-1]["r"]), ori="hor", hs=float("nan"), text=cell_text(g)) for g in groups
                     if any(re.search(r"[A-Za-z]", w["t"]) for w in g)]
            rows.append(dict(y=(ya, yb), cells=cells))
        return rows
    ty0, ty1 = bands[0][0], bands[-1][1]
    cols = sorted(set([tx0, tx1] + [v[0] for v in vc if v[3] >= max(150, 0.25 * (ty1 - ty0)) and tx0 + 15 < v[0] < tx1 - 15]))
    for ya, yb in bands:
        cells = []
        for xa, xb in zip(cols, cols[1:]):
            if xb - xa < 15:
                continue
            ws = [w for w in words if xa <= w["cx"] < xb and ya <= w["cy"] < yb]
            if not any(re.search(r"[A-Za-z]", w["t"]) for w in ws):
                continue
            ori, hs = orientation(m, xa, xb, ya, yb)
            cells.append(dict(x=(xa, xb), ori=ori, hs=hs, text=cell_text(ws)))
        rows.append(dict(y=(ya, yb), cells=cells))
    return rows


def running_head(lines):
    return re.sub(r"[^A-Z]", "", " ".join(w[4] for ln in lines[:4] for w in ln).upper())


def alkindi_pages(P):
    """pages whose running head reads ALKINDI / DEGRADIBVS (rule T1): the contiguous run around the Al-Kindi title."""
    hits = [k for k, (_, _, lines) in enumerate(P) if lines and (("KIND" in running_head(lines)) or ("GRADIB" in running_head(lines))
                                                                  or ("RADIBV" in running_head(lines)))]
    hits = [k for k in hits if k > 100]
    return list(range(min(hits), max(hits) + 2)) if hits else []


def extract_text(name, spec, P=None):
    """-> rows (dicts with page, y, cells, tokens), counts; applies the rule to every page of the volume."""
    import psutil
    try:
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:  # noqa: BLE001
        pass
    P = P if P is not None else ocr_pages(spec["xml"])
    ak = set(alkindi_pages(P)) if spec["part"] in ("alkindi", "rest") else set()
    if spec["part"] == "alkindi":
        pages = sorted(ak)
    elif spec["part"] == "rest":
        pages = [k for k in range(len(P)) if k not in ak]
    else:
        pages = list(range(len(P)))
    out, n_ruled, n_bands = [], 0, 0
    for k in pages:
        W, H, lines = P[k]
        ip = spec["img"] / f"n{k:03d}.jpg"
        if not lines or not ip.exists():
            continue
        a = np.asarray(Image.open(ip).convert("RGB"))
        rows = page_rows(a, W, H, lines, whitespace_cells=(spec["part"] == "alkindi"))
        n_bands += len(rows)
        for r in rows:
            if len(r["cells"]) < 3:
                continue
            n_ruled += 1
            hor = [c for c in r["cells"] if c["ori"] == "hor"]
            toks = S107.tok(" ".join(c["text"] for c in hor))
            out.append(dict(page=k, y=[float(r["y"][0]), float(r["y"][1])], cells=r["cells"], ncell=len(r["cells"]),
                            nhor=len(hor), tokens=toks))
    return out, dict(pages=len(pages), alkindi_pages=sorted(ak) if spec["part"] == "alkindi" else None, bands=n_bands,
                     ruled_rows=n_ruled, lines=sum(1 for r in out if r["tokens"]), tokens=sum(len(r["tokens"]) for r in out))


def legibility_sample(name, spec, rows):
    rng = np.random.default_rng(SEED108 + spec["idx"])
    cand = [i for i, r in enumerate(rows) if r["tokens"]]
    if len(cand) < N_SAMPLE:
        return cand
    return sorted(rng.choice(cand, size=N_SAMPLE, replace=False).tolist())


def read_leg_check():
    out = {}
    if not LEG_CHECK.exists():
        return out
    with LEG_CHECK.open(encoding="utf-8") as fh:
        for r in csv.DictReader((ln for ln in fh if not ln.startswith("#")), delimiter="\t"):
            out.setdefault(r["text"], []).append(r)
    return out


def leg_score(recs):
    num = sum(int(r["n_matched"]) for r in recs)
    den = sum(max(int(r["n_printed"]), int(r["n_extracted"])) for r in recs)
    return num, den, (num / den if den else float("nan"))


# ======================================================================= extract mode (no statistic)
def run_extract():
    emit("S108 EXTRACT (row-selection rule, token counts, legibility sample; no signature statistic)")
    emit(f"date: {S87.clock()}")
    emit(f"s108 sha256={sha256(SELF)}")
    LEG_DIR.mkdir(parents=True, exist_ok=True)
    cache = {}
    for name, spec in SRC.items():
        P = cache.setdefault(str(spec["xml"]), ocr_pages(spec["xml"]))
        rows, info = extract_text(name, spec, P)
        emit(f"\n=== {name}: {spec['lab']}")
        emit(f"  {info}")
        with (RUN_DIR / f"rows_{name}.tsv").open("w", encoding="utf-8", newline="\n") as fh:
            for i, r in enumerate(rows):
                fh.write(f"{i}\tn{r['page']:03d}\t{int(r['y'][0])}-{int(r['y'][1])}\tcells {r['ncell']} hor {r['nhor']}\t"
                         f"{' '.join(r['tokens'])}\n")
        samp = legibility_sample(name, spec, rows)
        emit(f"  legibility sample ({len(samp)} rows, seed {SEED108 + spec['idx']}): {samp}")
        for i in samp:
            r = rows[i]
            a = Image.open(spec["img"] / f"n{r['page']:03d}.jpg").convert("RGB")
            y0, y1 = max(0, int(r["y"][0]) - 6), min(a.size[1], int(r["y"][1]) + 6)
            xs = [c["x"] for c in r["cells"]]
            x0, x1 = max(0, int(min(x[0] for x in xs)) - 10), min(a.size[0], int(max(x[1] for x in xs)) + 10)
            crop = a.crop((x0, y0, x1, y1))
            if crop.size[0] < 1400:
                f = 1400 / crop.size[0]
                crop = crop.resize((int(crop.size[0] * f), int(crop.size[1] * f)))
            crop.save(LEG_DIR / f"{name}_row{i:04d}.jpg", quality=90)
            emit(f"  [{i}] n{r['page']:03d} y{int(r['y'][0])}-{int(r['y'][1])} cells {r['ncell']} hor {r['nhor']} | "
                 + " || ".join(f"[{c['ori']}{'' if c['hs'] != c['hs'] else f'{c[chr(104) + chr(115)]:.2f}'}] {c['text']}"
                               for c in r["cells"]))
            emit(f"      tokens ({len(r['tokens'])}): {' '.join(r['tokens'])}")
        flush()
    emit(f"\nruntime {time.time() - T0:.0f}s; finished {S87.clock()}")
    flush()


# ======================================================================= fixture
def run_fixture():
    emit("S108 FIXTURE (synthetic only; no real data read)")
    emit(f"date: {S87.clock()}  device: {S87.DEV}; below_normal={S87.below_normal()}")
    emit(f"s108 sha256={sha256(SELF)}  stub_match={stub_match()}")
    ok = True
    # FXa: drawn grid, 3 rows x 4 columns, black and red rules, column 2 rotated type
    W, H = 1200, 1600
    img = Image.new("RGB", (W, H), (235, 225, 205))
    d = ImageDraw.Draw(img)
    xs = [100, 300, 420, 700, 1050]
    ys = [200, 450, 700, 950]
    for y in ys:
        d.line([(xs[0], y), (xs[-1], y)], fill=(170, 40, 30), width=3)      # red horizontal rules
    for x in xs:
        d.line([(x, ys[0]), (x, ys[-1])], fill=(20, 20, 20), width=3)       # black column rules
    rng = np.random.default_rng(1)

    def hor_text(x0, y0, nlines, nchar):
        for li in range(nlines):
            for ci in range(nchar):
                if ci % 6 == 5:
                    continue
                xx, yy = x0 + ci * 13, y0 + li * 34
                d.rectangle([xx, yy, xx + 8, yy + 14], fill=(15, 15, 15))

    def rot_text(x0, y0, ncol, nchar):
        for li in range(ncol):
            for ci in range(nchar):
                if ci % 6 == 5:
                    continue
                xx, yy = x0 + li * 34, y0 + ci * 13
                d.rectangle([xx, yy, xx + 14, yy + 8], fill=(15, 15, 15))
    words, li = [], 0
    for ri in range(3):
        ya = ys[ri]
        for ci, (xa, xb) in enumerate(zip(xs, xs[1:])):
            if ci == 1:
                rot_text(xa + 20, ya + 20, 3, 15)
                txt = [f"zz{ri}"]
            else:
                hor_text(xa + 20, ya + 30, 3, max(6, (xb - xa - 40) // 13))
                txt = [f"w{ri}{ci}a", f"w{ri}{ci}b-", "c"] if ci == 2 else [f"w{ri}{ci}a", f"w{ri}{ci}b"]
            for wi, t in enumerate(txt):
                l = xa + 25 + 60 * wi
                words.append((li, (l, ya + 40, l + 50, ya + 60, t)))
            li += 1
    lines = {}
    for li_, w in words:
        lines.setdefault(li_, []).append(w)
    ocr = [lines[k] for k in sorted(lines)]
    rows = page_rows(np.asarray(img), W, H, ocr)
    got = [(len(r["cells"]), [c["ori"] for c in r["cells"]], " | ".join(c["text"] for c in r["cells"] if c["ori"] == "hor"))
           for r in rows]
    want = [(4, ["hor", "rot", "hor", "hor"], f"w{ri}0a w{ri}0b | w{ri}2a w{ri}2bc | w{ri}3a w{ri}3b") for ri in range(3)]
    fa = got == want
    emit(f"FXa drawn grid (red row rules, black column rules, rotated column 2): {got} -> {'PASS' if fa else 'FAIL'}")
    ok &= fa
    fb_t = S107.tok(cell_text([dict(li=0, l=0, t="melancho-"), dict(li=1, l=0, t="lico,"), dict(li=1, l=60, t="cūm"),
                               dict(li=1, l=120, t="ſyr.acet")]))
    fb = fb_t == ["melancholico", "cum", "ſyr", "acet"]
    emit(f"FXb hyphen join + S107.tok: {fb_t} -> {'PASS' if fb else 'FAIL'}")
    ok &= fb
    img2 = Image.new("RGB", (W, H), (235, 225, 205))
    d2 = ImageDraw.Draw(img2)
    for y in (300, 360, 420):
        d2.line([(100, y), (1100, y)], fill=(20, 20, 20), width=3)
    ocr2 = [[(120, 310, 220, 345, "Mafticis"), (400, 310, 430, 345, "3"), (440, 310, 470, 345, "ij"), (600, 310, 680, 345, "Partes"),
             (690, 310, 740, 345, "viij"), (850, 310, 900, 345, "Pars")],
            [(120, 370, 220, 405, "Alchon"), (600, 370, 680, 405, "partes"), (850, 370, 900, 405, "pars")]]
    rows2 = page_rows(np.asarray(img2), W, H, ocr2, whitespace_cells=True)
    got2 = [[c["text"] for c in r["cells"]] for r in rows2]
    fc = got2 == [["Mafticis", "3 ij", "Partes viij", "Pars"], ["Alchon", "partes", "pars"]]
    emit(f"FXc whitespace cells (T1 rule): {got2} -> {'PASS' if fc else 'FAIL'}")
    ok &= fc
    flush()
    names, glob, B, spec = S91.fx_world()
    prod = S91.LP91(glob, B)
    prod.set_params(S91.PLANTED)
    cB = S91.cut(prod.text(spec, 2))
    pr = S91.cut(S97.fx_prose(names, spec, 4))
    lens = [len(ln) for _, ls in cB for ln in ls]
    pnl = [len(ls) for _, ls in cB]
    lb = (0.0, 2.0)
    for n in (1300, 10000):
        pp = S87.layout(None, True, cB, lens, pnl, n_tot=n)
        qq = S87.layout(None, True, pr, lens, pnl, n_tot=n)
        p, e1 = S107.profile_safe(f"FX_LP91_n{n}", pp, S80.identity_seg_factory, SEED108 + n)
        q, e2 = S107.profile_safe(f"FX_prose_n{n}", qq, S80.identity_seg_factory, SEED108 + n + 1)
        fp, fq = S107.bc(p, lb), S107.bc(q, lb)
        emit("  " + S97.fmt(p, lb) + (f" [{e1}]" if e1 else ""))
        emit("  " + S97.fmt(q, lb) + (f" [{e2}]" if e2 else ""))
        emit(f"FXd n={n}: planted (b)+(c) {fp} (want True); Markov prose (b)+(c) {fq} (want False) -> "
             f"{'PASS' if (fp and not fq) else 'FAIL'}")
        ok &= fp and not fq
        flush()
    emit(f"FIXTURE {'PASS' if ok else 'FAIL'}   runtime {time.time() - T0:.0f}s; finished {S87.clock()}")
    flush()


# ======================================================================= main
def bc_parts(p, lb):
    _, comp, _ = S97.flags(p, lb)
    return bool(comp["b_Rwithin"]), bool(comp["c_Rcross<Rwithin"])


def main():
    if LIST_FILES:
        for m in stub_files():
            print(m)
        return
    if FIXTURE:
        run_fixture()
        return
    if EXTRACT:
        run_extract()
        return
    if OUT.exists():
        print(f"STOP: {OUT.name} exists; never overwrite")
        raise SystemExit(3)
    s107_before = sha256(S107_RESULTS)
    emit("S108: ruled period medical tables vs the F-40 core behaviour (D-066 (m); pre-registered in the docstring)")
    emit(f"date: {S87.clock()}")
    emit(f"device: {S87.DEV} ({torch.cuda.get_device_name(0) if S87.DEV.type == 'cuda' else 'cpu'}); torch {torch.__version__}; "
         f"numpy {np.__version__}; python {sys.version.split()[0]}; BelowNormal set={S87.below_normal()}; battery workers {S97.N_WORKERS}")
    emit(f"{SELF.name} sha256={sha256(SELF)}")
    emit(f"prereg stub {STUB.name} sha256={sha256(STUB) if STUB.exists() else '-'}  stub_match={stub_match()}")
    want, have, s107ok = s107_hash_check()
    emit(f"s107 import hash check vs {S107_STUB.name} (13:49): stub {want} file {have} -> {s107ok}")
    if not s107ok:
        emit("STOP: s107 scoring code differs from its frozen stub")
        flush()
        raise SystemExit(4)
    for m in stub_files():
        emit(f"  hashed {m} sha256={sha256(ROOT / m)}")
    for man in MANIFESTS:
        bad = manifest_ok(man)
        emit(f"  page-image manifest {man.relative_to(ROOT).as_posix()}: {'all match' if not bad else 'MISMATCH ' + ', '.join(bad[:5])}")
        if bad:
            emit("STOP: page images differ from the manifest")
            flush()
            raise SystemExit(5)
    emit(f"free RAM {S91.free_gb():.1f} GB at start (>= {MIN_FREE_GB} GB is required before the statistics: profiles and battery)")
    emit(f"N_TOT {N_TOT}; N_match {N_MATCH}; order/R shuffles {S87.N_SHUF_ORDER}/{S87.N_SHUF_R}; locality perms {S87.N_PERM_LOC}, "
         f"boot {S87.N_BOOT}; battery N_DRAW {S67.N_DRAW}, fold >= {S97.BAT_MIN_HOLD}/6, >= {S97.BAT_MIN_FOLDS}/15 folds per T; "
         f"MIN_CORE_SHARE {S97.MIN_CORE_SHARE}; s97 seed {S97.SEED}; s107 seed {S107.SEED}; s108 seed {SEED108}")
    flush()

    # ---- texts and legibility gate (before any statistic on them)
    emit("\n=== ruled-row extraction (docstring rules 1-7, every page) and LEGIBILITY GATE ===")
    LEG = read_leg_check()
    cache, ROWS, ADMIT, LEGROWS = {}, OrderedDict(), OrderedDict(), OrderedDict()
    for name, spec in SRC.items():
        P = cache.setdefault(str(spec["xml"]), ocr_pages(spec["xml"]))
        rows, info = extract_text(name, spec, P)
        ROWS[name] = rows
        frozen = (RUN_DIR / f"rows_{name}.tsv")
        same = None
        if frozen.exists():
            mine = [f"{i}\tn{r['page']:03d}\t{int(r['y'][0])}-{int(r['y'][1])}\tcells {r['ncell']} hor {r['nhor']}\t{' '.join(r['tokens'])}"
                    for i, r in enumerate(rows)]
            same = mine == frozen.read_text(encoding="utf-8").splitlines()
        nt = info["tokens"]
        samp = legibility_sample(name, spec, rows)
        recs = LEG.get(name, [])
        num, den, frac = leg_score(recs)
        ids_ok = sorted(int(r["row"]) for r in recs) == samp
        g1 = nt >= MIN_TOKENS
        g2 = len(recs) == N_SAMPLE and ids_ok and frac >= MIN_MATCH
        ADMIT[name] = g1 and g2
        LEGROWS[name] = dict(tokens=nt, g1=g1, recs=len(recs), ids_ok=ids_ok, num=num, den=den, frac=frac, g2=g2, info=info,
                             same_as_extract=same)
        emit(f"  {name:20s} {spec['lab']}")
        emit(f"      pages {info['pages']}; ruled bands {info['bands']}; ruled rows (>= 3 cells) {info['ruled_rows']}; lines with tokens "
             f"{info['lines']}; tokens {nt}; rows identical to --extract file: {same}")
        emit(f"      gate (i) tokens {nt} >= {MIN_TOKENS}: {g1}; gate (ii) hand check {len(recs)} rows (sample ids match: {ids_ok}): "
             f"{num}/{den} = {frac:.3f} >= {MIN_MATCH}: {g2}  ->  {'ADMITTED' if ADMIT[name] else 'ILLEGIBLE, not scored'}")
    flush()
    admitted = [n for n, v in ADMIT.items() if v]

    zl = S80.S55.voynich_pages("ZL3b")
    line_lens = [len(ln) for p in zl for ln in p["lines"] if ln]
    page_nl = [len(p["lines"]) for p in zl]

    def lay_lines(lines, n_tot=N_TOT):
        return S87.layout(lines, True, None, line_lens, page_nl, n_tot)

    if not admitted:
        emit("\n=== calls ===")
        emit("  no text passed the legibility gate; no signature statistic computed on any ruled table text")
        emit("  CALL_SHOWS_F40_CORE = NOT ASSESSABLE")
        emit("\nVERDICT: CALL_SHOWS_F40_CORE = NOT ASSESSABLE: no ruled table text passed the legibility gate")
        _sidecars(LEGROWS, None, None, None, None, None, None)
        _end(s107_before)
        return

    fg = S91.free_gb()
    emit(f"free RAM {fg:.1f} GB (need >= {MIN_FREE_GB})")
    if not (fg >= MIN_FREE_GB):
        emit(f"STOP: free RAM {fg:.1f} GB < {MIN_FREE_GB} GB")
        flush()
        raise SystemExit(2)

    # ---- Voynich target (s97 seeds, as s107)
    emit("\n=== Voynich target (SlotSegmenter cores, s87 seeds; as s97/s107) ===")
    VOY = OrderedDict()
    for i, T in enumerate(TRANSLITS):
        P_ = [(p["id"], p["lines"]) for p in S80.S55.voynich_pages(T)]
        pages = S87.layout(None, True, P_, line_lens, page_nl)
        VOY[T] = (pages, S97.profile_g(f"VOY_{T}", pages, SlotSegmenter, N_MATCH, S87.SEED + 100 * i))
    lb = S87.loc_band_from([v[1] for v in VOY.values()])
    emit(f"LOCALITY band: [{lb[0]:.4f}, {lb[1]:.4f}] (s97/s107: [0.9074, 1.0499])")
    rw_v = float(np.mean([v[1]["rep"][1]["Rw"] for v in VOY.values()]))
    rc_v = float(np.mean([v[1]["rep"][1]["Rc"] for v in VOY.values()]))
    for T, (_, p) in VOY.items():
        emit("  " + S97.fmt(p, lb))
    flush()

    emit("\n=== texts ===")
    aug = S87.load_control("latin_augustine.txt")
    allT = list(TRANSLITS)
    TEXTS = OrderedDict()
    TEXTS["PC2_VOY_IT2a_as_control"] = ("gate", VOY["IT2a"][0], ["slot"], ["IT2a"], 0, S97.SEED, "IT2a words, real pages, control path")
    TEXTS["NC_augustine_la"] = ("gate", S87.layout(aug, False, None, line_lens, page_nl), list(S97.SEGS), allT, 1, S97.SEED,
                                "plain Latin prose (Augustine), ZL3b line lengths")
    for name in admitted:
        lines = [r["tokens"] for r in ROWS[name] if r["tokens"]]
        TEXTS[name] = ("tabular", lay_lines(lines), list(S97.SEGS), allT, 20 + SRC[name]["idx"], SEED108, SRC[name]["lab"])
    FLAGS = {}
    for n, (role, pages, segs, Ts, xi, sd, lab) in TEXTS.items():
        nt = S107.ntok(pages)
        fl = (["below 22,500"] if nt < N_TOT else []) + (["pages < 15"] if len(pages) < NB else [])
        FLAGS[n] = fl
        nl = sum(len(ls) for _, ls in pages)
        emit(f"  {n:26s} {role:8s} tokens {nt:6d} pages {len(pages):4d} lines {nl:5d} mean line {nt / max(1, nl):5.1f}  {lab}"
             f"{'  FLAG: ' + '; '.join(fl) if fl else ''}")
    flush()

    # ---- PC1 (as s97/s107)
    emit("\n=== GATE PC1: s91 LP91 at PLANTED " + str(S91.PLANTED) + " on ZL3b lexicon/layout (identity on emitted cores; as s97) ===")
    zp = S67.load_pages(ROOT / "data" / "translit" / f"{TRANSLITS['ZL3b']}.meta.json")
    segz = SlotSegmenter([w for _, _, ls in zp for l in ls for w in l])
    cz = {}

    def zcore(w):
        c = cz.get(w)
        if c is None:
            c = cz[w] = segz.segment(w)[1]
        return c
    zcp = [(p, q, [[zcore(w) for w in l] for l in ls]) for p, q, ls in zp]
    from collections import Counter
    glob = Counter(c for _, _, ls in zcp for l in ls for c in l if c != "")
    prod = S91.LP91(glob, S91.bigram_of([(p, [[c for c in l if c != ""] for l in ls]) for p, q, ls in zcp]))
    prod.set_params(S91.PLANTED)
    spec = [(p, q, [len(l) for l in ls]) for p, q, ls in zp]
    pc1, lp_pages = [], None
    for s in (1, 2, 3):
        pages = S91.cut(prod.text(spec, S97.SEED + s))
        if s == 1:
            lp_pages = pages
        p = S97.profile_g(f"PC1_LP91_planted_s{s}", pages, S80.identity_seg_factory, N_MATCH, S97.SEED + 10 + s)
        pc1.append(S97.flags(p, lb)[0])
        emit("  " + S97.fmt(p, lb, f" | D {S87.distance(p, lb, rw_v, rc_v)[0]:.2f}"))
    PC1 = sum(pc1) >= S97.PC1_MIN
    emit(f"  PC1 Voynich-like on {sum(pc1)}/3 seeds (need >= {S97.PC1_MIN}) -> {'PASS' if PC1 else 'FAIL'}")
    flush()

    # ---- signature profiles
    emit("\n=== signature profiles (C1 flags a order, b R_within, c R_cross<R_within, d locality) ===")
    PR, ERR = OrderedDict(), {}
    for n, (role, pages, segs, Ts, xi, sd, lab) in TEXTS.items():
        PR[n] = OrderedDict()
        for si, sn in enumerate(segs):
            p, err = S107.profile_safe(f"{n}/{sn}", pages, S97.SEGS[sn], sd + 1000 * xi + 100 * si)
            PR[n][sn] = p
            if err:
                ERR[(n, sn)] = err
            app = p["core_share"] >= S97.MIN_CORE_SHARE
            b_, c_ = bc_parts(p, lb)
            emit("  " + S97.fmt(p, lb, f" | D {S87.distance(p, lb, rw_v, rc_v)[0]:.2f} | (b) {b_} (c) {c_} b+c {S107.bc(p, lb)}"
                              f"{'' if app else ' [NOT APPLICABLE: core share < 0.5]'}{' [order/locality not computable: ' + err + ']' if err else ''}"))
            flush()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # ---- power rows (descriptive)
    emit("\n=== POWER (descriptive): planted LP91 seed 1 (identity) and IT2a (slot) cut to each admitted text's size ===")
    POW = OrderedDict()
    for n, (role, pages, *_r) in TEXTS.items():
        if role != "tabular":
            continue
        nt = S107.ntok(pages)
        for lab2, src, segf, sd in (("LP91", lp_pages, S80.identity_seg_factory, SEED108 + 7), ("IT2a", VOY["IT2a"][0], SlotSegmenter, SEED108 + 8)):
            pp = S87.layout(None, True, src, line_lens, page_nl, n_tot=nt)
            p, err = S107.profile_safe(f"PWR_{lab2}_n{nt}", pp, segf, sd + nt)
            POW[(n, lab2)] = S107.bc(p, lb)
            emit("  " + S97.fmt(p, lb, f" | b+c {S107.bc(p, lb)} (size of {n}){' [' + err + ']' if err else ''}"))
            flush()

    # ---- battery
    emit("\n=== s67 slot battery (text block b vs real Voynich fold folds[b]) ===")
    ref = OrderedDict((T, S67.load_pages(ROOT / "data" / "translit" / f"{f}.meta.json")) for T, f in TRANSLITS.items())
    folds = S67.folds_of(ref["ZL3b"])
    emit(f"  folds ({len(folds)}): {' '.join(folds)}")
    assert len(folds) == NB
    jobs = S97.ref_jobs(ref, folds)
    for n, (role, pages, segs, Ts, xi, sd, lab) in TEXTS.items():
        jobs += S97.ctl_jobs(n, xi + 1, pages)
    M = S97.run_pool(jobs, "battery")
    bad = {k: v[1] for k, v in M.items() if v[0] is None}
    if bad:
        emit(f"  {len(bad)} Measured jobs raised: " + "; ".join(f"{k}: {e}" for k, e in list(bad.items())[:6]))
    BAT = OrderedDict()
    for n, (role, pages, segs, Ts, xi, sd, lab) in TEXTS.items():
        keys = [("CTL", n, b) for b in range(NB)] + [("REF", T, b) for T in Ts for b in range(NB)]
        if any(M[k][0] is None for k in keys):
            BAT[n] = None
            emit(f"  {n:26s} battery NOT ASSESSABLE (a Measured job raised; battery = False)")
            continue
        try:
            BAT[n] = S97.battery_score(n, Ts, M, ref, folds, pages)
        except Exception as e:  # noqa: BLE001
            BAT[n] = None
            emit(f"  {n:26s} battery NOT ASSESSABLE ({repr(e)[:120]}; battery = False)")
            continue
        for T, r in BAT[n].items():
            emit(f"  {n:26s} " + S97.bat_line(T, r))
    flush()

    # ---- calls
    emit("\n=== calls ===")
    FULL, SHOWS, SIG, DESC = OrderedDict(), OrderedDict(), OrderedDict(), OrderedDict()
    for n, (role, pages, segs, Ts, xi, sd, lab) in TEXTS.items():
        app = [sn for sn in segs if PR[n][sn]["core_share"] >= S97.MIN_CORE_SHARE]
        sig = {sn: S97.flags(PR[n][sn], lb) for sn in segs}
        SIG[n] = bool(app) and all(sig[sn][0] for sn in app)
        bat_ok = BAT[n] is not None and all(BAT[n][T]["holds"] for T in Ts)
        FULL[n] = SIG[n] and bat_ok
        bcs = {sn: S107.bc(PR[n][sn], lb) for sn in segs}
        parts = {sn: bc_parts(PR[n][sn], lb) for sn in segs}
        SHOWS[n] = any(bcs[sn] for sn in app)
        DESC[n] = dict(role=role, flags=FLAGS[n], tokens=S107.ntok(pages), applicable=app, sig={sn: sig[sn][2] for sn in segs},
                       bc=bcs, b={sn: parts[sn][0] for sn in segs}, c={sn: parts[sn][1] for sn in segs}, sig_ok=SIG[n],
                       battery_ok=bat_ok, battery=(None if BAT[n] is None else {T: BAT[n][T]["folds_ok"] for T in Ts}),
                       Rw1={sn: PR[n][sn]["rep"][1]["Rw"] for sn in segs}, pRw1={sn: PR[n][sn]["rep"][1]["pw"] for sn in segs},
                       Rc1={sn: PR[n][sn]["rep"][1]["Rc"] for sn in segs})
        btxt = "NOT ASSESSABLE" if BAT[n] is None else " ".join(f"{T} {BAT[n][T]['folds_ok']}/15" for T in Ts)
        emit(f"  {n:26s} {role:8s} signature " + " ".join(f"{sn}:{sig[sn][2]}" for sn in segs) +
             f" (applicable {','.join(app)}) -> SIGNATURE {SIG[n]}; battery {btxt} -> {bat_ok}; FULL_VOYNICH_LIKE = {FULL[n]}; "
             f"(b) [" + " ".join(f"{sn}:{parts[sn][0]}" for sn in segs) + "] (c) [" + " ".join(f"{sn}:{parts[sn][1]}" for sn in segs)
             + f"]; SHOWS_F40_CORE (b+c) = {SHOWS[n]}" + (f"  FLAG: {'; '.join(FLAGS[n])}" if FLAGS[n] else ""))
    PC2 = FULL["PC2_VOY_IT2a_as_control"]
    NC = not FULL["NC_augustine_la"]
    GATE = PC1 and PC2 and NC
    emit(f"  GATE (as s107): PC1 {PC1}; PC2 {PC2}; NC (plain Latin not Voynich-like) {NC} -> GATE = {GATE}")
    for name in SRC:
        if name not in admitted:
            emit(f"  {name:26s} ILLEGIBLE (legibility gate), not scored")
    hits = [n for n in admitted if SHOWS[n]]
    CALL = bool(hits)
    emit(f"  CALL_SHOWS_F40_CORE = {CALL}")
    if not GATE:
        why = [k for k, v in (("PC1", PC1), ("PC2", PC2), ("NC", NC)) if not v]
        reading = f"uninformative: s107 gate failed ({', '.join(why)})"
    elif CALL:
        reading = ("F-40 restated (not unique among texts): " + ", ".join(hits)
                   + "; a tabular source becomes a live rival for G2")
    else:
        reading = ("ruled period medical tables do not produce the core behaviour (" + ", ".join(admitted)
                   + "); the tabular-content reading loses its strongest form")
    emit(f"\nVERDICT: CALL_SHOWS_F40_CORE = {CALL}: {reading}")
    _sidecars(LEGROWS, PR, VOY, lb, rw_v, rc_v, dict(PC1=PC1, PC1_seeds=pc1, PC2=PC2, NC=NC, GATE=GATE, CALL=CALL, SHOWS=SHOWS,
                                                      SIG=SIG, FULL=FULL, desc=DESC, admitted=admitted,
                                                      power={f"{a}|{b}": v for (a, b), v in POW.items()},
                                                      errors={f"{a}|{b}": v for (a, b), v in ERR.items()}, verdict=reading))
    _end(s107_before)


def _sidecars(LEGROWS, PR, VOY, lb, rw_v, rc_v, calls):
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    if PR is not None:
        with (RUN_DIR / "profiles.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["text", "segmenter", "tokens", "types", "core_share", "te_tok", "o100", "p100", "o200", "Rw1", "pRw1", "Rc1",
                        "loc", "loc_lo", "loc_hi", "C1", "flags", "bc", "D"])
            rows = [(f"VOY_{T}", "slot", v[1]) for T, v in VOY.items()] + [(n, sn, p) for n in PR for sn, p in PR[n].items()]
            for n, sn, p in rows:
                o, r, l = p["order"], p["rep"], p["loc"]
                ok, _, fl = S97.flags(p, lb)
                w.writerow([n, sn, p["tokens"], p["types"], f"{p['core_share']:.4f}", p["te_tok"], f"{o[100]['mm']:.6f}",
                            f"{o[100]['p']:.4f}", f"{o[200]['mm']:.6f}", f"{r[1]['Rw']:.4f}", f"{r[1]['pw']:.4f}", f"{r[1]['Rc']:.4f}",
                            f"{l['ratio']:.4f}", f"{l['lo']:.4f}", f"{l['hi']:.4f}", ok, fl, S107.bc(p, lb),
                            f"{S87.distance(p, lb, rw_v, rc_v)[0]:.3f}"])
    (RUN_DIR / "calls.json").write_text(json.dumps(dict(legibility=LEGROWS, calls=calls), indent=1, default=str),
                                        encoding="utf-8", newline="\n")
    emit("\nsidecars: runs/s108/calls.json" + (", runs/s108/profiles.csv" if PR is not None else ""))


def _end(s107_before):
    after = sha256(S107_RESULTS)
    emit(f"results_s107.txt unchanged during the run: {after == s107_before}")
    emit(f"runtime {time.time() - T0:.0f} s; finished {S87.clock()}")
    flush()


if __name__ == "__main__":
    main()
