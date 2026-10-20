"""Reproduction tests: scoreboard.score_v2 must give the numbers printed in the
filed results files, to the precision printed there.

Run:  python -m unittest tests.test_score -v        (from the project root)

Tolerance rule: a printed value with d decimals is matched to +-0.5e-d
(exactly the printed precision). The only looser checks are the ones
whose originals depend on a random-number state the scorer cannot share:
  * b3 C4 shuffle deltas for NON-first corpora: b3 used one Random(7) across
    all corpora in sequence, so only voynich_eva (first) is bit-exact;
    controls are checked to +-0.01 (observed drift <=0.001).
  * b5 permutation-null mean/p99 for the CTRL rows: b5 shared one
    default_rng(0) across every block before the controls; checked to
    +-0.005 (200 draws; observed drift <=0.002). Observed NMI and the
    rotation null are deterministic and checked exactly.
  * a2 page-first gallows: the original counted '?'-containing words; the
    Corpus drops them. Exact reproduction is checked on a
    drop_unclear=False corpus; the standard corpus value is recorded in
    scoreboard/REPRODUCTION.md and only loosely checked here (+-1.5 pp).
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scoreboard.corpus import Corpus          # noqa: E402
from scoreboard import score_v2 as S             # noqa: E402

_cache = {}


def corpus(key):
    if key not in _cache:
        if key == "voynich":
            _cache[key] = Corpus.from_voynich()
        elif key == "voynich_raw":
            _cache[key] = Corpus.from_voynich(drop_unclear=False)
        elif key.startswith("voynich:"):
            _cache[key] = Corpus.from_voynich(tokenization=key.split(":")[1])
        elif key.endswith(":verse"):
            _cache[key] = Corpus.from_control(key[:-6], lines="verse")
        elif key.endswith(":sections"):
            from scoreboard.run import SECTION_HEADERS
            n = key[:-9]
            _cache[key] = Corpus.from_control_sections(n, SECTION_HEADERS[n])
        else:
            _cache[key] = Corpus.from_control(key)
    return _cache[key]


def full(key, skip_nmf=True):
    k = (key, skip_nmf)
    if k not in _cache:
        _cache[k] = S.score(corpus(key), skip_nmf=skip_nmf)
    return _cache[k]


class Repro(unittest.TestCase):
    def printed(self, got, want, what="", tol=None):
        """want is the printed string, e.g. '2.126' or '-1.047' or 'x17.89'."""
        s = str(want).lstrip("x").rstrip("%")
        m = re.search(r"\.(\d+)$", s)
        if tol is None:
            tol = 0.5 * 10 ** -(len(m.group(1)) if m else 0) + 1e-12
        self.assertIsNotNone(got, what)
        self.assertAlmostEqual(float(got), float(s), delta=tol,
                               msg=f"{what}: got {got} want {want} (+-{tol:g})")

    def rows(self, got, wants, prefix):
        for key, want in wants.items():
            with self.subTest(metric=f"{prefix}.{key}"):
                self.printed(got[key], want, f"{prefix}.{key}")


# ----------------------------------------------------------------- a1 -----
A1 = {  # results_a1.txt
    "voynich": dict(tokens="25000", types="5417", hapax="0.679", mean_len="4.888",
                    sd_len="1.764", alpha="26", h1="3.863", h2="2.126", h3="1.855",
                    zipf="-1.047", redup_pct="0.896", top10_pct="13.808"),
    "voynich:glyph": dict(mean_len="4.334", sd_len="1.610", alpha="32", h1="3.862",
                          h2="2.263", h3="2.022"),
    "voynich:glyph+": dict(mean_len="3.957", sd_len="1.435", alpha="38", h1="3.892",
                           h2="2.397", h3="2.161"),
    "latin_caesar": dict(tokens="19520", types="5491", hapax="0.612", mean_len="6.011",
                         sd_len="2.905", alpha="25", h1="4.009", h2="3.295", h3="2.617",
                         zipf="-0.856", redup_pct="0.000", top10_pct="12.992"),
    "italian_dante": dict(tokens="25000", types="5323", hapax="0.645", mean_len="3.932",
                          sd_len="2.241", alpha="23", h1="3.929", h2="3.107", h3="2.625",
                          zipf="-1.037", redup_pct="0.048", top10_pct="23.140"),
}


class TestA1Profile(Repro):
    def test_profile(self):
        for key, wants in A1.items():
            got = S.profile(corpus(key).words())
            self.rows(got, wants, f"a1.{key}")


# ----------------------------------------------------------------- a2 -----
A2 = {  # results_a2.txt: feature -> (jsd_first, null mean, std, jsd_last, null mean, std)
    "voynich": {
        "first_glyph": ("0.1759", "0.0019", "0.0005", "0.0363", "0.0020", "0.0005"),
        "last_glyph": ("0.0143", "0.0013", "0.0003", "0.0820", "0.0012", "0.0004"),
        "length": ("0.0217", "0.0007", "0.0003", "0.0124", "0.0008", "0.0003")},
    "italian_dante:verse": {
        "first_glyph": ("0.0337", "0.0009", "0.0003", "0.0686", "0.0010", "0.0002"),
        "last_glyph": ("0.0185", "0.0010", "0.0003", "0.1673", "0.0009", "0.0003"),
        "length": ("0.0062", "0.0013", "0.0005", "0.3050", "0.0013", "0.0004")},
}


class TestA2Position(Repro):
    def test_jsd_and_null(self):
        for key, feats in A2.items():
            pos = full(key)["position_all"]
            for feat, (jf, nfm, nfs, jl, nlm, nls) in feats.items():
                g = pos[feat]
                self.rows(g, dict(jsd_first=jf, null_first_mean=nfm, null_first_std=nfs,
                                  jsd_last=jl, null_last_mean=nlm, null_last_std=nls),
                          f"a2.{key}.{feat}")

    def test_enrichment_table(self):
        en = full("voynich")["position_all"]["enrich"]
        first = {r["glyph"]: r for r in en["first_table"]}
        last = {r["glyph"]: r for r in en["last_table"]}
        for g, want in dict(d="2.10", s="1.20", y="4.00", o="0.64", q="0.79", t="5.12",
                            p="17.89", c="0.18", k="0.70", l="0.41").items():
            with self.subTest(first=g):
                self.printed(first[g]["ratio"], want, f"a2 first {g}")
        for g, want in dict(y="0.92", m="16.31", n="0.95", l="0.67", r="0.58", s="1.09",
                            d="1.70", g="25.47", o="0.40", a="1.14").items():
            with self.subTest(last=g):
                self.printed(last[g]["ratio"], want, f"a2 last {g}")
        self.printed(en["fixed_first_ratio"], "17.89", "p fixed")
        self.printed(en["fixed_last_ratio"], "16.31", "m fixed")
        self.assertEqual((en["max_first_glyph"], en["max_last_glyph"]), ("p", "g"))
        self.printed(en["max_last_ratio"], "25.47", "max last")

    def test_page_first_gallows_raw(self):
        g = S.page_first_gallows(corpus("voynich_raw"))
        self.rows(g, dict(gallows_pagefirst_pct="85.99", gallows_other_pct="18.61",
                          pf_pagefirst_pct="48.31", pf_other_pct="7.93"), "a2.gallows.raw")

    def test_page_first_gallows_standard_corpus_close(self):
        g = full("voynich")["page_first_gallows"]
        self.printed(g["gallows_pagefirst_pct"], "85.99", "gallows std corpus", tol=1.5)
        self.printed(g["gallows_other_pct"], "18.61", "gallows other std corpus", tol=1.5)


# ---------------------------------------------------------------- a4b -----
class TestA4bNearCopy(Repro):
    def test_voynich_matched(self):
        nc = full("voynich")["near_copy"]
        self.rows(nc["matched_w10"], dict(exact_loc="0.079", exact_far="0.047", exact_ratio="1.69",
                                          d1_loc="0.210", d1_far="0.162", d1_ratio="1.30",
                                          le1_loc="0.289", le1_far="0.208", le1_ratio="1.39"),
                  "a4b.W10")
        self.rows(nc["matched_w40"], dict(exact_loc="0.210", exact_far="0.147", exact_ratio="1.42",
                                          d1_loc="0.357", d1_far="0.331", d1_ratio="1.08",
                                          le1_loc="0.567", le1_far="0.478", le1_ratio="1.18"),
                  "a4b.W40")

    def test_controls_unmatched(self):
        for key, w in {"latin_caesar": ("1.19", "1.08", "1.12"),
                       "italian_dante": ("0.96", "1.00", "0.99")}.items():
            got = S.near_copy_unmatched(corpus(key).words(), 10)
            self.rows(got, dict(exact_ratio=w[0], d1_ratio=w[1], le1_ratio=w[2]), f"a4b.{key}")


# ----------------------------------------------------------------- a7 -----
class TestA7Abbrev(Repro):
    def test_rows(self):
        for key, w in {"voynich": ("-0.248", "4.00", "4.89", "0.82"),
                       "voynich:glyph+": ("-0.243", "3.24", "3.96", "0.82"),
                       "latin_caesar": ("-0.344", "3.58", "6.01", "0.60"),
                       "italian_dante": ("-0.374", "2.48", "3.93", "0.63")}.items():
            got = S.abbreviation(corpus(key).words())
            self.rows(got, dict(rho=w[0], top50_len=w[1], token_mean_len=w[2], ratio=w[3]),
                      f"a7.{key}")


# ------------------------------------------------------------- b1 T2 -----
class TestB1ColumnCopy(Repro):
    def test_t2(self):
        got = full("voynich")["column_copy"]
        self.assertEqual((got["n_col"], got["n_off"], got["n_far"]), (30941, 17745, 29009))
        self.rows(got, dict(exact_col_pct="2.57", exact_off_pct="1.96", exact_far_pct="1.94",
                            near_col_pct="10.69", near_off_pct="8.79", near_far_pct="8.80",
                            near_col_over_far="1.21", near_col_over_off="1.22"), "b1.T2")


# ---------------------------------------------------------- b3 C3, C4 -----
B3_C3 = {"voynich": (2, [("n", "0.99"), ("m", "0.97"), ("y", "0.87"), ("r", "0.82"), ("l", "0.60"), ("s", "0.17")]),
         "latin_caesar": (0, [("m", "0.51"), ("s", "0.41"), ("x", "0.32"), ("t", "0.29"), ("d", "0.21"), ("e", "0.21")]),
         "italian_dante": (0, [("e", "0.50"), ("a", "0.46"), ("o", "0.45"), ("i", "0.42"), ("l", "0.28"), ("n", "0.25")])}
B3_C4 = {"voynich": ("2.126", "2.126", "+0.000", "3.610", "+1.484", None),
         "latin_caesar": ("3.295", "3.295", "+0.000", "3.927", "+0.633", 0.01),
         "italian_dante": ("3.107", "3.107", "-0.000", "3.742", "+0.635", 0.01)}


class TestB3Slots(Repro):
    def test_c3_final_restriction(self):
        for key, (n90, top) in B3_C3.items():
            got = S.final_restriction(corpus(key).words())
            self.assertEqual(got["n_ge90"], n90, key)
            self.assertEqual([g for g, _ in got["top"]], [g for g, _ in top], key)
            for (g, want), (_, share) in zip(top, got["top"]):
                with self.subTest(corpus=key, glyph=g):
                    self.printed(share, want, f"b3.C3.{key}.{g}")

    def test_c4_shuffle_deltas(self):
        for key, (o, ws, dw, cs, dc, tol) in B3_C4.items():
            got = S.shuffle_h2(corpus(key).words())
            self.printed(got["h2"], o, f"b3.C4.{key}.h2")
            self.printed(got["word_shuffled"], ws, f"b3.C4.{key}.word_shuffled")
            self.printed(got["d_word_shuffle"], dw, f"b3.C4.{key}.d_word", tol)
            self.printed(got["char_shuffled"], cs, f"b3.C4.{key}.char_shuffled", tol)
            self.printed(got["d_char_shuffle"], dc, f"b3.C4.{key}.d_char", tol)


# ----------------------------------------------------------------- b4 -----
class TestB4Body(Repro):
    def test_voynich_row(self):
        got = full("voynich")["position_body"]
        self.rows(got, dict(jsd_first="0.1722", null_first="0.0019", jsd_last="0.0839",
                            null_last="0.0013", p_init_ratio="15.97", m_final_ratio="16.55",
                            h2="2.093", repeat_pct="0.87", samecol_edit_le1="0.044",
                            tokens="33053"), "b4.VOYNICH")

    def test_ctrl_dante_row(self):
        # b4 CTRL_dante: all verse lines (no page-first exclusion), null n=20
        r = full("italian_dante:verse")
        pos = r["position_all"]
        self.printed(pos["first_glyph"]["jsd_first"], "0.0337", "b4.dante.jsdfirst")
        self.printed(pos["first_glyph"]["null20_first_mean"], "0.0009", "b4.dante.null_first")
        self.printed(pos["last_glyph"]["jsd_last"], "0.1673", "b4.dante.jsdlast")
        self.printed(pos["last_glyph"]["null20_last_mean"], "0.0009", "b4.dante.null_last")
        self.printed(pos["enrich"]["fixed_first_ratio"], "1.23", "b4.dante.p")
        self.printed(pos["enrich"]["fixed_last_ratio"], "0.00", "b4.dante.m")
        self.printed(r["h2_all_tokens"], "3.108", "b4.dante.h2")
        w = corpus("italian_dante:verse").words()
        self.assertEqual(len(w), 36104)
        self.printed(100 * sum(a == b for a, b in zip(w, w[1:])) / len(w), "0.05", "b4.dante.repeat")


# ----------------------------------------------------------------- b5 -----
class TestB5NMF(Repro):
    def test_voynich_block(self):
        nmf = full("voynich", skip_nmf=False)["nmf"]
        self.assertEqual(nmf["chunks"], 871)
        self.rows(nmf["section"], dict(nmi="0.379", perm_mean="0.055", perm_p99="0.078",
                                       rot_mean="0.165", rot_max="0.373", rot_p="0.000"), "b5.illus")
        self.rows(nmf["hand"], dict(nmi="0.375", perm_mean="0.043", perm_p99="0.069",
                                    rot_mean="0.125", rot_max="0.273", rot_p="0.000"), "b5.hand")
        self.rows(nmf["lang"], dict(nmi="0.346", perm_mean="0.021", perm_p99="0.045",
                                    rot_mean="0.072", rot_max="0.230", rot_p="0.000"), "b5.lang")
        wh = nmf["within_hand"]
        self.assertEqual(set(wh), {"1", "2"})
        self.assertEqual(wh["1"]["sections"], {"H": 201, "P": 58})
        self.assertEqual(wh["2"]["sections"], {"B": 156, "H": 58, "T": 44})
        self.rows(wh["1"], dict(nmi="0.275", perm_mean="0.014", perm_p99="0.040",
                                rot_mean="0.056", rot_max="0.271", rot_p="0.000"), "b5.hand1")
        self.rows(wh["2"], dict(nmi="0.333", perm_mean="0.045", perm_p99="0.104",
                                rot_mean="0.146", rot_max="0.376", rot_p="0.048"), "b5.hand2")

    def test_controls(self):
        for key, (n, w) in {"italian_dante:sections": (2552, ("0.017", "0.002", "0.004", "0.011", "0.017", "0.022")),
                            "latin_augustine:sections": (3414, ("0.155", "0.015", "0.020", "0.181", "0.273", "0.575"))}.items():
            got = S.nmf_topics(corpus(key))
            self.assertEqual(got["chunks"], n)
            sec = got["section"]
            self.printed(sec["nmi"], w[0], f"b5.{key}.nmi")
            self.printed(sec["perm_mean"], w[1], f"b5.{key}.perm_mean", tol=0.005)
            self.printed(sec["perm_p99"], w[2], f"b5.{key}.perm_p99", tol=0.005)
            self.printed(sec["rot_mean"], w[3], f"b5.{key}.rot_mean")
            self.printed(sec["rot_max"], w[4], f"b5.{key}.rot_max")
            self.printed(sec["rot_p"], w[5], f"b5.{key}.rot_p")


# ------------------------------------------------------- infrastructure -----
class TestInfra(unittest.TestCase):
    def test_meta_json_roundtrip(self):
        import json, tempfile
        pages = [dict(id="p1", section="H", hand="1", lines=[["a", "b", "c"], ["d", "e", "f"]]),
                 dict(id="p2", section="S", lines=[["g", "h", "i"]])]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.meta.json"
            p.write_text(json.dumps(dict(pages=pages)), encoding="utf-8")
            c = Corpus.from_meta_json(p)
        self.assertEqual(c.words(), list("abcdefghi"))
        self.assertEqual([pg["section"] for pg in c.pages], ["H", "S"])
        self.assertEqual(c.pages[1]["hand"], "?")

    def test_flat_wordlist_has_no_line_metrics(self):
        r = S.score(Corpus.from_wordlist(["ab", "cd"] * 3000), skip_nmf=True)
        self.assertIsNone(r["position_all"])
        self.assertIsNotNone(r["profile"]["h2"])

    def test_v1_api_still_exported(self):
        c = corpus("voynich")
        row = S.score_corpus("voynich_eva", c.words(), c.lines())
        self.assertAlmostEqual(row["h2"], 2.1262, places=4)
        self.assertAlmostEqual(row["jsd_first_fg"], 0.1759, places=4)


if __name__ == "__main__":
    unittest.main()
