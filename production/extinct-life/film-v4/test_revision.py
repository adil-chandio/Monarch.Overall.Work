import hashlib,json,unittest
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2]
class Revision(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=json.loads((B/'manifest.json').read_text())
 def test_latest_editing_instruction_overrides_old_cut_rule(self):
  self.assertFalse(self.m['forced_three_second_cuts']);self.assertEqual(len(self.m['sequences']),18);self.assertGreater(max((s['end_frame']-s['start_frame'])/30 for s in self.m['sequences']),30)
 def test_complete_unbroken_sequence_coverage(self):
  cursor=0
  for s in self.m['sequences']:
   self.assertEqual(s['start_frame'],cursor);self.assertGreater(s['end_frame'],cursor);cursor=s['end_frame']
   if s['start_frame']:self.assertGreaterEqual(s['blend_frames'],30)
  self.assertEqual(cursor,self.m['total_frames'])
 def test_new_sets_not_relabelled_replays(self):
  self.assertEqual(len({s['seed'] for s in self.m['sequences']}),18);self.assertEqual(len({s['design'] for s in self.m['sequences']}),18)
  source=(B/'worlds.mjs').read_text();self.assertIn('environmentDetails(w,episode)',source);self.assertIn('landShift=(episode.seed',source)
 def test_same_approved_natural_voice(self):
  for c in self.m['chapters']:self.assertEqual(hashlib.sha256((ROOT/c['voice']).read_bytes()).hexdigest(),c['voice_sha256'])
  self.assertFalse(self.m['voice_speed_changed']);self.assertEqual(self.m['voice_id'],'voice-02')
 def test_no_beat_index_camera_reset_or_reused_video(self):
  s=(B/'scene.mjs').read_text();self.assertNotIn('shot.coverage',s);self.assertNotIn('i%5',s);self.assertNotIn('c.index*13.7',s);self.assertIn('cameraPose(sequence,focus,frame)',s)
  for f in ['scene.mjs','render.mjs','worlds.mjs']:self.assertNotIn('Extinct_Life_v3_Full_English', (B/f).read_text())
 def test_full_frame_not_split_transitions(self):
  s=(B/'scene.mjs').read_text();self.assertIn('ctx.globalAlpha=opacity',s);self.assertIn('elapsed<sequence.blend_frames',s);self.assertNotIn('W/2,0,W/2',s)
 def test_evidence_qualifiers_remain(self):
  s=(B/'scene.mjs').read_text()
  for v in ['NOT AN OBSERVED ENCOUNTER','NOT TO SCALE','NOT ACTUAL SEQUENCE READS','NOT STUDY FOOTAGE']:self.assertIn(v,s)
 def test_no_wrapping_lab_delivery(self):
  s=(B/'worlds.mjs').read_text();self.assertNotIn('act%6.2',s);self.assertIn('Math.min(act,6.2)',s)
 def test_aac_peak_protection_not_relaxed_qc(self):
  s=(B/'finish.py').read_text();self.assertIn('aresample=192000,alimiter=limit=0.70:level=false',s);self.assertIn("assert float(measured['input_tp'])<=-.8",s)
 def test_no_false_finished_claim(self):self.assertFalse(self.m['full_film_complete'])
if __name__=='__main__':unittest.main()
