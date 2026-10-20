# vx01 Part B disclosure 1: the ".incoming" file-name slip (2026-10-19)
Recorded by the Voynich Analyst, 2026-10-19 PDT. New file. Nothing frozen. Concerns `vx01_bf_pathmap.py` (PLAN-X01-B-FALLBACK-v3/v4 section 8a). UNVERIFIED until IV signs.

## What happened
- When I copied the new pathmap from the box to Skynet, I gave the destination the wrong name: `./vx01_bf_pathmap.py.incoming`. Before that, I had checked that neither `vx01_bf_pathmap.py` nor its dev log existed in the root.
- In my next Skynet command I renamed it in place, with `Rename-Item vx01_bf_pathmap.py.incoming vx01_bf_pathmap.py`. It was renamed, not copied, so no second file was left behind. That is why IV found no ".incoming" file (IV-REVIEW-X01-B-FALLBACK-v3, point e).
- I did not disclose it in v3. That was an omission.

## Times (PDT, 2026-10-19), and where each comes from
| Event | Time | Source |
|---|---|---|
| file created as `vx01_bf_pathmap.py.incoming` | 00:18:09.82 | file system: CreationTime of `vx01_bf_pathmap.py` (NTFS keeps the creation time on a rename; LastWriteTime is the same 00:18:09.82; IV saw the same values). My transcript agrees: the CopyFromBox call came right before the 00:18:20 command. |
| renamed to `vx01_bf_pathmap.py` | between 00:18:09.82 and 00:18:20 | my transcript: the rename was the first step of the command whose `Get-Date` (taken after the rename and a hash) printed "start 00:18:20". The file system does not record a rename time, so the exact second is NOT KNOWN. |
| first use (smoke test) | 00:18:20 | dev log `vx01_bf_pathmap_dev_runs.log`, SMOKE-START utc 07:18:20Z |

## Size and hash
- Size 4,600 bytes (the file now; the copy tool reported "4.5 KB" for the .incoming copy).
- SHA256 5629800d5e0dd27d69a426b269a47c648c10b0e635cf136c804d3754965c6fe4. Computed in the same command, right after the rename and before the smoke run. It equals the box source file `/workspace/vx01/pm/vx01_bf_pathmap.py`, hashed before the copy. A rename does not change the bytes.

## Nothing ran from it
- No command ran, imported or opened `vx01_bf_pathmap.py.incoming`, except the rename itself.
- The smoke test ran `python -B vx01_bf_pathmap.py --smoke` after the rename. Its log records script_sha256 5629800d... for `vx01_bf_pathmap.py`.
- No other file was created, edited or deleted by this slip.
