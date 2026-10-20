# s128 DRAFT pre-registration: does a Voynich herbal page carry a page-confined "name slot" at its start?

Status: **DRAFT. Not frozen, no hash, not run. No Voynich data was read to write it.**
Offered to the lead as input to D-073 item (d) (held-out meaning prediction). The lead session owns item (d).
D-072 holds every meaning-test freeze until an external bridge (Egerton or Fontana) survives. This draft respects that and freezes nothing.
Author: Grok Bot (Jon's request, 2026-10-19 ~01:45 PDT). Calibration this draft rests on: `runs/s128/results_s128_herbal_profile.txt` (sha256 fdb4e114b6da9fe79f4d31a4ec511fda9e9efbc24ecc88efff9f887f40cea840).

## Prior work this must not repeat (check-first rule, D-066 dd)
- Stolfi 1998, "Plant names" (https://www.ic.unicamp.br/~stolfi/EXPORT/00-EXPORT/98-01-27-plant-names/): the first word of a herbal page is "almost always" page-specific; table of the shortest page-specific opening sequence per folio. Descriptive, no null.
- Stolfi word-grammar Note 011 (https://www.ic.unicamp.br/~stolfi/PUB/EXPORT/00-EXPORT/00-06-07-word-grammar/Notes/011/Note-011.txt): first and last words are characteristic of the page; the first word often recurs at the start of the second paragraph with slight change. Qualitative, no null.
- Zattera v4j Note 012 (https://mzattera.github.io/v4j/012/): word types prefer paragraph line 1 / line start / line end (e.g. "Sol" in Herbal A). Position preference, not page confinement.
- voynich.site, "Bax plant names" (https://voynich.site/en/hypotheses/bax-plant-names/, verdict 2026-07-26): identified-plant names do not match first words, first lines or sound shapes; candidate names occur outside the herbal 18% of the time. Tests name IDENTITY, not page confinement.
- Project: L-069 / F-02 (paragraph-initial words are mostly rare gallows types never seen mid-line), L-032 / d6 (labels do not name own-page objects beyond section vocabulary), F-43 (label cores retrieve own-page body vocabulary, one representation only), F-13 (rare cores repeat at short range), F-20 (no internal crib).
- What none of these does: compare the Voynich rate against a real illustrated herbal reduced to opaque types + positions, with a position-aware null and a planted control. That is the only new part here.

## Real-book expectation (from s128 calibration, known-answer books, ids + positions only)
Statistic S = share of pages whose earliest page-confined recurring type (count >= 2 on the page, >= 90% of its section tokens on that page) first appears in line 1.
- Circa Instans format (Egerton 747, name = first word 86%): S 0.25-0.27 vs within-page shuffle null 0.08-0.11 (q99 0.13); unique-and-recurring first token 0.20-0.22; power 1.00 at 110 pages, 0.63-0.72 at 40.
- Verse herbal (Macer, name in line 1 82%): S 0.12-0.16 vs 0.04 (q99 0.09-0.12); power 0.25-0.32 at 110 pages.
- Heading-separated herbal (Culpeper): S 0.07 vs 0.04; power 0.21-0.42.
- Plain first-word page-uniqueness (Stolfi's measure) runs 0.39-0.58 in the Latin herbals and is not diagnostic alone; it is inflated by any positional rarity.

## Prediction (if Voynich herbal pages work like a Circa Instans-type herbal)
P1. S_voy exceeds its null q99 under BOTH nulls below, and lies in or above the Macer-Egerton band (>= 0.12).
P2. The page-confined line-1 type recurs on its own page (median own-page count >= 2) and is near-absent from other herbal pages (median share of other herbal pages containing it <= 0.01), matching Egerton (0.002-0.004).
P3. The effect holds in leave-one-quire-out: for each held-out herbal quire, S on that quire exceeds the null built from that quire alone, in >= 2/3 of quires.

## Nulls (both required)
N1. Shuffle tokens within page (destroys position, keeps page vocabulary). Reproduces the calibration null.
N2. Positional-rarity null (the L-069 confound): within each quire and each sheet (bifolium, F-51), permute the paragraph-initial (gallows) words among pages, and separately the rest of the tokens within page. If S survives N1 but not N2, the signal is gallows-word rarity, not a page-specific name. N2 is the decisive null.

## Planted-answer control (D-068 rule: recover >= 10 of 15)
Take the Voynich herbal pages at their real token counts and line layout; on k = 15 random seeds, overwrite one token in line 1 of each page with a fresh page-confined type and add r more copies at random later positions, r drawn from Egerton's own-page recurrence distribution (recurs >= 2 on 54-60% of chapters). Pass = S exceeds N2 q99 in >= 10/15 seeds. Also run the Macer-strength plant (recurrence on ~36%); if that fails, report the test as able to detect Circa Instans-strength naming only.

## Data and units (to be fixed at freeze, after D-072 clears)
ZL3b, RF1b, IT2a; herbal pages per the project section map; Currier A and B reported separately. Units: whole words and, as a second line, cores under two segmenters (X-01 is at risk; calibration shows a 4-letter collapse halves but keeps S). Page sizes: the real herbal token counts and line counts, read by the frozen script, not by hand.

## What would and would not follow
- P1-P3 pass and N2 passes: Voynich herbal pages carry a page-confined, line-1, self-recurring type, the slot a plant name occupies in a real herbal. This locates where a name crib should be tried; it does not read it.
- Pass N1, fail N2: the page-start signal is the rare paragraph-initial vocabulary already known (L-069); the "first word = plant name" reading gets no support from page confinement.
- Fail N1: Voynich herbal pages do not behave like a named-chapter herbal at the page start.

## Needs the lead's ruling
1. Whether this becomes part of item (d) or a separate external-anchor line, and its run id (s128 is claimed only for the calibration).
2. Whether N2 (permuting paragraph-initial words within quire/sheet) is the right positional-rarity null.
3. Whether to wait for Egerton/Fontana under D-072 (default: yes).
