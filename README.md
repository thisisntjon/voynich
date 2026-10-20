# Voynich manuscript research record

*Snapshot of 2026-10-19. Research paused; handed over so that others, human or AI, can check it and go further.*

**What this is.** The full working record of an investigation of the Voynich manuscript (Yale, Beinecke MS 408) by a small team of AI research agents directed by one person, Jon, at Simone Systems Research: 205 analysis scripts at the root, 96 run folders, 619 results files, and the registers that tie every cited number to its results file.

**It is not deciphered.** Nothing here reads the manuscript, names its language or says what it means. No result is evidence of meaning; every finding is about how the text is built, not what it says.

**What was found.** 51 tested structural findings about how the text is built (how words, lines and pages behave), each graded by how many independent kinds of check agree: 17 triangulated, 14 corroborated, 15 single-line, 5 contested. Most extend published work; 8 have no published precedent we know of, and 3 re-find a published result.

**What was ruled out.** Of the 20 explanations considered, most (letter ciphers, verbose and table ciphers, generators as built, free gibberish, independent streams, artefacts of layout or transcription) were tested and are excluded or disfavoured in the forms tested. That list of dead ends is probably the most useful thing here: see `DEAD-ENDS.md`.

**What it means, in plain words.** The text is not random: words, lines and pages follow regular habits, such as word lengths that rise and fall together inside a line and vocabulary that shifts between sections and scribes. Several of these habits are also found in ordinary metrical verse, so they do not rule out a natural language written as verse; they do rule out many simple ciphers and generators, in the forms tested. Nothing found here says what the words mean, which language (if any) lies underneath, or whether the book is a hoax. The record's value is a map of what has been checked, how firmly, and what not to try again.

**How to check it.** Every number has a claim id (`c-NNN`) pointing to a results file; the transliterations are fetched and checked by sha256; scripts rerun to the same output (five commands below).

## Start here

| You are | Read |
|---|---|
| Curious about the manuscript | This page, then `FINDINGS.md` (plain titles and limits), then `DEAD-ENDS.md`. Terms are in `GLOSSARY.md`. |
| A Voynich researcher | `FINDINGS.md` (each finding with its novelty against published work and its evidence), `DEAD-ENDS.md`, then `OPEN-QUESTIONS.md`. Rerun anything with the commands below. |
| An AI agent continuing the work | `CONTINUING.md` (how to work here alone), then `OPEN-QUESTIONS.md`, then the source-of-truth map below. |

## Strongest result

**F-04: Word lengths follow a rhythm inside lines that stops at line breaks** (TRIANGULATED).

- Why: 5 agreeing axes (data, impl, method, order, split), does not rest on the at-risk slot-unit assumption X-01, replicated by Daybreak (exact, c-320), roach r3 (own code, held-out pages, c-414) and roach r12 blind (c-456); the ink-gap measurement has the same sign but fails its pre-set band (c-360), so it does not count as agreeing
- Limits: Structural only: says nothing about meaning. Not unique: Kalevala metrical verse shows the same within-line rhythm on 15/15 blocks (c-456), so ordinary metrical line-filling is a live explanation. Not a first-ever result: Gaskell and Bowern 2022 measured word-length autocorrelation (flattened); the within-line vs cross-line split is unverified against the wider literature. One line (Voynich Ninja external) is unverified.
- Evidence: CLAIMS c-320, c-360, c-414, c-456; runs/roach-r3/results_r3.txt; results_s45.txt; FINDINGS-MAP section 7 F-04

## Headline findings

Standing findings that reach TRIANGULATED or CORROBORATED and rest on no at-risk assumption. All of them, with limits and evidence, are in `FINDINGS.md`.

Axes are the independent kinds of check that agree: `data` another transliteration, `seg` another word-splitting method, `split` held-out pages or quires (LOQO = leave one quire out), `method` a different statistic, `impl` code written independently, `physical` measured from scan ink, `external` published by others, `order` survives changes of reading order. Other terms (cores, h2, POST-HOC, run ids, agent names) are in `GLOSSARY.md`.

| id | finding | grade | agreeing axes | axes if each run counts once | novelty |
|---|---|---|---|---|---|
| [F-01](FINDINGS.md#f-01) | Lines are units of the text | TRIANGULATED | data, impl, method, order, physical | 5 | extends |
| [F-03](FINDINGS.md#f-03) | Cross-space coupling is adjacent ordering, strongest in Currier B, and cheap to make | TRIANGULATED | data, external, impl | 3 | extends |
| [F-04](FINDINGS.md#f-04) | Word lengths follow a rhythm inside lines that stops at line breaks | TRIANGULATED | data, impl, method, order, split | 5 | extends |
| [F-05](FINDINGS.md#f-05) | Characters predict the text better than its word list does | CORROBORATED | data, method | 2 | extends |
| [F-06](FINDINGS.md#f-06) | Cores carry held-out word-order structure (restated; the 'affixes carry none' half withdrawn by r5) | TRIANGULATED | data, impl, method, split | 3 | extends |
| [F-07](FINDINGS.md#f-07) | Hand-1 section vocabulary beats the generator and a bifolio null at the permutation floor, consistent with Schwartz 2026's weak section tint | TRIANGULATED | data, impl, split | 3 | extends |
| [F-08](FINDINGS.md#f-08) | The edge and coupling anomalies are not alphabet or boundary artefacts; entropy and type counts are | CORROBORATED | method, seg | 2 | extends |
| [F-15](FINDINGS.md#f-15) | Prefix and suffix are chosen together with the core | TRIANGULATED | impl, method, seg, split | 3 | extends |
| [F-16](FINDINGS.md#f-16) | Currier A/B coincides with Davis's scribe split; within B, the Hand 2 vs Hand 3 slot divergence is section | CORROBORATED | method, split | 2 | extends |
| [F-17](FINDINGS.md#f-17) | Quire M (the sole Biological quire) uses a 1.43-1.47x narrower vocabulary than token-matched global draws; the other 14 quires do not | TRIANGULATED | data, impl, seg, split | 3 | extends |
| [F-19](FINDINGS.md#f-19) | Transliterated spaces are physical ink gaps (kappa 0.87); commas are intermediate gaps | TRIANGULATED | data, method, physical | 2 | extends |
| [F-20](FINDINGS.md#f-20) | Tested plant-label and repeated-label cribs show no supported text link | CORROBORATED | external, method | 2 | new |
| [F-22](FINDINGS.md#f-22) | New rare cores are only weakly edited from nearby forms, and many are segmenter boundary shifts | CORROBORATED | physical, split | 2 | extends |
| [F-24](FINDINGS.md#f-24) | The per-word random-table cipher leaves the prefix stream orderless | CORROBORATED | data, method, split | 2 | extends |
| [F-25](FINDINGS.md#f-25) | Plain letter-in-core and verbose-homophonic ciphers reach the weak core order but miss h2, rhythm and prefix memory | CORROBORATED | data, method | 2 | extends |
| [F-28](FINDINGS.md#f-28) | No antidotary, alphabetical or zodiac order | TRIANGULATED | data, external, impl, method | 2 | new |
| [F-32](FINDINGS.md#f-32) | Page drift and cross-page carryover depend on the bound page order, mostly within quires | CORROBORATED | data, order | 1 | extends |
| [F-33](FINDINGS.md#f-33) | No strong link between plant pictures and core vocabulary; affix frames associate with pictures | CORROBORATED | data, physical | 1 | extends |
| [F-45](FINDINGS.md#f-45) | Period-documented ciphers over period recipe texts do not reproduce the manuscript; low h2, positive length rhythm and in-line reuse must come from the encoding itself | CORROBORATED | data, method | 1 | extends |
| [F-47](FINDINGS.md#f-47) | Spec-built verbose table encodings of real recipe text fail; shuffled input fits the line rhythm better than real word order | CORROBORATED | data, method | 1 | extends |

## Hypothesis scoreboard

Weights are computed from the findings that bear on each hypothesis (strength x grade, halved when the finding rests on an at-risk assumption; the same computation as section 1 of `workflow/FINDINGS-MAP.md`). They summarise this project's evidence only. The status column is the project's judgement and also reflects failed tests that are not encoded as finding links (for example, H-05's weakened grille failed held-out quires 0/15), so a weight for can sit beside a weakened status.

| id | explanation | status | weight for | weight against |
|---|---|---|---|---|
| H-01 | Natural language written plainly (any known language) | disfavoured | 0.0 | 13.3 |
| H-02 | Letter-level cipher with plaintext letters carried in the cores | disfavoured again on the corrected statistic (s82 h2/rhythm, s83 too much core order) | 0.0 | 5.2 |
| H-03 | Verbose homophonic cipher: plaintext in the affixes, filler cores | disfavoured as built | 0.0 | 2.7 |
| H-04 | Per-word random-table cipher (Naibbe); per-line or sticky variant open | excluded at default settings | 0.0 | 3.5 |
| H-05 | Table-and-grille style procedure applied word by word within a line (Rugg family) | weakened: weakened grille fails LOQO 0/15 (s71) | 3.0 | 0.0 |
| H-06 | Word-level lexical system: cores are vocabulary (code, nomenclator or list-like content) | live | 2.0 | 2.7 |
| H-07 | Self-citation / local-memory generator (Timm and Schinner family) | disfavoured as built | 1.0 | 5.3 |
| H-08 | Free human gibberish or glossolalia | disfavoured | 0.0 | 3.8 |
| H-09 | Superimposed independent streams (music, glyph classes) | excluded | 0.0 | 4.0 |
| H-10 | Liturgy or charms, copying without understanding, historical conlangs | excluded as tested | 0.0 | 1.0 |
| H-11 | Structure is an artefact of layout, drawings, transcription or alphabet | excluded | 0.0 | 8.0 |
| H-12 | Antidotary, alphabetical or zodiac-ordered content | excluded as tested | 0.0 | 3.0 |
| H-13 | Currier A and B are two languages or dialects (rather than two scribes) | weakened, confounded | 0.0 | 1.3 |
| H-14 | Table cipher whose affix table is held for a line (sticky Naibbe family): carries plaintext | narrowed (D-067): a fixed line-held table is contested by roach r6 and s98; a drifting table failed 0/15 (r9, L-217); what remains is a multi-scale state (D-067 amended) | 1.0 | 5.3 |
| H-15 | Transposition cipher or null-glyph insertion over a plain text | disfavoured within tested scope (s75) | 0.0 | 0.3 |
| H-16 | Practitioner notation, shorthand or mnemonic manual: cores stand for ingredients, operations or categories a trained reader knew (red-team 2026-10-18; Sylvie guess 3) | weakened, thin evidence (s97: constructed sigla control fails; no real shorthand text tested) | 0.0 | 0.0 |
| H-17 | A natural language written in an invented verbose script with heavy abbreviation or misleading word boundaries (red-team 2026-10-18; Sylvie guess 4) | weakened (s97): abbreviated, abjad and verbose-orthography controls fail; a line-held spelling-variant scheme gives in-line reuse but not order or locality | 0.0 | 1.0 |
| H-18 | A private category-based constructed or esoteric language (philosophical-language style) (red-team 2026-10-18; Sylvie guess 5) | live, untested; needs a falsifiable prediction | 0.0 | 0.0 |
| H-19 | The text is written from a combinatory or permutation table (Llull-style letter cells repeated across columns), with or without content (s107 2026-10-18) | live; one 957-token OCR example shows in-line reuse; needs a full-size test and a construction from such a table against the joint profile | 0.0 | 0.0 |
| H-20 | The pictures form one programme on plant life: cosmic influence, the plant's inner workings (biological section as medieval plant physiology / vegetative soul, Taiz & Taiz 2011), and plant parts as medicine (Panofsky 1954 via D'Imperio 1978) | live, untested (subject-matter hypothesis; says nothing about the text mechanism) | 0.0 | 0.0 |

## Limits of this work

- **Who checked it.** Every run, audit and replication was done by AI agents inside the project. No outside researcher has reviewed it. "Independent" replications (the `impl` axis) are by other agents on the same team, writing their own code.
- **Counting checks.** A grade counts the kinds of check (axes) that agree, as filed. One run sometimes supplies two axes (for example, independent code on held-out pages counts as both `impl` and `split`); the headline table and `FINDINGS.md` also give the count when each run counts once. Some axes are weaker than their name suggests for a given statistic (a lag-1 statistic reads the same in either direction, so its `order` line is nearly automatic).
- **Edited scripts.** `tools/verify_stubs.py` finds 18 stub lines whose script was edited after it was pinned; the pinned original is kept beside it as `*.orig-<hash>`. Results from those scripts still appear in some evidence lines.
- **Pre-registration.** Designs were frozen by hash (`*.prereg.sha256`) by the same agents, often minutes before the real run. 79 of 238 evidence lines are flagged POST-HOC or unverified (a results file was overwritten after its stub was re-stamped, or the line was never re-frozen) and do not count toward any grade.
- **Multiple testing.** About 96 run folders, 205 root scripts and 157 pre-registration stubs tested many statistics. The registers describe no correction for multiple testing across the project as a whole (no family-wise or false-discovery control); individual runs set their own thresholds and nulls. Treat single-run p-values near 0.05 as leads, not results, and the hypothesis weights as a summary, not a probability.
- **Shared data.** The three main transliterations (ZL3b, RF1b, IT2a) share the same scans and the EVA glyph set, so agreement across them is the weakest axis (`data`) and never counts as independence alone.
- **Segmentation.** 18 findings rest on assumption X-01 (that the automatic prefix/core/suffix split gives the right units), which is at risk: no tested segmenter recovered planted books (c-592). Those findings are weighted half.
- **Prior work.** 40 of 51 findings extend published observations and 3 re-find them. "New" (8) means only that the project's own literature notes hold no precedent; several are null tests, and informal tries on forums (voynich.ninja, Zandbergen's pages) were not searched systematically.
- **Structure, not meaning.** No finding is evidence of what the text says.

## Where each kind of fact lives (source-of-truth map)

Edit only the canonical home; derived views are rebuilt from it. If a document and a results file disagree, the results file is right.

| Kind of fact | Canonical home | Derived views |
|---|---|---|
| Raw measurements | `results_*.txt` at the root and `runs/<id>/results*` (619 files; the record of each run. A results file overwritten after its stub was re-stamped is flagged POST-HOC and its lines do not count) | the numbers quoted everywhere else |
| Cited numbers | `.inventory/registers/CLAIMS.md` (582 claim rows, `c-NNN`, each with its source file) | |
| Findings, hypotheses, assumptions and their evidence lines | `workflow/FINDINGS-GRAPH.yaml` | `workflow/FINDINGS-MAP.md` (`python tools/findings_graph.py render --allow-missing`), `FINDINGS.md`, this page |
| What was learned, including failures | `.inventory/registers/LEARNINGS.md` (308 rows, theme index at the top) | `DEAD-ENDS.md` |
| Decisions, reversals and rejections | `.inventory/registers/DECISIONS.md` (88 rows; D-066 is the run log) | |
| Open questions and parked work | `.inventory/registers/OPEN.md` (86 rows) | `OPEN-QUESTIONS.md` |
| Methods, equations, thresholds | `.inventory/registers/METHODS.md`, `workflow/TRIANGULATION.md` (how results are graded and filed) | |
| Runs and who ran them | `runs/<id>/` and `TEAM-HANDOFF.md` | `ROOT-INDEX.md` |
| Pre-registrations | `*.prereg`, `*.prereg.sha256` | `python tools/verify_stubs.py` |
| Published per-page facts (who said what about each folio) | `data/page-facts/*.tsv` (sources and links; quotations removed) | |
| Third-party sources and licences | `data/SOURCES.tsv`, `data/FETCH.tsv` | `NEEDS.tsv` (what each script needs) |
| What is not here, and why | `WITHHELD.tsv`, `MISSING-EVIDENCE.tsv`, `START-HERE.md` | |

## Reproduce a result

```
pip install -r requirements-lock.txt   # Python 3.11; on 3.12 or newer use requirements-lock-py313.txt
python tools/fetch_data.py             # transliterations from voynich.nu, checked by sha256
python tools/build_translit.py         # rebuilds data/translit/*.meta.json byte for byte
python tools/restore_s45_text.py       # puts the transliteration back into the s45 page files
python s34_morphology_syntax_geography.py
git diff results_s34_morphology_syntax_geography.txt   # only the clock and run-time lines change
```

Other results files can also differ in lines that print a local path or a date; compare the numbers. Restoring the s45 text changes 171 tracked page files: do not commit them.

Rerun the strongest result (F-04): `python s21_moran_realline.py` (our run, results_s21.txt), then its independent replications: `python tools/roach_layout.py` (rebuilds roach's folder layout under `roach-root/` and downloads the Project Gutenberg, Hebrew Bible and CREMMA controls, each checked by sha256; run `tools/fetch_cremma.py` first for CREMMA) and the command in `runs/roach-r3/README.md` and `runs/roach-r12/README.md`, run from `roach-root/r3` and `roach-root/r12`.

`python tools/verify_stubs.py` checks every pre-registration stub; `START-HERE.md` has the full guide, what is withheld and why, and credits.

## Credit, licence and citation

Transliterations by René Zandbergen and Gabriel Landini, Takeshi Takahashi, Glen Claston, Prescott Currier and Mary D'Imperio, William Friedman's study group and Jorge Stolfi, all from https://www.voynich.nu/; manuscript images by Yale University's Beinecke Library. Full credits in `START-HERE.md`.

Code: MIT (`LICENSE`). Our text, results and data: CC BY 4.0 (`LICENSE-DATA.md`). Cite with `CITATION.cff`.
