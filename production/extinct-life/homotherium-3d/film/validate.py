"""Structural checks do not certify perceptual or anatomical quality."""
import json,unittest
from pathlib import Path
B=Path(__file__).resolve().parents[1]
class Cub3DTests(unittest.TestCase):
 def test_volumetric_subject(self):
  s=(B/'film/cub.mjs').read_text()
  for q in ['MarchingCubes','surface.update()','LineSegments','partial_body:true','no_living_animation:true']:self.assertIn(q,s)
 def test_scene_uses_model(self):
  s=(B/'film/scene.mjs').read_text()
  for q in ['makeCub()','PerspectiveCamera','renderer.render(scene,cam)','cam.lookAt(target)','3D SCIENTIFIC ILLUSTRATION']:self.assertIn(q,s)
 def test_timeline(self):
  s=json.loads((B/'film/timeline.json').read_text());self.assertEqual(s['total_frames'],1530);self.assertEqual(s['duration'],51);self.assertEqual(s['width'],1080);self.assertEqual(s['height'],1920)
 def test_spatial_ct_remains_labelled_image(self):
  s=(B/'film/scene.mjs').read_text();self.assertIn('PUBLISHED CT-BASED MODEL ON A SPATIAL DISPLAY',s);self.assertIn('partly reconstructed by mirroring',s)
 def test_rights(self):
  s=(B/'README.md').read_text();self.assertIn('https://creativecommons.org/licenses/by/4.0/',s);self.assertIn('not a recovered scientific model',s);self.assertIn('No YouTube publication',s)
if __name__=='__main__':unittest.main()
