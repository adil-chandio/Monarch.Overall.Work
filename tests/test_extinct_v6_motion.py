"""Identity/scope guardrails, not an artistic-quality or listening certificate."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'production/extinct-life/film-v6-motion'

class Moving3DRevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = json.loads((BASE / 'schedule.json').read_text())
        cls.master = json.loads((BASE.parent / 'film-v3/manifest.json').read_text())

    def test_master_script_identity_preserved(self):
        self.assertEqual(self.s['script_sha256'], self.master['script_sha256'])
        self.assertEqual(self.master['voice_id'], 'voice-02')
        self.assertFalse(self.master['voice_speed_changed'])

    def test_native_size_and_cadence(self):
        self.assertEqual([self.s[k] for k in ('width', 'height', 'fps')], [1920, 1080, 30])

    def test_selected_excerpt_not_claimed_as_full_film(self):
        self.assertFalse(self.s['full_film_complete'])
        self.assertLess(self.s['total_frames'], self.master['total_frames'])
        self.assertEqual(self.master['total_frames'], 13163)

    def test_all_excerpt_frames_covered_without_gap_or_overlap(self):
        cursor = 0
        for row in self.s['segments']:
            self.assertEqual(row['start_frame'], cursor)
            self.assertGreater(row['end_frame'], cursor)
            cursor = row['end_frame']
        self.assertEqual(cursor, self.s['total_frames'])

    def test_voice_samples_exactly_fit_selected_ranges(self):
        samples = sum(r['local_end_frame'] - r['local_start_frame'] for r in self.s['voice_clips'])
        self.assertEqual(samples, self.s['total_frames'])
        chapters = {r['id']: r for r in self.master['chapters']}
        for row in self.s['voice_clips']:
            self.assertGreaterEqual(row['local_start_frame'], 0)
            self.assertLessEqual(row['local_end_frame'], chapters[row['chapter']]['frames'])

    def test_not_rejected_image_plate_pipeline(self):
        self.assertFalse(self.s['rejected_v5_image_assets_used'])
        for name in ('scene.mjs', 'worlds.mjs', 'render.mjs'):
            text = (BASE / name).read_text()
            self.assertNotIn('film-v5-dev/style', text)
            self.assertNotIn('living-world-designed', text)
        self.assertIn('new T.Scene', (BASE / 'worlds.mjs').read_text())

    def test_composer_primary_source_and_credit_not_silently_substituted(self):
        music = json.loads((BASE / 'MUSIC-LICENSE.json').read_text())
        self.assertEqual(music['track'], 'Hiraeth')
        self.assertEqual(music['composer'], 'Scott Buckley')
        self.assertTrue(music['official_download'].startswith('https://www.scottbuckley.com.au/'))
        self.assertIn('CC-BY 4.0', music['required_credit'])
        self.assertFalse(music['listening_approval'])

if __name__ == '__main__':
    unittest.main()
