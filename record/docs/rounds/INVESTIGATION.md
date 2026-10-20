> Current map: [TEAM-HANDOFF.md](TEAM-HANDOFF.md). This file is the literature survey from before the local scoreboard.

# How close has anyone gotten to cracking the Voynich manuscript — and why not closer?

Multi-agent investigation filed: 2026-10-17 15:11 (system clock).
Method: 6 parallel researchers (classic cryptanalysis, linguistic claims,
statistical studies, hoax/generation, recent consensus, local positioning)
+ adversarial critic + synthesis. Each was required to open every cited
source. Status: **partial** — see Gaps. Rankings below rest on the opened
evidence in the agents' notes; unopened/paywalled primaries are flagged.

## Top finding

**Nobody is close to a decipherment. The closest durable ground is purely
negative**: Currier's A/B partition, Friedman-era transliteration
infrastructure, and Tiltman/Bennett constraints (low conditional character
entropy, re-measured by Lindemann & Bowern across 294 languages). Every later
claim must satisfy those constraints, and none has converted them into a key,
a language, a crib, or a reading. A century of work has narrowed what the
text *cannot* be, without identifying what it *is*.

## Ranked closeness

### 1. Closest: the negative constraints (Currier / Friedman / Tiltman / Bennett)

Verifiable, reproducible, and still load-bearing: the A/B statistical split,
shared transliterations enabling replication, and the demonstration that the
text is not a standard period cipher and not plain substitution. Why it is
not a crack: it excludes mechanisms; it identifies none. All claimed readings
from that era (Newbold, Feely, Strong, Brumbaugh) gained zero verifiable
ground — excess degrees of freedom (anagramming, multi-valued signs,
subjective word selection) made outputs non-reproducible until Manly and
Tiltman applied reproducibility tests.

### 2. Second: statistical language-likeness (Montemurro & Zanette; Amancio et al., PLOS ONE 2013; topic modelling)

Gained: Zipfian frequencies, long-range clustering of putative content
words, section-linked co-occurrence networks mostly inside the
natural-language range; vocabulary tracks illustrated subjects and scribal
hands. This proves the text is not random or shuffled gibberish. Why it
stalls: "compatible with natural language" is many-to-one — meaningless
generators produce the same signatures; the same batteries failed to identify
even known English/Portuguese controls; and word-level language-likeness
coexists with character-level entropy far below every natural text sampled.
Statistics yield candidate clusters, never a lexicon or a falsifiable reading.

### 3. Third: generation models (Timm & Schinner self-citation, ahead of Rugg's grille)

Gained: a medieval-plausible mechanism reproducing both Zipf laws, binomial
word lengths, low conditional entropy, and adjacent-word similarity — killing
the naive inference "nonrandom, therefore meaningful." Why it stalls: word
structure is built in by construction; no generator has jointly demonstrated
line/paragraph position and gallows effects, Currier A/B plus hand structure,
and long-range section-topic specificity; human gibberish (Gaskell & Bowern)
fails one word-internal position metric. Hoax is a viable null that cancels
#2, not a proven origin.

### Debunked (zero verifiable ground)

Newbold, Feely, Strong, Brumbaugh; Bax (2014, explicitly provisional —
closest to honest, still unverified and unextended), Gibbs (2017, press-led),
Cheshire (2019, retracted publicity), Tucker & Talbert (botanical
identifications only, no text decipherment); Hauer & Kondrak / Alberta Hebrew
(method paper, authors admit no readable text) and subsequent LLM/ChatGPT
claims (no readable page; confirmation depends on prompt phrasing). The
repeating failure pattern: guess isolated labels from nearby pictures, hunt
dictionaries for fits, allow anagramming/spelling freedom/many-to-many
mappings — then fail the blind fixed-key test on unseen continuous text.

## What the field would now accept as proof

1. A fixed published key + identified language, applied mechanically by
   independents to read long continuous text (one formulation: ten
   consecutive pages with consistent grammar and semantics).
2. Manuscript-wide coverage: same system across Currier A/B, all hands and
   sections, labels matching illustrations, no per-page re-tuning.
3. Early-15th-century plausibility, and controls: the key must fail on
   shuffled Voynich, gibberish corpora, and arbitrary languages.
4. Held-out-folio prediction, shared transliteration/code/data, peer review,
   historical-language expert sign-off.

No 2020–2026 neural or LLM claim in the opened evidence meets this standard.

## Where the local battery sits

The workflow's local-positioning agent returned no complete evidence, so this
section is the parent session's verified summary, not a workflow finding.
Local work (`FINDINGS.md`, `README.md` a1–a7, `DOCX_REVIEW.md` B1) replicates
the #1 constraints independently (h2 ≈ 2.13 vs 3.11–3.30 controls; solver
positive controls at 100% with Voynich at wrong-language levels), strengthens
#3 slightly (column-aligned copying excess ~1.9 pp, B1), and verifies
section signatures the literature asserts. It does not advance past #1–#3:
no joint position + A/B + topic test has been run locally either. That joint,
pre-registered, blind test — against self-citation, intuitive-gibberish, and
shuffled controls — is the highest-value next step, locally and in the field.

## Gaps and limits (preserved from the workflow)

- Five researcher scopes returned `complete:false` at the structured-evidence
  layer (paywalled primaries: Landini 2001, Rugg & Taylor 2017, Timm &
  Schinner 2020 publisher versions; NSA D'Imperio PDF 403; two PDFs fetched
  as binary without text inspection). Their substantive findings survive in
  agent notes from opened secondaries, full-text PLOS ONE, arXiv preprints,
  and Crossref records — but any claim resting only on a paywalled primary
  should be treated as **unverified** until opened.
- The synthesis agent flagged itself incomplete and the critic slot as
  unavailable at the envelope layer, although a critic note was delivered:
  no debunked reading was found over-claimed in the evidence bodies;
  overstatement risk concentrates in press/synthesis framing.
- One secondary audit used for the proof standard (Carvalho, Sept 2026,
  80 experiments) is explicitly non-peer-reviewed and not consensus alone.
- Local positioning via workflow: missing (see parent summary above).

What would refute the ranking: an opened primary showing a fixed-key blind
reading, a generator jointly matching position + A/B + topic metrics, or a
statistical battery that identifies known-language controls and then singles
out one language for Voynich. None was found in the opened evidence.
