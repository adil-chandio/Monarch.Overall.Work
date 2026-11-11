import importlib.util,json,unittest,wave
from pathlib import Path
p=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('celebrity',p/'render.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
class TestVideo(unittest.TestCase):
 def test_narration_fits(self):
  cues=json.loads((p/'script.json').read_text())
  for i,cue in enumerate(cues):
   with wave.open(str(p/'audio'/f'{i+1:02}.wav')) as f:dur=f.getnframes()/f.getframerate()
   end=cues[i+1]['start'] if i+1<len(cues) else 60
   self.assertLessEqual(cue['start']+dur,end)
 def test_deterministic_frames(self):
  for t in (1,8,13,21,27,34,41,49,56):
   a=r.compose(t);self.assertEqual(a.size,(960,540));self.assertEqual(a.tobytes(),r.compose(t).tobytes())
 def test_action_progress(self):
  for a,b in ((2.1,4),(13,14),(26,28),(40.5,42),(49,50)):
   self.assertNotEqual(r.compose(a).tobytes(),r.compose(b).tobytes())
if __name__=='__main__':unittest.main()
