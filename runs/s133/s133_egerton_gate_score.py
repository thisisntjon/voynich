"""s133: score the Egerton 747 caption gate, first read vs the Independent Verifier's second read (D-079, lead).

Frozen gate (SECOND_READER_PROTOCOL.md sha256 092254bc..., lines 30-31, quoted in deviation note v2):
  diplomatic first-item agreement >= 36/40 after a blind comparison permitting only case, whitespace, punctuation and
  explicitly recorded abbreviation-mark normalization; normalized first-item agreement >= 85% among rows where both
  readers supplied a normalized first item.
Deviation (deviation note v2 + lead ruling D-077 c / GATE-RULING 17:41Z): primary rows = second-read CSV positions
  5 6 9 14 16 17 18 19 22 23 26 27 29 30 31 33 34 36 38 39 40 (21 rows); T1 same proportion (>= 19/21, or 18/20);
  D-b rows blank/absent in either read are dropped from the diplomatic denominator; normalized gate 85% as a rate.
  Every report gives count, point estimate and 95% Clopper-Pearson interval; at n <= 21 no result clears 0.85 at
  95% confidence (L-365), so the call is labelled 'passes point threshold' never bare PASS.
First reads: rows <= 128 from Grok Bot's first-read CSVs; the 18 gate rows > 128 from the blind-read-1 packet v3
  response (fresh blind reader, D-079), joined to the second read on (page, box_index) via the sealed P-id key.
Diplomatic normalization (frozen here): Unicode NFD, drop combining marks (abbreviation macrons and tildes), lowercase,
  drop everything that is not a letter. 'Diplomatic first item' = first whitespace-separated token of the diplomatic
  caption, normalized; agreement = equal non-empty normalized first items.
Modes: fixture | score FIRSTREAD_PACKET_RESPONSE.csv
"""
import csv, glob, math, sys, unicodedata

SQ = "D:/Squire"
SECOND = f"{SQ}/SECOND_READER_RESPONSE_V1.csv"
FIRST_GROK = sorted(glob.glob(f"{SQ}/egerton747_caption_first_read_v1_range_rows*_grokbot_20261019.csv"))
KEY = "C:/Users/thisi/Desktop/Python/voynich/data/egerton_caption_gate/sealed/SEALED_KEY_blind_read_1_pid_to_row_v1.tsv"
PRIMARY = [5, 6, 9, 14, 16, 17, 18, 19, 22, 23, 26, 27, 29, 30, 31, 33, 34, 36, 38, 39, 40]
DIP_RATE, NORM_RATE = 36 / 40, 0.85


def nfirst(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    tok = s.split()
    return "".join(c for c in tok[0] if c.isalpha()) if tok else ""


def cp(k, n, a=0.05):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k)
    return lo, hi


def compare(pairs):
    """pairs: list of (first_row_dict, second_row_dict); returns counts and calls."""
    dk = dn = nk = nn = 0
    detail = []
    for f, s in pairs:
        df, ds = nfirst(f.get("diplomatic_caption")), nfirst(s.get("diplomatic_caption"))
        if df and ds:
            dn += 1
            dk += df == ds
        nf, ns = (f.get("normalized_first_item") or "").strip().lower(), (s.get("normalized_first_item") or "").strip().lower()
        if nf and ns:
            nn += 1
            nk += nf == ns
        detail.append((s.get("page"), s.get("box_index"), df, ds, nf, ns))
    return dk, dn, nk, nn, detail


def report(dk, dn, nk, nn):
    need = math.ceil(DIP_RATE * dn - 1e-9) if dn else None
    dpass = dn > 0 and dk >= need
    npass = nn > 0 and nk / nn >= NORM_RATE
    lo, hi = cp(dk, dn) if dn else (0, 0)
    print(f"diplomatic first item: {dk}/{dn} (point {dk / dn if dn else 0:.3f}; T1 needs >= {need}; 95% CP [{lo:.3f}, {hi:.3f}])"
          f" -> {'passes point threshold' if dpass else 'below point threshold'}")
    lo, hi = cp(nk, nn) if nn else (0, 0)
    print(f"normalized first item: {nk}/{nn} (point {nk / nn if nn else 0:.3f}; needs >= 0.85; 95% CP [{lo:.3f}, {hi:.3f}])"
          f" -> {'passes point threshold' if npass else 'below point threshold'}")
    call = "BOTH_PASS_POINT_THRESHOLDS" if dpass and npass else "GATE_NOT_PASSED"
    print(f"CALL={call} (interval caveat: n <= 21 cannot show 0.85 at 95% confidence, L-365)")
    return call


def fixture():
    # diplomatic pair differing only in case, punctuation and an abbreviation mark (mark stripped, never expanded)
    a = {"diplomatic_caption": "Apiū ranīnū", "normalized_first_item": "apium"}
    b = {"diplomatic_caption": "apiu, raninu", "normalized_first_item": "apium"}
    c = {"diplomatic_caption": "Atriplex", "normalized_first_item": "atriplex"}
    print("nfirst normalisation:", nfirst("Apiū ranīnū"), nfirst("apiu, raninu"), nfirst("apium"))
    print("-- 21 agreeing pairs (expect pass)")
    r1 = report(*compare([(a, b)] * 21)[:4])
    print("-- 15 agree, 6 disagree (expect not passed)")
    r2 = report(*compare([(a, b)] * 15 + [(a, c)] * 6)[:4])
    print("-- blanks dropped (D-b): 20 agree + 1 blank (expect 20/20 pass)")
    r3 = report(*compare([(a, b)] * 20 + [({"diplomatic_caption": ""}, b)])[:4])
    print("-- 18/20 diplomatic boundary (expect pass) and 17/20 (expect not passed)")
    r4 = report(*compare([(a, b)] * 18 + [(a, c)] * 2)[:4][:2], 1, 1)
    r5 = report(*compare([(a, b)] * 17 + [(a, c)] * 3)[:4][:2], 1, 1)
    ok = (r1, r2, r3, r4, r5) == ("BOTH_PASS_POINT_THRESHOLDS", "GATE_NOT_PASSED", "BOTH_PASS_POINT_THRESHOLDS",
                                  "BOTH_PASS_POINT_THRESHOLDS", "GATE_NOT_PASSED")
    print("CONTROL_PASS" if ok else "CONTROL_FAIL")


def score(packet_resp):
    second = list(csv.DictReader(open(SECOND, encoding="utf-8")))
    prim = [second[i - 1] for i in PRIMARY]
    grok = [r for f in FIRST_GROK for r in csv.DictReader(open(f, encoding="utf-8"))]
    key = [r for r in csv.DictReader((l for l in open(KEY, encoding="utf-8") if not l.startswith("#")), delimiter="\t")]
    resp = {r["packet_id"]: r for r in csv.DictReader(open(packet_resp, encoding="utf-8"))}
    by_pb = {}
    for r in grok:
        by_pb[(r["page"], str(r["box_index"]))] = r
    for k in key:
        if k["role"] == "gate" and k["packet_id"] in resp:
            by_pb[(k["page"], str(k["box_index"]))] = resp[k["packet_id"]]
    pairs, missing = [], []
    for s in prim:
        f = by_pb.get((s["page"], str(s["box_index"])))
        (pairs.append((f, s)) if f else missing.append((s["page"], s["box_index"])))
    print(f"primary rows {len(prim)}; first reads found {len(pairs)}; missing {missing}")
    dk, dn, nk, nn, detail = compare(pairs)
    for d in detail:
        print("  ", d)
    if missing:
        print("CALL=INCOMPLETE (missing first reads; gate not scored)")
        return
    report(dk, dn, nk, nn)


if __name__ == "__main__":
    fixture() if sys.argv[1] == "fixture" else score(sys.argv[2])
