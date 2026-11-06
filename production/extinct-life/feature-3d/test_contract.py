"""Production safeguards, not a creative-quality scoring system."""
import hashlib,json,subprocess,unittest
from pathlib import Path
B=Path('production/extinct-life/feature-3d');M=json.loads((B/'sequence.json').read_text());OLD=Path('production/extinct-life/feature-rebuild')
class ProductionContract(unittest.TestCase):
 def test_original_script_and_voice_contract(self):
  scripts=json.loads((OLD/'narration-ur.json').read_text());voices=json.loads((OLD/'voice-provenance.json').read_text())['clips']
  self.assertEqual(len(M['chapters']),8);self.assertEqual(M['frames'],12144)
  for ch,script,voice in zip(M['chapters'],scripts,voices):
   self.assertEqual(ch['narration_sha256'],hashlib.sha256(script['text'].encode()).hexdigest());self.assertEqual(ch['voice_pcm_sha256'],voice['pcm_sha256']);self.assertEqual(ch['voice_seconds'],voice['seconds'])
 def test_no_fake_full_film_or_fallback(self):
  self.assertFalse(M['full_film_complete'])
  for ch in M['chapters']:
   if not ch['implemented']:self.assertIsNone(ch['scene'])
  p=subprocess.run(['node',str(B/'render.mjs'),'--chapter=0','--stills'],capture_output=True,text=True)
  self.assertNotEqual(p.returncode,0);self.assertIn('refusing a fallback scene',p.stderr)
 def test_authored_shot_coverage(self):
  shots=M['chapter_02_shots'];self.assertEqual(shots[0]['start_frame'],0);self.assertEqual(shots[-1]['end_frame'],1563)
  for a,b in zip(shots,shots[1:]):self.assertEqual(a['end_frame'],b['start_frame']);self.assertNotEqual(a['coverage'],b['coverage'])
  for s in shots:self.assertGreater(s['end_frame']-s['start_frame'],0);self.assertLessEqual(s['end_frame']-s['start_frame'],90)
 def test_optional_rendered_chapter(self):
  report=B/'render-reports/chapter-03.json'
  if not report.exists():self.skipTest('Chapter render is not complete yet; no finished-media claim.')
  import imageio_ffmpeg
  q=json.loads(report.read_text());p=Path(q['file']);self.assertTrue(p.exists());self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),q['sha256'])
  r=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-i',str(p),'-map','0:v:0','-c:v','copy','-progress','pipe:1','-f','null','-'],capture_output=True,text=True,check=True)
  import re
  self.assertEqual(int(re.findall(r'^frame=(\d+)',r.stdout,re.M)[-1]),1563);self.assertIn('1920x1080',r.stderr);self.assertLessEqual(float(q['audio_measurement']['input_tp']),-1)
if __name__=='__main__':unittest.main(verbosity=2)
