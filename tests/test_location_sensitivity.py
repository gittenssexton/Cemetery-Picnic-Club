"""Synthetic-independent validation of Pine Grove location cross-check records.

This tests data consistency, not actual geology or surveyed position.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class PineGroveSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'pine_grove_location_sensitivity.json').read_text())

    def test_two_unsurveyed_references_have_distinct_sources(self):
        points = self.data['references']
        self.assertEqual(len(points), 2)
        self.assertEqual(len({p['source'] for p in points}), 2)
        self.assertTrue(all(p['point_status'] == 'published_unsurveyed_reference' for p in points))

    def test_both_published_points_intersect_same_mapped_symbol(self):
        for point in self.data['references']:
            self.assertEqual([m['symbol'] for m in point['polygon_hits']], ['Ops'])

    def test_boundary_distance_is_far_less_than_source_uncertainty(self):
        uncertainty = self.data['source_accuracy_m_estimate']
        self.assertGreater(uncertainty, 1000)
        self.assertTrue(all(p['polygon_hits'][0]['edge_distance_m'] < uncertainty for p in self.data['references']))
        self.assertGreater(self.data['reference_separation_m'], 50)

    def test_neither_claims_quarry_or_survey(self):
        self.assertIn('neither', self.data['interpretation'].lower())
        self.assertIn('neither point is a survey', self.data['verification'].lower())

if __name__ == '__main__': unittest.main()