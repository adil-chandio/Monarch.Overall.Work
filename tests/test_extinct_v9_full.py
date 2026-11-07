"""Technical contracts; deliberately not a creative-quality certificate."""
import hashlib,json,unittest,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R/'production/extinct-life/film-v9-full'
class FullMaster(unittest.TestCase):
 def setUp(self):self.m=json.loads((B/'schedule.json').read_text())
 def test_full_not_excerpt(self):
  self.assertEqual(self.m['total_frames'],13163);self.assertEqual(self.m['voice_id'],'voice-02');self.assertFalse(self.m['voice_speed_changed'])
 def test_contiguous(self):
  q=self.m['sequences'];self.assertEqual(q[0]['start_frame'],0);self.assertEqual(q[-1]['end_frame'],13163)
  for a,b in zip(q,q[1:]):self.assertEqual(a['end_frame'],b['start_frame'])
 def test_unchanged_voice(self):
  for c in self.m['chapters']:self.assertEqual(hashlib.sha256((R/c['voice']).read_bytes()).hexdigest(),c['voice_sha256'])
 def test_unchanged_subtitles(self):self.assertEqual((B/'English-v9.srt').read_bytes(),(B.parent/'film-v7-full/English-v7.srt').read_bytes())
 def test_no_caption_panels_or_scene_plates(self):
  s=(B/'scene.mjs').read_text();self.assertNotIn('fillRect(',s);self.assertNotIn('drawImage(photo',s);self.assertIn('project(camera)',s)
 def test_original_mesh_assets(self):
  s=(B/'assets.mjs').read_text();self.assertIn('GLTFLoader',s);self.assertIn('bind=new Float32Array',s);self.assertIn('footState(t',s)
 def test_separate_review_status(self):
  s=(B/'finish.py').read_text();self.assertIn("'full_film_creative_acceptance':False",s);self.assertIn("'human_full_watch_listen_claimed':False",s)
 def test_javascript_parse(self):
  for name in ['scene.mjs','worlds.mjs','assets.mjs','motion.mjs','render.mjs']:subprocess.run(['node','--check',str(B/name)],check=True,capture_output=True)
 def test_kinematic_contracts(self):subprocess.run(['node',str(B/'motion.test.mjs')],check=True,capture_output=True)
if __name__=='__main__':unittest.main()
