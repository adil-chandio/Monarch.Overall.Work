"""Guard the authorized experiment's source timing, captions and untouched master relationship."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'production/extinct-life/film-v11-pov'


class POVMinuteTests(unittest.TestCase):
    def test_native_format_and_source_timing(self):
        new = json.loads((BASE / 'schedule.json').read_text())
        old = json.loads((BASE.parent / 'film-v9-full/schedule.json').read_text())
        self.assertEqual((new['width'], new['height'], new['fps'], new['total_frames']),
                         (1920, 1080, 30, 1830))
        self.assertEqual(new['duration_seconds'], 61)
        self.assertFalse(new['voice_speed_changed'])
        self.assertEqual(new['voice_id'], old['voice_id'])
        self.assertEqual(new['script_sha256'], old['script_sha256'])
        self.assertEqual(new['chapters'], old['chapters'][:2])
        for chapter in new['chapters']:
            self.assertEqual(hashlib.sha256((ROOT / chapter['voice']).read_bytes()).hexdigest(),
                             chapter['voice_sha256'])
        self.assertEqual([c['start_frame'] for c in new['chapters']], [0, 1600])

    def test_sentence_complete_original_subtitles(self):
        old = (BASE.parent / 'film-v9-full/English-v9.srt').read_text().strip().split('\n\n')
        new = (BASE / 'English.srt').read_text().strip().split('\n\n')
        self.assertEqual(new, old[:18])
        self.assertIn('00:01:00,743', new[-1])
        self.assertTrue(new[-1].endswith('Living things shed biological material.'))
        self.assertIn('00:01:01,143', old[18])

    def test_asset_provenance_and_reference_privacy(self):
        q = json.loads((BASE / 'ASSET-PROVENANCE.json').read_text())
        self.assertFalse(q['owner_reference']['redistributed'])
        self.assertFalse(q['previous_movie_frames_used'])
        self.assertFalse(q['image_plate_animation'])
        for asset in q['reused_assets']:
            self.assertEqual(hashlib.sha256((ROOT / asset['path']).read_bytes()).hexdigest(), asset['sha256'])
        self.assertFalse((BASE / 'reference/owner-character-sheet.png').exists())

    def test_rendered_world_travel_and_reachable_hands(self):
        cache = ROOT / '.cache/extinct-v11/seek-QC.json'
        if not cache.exists():
            self.skipTest('Run native --stills first; source checks do not replace rendered checks')
        q = json.loads(cache.read_text())
        self.assertTrue(q['deterministic_seek'])
        self.assertTrue(q['subject_moves_with_frozen_camera'])
        self.assertEqual(q['page_errors'], [])
        samples = q['samples']
        self.assertGreaterEqual(len({v['world'] for v in samples}), 5)
        field = [v for v in samples if v['world'] == 'field']
        self.assertGreater(sum((a-b)**2 for a,b in zip(field[0]['camera'],field[-1]['camera']))**.5, 3)
        for v in samples:
            for joint in v['joints']:
                self.assertAlmostEqual(joint['a'], .3, places=5)
                self.assertAlmostEqual(joint['b'], .3, places=5)
                self.assertFalse(joint['clamped'])
        life = [v for v in samples if v['world'] == 'living-world']
        self.assertGreater(life[-1]['actor_position'][0] - life[0]['actor_position'][0], .9)


if __name__ == '__main__':
    unittest.main()
