> Current map: [TEAM-HANDOFF.md](TEAM-HANDOFF.md). This file is an earlier battery. It does not include the scoreboard, the G round, or H1.

# Voynich manuscript — a serious crack attempt (focused battery)

Run date (from system clock): 2026-10-17
Code: `analyze.py` + existing `vparse.py` (stdlib only, seed 20261017)
Data: `data/ZL3b-n.txt` — ZL IVTFF EVA transliteration, version 3b
(header inside the file). Analysis uses running paragraph text (units `P*`):
34,857 tokens, 7,025 types. Labels, circles, and radii are excluded.

## Bottom line

**The manuscript was not cracked. One major hypothesis was cleanly falsified,
and three remain standing.** Plain monoalphabetic substitution (one EVA
character = one cipher letter over English-like plaintext) fails against a
solver proven to work on a known cipher. What survives: (a) an unknown natural
language in an invented script, (b) a verbose/homophonic encoding where EVA
characters are not 1-to-1 with plaintext letters, or (c) templated generated
pseudo-text. This battery cannot separate (a)–(c); §5 names the tests that can.

Every number below was measured in this run (`results/results.json`,
`results/summary.md`). Literature values are not quoted as facts.

## 1. Method: controls first, claims second

Each statistic was computed on five corpora:

| Corpus | Purpose |
|---|---|
| Voynich paragraphs | The target |
| English workspace docs (1,174 tokens) | Known natural language (small — see limits) |
| Same English, monoalphabetically enciphered | **Positive control**: cipher tests must flag it |
| Voynich, word order shuffled | Destroys syntax, keeps vocabulary |
| Voynich Markov-1 pseudo-words | Keeps char bigrams, destroys real words |

What would refute this design: a control behaving like the target on a test
claimed as distinctive. That happened twice (Zipf, edit-neighbors) — both
claims were downgraded accordingly. Checked: yes, in this run.

## 2. The crack attempt: simple substitution

A hill-climbing solver searched for the injective EVA→English letter mapping
maximizing English within-word bigram log-probability (higher = more
English-like), 6 restarts × 3,000 swaps:

| Text | Score / bigram |
|---|---|
| English (identity mapping) | −2.2607 |
| Enciphered English (solved blind) | −2.2541 |
| Voynich (best mapping found) | −2.4817 |

The solver recovered the control plaintext essentially perfectly
("python projects root navigation topic existing entry point scope …"), so
the method works when a simple substitution is really there. The best Voynich
decoding is gibberish ("gkarob odkn kx kpkssu bren brexo …") and scores
0.22 nats/bigram worse despite the optimizer overfitting 25 free mappings.

**Verdict: falsified** — under two explicit assumptions: EVA characters map
1-to-1 to cipher symbols, and plaintext letter-bigrams resemble English.
Other plaintext languages and non-1-to-1 encodings are *not* touched by this
test (see §5).

Corroborating cipher evidence:

- Char index of coincidence: Voynich 0.0766 vs English 0.0628. Substitution
  preserves IC (verified: control IC identical before/after enciphering);
  polyalphabetic ciphers depress it. Voynich's *high* IC argues against
  Vigenère-style flattening.
- Char conditional entropy H1: Voynich 2.32 bits vs English 3.52 bits vs
  Markov-1 pseudo-Voynich 2.71 bits. Voynich characters are far more
  predictable than English letters — and more predictable than its own
  bigram model predicts, implying structure beyond adjacent pairs
  (word templates/positions, §3).

## 3. What Voynich text actually looks like

- **Zipf-like, but that proves little.** Word-frequency slope −0.94,
  R² = 0.97 — language-like. However Markov-1 gibberish also fits
  (R² = 0.99). Zipf compliance is necessary-ish, nowhere near sufficient.
- **Crowded vocabulary.** 86% of sampled word types have an edit-distance-1
  neighbor (mean 7.4 neighbors) vs 27% (mean 0.5) for English. Striking —
  but Markov-1 matches it (80%, mean 7.5), so crowding follows from a small
  set of allowed char combinations, not necessarily from meaning.
- **Strong word templates.** Prefixes `ch-` (5,619), `qo-` (5,192), `sh-`
  (3,056) and suffixes `-edy` (4,018), `-iin` (3,974) dominate. Last-character
  entropy (2.32 bits) is well below first-character entropy (3.10 bits):
  word endings are heavily constrained, like inflection — or like a template.
- **Layout leaks into letters.** Line-initial words start with a gallows
  char (EVA k/t/p/f) 21.9% of the time vs 6.2% elsewhere (4,130 lines).
  A letter-for-letter cipher of ordinary prose has no mechanism to produce
  a line-position effect this size; scribal/generative processes do.
- **Weak phrase structure.** Most frequent word trigram occurs only 5 times
  in 34,857 tokens; adjacent doubles 0.84% (294). Word-order shuffling costs
  only ~0.18 bits of conditional entropy (4.43 → 4.61): knowing the previous
  word helps surprisingly little.
- **Currier A/B is real.** Char Jensen–Shannon divergence A-vs-B = 0.0168
  bits vs 0.00019 between random halves of B (~88×). Vocabulary Jaccard
  overlap is just 0.159. Frequent B-only words include `qokeedy` (307×),
  while all top-50 A words occur at least once in B — the split looks like
  dialect/register shift on shared foundations, not two unrelated systems.

## 4. Hypothesis scoreboard

| Hypothesis | Prediction | Observed | Verdict |
|---|---|---|---|
| Monoalphabetic substitution, English-like plaintext | Solver ≈ English score, readable output | −2.48 vs −2.25; gibberish; control solved perfectly | **Falsified** (assumptions in §2) |
| Polyalphabetic (Vigenère-like) cipher | Depressed IC | IC 0.0766, above English | **Disfavored** |
| Random/meaningless scribble | Flat stats, no positional structure | Templates, gallows effect, A/B split, Zipf fit | **Falsified** |
| Unknown natural language, invented script | Language-like stats, no simple-cipher solution | Consistent with everything above | **Standing** |
| Verbose/homophonic encoding (EVA ≠ 1-to-1) | Low char entropy, templates, solver failure | Consistent | **Standing** |
| Templated generated pseudo-text (e.g. grille/self-citation) | Crowded vocab, weak word-order info, positional effects | Consistent; Markov control mimics several traits | **Standing** |

> These five items were the queue when this file was written. Later result files cover them. The queue is `TEAM-HANDOFF.md`.

## 5. Next discriminating tests (in order)

1. **Digraph-aware re-run.** Collapse EVA `ch`, `sh`, `ee`, `qo` etc. into
   single symbols and repeat §2. If EVA splits single glyphs, the current
   falsification has a loophole; this closes or confirms it.
2. **Multi-language scorers.** Repeat the solver with Latin, medieval German,
   Italian, and romanized Hebrew bigram/trigram models from large corpora.
   A real plaintext language should spike on exactly one scorer.
3. **Homophonic solver.** Allow many-to-one mappings (several EVA symbols →
   one plaintext letter) with simulated annealing. This directly tests (b).
4. **Generative-model bake-off.** Fit (i) a word-template generator and
   (ii) a self-citation/grille simulator; compare held-out likelihood and the
   §3 diagnostics against real text. This tests (c) against (a)/(b).
5. **Section-wise analysis.** Repeat profiles by illustration type (herbal,
   biological, stars…) and hand. Genuine language about different topics
   should shift vocabulary like topic shift; pure generation should not.

## 6. Limits — read before citing

- EVA is a transliteration alphabet, not the glyphs themselves; every
  char-level result inherits transliterator choices (`vparse.py` takes first
  readings of `[a:b]` alternatives and treats uncertain spaces as breaks).
- The English control is only 1,174 tokens of repetitive technical docs.
  Char-level comparisons are usable; word-level entropy/TTR comparisons
  against it are indicative only. §5.2 needs proper period corpora.
- The substitution test falsifies one cipher family under stated assumptions.
  It does not, and cannot, show the text is meaningless.
- Single transliteration (ZL 3b), paragraphs only. Labels/diagrams may behave
  differently.

## Reproduce

```powershell
cd voynich
uv run python analyze.py
uv run python -m unittest discover -s tests -v
```

Outputs: `results/results.json` (full machine-readable detail),
`results/summary.md` (comparison table). Five invariant tests pass,
including "solver recovers a known cipher" and "substitution preserves IC".

## Concurrent work notice

During this run, additional files appeared in this folder from parallel work
(`a1_profile.py`–`a5_verbose.py`, `corpora.py`, `data/controls/*.txt` with
Latin/German/Italian/English texts, `results_a*.txt`). They were not created
or used by this battery, were left untouched, and are unverified here.
Integrating them — especially the period corpora for §5.2 — is the obvious
next step.
