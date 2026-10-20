"""P1: bifolio-aligned null for the last page-contiguous signals.

Declared before the run. No new band and no threshold that is not already
in L1, C1, or M1. $Q and $F are the current binding's quire and sheet
(IVTFF). This is not a singulion reading order.

Part A. Conjoint folios. A sheet is one ($Q, $B). $B is the bifolio
(f1 and f8 in quire A are both $B=1). $F is the folio slot (a, b, ... z),
not the sheet. The pair is the two folios on a sheet that has exactly two
folios with paragraph text and the same majority (hand, illus), majority
taken over lines the way L1 does.
Cosine is L1's vocabulary cosine on the folio bag (recto+verso).
  page-shuffle null: 2000 within-stratum shuffles of folio bags, seed 20261017.
  length-preserving null: 2000 within-stratum token shuffles that keep each
  folio's token count, seed continuing from the same Random.
Decision, the L1 Part B rule, on the length-preserving null only:
  SURVIVES if p < 0.001, DIES if p >= 0.05, else MARGINAL.
Sheets with one folio or more than two are counted and not in that decision.
Sanity: the same function on pages must reprint L1's recto/verso observed
cosine 0.4206 and adjacent observed cosine 0.4153 (results_l1.txt). If it
does not, Part A is SANITY_FAIL and is not interpreted.

Part B. Topics. Same 40-word chunks and NMF as b5/c1 (random_state=0),
hands (1, H/P) and (2, B/H/T). The permutation unit is the bifolio
($Q|$B), not the quire-section block c1 used. NMI and the centroid
gap use c1's block_test definitions. Permutation seed 20261017.
  SURVIVES if NMI p < 0.05 and centroid p < 0.05.
  NMI-ONLY if only the NMI p is < 0.05.
  DIES if NMI p >= 0.05.
Sheet cohesion, separate from NMI: within a (hand, section), gap =
mean TF-IDF cosine of chunk pairs on the same bifolio minus mean cosine
of chunk pairs on different bifolios. Null: 2000 within-section shuffles
of bifolio labels. Pooled across sections.
  NEIGHBOURHOOD if that gap's one-sided p < 0.05, else NO_SHEET_EFFECT.

Part C. Page MI. Word-boundary pairs, top 500 types, cap 30,000, 5
shuffles, 30 bootstrap resamples, seed 20261017, the m0 profile's
corrections. Three relations share one subsample size:
  same_page_far (a line at least 3 away on the same page),
  same_bifolio_other_folio (same $Q|$B, other folio, not the verso),
  same_section_other_bifolio.
gap = mi(page) - mi(sheet). se_gap = se(page) + se(sheet), the sum of
the raw-MI bootstrap SEs.
  PAGE if gap > se_gap and mi(page) > 0.
  SHEET if not PAGE and mi(sheet) + se(sheet) >= mi(page) - se(page)
        and mi(sheet) > mi(other) + se(other).
  else WEAK.
Fewer than 200 pairs on a relation: INSUFFICIENT.

Part D. Section S column-specific excess from m1, same collect, seed
20261017. Page-cluster bootstrap is the filed check. Bifolio-cluster
bootstrap resamples ($Q, $B) and keeps every page of a drawn sheet.
  SURVIVES if the bifolio 95% interval lies entirely above 0.
  DIES if that interval includes 0.
The point estimate is descriptive. A mismatch with results_m1's +1.02 pp
is reported and Part D is then SANITY_FAIL.

Overall: CONTENT if any of A SURVIVES, B SURVIVES, C PAGE, D SURVIVES.
PHYSICAL if B is NEIGHBOURHOOD and the overall is not CONTENT.
Otherwise NONE. PHYSICAL is sheet similarity, not a reading.

Run: uv run python p1_bifolio_null.py -> results_p1.txt
"""
import math
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import normalized_mutual_info_score as nmi

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import b4_selfcite_sim as b4
import b5_nmf_topics as b5
import m1_coordinates as m1
import scoreboard.metrics_new as metrics_new
import vparse

OUT = ROOT / "results_p1.txt"
SEED = 20261017
N_PERM = 2000
HANDS = (("1", ("H", "P")), ("2", ("B", "H", "T")))
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def flush():
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


def bifolio_of_pages():
    out = {}
    for raw in vparse.DATA.read_text(encoding="ascii", errors="replace").splitlines():
        m = vparse.PAGE_RE.match(raw)
        if not m:
            continue
        meta = dict(vparse.VAR_RE.findall(m.group(2)))
        out[m.group(1)] = (meta.get("Q", "?"), meta.get("B", "?"))
    return out


def folio_key(page):
    m = __import__("re").match(r"^f(\d+)([rv])(\d*)$", page)
    if not m:
        return page
    return f"f{int(m.group(1))}{m.group(3)}"


def cosine_counter(c1, c2):
    if not c1 or not c2:
        return 0.0
    dot = sum(v * c2.get(k, 0) for k, v in c1.items())
    n1 = math.sqrt(sum(v * v for v in c1.values()))
    n2 = math.sqrt(sum(v * v for v in c2.values()))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)


def stats(obs, nulls):
    mu = sum(nulls) / len(nulls)
    var = sum((x - mu) ** 2 for x in nulls) / len(nulls)
    sd = math.sqrt(var)
    z = (obs - mu) / sd if sd > 0 else 0.0
    p = sum(1 for x in nulls if x >= obs - 1e-15) / len(nulls)
    return mu, sd, z, p


def decide_l1(p):
    if p < 0.001:
        return "SURVIVES"
    if p >= 0.05:
        return "DIES"
    return "MARGINAL"


def page_continuity(page_order, page_strata, page_words, rng):
    """L1 Part B, copied so the sanity line uses this file's cosine."""
    counters = {p: Counter(page_words[p]) for p in page_order}
    idx = {p: i for i, p in enumerate(page_order)}
    rv_pairs, adj_pairs = [], []
    for p1 in page_order:
        m = __import__("re").match(r"^f(\d+)([rv])(\d*)$", p1)
        if not m or m.group(2) != "r":
            continue
        target = f"f{m.group(1)}v{m.group(3)}"
        if target in idx and page_strata[p1] == page_strata[target]:
            rv_pairs.append((p1, target))
    for a, b in zip(page_order, page_order[1:]):
        if page_strata[a] == page_strata[b]:
            adj_pairs.append((a, b))

    def mean_sim(pairs, cmap):
        if not pairs:
            return 0.0
        return sum(cosine_counter(counters[cmap[a]], counters[cmap[b]]) for a, b in pairs) / len(pairs)

    ident = {p: p for p in page_order}
    obs_rv, obs_adj = mean_sim(rv_pairs, ident), mean_sim(adj_pairs, ident)
    by_st = defaultdict(list)
    for p in page_order:
        by_st[page_strata[p]].append(p)
    null_rv, null_adj = [], []
    for _ in range(N_PERM):
        perm = {}
        for plist in by_st.values():
            shuf = list(plist)
            rng.shuffle(shuf)
            perm.update(zip(plist, shuf))
        null_rv.append(mean_sim(rv_pairs, perm))
        null_adj.append(mean_sim(adj_pairs, perm))
    return dict(n_rv=len(rv_pairs), obs_rv=obs_rv, rv=stats(obs_rv, null_rv),
                n_adj=len(adj_pairs), obs_adj=obs_adj, adj=stats(obs_adj, null_adj))


def length_null(units, strata, words, pairs, rng, n_perm):
    """Mean cosine of `pairs` after shuffling tokens inside each stratum."""
    pool = defaultdict(list)
    for u in units:
        pool[strata[u]].extend(words[u])
    out = []
    for _ in range(n_perm):
        iters = {}
        for st, toks in pool.items():
            cp = list(toks)
            rng.shuffle(cp)
            iters[st] = iter(cp)
        counters = {}
        for u in units:
            n = len(words[u])
            it = iters[strata[u]]
            counters[u] = Counter(next(it) for _ in range(n))
        out.append(sum(cosine_counter(counters[a], counters[b]) for a, b in pairs) / len(pairs))
    return out


def assignments(labels, rng, maxperm=5000):
    cnt = Counter(labels)
    n_distinct = 1
    rem = len(labels)
    for v in cnt.values():
        n_distinct *= math.comb(rem, v)
        rem -= v
    if n_distinct > maxperm:
        return [tuple(rng.permutation(labels)) for _ in range(maxperm)], n_distinct
    out = []

    def rec(prefix, left):
        if len(prefix) == len(labels):
            out.append(tuple(prefix))
            return
        for k in sorted(left):
            if left[k]:
                left[k] -= 1
                rec(prefix + [k], left)
                left[k] += 1

    rec([], dict(cnt))
    return out, n_distinct


def block_test(units, cl, rng):
    blks = list(dict.fromkeys(u["blk"] for u in units))
    lab = [Counter(u["sec"] for u in units if u["blk"] == b).most_common(1)[0][0] for b in blks]
    obs = nmi([u["sec"] for u in units], cl)
    alls, n_dist = assignments(lab, rng)
    ix = [blks.index(u["blk"]) for u in units]
    vals = np.array([nmi([a[i] for i in ix], cl) for a in alls])
    X = TfidfVectorizer(min_df=2, token_pattern=r"\S+", sublinear_tf=True).fit_transform(
        [u["text"] for u in units])
    C = np.vstack([np.asarray(X[[i for i, u in enumerate(units) if u["blk"] == b]].mean(0)) for b in blks])
    norms = np.linalg.norm(C, axis=1, keepdims=True)
    norms[norms == 0] = 1
    C = C / norms
    D = 1 - C @ C.T
    iu = np.triu_indices(len(blks), 1)

    def dstat(a):
        same = np.array([a[i] == a[j] for i, j in zip(*iu)])
        d = D[iu]
        if not same.any() or not (~same).any():
            return np.nan
        return d[~same].mean() - d[same].mean()

    dobs = dstat(lab)
    dnull = np.array([dstat(a) for a in alls])
    return dict(obs=obs, null=float(vals.mean()), p=float(np.mean(vals >= obs - 1e-12)),
                nb=len(blks), na=len(alls), n_dist=n_dist, lab="".join(x[0] for x in lab),
                dobs=float(dobs), dp=float(np.nanmean(dnull >= dobs - 1e-12)))


def decide_topic(r):
    if r["p"] >= 0.05:
        return "DIES"
    if r["dp"] < 0.05:
        return "SURVIVES"
    return "NMI-ONLY"


def chunks(by, bmap):
    toks = []
    for recs in by.values():
        for r in recs:
            q, f = bmap.get(r["page"], ("?", "?"))
            for w in r["words"]:
                toks.append((w, r, f"{q}|{f}"))
    out = []
    for i in range(0, len(toks) - b5.CHUNK + 1, b5.CHUNK):
        part = toks[i:i + b5.CHUNK]
        def maj(key):
            return Counter(t[1][key] for t in part).most_common(1)[0][0]
        out.append(dict(text=" ".join(t[0] for t in part), sec=maj("illus"), hand=maj("hand"),
                        quire=maj("quire"), bifolio=Counter(t[2] for t in part).most_common(1)[0][0]))
    return out


def sheet_gap(S, labels):
    iu = np.triu_indices(len(labels), 1)
    same = np.array([labels[i] == labels[j] for i, j in zip(*iu)])
    if not same.any() or not (~same).any():
        return None
    d = S[iu]
    return float(d[same].mean() - d[~same].mean())


def part_c_profile(pages, bmap):
    rng = random.Random(SEED)
    freq = Counter(t for p in pages for ln in p["lines"] for t in ln)
    vocab = {w: i for i, (w, _) in enumerate(freq.most_common(500))}
    V = len(vocab) + 1
    other = V - 1
    ids = []
    for p in pages:
        qf = bmap.get(p["id"], ("?", "?"))
        ids.append((p["section"], f"{qf[0]}|{qf[1]}", folio_key(p["id"]),
                    [[vocab.get(t, other) for t in ln] for ln in p["lines"]]))
    rels = ["same_page_far", "same_bifolio_other_folio", "same_section_other_bifolio"]
    pairs = {r: [] for r in rels}
    by_sec = defaultdict(list)
    by_bf = defaultdict(list)
    flat = []
    for i, (sec, bf, fol, lines) in enumerate(ids):
        by_sec[sec].append(i)
        by_bf[bf].append(i)
        flat.append([t for ln in lines for t in ln])
    for i, (sec, bf, fol, lines) in enumerate(ids):
        others_bf = [j for j in by_bf[bf] if ids[j][2] != fol and flat[j]]
        others_sec = [j for j in by_sec[sec] if j != i and ids[j][1] != bf and flat[j]]
        for li, line in enumerate(lines):
            far = [k for k in range(len(lines)) if abs(k - li) >= 3 and lines[k]]
            for w in line:
                if far:
                    pairs["same_page_far"].append((w, rng.choice(lines[rng.choice(far)])))
                if others_bf:
                    pairs["same_bifolio_other_folio"].append((w, rng.choice(flat[rng.choice(others_bf)])))
                if others_sec:
                    pairs["same_section_other_bifolio"].append((w, rng.choice(flat[rng.choice(others_sec)])))
    usable = {r: pr for r, pr in pairs.items() if len(pr) >= 200}
    if len(usable) < 3:
        return pairs, None
    n = min(min(len(pr) for pr in usable.values()), 30000)
    nrng = np.random.default_rng(rng.randrange(1 << 30))
    res = {}
    for rel, pr in pairs.items():
        if len(pr) < 200:
            res[rel] = None
            continue
        arr = np.array(pr, dtype=np.int64)
        arr = arr[nrng.choice(len(arr), n, replace=False)]
        a, b = arr[:, 0], arr[:, 1]
        mi_raw, _hw = metrics_new._mi_from_pairs(a, b, V)
        null = [metrics_new._mi_from_pairs(a, nrng.permutation(b), V)[0] for _ in range(5)]
        boots = []
        for _ in range(30):
            ix = nrng.integers(0, n, n)
            boots.append(metrics_new._mi_from_pairs(a[ix], b[ix], V)[0])
        res[rel] = dict(n_pairs=len(pr), n_used=n, mi=mi_raw - float(np.mean(null)),
                        se=float(np.std(boots)))
    return pairs, res


def decide_mi(res):
    if res is None or any(res[k] is None for k in res):
        return "INSUFFICIENT"
    page, sheet, other = res["same_page_far"], res["same_bifolio_other_folio"], res["same_section_other_bifolio"]
    gap = page["mi"] - sheet["mi"]
    se_gap = page["se"] + sheet["se"]
    if gap > se_gap and page["mi"] > 0:
        return "PAGE"
    if sheet["mi"] + sheet["se"] >= page["mi"] - page["se"] and sheet["mi"] > other["mi"] + other["se"]:
        return "SHEET"
    return "WEAK"


def boot_clusters(res, rng, cluster_of, n_boot):
    folios = sorted({r[0] for rows in res.values() for r in rows})
    idx = {f: i for i, f in enumerate(folios)}
    clusters = sorted({cluster_of[f] for f in folios})
    members = defaultdict(list)
    for f in folios:
        members[cluster_of[f]].append(idx[f])
    per = {}
    for cond, rows in res.items():
        acc = defaultdict(lambda: np.zeros(3))
        for f, ex, e1 in rows:
            acc[f] += (1, ex, e1)
        M = np.zeros((len(folios), 3))
        for f, v in acc.items():
            M[idx[f]] = v
        per[cond] = M
    diffs = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(clusters), len(clusters))
        rows_idx = [i for c in pick for i in members[clusters[c]]]
        est = {}
        for c, M in per.items():
            s = M[rows_idx].sum(0)
            n = max(s[0], 1)
            est[c] = 100 * (s[1] + s[2]) / n
        diffs.append((est["same"] - est["far"]) - (est["off"] - est["off_far"]))
    a = np.array(diffs)
    return (float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5)),
            float(np.mean(a <= 0)), len(clusters))


def main():
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    emit(f"P1 bifolio-aligned null   seed {SEED}   run {stamp}")
    emit("Rules are in the docstring of p1_bifolio_null.py. No new band.")
    emit("$Q|$B is the current sheet ($F is the folio slot). Not a reading order.")
    emit("A first pass keyed on $F. Headers show f1 and f8 share $B=1 and not $F. This file is the $B run.")
    emit()
    bmap = bifolio_of_pages()
    by = b4.pages()

    emit("Part A  conjoint folios, L1 cosine")
    emit("-" * 72)
    page_order = list(by)
    page_strata = {}
    page_words = {}
    for p, recs in by.items():
        page_strata[p] = Counter((r["hand"], r["illus"]) for r in recs).most_common(1)[0][0]
        page_words[p] = [w for r in recs for w in r["words"] if w]
    sanity_rng = random.Random(SEED)
    san = page_continuity(page_order, page_strata, page_words, sanity_rng)
    sanity_ok = abs(san["obs_rv"] - 0.4206) < 5e-5 and abs(san["obs_adj"] - 0.4153) < 5e-5
    emit(f"sanity L1 page cosine  RV n={san['n_rv']} obs={san['obs_rv']:.4f} "
         f"(filed 0.4206)  Adj n={san['n_adj']} obs={san['obs_adj']:.4f} (filed 0.4153)  "
         f"{'MATCH' if sanity_ok else 'SANITY_FAIL'}")
    mu, sd, z, p = san["rv"]
    emit(f"sanity page-shuffle RV  null={mu:.4f}+/-{sd:.4f} z={z:+.2f} p={p:.4f}")
    mu, sd, z, p = san["adj"]
    emit(f"sanity page-shuffle Adj null={mu:.4f}+/-{sd:.4f} z={z:+.2f} p={p:.4f}")

    folios = {}
    for p, recs in by.items():
        fk = folio_key(p)
        slot = folios.setdefault(fk, dict(words=[], strata=Counter(), sheet=bmap.get(p, ("?", "?"))))
        slot["words"].extend(page_words[p])
        slot["strata"].update((r["hand"], r["illus"]) for r in recs)
        if slot["sheet"] != bmap.get(p, ("?", "?")):
            slot["sheet"] = ("CONFLICT", "CONFLICT")
    bags, strata, sheet_of = {}, {}, {}
    for fk, slot in folios.items():
        if not slot["words"] or slot["sheet"][0] == "CONFLICT":
            continue
        bags[fk] = slot["words"]
        strata[fk] = slot["strata"].most_common(1)[0][0]
        sheet_of[fk] = slot["sheet"]
    groups = defaultdict(list)
    for fk, sh in sheet_of.items():
        groups[sh].append(fk)
    n_one = sum(1 for v in groups.values() if len(v) == 1)
    n_two = sum(1 for v in groups.values() if len(v) == 2)
    n_more = sum(1 for v in groups.values() if len(v) > 2)
    pairs, mixed = [], 0
    for members in groups.values():
        if len(members) != 2:
            continue
        a, b = members
        if strata[a] != strata[b]:
            mixed += 1
            continue
        pairs.append((a, b))
    emit(f"sheets: {len(groups)}   exactly-two folios: {n_two}   singleton: {n_one}   "
         f"foldout(>2): {n_more}   mixed-stratum pairs dropped: {mixed}   pairs used: {len(pairs)}")
    a1 = sorted(fk for fk, sh in sheet_of.items() if sh == ("A", "1"))
    emit(f"check quire A $B=1 folios (f1 and f8 expected): {a1}")
    counters = {fk: Counter(bags[fk]) for fk in bags}
    obs = sum(cosine_counter(counters[a], counters[b]) for a, b in pairs) / len(pairs)
    by_st = defaultdict(list)
    for fk in bags:
        by_st[strata[fk]].append(fk)
    rng = random.Random(SEED)
    null_bag = []
    for _ in range(N_PERM):
        perm = {}
        for plist in by_st.values():
            shuf = list(plist)
            rng.shuffle(shuf)
            perm.update(zip(plist, shuf))
        null_bag.append(sum(cosine_counter(counters[perm[a]], counters[perm[b]]) for a, b in pairs) / len(pairs))
    mu, sd, z, p = stats(obs, null_bag)
    emit(f"conjoint page-shuffle   obs={obs:.4f} null={mu:.4f}+/-{sd:.4f} z={z:+.2f} p={p:.4f}  n={len(pairs)}")
    null_len = length_null(list(bags), strata, bags, pairs, rng, N_PERM)
    mu, sd, z, p = stats(obs, null_len)
    part_a = "SANITY_FAIL" if not sanity_ok else decide_l1(p)
    emit(f"conjoint length-preserved obs={obs:.4f} null={mu:.4f}+/-{sd:.4f} z={z:+.2f} p={p:.4f}")
    emit(f"DECISION Part A: {part_a}")
    emit("What would refute SURVIVES: length-preserved p >= 0.001 on these pairs. Checked in this file.")
    emit()
    flush()

    emit("Part B  bifolio-block topic null and sheet cohesion")
    emit("-" * 72)
    ch = chunks(by, bmap)
    rng_np = np.random.default_rng(SEED)
    part_b = "DIES"
    for hand, secs in HANDS:
        sub = [dict(c, blk=c["bifolio"]) for c in ch if c["hand"] == hand and c["sec"] in secs]
        cl = b5.topics([c["text"] for c in sub], k=len(secs) + 2)
        r = block_test(sub, cl, rng_np)
        flag = decide_topic(r)
        if flag == "SURVIVES":
            part_b = "SURVIVES"
        elif flag == "NMI-ONLY" and part_b != "SURVIVES":
            part_b = "NMI-ONLY"
        emit(f"hand {hand} bifolio-block NMI={r['obs']:.3f} null={r['null']:.3f} p={r['p']:.3f}  "
             f"centroid={r['dobs']:+.4f} p={r['dp']:.3f}  blocks={r['nb']} "
             f"assignments={r['na']}/{r['n_dist']}  {flag}")
        emit(f"  block labels {r['lab']}")
    X = TfidfVectorizer(min_df=2, token_pattern=r"\S+", sublinear_tf=True).fit_transform(
        [c["text"] for c in ch]).astype(float)
    norms = np.sqrt(np.asarray(X.multiply(X).sum(1)).ravel())
    norms[norms == 0] = 1
    X = X.multiply(1 / norms[:, None])
    gram = X @ X.T
    S = gram.toarray() if hasattr(gram, "toarray") else np.asarray(gram)
    groups_ch = defaultdict(list)
    for i, c in enumerate(ch):
        groups_ch[(c["hand"], c["sec"])].append(i)
    rng_b = np.random.default_rng(SEED)
    labels0 = np.array([c["bifolio"] for c in ch])
    same_sum = diff_sum = 0.0
    same_n = diff_n = 0
    eligible = []
    for key, ixs in groups_ch.items():
        ixs = np.array(ixs)
        if len(ixs) < 4:
            continue
        lab = labels0[ixs]
        if len(set(lab)) < 2 or max(Counter(lab).values()) < 2:
            continue
        eligible.append(ixs)
        g = sheet_gap(S[np.ix_(ixs, ixs)], lab)
        emit(f"  cohesion {key[0]}/{key[1]}: gap={g:+.4f}  chunks={len(ixs)} bifolios={len(set(lab))}")
    for ixs in eligible:
        lab = labels0[ixs]
        iu_i, iu_j = np.triu_indices(len(ixs), 1)
        d = S[ixs[iu_i], ixs[iu_j]]
        same = lab[iu_i] == lab[iu_j]
        same_sum += d[same].sum(); same_n += int(same.sum())
        diff_sum += d[~same].sum(); diff_n += int((~same).sum())
    obs_gap = same_sum / same_n - diff_sum / diff_n
    null_gaps = []
    for _ in range(N_PERM):
        ss = ds = 0.0
        sn = dn = 0
        for ixs in eligible:
            lab = labels0[ixs].copy()
            rng_b.shuffle(lab)
            iu_i, iu_j = np.triu_indices(len(ixs), 1)
            d = S[ixs[iu_i], ixs[iu_j]]
            same = lab[iu_i] == lab[iu_j]
            if not same.any() or not (~same).any():
                continue
            ss += d[same].sum(); sn += int(same.sum())
            ds += d[~same].sum(); dn += int((~same).sum())
        if sn and dn:
            null_gaps.append(ss / sn - ds / dn)
    mu, sd, z, p = stats(obs_gap, null_gaps)
    neigh = "NEIGHBOURHOOD" if p < 0.05 else "NO_SHEET_EFFECT"
    emit(f"pooled sheet gap obs={obs_gap:+.4f} null={mu:+.4f}+/-{sd:.4f} z={z:+.2f} p={p:.4f}  {neigh}")
    emit(f"DECISION Part B topics: {part_b}    sheet cohesion: {neigh}")
    emit("What would refute SURVIVES: bifolio-block NMI p >= 0.05, or centroid p >= 0.05. Checked above.")
    emit()
    flush()

    emit("Part C  same-page MI against the other page of the sheet")
    emit("-" * 72)
    pages = metrics_new.voynich_pages()
    raw_pairs, res = part_c_profile(pages, bmap)
    for rel, pr in raw_pairs.items():
        extra = ""
        if res and res.get(rel):
            extra = f"  mi={res[rel]['mi']:+.4f} se={res[rel]['se']:.4f} n_used={res[rel]['n_used']}"
        emit(f"  {rel}: n_pairs={len(pr)}{extra}")
    part_c = decide_mi(res)
    emit(f"DECISION Part C: {part_c}")
    emit("What would refute PAGE: gap <= se(page)+se(sheet) inside this run. Checked above.")
    emit("m0's filed same_page_far is +0.029 on a seven-relation common subsample; this run's")
    emit("three-relation subsample is a different draw and is not required to reprint +0.029.")
    emit()
    flush()

    emit("Part D  section S column excess, bifolio cluster bootstrap")
    emit("-" * 72)
    try:
        pages_m, _stats = m1.build_pages()
        sec = {f: pg for f, pg in pages_m.items() if pg["meta"]["illus"] == "S"}
        res_s = m1.collect(sec, random.Random(SEED))
        rs, rf = m1.rates(res_s["same"]), m1.rates(res_s["far"])
        ro, rof = m1.rates(res_s["off"]), m1.rates(res_s["off_far"])
        point = (rs["le1"] - rf["le1"]) - (ro["le1"] - rof["le1"])
        filed = 1.02
        match = abs(point - filed) < 0.02
        emit(f"section S pages={len(sec)}  column-specific excess={point:+.2f} pp  "
             f"filed +1.02  {'MATCH' if match else 'SANITY_FAIL'}")
        _ci, dci = m1.boot(res_s, np.random.default_rng(SEED))
        lo, hi, pv = dci["column-specific"]
        emit(f"page-cluster 95% CI [{lo:+.2f}, {hi:+.2f}]  P(diff<=0)={pv:.3f}  (filed P=0.016)")
        cluster = {f: bmap.get(f, ("?", f)) for f in sec}
        blo, bhi, bp, nb = boot_clusters(res_s, np.random.default_rng(SEED), cluster, m1.N_BOOT)
        part_d = "SANITY_FAIL" if not match else ("SURVIVES" if blo > 0 else "DIES")
        emit(f"bifolio-cluster n={nb}  95% CI [{blo:+.2f}, {bhi:+.2f}]  P(diff<=0)={bp:.3f}")
        emit(f"DECISION Part D: {part_d}")
    except Exception as exc:
        part_d = "ERROR"
        emit(f"DECISION Part D: ERROR {type(exc).__name__}: {exc}")
    emit("What would refute DIES: a bifolio-cluster interval lying entirely above 0, on a collect")
    emit("whose point estimate matches the filed +1.02 pp. Checked above.")
    emit()

    content = []
    if part_a == "SURVIVES":
        content.append("A")
    if part_b == "SURVIVES":
        content.append("B")
    if part_c == "PAGE":
        content.append("C")
    if part_d == "SURVIVES":
        content.append("D")
    if content:
        overall = "CONTENT (" + ",".join(content) + ")"
    elif neigh == "NEIGHBOURHOOD":
        overall = "PHYSICAL"
    else:
        overall = "NONE"
    emit(f"DECISION OVERALL: {overall}")
    emit("CONTENT would be page or section signal past the sheet. PHYSICAL is sheet similarity.")
    emit("Neither is a key, a language, or a reading. What would refute NONE/PHYSICAL as the")
    emit("last word on content is a later non-Voynich joint pass of the seven v1 bands.")
    flush()


if __name__ == "__main__":
    main()
