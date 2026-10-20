"""Voynich focused battery: statistics + cipher tests (stdlib only).

Method: every test runs on Voynich paragraph text AND on controls:
  - English control (workspace docs), also monoalphabetically enciphered
    (positive control: tests/solvers must flag a known simple cipher),
  - Voynich with word order shuffled (destroys syntax, keeps vocabulary),
  - Markov-1 pseudo-Voynich (keeps char bigrams, destroys real words).
A Voynich result only counts if it separates from the right controls.

Run: uv run python analyze.py   (writes results/results.json, results/summary.md)
"""
import json
import math
import random
import re
from collections import Counter
from pathlib import Path

import vparse

ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
SEED = 20261017
rng = random.Random(SEED)


# ---------- generic stats helpers ----------

def entropy(counter):
    n = sum(counter.values())
    return -sum((c / n) * math.log2(c / n) for c in counter.values() if c)


def cond_entropy(seq):
    """H(X_t | X_{t-1}) over a flat sequence."""
    if len(seq) < 3:
        return float("nan")
    pairs = Counter(zip(seq, seq[1:]))
    firsts = Counter(seq[:-1])
    n = len(seq) - 1
    h = 0.0
    for (a, _b), c in pairs.items():
        p_ab = c / n
        p_a = firsts[a] / n
        h -= p_ab * math.log2(p_ab / p_a)
    return h


def index_of_coincidence(seq):
    n = len(seq)
    if n < 2:
        return float("nan")
    return sum(c * (c - 1) for c in Counter(seq).values()) / (n * (n - 1))


def zipf_fit(freqs, top_n=500):
    """Least-squares fit of log10(freq) vs log10(rank); returns slope, r^2."""
    vals = sorted(freqs.values(), reverse=True)[:top_n]
    xs = [math.log10(i + 1) for i in range(len(vals))]
    ys = [math.log10(v) for v in vals]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    slope = sxy / sxx if sxx else float("nan")
    r2 = (sxy * sxy) / (sxx * syy) if sxx and syy else float("nan")
    return slope, r2


def js_divergence(c1, c2):
    """Jensen-Shannon divergence (bits) between two Counters."""
    keys = set(c1) | set(c2)
    n1, n2 = sum(c1.values()), sum(c2.values())
    js = 0.0
    for k in keys:
        p, q = c1.get(k, 0) / n1, c2.get(k, 0) / n2
        m = (p + q) / 2
        if p:
            js += 0.5 * p * math.log2(p / m)
        if q:
            js += 0.5 * q * math.log2(q / m)
    return js


def edit1_neighbors(word, vocab):
    """Count vocab words at Levenshtein distance exactly 1 (generative check)."""
    out = 0
    alphabet = set("".join(vocab)) if vocab else set()
    for i in range(len(word)):  # deletions + substitutions
        if word[:i] + word[i + 1:] in vocab:
            out += 1
        for ch in alphabet:
            if ch != word[i] and word[:i] + ch + word[i + 1:] in vocab:
                out += 1
    for i in range(len(word) + 1):  # insertions
        for ch in alphabet:
            if word[:i] + ch + word[i:] in vocab:
                out += 1
    return out


# ---------- corpora ----------

def clean_words(words):
    return [w for w in words if w and "?" not in w]


def char_stream(words):
    return list("".join(words))


def english_control():
    """Modern technical English from workspace docs (measured, local provenance)."""
    texts = []
    for name in ("PROJECTS.md", "AGENTS.md", "README.md"):
        p = ROOT.parent / name
        if p.exists():
            texts.append(p.read_text(encoding="utf-8", errors="replace"))
    words = re.findall(r"[a-z]+", " ".join(texts).lower())
    return [w for w in words if len(w) > 1]


def substitution_cipher(words, seed=SEED):
    """Monoalphabetic substitution over a-z with a seeded random key."""
    local = random.Random(seed)
    plain = list("abcdefghijklmnopqrstuvwxyz")
    cipher = plain[:]
    local.shuffle(cipher)
    table = str.maketrans("".join(plain), "".join(cipher))
    return [w.translate(table) for w in words]


def markov_words(words, count, seed=SEED):
    """Pseudo-words from within-word char bigrams, lengths matched to source."""
    local = random.Random(seed)
    starts = Counter(w[0] for w in words if w)
    trans = {}
    for w in words:
        for a, b in zip(w, w[1:]):
            trans.setdefault(a, Counter())[b] += 1
    lengths = [len(w) for w in words]
    start_pool = list(starts.elements())
    out = []
    for _ in range(count):
        target = local.choice(lengths)
        w = local.choice(start_pool)
        while len(w) < target:
            nxt = trans.get(w[-1])
            if not nxt:
                break
            w += local.choices(list(nxt), weights=list(nxt.values()))[0]
        out.append(w)
    return out


def profile(words, label):
    freqs = Counter(words)
    chars = char_stream(words)
    slope, r2 = zipf_fit(freqs)
    lens = [len(w) for w in words]
    return {
        "label": label,
        "tokens": len(words),
        "types": len(freqs),
        "ttr": round(len(freqs) / len(words), 4) if words else None,
        "hapax_rate": round(
            sum(1 for c in freqs.values() if c == 1) / len(freqs), 4
        ) if freqs else None,
        "mean_word_len": round(sum(lens) / len(lens), 3) if lens else None,
        "alphabet_size": len(set(chars)),
        "char_H0_bits": round(entropy(Counter(chars)), 4),
        "char_H1_cond_bits": round(cond_entropy(chars), 4),
        "char_IC": round(index_of_coincidence(chars), 5),
        "word_IC": round(index_of_coincidence(words), 5),
        "word_H0_bits": round(entropy(freqs), 4),
        "word_H1_cond_bits": round(cond_entropy(words), 4),
        "zipf_slope": round(slope, 4),
        "zipf_r2": round(r2, 4),
        "top_words": freqs.most_common(15),
        "top_chars": Counter(chars).most_common(25),
        "wordlen_dist": dict(sorted(Counter(lens).items())),
    }


# ---------- Voynich-specific tests ----------

def repetition(words):
    doubles = sum(1 for a, b in zip(words, words[1:]) if a == b)
    bigrams = Counter(zip(words, words[1:]))
    trigrams = Counter(zip(words, words[1:], words[2:]))
    return {
        "adjacent_double_rate": round(doubles / max(len(words) - 1, 1), 5),
        "adjacent_doubles": doubles,
        "top_word_bigrams": [(f"{a} {b}", c) for (a, b), c in bigrams.most_common(10)],
        "top_word_trigrams": [
            (f"{a} {b} {c}", n) for (a, b, c), n in trigrams.most_common(10)
        ],
        "repeated_bigram_types": sum(1 for c in bigrams.values() if c > 1),
        "bigram_types": len(bigrams),
    }


def word_structure(words, para_recs):
    prefixes = Counter(w[:2] for w in words if len(w) >= 2)
    suffixes = Counter(w[-3:] for w in words if len(w) >= 3)
    def pos_entropy(pick):
        return round(entropy(Counter(pick(w) for w in words if len(w) >= 4)), 4)
    gallows = set("ktpf")
    first_words, other_words = [], []
    for r in para_recs:
        ws = clean_words(r["words"])
        if ws:
            first_words.append(ws[0])
            other_words.extend(ws[1:])
    def gallows_rate(ws):
        return round(
            sum(1 for w in ws if w and w[0] in gallows) / len(ws), 4
        ) if ws else None
    return {
        "top_prefixes_2": prefixes.most_common(12),
        "top_suffixes_3": suffixes.most_common(12),
        "pos_entropy_first_char": pos_entropy(lambda w: w[0]),
        "pos_entropy_second_char": pos_entropy(lambda w: w[1]),
        "pos_entropy_last_char": pos_entropy(lambda w: w[-1]),
        "pos_entropy_second_last": pos_entropy(lambda w: w[-2]),
        "line_initial_gallows_rate": gallows_rate(first_words),
        "line_other_gallows_rate": gallows_rate(other_words),
        "line_initial_n": len(first_words),
    }


def neighbor_density(words, sample_n=400, seed=SEED):
    vocab = set(words)
    local = random.Random(seed)
    sample = local.sample(sorted(vocab), min(sample_n, len(vocab)))
    counts = [edit1_neighbors(w, vocab) for w in sample]
    return {
        "sample_n": len(sample),
        "frac_with_neighbor": round(sum(1 for c in counts if c) / len(counts), 4),
        "mean_neighbors": round(sum(counts) / len(counts), 3),
        "max_neighbors": max(counts) if counts else 0,
    }


def currier(recs_para):
    def words_for(lang):
        return clean_words([w for r in recs_para if r["lang"] == lang for w in r["words"]])
    a, b = words_for("A"), words_for("B")
    va, vb = set(a), set(b)
    half = len(b) // 2
    shuffled = b[:]
    random.Random(SEED).shuffle(shuffled)
    return {
        "A_tokens": len(a), "B_tokens": len(b),
        "A_types": len(va), "B_types": len(vb),
        "vocab_jaccard_AB": round(len(va & vb) / len(va | vb), 4),
        "char_JS_AB_bits": round(js_divergence(Counter(char_stream(a)),
                                                Counter(char_stream(b))), 5),
        "word_JS_AB_bits": round(js_divergence(Counter(a), Counter(b)), 5),
        "char_JS_B_halves_bits": round(js_divergence(
            Counter(char_stream(shuffled[:half])),
            Counter(char_stream(shuffled[half:]))), 5),
        "word_JS_B_halves_bits": round(js_divergence(
            Counter(shuffled[:half]), Counter(shuffled[half:])), 5),
        "top_A_only": [
            (w, c) for w, c in Counter(a).most_common(50) if w not in vb][:10],
        "top_B_only": [
            (w, c) for w, c in Counter(b).most_common(50) if w not in va][:10],
    }


# ---------- simple-substitution crack attempt ----------

def bigram_model(words):
    """Log-probs for letter bigrams (within words), add-1 smoothed."""
    counts = Counter()
    totals = Counter()
    for w in words:
        for a, b in zip(w, w[1:]):
            counts[(a, b)] += 1
            totals[a] += 1
    alphabet = sorted(set(char_stream(words)))
    model = {}
    for a in alphabet:
        denom = totals[a] + len(alphabet)
        for b in alphabet:
            model[(a, b)] = math.log((counts.get((a, b), 0) + 1) / denom)
    return model, alphabet


def solve_substitution(cipher_words, model, plain_alphabet,
                       restarts=6, iters=3000, max_chars=4000, seed=SEED):
    """Hill-climb injective cipher->plain mapping by bigram score.

    Returns (best_score_per_bigram, mapping, sample_plain_words).
    Score is comparable across corpora scored with the same model.
    """
    text = " ".join(cipher_words)
    # cap work: keep whole words up to max_chars characters
    kept, total = [], 0
    for w in cipher_words:
        kept.append(w)
        total += len(w) + 1
        if total >= max_chars:
            break
    cipher_alpha = sorted(set(char_stream(kept)))
    pairs = []
    for w in kept:
        pairs.extend(zip(w, w[1:]))
    pair_counts = Counter(pairs)
    n_pairs = max(sum(pair_counts.values()), 1)
    local = random.Random(seed)
    best = None
    for _ in range(restarts):
        targets = plain_alphabet[:]
        local.shuffle(targets)
        targets = targets[:len(cipher_alpha)]
        mapping = dict(zip(cipher_alpha, targets))
        def score(m):
            return sum(c * model.get((m[a], m[b]), -12.0)
                       for (a, b), c in pair_counts.items())
        cur = score(mapping)
        for _ in range(iters):
            i, j = local.sample(range(len(cipher_alpha)), 2)
            a, b = cipher_alpha[i], cipher_alpha[j]
            mapping[a], mapping[b] = mapping[b], mapping[a]
            new = score(mapping)
            if new > cur:
                cur = new
            else:
                mapping[a], mapping[b] = mapping[b], mapping[a]
        if best is None or cur > best[0]:
            best = (cur, dict(mapping))
    total_score, mapping = best
    plain_sample = ["".join(mapping.get(ch, "?") for ch in w) for w in kept[:25]]
    return round(total_score / n_pairs, 4), mapping, plain_sample, len(text)


# ---------- main ----------

def main():
    recs = vparse.load()
    para = vparse.paragraph_text(recs)
    vwords = clean_words([w for r in para for w in r["words"]])
    shuffled = vwords[:]
    rng.shuffle(shuffled)
    eng = english_control()
    eng_cipher = substitution_cipher(eng)
    markov = markov_words(vwords, len(vwords))

    results = {
        "source": "ZL IVTFF EVA transliteration (data/ZL3b-n.txt), paragraph units (P*)",
        "seed": SEED,
        "profiles": {
            "voynich_para": profile(vwords, "Voynich paragraphs"),
            "english_control": profile(eng, "English workspace docs"),
            "english_substitution_cipher": profile(eng_cipher, "English, monoalphabetic cipher"),
            "voynich_shuffled_words": profile(shuffled, "Voynich, word order shuffled"),
            "voynich_markov1": profile(markov, "Voynich Markov-1 pseudo-words"),
        },
        "repetition_voynich": repetition(vwords),
        "repetition_english": repetition(eng),
        "repetition_markov": repetition(markov),
        "word_structure_voynich": word_structure(vwords, para),
        "neighbors_voynich": neighbor_density(vwords),
        "neighbors_english": neighbor_density(eng),
        "neighbors_markov": neighbor_density(markov),
        "currier_AB": currier(para),
    }

    model, plain_alpha = bigram_model(eng)
    # Identity check: score English with identity mapping directly.
    eng_pairs = Counter(p for w in eng for p in zip(w, w[1:]))
    eng_identity = round(
        sum(c * model[p] for p, c in eng_pairs.items())
        / max(sum(eng_pairs.values()), 1), 4)
    cipher_score, cipher_map, cipher_plain, _ = solve_substitution(
        eng_cipher, model, plain_alpha)
    voy_score, voy_map, voy_plain, _ = solve_substitution(
        vwords, model, plain_alpha)
    results["substitution_attempt"] = {
        "scorer": "English within-word letter-bigram log-prob per bigram (higher=more English-like)",
        "english_identity_score": eng_identity,
        "enciphered_english_solved_score": cipher_score,
        "enciphered_english_recovered_sample": cipher_plain,
        "voynich_best_score": voy_score,
        "voynich_best_mapping": voy_map,
        "voynich_decoded_sample": voy_plain,
        "note": "Positive control must score near English identity; "
                "Voynich far below it falsifies plain monoalphabetic substitution "
                "of English-like plaintext under EVA-as-alphabet.",
    }

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8")
    write_summary(results)
    print(json.dumps({k: results["profiles"][k] for k in
                      ("voynich_para", "english_control")}, indent=2)[:1500])
    print("substitution:", results["substitution_attempt"]["voynich_best_score"],
          "vs english", eng_identity, "vs solved-cipher", cipher_score)
    print(f"Wrote {RESULTS / 'results.json'} and {RESULTS / 'summary.md'}")


def write_summary(r):
    p = r["profiles"]
    keys = ["tokens", "types", "ttr", "hapax_rate", "mean_word_len",
            "alphabet_size", "char_H0_bits", "char_H1_cond_bits", "char_IC",
            "word_H1_cond_bits", "zipf_slope", "zipf_r2"]
    cols = list(p.keys())
    lines = ["# Voynich battery summary (generated by analyze.py)", "",
             f"Source: {r['source']}  |  Seed: {r['seed']}", "",
             "| Metric | " + " | ".join(cols) + " |",
             "|---|" + "---|" * len(cols)]
    for k in keys:
        lines.append("| " + k + " | " + " | ".join(str(p[c][k]) for c in cols) + " |")
    s = r["substitution_attempt"]
    lines += ["", "## Simple-substitution attempt (English bigram scorer)", "",
              f"- English (identity): {s['english_identity_score']}",
              f"- Enciphered English (solved): {s['enciphered_english_solved_score']}",
              f"- Voynich (best found): {s['voynich_best_score']}",
              f"- Voynich decoded sample: {' '.join(s['voynich_decoded_sample'])}",
              f"- Recovered English sample: {' '.join(s['enciphered_english_recovered_sample'])}",
              "", "See results.json for full detail and FINDINGS.md for interpretation."]
    (RESULTS / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
