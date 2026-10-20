"""P2 (Top-10 #10): frozen scoreboard across transliterations.
Scores paragraph text of ZL3b (team primary), RF1b-e, IT2a-n, GC2a-n with
scoreboard/score.py v1 unchanged. Reports per-metric ranges; a headline
metric is ROBUST if its cross-transliteration range stays inside the
PREREG band margin that separates Voynich from controls/nulls.
Run: uv run python p2_robustness.py -> results_p2.txt + scoreboard/robustness_p2.json
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parent
spec = importlib.util.spec_from_file_location("score", ROOT / "scoreboard" / "score.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

import vparse  # noqa: E402

FILES = {
    "ZL3b": ROOT / "data" / "ZL3b-n.txt",
    "RF1b-e": ROOT / "data" / "external" / "voynich-nu-ivtff" / "RF1b-e.txt",
    "IT2a-n": ROOT / "data" / "external" / "voynich-nu-ivtff" / "IT2a-n.txt",
    "GC2a-n": ROOT / "data" / "external" / "voynich-nu-ivtff" / "GC2a-n.txt",
}
KEYS = ["tokens", "types", "hapax_rate", "mean_len", "sd_len", "h1", "h2", "zipf",
        "redup_pct", "jsd_first_fg", "jsd_last_lg", "p_init_enrich",
        "m_final_enrich", "cross_mi_eva", "cross_excess_eva", "recur_le_100"]
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def main():
    rows = {}
    for name, path in FILES.items():
        recs = vparse.load(path=path)
        para = vparse.paragraph_text(recs)
        lines = [[w for w in r["words"] if "?" not in w] for r in para]
        lines = [l for l in lines if l]
        words = [w for l in lines for w in l]
        rows[name] = score.score_corpus(name, words, lines)
        r = rows[name]
        emit(f"{name:8} tok={len(words)} h2={r['h2']:.3f} sd={r['sd_len']:.2f} "
             f"JSDf={r['jsd_first_fg']:.4f} p=x{r['p_init_enrich']} m=x{r['m_final_enrich']} "
             f"excess={r['cross_excess_eva']:+.4f} redup={r['redup_pct']}% hapax={r['hapax_rate']}")
    emit("\nRanges across transcriptions (min..max):")
    ranges = {}
    for k in KEYS:
        vals = [rows[n][k] for n in FILES]
        ranges[k] = [min(vals), max(vals)]
        emit(f"  {k:18} {min(vals)} .. {max(vals)}")
    out = {"files": {k: str(v.relative_to(ROOT)) for k, v in FILES.items()},
           "rows": rows, "ranges": ranges}
    (ROOT / "scoreboard" / "robustness_p2.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    (ROOT / "results_p2.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    emit("Wrote results_p2.txt + scoreboard/robustness_p2.json")


if __name__ == "__main__":
    main()
