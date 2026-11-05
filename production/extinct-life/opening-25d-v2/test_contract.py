"""Animation and encoded-media regressions, not a cinematic-quality score."""
import json
from pathlib import Path
import unittest
P=Path(__file__).resolve().parent

class PolishContract(unittest.TestCase):
 def test_independent_animation_not_scene_plates(self):
  s=(P/'stage.html').read_text()
  for token in ['<img','TextureLoader','data:image','https://','http://','.jpg','.png','Date.now','requestAnimationFrame']:
   self.assertNotIn(token,s)
  for token in ['function leg(','function fern(','function birds(','cam*(.22+layer*.3)','cam*1.1','cam*1.3','t*13']:
   self.assertIn(token,s)

 def test_edit_ledger_and_real_compositor(self):
  e=json.loads((P/'edit.json').read_text());s=(P/'stage.html').read_text()
  self.assertEqual(e['duration'],45);self.assertEqual(e['fps'],30)
  self.assertEqual(len(e['seams']),9)
  self.assertEqual(sorted(x['t'] for x in e['seams']),[x['t'] for x in e['seams']])
  self.assertTrue(all(0<x['duration']<=.7 for x in e['seams']))
  for token in ['function rail(t)','function renderTo(','g.drawImage(deckA,0,0)','g.drawImage(deckB,0,0)','drawCarrier(seam,u)','sceneTime-.07']:
   self.assertIn(token,s)

 def test_map_and_disclosures(self):
  data=json.loads((P/'greenland.json').read_text());self.assertEqual(data['type'],'Polygon')
  self.assertGreater(len(data['coordinates'][0]),100)
  s=(P/'stage.html').read_text()
  for token in ['not actual footage','not footage of the study site','not actual DNA reads or a complete genome','Appearance is illustrative','Artistic reconstruction']:
   self.assertIn(token,s)

 def test_random_seek_and_camera_continuity(self):
  q=json.loads((P/'QC.json').read_text());r=q['native_render_checks']
  self.assertEqual(len(r['non_monotonic_seek_probes']),7)
  self.assertTrue(all(len(x['sha256'])==64 for x in r['non_monotonic_seek_probes']))
  for sample in r['camera']:
   left=(sample['at']['camera']-sample['before']['camera'])/.001
   right=(sample['after']['camera']-sample['at']['camera'])/.001
   self.assertLess(abs(left-right),.01)

 def test_final_media_contract(self):
  q=json.loads((P/'QC.json').read_text())
  self.assertEqual(q['duration_seconds'],45);self.assertEqual(q['decoded_frames'],1350)
  self.assertEqual(q['native_resolution'],[1920,1080]);self.assertEqual(q['fps'],30)
  self.assertTrue(q['audio_identical_to_previous_25d'])
  self.assertLess(float(q['measured_encoded_audio']['input_tp']),0)
  self.assertFalse(any('black_start:' in x for x in q['black_or_freeze_events']))
  self.assertEqual(q['half_second_motion_samples']['count'],90)
  self.assertGreater(q['half_second_motion_samples']['unique_decoded_frames'],80)

if __name__=='__main__':unittest.main()
