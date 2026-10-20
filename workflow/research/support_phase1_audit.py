"""Independent, lightweight audit of Phase 1 measurement assumptions.

Synthetic counterexamples and source-format checks only. Does not run the CREMMA
experiment, modify its inputs, or alter the frozen board. Output is exclusive to
this support investigation. Run from the project root with Python -B.
"""
import hashlib
import json
from pathlib import Path
import sys
import unicodedata
import xml.etree.ElementTree as ET

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.medieval_line_controls.run import Edges, tokens

OUT = Path(__file__).with_suffix('.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def planned_tokenizer(text):
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                   if not unicodedata.category(c).startswith('M')).lower()
    return [w.rstrip('.:,;') for w in text.split() if w.rstrip('.:,;')]


def main():
    if OUT.exists():
        raise FileExistsError(f'Refusing to overwrite {OUT}')
    a = [['ax', 'bx', 'bx']]*100
    b = [['bx', 'ax', 'ax']]*100
    pooling = dict(manuscript_a=float(Edges(a).observed()[0]),
                   manuscript_b=float(Edges(b).observed()[0]),
                   pooled=float(Edges(a+b).observed()[0]))
    assert pooling == dict(manuscript_a=1., manuscript_b=1., pooled=0.)
    marked = [['a\u0303x', 'ax', 'ax']]*100
    unmarked = [[w.replace('\u0303', '') for w in ln] for ln in marked]
    marks = dict(preserved=float(Edges(marked).observed()[0]),
                 stripped=float(Edges(unmarked).observed()[0]))
    assert marks == dict(preserved=1., stripped=0.)
    rng = np.random.default_rng(20261017)
    null_bias = {}
    # Every token independently uniform: by construction there is no line effect.
    for n in (50, 100, 500, 1000, 4130):
        values = []
        for _ in range(200):
            arr = rng.integers(24, size=(n, 7))
            first = np.bincount(arr[:, 0], minlength=24).astype(float)
            mid = np.bincount(arr[:, 1:-1].ravel(), minlength=24).astype(float)
            from experiments.medieval_line_controls.run import jsd
            values.append(jsd(first, mid))
        null_bias[str(n)] = dict(mean=float(np.mean(values)),
            q025=float(np.quantile(values, .025)), q975=float(np.quantile(values, .975)))
    path = ROOT/'data/external/cremma-medieval-lat-mlc1/data/Arras-861/056r.xml'
    source = None
    if path.exists():
        ns = {'a': 'http://www.loc.gov/standards/alto/ns-v4#'}
        root = ET.fromstring(path.read_bytes())
        tags = {t.get('ID'): t.get('LABEL') for t in root.findall('.//a:OtherTag', ns)}
        blocks, differences = [], []
        for block in root.findall('.//a:TextBlock', ns):
            labels = [tags.get(t) for t in block.get('TAGREFS', '').split()]
            if 'MainZone' not in labels:
                continue
            lines = block.findall('a:TextLine', ns)
            blocks.append(dict(id=block.get('ID'), lines=len(lines),
                               hpos=block.get('HPOS'), width=block.get('WIDTH')))
            for line in lines:
                text = ' '.join(s.get('CONTENT', '') for s in line.findall('a:String', ns))
                planned = planned_tokenizer(text)
                split = tokens(text, 'strip')
                if len(planned) != len(split):
                    differences.append(dict(line=line.get('ID'), text=text,
                                            planned=planned, punctuation_delimited=split))
        source = dict(path=str(path.relative_to(ROOT)), sha256=sha(path),
                      mainzone_blocks=blocks, token_count_differences=len(differences),
                      examples=differences[:3])
    out = dict(scope='method audit, not manuscript effect estimation', seed=20261017,
        code_sha256=sha(Path(__file__)),
        helper_sha256=sha(ROOT/'experiments/medieval_line_controls/run.py'),
        reviewed_plan_sha256=sha(ROOT/'workflow/phases/phase-1.md'),
        pooling_counterexample=pooling, mark_stripping_counterexample=marks,
        iid_null_jsd_by_line_count=null_bias, source_format_check=source,
        assertions='PASS: two pooling values 1, pooled 0; marked 1, stripped 0')
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(out, indent=2, ensure_ascii=True))


if __name__ == '__main__':
    main()
