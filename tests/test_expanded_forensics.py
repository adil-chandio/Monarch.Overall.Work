"""Offline provenance/scope integrity, not science, retention, or quality tests."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/research/extinct-script-forensics/expanded'
DATA = ROOT / 'docs/research/data/extinct-expanded-study'

class ExpandedForensicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.register = json.loads((OUT / 'register.json').read_text())
        cls.api = json.loads((DATA / 'api-snapshot.json').read_text())
        cls.captions = json.loads((DATA / 'publisher-captions.json').read_text())

    def test_unique_cases_and_honest_coverage(self):
        r = self.register
        self.assertEqual(len(r['cases']), 19)
        self.assertEqual(len({c['case'] for c in r['cases']}), 19)
        self.assertEqual(r['complete_new_public_text_cases'], 17)
        self.assertEqual(r['partial_new_cases'], 2)
        partial = {c['case'] for c in r['cases'] if c['coverage_status'] != 'complete-public-text-read'}
        self.assertEqual(partial, {'M08', 'P04'})

    def test_api_identity_and_seven_complete_modern_scripts(self):
        videos = {v['id']: v for v in self.api['videos']}
        modern = [c for c in self.register['cases'] if c['case'].startswith('M')]
        self.assertEqual(len(modern), 8)
        self.assertEqual(sum(c['coverage_status'] == 'complete-public-text-read' for c in modern), 7)
        for c in modern:
            v = c['api_video']
            self.assertEqual(v['views'], videos[v['id']]['views'])
            self.assertGreaterEqual(v['views'], 1_000_000)
            self.assertIn(v['id'], c['source_url'])
        self.assertEqual(self.register['api_checked_at'], self.api['checked_at'])
        self.assertEqual(len(videos), self.register['api_video_records'])

    def test_cue_counts_are_separate_from_manual_beats(self):
        r = self.register
        self.assertEqual(sum(c['cue_count'] for c in self.captions['cases']), 4129)
        self.assertEqual(r['publisher_cue_derivatives'], 4129)
        self.assertEqual(sum(c['publisher_duration_seconds'] for c in self.captions['cases']), 10670)
        self.assertEqual(r['new_manual_analytical_beats'], 267)
        self.assertEqual(sum(c['manual_analytical_beats'] for c in r['cases']), 267)
        for c in r['cases']:
            self.assertEqual(c['manual_analytical_beats'], len(c['ordered_original_analysis']))
            self.assertIn('source order', c['timing_of_manual_beats'])

    def test_analysis_files_and_no_uninspected_gap_counted_as_beat(self):
        for c in self.register['cases']:
            text = (OUT / c['analysis_file']).read_text()
            self.assertIn(c['source_url'], text)
            self.assertGreater(c['analysis_word_count'], 250)
            self.assertFalse(any('Uninspected middle' in b for b in c['ordered_original_analysis']))
        self.assertIn('middle missing', (OUT / 'REPORT.md').read_text())

    def test_no_full_caption_text_or_descriptions_published(self):
        self.assertFalse(self.captions['raw_captions_published'])
        self.assertFalse(self.register['raw_competitor_scripts_published'])
        for c in self.captions['cases']:
            self.assertLessEqual(len(c.get('brief_opening_excerpt', '').split()), 13)
            for cue in c['cues']:
                self.assertNotIn('text', cue)
                self.assertIn('text_sha256', cue)
        for v in self.api['videos']:
            self.assertNotIn('description', v)
            self.assertNotIn('snippet', v)

    def test_no_playback_or_causal_retention_claim(self):
        self.assertFalse(self.register['causal_retention_claim'])
        self.assertFalse(self.api['playback_reviewed'])
        self.assertFalse(self.api['retention_access'])
        for c in self.register['cases']:
            self.assertFalse(c['playback_reviewed'])
            self.assertFalse(c['private_retention_available'])

    def test_reproducible_build(self):
        paths = [OUT / 'register.json', OUT / 'register.csv'] + [OUT / c['analysis_file'] for c in self.register['cases']]
        before = {p: p.read_bytes() for p in paths}
        spec = importlib.util.spec_from_file_location('expanded_builder', ROOT / 'scripts/build-expanded-forensics.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.build()
        self.assertEqual(before, {p: p.read_bytes() for p in paths})

if __name__ == '__main__':
    unittest.main(verbosity=2)
