"""S99: does a label's less-common core recur in the text lines physically nearest the label?  (Phase 6.3, design E1)

QUESTION (frozen): pseudotext produced line by line gives no reason for a label's rare core to sit in the body lines
nearest the label; content reference does.  For each label whose core is below a training-frequency threshold, rank the
page's paragraph lines by physical distance to the label and test whether the lines carrying that core sit at smaller
distance rank than under a within-page permutation of line positions.

DATA (all on disk, read-only)
  ZL3b (data/ZL3b-n.txt) through vparse.load(); Rozanova/voynichese word boxes (pixel x,y,w,h per token, reading order)
  aligned to ZL3b lines by tools/boxes.align_all (the alignment Daybreak's s112 registration also uses).
  Label = ZL unit L*, with >= 1 token string-matched to a box; label point = mean centre of its matched boxes.
  Body line = ZL unit P* with >= 1 matched box; line position = its box centres.  Page eligible: >= MIN_BODY_LINES body
  lines and >= 1 label.  Distance label -> line = min Euclidean distance (box pixels) from the label point to the line's
  box centres.  Guard: a label whose point lies inside any body-token box is dropped (box misassignment).
  Words containing '?' are skipped.

CHANNELS (event = one distinct (label, key) on an eligible page whose key occurs in k body lines, 1 <= k <= n-1)
  PRIMARY  core_slot   : SlotSegmenter core (trained on P words of pages without labels, as s109); rare = not among
                         the TOP_K most frequent training cores (s109's tail definition).  Line matches if it holds a
                         word with that core.
  SECOND   core_zat    : Zattera 12-slot segmenter core (s76 ZatteraSegmenter, und='whole'); rare = not in its TOP_K
                         training cores.  Used for the direction condition.
  NEAR     trim        : segmenter-free near-match: label word of length >= 5, key = word[1:-1]; rare = contained in
                         < RARE_SUB_SHARE of training tokens; line matches if one of its words contains the key.
  CONTROL  frame       : SlotSegmenter (prefix, suffix) of the label word, at least one non-empty; line matches if one
                         of its words has the identical frame.
  CONTROL  common_core : SlotSegmenter core that IS among the TOP_K training cores.
  CONTROL  moved       : each primary event re-scored on one random OTHER eligible page of the same ZL illustration
                         class ($I) where the core occurs in 1..n-1 lines; label point transferred in page-normalized
                         coordinates (page box extent).
  SENS     core_*_k5   : both segmenters with rare = not among the TOP_K_BROAD (5) training cores; reported only.
  RECENCY  core_slot_noadj : primary with the label's reading-order neighbours removed: the P line immediately before
                         and immediately after the label in ZL file order on that page.  Also printed: share of events
                         whose nearest matching line is such a neighbour.

STATISTIC
  Per event: lines ranked by distance (ties by file order), u_j = (rank_j - 0.5)/n; M = mean u_j over matching lines.
  T = mean M over events (0.5 = no gradient; smaller = matches nearer the label).
  Null: per page, one random permutation of line positions (line j takes the distances of line pi(j)) shared by all
  events on the page; N_PERM replicates; one-sided p = (1 + #{T* <= T}) / (N_PERM + 1).
  Power: MDE = (Z_ALPHA + Z_POWER) * SD(T*) as a shift of T below 0.5, at the n actually obtained.

PRE-REGISTERED CALL (printed as booleans)
  CALL_PRIMARY   = p(core_slot) < ALPHA
  CALL_SECOND    = T(core_zat) < 0.5  (direction)
  CALL_CONTROLS  = p(frame) >= ALPHA and p(common_core) >= ALPHA
  CALL_FIXTURE   = planted-near fixture p < ALPHA and no-relation fixture p >= ALPHA
  POSITIVE if all four.  Else: if CALL_FIXTURE False -> INCONCLUSIVE (fixture);
  if CALL_CONTROLS False -> INCONCLUSIVE (controls not null);
  if CALL_PRIMARY True but CALL_SECOND False -> INCONCLUSIVE (segmenter-dependent);
  if CALL_PRIMARY False -> NEGATIVE when MDE(core_slot) <= NEG_MDE_MAX, else INCONCLUSIVE (underpowered).
  Near-match, moved-label and recency results are reported beside the call, not part of it.

PROCESS: --planted runs only synthetic pages (reads no real data, writes runs/s99/fixture.txt).  --list-inputs prints
the files the stub must cover.  A real run refuses to score unless every stub line matches and every loaded local
module and data file is covered.  Crash protocol: FAILED / AMENDMENT OK -> results_s99_amend1.txt.
"""
from __future__ import annotations

import csv
import ctypes
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / "tools")]

PLANTED = "--planted" in sys.argv
LIST_INPUTS = "--list-inputs" in sys.argv

SELF = ROOT / "s99_label_nearby_lines.py"
STUB = ROOT / "s99_label_nearby_lines.prereg.sha256"
RUN_DIR = ROOT / "runs" / "s99"
OUT = RUN_DIR / "fixture.txt" if PLANTED else ROOT / "results_s99.txt"

SEED = 99018
N_PERM = 10000
TOP_K = 20
TOP_K_BROAD = 5          # reported-only sensitivity (pre-freeze count: Zattera at TOP_K=20 gives only ~8 events)
RARE_SUB_SHARE = 0.01
MIN_BODY_LINES = 4
ALPHA = 0.05
Z_ALPHA, Z_POWER = 1.6449, 0.8416
NEG_MDE_MAX = 0.10
MIN_FREE_GB = 4.0
DATE_EXE = Path(r"C:\Program Files\Git\usr\bin\date.exe")

log: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")


def clock():
    try:
        r = subprocess.run([str(DATE_EXE)], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now; `date` unavailable)"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def below_normal_and_ram():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        free = psutil.virtual_memory().available / 2 ** 30
    except Exception:  # noqa: BLE001
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
        free = float("nan")
    return free


# ============================================================ core statistic (shared by fixture and real run)
def event_M(D, match, keep, perm=None):
    """D: distances of the page's lines to this label (n,). match, keep: bool (n,). perm: line j takes D[perm[j]]."""
    d = D if perm is None else D[perm]
    idx = np.flatnonzero(keep)
    dd = d[idx]
    order = np.argsort(dd, kind="stable")
    ranks = np.empty(len(idx))
    ranks[order] = np.arange(1, len(idx) + 1)
    u = (ranks - 0.5) / len(idx)
    m = match[idx]
    return float(u[m].mean())


def score(events, n_perm, rng):
    """events: list of dict(page, D, match, keep).  Returns (T, null array)."""
    if not events:
        return float("nan"), np.array([])
    T = float(np.mean([event_M(e["D"], e["match"], e["keep"]) for e in events]))
    by_page = defaultdict(list)
    for e in events:
        by_page[e["page"]].append(e)
    nul = np.empty(n_perm)
    for i in range(n_perm):
        tot = 0.0
        for p, es in by_page.items():
            perm = rng.permutation(len(es[0]["D"]))
            for e in es:
                tot += event_M(e["D"], e["match"], e["keep"], perm)
        nul[i] = tot / len(events)
    return T, nul


def summarize(name, events, n_perm, rng):
    T, nul = score(events, n_perm, rng)
    if not len(nul):
        return dict(name=name, n=0, pages=0, T=float("nan"), null_mean=float("nan"), sd=float("nan"),
                    p=float("nan"), mde=float("nan"))
    p = float((1 + np.sum(nul <= T + 1e-12)) / (n_perm + 1))
    sd = float(nul.std(ddof=1))
    return dict(name=name, n=len(events), pages=len({e["page"] for e in events}), T=T,
                null_mean=float(nul.mean()), sd=sd, p=p, mde=(Z_ALPHA + Z_POWER) * sd)


def fmt(s):
    return (f"[{s['name']}] events={s['n']} pages={s['pages']} T={s['T']:.4f} null_mean={s['null_mean']:.4f} "
            f"sd={s['sd']:.4f} shift={s['null_mean'] - s['T']:+.4f} p={s['p']:.4f} MDE={s['mde']:.4f}")


# ============================================================ planted fixture (synthetic, no real data)
def synth(mode, rng, n_pages=24, events_per_page=3, n_lines=20):
    """mode 'near': each label core planted in 2 of its 3 nearest lines; 'none': in 2 random lines;
    'mild': in 1 of its 5 nearest lines + 1 random line."""
    events = []
    for p in range(n_pages):
        ly = np.sort(rng.uniform(0, 1, n_lines))
        lx0 = rng.uniform(0, 0.3, n_lines)
        lx1 = lx0 + rng.uniform(0.3, 0.7, n_lines)
        for _ in range(events_per_page):
            px, py = rng.uniform(0, 1), rng.uniform(0, 1)
            D = np.empty(n_lines)
            for j in range(n_lines):
                xs = np.linspace(lx0[j], lx1[j], 8)
                D[j] = np.min(np.hypot(xs - px, ly[j] - py))
            near = np.argsort(D, kind="stable")
            match = np.zeros(n_lines, bool)
            if mode == "near":
                match[rng.choice(near[:3], 2, replace=False)] = True
            elif mode == "mild":
                match[rng.choice(near[:5])] = True
                match[rng.integers(n_lines)] = True
            else:
                match[rng.choice(n_lines, 2, replace=False)] = True
            events.append(dict(page=f"s{p}", D=D, match=match, keep=np.ones(n_lines, bool)))
    return events


def run_fixture(n_perm):
    rng = np.random.default_rng(SEED + 1)
    out = {}
    for mode in ("near", "none", "mild"):
        ev = synth(mode, rng)
        out[mode] = summarize(f"fixture_{mode}", ev, n_perm, rng)
    ok = out["near"]["p"] < ALPHA and out["none"]["p"] >= ALPHA
    return out, bool(ok)


# ============================================================ real data
def load_real():
    import vparse
    import boxes
    from scoreboard.metrics_new import SlotSegmenter
    import s76_segmenter_independence as S76

    recs = vparse.load()
    pages, _stats = boxes.align_all(recs)
    label_pages = {r["page"] for r in recs if r["unit"].startswith("L")}
    train = [w for r in recs if r["unit"].startswith("P") and r["page"] not in label_pages
             for w in r["words"] if w and "?" not in w]
    slot = SlotSegmenter(train)
    zat = S76.ZatteraSegmenter(und="whole", tokens=train)
    seg = {"slot": lambda w: slot.segment(w), "zat": lambda w: zat.segment(w)}
    top = {}
    for k, f in seg.items():
        cnt = Counter(f(w)[1] for w in train if f(w)[1])
        top[k] = {c for c, _ in cnt.most_common(TOP_K)}
        top[k + "_broad"] = {c for c, _ in cnt.most_common(TOP_K_BROAD)}
    sub_cache = {}

    def sub_share(key):
        if key not in sub_cache:
            sub_cache[key] = sum(key in w for w in train) / len(train)
        return sub_cache[key]

    box_files = sorted({str((boxes.BOX_DIR / f"{f}.js").resolve()) for f in pages})
    return recs, pages, seg, top, sub_share, len(train), box_files


def page_struct(pairs):
    body, labels, order = [], [], []
    all_tok = [t for _, l in pairs for t in l["tokens"]]
    for i, (r, l) in enumerate(pairs):
        words = [w for w in r["words"] if w and "?" not in w]
        if r["unit"].startswith("P") and l["tokens"] and l["n_matched"] >= 1:
            body.append(dict(idx=i, words=words, pts=np.array([[t["cx"], t["cy"]] for t in l["tokens"]]),
                             toks=l["tokens"]))
        elif r["unit"].startswith("L") and l["tokens"]:
            m = [t for t in l["tokens"] if t["matched"]]
            if m and words:
                labels.append(dict(idx=i, line=r["line"], unit=r["unit"], words=words,
                                   x=float(np.mean([t["cx"] for t in m])), y=float(np.mean([t["cy"] for t in m]))))
    if not all_tok:
        return None
    ext = (min(t["cx"] - t["w"] / 2 for t in all_tok), max(t["cx"] + t["w"] / 2 for t in all_tok),
           min(t["cy"] - t["h"] / 2 for t in all_tok), max(t["cy"] + t["h"] / 2 for t in all_tok))
    return dict(body=body, labels=labels, ext=ext)


def inside_body_box(lab, body):
    for b in body:
        for t in b["toks"]:
            if abs(lab["x"] - t["cx"]) <= t["w"] / 2 and abs(lab["y"] - t["cy"]) <= t["h"] / 2:
                return True
    return False


def distances(x, y, body):
    return np.array([float(np.min(np.hypot(b["pts"][:, 0] - x, b["pts"][:, 1] - y))) for b in body])


def build_events(recs, pages, seg, top, sub_share, rng):
    illus = {r["page"]: r["illus"] for r in recs}
    P = {}
    dropped_guard = 0
    for page, pairs in pages.items():
        st = page_struct(pairs)
        if st is None or len(st["body"]) < MIN_BODY_LINES or not st["labels"]:
            continue
        keep_labels = []
        for lab in st["labels"]:
            if inside_body_box(lab, st["body"]):
                dropped_guard += 1
            else:
                keep_labels.append(lab)
        st["labels"] = keep_labels
        if keep_labels:
            P[page] = st
    ch = defaultdict(list)
    rows = []
    slot = seg["slot"]
    for page, st in sorted(P.items()):
        body = st["body"]
        n = len(body)
        bcore = {k: [{seg[k](w)[1] for w in b["words"]} for b in body] for k in seg}
        bframe = [{(slot(w)[0], slot(w)[2]) for w in b["words"]} for b in body]
        for lab in st["labels"]:
            D = distances(lab["x"], lab["y"], body)
            full = np.ones(n, bool)
            # reading-order neighbours: P line immediately before / after the label in file order
            before = [j for j, b in enumerate(body) if b["idx"] < lab["idx"]]
            after = [j for j, b in enumerate(body) if b["idx"] > lab["idx"]]
            adj = set(([before[-1]] if before else []) + ([after[0]] if after else []))
            noadj = np.array([j not in adj for j in range(n)])

            def add(chan, key, match, keep=full):
                k = int(match[keep].sum())
                if 1 <= k <= int(keep.sum()) - 1:
                    ev = dict(page=page, D=D, match=match, keep=keep, key=key, label=f"{page}.{lab['line']}",
                              adj=adj, lab=lab)
                    ch[chan].append(ev)
                    return ev
                return None

            seen = defaultdict(set)
            for w in lab["words"]:
                for k in seg:
                    c = seg[k](w)[1]
                    if not c or c in seen[k]:
                        continue
                    seen[k].add(c)
                    m = np.array([c in bc for bc in bcore[k]])
                    if c not in top[k + "_broad"]:
                        add(f"core_{k}_k{TOP_K_BROAD}", c, m)
                    if c not in top[k]:
                        ev = add(f"core_{k}", c, m)
                        if k == "slot":
                            add("core_slot_noadj", c, m, noadj)
                            if ev is not None:
                                near = int(np.argmin(np.where(m, D, np.inf)))
                                rows.append(dict(page=page, label=ev["label"], unit=lab["unit"], word=w, core=c,
                                                 illus=illus[page], n_lines=n, k=int(m.sum()),
                                                 M=event_M(D, m, full), nearest_match_is_adjacent=near in adj,
                                                 nearest_line_is_adjacent=int(np.argmin(D)) in adj))
                    elif k == "slot":
                        add("common_core", c, m)
                pre, _c, suf = slot(w)
                if (pre or suf) and (pre, suf) not in seen["frame"]:
                    seen["frame"].add((pre, suf))
                    add("frame", f"{pre}|{suf}", np.array([(pre, suf) in bf for bf in bframe]))
                if len(w) >= 5:
                    key = w[1:-1]
                    if key not in seen["trim"] and sub_share(key) < RARE_SUB_SHARE:
                        seen["trim"].add(key)
                        add("trim", key, np.array([any(key in x for x in b["words"]) for b in body]))
    # moved-label control: one random other eligible page of the same illustration class
    for ev in ch["core_slot"]:
        page, lab, c = ev["page"], ev["lab"], ev["key"]
        x0, x1, y0, y1 = P[page]["ext"]
        nx, ny = (lab["x"] - x0) / (x1 - x0), (lab["y"] - y0) / (y1 - y0)
        cands = []
        for q, st in sorted(P.items()):
            if q == page or illus[q] != illus[page]:
                continue
            m = np.array([c in {seg["slot"](w)[1] for w in b["words"]} for b in st["body"]])
            if 1 <= m.sum() <= len(m) - 1:
                cands.append((q, m))
        if not cands:
            continue
        q, m = cands[rng.integers(len(cands))]
        qx0, qx1, qy0, qy1 = P[q]["ext"]
        D = distances(qx0 + nx * (qx1 - qx0), qy0 + ny * (qy1 - qy0), P[q]["body"])
        ch["moved"].append(dict(page=q, D=D, match=m, keep=np.ones(len(m), bool), key=c, label=ev["label"]))
    return ch, rows, dropped_guard, len(P), sum(len(st["labels"]) for st in P.values())


# ============================================================ stub
def local_inputs(box_files):
    mods = set()
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
            mods.add(rel.as_posix())
    mods.add(SELF.name)
    data = {"data/ZL3b-n.txt"} | {Path(b).resolve().relative_to(ROOT).as_posix() for b in box_files}
    return sorted(mods), sorted(data)


def stub_match(required):
    if not STUB.exists():
        return False, "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    missing = [f for f in required if f not in want]
    ok = bool(want) and not bad and not missing
    return ok, f"bad={bad[:5]} missing={missing[:5]}"


# ============================================================ main
def main():
    t0 = time.time()
    free = below_normal_and_ram()
    emit("S99 - label rare core vs physically nearest body lines (Phase 6.3, E1)")
    emit(f"started {clock()}  priority=BelowNormal workers=1  free_RAM_GB={free:.2f}")
    if free == free and free < MIN_FREE_GB:
        emit(f"ABORT: free RAM {free:.2f} GB < {MIN_FREE_GB}")
        flush()
        sys.exit(2)
    emit(f"thresholds: TOP_K={TOP_K} TOP_K_BROAD={TOP_K_BROAD} RARE_SUB_SHARE={RARE_SUB_SHARE} MIN_BODY_LINES={MIN_BODY_LINES} "
         f"N_PERM={N_PERM} ALPHA={ALPHA} NEG_MDE_MAX={NEG_MDE_MAX} SEED={SEED}")
    if PLANTED:
        fx, ok = run_fixture(2000)
        for s in fx.values():
            emit(fmt(s))
        emit(f"FIXTURE_PASS={ok}")
        emit(f"finished {clock()} runtime_s={time.time() - t0:.1f}")
        flush()
        return
    if LIST_INPUTS:
        _r, _p, _s, _t, _ss, _n, box_files = load_real()
        mods, data = local_inputs(box_files)
        print("\n".join(mods + data))
        return
    recs, pages, seg, top, sub_share, n_train, box_files = load_real()
    mods, data = local_inputs(box_files)
    ok, why = stub_match(mods + data)
    emit(f"stub_match={ok} ({len(mods)} modules, {len(data)} data files) {'' if ok else why}")
    if not ok:
        emit("REFUSED: stub does not verify; no real scoring.")
        flush()
        sys.exit(3)
    fx, fx_ok = run_fixture(2000)
    for s in fx.values():
        emit(fmt(s))
    emit(f"CALL_FIXTURE={fx_ok}")
    rng = np.random.default_rng(SEED)
    ch, rows, dropped, n_pages, n_labels = build_events(recs, pages, seg, top, sub_share, rng)
    emit(f"data: train_tokens={n_train} eligible_pages={n_pages} labels={n_labels} "
         f"labels_dropped_by_box_guard={dropped}")
    res = {}
    for i, name in enumerate(("core_slot", "core_zat", "trim", "frame", "common_core", "moved", "core_slot_noadj",
                              f"core_slot_k{TOP_K_BROAD}", f"core_zat_k{TOP_K_BROAD}")):
        res[name] = summarize(name, ch[name], N_PERM, np.random.default_rng(SEED + 10 + i))
        emit(fmt(res[name]))
    n_adj_near = sum(r["nearest_match_is_adjacent"] for r in rows)
    n_adj_line = sum(r["nearest_line_is_adjacent"] for r in rows)
    emit(f"recency: primary events whose nearest MATCHING line is a reading-order neighbour = {n_adj_near}/{len(rows)}; "
         f"whose nearest line overall is a neighbour = {n_adj_line}/{len(rows)}")
    pr, se, fr, cc = res["core_slot"], res["core_zat"], res["frame"], res["common_core"]
    c_primary = bool(pr["p"] < ALPHA)
    c_second = bool(se["T"] < 0.5)
    c_controls = bool(fr["p"] >= ALPHA and cc["p"] >= ALPHA)
    emit(f"CALL_PRIMARY={c_primary}  (p={pr['p']:.4f} < {ALPHA})")
    emit(f"CALL_SECOND={c_second}  (T_zat={se['T']:.4f} < 0.5)")
    emit(f"CALL_CONTROLS={c_controls}  (p_frame={fr['p']:.4f}, p_common={cc['p']:.4f}, both >= {ALPHA})")
    emit(f"POWER: MDE(core_slot) = {pr['mde']:.4f} shift in mean normalized rank at n={pr['n']} events / "
         f"{pr['pages']} pages (one-sided alpha {ALPHA}, power 0.8); NEG_MDE_MAX={NEG_MDE_MAX}")
    if not fx_ok:
        verdict = "INCONCLUSIVE (fixture failed)"
    elif c_primary and c_second and c_controls:
        verdict = "POSITIVE"
    elif not c_controls:
        verdict = "INCONCLUSIVE (controls not null)"
    elif c_primary:
        verdict = "INCONCLUSIVE (segmenter-dependent)"
    elif pr["mde"] <= NEG_MDE_MAX:
        verdict = "NEGATIVE"
    else:
        verdict = "INCONCLUSIVE (underpowered)"
    emit(f"VERDICT={verdict}")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    if rows:
        with (RUN_DIR / "events_core_slot.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    (RUN_DIR / "summary.json").write_text(json.dumps(dict(fixture=fx, fixture_pass=fx_ok, channels=res,
                                                          calls=dict(CALL_PRIMARY=c_primary, CALL_SECOND=c_second,
                                                                     CALL_CONTROLS=c_controls,
                                                                     CALL_FIXTURE=fx_ok),
                                                          verdict=verdict), indent=2), encoding="utf-8")
    emit(f"sidecars: runs/s99/events_core_slot.csv, runs/s99/summary.json")
    emit(f"finished {clock()} runtime_s={time.time() - t0:.1f}")
    flush()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        emit(f"FAILED: {type(exc).__name__}: {exc}")
        emit("AMENDMENT OK: rerun under results_s99_amend1.txt")
        flush()
        raise
