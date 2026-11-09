"""Structural/delivery checks, not a substitute for perceptual acceptance."""
from pathlib import Path
import json,hashlib,unittest
B=Path(__file__).resolve().parents[1]
class FilmTests(unittest.TestCase):
 def test_timeline(self):
  s=json.loads((B/'film/timeline.json').read_text());self.assertEqual(s['total_frames'],1530);self.assertEqual(s['width'],1080);self.assertEqual(s['height'],1920);self.assertTrue(45<=s['duration']<=55)
  scenes=s['scenes'];self.assertEqual(len(set(x['id'] for x in scenes)),10);self.assertEqual(scenes[0]['start'],0);self.assertEqual(scenes[-1]['end'],51)
  for a,b in zip(scenes,scenes[1:]):self.assertEqual(a['end'],b['start'])
 def test_captions(self):
  cues=json.loads((B/'film/timeline.json').read_text())['captions'];self.assertEqual(len(cues),20)
  for c in cues:self.assertLess(c['start'],c['end']);self.assertLessEqual(c['end'],51);self.assertLessEqual(len(c['lines']),2)
  for a,b in zip(cues,cues[1:]):self.assertLessEqual(a['end'],b['start'])
 def test_source_hashes(self):
  d=json.loads((B/'SOURCE-LICENSE.json').read_text())
  for a in d['files']:self.assertEqual(hashlib.sha256((B/'source'/Path(a['file']).name).read_bytes()).hexdigest(),a['sha256'])
 def test_crop_hashes(self):
  d=json.loads((B/'ASSET-EDITS.json').read_text())
  for a in d:self.assertEqual(hashlib.sha256((B/'assets'/(a['name']+'.png')).read_bytes()).hexdigest(),a['sha256'])
 def test_credits_and_limits(self):
  s=(B/'README.md').read_text();self.assertIn('https://creativecommons.org/licenses/by/4.0/',s);self.assertIn('mirroring',s);self.assertIn('not displayed to a common',s);self.assertIn('No YouTube upload',s)
 def test_no_old_animal_scene_dependency(self):
  s=(B/'film/scene.mjs').read_text();self.assertNotIn('animals.mjs',s);self.assertNotIn('mastodon',s);self.assertIn('PUBLISHED CT-BASED MODEL',s);self.assertIn('NOT A COMPLETE MUMMY',s)
if __name__=='__main__':unittest.main()
