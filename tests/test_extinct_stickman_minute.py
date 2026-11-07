"""Guard the authorized experiment's source timing, captions and untouched master relationship."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'production/extinct-life/film-v10-stickman'


class StickmanMinuteTests(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
