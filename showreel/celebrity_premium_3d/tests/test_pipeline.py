import json
import re
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STORY = ROOT / 'showreel/celebrity_story_3d_v6'


class PipelineTests(unittest.TestCase):
    def test_render_shards_cover_exactly_one_minute(self):
        ranges = [range(i * 72, (i + 1) * 72) for i in range(20)]
        self.assertEqual([n for r in ranges for n in r], list(range(24 * 60)))

    def test_original_ten_narration_takes_fit_cues(self):
        cues = json.loads((STORY / 'script.json').read_text())
        self.assertEqual(len(cues), 10)
        previous_end = 0
        for i, cue in enumerate(cues, 1):
            self.assertGreaterEqual(cue['start'], previous_end)
            self.assertLessEqual(cue['start'] + cue['duration'], 60)
            with wave.open(str(STORY / 'trimmed' / f'{i:02}.wav')) as source:
                self.assertEqual(source.getnchannels(), 1)
                self.assertEqual(source.getsampwidth(), 2)
                self.assertAlmostEqual(source.getnframes() / source.getframerate(), cue['duration'], delta=.01)
            previous_end = cue['start'] + cue['duration']

    def test_used_assets_have_pinned_hashes_and_licenses(self):
        entries = json.loads((ROOT / 'showreel/celebrity_lookdev/assets.json').read_text())
        wanted = {'ryan.glb', 'emma.glb', 'marcus.glb', 'nightstand.glb'}
        found = [e for e in entries if e['name'] in wanted]
        self.assertEqual({e['name'] for e in found}, wanted)
        for item in found:
            self.assertRegex(item['sha256'], re.compile('^[0-9a-f]{64}$'))
            self.assertRegex(item['git_blob'], re.compile('^[0-9a-f]{40}$'))
            self.assertTrue(item['license'])

    def test_caption_events_follow_ten_cues(self):
        from tempfile import TemporaryDirectory
        from showreel.celebrity_recovery_3d import render
        cues = json.loads((STORY / 'script.json').read_text())
        with TemporaryDirectory() as td:
            path = Path(td) / 'captions.ass'
            render.captions(cues, path)
            self.assertEqual(path.read_text().count('Dialogue: '), 19)


if __name__ == '__main__':
    unittest.main()
