"""Structural tests for the visual A/B comparison, not a premium-quality score."""
import unittest,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
class ComparisonContract(unittest.TestCase):
 def test_original_vector_animation_no_external_scene_plates(self):
  s=(P/'stage.html').read_text()
  for x in ['<img','TextureLoader','data:image','https://','http://','.jpg','.png','Date.now','performance.now','requestAnimationFrame']:
   self.assertNotIn(x,s)
  self.assertIn('new Path2D',s);self.assertIn('function leg(',s);self.assertIn('function fern(',s)
 def test_depth_planes_and_active_scenery(self):
  s=(P/'stage.html').read_text()
  for x in ['cam*(.22+layer*.3)','cam*1.1','cam*1.3','function birds(t)','Math.sin(t*.53+a.phase)','t*13','const swing=clamp']:
   self.assertIn(x,s)
 def test_disclosures_and_palette(self):
  s=(P/'stage.html').read_text()
  for x in ['#0b242c','#e4b66b','#f0e7cd','NOT A SPECIES-VALIDATED MODEL','NOT REAL DNA READS','NOT FOOTAGE OF THE STUDY SITE']:
   self.assertIn(x,s)
 def test_map_and_source(self):
  data=json.loads((P/'greenland.json').read_text());self.assertEqual(data['type'],'Polygon');self.assertGreater(len(data['coordinates'][0]),100)
 def test_final_media_contract(self):
  q=json.loads((P/'QC.json').read_text());self.assertEqual(q['duration_seconds'],45);self.assertEqual(q['decoded_frames'],1350);self.assertTrue(q['audio_identical_to_3d_reference']);self.assertEqual(q['native_resolution'],[1920,1080]);self.assertLess(float(q['measured_encoded_audio']['input_tp']),0);self.assertFalse(any('black_start:' in x for x in q['black_or_freeze_events']));self.assertEqual(q['half_second_motion_samples']['count'],90);self.assertGreater(q['half_second_motion_samples']['unique_decoded_frames'],80)
if __name__=='__main__':unittest.main()
