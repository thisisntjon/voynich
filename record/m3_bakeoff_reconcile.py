"""M3: reconcile the two held-out bake-offs (d2_slot_bakeoff.py vs scoreboard/metrics_new.py
heldout_bakeoff) that disagree on word-unigram vs char-trigram ordering on Voynich.

ONE SHARED DEFINITION (used for every cell of the table):
  * corpus  : Voynich paragraph units (P*), EVA, tokens containing '?' dropped (both scripts
              already do this); italian_dante = corpora.control(25000 tokens) wrapped
              8 tokens/line, 20 lines/page (as scoreboard/run_new.py).
  * score   : bits/token = -mean log2 P(word string) over all held-out tokens.  Every char
              model scores the whole string INCLUDING the end-of-word symbol '$' (so word
              length is paid for); no separate space symbol; bits/char also reported as
              bits / (len(w)+1), as in m0.
  * splits  : "page"  = d2's split: shuffle pages, 80/20, one fold.
              "quire" = m0's split: leave-one-quire-out for Voynich (16 folds); blocks of 10
              consecutive pages for the control (no quire labels), summed over folds.
  * models  : unigram-GT+char   = m0 UnigramGT: seen w -> (1-p0) c/N, unseen -> p0 * P_char3WB(w),
                                  p0 = N1/N (mass spread over strings by the WB char-3 model).
              unigram-GT-renorm = same, but the char-3 mass already sitting on seen train types
                                  (~86% for Voynich, ~68% Italian) is removed: unseen ->
                                  p0 * P_char3WB(w) / (1 - sum_{seen v} P_char3WB(v)).  This is a
                                  proper distribution over strings (the fair vocabulary-list model).
              unigram-flatUNK   = d2 p_unigram: (c+0.1)/(N+0.1(V+1)); ALL unseen strings share
                                  ONE bucket of mass 0.1/(N+0.1(V+1)).  NOT a distribution over
                                  strings (sums to >1 over the string space), so its unseen cost
                                  is a lower bound, not a code length.
              char3-WB          = m0 CharMarkov(order 3), interpolated Witten-Bell, '^^^' pad.
              char3-add0.01     = d2 p_char_str with alpha=0.01 (d2 used 0.1): '^^' pad,
                                  (c+a)/(n+a*A), A = |alphabet|+1 ('$').
  Reproduction rows: d2's exact split (seed 42) with d2's own alpha=0.1 models, to show the
  published 10.728 / 11.279 are recovered before changing anything.
Seed 20261017 for the page split.  Writes results_m3_bakeoff_reconcile.txt.
"""
import math
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import corpora  # noqa: E402
from scoreboard import metrics_new as M  # noqa: E402

SEED = 20261017
OUT = ROOT / "results_m3_bakeoff_reconcile.txt"
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


# ---------------------------------------------------------------- models
class UnigramFlatUNK:
    """d2 (i): add-alpha over train types + one UNK bucket."""

    def __init__(self, words, alpha=0.1):
        self.c = Counter(words); self.N = len(words); self.V = len(self.c); self.a = alpha
        self.den = self.N + alpha * (self.V + 1)

    def logp_word(self, w):
        return math.log2((self.c.get(w, 0) + self.a) / self.den)


class CharAdditive:
    """d2 (ii): P(c | prev2) add-alpha per context, '^^' pad, '$' end."""

    def __init__(self, words, alpha=0.01, order=2):
        self.a = alpha; self.k = order
        alph = set("".join(words))
        self.A = len(alph) + 1
        self.ctx = defaultdict(Counter); self.tot = Counter()
        for w in words:
            s = "^" * order + w + "$"
            for i in range(order, len(s)):
                self.ctx[s[i - order:i]][s[i]] += 1; self.tot[s[i - order:i]] += 1

    def logp_word(self, w):
        s = "^" * self.k + w + "$"; lp = 0.0
        for i in range(self.k, len(s)):
            c = s[i - self.k:i]
            lp += math.log2((self.ctx[c].get(s[i], 0) + self.a) / (self.tot[c] + self.a * self.A))
        return lp


class UnigramGTRenorm(M.UnigramGT):
    """m0 UnigramGT with the char mass on seen types removed (proper distribution)."""

    def __init__(self, words, char_model):
        super().__init__(words, char_model)
        self.seen_mass = sum(2 ** char_model.logp_word(w) for w in self.c)
        self.log_renorm = -math.log2(1.0 - self.seen_mass)

    def logp_word(self, w):
        lp = super().logp_word(w)
        return lp if w in self.c else lp + self.log_renorm


def build_models(train, d2_alpha=None):
    m3 = M.CharMarkov(train, 3)
    out = {
        "unigram-GT+char3WB": M.UnigramGT(train, m3),
        "unigram-GT-renorm": UnigramGTRenorm(train, m3),
        "unigram-flatUNK(a=0.1)": UnigramFlatUNK(train, 0.1),
        "char3-WB": m3,
        "char3-add0.01": CharAdditive(train, 0.01),
    }
    if d2_alpha is not None:
        out["char3-add0.1 (d2 repro)"] = CharAdditive(train, 0.1)
    return out


MODELS = ["unigram-GT+char3WB", "unigram-GT-renorm", "unigram-flatUNK(a=0.1)", "char3-WB", "char3-add0.01"]


# ---------------------------------------------------------------- scoring
def score_folds(pages, folds, extra_d2=False):
    """folds: list of lists of page indices (test sets).  Returns per-model accumulators."""
    names = MODELS + (["char3-add0.1 (d2 repro)"] if extra_d2 else [])
    acc = {m: dict(bits=0.0, tok=0, ch=0, seen_bits=0.0, seen=0, un_bits=0.0, un=0) for m in names}
    for fold in folds:
        test = set(fold)
        train = M.flat_tokens([p for i, p in enumerate(pages) if i not in test])
        tt = M.flat_tokens([pages[i] for i in fold])
        if not train or not tt:
            continue
        tr_types = set(train)
        models = build_models(train, d2_alpha=0.1 if extra_d2 else None)
        for w in tt:
            seen = w in tr_types
            for m in names:
                lp = models[m].logp_word(w)
                a = acc[m]
                a["bits"] -= lp; a["tok"] += 1; a["ch"] += len(w) + 1
                if seen:
                    a["seen_bits"] -= lp; a["seen"] += 1
                else:
                    a["un_bits"] -= lp; a["un"] += 1
    return acc


def page_split(pages, seed):
    idx = list(range(len(pages)))
    random.Random(seed).shuffle(idx)
    n_tr = int(round(0.8 * len(idx)))
    return [idx[n_tr:]]


def d2_exact_split(pages):
    """Reproduce d2: pages sorted by id, random.Random(42).shuffle, 80/20 (test = tail)."""
    ids = sorted(p["id"] for p in pages)
    rng = random.Random(42); rng.shuffle(ids)
    n_tr = int(round(0.8 * len(ids)))
    te = set(ids[n_tr:])
    return [[i for i, p in enumerate(pages) if p["id"] in te]]


def table(title, rows):
    emit(f"--- {title} ---")
    emit(f"{'split':<8} {'model':<26} {'bits/tok':>9} {'bits/char':>10} {'seen':>8} {'unseen':>8} {'unseen%':>8} {'n_tok':>7}")
    for split, acc in rows:
        for m, a in acc.items():
            if not a["tok"]:
                continue
            emit(f"{split:<8} {m:<26} {a['bits']/a['tok']:9.3f} {a['bits']/a['ch']:10.3f} "
                 f"{a['seen_bits']/max(a['seen'],1):8.3f} {a['un_bits']/max(a['un'],1):8.3f} "
                 f"{100*a['un']/a['tok']:8.1f} {a['tok']:7d}")
    emit()


def main():
    emit(f"M3 bake-off reconciliation  run={datetime.now().isoformat(timespec='seconds')}  seed={SEED}")
    emit(__doc__.strip())
    emit()
    voy = M.voynich_pages("eva")
    ita = M.wordlist_pages(corpora.control("italian_dante", 25000), 8, 20, ["s1", "s2", "s3", "s4"])
    emit(f"voynich pages={len(voy)} tokens={len(M.flat_tokens(voy))} | italian pages={len(ita)} tokens={len(M.flat_tokens(ita))}")
    emit()

    # reproduction of d2 exact numbers
    emit("REPRODUCTION of d2 (its split: seed 42, pages sorted by id; its models alpha=0.1):")
    rep = score_folds(voy, d2_exact_split(voy), extra_d2=True)
    emit(f"  d2 published: word-unigram 10.728 (seen 9.469 / unseen 18.101), char-trigram 11.279 (9.776 / 20.087)")
    for m in ("unigram-flatUNK(a=0.1)", "char3-add0.1 (d2 repro)"):
        a = rep[m]
        emit(f"  here        : {m:<26} {a['bits']/a['tok']:.3f} (seen {a['seen_bits']/a['seen']:.3f} / unseen {a['un_bits']/a['un']:.3f})  unseen tokens {a['un']}/{a['tok']}")
    emit(f"  m0 published (quire): markov3 11.556, markov2 11.581, unigram_gt 12.082")
    emit()

    results = {}
    for cname, pages in (("voynich_eva", voy), ("italian_dante", ita)):
        rows = []
        folds_page = page_split(pages, SEED)
        rows.append(("page", score_folds(pages, folds_page)))
        folds_q = M._folds(pages)
        rows.append(("quire" if pages[0].get("quire") else "block10", score_folds(pages, folds_q)))
        results[cname] = rows
        table(f"{cname}: {{page split (seed {SEED}, 80/20), {rows[1][0]} split ({len(folds_q)} folds)}} x 5 models", rows)

    # verdict
    emit("=== VERDICT: does 'spelling (char-3) beats vocabulary list (unigram)' hold on Voynich? ===")
    for split, acc in results["voynich_eva"]:
        gt = acc["unigram-GT+char3WB"]["bits"] / acc["unigram-GT+char3WB"]["tok"]
        rn = acc["unigram-GT-renorm"]["bits"] / acc["unigram-GT-renorm"]["tok"]
        fl = acc["unigram-flatUNK(a=0.1)"]["bits"] / acc["unigram-flatUNK(a=0.1)"]["tok"]
        wb = acc["char3-WB"]["bits"] / acc["char3-WB"]["tok"]
        ad = acc["char3-add0.01"]["bits"] / acc["char3-add0.01"]["tok"]
        emit(f"  [{split}] proper distributions: char3-WB {wb:.3f} vs unigram-GT {gt:.3f} -> "
             f"{'char3 wins' if wb < gt else 'unigram wins'} by {abs(wb-gt):.3f}; "
             f"char3-add0.01 {ad:.3f} vs unigram-GT -> {'char3 wins' if ad < gt else 'unigram wins'}; "
             f"RENORMALISED unigram-GT {rn:.3f} vs char3-WB -> {'char3 wins' if wb < rn else 'unigram wins'} by {abs(wb-rn):.3f}; "
             f"flat-UNK unigram {fl:.3f} ({'beats' if fl < wb else 'loses to'} char3-WB, but is not normalised over strings)")
    for split, acc in results["italian_dante"]:
        gt = acc["unigram-GT+char3WB"]["bits"] / acc["unigram-GT+char3WB"]["tok"]
        rn = acc["unigram-GT-renorm"]["bits"] / acc["unigram-GT-renorm"]["tok"]
        wb = acc["char3-WB"]["bits"] / acc["char3-WB"]["tok"]
        emit(f"  [italian {split}] char3-WB {wb:.3f} vs unigram-GT {gt:.3f} / renorm {rn:.3f} -> {'char3 wins' if wb < rn else 'unigram wins'}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    emit(f"wrote {OUT}")


if __name__ == "__main__":
    main()
