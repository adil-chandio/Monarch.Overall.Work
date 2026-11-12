"""Small consistency checks, not a substitute for playback/listening review."""
import json
import unittest
import numpy as np
from showreel.celebrity_recovery_3d import render


class RebuildTest(unittest.TestCase):
    def test_script_and_captions_are_the_original_ten_cues(self):
        cues = json.loads((render.V6 / 'script.json').read_text())
        self.assertEqual(len(cues), 10)
        self.assertEqual(len(render.CAPTIONS), len(cues))
        for cue, parts, split in zip(cues, render.CAPTIONS, render.SPLITS):
            actual = ' '.join(' '.join(parts).replace('\\N', ' ').split())
            self.assertEqual(actual, ' '.join(cue['text'].split()))
            if split is not None:
                self.assertLess(split, cue['duration'])
                self.assertGreater(split, 0)
        self.assertLess(cues[-1]['start'] + cues[-1]['duration'], 60)
        self.assertEqual(render.FPS * 60, 1440)

    def test_ik_preserves_bone_lengths_when_target_is_out_of_reach(self):
        start = render.vec((0, 0, 0))
        for target in ((0, 0, -.3), (1.2, -.1, -.1), (.2, -.3, -.1)):
            elbow, end = render.bone_joint(start, target, .30, .27, (0, 0, -1))
            self.assertAlmostEqual(np.linalg.norm(elbow-start), .30, places=5)
            self.assertAlmostEqual(np.linalg.norm(end-elbow), .27, places=5)

    def test_rendered_actions_are_not_static_frames(self):
        film=render.Film()
        try:
            for early,late in ((3,8),(26,28),(40.5,42),(47,49)):
                a,b=film.render(early),film.render(late)
                self.assertEqual(a.shape,(568,320,3))
                self.assertGreater(float(np.abs(a.astype(float)-b.astype(float)).mean()),1.0)
        finally:
            if film.w:film.w.close()


if __name__ == '__main__':
    unittest.main()
