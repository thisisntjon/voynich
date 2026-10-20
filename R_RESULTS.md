> **Historical (superseded 2026-10-17 23:33).** Current state: `README.md` → `workflow/FINDINGS-REPORT.md`. Findings from this file are in `.inventory/registers/`.

# R-series results (this session: register diff + period attestation)

## R1 register extract (`r1_register_extract.py`, REGISTER-DIFF.md)
691 findings parsed; statuses tally matches site. See REGISTER-DIFF.md.

## R2 quid-pro-quo sharing (`r2_quidproquo.py`, `results_r2.txt`)
Source downloaded: School of Salernum (archive.org, 137,939 bytes,
SHA256 7243833611efa7dea4a25c7d14cc7bf1c0ef252abb6613fb076306c5c46ed6d3)
in `data/external/quid-pro-quo/` + `quid_pro_quo_pairs.csv` (8 rows).
Finding: this edition quotes the Quid pro Quo of Nicholas by example only
(4 entries, verified at lines 1011–1024 of the text). Within those,
many-to-one sharing is explicit: origanum substitutes for both abrotano
and absynthio, and abrotano/absynthio substitute for each other.
Verdict: genre + sharing structure period-attested in print; a usable
full table requires the Quid pro Quo text itself (referenced as NY
Hospital Nos. 6645/6646 with Platearius commentary) — not yet sourced.
1477 Benedetto item remains unverified (STEAL-VERIFY.md unchanged).

## Evidence corrections recorded (old claim → current view; originals preserved)

- Old: F3 flow residual favours encoded text over copying (F_RESULTS).
  New (builder N1/N2 + fable note): habit table at p=0.04–0.05 fakes the
  residual inside manuscript CI on 3/3 transcriptions; tonight's powered
  7k generator additionally fails F1 on 2/3 transcriptions, reopening F1.
  Meaning change: F1 residual is a benchmark, not a family discriminator.
  Downstream: OPPORTUNITY-NEXT Tier-2 language for F3 is superseded;
  J-series interpretation unaffected (independent controls).
- Old: hand-1 section NMI fails in habit generators (n4 first run).
  New (fable note; n6 files on disk): powered generator reversed n4,
  hand-1 NMI holds; Currier A inside natural range on coupling metrics
  where B is not (n6). Meaning change: A/B must be scored separately in
  all future boards (PREREG-v2 direction). Downstream: whole-manuscript
  joint-pass verdicts (incl. G0) should be re-read as B-dominated.
- Old (mine): B1 column-copying excess +1.9pp as support for visual copying.
  New (builder M1 direct coordinates): +0.41pp, CI crosses zero.
  Meaning change: column copying unproven; B1 retained as proxy result.
Reopen conditions: F1 re-closes only with a statistic habit tables fail
at matched types/hapax; A/B coupling split needs CREMMA real-line
controls per builder roadmap before interpretation.
