"""Technical checks; visual or audio fidelity needs independent review."""
import importlib.util,json,unittest,wave
from pathlib import Path
p=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('farm_reference',p/'render.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
class TestRecreation(unittest.TestCase):
 def test_script_audio_fits_cues(self):
  lines=json.loads((p/'script.json').read_text())
  self.assertEqual(len(lines),9)
  for i,item in enumerate(lines):
   with wave.open(str(p/'audio'/f'{i+1:02}.wav')) as f:duration=f.getnframes()/f.getframerate()
   end=lines[i+1]['start'] if i+1<len(lines) else 60
   self.assertLessEqual(item['start']+duration,end)
 def test_frames_and_seek_determinism(self):
  for t in (1,3,4,6,9,13,16,20,23,26.7,29,34,37,40,44,49,56):
   image=r.compose(t);self.assertEqual(image.size,(960,540));r.compose(1);self.assertEqual(image.tobytes(),r.compose(t).tobytes())
 def test_stance_foot_is_planted(self):
  speed=27.6; period=.78; t1=.1; t2=.3
  a=r.stride_foot(350-speed*t1,260,.83,t1,0,speed,period)
  b=r.stride_foot(350-speed*t2,260,.83,t2,0,speed,period)
  self.assertAlmostEqual(a[0],b[0]);self.assertEqual(a[1],b[1])
 def test_knee_link_lengths(self):
  import math
  hip=(10,10);foot=(10,30);knee=r.knee_for(hip,foot,12,1)
  self.assertAlmostEqual(math.dist(hip,knee),12);self.assertAlmostEqual(math.dist(knee,foot),12)
 def test_action_changes(self):
  for a,b in ((3.7,4.1),(12.3,14.2),(19.3,21.2),(26.3,26.8),(28,29.5),(38.5,40.4)):
   self.assertNotEqual(r.compose(a).tobytes(),r.compose(b).tobytes())
if __name__=='__main__':unittest.main()
