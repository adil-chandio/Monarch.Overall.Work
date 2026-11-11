import importlib.util,unittest,math,json,wave
from pathlib import Path
p=Path(__file__).resolve().parents[1];sp=importlib.util.spec_from_file_location('motion',p/'motion.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class Checks(unittest.TestCase):
 def test_walk_reset_displacement(self):
  for n in (1,2,3):
   t=n*m.WALK_DURATION/m.WALK_RATE
   before_frame,before_root=m.walk(t-1e-6);after_frame,after_root=m.walk(t+1e-6)
   self.assertGreater(before_frame,28.7);self.assertLess(after_frame,.01)
   self.assertAlmostEqual(before_root-after_root,m.ROOT_PER_CYCLE)
 def test_blink_range(self):
  self.assertTrue(all(0<=m.blink(i/20)<=1 for i in range(200)))
 def test_cues(self):
  c=json.loads((p/'script.json').read_text())
  for i,e in enumerate(c):
   with wave.open(str(p/'audio'/f'{i+1:02}.wav')) as w:d=w.getnframes()/w.getframerate()
   self.assertGreater(e['tempo'],0)
   self.assertLessEqual(e['start']+d/e['tempo'],c[i+1]['start'] if i+1<len(c) else 60)
if __name__=='__main__':unittest.main()
