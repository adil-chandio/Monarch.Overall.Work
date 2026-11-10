"""Structural safeguards for the full film; not an aesthetic certification."""
import json, unittest
from pathlib import Path

B=Path(__file__).resolve().parent
P=json.loads((B/'timeline.json').read_text())
VO=json.loads((B.parent/'FILM-VO.json').read_text())

class FullFilmTests(unittest.TestCase):
 def test_script_and_takes(self):
  self.assertEqual([s['id'] for s in VO['segments']],[s['id'] for s in P['chapters']])
  for s in VO['segments']:
   self.assertTrue((B/'source'/f"{s['id']}.mp3").is_file())
   self.assertLessEqual(len(s['text']),1500)
 def test_storyboard_coverage(self):
  self.assertEqual(P['shots'][0]['start'],60)
  self.assertAlmostEqual(P['shots'][-1]['end'],P['duration'],places=2)
  for x,y in zip(P['shots'],P['shots'][1:]): self.assertAlmostEqual(x['end'],y['start'],places=2)
  self.assertGreaterEqual(len(P['shots']),40)
  for s in P['shots']:
   self.assertGreater(s['end'],s['start']);self.assertTrue((B/'assets'/f"{s['background']}.jpg").exists())
 def test_caption_timing(self):
  self.assertGreater(len(P['captions']),100)
  for c in P['captions']:
   self.assertGreaterEqual(c['start'],60);self.assertLess(c['start'],c['end']);self.assertLessEqual(c['end'],P['duration'])
  for x,y in zip(P['captions'],P['captions'][1:]):self.assertLessEqual(x['end'],y['start']+.02)
 def test_science_qualifications(self):
  text=' '.join(s['text'].lower() for s in VO['segments'])
  for phrase in ['not a literal headcount','not directly observed','cannot be ruled out','does not identify a disease','final ten generations']:
   # 'not directly observed' is paraphrased in the narration, not asserted verbatim.
   if phrase=='not directly observed': self.assertIn('did not observe',text)
   else:self.assertIn(phrase,text)
 def test_sound_direction(self):
  data=json.loads((B/'SOUND-DESIGN.json').read_text())
  self.assertFalse(data['opening_old_score_reused']);self.assertFalse(data['wind_drone_or_machine_bed'])
if __name__=='__main__':unittest.main()
