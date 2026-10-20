# B — Prior art and the field's open questions (angle B)

Stamp: 2026-10-17 19:25 PDT (clock read with `date` at the end of the search session). Scope: read-only
except this file. Question: which of the project's candidate leads has the field already answered, which
tests does the current literature treat as decisive, and what did the project miss?

Local position read first: `.inventory/INDEX.md`, `.inventory/registers/OPEN.md`,
`.inventory/registers/REDTEAM.md` §2–3, `PLAN.md` §6, `data/external/README.md`, and the local paper texts
(Rozanova–Temerev 2608.17096, Parisel 2604.19762, Zattera CEUR 3313/10, Gaskell–Bowern 2022, Lindemann–Bowern
2021, Timm 2014, Schwartz 2026 preprint, the Naibbe forum thread) plus the six `research_notes/Voynich
decipherment attempts and failures/*.md`. Everything below marked **opened** was fetched and read in this
session (WebFetch summary or local text); **not opened** means a search snippet or a citation only.

Severity key for "what it changes": **closes** = the field has already answered this lead; **demotes** =
the lead stands but is replication, not novelty; **promotes** = the field has the same gap and the lead
would be new; **reframes** = the lead survives only with a different test.

---

## 1. Line-edge / paragraph-initial effects: who has what, and the missing real-manuscript control

**What the project claims as its own.** `results_m5_line_anatomy.txt` (INDEX "five things" #3): the
gallows/p effect is paragraph-initial (83 % of paragraph-first lines); ordinary line starts are a y/d/t/s
vocabulary profile; line ends draw from a small m/g set; 79 % of the first-glyph divergence survives
restricting to mid-line types. REDTEAM #3 says the project has zero real-manuscript line data.

**What the field already has (all opened unless noted):**

| Source | Finding | Overlap with m5 |
|---|---|---|
| Timm 2014, arXiv 1407.6639 (local text, lines 716–719, 803–805, 1216–1218, 1268–1288) | Paragraph-initial gallows in 617/716 paragraphs (86 %); p and f frequent in first lines and rare elsewhere; first-line words longer (5.45 vs ~4.9); 9.4 groups per first line | m5's paragraph-initial finding is a replication with a different count (83 % vs 86 %) |
| Rozanova–Temerev 2026, arXiv 2608.17096 §2.5, §3.6 (local text, lines 229–231, 536–551) | Line-initial JSD 0.528 for 717 paragraph-first lines vs 0.179 for 3,163 other lines; pooled 0.203; quire-bootstrap 95 % of the difference [0.31, 0.40]; p 24×, t 12×, f 5×, k 3× enriched on paragraph-first lines, "almost never y or d"; ordinary lines favour p, t and reverse sign for k, f, y, d; page-opening lines JSD 0.49. They cite Currier 1976, D'Imperio 1978, Vogt 2012, Feaster 2021, Steckley & Steckley 2024 as earlier quantifications | The two-population decomposition the project reports as m5's "what the edge effect actually is" is published, with a quire bootstrap the project lacks |
| Steckley & Steckley 2024, arXiv 2404.13069 (opened: https://arxiv.org/html/2404.13069v1) | 7,660 tokens, 1,223 lines, 95 folios (Scribe 1 herbal): line-final and before-drawing tokens ~7.5 % shorter; paragraph-top and line-initial ~10–12 % longer; token propensities at p ≤ 0.01, log(B) ≥ 5 per position; random cohorts show none. No manuscript control; mentions Gaskell–Bowern gibberish as possibly sharing the feature but does not test it | Drawings as an *extrinsic* boundary with their own propensities: the project has no "before/after drawing" position class at all |
| Feaster 2022, CEUR 3313 paper12 (opened via pdftotext) | "Rightwardness/downwardness" scores; glyph composition of a word constrained by line and paragraph position; **word-break combination anomalies [y.q] and [n.q] (Smith & Ponzi, Cryptologia 43.6, 2019) are partly positional**: n-final words sit at line starts and far right, where q-initial words rarely follow. Only real-text comparison: Virgil's Aeneid, [es] vs [ibus] midline rightwardness 0.399 (343 tokens) vs 0.708 (390), "as stark as any presented above". Favours no mechanism; offers "alternate homophone options by page area" as one cipher-side scenario | A direct attack on the project's second anomaly: part of the cross-space coupling may be line-position co-occurrence, which R&T's within-line shuffle also destroys, so R&T's "88–93 % destroyed by shuffling" does not separate ordering from position |
| Zandbergen 2021, arXiv 2104.12548 "The Cardan grille approach … taken to the next level" (not opened; cited by Feaster as calling p/f/cPh/cFh-in-first-lines "a prohibitive feature for a large number of proposed solutions") | — | The project's `rugg_grille` control may be superseded by Zandbergen's version; unverified |
| Vogt 2012, "The line as a functional unit" (not opened; URL https://voynichthoughts.files.wordpress.com/2012/11/the_voynich_line.pdf) | Second word of a line shorter than average (48 % shorter vs 32 % longer, per the Ninja summary) | m5 does not test second-word effects |
| voynich.ninja thread 4343 "Summary of Voynich Day presentation on Line Patterns" (tavie, 8 Aug 2024; opened: https://www.voynich.ninja/thread-4343.html) | Per scribe: all three avoid initial ch at line start (Herbal A: 64 observed vs ~300 expected) and favour y, d, s; line ends favour final m, avoid q/ch/sh; Scribe 1 favours o-/q- at line start, "da" at line end; **vertical effect**: o-o vertical pairs ~40 expected, rare; o-q surplus ~38; m-ending lines followed by q-starting lines 58 % of expectation. "Comparison with a real medieval manuscript: none." Explanations offered: stylistic, clash avoidance, marker glyphs, self-citation, nulls | Scribe-split line profiles exist informally; the project's m5 is pooled over hands except A/B |
| voynich.nu/writing.html (opened) | Straight left margin; in places the first characters of lines were written first as a column; last lines of paragraphs left-justified (17 pages centred, 11 right-justified, 5 "titles"); paragraph-initial set is "a very small subset"; no comparison with medieval line-filling | The "column written first" observation is a physical mechanism for line-initial vocabulary that no producer models |
| RN-Top/Voynich PR #5, merged 1 Oct 2026 (opened: https://github.com/RN-Top/Voynich/pull/5; LLM-generated, Claude Code commits) | Pre-registered: line-final -m/-am is half as frequent at paragraph ends (8.5 % vs 16.1 % of line-final tokens, p ≈ 1e-4), read as space-saving; **-am line-final odds ratio 22.9 in native lines, 1.8 after re-lining** the same words; Latin controls (Apicius, Albertanus, Bede) only for entropy (2.11 vs 3.2–3.4) | The only re-lining control found anywhere; it says the line-final effect is a property of the physical line, which is what a real-manuscript control would test. Not peer reviewed, not a manuscript control |

**Searches that found nothing** (standard then extended): "line-initial gallows real medieval manuscript
control 2025 2026"; "Lisa Fagin Davis 2025 2026 paragraph gallows"; "Voynich line-initial Latin manuscript
comparison line effects scribal line filling". No 2025–2026 paper compares Voynich line-edge statistics with
a real manuscript's lines. Both R&T (line 406: controls "match the Voynich line template") and Schwartz (line
227: comparison texts "cut to the manuscript's page and line lengths") use pseudo-lines, so the field's
"no prose control reaches the edge bands" is true by construction, exactly as REDTEAM #3 says of the project.

**What it changes.** m5 as a *finding* is **demoted** (replication of Timm 2014 / R&T §3.6 / Steckley 2024).
The real-manuscript line control is **promoted**: nobody in the literature has it, item 6 below supplies the
corpus, and the RN-Top re-lining result gives a cheap pre-test (re-line Voynich; see whether jsd_first and the
m/g line-end set collapse the way -am does). Feaster's positional account of [y.q]/[n.q] **reframes** the
cross-space coupling lead: the project needs a position-stratified null (shuffle tokens only among tokens at
the same line position) before calling the +0.18 coupling an ordering effect.

## 2. Habit generators and Schwartz's procedure against section/topic signals under quire or bifolio nulls

**Schwartz 2026 §5.4 (local text, lines 978–1040; opened).** He tests *the manuscript* for section tinting
with scribe and page order controlled, against within-scribe page shuffles, contiguous fake sections and
"fake sections aligned to the quires" because "sections, hands and binding are entangled [Clemens 2016]".
Result: only word choice survives, "roughly 0.2 to 0.3 bits per page", "least far outside the quire-aligned"
null; "with quire membership added to the conditioning the raw evidence gain turns negative"; the effect
comes from the astronomical and balneological sections and "the herbal section … shows no tint of its own";
it "weakens to marginal significance under the harshest controls (page damage, page length)". Seven channels
tried, one survivor. The label register is the other survivor (o-initial ~3/5 vs 1/3; 75 label types on more
than one page vs 85–111 expected).

**Did anyone score a generator's output on the section signal under quire nulls?** No. Schwartz's generator
reuses "the scribe's own vocabulary" per hand (line 1528 ff.), so it is section-seeded by construction and
he does not report scoring its output on his own section test. R&T use quire bootstraps for intervals and
leave-one-quire-out for BPE/entropy, not for a topic test. Gaskell & Bowern 2022 say their samples are "too
short to test whether the higher-level structure of VMS pages and quires could also be produced by
gibberish" (local text, abstract). No search hit for a word-pair habit generator outside this project.

**New codicology that bears on the null unit.** Layfield & Fagin Davis, "Singulion Structure and the Voynich
Manuscript", Digital Medievalist 19 (2026), full text 10 July 2026 (listing opened:
https://rmblf.be/2026/07/29/publication-digital-medievalist-19-2026/; article itself not opened). Press and
the Ninja thread (opened: https://www.voynich.ninja/printthread.php?tid=5896, 10–11 Jul 2026) say the bifolios
originally existed as separate "singletons" later nested, so page order is not original; Davis there: quire
marks were added at a later binding; only f76r (Q13) and f105r (Q20) begin with an enlarged glyph. Objections
(Grove): the Q9 and Q13 marks sit awkwardly with the proposed reorder.

**What it changes.** O-041 (hand-1 section NMI as the last content signal) is **reframed**: the field's
number for the same effect is 0.2–0.3 bits/page, restricted to astro/balneo, negative once quire is
conditioned on, and the herbal section carries none. The project's hand-1 margin (0.013 / 0.005 NMI) is
consistent with that and should be reported as "agrees with Schwartz's weak tint", not as an independent
content signal. O-004 (bifolio null) is **promoted**: Layfield & Davis make the bifolio, not the quire, the
production unit, and no generator has been scored under it. Scoring N2/N3 output on Schwartz's own
section-tint test under a bifolio null would be new.

## 3. State of the Naibbe debate

- Greshko 2025, Cryptologia doi 10.1080/01611194.2025.2566408 (open access; not opened — 403 to this tool,
  O-018 stands). Author's own concessions, via the Ninja thread (local `voynich_ninja_thread5081.txt` and
  page 2 opened: https://www.voynich.ninja/archive/index.php/thread-5081-2.html): no long-range correlations,
  no line-position effects, ~45 % of VMS word types generated and non-VMS types produced; tables filled with
  VMS words; ratios 5:2:2:2:1:1 fitted; cannot produce standalone s, l, o, r, d; Currier B only.
- Timm's critique (7–8 Dec 2025, same page): primary table α used 38.5 %, so the most common token likely
  reveals the plaintext letter ("the opposite of homophonic design goals"); 18 options per letter vs 2–4
  in attested 15th-century ciphers; **line-level structure "mathematically impossible" for a verbose
  cipher: ~38,000 tokens against 57,000–76,000 plaintext letters at 1.5–2 letters per token**; m at line end
  ~62 % (Timm 2014).
- Rozanova–Temerev 2026 §3.9, Table (local lines 690–698): Naibbe-of-Caesar hapax 41 % vs Voynich 70 %, edge
  information 0.006 vs 0.197 bits; the self-citation generator 59–60 % hapax; "neither reproduces the
  edge-glyph coupling or the open, hapax-rich vocabulary".
- Delgado, "Technical Rebuttal: Semantic Density and the 'Naibbe' Verbosity Constraint", Cryptologia
  ahead-of-print (announced 8 Sep 2026; thread opened: https://www.voynich.ninja/thread-6067.html). Toy
  model: positional sign, null, swap marker, abbreviation. Timm (10 Sep): abbreviation raises entropy,
  swaps are length-preserving, nulls lower density; "some cipher can be denser than Naibbe" but nothing
  shown to match the text. Greshko/magnesium (10 Sep): has the full text, "not much of a 'technical
  rebuttal'", toy model not quantitatively demonstrated; his own alphabetising-permutation test on
  Naturalis Historia did not reach Voynich entropy.
- Media coverage only (not opened): wildhunt.org Jan 2026, livescience, newsweek, sci.news. Zandbergen quoted
  as "valuable demonstration" that does not settle meaning.

**What it changes.** The project's stop-list entry "Naibbe as-is" **matches the field; closed**. The open
question the field states is the project's O-006 verbatim (edge coupling + hapax 0.68 inside the type
budget). Timm's token-count argument is a cheap quantitative check the project has not run: given h2 and
word-length, how many plaintext letters can 38k tokens carry, and is that enough for line-level structure
to be a plaintext property? It bounds the whole verbose-cipher family (F3, j, O-009), not just Naibbe.

## 4. Gaskell–Bowern gibberish corpus and line-edge metrics

- Corpus is on disk with **real line breaks** (checked: `danielgaskell-voynich-main/voynich-main/data/
  gibberish_transcriptions/Gibberish - DA_01.txt`, one written line per text line); the paper says
  transcriptions preserve line breaks (local text, line 97–102).
- G&B 2022 (local text, lines 142–190, 220–235) already score one line-position metric: `charbias_lines`
  (5-bin heat-map of character position within a line). Gibberish has **higher** charbias_mean than
  meaningful text; **the VMS is "not significantly different" from meaningful text on charbias_mean** — the
  one metric of 42 on which Voynich does not sit with gibberish. Also charbias_words_mean is the one metric
  on which VMS does not plausibly resemble gibberish.
- No one has scored the corpus on line-initial JSD, paragraph-first gallows, m/g line-end share or edge
  coupling: searches ("Gaskell Bowern gibberish line-initial line-final", standard) returned only the 2022
  papers and forum threads. Steckley 2024 raises the question and does not test it. Forum (thread 6147 #82,
  JoJo_Jost, 17 Oct 2026): the samples are "only 2–3 pages long".
- Bowern & Gaskell "Enciphered after all?" (local lingbuzz text) covers topic structure across ciphers,
  not lines.

**What it changes.** O-031 (score the 38 gibberish texts on the board) stays **promoted and cheap**, and it
now has a prior to beat: on the coarse charbias metric human gibberish is *more* line-biased than Voynich.
If the fine line-edge metrics agree (gibberish over-shoots jsd_first), the "line edges are vocabulary
habit" reading of m5 loses its best natural analogue; if gibberish lands near 0.176 it becomes the first
non-Voynich-fitted family to reach the edge band and the G-favoured verdict (REDTEAM #5) gets real support.

## 5. Statistical profile of 15th-century nomenclators and chancery ciphers

- **DECODE / DECRYPT (Megyesi et al.).** Database now lists 10,106 records, 6,396 keys, 3,692 ciphers
  (https://de-crypt.org/decrypt-web/RecordsList; not opened, counts from search snippet). Cryptologia 2022
  "Keys with nomenclatures in the early modern Europe" (doi 10.1080/01611194.2022.2113185; 403, not opened;
  >1,600 keys from 10 countries). Two open HistoCrypt papers opened via pdftotext:
  - *Key Design in the Early Modern Era in Europe* (2021, https://ecp.ep.liu.se/index.php/histocrypt/article/download/165/121): 700 keys structurally described. Plaintext entity sets run from "ca 20–30 entities" (alphabet) to "several hundred"; **72 % of keys contain over 100 plaintext entities** (alphabet plus a word list). **15th century: 96 % of keys include nulls** (18th: 27 %), 94 % of nulls have ≥ 2 codes; symbol sets combine letters, digits and graphic signs "in almost all keys" in the 15th century; alphabets typically homophonic, **nomenclature elements "tend to have one code only"**; very large tables (100+ n-grams) use homophones only for a few frequent entities.
  - *What Was Encoded in Historical Cipher Keys in the Early Modern Era?* (2022, https://ecp.ep.liu.se/index.php/histocrypt/article/download/404/362): >1,300 keys with nomenclatures, 1400–1800; 15th–16th-century nomenclatures "dominated" by personal and place names; ~20 % of 15th-century keys encode numbers; syllables and morphological endings appear mainly from the 17th century; punctuation absent in the 15th.
- **Tranchedino, Cod. Vind. 2398.** 2003 voynich.net post quoting an expert opinion: 6 intercepted ciphers, **287 complete + 4 incomplete keys**, c. 1475 (http://www.voynich.net/Arch/2003/11/msg00137.html; not opened, snippet); facsimile publishers say "about 300" (local `facsimiles_com_tranchedino.html`). Pelling on a c. 1450 Mantuan key in the ledger: **2 homophones per consonant (except x, z, '9'), 3 per vowel, a mini-codebook of common words, some nulls, syllable shapes and a small nomenclator** (https://ciphermysteries.com/2016/07/06/fifteenth-century-cryptography; not opened, snippet). Höflechner 1970 ADEVA facsimile remains the only full edition.
- **Meister 1902** is at HathiTrust (page images, US access only) per the Online Books Page
  (https://onlinebooks.library.upenn.edu/webbin/who/Meister%2c%20Aloys%2c%201866%2d1925; not opened). Not on
  archive.org as O-017 says. Meister 1906 also at HathiTrust.
- **Buonafalce, Cryptologia 32(1) 2008, 62–70** on Simonetta's *Regule*: the rules apply only to dispatches
  with word divisions, no homophones, nulls or code words; cipher clerks of the time already defeated them;
  rejects Simonetta as Voynich encipherer (snippets via ciphermysteries 2008-01-11; not opened).
- Simeone de Crema 1401 (Mantua): first vowel homophones; exact counts not found in any open source.

**What it changes.** O-016/O-017 are **largely closed by substitution**: the project does not need Meister
1902 for sizes; the DECODE aggregate gives the period profile (alphabet 20–30 + a names nomenclature of tens
to a few hundred entries, 2–3 homophones per letter, nulls almost universal, one code per nomenclature
element). Against that profile the project's `ctl_nomen*` (20-letter random alphabet) and K4 (5.5k shared
codewords) are both unhistorical: a period nomenclator cannot supply 7k types, so the codebook family is
**closed on historical grounds as well as entropy**, and the cipher family that fits the period is
"homophonic alphabet + nulls + small names list", which is Naibbe's design space. The 96 %-nulls figure
makes O-024 (null-glyph ciphers) the historically grounded untested family, and null glyphs are one
mechanism for line-initial/line-final vocabulary that no producer has tried.

## 6. Machine-readable diplomatic (abbreviations unexpanded) medieval Latin with real lines

- **CREMMA Medii Aevi** (Clérice, Chagué, Vlachou-Efstathiou), JOHD 2023 doi 10.5334/johd.97 (datapaper opened
  via pdftotext; repo opened: https://github.com/htr-united/cremma-medieval-lat; Zenodo opened:
  https://zenodo.org/records/7013436 → v0.1.2 record 8407213, 356.7 MB zip, Oct 2023). **21 manuscripts, 7,274
  lines, 263,000 characters, 12th–16th c., graphematic transcription (abbreviation marks kept as MUFI
  characters, not resolved), ALTO XML with line-level segmentation, licence CC0** (datapaper line 143;
  Zenodo says "Other (Open)"). Texts chosen "to display a higher degree of abbreviations"; genres mixed
  (scholastic, classical, recipes noted as less abbreviated). Line breaks are preserved by construction
  (HTR ground truth is one ALTO `TextLine` per physical line).
- **CATMuS Medieval** (Zenodo 10066219 / 15030337; not opened beyond snippet): multi-language medieval HTR
  ground truth built on the same guidelines, "no abbreviations are resolved", each superscript its own
  character.
- **CAMA** (Corpus Approach to Manuscript Abbreviations; DH 2018 abstract; not opened).
- **TRIDIS** (arXiv 2503.22714): semi-diplomatic, expands abbreviations — confirms the project's O-014 note.
- Not found: any plain-text IVTFF-style edition with original lines; CREMMA's ALTO needs a 20-line parser.

**What it changes.** **O-014 and O-026 close together** with one download (REDTEAM #3's "highest-value single
control"). Caveat: 15th-century Latin book hands in CREMMA are few; the datapaper's registry CSV lists dates
per manuscript, so filter to 1350–1500 and to single-column prose pages before scoring jsd_first / jsd_last /
m5 anatomy / edge coupling.

## 7. voynich.ninja: is there a consensus on the next decisive test?

Opened: News forum index (https://www.voynich.ninja/forum-25.html), the Schwartz thread "Harvard
physicist's take on the VMS" (magnesium, opened 2 Oct 2026, 85 posts to 18 Oct; pages 1–9 at
https://www.voynich.ninja/thread-6147.html … -page-9.html), the R&T thread
(https://www.voynich.ninja/thread-6034.html, 20–21 Aug 2026), the Naibbe rebuttal thread (6067), the line
patterns thread (4343), the Layfield & Davis thread (5896).

- **No decisive test is named by anyone.** The R&T thread's only methodological question is Koen G's
  "selection vs alteration" for the edge coupling (does a final glyph attract an existing word with a given
  initial, or change the word?). bi3mw reproduces the coupling at ~0.18 bits (H(head) 3.09 → 2.91) and finds
  23 of 536 stems with significant predictability. Rafal: the real dependency is "last letter – last
  letter", not last–first. nablator: word conditional entropy "similar to Latin".
- **Schwartz reception** is dominated by authorship, not method: Koen G "Too technical or too AI?", the
  Anthropic funding line is quoted repeatedly; Rafal: "36 articles … sponsored by an AI company"; Lisa Fagin
  Davis (5 Oct): ~200 AI-assisted "solutions" received this year; Bluetoes "AI barnacles"; Mauro will verify
  the references. (Science, 9 Oct 2026, reports forum contributors called it "AI slop"; 403, not opened.)
  Substantive points: nablator (2 Oct) — "no dependence between words beyond the coupling of adjacent word
  edges" means any language theory needs heavy homophony (credits Mark Fincher); Jorge Stolfi (4 Oct) —
  every such test uses European/Semitic controls and novels rather than herbals, proposes non-European
  herbal controls (Shennong Bencao named by DG97EEB, 5 Oct); hensing1's summary (15 Oct) — generator fitted
  to only 2 of 5 hands, edge coupling not reproduced, test "a little too strict", and the paper's own
  falsifier is "a confirmed reading of any passage"; RadioFM (16 Oct) flags the f115r change-point test as
  unexplained; Stolfi (16–17 Oct) — no large statistical drifts in the text, which he says a free gibberish
  process would show; RadioFM — third-order and higher conditional entropies comparable to Germanic/Latin.
- **What the literature treats as decisive instead** (each already a project band or near it): R&T — edge
  coupling (0.197 bits, 5.7 % of next-first-glyph entropy; A 0.137, B 0.248) *and* hapax 70 % jointly, which
  "no imitation" reaches; Parisel 2026 — four signatures per dialect, cross-boundary MI ≥ 0.29 (A) / ≥ 0.25
  (B) plus the 80.6 % end-class→start-class rate, best slot generator MI 0.17, grille 0.05; Zandbergen (via
  Feaster) — p/f/cPh/cFh in first lines as "prohibitive"; Schwartz — the generator's residual misses (edge
  coupling 0.009/0.001 on generated pages, adjacent near-repeats, hapaxes, same-initial consecutive lines in
  Scribe 2) and a blind-applicable reading as the falsifier.
- Independent audit of R&T (GitHub SoylentAquamarine/voynich-collective PR #5, 19 Sep 2026; not opened):
  reproduces the separator hierarchy, token-order and 32–64 BPE scale; notes a provenance defect in the
  cited data snapshot.

**What it changes.** The field's implicit decisive test is the one the project already converged on
(edge coupling + hapax + line edges inside the type budget = O-006/O-008). Two things the project has not
got: Stolfi's non-European herbal control (a cheap addition to the L family that would blunt the "no
language reaches the edge bands" claim if one did), and the selection-vs-alteration decomposition of the
coupling, which m5's "vocabulary choice vs flourish" split already half-answers and should be stated in
those terms.

---

## What the project missed (prior art not in the local registers)

1. Smith & Ponzi 2019, *Glyph combinations across word breaks*, Cryptologia 43.6 (doi 10.1080/01611194.2019.1596998; not opened) — the published statistic behind the cross-space coupling; the project's c3 reimplements R&T's abstract instead (O-037).
2. Feaster 2022 positional explanation of [y.q]/[n.q] (opened) — position-stratified null needed.
3. Steckley & Steckley 2024 (opened) — drawings as a boundary class; Bayes factors per token; no project equivalent.
4. Vogt 2012, Stafford/tavie 2022–2024 per-scribe line profiles (opened thread) — vertical o-q effects untested by any producer.
5. Zandbergen 2021 arXiv 2104.12548 grille generator (not opened) — possibly a better G control than `rugg_grille`.
6. Layfield & Davis 2026 singulion structure (not opened) — bifolio as production unit.
7. DECODE key statistics (opened) — period nomenclator profile; replaces O-016/O-017.
8. CREMMA Medii Aevi (opened) — the real-line control.
9. G&B charbias_lines result (local, unread by the project) — Voynich sides with meaningful text on line-position character bias.
10. Timm's token-budget argument against line effects in a verbose cipher (opened) — a bound the project can compute.

## Assumption candidates

**Verified (opened and read in this session, or local text quoted by line):**
- R&T §3.6 numbers (0.528 / 0.179 / 0.203; [0.31, 0.40]; enrichment factors); R&T controls use the Voynich line template; Naibbe hapax 41 %, edge 0.006.
- Schwartz §5.4: 0.2–0.3 bits/page, quire-aligned null, herbal no tint, raw gain negative with quire conditioning; comparison texts cut to the manuscript's line lengths.
- Timm 2014: 617/716 paragraphs (86 %) gallows-initial.
- Steckley 2024: 7,660 tokens / 1,223 lines / 95 folios; ~7.5 % shorter line-final; no manuscript control.
- Feaster 2022: Aeneid 0.399 vs 0.708; positional account of [y.q]/[n.q]; cites Zandbergen 2021 "prohibitive feature".
- G&B 2022: charbias_mean not significantly different between VMS and meaningful text; corpus files keep line breaks.
- DECODE HistoCrypt 2021/2022: 96 % of 15th-century keys with nulls; 72 % of keys > 100 plaintext entities; nomenclature elements mostly single-coded; 15th-century nomenclatures name-dominated.
- CREMMA: 21 manuscripts, 7,274 lines, 263k characters, graphematic, ALTO, CC0 (datapaper), 356.7 MB zip v0.1.2.
- Ninja threads 6147, 6034, 6067, 4343, 5896: posters, dates and quoted points as listed; no decisive test proposed.
- Naibbe thread page 2: Timm's 38.5 % table-α and 38k-tokens-vs-57–76k-letters arguments; Greshko's concessions.
- RN-Top PR #5: OR 22.9 native vs 1.8 re-lined; 8.5 % vs 16.1 %; LLM-generated.

**Inferred (snippet, citation, or secondary only — refutable by opening the source):**
- Tranchedino "287 + 4 keys" (2003 mailing-list quotation of an expert opinion) and "~300" (publisher); c. 1450 Mantuan key 2/3 homophones + nulls + mini-codebook (Pelling blog snippet).
- Meister 1902 on HathiTrust US-only (Online Books Page snippet).
- Buonafalce 2008 content (ciphermysteries and abstract snippets).
- Layfield & Davis 2026 claims (press and forum paraphrase; article not opened).
- Zandbergen 2021 arXiv 2104.12548 as a grille generator with line rules (title and Feaster's citation only).
- Smith & Ponzi 2019 as the origin of the word-break statistic (Feaster's citation).
- Science 9 Oct 2026 "AI slop" quotation (search snippet; page 403).
- SoylentAquamarine audit of R&T (search snippet).
- DECODE live counts (10,106 / 6,396 / 3,692) (snippet).
- That CREMMA contains enough 1400–1500 single-column prose to matter (datapaper lists 12th–16th c.; the per-manuscript date table was not read).
- That no 2025–2026 paper has a real-manuscript line control: three searches found none; absence, not proof.
