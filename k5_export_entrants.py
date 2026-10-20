"""K5: export K-series producers as scoreboard entrants.

Writes data/controls_synthetic/<name>.meta.json in the format of
scoreboard/corpus.py (pages with id/section/hand/lang/quire/lines, extra keys
kept: para_start per line). Producers are regenerated with the same seeds and
constants as k1/k2 (deterministic), so the files match results_k1/k2 rows.
  flow_cipher_layer   K1 letter cipher (F3 flow) + M5 layer        (no family range)
  flow_gen_layer      K1 flow generator + layer, seed 1            (no family range)
  nomen_k2_x2         K2 homophonic nomenclator x2                 (C range by name)
  nomen_k2_x8         K2 homophonic nomenclator x8                 (C range by name)
Run: python k5_export_entrants.py
"""
import json
import random
from pathlib import Path

import c2_section_generator as c2
import f3_flow_choice as f3
import k1_joint_producer as k1
import k2_nomenclator as k2

DEST = Path(__file__).parent / "data" / "controls_synthetic"


def dump(name, by, note):
    pages = []
    for page, recs in by.items():
        r0 = recs[0]
        pages.append(dict(id=page, section=r0["illus"], hand=r0["hand"], lang=r0["lang"], quire=r0["quire"],
                          illus=r0["illus"], para_start=[bool(r.get("para_start")) for r in recs],
                          lines=[list(r["words"]) for r in recs]))
    path = DEST / f"{name}.meta.json"
    path.write_text(json.dumps(dict(name=name, tokenization="eva", source=note, pages=pages)), encoding="utf-8")
    print(f"{path.name}: {len(pages)} pages, {sum(len(l) for p in pages for l in p['lines'])} tokens")


def main():
    by = k1.layout()
    R = f3.ratio_table(by)
    Qi, Qe, para = k1.line_tables(by)
    seq, tab = f3.naibbe_chunks()
    it = iter([c for c, _ in seq])
    dump("flow_cipher_layer", k1.cipher_pages(by, lambda r: next(it, None), tab, R, Qi, Qe, para, True, 1),
         "k1 CIPHER +layer: Naibbe tables (Zenodo 17219445), flow beta 1.5, M5 layer; tables measured on Voynich")
    g = c2.Gen(by)
    dump("flow_gen_layer", k1.gen_pages(g, R, Qi, Qe, para, True, 1),
         "k1 GEN +layer s1: c2 section generator, flow beta 1.5, M5 layer")
    streams = k2.plaintext_streams(by)
    allw = [w for v in streams.values() for w in v]
    pool = k2.codeword_pool(g, 120_000)
    for scale in (2.0, 8.0):
        book = k2.codebook(allw, g, scale, pool)[0]
        dump(f"nomen_k2_x{int(scale)}", k2.encrypt(by, streams, book, R, Qi, Qe, para, 1),
             f"k2 homophonic nomenclator x{scale}: Latin (Caesar/Augustine by section), flow beta 1.5, M5 layer")


if __name__ == "__main__":
    main()
