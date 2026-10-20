> **Historical (superseded 2026-10-17 23:33).** Current state: `README.md` → `workflow/FINDINGS-REPORT.md`. Findings from this file are in `.inventory/registers/`.

# Red team: external "truths" checklist vs team knowledge system

Audited: 2026-10-17 16:58+ (system clock). Method: coverage counts in
`research_notes/` + `reports/` + root *.md; primary fetches this session
(voynich.ninja, voynich.nu + transcr.html, thevoynich.org, ACL Q16-1006,
arXiv:2608.17096, Digital Medievalist 2331 abstract). Result files beat
summaries (TEAM-HANDOFF rule). Verdict key: EXISTS / PARTIAL / MISSING /
OVERSTATED (in the checklist as pasted).

## 1. Physical & forensic

| Claim | Team state | Verdict |
|---|---|---|
| Vellum 1404–1438, 4 Arizona AMS samples | 20 lines / 6 files; docx audit re-derived 1406–1434 | EXISTS. "100%" is rhetoric: 95% CI on parchment, not ink. |
| McCrone inks/pigments period-authentic, no modern synthetics | 9 lines / 4 files | EXISTS (secondary-level; McCrone primary not opened locally). |
| Ink applied fresh, Kelley-on-old-vellum eliminated | Team report records Zandbergen's opposite caution: immediacy "did not follow" from analysis | **OVERSTATED.** Fresh-ink inference is argued, not confirmed. Keep Kelley improbable, not eliminated-by-ink. Why it matters: a 150-year ink gap would reopen 16th-c. cipher context for solver language choice. |
| Alpine origin (merlons Italy vs dress/marginalia S. German/Bohemia) | merlon 9 lines / 3 files; docx adds saddleback roofs, Firenze MS 106 | EXISTS as leading hypothesis, not consensus proof. Merlons also occur wider; origin constrains language priors — treat as prior, not filter. |

## 2. Paleography & binding

| Claim | Team state | Verdict |
|---|---|---|
| ≥5 scribes (Davis 2020) | Covered; hands in ZL metadata used by B5/C1 | EXISTS. Inference "five people understood the system" does NOT follow: copying/exemplar transmission needs no comprehension (rambling-hybrid models exploit exactly this). |
| Layfield & Davis singulions "proved", Oct 2026, gutter/illustration analysis | Layfield 14 lines / 4 files; singulion 6 / 3. Primary abstract fetched: LSA on pages/leaves/bifolia/quires, "strong evidence", sequence *hypothesized* | **OVERSTATED + method misdescribed.** Evidence is textual-statistical (LSA), not gutter image proof; Timm: reading order underdetermined. Checklist's own caveat (pages self-contained) is correct and important: folio order affects Heaps/topic/drift tests (M2 flips), so author-order sensitivity must accompany any sequence claim. |

## 3. Linguistic & cryptographic

| Claim | Team state | Verdict |
|---|---|---|
| Currier A = Scribe 1 only; B = Scribes 2–5 | Local: S4 = A/B/third blend (docx/Bayesian notes); C1 quire null weakens hand-2 signal | PARTIAL/OVERSTATED as clean split. Use (hand × illus × quire), never A/B alone. Word lengths: A 4.79 vs B 5.09 (a1) — real but modest. |
| Line as functional unit; no hyphenation | a2/B4/L1 quantified (JSD 0.176; p ×17.9; m ×16.3) | EXISTS, strengthened locally. "Certain words only at line start/end" overstates enrichment as exclusivity. |
| Rigid slot morphology; 1-edit neighbours adjacent | b3 second-order slot effect real (qo→gallows 0.841 vs null 0.403); D2/M3: induced slots lose held-out under proper scoring nuance | EXISTS as description; slot-as-grammar NOT established. Gallows are not middle-only (line-initial p/f). |
| H2 ~2 vs 3.5–4 "proves" no simple substitution (Schinner 2006; Bowern 2016) | Local h2 2.126 vs controls 3.11–3.30 (a1 def.); Rozanova def. gives 2.7 vs ~3.5 | Direction EXISTS; attribution/dates loose (Bennett 1976 anomaly; Lindemann & Bowern 2020/21 across 294 languages). Logically: substitution preserves h2, so plaintext h2 ≈ 2 — below *sampled* languages. State scope, always cite definition. |

## 4. Contextual & visual

| Claim | Team state | Verdict |
|---|---|---|
| Toresella N. Italian alchemical herbal tradition | 1 line / 1 file (docx only) | **PARTIAL — thin.** No local comparator corpus built (ctl_nomenclator uses Macer+Pliny text, not image comparators). Why it matters: herbal section priors + label crib candidates depend on it. |
| Brewer & Lewis 2024, SHM, Hartlieb Secreta Mulierum ciphers | **0 lines** in notes/reports/root (exists only as docx works-cited OUP link) | **MISSING — biggest knowledge gap.** Existence verified externally this scout (SHM 37(3):559–582, multiple independent citations; OUP primary not opened). Why it matters: only peer-reviewed period *motive + practice* for enciphered medical text in the exact region/date; decoded comparator ciphers could supply solver priors (abbreviation habits) no statistics can. Their Rosettes/uterus mapping is interpretation, not proof — import as Candidate. |
| Sept 2026 WitchTok menstrual-blood hoax | 1 TikTok line / 1 file (unrelated context) | **UNVERIFIED.** No source opened; do not cite until a primary/press record is fetched. Low research value either way. |

## 5. Provenance

| Claim | Team state | Verdict |
|---|---|---|
| Rudolf II purchase (600 ducats) → Sinapius → Baresch → Marci → Kircher 1666 → Jesuits → Voynich 1912 | 600: 14 lines / 5 files; Guzy 1599 Widemann sale (600 florins, rare books) in report | Chain EXISTS from Baresch/Marci letters onward. Rudolf purchase + gift remain Marci-letter hearsay, strengthened not confirmed by Guzy. Sinapius ex-libris on f1r is physical; "given by Rudolf" is not. |
| 150-year gap = zero record | Consistent with notes | EXISTS. Consequence correctly drawn: 1420 authorship claims are speculation. |

## Rules-of-engagement audit (checklist table)

- Transcription: team uses ZL3b (current Zandbergen–Landini), now with
  `data/external/voynich-nu-ivtff/` + M2 cross-transcription robustness.
  "Never FSG/Currier, massive errors" is **overstated** — older
  transliterations are exactly what robustness checks need; ban only
  *sole-source* use. "2022–2026 multispectral transcriptions" as EVA update:
  multispectral changed specific readings (f116v, f1r columns), no wholesale
  re-transcription exists locally — **partial**.
- A/B as separate datasets ordered by singulion sequence: team does split
  A/B and hand/illus, but author order is hypothesized (above) — run
  order-sensitivity, don't hard-code one sequence as truth.
- Botany vs N. Italian herbals: agreed, unbuilt locally (see Toresella gap).
  TheVoynich.org Comparators (651 records, scouted separately) is the fastest
  structured entry — currently 0 team mentions, second blind spot.
- Bacon/Dee/Kelley exclusions: Bacon solid (dating); Dee/Kelley rest on
  dating + provenance, not the fresh-ink claim.

## Missing-and-important (ranked)

1. **Brewer & Lewis + Hartlieb cipher comparators** — motive, period cipher
   practice, possible abbreviation priors. Nothing local substitutes.
2. **TheVoynich.org register diff** (70 Falsified / 77 Confirmed vs LEADS
   §B/§A) — cheapest duplicate-work insurance available.
3. **Comparator manuscripts as data** (Firenze MS 106, Cgm 7958, herbal
   image set) — every visual/crib claim currently rests on prose summaries.
4. **Author-order sensitivity** for every sequence statistic (Heaps, drift,
   topic) — M2 already shows flips; singulion order makes this load-bearing.
