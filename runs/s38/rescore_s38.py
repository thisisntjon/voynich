import sys, json
sys.path.insert(0, ".")
import n5_signature_discrimination as n5
for n in ["boxes_baseline","phys_touching_merged","phys_narrow_merged","phys_wide_plus_lifts"]:
    p = json.load(open(f"./runs/s38/s38_{n}.meta.json"))["pages"]
    r = n5.score(p); print(n, {k: round(v,4) if isinstance(v,float) else v for k,v in r.items()}, flush=True)
