"""Sample-size floors for the seven v1 bands: page-cluster bootstrap of Voynich at token
budgets n; 95% interval width vs band width. Uses scoreboard/score.py functions unchanged
(edge null nrep reduced to 5 per bootstrap draw for runtime). Also: Currier A pages only,
and 41-page random subsets (the g1/l1 held-out size) with no replacement.
Run: python -I workflow/research/C-helpers/floors_v1_bands.py"""
import sys, time, random, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import numpy as np
import corpora
spec = importlib.util.spec_from_file_location("score_v1", ROOT / "scoreboard" / "score.py")
sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)

BANDS = {"h2": (1.98, 2.28), "sd_len": (1.41, 2.11), "redup_pct": (0.4, 1.8), "jsd_first_fg": (0.10, None),
         "p_init_enrich": (8.0, None), "m_final_enrich": (8.0, None), "cross_excess_eva": (0.09, None)}
recs = corpora.voynich_lines()
by = {}
for r in recs: by.setdefault(r["page"], []).append(r["words"])
pages = list(by)
A_pages = [p for p in pages if any(r["page"] == p and r["lang"] == "A" for r in recs)]
ntok = {p: sum(len(ws) for ws in by[p]) for p in pages}

def metrics(lines):
    words = [w for ws in lines for w in ws]
    out = sc.profile_metrics(words); out.update(sc.line_metrics(lines))
    out["cross_excess_eva"] = sc.edge_metrics(lines, lambda w: w, nrep=5)["excess"]
    return out

def draw(pool, n, rng, replace=True):
    lines, tot = [], 0
    order = rng.choices(pool, k=10 * len(pool)) if replace else rng.sample(pool, len(pool))
    for p in order:
        for ws in by[p]:
            lines.append(ws); tot += len(ws)
            if tot >= n: return lines
    return lines

def summarise(label, draws):
    print(f"[{label}] draws={len(draws)}")
    for k, (lo, hi) in BANDS.items():
        v = np.array([d[k] for d in draws]); q = np.percentile(v, [2.5, 97.5]); w = q[1] - q[0]
        full = FULL[k]
        if hi is not None:
            bw = hi - lo; verdict = "readable" if w < bw else "UNREADABLE"
            print(f"  {k:17} 95% [{q[0]:8.4f},{q[1]:8.4f}] width {w:.4f} vs band width {bw:.3f} -> {verdict}; share of draws outside band {np.mean((v<lo)|(v>hi)):.2f}")
        else:
            verdict = "readable" if q[0] > lo else "UNREADABLE"
            print(f"  {k:17} 95% [{q[0]:8.4f},{q[1]:8.4f}] width {w:.4f} vs gap to floor {full-lo:.3f} -> {verdict}; share of draws below floor {np.mean(v<lo):.2f}")

t0 = time.time()
FULL = metrics([ws for p in pages for ws in by[p]])
print("full Voynich:", {k: FULL[k] for k in BANDS})
NB = int(sys.argv[1]) if len(sys.argv) > 1 else 60
for n in [2000, 5000, 8600, 11231, 17000, 25000, 34857]:
    rng = random.Random(n)
    summarise(f"all pages, page bootstrap to n={n} tokens", [metrics(draw(pages, n, rng)) for _ in range(NB)])
    print(f"  t={time.time()-t0:.0f}s")
rng = random.Random(7)
summarise(f"Currier A pages only ({len(A_pages)} pages, {sum(ntok[p] for p in A_pages)} tokens), page bootstrap", [metrics(draw(A_pages, 10**9, rng)) for _ in range(NB)])
rng = random.Random(41)
sub = []
for _ in range(NB):
    pick = rng.sample(pages, 41); sub.append(metrics([ws for p in pick for ws in by[p]]))
print("41-page subsets: mean tokens", np.mean([d["tokens"] for d in sub]))
summarise("41 random pages, no replacement (g1/l1 held-out size)", sub)
print(f"t={time.time()-t0:.0f}s")
