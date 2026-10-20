import itertools
import unittest
import numpy as np
from experiments.medieval_line_controls.run import Edges, holm, parse_xml, symbols, tokens


class MedievalLinesTests(unittest.TestCase):
    def test_abbreviations_and_punctuation(self):
        self.assertEqual(tokens('Quo\u0303, ⁊ ꝑter.\uf1ac 123'), ['quo\u0303', '⁊', 'ꝑter', '\uf1ac'])
        self.assertEqual(symbols('quo\u0303'), ['q', 'u', 'o\u0303'])
        self.assertEqual(tokens('Quo\u0303', 'strip'), ['quo'])
        self.assertEqual(tokens('Quo\u0303', 'case'), ['Quo\u0303'])

    def test_zone_and_line_filters(self):
        raw = '''<alto xmlns="http://www.loc.gov/standards/alto/ns-v4#"><Tags>
        <OtherTag ID="m" LABEL="MainZone"/><OtherTag ID="d" LABEL="DefaultLine"/>
        <OtherTag ID="h" LABEL="HeadingLine"/></Tags><Layout>
        <TextBlock TAGREFS="m"><TextLine TAGREFS="d"><String CONTENT="a b c"/></TextLine>
        <TextLine TAGREFS="d"><String CONTENT="a b"/></TextLine>
        <TextLine TAGREFS="h"><String CONTENT="d e f"/></TextLine></TextBlock>
        <TextBlock><TextLine TAGREFS="d"><String CONTENT="g h i"/></TextLine></TextBlock>
        </Layout></alto>'''
        ls, qc = parse_xml(raw)
        self.assertEqual(ls, [['a', 'b', 'c']])
        self.assertEqual(qc, dict(all_xml_lines=4, excluded_short=1,
                                 excluded_zone_or_type=2, retained_lines=1))

    def test_exact_edge_null_matches_enumerated_permutations(self):
        words = ['ab', 'ac', 'db', 'dc']
        exact = np.mean([Edges([list(p)]).observed() for p in itertools.permutations(words)], axis=0)
        e = Edges([words])
        edges = np.mean([e.at(np.array([a]), np.array([b])) for a in range(4)
                         for b in range(4) if a != b], axis=0)
        np.testing.assert_allclose(exact, edges, atol=1e-12)

    def test_planted_initial_marker_and_constant_null(self):
        e = Edges([['ax', 'by', 'bz', 'bw']]*100)
        self.assertAlmostEqual(e.observed()[0], 1.0)
        self.assertLess(e.null(np.random.default_rng(1), 99)[:, 0].mean(), .02)
        e = Edges([['aa', 'aa', 'aa']]*10 + [['x', 'y']])
        np.testing.assert_equal(e.observed(), [0., 0.])

    def test_holm(self):
        np.testing.assert_allclose(holm([.01, .04, .03]), [.03, .06, .06])


if __name__ == '__main__':
    unittest.main()
