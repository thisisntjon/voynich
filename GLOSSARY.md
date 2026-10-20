# Glossary

Plain-English definitions of the terms, grades, ids and names used in this record. Each entry points to the file where you can see more. Written for a curious non-specialist and for an AI agent picking up the work.

## The manuscript and how its text is written down

**Voynich manuscript (MS 408).** An illustrated book in an unknown script, held by Yale University's Beinecke Rare Book and Manuscript Library as Beinecke MS 408. It has not been deciphered, and nothing in this record reads it. See `README.md`.

**Folio and page ids (f1r, f1v, f67r1 ...).** A folio is one leaf; `r` (recto) is its front and `v` (verso) its back, so `f1r` is the front of leaf 1. Fold-out leaves carry extra panel numbers (for example `f67r1`). See René Zandbergen's IVTFF format description on https://www.voynich.nu/ (IVTFF).

**Quire.** A gathering of folded sheets sewn together; the manuscript's quires are lettered A to T (numbered 1 to 20, with P and R unused) in the IVTFF page variable `$Q`. Many tests hold out one quire at a time (see LOQO). See the IVTFF format description (voynich.nu), Table 6.

**Bifolio.** One sheet folded once, giving two leaves (four pages); some tests use bifolios as blocks. See `.inventory/registers/METHODS.md`.

**Transliteration.** A typed version of the manuscript's glyphs in some agreed alphabet, made by a human transcriber; it is not a translation. Different transcribers read some glyphs, word breaks and line breaks differently. See `data/external/README.md` section 1.

**EVA (European Voynich Alphabet).** The most widely used way to type Voynich glyphs as Latin letters (for example `daiin`, `chedy`, `qokeedy`); the letters are labels for shapes, not sounds. "Basic EVA" leaves out rare glyphs; "extended EVA" codes them as `@nnn;`. See `data/external/README.md` section 1.

**IVTFF (Intermediate Voynich Transliteration File Format).** René Zandbergen's common file format for all public transliterations, with one line per locus and page variables in a header line per page. See the transliteration README on voynich.nu and the IVTFF format description (voynich.nu).

**Locus (plural loci).** One unit of text on a page: a line of a paragraph, a label, or a ring or spoke of text in a circular drawing. In IVTFF a locus is written like `<f1r.3,+P0>`: page, locus number, a position symbol and a locus type. See the IVTFF format description (voynich.nu), Tables 8 and 9.

**Locus types (P, L, C, R units).** The capital letter gives the generic type: `P` is paragraph text, `L` a label (a short word near a drawing), `C` text running around a circle, `R` text running along a radius. A lower-case letter or digit after it gives the subtype (for example `P0` normal left-justified text, `Pt` a right-justified title, `Lz` a zodiac label). See the IVTFF format description (voynich.nu), Table 9.

**Paragraph markers `<%>` and `<$>`.** In IVTFF, `<%>` marks the start of a paragraph and `<$>` its end; they come in pairs on the same page. Where paragraphs begin is the transcriber's decision, so files can differ. See the IVTFF format description (voynich.nu) (dedicated comments); `tools/ivtff_to_meta.py` strips them when building word streams.

**Drawing interruptions `<->` and `<~>`.** `<->` means the line is interrupted by a drawing; `<~>` means the same with the two parts poorly aligned. See the IVTFF format description (voynich.nu).

**Page variables (`$Q`, `$L`, `$H`, `$C`, `$I`).** Per-page settings in IVTFF: quire (`$Q`), Currier language (`$L`), Lisa Fagin Davis's scribe (`$H`), Currier's older hand id (`$C`) and illustration type (`$I`). See the IVTFF format description (voynich.nu), Table 6, and the voynich.nu transliteration README.

**Currier A and B ("languages").** Prescott Currier (1970s) found that pages fall into two statistically different text types, which he called languages A and B; whether they are two languages, two dialects or two scribes' habits is unsettled. In this record that question is hypothesis H-13 ("weakened, confounded"). See `workflow/FINDINGS-GRAPH.yaml` (H-13).

**Hands (scribes).** Lisa Fagin Davis (2020) identified five scribes by handwriting, recorded as hand 1 to 5 in `$H`; Currier's older hand ids are kept in `$C`. Many tests compare or control for hand. See the voynich.nu transliteration README and `data/external/README.md`.

**Gallows.** The four tall EVA glyphs `k`, `t`, `p`, `f`. In this record, `p` and `f` behave mainly as paragraph-initial markers while `k` and `t` occur throughout the text. See `.inventory/registers/METHODS.md` row 2.4 and `.inventory/registers/LEARNINGS.md`.

**Prefix, core, suffix (slot grammar).** Our model splits each word into an optional prefix, a central core and an optional suffix, found automatically by `SlotSegmenter`. That these are the right units is assumption X-01, which is currently at risk, so findings resting on it are weighted down. See `.inventory/registers/METHODS.md` row 4.7 and X-01 in `workflow/FINDINGS-GRAPH.yaml`.

## Transliteration files (by short name)

**ZL3b.** The Zandbergen-Landini transliteration, version 3b (13 May 2025), in EVA; our main data source. Downloaded to `data/ZL3b-n.txt` by `tools/fetch_data.py` (not stored in this repository). See `data/FETCH.tsv`.

**RF1b.** The reference transliteration, built automatically by merging the ZL and GC transliterations, version 1b; `RF1b-e` uses extended EVA and `RF1b-er` basic EVA. See `data/external/README.md` section 1.

**IT2a.** Takeshi Takahashi's complete transliteration as included in Jorge Stolfi's 1999 interlinear file, in basic EVA. See the voynich.nu transliteration README.

**VT0e.** Takahashi's transliteration as used on the voynichese.com site; differs from IT2a only in how unreadable glyphs are marked. See the voynich.nu transliteration README.

**GC2a and voyn_101.** Glen Claston's v101 transliteration: `voyn_101.txt` is his original file, `GC2a` the IVTFF version. It uses its own v101 alphabet, which does not convert losslessly to EVA. See `data/external/README.md` section 1.

**CD2a.** The Currier-D'Imperio transliteration, in Currier's own alphabet; it covers about 41 % of loci, mostly herbal pages. See the voynich.nu transliteration README.

**FG2a.** The transliteration of William Friedman's study group (1940s), in its own FSG alphabet, as re-typed by Jim Reeds (1994). See the `FG2a-n.txt` header and `data/external/README.md`.

**LSI.** The Landini-Stolfi Interlinear file: many transcribers' readings interleaved locus by locus (Landini, Stolfi, Takahashi, Grove, the historical Currier and Friedman transcriptions and others). Split by transcriber letter before counting words. See `data/external/README.md` section 1.

**"Three transliterations."** Most of our runs repeat on ZL3b, RF1b and IT2a. Because these share the same scans and glyph set, agreement across them counts only as the weak `data` axis. See `workflow/TRIANGULATION.md`.

## Statistics and methods

**LOQO (leave-one-quire-out).** A held-out test: fit on all quires but one, score the quire left out, and repeat for each of the 15 quires with at least 4 pages. A result "at 10/15" passes on 10 of the 15 folds. See `.inventory/registers/METHODS.md` row 13.1.

**Moran's I.** A measure of whether neighbouring values resemble each other; here, whether a word's length predicts the next word's length (positive means similar lengths cluster). See `.inventory/registers/METHODS.md` row 1.13.

**MI (mutual information).** How many bits knowing one thing (for example, a word's core) tells you about another (the next word's core); our runs report MI "excess" over a shuffled baseline. PMI (pointwise MI) is the same idea for one specific pair, and is used rarely here. See `.inventory/registers/METHODS.md` rows 4.x and 13.2.

**NMI (normalised mutual information).** MI scaled to run from 0 (no relation) to 1 (perfect match); used to ask how well word-topic clusters line up with manuscript sections. See `.inventory/registers/METHODS.md` rows 6.1 to 6.4.

**Positive control.** A planted case where the true answer is known (for example, a real language run through a known cipher), used to show a test can find what it looks for. A test that cannot find a planted instance on at least 10 of 15 folds has its exclusions filed as UNINFORMATIVE (D-068). See `workflow/TRIANGULATION.md`.

**Producer.** A candidate mechanism that could have produced the text (a language, a cipher, a generator, gibberish); a run "excludes" a producer when its output fails to match the manuscript's measured profile. See `workflow/FINDINGS-GRAPH.yaml` (hypotheses).

## How results are graded

**Grades.** Each finding gets one grade from its evidence lines. **TRIANGULATED**: agreeing lines on at least three axes, at least one from outside our own pipeline (`impl`, `physical` or `external`); counts 1.0. **CORROBORATED**: agreeing lines on at least two axes; counts 0.67. **SINGLE**: one axis; counts 0.34. **CONTESTED**: an unresolved disagreeing line; counts 0. See `workflow/TRIANGULATION.md`, section Grades.

**Axes.** The independent routes an evidence line can take: `data` (another transliteration; never independence on its own), `seg` (another word-splitting method), `split` (held-out pages or quires), `method` (a different statistic for the same property), `impl` (code written independently of this tree), `physical` (measured from scan ink, not transcription), `external` (published by others) and `order` (survives changes in assumed reading order). See the `axes:` block at the top of `workflow/FINDINGS-GRAPH.yaml`.

**Evidence line.** One independent way a finding was obtained, recorded as `{axis, by, ref, claim, agrees}`. A line marked `unverified: true` counts for nothing until its run is re-frozen or replicated. See `workflow/TRIANGULATION.md`.

**At-risk assumption.** An assumption (X- id) that evidence has put in doubt; a finding resting on it, not yet discharged by a line, is weighted half. See `workflow/TRIANGULATION.md`.

**Load-bearing finding (◆).** A finding many others rest on; if it becomes CONTESTED, work stops for a pivot check. See `workflow/TRIANGULATION.md`, step 5.

## Id families

**X- (assumptions).** Things findings rest on, such as X-01 "the prefix/core/suffix units are right"; each has a status (verified, unverified, at-risk or flipped), and an evidence line can `discharge` one by testing it directly. See `workflow/FINDINGS-GRAPH.yaml` (`assumptions:`).

**F- (findings).** Tested structural properties of the text, each with evidence lines and a grade. See `workflow/FINDINGS-GRAPH.yaml` and the generated `workflow/FINDINGS-MAP.md`.

**H- (hypotheses).** Candidate explanations of what the text is (plain language, a cipher family, gibberish and so on), each with a status such as live, disfavoured or excluded. See `workflow/FINDINGS-GRAPH.yaml` (`hypotheses:`).

**P- (pending tests).** Planned or finished runs and which findings, hypotheses or assumptions each would decide. See `workflow/FINDINGS-GRAPH.yaml` (`pending:`).

**U (plan assumptions, U1, U2 ...).** Upstream unknowns the plan depends on, tested by early runs and kept with the stage and phase log. See `workflow/PLAN.md`.

**c- (claims).** Every cited number, with the results file and line it comes from. See `.inventory/registers/CLAIMS.md`.

**L- (learnings).** What was learned, including failures and method lessons, indexed by theme. See `.inventory/registers/LEARNINGS.md`.

**D- (decisions).** Why things were done, reversed or rejected; D-066 is the running log of frozen designs and approvals, D-072 the strategy pivot to external validation. See `.inventory/registers/DECISIONS.md`.

**O- (open questions).** Gaps, open questions and the work queue. See `.inventory/registers/OPEN.md`.

**Run ids and prefixes.** Each run's id carries its owner's prefix: `s` the lead session, `db-s` Daybreak, `r` (or `roach-r`) roach, `gk-` Grok Bot, `ve-` Voynich Expert, `vx` Eve / Voynich Analyst, `ar-` Argon, `mu-` Muse. The same number under two prefixes (for example `s96` and `db-s96`) names two different experiments. See `AGENTS.md` (id rule) and `TEAM-HANDOFF.md` (alias map).

## Process terms

**Pre-registration stub.** Before a run sees real data, its script and design files are hashed into a `*.prereg.sha256` stub, which anyone can check with `grep -v "^#" STUB | tr -d '\r' | sha256sum -c -`. If a stub lists the same file twice (an amendment), the last uncommented line is binding. See `AGENTS.md` and `workflow/TRIANGULATION.md`.

**Printed call.** Each pre-registered test prints its outcome as `NAME = True/False`; the record files that printed value, not the summary prose. See `workflow/TRIANGULATION.md`, step 1.

**POST-HOC.** A note on evidence lines whose results file was overwritten after its stub was re-stamped, so the first output is lost. Eighteen such runs were found; their 54 graph lines stop counting until roach replicates them (D-075). See `.inventory/registers/DECISIONS.md` row D-075.

**Exact-pinned.** A file published byte-for-byte unchanged because a pre-registration stub pins its sha256; it may still show original local paths or internal names. See the handover `README.md` and `MANIFEST.tsv`.

**Explore and confirm tiers.** Explore (the default) is any quick read-only probe on data already held: labelled EXPLORATORY, kept under `runs/explore/`, and never moves a grade. Confirm applies the full rules (pre-registration, positive control, independent replication or lead audit) once, to a single result that would change a grade or be cited (D-085). See `AGENTS.md` (speed rule) and `.inventory/registers/DECISIONS.md` row D-085.

**Independent replication.** The same result reproduced by code written without this tree's code (the `impl` axis, usually roach). A result changes a grade only after such a replication or a lead audit passes. See `workflow/TRIANGULATION.md` ("Replication by default").

**Blind study.** A run where readers (agents) label manuscript crops without knowing the answer key. The protocols, pre-registrations and results are published; reader inputs, responses and sealed keys are withheld. See the handover `README.md`.

## People, agents and machines

Except for Jon, the names below are AI agents or AI sessions; the handover `README.md` describes the run-prefix owners as "the AI research agents that did the work under Jon's direction". Roles changed over the project; the ones given are those in the records at the October 2026 pause.

**Jon.** Project owner: set the goal, approved pivots and decisions, and relayed messages between agents that could not reach each other. See `.inventory/registers/DECISIONS.md` (rows cite "Jon").

**Astra.** AI agent; execution lead from D-080 (19 Oct 2026): scheduling, dispatch, running frozen steps, the replication queue and assignments. Also maintained the companion lab tree (`lab/...`). See `TEAM-HANDOFF.md` (roles) and D-080.

**Opus / voynich-08 (lead session).** A Claude Code session running a Claude Opus model; lead of the work, and from D-080 the evidence and methodology reviewer and sole custodian of the registers, the findings graph and the plan. Its runs use the `s` prefix. See `TEAM-HANDOFF.md` and D-080.

**Daybreak.** AI agent (a Codex session) working in the companion lab tree: frozen snapshots, independent audits and scan registration; runs use `db-s`. See `TEAM-HANDOFF.md` (lanes, alias map).

**roach.** Both the second machine and the agent working on it, which writes code-independent blind replications (`r` runs); its replications supply the `impl` axis. See `TEAM-HANDOFF.md` and `workflow/TRIANGULATION.md`.

**Grok Bot.** AI agent (`gk-` runs) that organised the knowledge library (`data/external/library/`), ran the herbal-profile calibration (s128) and did a first read of Egerton caption rows 1 to 128. A Grok session is also recorded as the standing read-only auditor of lead runs. See `TEAM-HANDOFF.md` and `.inventory/registers/DECISIONS.md`.

**Argon.** AI agent sessions (`ar-` runs; earlier also some `s` ids such as s33 to s38 and s85 to s101) that ran large structural studies and wrote recommendation lists. Several Argon results were rejected or quarantined because results were overwritten after freezing (D-063 to D-065). See `TEAM-HANDOFF.md` and `.inventory/registers/DECISIONS.md`.

**Sylvie.** AI reviewer and overseer whose reviews corrected overclaims; their systematic method shapes D-066, and they were put in charge while Eve was unavailable (D-078). Their messages reached the team through Jon. See `.inventory/registers/DECISIONS.md` rows D-066 and D-078.

**Muse.** AI helper agent (`mu-` runs) that ran the zodiac-label crib test (Q1, L-152) and extracted Beasley's 2024 herbal census (L-344). See `.inventory/registers/LEARNINGS.md`.

**Eve / Voynich Analyst.** AI agent (`vx` runs) that tested assumption X-01 against several word-splitting methods on planted books (vx01, c-592); unavailable from 19 Oct 2026. See `.inventory/registers/CLAIMS.md` (c-592) and `TEAM-HANDOFF.md`.

**Voynich Expert.** AI agent session (`ve-` prefix) that set up the picture plan and the full facsimile manifest (s127, parked; its manifest offset is O-073). See `TEAM-HANDOFF.md` and `.inventory/registers/OPEN.md` (O-073).

**Skynet.** The main workstation, where the canonical tree and the lead session ran. See `TEAM-HANDOFF.md` (lead identity).

**roach (machine).** The second machine, used for code-independent replications and offloaded compute. See `AGENTS.md`.

**Lab tree (`lab/...`).** A companion working tree where Daybreak and Astra worked; the lab files that the findings and registers cite are included under `lab/`. See the handover `README.md`.
