"""Deterministic render and action-blocking checks (not aesthetic evaluation)."""
import importlib.util,math,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'render.py'
spec=importlib.util.spec_from_file_location('render',p);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
class TestRender(unittest.TestCase):
 def test_timeline(self):
  self.assertEqual(r.CUTS[0],0);self.assertEqual(r.CUTS[-1],60)
  self.assertTrue(all(a<b for a,b in zip(r.CUTS,r.CUTS[1:])))
  self.assertTrue(all((r.AUDIO/f'{i:02d}.wav').is_file() for i in range(1,8)))
 def test_contact_and_release(self):
  bx,by,fx,fy=r.dribble_pose(1.04)
  self.assertAlmostEqual(math.dist((bx,by),(fx+33,fy-12)),25)
  self.assertEqual(r.dribble_pose(1.03)[:2],(526,416))
  self.assertGreater(r.dribble_pose(1.3)[0],526)
 def test_output_size_and_seek_determinism(self):
  for t in (1,4,9,12,17,19.54,25,39,46,57):
   a=r.compose(t);self.assertEqual(a.size,(960,540));r.compose(3);self.assertEqual(a.tobytes(),r.compose(t).tobytes())
 def test_selected_actions_change(self):
  for a,b in ((3.3,4.3),(8.2,9.3),(16.4,17.2),(19.3,19.8),(24.2,25.2)):
   self.assertNotEqual(r.compose(a).tobytes(),r.compose(b).tobytes())
if __name__=='__main__':unittest.main()
