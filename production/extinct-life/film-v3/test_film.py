import hashlib,json,re,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
class Film(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=json.loads((BASE/'manifest.json').read_text());cls.p=json.loads((BASE/'voice-provenance.json').read_text());cls.scenes=(BASE/'worlds.mjs').read_text()
 def test_source(self):
  master=ROOT/'production/extinct-life/script-lab/master-v3.json';self.assertEqual(hashlib.sha256(master.read_bytes()).hexdigest(),self.m['script_sha256'])
 def test_duration(self):
  self.assertTrue(360<self.m['duration_seconds']<480);self.assertAlmostEqual(self.m['total_frames']/30,self.m['duration_seconds']);self.assertFalse(self.m['full_film_complete'])
 def test_coverage(self):
  cursor=0
  for c in self.m['chapters']:
   self.assertEqual(c['start_frame'],cursor);local=0
   for s in c['shots']:
    self.assertEqual(s['start_frame'],local);self.assertGreater(s['end_frame'],local);self.assertLessEqual(s['end_frame']-local,90);self.assertIn("'"+s['mode']+"'",self.scenes);local=s['end_frame']
   self.assertEqual(local,c['frames']);cursor+=c['frames']
  self.assertEqual(cursor,self.m['total_frames'])
 def test_voice_hashes(self):
  self.assertEqual(self.p['voice_id'],'voice-02');self.assertFalse(self.p['time_stretching'])
  for v in self.p['clips']:self.assertEqual(hashlib.sha256((ROOT/v['voice']).read_bytes()).hexdigest(),v['voice_sha256'])
 def test_science_labels(self):
  s=(BASE/'scene.mjs').read_text()
  for text in ['NOT AN OBSERVED ENCOUNTER','NOT TO SCALE','NOT ACTUAL SEQUENCE READS','NOT STUDY FOOTAGE']:self.assertIn(text,s)
 def test_no_old_fallback(self):
  for file in ['scene.mjs','render.mjs','finish.py']:
   s=(BASE/file).read_text()
   for old in ['feature-25d','feature-rebuild','voice-01','ffmpeg -loop']:self.assertNotIn(old,s)
 def test_seek_no_accumulation(self):
  s=(BASE/'scene.mjs').read_text();self.assertIn('const act=t-shot.sentence_start',s);self.assertNotIn('deltaTime',s)
if __name__=='__main__':unittest.main()
