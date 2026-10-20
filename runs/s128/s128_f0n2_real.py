#!/usr/bin/env python3
"""s128 F0-N2-REAL (prereg v4 step d1): the DECIDING known-answer check for N2 at real Voynich herbal layout.
Reads only the count list (page ids, $Q/$B/$H/$L, per-line token counts, paragraph-start flags) and the Egerton calibration chapters.
It opens no Voynich transliteration. Before anything else it checks, against the stub, the sha256 of this script,
runs/s128/s128_herbal_profile.py, the Ventura TEI and the count list; any missing entry or mismatch -> exit 2.
Usage, from the project root (after step d0 appended the count-list hash to the stub):
  python -I runs/s128/s128_f0n2_real.py runs/s128/s128_name_slot_prediction_v4.prereg.sha256 runs/s128/s128_layout_counts_ZL3b.tsv runs/s128/results_s128_f0n2_real_<YYYYMMDDTHHMMSS>.txt
Exit: 0 PASS; 1 FAIL (s128 stops before any Voynich text is read); 2 usage or hash error.
Seeds 20261046..20261060. 200 draws per null; q99 = sorted index 197. Failed seed = NAME miss and RARITY fire.
A seed fails if the edition runs out before every page is filled, or if more than 50% of the chapters examined were too short."""
import sys, hashlib, random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = "runs/s128/s128_f0n2_real.py"
PROFILE = "runs/s128/s128_herbal_profile.py"
TEI = "data/external/ventura_egerton747/tractatus-de-herbis-egerton-747-ventura2009-tei.xml"
SEEDS = list(range(20261046, 20261061))
DRAWS = 200
Q99 = 197

def sha(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()

def read_stub(stub):
    d = {}
    for ln in (ROOT / stub).read_text(encoding="utf-8").replace("\r", "").split("\n"):
        if ln and not ln.startswith("#") and "  " in ln:
            h, p = ln.split("  ", 1); d[p] = h
    return d

def read_counts(path):
    pages = []
    for ln in (ROOT / path).read_text(encoding="ascii").split("\n"):
        if not ln or ln.startswith("#") or ln.startswith("page\t"): continue
        pg, Q, B, H, L, c, f = ln.split("\t")
        pages.append(dict(page=pg, Q=Q, B=B, H=H, L=L, lens=[int(x) for x in c.split(",")], flags=[int(x) for x in f.split(",")]))
    return pages

def strata(pages):
    """N2 strata: (Q, (Q,B), H, L); pages with H or L '?' held in place (no stratum).
    If > 25% of stratified pages are alone, those pages are re-stratified by (Q, H, L)."""
    key = {}
    for i, p in enumerate(pages):
        if p["H"] == "?" or p["L"] == "?": continue
        key[i] = (p["Q"], p["B"], p["H"], p["L"])
    groups = defaultdict(list)
    for i, k in key.items(): groups[k].append(i)
    single = [g[0] for g in groups.values() if len(g) == 1]
    widened = 0
    if key and len(single) > 0.25 * len(pages):
        for i in single:
            p = pages[i]; key[i] = ("W", p["Q"], p["H"], p["L"]); widened += 1
        groups = defaultdict(list)
        for i, k in key.items(): groups[k].append(i)
    held = [i for i in range(len(pages)) if i not in key]
    order = sorted(groups.values(), key=lambda g: min(g))
    return order, held, widened

def slots(p):
    """Per page: lists of token positions for paragraph-initial, line-initial, other; and the line-1 end position."""
    pi, li, ot, pos = [], [], [], 0
    for n, f in zip(p["lens"], p["flags"]):
        (pi if f else li).append(pos); ot.extend(range(pos + 1, pos + n)); pos += n
    return pi, li, ot, p["lens"][0]

def S(pages_tok, layout, langs):
    tot = defaultdict(Counter)
    for tk, L in zip(pages_tok, langs): tot[L].update(tk)
    hit = 0
    for tk, (_, _, _, l1), L in zip(pages_tok, layout, langs):
        cnt = Counter(tk)
        Q = [w for w, k in cnt.items() if k >= 2 and k / tot[L][w] >= 0.9]
        if Q and min(tk.index(w) for w in Q) < l1: hit += 1
    return hit / len(pages_tok)

def n2(pages_tok, layout, groups, rng):
    out = [tk[:] for tk in pages_tok]
    for g in groups:
        slot = [(i, j) for i in g for j in layout[i][0]]
        vals = [out[i][j] for i, j in slot]; rng.shuffle(vals)
        for (i, j), v in zip(slot, vals): out[i][j] = v
    for tk, (pi, li, ot, _) in zip(out, layout):
        for cls in (li, ot):
            vals = [tk[j] for j in cls]; rng.shuffle(vals)
            for j, v in zip(cls, vals): tk[j] = v
    return out

def n1(pages_tok, rng):
    out = []
    for tk in pages_tok: t = tk[:]; rng.shuffle(t); out.append(t)
    return out

def run(stub, counts, outp):
    d = read_stub(stub); bad = []
    for p in (SELF, PROFILE, TEI, counts):
        if p not in d: bad.append(p + " NOT_IN_STUB")
        elif sha(p) != d[p]: bad.append(p + " HASH_MISMATCH")
    if bad:
        for b in bad: print("HASH_CHECK_FAIL", b)
        return 2
    sys.path.insert(0, str(ROOT / "runs" / "s128"))
    import s128_herbal_profile as prof
    # Egerton chapters parsed with the calibration loader's rules (s128_herbal_profile.load_egerton), from the hashed TEI path
    E = load_egerton_from_text(prof, (ROOT / TEI).read_text(encoding="utf-8"))
    pages = read_counts(counts)
    layout = [slots(p) for p in pages]
    langs = [p["L"] for p in pages]
    groups, held, widened = strata(pages)
    log = [f"# s128 F0-N2-REAL; count list {counts} sha256 {sha(counts)}; pages {len(pages)}; strata {len(groups)}; "
           f"held_in_place {len(held)}; widened {widened}; Egerton chapters {len(E)}"]
    res = {"NAME": 0, "RARITY": 0}
    for seed in SEEDS:
        rng = random.Random(seed)
        start = rng.randrange(len(E))
        order = [i for g in groups for i in g] + held     # strata in order of first page, then held pages in count-list order
        order_set = set(order)
        assert len(order_set) == len(pages)
        assign, k, examined, skipped, failed = {}, start, 0, 0, False
        for i in order:
            need = sum(pages[i]["lens"])
            while True:
                if examined >= len(E): failed = True; break
                ch = E[k % len(E)]; k += 1; examined += 1
                if len(ch["tk"]) >= need: assign[i] = ch; break
                skipped += 1
            if failed: break
        if not failed and skipped > 0.50 * examined: failed = True   # v4 rule: > 50% short skips fails the seed
        if failed:
            log.append(f"seed {seed} FAILED_SEED examined {examined} short_skip {skipped} -> NAME miss, RARITY fire")
            res["RARITY"] += 1
            continue
        arms = {}
        for arm in ("NAME", "RARITY"):
            P = []
            for i in range(len(pages)):
                ch = assign[i]; need = sum(pages[i]["lens"])
                tk = ch["tk"]
                if arm == "RARITY":
                    tk = ["et" if t.startswith(ch["stem"]) else t for t in tk]
                tk = tk[:need]
                if arm == "RARITY":
                    tk = tk[:]; tk[layout[i][0][0]] = f"RARE_{seed}_{i}"
                P.append(tk)
            o = S(P, layout, langs)
            q2 = sorted(S(n2(P, layout, groups, rng), layout, langs) for _ in range(DRAWS))[Q99]
            q1 = sorted(S(n1(P, rng), layout, langs) for _ in range(DRAWS))[Q99]
            fire = o > q2; res[arm] += fire; arms[arm] = (o, q1, q2, fire)
        log.append(f"seed {seed} start {start} examined {examined} short_skip {skipped} " +
                   " ".join(f"{a}: S {v[0]:.3f} N1q99 {v[1]:.3f} N2q99 {v[2]:.3f} fire {int(v[3])}" for a, v in arms.items()))
    ok = res["NAME"] >= 10 and res["RARITY"] <= 5
    log.append(f"NAME fires {res['NAME']}/15 (need >= 10); RARITY fires {res['RARITY']}/15 (need <= 5)")
    log.append(f"CALL_F0N2_REAL {'PASS' if ok else 'FAIL'}")
    (ROOT / outp).write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))
    return 0 if ok else 1

def load_egerton_from_text(prof, t):
    import re
    body = t[t.find('<body'):]
    out = []
    for m in re.finditer(r'<div2[^>]*>(.*?)</div2>', body, re.S):
        blk = m.group(1)
        h = re.search(r'<head>(.*?)</head>', blk, re.S)
        if not h: continue
        head = re.sub(r'<[^>]+>', ' ', h.group(1)).strip()
        if head.upper().startswith(('PROLOG', 'EXPLICIT', 'COLOPHON')) or not re.match(r'\s*\d+\.', head): continue
        txt = re.sub(r'<head>.*?</head>', ' ', blk, flags=re.S)
        txt = re.sub(r'<[^>]+>', ' ', txt).replace('&lt;', '').replace('&gt;', '')
        nw = [w for w in prof.toks(head) if w not in prof.STOP_HEAD]
        tk = prof.toks(txt)
        if not nw or len(tk) < 5: continue
        out.append(dict(tk=tk, stem=prof.stem_of(prof.key_name(nw))))
    return out

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__); sys.exit(2)
    sys.exit(run(*sys.argv[1:]))
