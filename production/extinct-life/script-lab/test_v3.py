"""Draft integrity checks, not scientific, translation, or entertainment proof."""
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

LAB = Path(__file__).resolve().parent
ROOT = LAB.parents[2]

class V3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.master = json.loads((LAB / 'master-v3.json').read_text())
        cls.validation = json.loads((LAB / 'validation-v3.json').read_text())

    def test_pairing_and_count(self):
        cs = self.master['chapters']
        self.assertEqual([c['id'] for c in cs], [f'B{i:02}' for i in range(1, 9)])
        self.assertTrue(all(c['en'] and c['ur'] and c['payoff'] for c in cs))
        self.assertEqual(sum(len(c['en'].split()) for c in cs), 1048)

    def test_documents_come_from_canonical_pairs(self):
        en = (LAB / 'ENGLISH-MASTER-v3.md').read_text()
        pair = (LAB / 'OWNER-REVIEW-v3.md').read_text()
        for c in self.master['chapters']:
            self.assertIn(c['en'], en)
            self.assertIn(c['en'], pair)
            self.assertIn(c['ur'], pair)

    def test_science_references_and_early_reveal(self):
        valid = {f'C{i:02}' for i in range(1, 14)}
        for c in self.master['chapters']:
            self.assertTrue(set(c['claim_ids']) <= valid)
        opening = self.master['chapters'][0]
        self.assertEqual(opening['en'].split()[1], 'mastodon')
        self.assertIn('2022', opening['en'])
        self.assertIn('بیس لاکھ', opening['ur'])
        self.assertIn('not a recovered afternoon', self.master['chapters'][5]['en'])
        self.assertIn('No signal is not the same as no animal', self.master['chapters'][6]['en'])
        self.assertIsNone(self.master['chapters'][-1]['bridge'])

    def test_hash_and_no_measured_audio_claim(self):
        v = self.validation
        self.assertEqual(v['master_sha256'], hashlib.sha256((LAB / 'master-v3.json').read_bytes()).hexdigest())
        self.assertIsNone(v['measured_v3_english_audio_seconds'])
        self.assertIsNone(v['measured_v3_urdu_audio_seconds'])
        self.assertFalse(v['retention_effect_verified'])
        self.assertFalse(v['cold_listener_tested'])
        self.assertFalse(v['finished_film_review'])

    def test_v2_preserved_and_render_on_hold(self):
        old = json.loads((LAB / 'master-v2.json').read_text())
        self.assertEqual(sum(len(c['en'].split()) for c in old['chapters']), 1045)
        self.assertTrue(all(a['en'] != b['en'] for a, b in zip(old['chapters'], self.master['chapters'])))
        sequence = json.loads((LAB.parent / 'feature-3d/sequence.json').read_text())
        self.assertFalse(sequence['render_enabled'])
        self.assertFalse(sequence['full_film_complete'])

    def test_reproducible_generation(self):
        paths = [LAB / name for name in ['ENGLISH-MASTER-v3.md', 'OWNER-REVIEW-v3.md', 'validation-v3.json']]
        before = {p: p.read_bytes() for p in paths}
        spec = importlib.util.spec_from_file_location('v3_builder', LAB / 'build_v3.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.build()
        self.assertEqual(before, {p: p.read_bytes() for p in paths})

if __name__ == '__main__':
    unittest.main(verbosity=2)
