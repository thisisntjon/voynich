# READ THIS BEFORE results_s103.txt (lead note, 2026-10-18 13:23 PDT)

results_s103.txt ends with `VERDICT: NO MATCH at adequate power: copying drift excluded at this resolution`.
**That verdict is NOT accepted. The lead files s103 as INCONCLUSIVE (claim c-441, decision D-066 (i-result), learning L-211).**

Why:
1. The 'adequate power' bar (MDE top-1 <= 0.20) was chosen by the running agent; it was not frozen in D-066 (i).
2. The run's own positive control gains only +0.009 (part-shape) and +0.034 (whole-plant) over its control population, below the minimum detectable effect, so a real match would not have been detected.
3. The part-shape representation recovers the right species across two real herbals on only 1/130 top-1, and planted part-chimeras were not detected, so deliberate part-wise disguise was not tested.
4. Plant names were transcribed from images by agents at genus level and are unverified.

What s103 does support: the method matches whole plants across LJS 419 and Sloane 4016 (MRR 0.255 vs 0.035), and Voynich plants are not closer to these two herbals than unrelated period plants are. Nothing about copying drift, disguise or invention is established. Do not cite s103 as excluding anything.
