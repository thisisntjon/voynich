"""G control 1: the REAL Timm & Schinner self-citation generator (Java), run as-is.

Source: data/external/timm-schinner-generator/SelfCitationTextgenerator-main/
        SelfCitationTextgenerator-master/executable/text-generator.jar (MIT, Torsten Timm,
        Zenodo 10.5281/zenodo.2531632; companion to Timm & Schinner, Cryptologia 2020).
Runtime: portable Eclipse Temurin 21 JRE unpacked to data/external/jre/ (not installed,
        NOTE 2026-10-17 18:10: the JRE was deleted after the outputs were filed; re-download
        per data/external/README.md 'Pruned' section before rerunning.
        not on PATH; java.exe called by absolute path). The jar runs under Java 21 unchanged.

What is run: the generator with its shipped conf.properties, ONE change:
    text.lines_to_create = 1200 -> 4800   (to get >= 40k tokens; 1200 lines ~ 10.9k tokens)
Every other parameter is the shipped default (PROPERTIES.md of the repo):
    text.max_line_length=55, text.min_line_length=15 (last line of a paragraph),
    text.lines_per_page=29, text.max_repeat_count=3,
    text.initial_line = "pchal shal shorchdy okeor okain shedy pchedy qotchedy qotar ol lkar" (f103v.P.9),
    method.random=pseudo, method.random.pseudo.seed=19,
    method.canFollow=curveline, method.canFollow.error_rate=0,
    method.sourceChooser=page, method.sourceChooser.same_position_probability=28,
    method.morph=slim, add_remove=20, combine_split=30, replace=50, reuse_last=10,
    combined.dismiss_as_source_probability=30, use_word_final_substitutions=true,
    method.suggestions=top, probability=40, iType/olType/dyType min % = 20/25/25,
    save.gephi.nodes=false.
Line / paragraph / page structure is not optional in this generator: it always writes
lines of <= max_line_length characters, closes a paragraph with a shortened line
(probability rises with the paragraph's line count, SelfCitationTextGenerator.generateText),
and starts a new page every lines_per_page lines; the output file carries no explicit
paragraph or page markers (paragraph ends are only visible as short lines).

Outputs (data/controls_synthetic/):
    timm_schinner.java_output.txt    raw generator output (header comments + 4800 lines)
    timm_schinner.conf.properties    the exact conf used
    timm_schinner.txt / .meta.json   tokens poured, in order, into the Voynich page/line shape
    timm_schinner_ownlines.meta.json the generator's own lines, 29 per page (its page rule),
                                     section "TS" / hand "TS" (no real labels exist)
Run:  python ctl_timm_schinner.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import ctl_common as cc

ROOT = Path(__file__).parent
GEN = ROOT / "data/external/timm-schinner-generator/SelfCitationTextgenerator-main/SelfCitationTextgenerator-master/executable"
JAVA = ROOT / "data/external/jre/jdk-21.0.12.1+1-jre/bin/java.exe"
LINES = 4800
LINES_PER_PAGE = 29


def run_generator(run_dir):
    run_dir = Path(run_dir)
    (run_dir / "generate").mkdir(parents=True, exist_ok=True)
    shutil.copy(GEN / "text-generator.jar", run_dir / "text-generator.jar")
    conf = (GEN / "conf.properties").read_text(encoding="utf-8")
    assert "text.lines_to_create=1200\n" in conf
    conf = conf.replace("text.lines_to_create=1200\n", f"text.lines_to_create={LINES}\n")
    (run_dir / "conf.properties").write_text(conf, encoding="utf-8")
    r = subprocess.run([str(JAVA), "-jar", "text-generator.jar"], cwd=run_dir,
                       capture_output=True, text=True, timeout=600)
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr)
        raise SystemExit("java failed")
    return (run_dir / "generate" / "generated_text.txt").read_text(encoding="utf-8"), conf


def main():
    with tempfile.TemporaryDirectory() as d:
        raw, conf = run_generator(d)
    (cc.OUT / "timm_schinner.java_output.txt").write_text(raw, encoding="utf-8")
    (cc.OUT / "timm_schinner.conf.properties").write_text(conf, encoding="utf-8")
    lines = [l.split() for l in raw.splitlines() if l.strip() and not l.startswith("#")]
    tokens = [w for l in lines for w in l]
    print(f"generator: {len(lines)} lines, {len(tokens)} tokens, {len(set(tokens))} types")
    note = (f"Timm & Schinner Java generator text-generator.jar, shipped conf.properties with "
            f"text.lines_to_create={LINES} (only change); tokens poured in order into the ZL3b "
            f"paragraph page/line shape; generator ran under Temurin 21 JRE")
    pages = cc.pour(tokens)
    cc.write_control("timm_schinner", pages, note=note, source="real Java run", seed=19)
    own = [dict(id=f"ts{i // LINES_PER_PAGE + 1:04d}", section="TS", hand="TS",
                lines=lines[i:i + LINES_PER_PAGE]) for i in range(0, len(lines), LINES_PER_PAGE)]
    import json
    (cc.OUT / "timm_schinner_ownlines.meta.json").write_text(
        json.dumps(dict(name="timm_schinner_ownlines", note=note + "; generator's own lines, 29 per page",
                        pages=own)), encoding="utf-8")
    print(cc.stats_row("timm_schinner", cc.ctl_stats(pages)))
    print(cc.stats_row("ts_ownlines", cc.ctl_stats(own)))


if __name__ == "__main__":
    main()
