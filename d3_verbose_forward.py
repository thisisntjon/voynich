"""D3: VERBOSE-CIPHER FORWARD TEST (Naibbe-LIKE).

Question: if you take a REAL natural-language plaintext (Latin Caesar, via
corpora.control) and encipher it with a verbose homophonic cipher, which
Voynich signatures appear FOR FREE (no line rules, no positional rules),
and which still fail?

Encipherer (a deliberate simplification of Gaskell's 'Naibbe' proposal --
documented honestly; this is Naibbe-LIKE, not a reconstruction of any
specific published table set):
  1. Plaintext spaces are DISCARDED; the letter stream is segmented
     greedily into single letters and the 20 most frequent Latin letter
     bigrams of the Caesar sample itself (data-driven unit inventory).
  2. FIVE randomized tables (seeded). Each table is a complete codebook:
     it maps every unit to a distinct Voynich-like fragment sampled WITHOUT
     replacement within that table from a curated pool of frequent Voynich
     fragments (qo, ol, ar, aiin, edy, chol, che, she, dal, qoke, ...;
     1-4 EVA chars). The same fragment may serve different units in
     DIFFERENT tables (that cross-table reuse is what makes the cipher
     homophonic-yet-ambiguous in the Naibbe style). Per unit, the table is
     chosen i.i.d. uniformly -- a real scribe might cycle tables by line
     or page; i.i.d. choice is the no-positional-structure assumption.
  3. Cipher WORDS: after each encoded unit a word break is inserted with
     fixed probability p_space=0.5 (coin flip, chosen a priori, NOT tuned),
     independent of plaintext word boundaries, glyphs, and line position.
     Real Naibbe space placement may depend on the glyphs just written.
  4. Cipher LINES are imposed post hoc: words are grouped into lines whose
     words-per-line are resampled from the real Voynich empirical
     distribution. Enciphering/spacing never sees line position, so ANY
     line-position effect in the cipher would have to be a sampling fluke.
  5. Absent entirely: gallows/positional glyph rules, line-initial or
     line-final special forms, abbreviations, nulls, illustrations,
     Currier A/B variation, scribal hands. Metrics are on EVA characters
     (not merged glyphs), matching a1_profile's "VMS eva" convention.

Scoring (cipher vs real Voynich, flat stats both cut to N=25000 word
tokens as in a1_profile; line stats on full line-structured data):
  h2 (char conditional entropy, a1_profile.char_entropies), word-length
  mean/SD, Zipf slope (a1_profile.zipf_slope), adjacent-repeat rate,
  line-position JSDs (a2_position.stats/jsd, first/last glyph and length,
  plus a2_position permutation null), and p-initial / m-final enrichment
  (line-edge rate / mid-line rate). Cipher results are mean across 3 seeds
  (fresh tables, fresh table/space/line choices each seed).
"""
import random
from collections import Counter

import numpy as np

import corpora
from a1_profile import char_entropies, zipf_slope
from a2_position import null as a2_null, stats as a2_stats

N_TOKENS = 25000
N_TABLES = 5
P_SPACE = 0.5
N_BIGRAMS = 20
SEEDS = [1, 2, 3]

# --- Voynich-like fragment pool: frequent Voynich fragments, 1-4 EVA chars ---
FRAGMENTS = sorted(set([
    "o", "a", "e", "y", "d", "s", "l", "r", "k", "t",
    "qo", "ol", "or", "ar", "al", "dy", "ey", "ky", "ty", "sy", "ee", "ai",
    "ain", "edy", "chy", "shy", "che", "she", "kee", "tee", "oke", "ote",
    "dal", "dar", "sal", "sar", "kal", "kar", "tal", "tar", "dol", "dor",
    "sol", "sor", "kol", "kor", "qok", "qot", "oka", "ota", "eol", "eor",
    "eey", "iin", "iir", "in",
    "aiin", "chol", "chor", "shol", "dain", "sain", "kain", "tain",
    "chey", "shey", "qoke", "qote", "eedy", "aiir", "ched", "shed",
    # p-initial and m-final fragments exist in the pool so that line-edge
    # enrichment *could* arise; the encipherer uses them position-blindly.
    "po", "pol", "por", "pche", "am", "om", "dam", "sam", "aim", "eom",
]))


def fragment_pool():
    return list(FRAGMENTS)


def plaintext_units(words):
    stream = "".join(words)
    big = [b for b, _ in Counter(zip(stream, stream[1:])).most_common(N_BIGRAMS)]
    big = {"".join(b) for b in big}
    units, i = [], 0
    while i < len(stream):
        if stream[i:i + 2] in big:
            units.append(stream[i:i + 2]); i += 2
        else:
            units.append(stream[i]); i += 1
    return units, sorted(set(units) | big)


def encipher(seed, plain_words, line_lengths):
    rng = random.Random(seed)
    units, inventory = plaintext_units(plain_words)
    pool = fragment_pool()
    assert len(inventory) <= len(pool), f"pool {len(pool)} < units {len(inventory)}"
    tables = [dict(zip(inventory, rng.sample(pool, len(inventory))))
              for _ in range(N_TABLES)]
    used = [f for t in tables for f in t.values()]
    # encode + insert spaces
    words, cur = [], ""
    for u in units:
        cur += rng.choice(tables)[u]
        if rng.random() < P_SPACE:
            words.append(cur); cur = ""
        if len(words) >= N_TOKENS:
            break
    words = words[:N_TOKENS]
    # impose lines: resample Voynich words-per-line
    lines, i = [], 0
    while i < len(words):
        k = rng.choice(line_lengths)
        lines.append(words[i:i + k]); i += k
    meta = dict(n_units_used=len(inventory), pool_size=len(fragment_pool()),
                frag_mean_len=float(np.mean([len(f) for f in used])))
    return words, [l for l in lines if l], meta


def enrichment(lines):
    """p-initial (line-first word starts 'p') and m-final (line-last word
    ends 'm') rates at the line edge vs mid-line; ratio = enrichment."""
    cnt = Counter(); tot = Counter()
    for ws in lines:
        if len(ws) < 3:
            continue
        tot["first"] += 1; cnt["first_p"] += ws[0].startswith("p")
        tot["last"] += 1; cnt["last_m"] += ws[-1].endswith("m")
        for w in ws[1:-1]:
            tot["mid"] += 1
            cnt["mid_p"] += w.startswith("p"); cnt["mid_m"] += w.endswith("m")
    p_r = (cnt["first_p"] / tot["first"]) / max(cnt["mid_p"] / tot["mid"], 1e-9)
    m_r = (cnt["last_m"] / tot["last"]) / max(cnt["mid_m"] / tot["mid"], 1e-9)
    return dict(p_init_rate=cnt["first_p"] / tot["first"],
                p_mid_rate=cnt["mid_p"] / tot["mid"], p_enrich=p_r,
                m_final_rate=cnt["last_m"] / tot["last"],
                m_mid_rate=cnt["mid_m"] / tot["mid"], m_enrich=m_r)


def measure(words, lines, do_null=False):
    ce = char_entropies(words)
    lens = [len(w) for w in words]
    m = dict(h1=ce["h1"], h2=ce["h2"], mean_len=float(np.mean(lens)),
             sd_len=float(np.std(lens)), zipf=float(zipf_slope(words)),
             types=len(set(words)),
             hapax=float(np.mean([v == 1 for v in Counter(words).values()])),
             redup=100 * sum(a == b for a, b in zip(words, words[1:])) / (len(words) - 1))
    for label, feat in [("fg", lambda w: w[0]), ("lg", lambda w: w[-1]),
                        ("len", lambda w: min(len(w), 9))]:
        f, l = a2_stats(lines, feat)
        m[f"jsd_first_{label}"], m[f"jsd_last_{label}"] = float(f), float(l)
        if do_null:
            nl = a2_null(lines, feat, n=20)
            m[f"jsd_first_{label}_null"] = float(nl[:, 0].mean())
            m[f"jsd_last_{label}_null"] = float(nl[:, 1].mean())
    m.update({f"enr_{k}": v for k, v in enrichment(lines).items()})
    return m


def main():
    out = []
    def say(s=""):
        print(s); out.append(s)

    vlines_r = corpora.voynich_lines()
    vlines = [r["words"] for r in vlines_r]
    vwords = [w for l in vlines for w in l][:N_TOKENS]
    line_lengths = [len(l) for l in vlines if len(l) >= 1]
    latin = corpora.control("latin_caesar")
    say(f"D3 VERBOSE-CIPHER FORWARD TEST  N={N_TOKENS} tokens, tables={N_TABLES}, "
        f"p_space={P_SPACE}, bigram units={N_BIGRAMS}, seeds={SEEDS}")
    say(f"Voynich paragraph lines={len(vlines)} tokens(all)="
        f"{sum(map(len, vlines))}; Caesar plaintext words={len(latin)}")

    vm = measure(vwords, vlines, do_null=True)
    lm = measure(latin[:N_TOKENS], [latin[i:i + 8] for i in range(0, 8000, 8)])
    cms, metas = [], []
    for s in SEEDS:
        cw, cl, meta = encipher(s, latin, line_lengths)
        metas.append(meta)
        cms.append(measure(cw, cl, do_null=True))
        say(f"seed {s}: cipher words={len(cw)} lines={len(cl)} meta={meta}")
    keys = [k for k in vm if k in cms[0]]
    cm = {k: float(np.mean([c[k] for c in cms])) for k in keys}
    csd = {k: float(np.std([c[k] for c in cms])) for k in keys}

    say("\nmetric                         Voynich      cipher(mean+-sd)       Latin(plain)")
    for k in keys:
        say(f"{k:28} {vm[k]:10.3f}   {cm[k]:10.3f} +- {csd[k]:5.3f}   {lm.get(k, float('nan')):12.3f}")

    say("\nLine-position JSD vs permutation null (excess = observed - null mean):")
    for lab in ["fg", "lg", "len"]:
        for side in ["first", "last"]:
            k = f"jsd_{side}_{lab}"
            say(f"  {k:18} VMS excess={vm[k]-vm[k+'_null']:+.4f} (obs {vm[k]:.4f} null {vm[k+'_null']:.4f})"
                f"   cipher excess={cm[k]-cm[k+'_null']:+.4f} (obs {cm[k]:.4f} null {cm[k+'_null']:.4f})")
    say(f"\np-initial enrichment: VMS x{vm['enr_p_enrich']:.2f} "
        f"({vm['enr_p_init_rate']:.3f} vs mid {vm['enr_p_mid_rate']:.3f}) | "
        f"cipher x{cm['enr_p_enrich']:.2f} ({cm['enr_p_init_rate']:.3f} vs mid {cm['enr_p_mid_rate']:.3f})")
    say(f"m-final enrichment:   VMS x{vm['enr_m_enrich']:.2f} "
        f"({vm['enr_m_final_rate']:.3f} vs mid {vm['enr_m_mid_rate']:.3f}) | "
        f"cipher x{cm['enr_m_enrich']:.2f} ({cm['enr_m_final_rate']:.3f} vs mid {cm['enr_m_mid_rate']:.3f})")

    def verdict(name, ok):
        say(f"  [{'REPRODUCED' if ok else 'FAILS     '}] {name}")
    say("\nVERDICT (tolerances stated inline; read numbers above, not just flags):")
    verdict(f"h2 within 0.4 bits (VMS {vm['h2']:.2f} vs cipher {cm['h2']:.2f}; Latin plain {lm['h2']:.2f})",
            abs(cm["h2"] - vm["h2"]) <= 0.4)
    verdict(f"word-len mean within 1.0 EVA chars (VMS {vm['mean_len']:.2f} vs cipher {cm['mean_len']:.2f}) "
            f"[mean is partly set by p_space]", abs(cm["mean_len"] - vm["mean_len"]) <= 1.0)
    verdict(f"word-len SD within 0.5 (VMS {vm['sd_len']:.2f} vs cipher {cm['sd_len']:.2f}; "
            f"Bernoulli spaces predict geometric, over-dispersed lengths)",
            abs(cm["sd_len"] - vm["sd_len"]) <= 0.5)
    verdict(f"Zipf slope within 0.15 (VMS {vm['zipf']:.3f} vs cipher {cm['zipf']:.3f})",
            abs(cm["zipf"] - vm["zipf"]) <= 0.15)
    verdict(f"adjacent-repeat within 0.5pp (VMS {vm['redup']:.3f}% vs cipher {cm['redup']:.3f}%)",
            abs(cm["redup"] - vm["redup"]) <= 0.5)
    vex = np.mean([vm[f"jsd_{s}_{l}"] - vm[f"jsd_{s}_{l}_null"] for l in ["fg", "lg"] for s in ["first", "last"]])
    cex = np.mean([cm[f"jsd_{s}_{l}"] - cm[f"jsd_{s}_{l}_null"] for l in ["fg", "lg"] for s in ["first", "last"]])
    verdict(f"line-position JSD excess: VMS mean {vex:+.4f} vs cipher {cex:+.4f} "
            f"(cipher would need >= half the VMS excess)", cex >= 0.5 * vex)
    verdict(f"p-init / m-final enrichment: VMS x{vm['enr_p_enrich']:.2f}/x{vm['enr_m_enrich']:.2f} vs "
            f"cipher x{cm['enr_p_enrich']:.2f}/x{cm['enr_m_enrich']:.2f} (~1.0 = no effect)",
            cm["enr_p_enrich"] >= 1.3 and cm["enr_m_enrich"] >= 1.3)
    say("\nSimplifications: see module docstring (spaces discarded pre-enciphering; "
        "5 i.i.d. tables; fragments distinct within a table, reused across tables; Bernoulli p=0.5 spaces; "
        "lines imposed post hoc; no gallows/positional/abbreviation rules; EVA chars).")
    say("Interpretation: metrics flagged REPRODUCED are what ANY verbose homophonic "
        "enciphering of real Latin buys for free and therefore do not discriminate "
        "verbose-cipher from other generators; metrics flagged FAILS need extra "
        "machinery beyond verbose enciphering (see numbers).")

    with open("results_d3.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
