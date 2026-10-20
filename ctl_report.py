"""Comparison table for the three G controls (PLAN Phase 0 item 4, generators) ->
results_ctl_generators.txt. Reads the sidecars written by ctl_timm_schinner.py,
ctl_schwartz.py and ctl_c2_best.py and scores them with ctl_common.ctl_stats beside
the real ZL3b paragraph text measured identically, and the filed Voynich targets
(a1: h2 2.13, SD 1.76; b4: repeat 0.90 %, p-init x16, m-final x16.6).
Run:  python ctl_report.py
"""
import json
import subprocess
from pathlib import Path

import ctl_common as cc

NAMES = ["timm_schinner", "timm_schinner_ownlines", "schwartz_reuse", "c2_best"]


def main():
    stamp = subprocess.run(["date", "+%Y-%m-%d %H:%M %Z"], capture_output=True, text=True).stdout.strip()
    lines = [f"G controls (generated text) vs Voynich ZL3b paragraph text; written {stamp} by ctl_report.py",
             "h2 = char conditional entropy with space as a symbol (a1_profile.char_entropies); len = word length mean+-SD;",
             "repeat = immediate exact repeat rate; p-init / m-final = b4_selfcite_sim.enrich on lines 2+ of each page",
             "(all-lines values in parentheses). Filed Voynich targets: h2 2.13 (a1, 25k sample), SD 1.76, repeat 0.90%, p-init x16, m-final x16.6.",
             ""]
    rows = [("VOYNICH (ZL3b para)", cc.voynich_pages())]
    for n in NAMES:
        p = cc.OUT / f"{n}.meta.json"
        if p.exists():
            rows.append((n, json.loads(p.read_text(encoding="utf-8"))["pages"]))
    for name, pages in rows:
        lines.append(cc.stats_row(name, cc.ctl_stats(pages)))
    lines += ["",
              "provenance: timm_schinner = REAL Java run of Timm & Schinner's text-generator.jar (Temurin 21 JRE, shipped",
              "  conf.properties, lines_to_create 1200->4800, seed 19), tokens poured into the Voynich page/line shape;",
              "  timm_schinner_ownlines = the same run in the generator's own 29-line pages (its line-edge habits survive only here);",
              "schwartz_reuse = Python re-implementation (ctl_schwartz.py, seed 20261017) of Schwartz 2026 §5.2, parameters in",
              "  its docstring and sidecar 'fit'; c2_best = c2_section_generator at the minimax-deviation setting (ctl_c2_best.py)."]
    sc = cc.OUT / "c2_best.meta.json"
    if sc.exists():
        d = json.loads(sc.read_text(encoding="utf-8"))
        lines.append(f"  c2_best setting: {d['setting']} kwargs={d['kwargs']}")
    sw = cc.OUT / "schwartz_reuse.meta.json"
    if sw.exists():
        d = json.loads(sw.read_text(encoding="utf-8"))
        for h, f in sorted(d["fit"].items()):
            lines.append(f"  schwartz hand {h}: shares={f['shares']} w_init={f['w_init']:.3f} w_final={f['w_final']:.3f} "
                         f"lag1={f['lag1_target']:+.3f} beta={f['beta']:.3f} vocab={f['vocab_types']} types/{f['vocab_tokens']} tokens")
    out = Path(__file__).parent / "results_ctl_generators.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
