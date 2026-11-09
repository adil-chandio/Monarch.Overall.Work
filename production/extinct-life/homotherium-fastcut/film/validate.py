"""Structural checks, not a certification of perceptual editing quality."""
import json,unittest
from pathlib import Path
B=Path(__file__).resolve().parents[1]
class FastCutTests(unittest.TestCase):
 def test_no_3d(self):
  s=(B/'film/scene.mjs').read_text()
  for q in ['WebGLRenderer(',"from 'three'",'makeCub(',"import * as T"]:self.assertNotIn(q,s)
  self.assertTrue(json.loads((B/'film/timeline.json').read_text())['no_3d'])
 def test_deliverable_format(self):
  s=json.loads((B/'film/timeline.json').read_text());self.assertEqual((s['width'],s['height'],s['fps'],s['duration'],s['total_frames']),(1080,1920,30,46,1380))
 def test_fast_contiguous_shots(self):
  shots=json.loads((B/'film/timeline.json').read_text())['scenes'];self.assertEqual(len(shots),35);self.assertEqual(shots[0]['start'],0);self.assertEqual(shots[-1]['end'],46)
  for a,b in zip(shots,shots[1:]):self.assertEqual(a['end'],b['start'])
  for s in shots:self.assertGreater(s['end']-s['start'],.3);self.assertLess(s['end']-s['start'],2.8)
 def test_caption_safe_chunks(self):
  cues=json.loads((B/'film/timeline.json').read_text())['captions']
  for c in cues:self.assertGreaterEqual(len(c['text'].split()),2);self.assertLessEqual(len(c['text'].split()),5);self.assertLess(c['start'],c['end']);self.assertLess(c['end'],46)
  for a,b in zip(cues,cues[1:]):self.assertLessEqual(a['end'],b['start']+.0001)
 def test_no_voice_speedup(self):
  s=json.loads((B/'AUDIO-EDITS.json').read_text());self.assertEqual(s['speech_speed'],1)
  for e in s['edits']:self.assertEqual(e['speed'],1);self.assertGreater(e['source_end'],e['source_start'])
 def test_retains_all_words(self):
  old=json.loads((B/'../homotherium-short/film/timeline.json').read_text())['captions'];new=json.loads((B/'film/timeline.json').read_text())['captions'];self.assertEqual(' '.join(' '.join(c['lines']) for c in old),' '.join(c['text'] for c in new))
 def test_local_qualifiers(self):
  s=(B/'film/scene.mjs').read_text()
  for q in ['different display scales','partly mirrored','Published CT-based model','INCOMPLETE','Full living appearance remains uncertain']:self.assertIn(q,s)
 def test_credits_and_base(self):
  s=(B/'README.md').read_text();self.assertIn('d61ed05',s);self.assertIn('https://creativecommons.org/licenses/by/4.0/',s);self.assertIn('no YouTube publication',s)
if __name__=='__main__':unittest.main()
