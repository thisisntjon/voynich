# vx01_bf_DISCLOSURE_2: wrong time on plan line 167
Date 2026-10-19 (PDT). Author: Voynich Analyst for Jon. UNVERIFIED until IV accepts.
Plan: PLAN-X01-B-FALLBACK-v5.md, cited by SHA256 4ed0314a7c8aef4d925dee4fbab3ef8eca3a005352062563e3708a0273e63f3e (its title line still reads v4; IV-REVIEW-X01-B-FALLBACK-v5 nit 1). The plan is NOT edited.

## What is wrong
v5 line 167 (the "Environment pin" bullet; line 168 in a 1-based file view) says the pin values were re-checked read-only on Skynet "2026-10-19 ~01:00 PDT". That is false. 01:00 PDT had not come yet when the plan was written and hashed.

## True time (from file times; no log kept the second)
- IV-REVIEW-X01-B-FALLBACK-v4.md (the must-fix that asked for the pin) landed on the box at 00:43:55 PDT.
- PLAN-X01-B-FALLBACK-v5.md was written on the box at 00:46:09 PDT (box mtime); its Skynet backup copy at 00:46:16 PDT.
- So the re-check (Get-FileHash on python.exe and sitecustomize.py, python -VV, importlib.metadata.version for 21 distributions) ran between 00:43:55 and 00:46:09 PDT, about 00:45 PDT, as IV said.
- No dev log, stdout file or record of that re-check was kept, so I cannot give the exact second. That is a gap, stated here.

## Effect
None on any hash, value or rule. The values in v5 were right: IV re-read them at 00:46 PDT and they matched, and I re-read them again read-only at 00:49:20 PDT on 2026-10-19 (exe 5F7B89A6...52EC, -VV string as in v5, sitecustomize 14BAE2B6...E113, all 21 distribution versions as in v5). Only the time words on line 167 are wrong. The stub takes the pin at freeze, not from line 167.
