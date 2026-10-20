"""Invariant tests for the Voynich battery (run: uv run python -m unittest discover -s tests)."""
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import analyze
import vparse


class ParserTests(unittest.TestCase):
    def test_corpus_loads(self):
        recs = vparse.load()
        words = [w for r in recs for w in r["words"]]
        self.assertGreater(len(recs), 5000)
        self.assertGreater(len(words), 30000)
        para = vparse.paragraph_text(recs)
        self.assertTrue(all(r["unit"].startswith("P") for r in para))

    def test_clean_alternatives(self):
        self.assertEqual(vparse.clean("a.[cth:oto]res.b"), ["a", "cthres", "b"])


class StatsTests(unittest.TestCase):
    def test_entropy_bounds(self):
        self.assertAlmostEqual(analyze.entropy(Counter("aaaa")), 0.0)
        self.assertAlmostEqual(analyze.entropy(Counter("ab")), 1.0)

    def test_substitution_preserves_ic(self):
        words = analyze.english_control()
        cipher = analyze.substitution_cipher(words)
        self.assertAlmostEqual(
            analyze.index_of_coincidence(analyze.char_stream(words)),
            analyze.index_of_coincidence(analyze.char_stream(cipher)),
            places=9,
        )
        self.assertEqual(Counter(words).most_common(1)[0][1],
                         Counter(cipher).most_common(1)[0][1])

    def test_solver_beats_random_on_known_cipher(self):
        words = analyze.english_control()
        model, alpha = analyze.bigram_model(words)
        cipher = analyze.substitution_cipher(words)
        solved, _m, _s, _n = analyze.solve_substitution(
            cipher, model, alpha, restarts=3, iters=1500)
        pairs = Counter(p for w in words for p in zip(w, w[1:]))
        identity = sum(c * model[p] for p, c in pairs.items()) / sum(pairs.values())
        # Solved cipher must land close to true-English score.
        self.assertGreater(solved, identity - 0.15)


if __name__ == "__main__":
    unittest.main()
