import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / 'showreel/celebrity_cinematic_3d'
STORY = ROOT / 'showreel/celebrity_story_3d_v6'


class CinematicPipelineTests(unittest.TestCase):
    def test_release_assets_are_pinned_and_licensed(self):
        manifest = json.loads((HERE / 'assets.json').read_text())
        self.assertEqual({a['name'] for a in manifest},
                         {'materials.glb', 'planter.glb', 'streetLamp.glb', 'vase.glb', 'car.glb'})
        for asset in manifest:
            self.assertRegex(asset['sha256'], re.compile(r'^[a-f0-9]{64}$'))
            self.assertGreater(asset['release_asset'], 0)
            self.assertTrue(asset['license'])
            self.assertTrue(asset['source'].startswith('https://'))
        self.assertIn('CC BY 4.0', next(a for a in manifest if a['name'] == 'car.glb')['license'])
        credits = (HERE / 'ASSET_CREDITS.txt').read_text()
        self.assertIn('DanielZhabotinsky', credits)
        self.assertIn('https://creativecommons.org/licenses/by/4.0/', credits)

    def test_story_timing_and_shards_remain_intact(self):
        cues = json.loads((STORY / 'script.json').read_text())
        self.assertEqual(len(cues), 10)
        self.assertTrue(all(0 <= c['start'] < c['start']+c['duration'] <= 60 for c in cues))
        self.assertEqual([n for i in range(20) for n in range(i*72, (i+1)*72)], list(range(1440)))

    def test_fetch_manifest_has_every_visible_asset(self):
        from showreel.celebrity_cinematic_3d.fetch_assets import entries
        names = [e['name'] for e in entries()]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(names), {'ryan.glb', 'emma.glb', 'marcus.glb', 'nightstand.glb',
                                      'armchair.glb', 'materials.glb', 'planter.glb',
                                      'streetLamp.glb', 'vase.glb', 'car.glb'})


if __name__ == '__main__':
    unittest.main()
