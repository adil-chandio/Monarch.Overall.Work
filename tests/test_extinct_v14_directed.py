"""Full POV master technical contracts, not a creative/biological quality certificate."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path

R = Path(__file__).resolve().parents[1]
B = R / 'production/extinct-life/film-v14-directed'
OLD = B.parent / 'film-v9-full'


class DirectedMaster(unittest.TestCase):
    def setUp(self):
        self.m = json.loads((B / 'schedule.json').read_text())

    def test_entire_original_master_and_all_voice_assets(self):
        old = json.loads((OLD / 'schedule.json').read_text())
        for k in ['chapters', 'script_sha256', 'total_frames', 'duration_seconds', 'voice_id']:
            self.assertEqual(self.m[k], old[k])
        self.assertEqual((self.m['width'], self.m['height'], self.m['fps'], self.m['total_frames']),
                         (1920, 1080, 30, 13163))
        self.assertEqual(len(self.m['chapters']), 8)
        self.assertFalse(self.m['voice_speed_changed'])
        self.assertEqual(sum(c['frames'] for c in self.m['chapters']), 13163)
        for c in self.m['chapters']:
            self.assertEqual(hashlib.sha256((R / c['voice']).read_bytes()).hexdigest(), c['voice_sha256'])

    def test_contiguous_complete_narration_and_visual_coverage(self):
        q = self.m['sequences']
        self.assertEqual(q[0]['start_frame'], 0)
        self.assertEqual(q[-1]['end_frame'], 13163)
        for a, b in zip(q, q[1:]):
            self.assertEqual(a['end_frame'], b['start_frame'])
            self.assertLess(a['start_frame'], a['end_frame'])
        first_later = next(s for s in q if not s['id'].startswith('POV-OPEN-'))
        self.assertEqual(first_later['start_frame'], 1925)
        coverage = json.loads((B / 'coverage.json').read_text())
        old = json.loads((OLD / 'coverage.json').read_text())
        self.assertEqual(len(coverage['beats']), len(old['beats']))
        for c in coverage['beats']:
            self.assertEqual(c['implemented_3d_sequences'], [s['id'] for s in q
                if s['start_frame'] < c['end_frame'] and s['end_frame'] > c['start_frame']])
            self.assertTrue(c['implemented_3d_sequences'])

    def test_complete_original_subtitles(self):
        self.assertEqual((B / 'English.srt').read_bytes(), (OLD / 'English-v9.srt').read_bytes())
        self.assertIn('00:01:01,143', (B / 'English.srt').read_text())
        self.assertIn('00:07:', (B / 'English.srt').read_text())

    def test_assets_privacy_and_no_previous_film_plates(self):
        q = json.loads((B / 'ASSET-PROVENANCE.json').read_text())
        self.assertFalse(q['owner_reference']['redistributed'])
        self.assertFalse(q['previous_movie_frames_used'])
        self.assertFalse(q['image_plate_animation'])
        for asset in q['reused_assets']:
            self.assertEqual(hashlib.sha256((R / asset['path']).read_bytes()).hexdigest(), asset['sha256'])
        self.assertFalse((B / 'reference/owner-character-sheet.png').exists())
        self.assertIn("'human_full_watch_listen_claimed':False", (B / 'finish.py').read_text())

    def test_javascript_and_kinematics(self):
        for p in B.glob('*.mjs'):
            subprocess.run(['node', '--check', str(p)], check=True, capture_output=True)
        for name in ['motion.test.mjs', 'kinematics.test.mjs', 'direction.test.mjs']:
            subprocess.run(['node', str(B / name)], check=True, capture_output=True)

    def test_rendered_full_coverage_determinism_and_reachable_hands(self):
        p = R / '.cache/extinct-v14/seek-QC.json'
        if not p.exists():
            self.skipTest('Native --stills required; checked again after cloud preflight')
        q = json.loads(p.read_text())
        h = hashlib.sha256()
        for name in sorted(p.name for p in B.glob('*.mjs')) + ['schedule.json']:
            h.update(name.encode() + b'\0')
            h.update((B / name).read_bytes())
        self.assertEqual(q['source_fingerprint'], h.hexdigest(), 'Native QC must match this exact source')
        self.assertTrue(q['deterministic_seek'])
        self.assertTrue(q['subject_moves_with_frozen_camera'])
        self.assertEqual(q['page_errors'], [])
        samples = q['samples']
        self.assertEqual({v['sequence'] for v in samples}, {v['id'] for v in self.m['sequences']})
        self.assertTrue({1782, 1924, 1925, 13162}.issubset({v['frame'] for v in samples}))
        for v in samples:
            self.assertEqual(v['total_frames'], 13163)
            self.assertTrue(v['full_master'])
            if v['sequence'].startswith('FULL-') and v['world'] in ['coast', 'closing']:
                self.assertIs(v['hand_palms_visible'], True)
            for j in v.get('joints', []):
                self.assertAlmostEqual(j['a'], .3, places=5)
                self.assertAlmostEqual(j['b'], .3, places=5)
                self.assertFalse(j['clamped'], str(v['frame']))
        for v in samples:
            vis = v.get('visibility')
            if vis and (v['world'] == 'community' or vis['subject'] == 'goose'):
                self.assertGreaterEqual(vis['unobstructed_fraction'], .65, str(v['frame']))
                self.assertGreater(vis['width'], 110)
                self.assertGreater(vis['height'], 75)
        river = sorted([v for v in samples if v['world'] == 'river'], key=lambda v: v['frame'])
        self.assertGreater(sum((x-y)**2 for x, y in zip(river[0]['camera'], river[-1]['camera']))**.5, 2)


if __name__ == '__main__':
    unittest.main()
