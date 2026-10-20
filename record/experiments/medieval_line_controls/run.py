"""MLC1: fetch pinned ALTO sources or score original medieval manuscript lines."""
from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import unicodedata as U
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scoreboard import metrics_new as M

HERE = Path(__file__).resolve().parent
DATA = ROOT / 'data/external/cremma-medieval-lat-mlc1'
COMMIT = '292525969ad98380b398e6606a9c2a36d51913ae'
REPO = 'HTR-United/CREMMA-Medieval-LAT'
SEED = 20261017


def digest(b):
    return hashlib.sha256(b).hexdigest()


def get(url):
    with urlopen(Request(url, headers={'User-Agent': 'Voynich-MLC1-research'}), timeout=60) as r:
        return r.read()


def fetch():
    tree = json.loads(get(f'https://api.github.com/repos/{REPO}/git/trees/{COMMIT}?recursive=1'))
    if tree.get('truncated'):
        raise RuntimeError('Truncated source tree')
    entries = [e for e in tree['tree'] if e['path'] in
               ('README.md', 'data-registry.csv', 'htr-united.yml') or
               (e['path'].startswith('data/') and e['path'].endswith('.xml')
                and not e['path'].endswith('.chocomufin.xml'))]

    def one(e):
        path = DATA / e['path']
        url = f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{e['path']}"
        b = path.read_bytes() if path.exists() else get(url)
        blob = hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
        if blob != e['sha']:
            raise RuntimeError(f"Source hash mismatch: {e['path']}")
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b)
        return dict(path=e['path'], url=url, git_blob=blob, sha256=digest(b), bytes=len(b))

    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(one, entries))
    manifest = dict(repository=REPO, commit=COMMIT, files=rows)
    (DATA / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Fetched/verified {len(rows)} files, {sum(r["bytes"] for r in rows)} bytes', flush=True)


def tokens(text, mode='lower'):
    s = U.normalize('NFD', text if mode == 'case' else text.lower())
    out, cur = [], ''
    for ch in s:
        cat = U.category(ch)
        if mode == 'strip' and cat.startswith('M'):
            continue
        if cat[0] in 'LM' or cat == 'Co' or ch == '\u204a':
            cur += ch
        elif cur:
            out.append(cur)
            cur = ''
    if cur:
        out.append(cur)
    return [w for w in out if any(not U.category(c).startswith('M') for c in w)]


def symbols(word):
    out = []
    for c in word:
        if U.category(c).startswith('M') and out:
            out[-1] += c
        else:
            out.append(c)
    return out


def parse_xml(raw, mode='lower'):
    root = ET.fromstring(raw)
    ns = {'a': 'http://www.loc.gov/standards/alto/ns-v4#'}
    tags = {x.get('ID'): x.get('LABEL') for x in root.findall('.//a:OtherTag', ns)}
    lines, qc = [], defaultdict(int)
    for block in root.findall('.//a:TextBlock', ns):
        ismain = 'MainZone' in [tags.get(t) for t in block.get('TAGREFS', '').split()]
        for ln in block.findall('a:TextLine', ns):
            qc['all_xml_lines'] += 1
            default = 'DefaultLine' in [tags.get(t) for t in ln.get('TAGREFS', '').split()]
            if not ismain or not default:
                qc['excluded_zone_or_type'] += 1
                continue
            text = ' '.join(s.get('CONTENT', '') for s in ln.findall('a:String', ns))
            ws = tokens(text, mode)
            if len(ws) < 3:
                qc['excluded_short'] += 1
            else:
                lines.append(ws)
                qc['retained_lines'] += 1
    return lines, dict(qc)


def jsd(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a / a.sum(), b / b.sum()
    m = (a + b) / 2
    ia, ib = a > 0, b > 0
    return float((np.sum(a[ia] * np.log2(a[ia] / m[ia])) +
                  np.sum(b[ib] * np.log2(b[ib] / m[ib]))) / 2)


class Edges:
    def __init__(self, lines):
        self.lines = [ln for ln in lines if len(ln) >= 3]
        if not self.lines:
            raise ValueError('No eligible lines')
        ws = [w for ln in self.lines for w in ln]
        self.n = np.array([len(ln) for ln in self.lines])
        self.starts = np.r_[0, np.cumsum(self.n)[:-1]]
        heads, tails = zip(*[(symbols(w)[0], symbols(w)[-1]) for w in ws])
        vocab = {g: i for i, g in enumerate(sorted(set(heads) | set(tails)))}
        self.k = len(vocab)
        self.h = np.array([vocab[g] for g in heads])
        self.t = np.array([vocab[g] for g in tails])
        self.hall = np.bincount(self.h, minlength=self.k)
        self.tall = np.bincount(self.t, minlength=self.k)

    def at(self, a, b):
        hf = np.bincount(self.h[a], minlength=self.k)
        hl = np.bincount(self.h[b], minlength=self.k)
        tf = np.bincount(self.t[a], minlength=self.k)
        tl = np.bincount(self.t[b], minlength=self.k)
        return np.array([jsd(hf, self.hall - hf - hl), jsd(tl, self.tall - tf - tl)])

    def observed(self):
        return self.at(self.starts, self.starts + self.n - 1)

    def null(self, rng, reps):
        out = []
        for _ in range(reps):
            a = rng.integers(self.n)
            b = rng.integers(self.n - 1)
            b += b >= a
            out.append(self.at(self.starts + a, self.starts + b))
        return np.array(out)


def score(pages, rng, reps=999, rotations=199):
    lines = [ln for pg in pages for ln in pg if len(ln) >= 3]
    e = Edges(lines)
    obs = e.observed()
    null = e.null(rng, reps)
    result = dict(lines=len(lines), tokens=sum(map(len, lines)), pages=len(pages),
                  observed=obs.tolist(), null_mean=null.mean(0).tolist(),
                  excess=(obs-null.mean(0)).tolist(), null_sd=null.std(0).tolist(),
                  p=((1+(null >= obs).sum(0))/(reps+1)).tolist())
    if rotations:
        shifted = []
        for _ in range(rotations):
            ls = []
            for pg in pages:
                pg = [ln for ln in pg if len(ln) >= 3]
                words = [w for ln in pg for w in ln]
                if not words:
                    continue
                j = int(rng.integers(len(words)))
                words = words[j:] + words[:j]
                start = 0
                for ln in pg:
                    ls.append(words[start:start+len(ln)])
                    start += len(ln)
            shifted.append(Edges(ls).observed())
        shifted = np.array(shifted)
        result['rotation_mean'] = shifted.mean(0).tolist()
        result['rotation_excess'] = (obs-shifted.mean(0)).tolist()
        result['rotation_p'] = ((1+(shifted >= obs).sum(0))/(rotations+1)).tolist()
    return result


def holm(ps):
    order = np.argsort(ps)
    result = np.empty(len(ps))
    high = 0.0
    for i, j in enumerate(order):
        high = max(high, min(1.0, (len(ps)-i)*ps[j]))
        result[j] = high
    return result.tolist()


def run(output):
    if output.exists():
        raise FileExistsError(f'Refusing to overwrite {output}')
    manifest = json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
    for row in manifest['files']:
        if digest((DATA/row['path']).read_bytes()) != row['sha256']:
            raise RuntimeError(f"Changed input: {row['path']}")
    registry = {r['Folder']: r for r in csv.DictReader(io.StringIO(
        (DATA/'data-registry.csv').read_text(encoding='utf-8-sig')))}
    books = defaultdict(list)
    for row in manifest['files']:
        if row['path'].endswith('.xml'):
            books[str(Path(row['path']).parent).replace('\\', '/')].append(row['path'])
    rng = np.random.default_rng(SEED)
    out = dict(protocol_sha256=digest((HERE/'PREREG.md').read_bytes()),
               code_sha256=digest(Path(__file__).read_bytes()), seed=SEED,
               python=platform.python_version(), numpy=np.__version__, source_commit=COMMIT,
               input_manifest_sha256=digest((DATA/'manifest.json').read_bytes()),
               metric_order=['initial_symbol_jsd', 'final_symbol_jsd'], manuscripts={}, controls={})
    manuscript_pages = {'ZL3b': M.voynich_pages('eva')}
    for name in ('RF1b', 'IT2a'):
        manuscript_pages[name] = M.meta_json_pages(ROOT/f'data/translit/{name}.meta.json')
    for name, pages in manuscript_pages.items():
        pgs = [p['lines'] for p in pages]
        r = score(pgs, rng)
        if name == 'ZL3b' and abs(r['observed'][0] - .1759) > .0001:
            raise RuntimeError(f'Baseline mismatch: {r}')
        out['manuscripts'][name] = r
        print(f'{name}: initial {r["observed"][0]:.4f}, excess {r["excess"][0]:.4f}', flush=True)
    for folder, files in sorted(books.items()):
        name = folder.split('/')[-1]
        rows, qcs = {}, {}
        for mode in ('lower', 'case', 'strip'):
            parsed = [parse_xml((DATA/f).read_bytes(), mode) for f in sorted(files)]
            pgs = [ls for ls, _ in parsed if ls]
            qc = defaultdict(int)
            for _, counts in parsed:
                for k, v in counts.items():
                    qc[k] += v
            qcs[mode] = dict(qc)
            if pgs:
                rows[mode] = score(pgs, rng, rotations=199 if mode == 'lower' else 0)
        out['controls'][name] = dict(registry=registry.get(folder), files=files, qc=qcs, scores=rows)
        if 'lower' in rows:
            r = rows['lower']
            print(f'{name}: lines {r["lines"]}, initial {r["observed"][0]:.4f}, excess {r["excess"][0]:.4f}', flush=True)
    eligible = [n for n, b in out['controls'].items() if b['scores'].get('lower', {}).get('lines', 0) >= 100]
    for metric in (0, 1):
        ps = [out['controls'][n]['scores']['lower']['p'][metric] for n in eligible]
        for n, p in zip(eligible, holm(ps)):
            out['controls'][n].setdefault('holm_p', [None, None])[metric] = p
    match_rng = np.random.default_rng(SEED+1)
    for n in eligible:
        ctrl = out['controls'][n]
        size = ctrl['scores']['lower']['lines']
        ctrl['matched_voynich'] = {}
        for name, pages in manuscript_pages.items():
            lines = [ln for p in pages for ln in p['lines'] if len(ln) >= 3]
            if size > len(lines):
                ctrl['matched_voynich'][name] = {'unavailable': 'control has more lines'}
                continue
            vals = []
            for _ in range(100):
                chosen = [lines[i] for i in match_rng.choice(len(lines), size=size, replace=False)]
                e = Edges(chosen)
                vals.append(e.observed()-e.null(match_rng, 19).mean(0))
            q = np.quantile(vals, [.025, .5, .975], axis=0)
            ctrl['matched_voynich'][name] = dict(quantiles=q.tolist(),
                initial_separates=bool(q[0, 0] > ctrl['scores']['lower']['excess'][0]))
        print(f'Size-matched {n}', flush=True)
    separated = all(c['initial_separates'] for n in eligible
                    for c in out['controls'][n]['matched_voynich'].values())
    positive = all(r['excess'][0] > 0 and r['p'][0] <= .01 for r in out['manuscripts'].values())
    out['eligible_controls'] = eligible
    out['verdict'] = 'SURVIVES_THIS_COMPARISON' if separated and positive and eligible else 'OVERLAP_OR_PARTIAL_SEPARATION'
    out['input_hashes'] = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in
        [ROOT/'data/ZL3b-n.txt', ROOT/'data/translit/RF1b.meta.json', ROOT/'data/translit/IT2a.meta.json',
         ROOT/'scoreboard/metrics_new.py', ROOT/'vparse.py', ROOT/'corpora.py']}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print(out['verdict'], output, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['fetch', 'score'])
    parser.add_argument('--output', type=Path, default=HERE/'results.json')
    args = parser.parse_args()
    fetch() if args.action == 'fetch' else run(args.output)
