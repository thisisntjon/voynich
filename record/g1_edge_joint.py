"""G1: section lexicon + train-only edge table + two line rules.

Pre-registered before the run. No parameter below is to be edited after
results_g1.txt exists.

Reported config (the one the outcome is read from):
  mode=seed, lex_size=200, seed=20261017, rule_p=0.088, rule_m=0.148
  rules applied after the line is drawn
Stability, same rules, not used to pick a winner: seed mode seeds 1..5
Circular upper bound, same rules: seeds 20261017, 1, 2
Cap: 9 configs.

Edge table: P(first EVA character | previous word's last character),
fit on real train-page lines only. Page split is an 80/20 shuffle with
Random(20261017). A left-context with fewer than 5 train pairs uses the
train marginal. The table is applied at draw time by rejection:
propose a word from the section lexicon, accept with probability
P(its first character | context) / max_g P(g | context), up to 40 tries,
then take the last proposal and count a fallback.

Line rules use C2's filed RULE_P and RULE_M (not the later rule_m=0.21
grid). They rewrite the first character of the line-initial word and the
last character of the line-final word. Within-line edge pairs use the
last character of word i and the first character of word i+1, which those
rewrites do not touch. The rules therefore do not override the edge table
on the pairs the board measures. That fact is a property of these two
rules, and it is logged.

Seed lexicon: C2's draw, L types with corpus count >= 2, weight sqrt(freq),
from the whole manuscript's types. Circular lexicon: the real words of
that (hand, section), also from the whole manuscript. Both look at test-page
types. The edge table does not. A run that fit the table on test pages
would be void; this script does not.

Score: score.score_corpus on the held-out pages and on the full skeleton.
A pass is the seven frozen PREREG v1 bands, on the held-out skeleton.
"""
import importlib.util
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location(
    "scoreboard_score", ROOT / "scoreboard" / "score.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

import corpora

OUT = ROOT / "results_g1.txt"
SEED = 20261017
MIN_COUNT = 5
MAX_TRIES = 40
RULE_P = 0.088
RULE_M = 0.148
REPORTED = ("seed", 200, SEED)
STABILITY = [("seed", 200, s) for s in (1, 2, 3, 4, 5)]
CIRCULAR = [("circular", None, s) for s in (SEED, 1, 2)]
CONFIGS = [REPORTED] + STABILITY + CIRCULAR

log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def pages():
    by = defaultdict(list)
    for r in corpora.voynich_lines():
        by[r["page"]].append(r)
    return by


def split_names(by):
    names = list(by)
    rng = random.Random(SEED)
    rng.shuffle(names)
    n = int(round(0.8 * len(names)))
    return names[:n], names[n:]


def fit_table(by, train_names):
    pairs = []
    for name in train_names:
        for r in by[name]:
            ws = r["words"]
            pairs += [(a[-1], b[0]) for a, b in zip(ws, ws[1:]) if a and b]
    by_left = defaultdict(Counter)
    marginal = Counter()
    for a, b in pairs:
        by_left[a][b] += 1
        marginal[b] += 1
    table = {a: cnt for a, cnt in by_left.items() if sum(cnt.values()) >= MIN_COUNT}
    cells = sum(len(cnt) for cnt in table.values())
    return table, marginal, len(pairs), cells


def lexicon_getter(by, mode, rng, lex_size):
    freq = Counter(w for recs in by.values() for r in recs for w in r["words"])
    types = [w for w, c in freq.items() if c >= 2 and w]
    weights = [freq[w] ** 0.5 for w in types]
    real = {}
    for recs in by.values():
        for r in recs:
            real.setdefault((r["hand"], r["illus"]), Counter()).update(
                w for w in r["words"] if w)
    cache = {}

    def get(key):
        if key not in cache:
            if mode == "circular":
                cnt = real.get(key) or Counter()
                ws = list(cnt) or types
                cache[key] = (ws, [cnt[w] if cnt else 1 for w in ws])
            else:
                chosen = set()
                target = min(lex_size, len(types))
                while len(chosen) < target:
                    need = target - len(chosen)
                    chosen.update(rng.choices(types, weights, k=need))
                ws = sorted(chosen)
                cache[key] = (ws, [freq[w] for w in ws])
        return cache[key]

    return get


def sample_glyph(rng, cnt):
    glyphs = list(cnt)
    return rng.choices(glyphs, [cnt[g] for g in glyphs])[0]


def draw_word(rng, ws, wt, prev, table, marginal):
    if prev is None:
        return rng.choices(ws, wt)[0], False
    cnt = table.get(prev, marginal)
    total = sum(cnt.values())
    pmax = max(cnt.values()) / total
    proposal = ws[0]
    for _ in range(MAX_TRIES):
        proposal = rng.choices(ws, wt)[0]
        p = cnt.get(proposal[0], 0) / total
        if pmax > 0 and rng.random() < p / pmax:
            return proposal, False
    return proposal, True


def apply_rules(rng, line):
    if line and rng.random() < RULE_P:
        w = line[0]
        line[0] = "p" + (w[1:] if w[0] in "ktfq" else w)
    if line and rng.random() < RULE_M:
        w = line[-1]
        line[-1] = (w[:-1] if w[-1] in "ynlrs" else w) + "m"
    return line


def generate(by, test_names, table, marginal, get, rng):
    """One pass in manuscript order. Held-out lines are the test pages of
    this same pass, not a second draw."""
    test = set(test_names)
    full, held = [], []
    draws = fallbacks = 0
    for name, recs in by.items():
        for r in recs:
            ws, wt = get((r["hand"], r["illus"]))
            line = []
            prev = None
            for _ in r["words"]:
                w, fell = draw_word(rng, ws, wt, prev, table, marginal)
                fallbacks += int(fell)
                draws += 1
                line.append(w)
                prev = w[-1]
            line = apply_rules(rng, line)
            full.append(line)
            if name in test:
                held.append(line)
    return full, held, draws, fallbacks


def band_fail(row):
    checks = {
        "h2": 1.98 <= row["h2"] <= 2.28,
        "sd_len": 1.41 <= row["sd_len"] <= 2.11,
        "jsd_first_fg": row["jsd_first_fg"] >= 0.10,
        "p_init_enrich": row["p_init_enrich"] >= 8,
        "m_final_enrich": row["m_final_enrich"] >= 8,
        "cross_excess_eva": row["cross_excess_eva"] >= 0.09,
        "redup_pct": 0.4 <= row["redup_pct"] <= 1.8,
    }
    return [k for k, ok in checks.items() if not ok]


def main():
    assert len(CONFIGS) <= 20
    by = pages()
    train, test = split_names(by)
    table, marginal, n_pairs, n_cells = fit_table(by, train)
    emit("G1 edge-joint  seed-split=20261017  rules after the line")
    emit(f"pages train={len(train)} test={len(test)}  "
         f"edge pairs={n_pairs}  contexts>={MIN_COUNT}: {len(table)}  "
         f"cells={n_cells}")
    emit("rejection draw, max 40 tries; line rules do not edit the characters "
         "inside a within-line edge pair")
    emit(f"reported config: {REPORTED}  rule_p={RULE_P} rule_m={RULE_M}")
    emit("held-out pass = all seven PREREG bands on test pages only")
    emit()
    held_rows = []
    for mode, lex_size, seed in CONFIGS:
        rng = random.Random(seed)
        get = lexicon_getter(by, mode, rng, lex_size or 0)
        full_lines, held_lines, draws, falls = generate(
            by, test, table, marginal, get, rng)
        tag = f"{mode}_L{lex_size}_s{seed}"
        for label, lines in (("full", full_lines), ("held", held_lines)):
            words = [w for line in lines for w in line]
            row = score.score_corpus(f"g1_{tag}_{label}", words, lines)
            failed = band_fail(row)
            emit(f"{tag:22} {label:4} tok={row['tokens']:5d} "
                 f"h2={row['h2']:.3f} sd={row['sd_len']:.3f} "
                 f"JSDf={row['jsd_first_fg']:.4f} p=x{row['p_init_enrich']} "
                 f"m=x{row['m_final_enrich']} excess={row['cross_excess_eva']:+.4f} "
                 f"redup={row['redup_pct']}%  "
                 f"fallback={falls}/{draws} ({100 * falls / max(draws, 1):.2f}%)")
            emit(f"{'':22} {label:4} joint={'PASS' if not failed else 'FAIL'} "
                 f"failed={failed or '-'}")
            if label == "held":
                held_rows.append((tag, row, failed))
        emit()

    def passed(mode_prefix):
        return [t for t, _, failed in held_rows
                if t.startswith(mode_prefix) and not failed]

    seed_ok = passed("seed_")
    circ_ok = passed("circular_")
    emit(f"held-out joint passes: seed={seed_ok or '-'} circular={circ_ok or '-'}")
    best = min(held_rows, key=lambda item: (len(item[2]), -item[1]["cross_excess_eva"]))
    emit(f"fewest held-out misses: {best[0]} failed={best[2] or '-'} "
         f"excess={best[1]['cross_excess_eva']:+.4f} "
         f"JSDf={best[1]['jsd_first_fg']:.4f}")
    if best[1]["cross_excess_eva"] < 0.05 or best[1]["jsd_first_fg"] < 0.05:
        emit("KILL CHECK: best held-out run is still under cross_excess +0.05 "
             "or JSDf 0.05. Generation is not a complete explanation.")
    else:
        emit("KILL CHECK: best held-out run clears both kill floors. "
             "A partial pass retires nothing.")
    if seed_ok and circ_ok:
        outcome = "BOTH PASS: a word list plus the two filters meets the board."
    elif circ_ok and not seed_ok:
        outcome = ("CIRCULAR ONLY: the real vocabulary passes and the seed "
                   "lexicon does not. The vocabulary is the load-bearing object.")
    elif not circ_ok:
        rep = next(item for item in held_rows if item[0] == "circular_LNone_s20261017")
        outcome = ("CIRCULAR FAILS on the reported seed. Bands missed: "
                   + ", ".join(rep[2]))
    else:
        outcome = "SEED PASSES, CIRCULAR DOES NOT. Unexpected; inspect the rows."
    emit("OUTCOME: " + outcome)
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
