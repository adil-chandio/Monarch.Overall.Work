import unittest,json,pathlib,re
P=pathlib.Path(__file__).parent
class ShortTests(unittest.TestCase):
 def setUp(self):self.s=json.loads((P/'timeline.json').read_text())
 def test_native_portrait(self):self.assertEqual((self.s['width'],self.s['height'],self.s['fps']),(1080,1920,30))
 def test_frame_duration(self):self.assertEqual(self.s['duration']*self.s['fps'],self.s['total_frames'])
 def test_boundaries(self):
  values=list(self.s['bounds'].values());self.assertEqual(values,sorted(values));self.assertTrue(all(0<x<self.s['duration'] for x in values))
 def test_captions_order_nonoverlap(self):
  last=0
  for c in self.s['captions']:
   self.assertGreaterEqual(c['start'],last);self.assertGreater(c['end'],c['start']);self.assertLessEqual(c['end'],self.s['duration']);last=c['end']
 def test_caption_safe_lengths(self):
  for c in self.s['captions']:
   self.assertLessEqual(len(c['lines']),2)
   for l in c['lines']:self.assertLessEqual(len(l),36)
 def test_approved_text_coverage(self):
  s=(P.parent/'PROPOSAL.md').read_text();approved=re.search(r'```text\n(.*?)\n```',s,re.S)[1]
  caption=' '.join(' '.join(c['lines']) for c in self.s['captions'])
  def norm(t):return re.sub(r'[^a-z0-9]','',t.lower())
  self.assertEqual(norm(approved),norm(caption))
 def test_explicit_scientific_limits(self):
  src=(P/'scene.mjs').read_text()
  for t in ['NOT A COMPLETE GENOME','SCHEMATIC','RECONSTRUCTION','NORTH GREENLAND']:self.assertIn(t,src)
 def test_original_sound_only(self):
  s=json.loads((P.parent/'SOUND-DESIGN.json').read_text());self.assertTrue(s['original_music']);self.assertTrue(s['original_synthetic_sfx']);self.assertFalse(s['copied_competitor_audio'])
if __name__=='__main__':unittest.main(verbosity=2)
