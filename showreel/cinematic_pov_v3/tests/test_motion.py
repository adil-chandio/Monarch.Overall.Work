import math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from motion import foot_target,knee,rolling
class MotionTests(unittest.TestCase):
 def test_constant_friction_roll(self):
  self.assertEqual(rolling(0,10,2),(0,10));self.assertEqual(rolling(9,10,2),(25,0))
  x,v=rolling(3,10,2);self.assertAlmostEqual(x,21);self.assertAlmostEqual(v,4)
  self.assertEqual(rolling(-1,10,2),(0,10));self.assertEqual(rolling(2,10,0),(20,10))
  with self.assertRaises(ValueError):rolling(1,-1,2)
 def test_foot_sticks_during_stance(self):
  points=[foot_target(x,0,100,1,0) for x in (1,5,12,20)]
  self.assertTrue(all(plant for _,plant in points))
  self.assertTrue(all(p==points[0][0] for p,_ in points));self.assertEqual(points[0][0][1],100)
 def test_foot_swings_and_lands_continuously(self):
  start=foot_target(24,0,100,1,0);middle=foot_target(32,0,100,1,0);end=foot_target(40,0,100,1,0)
  self.assertEqual(start[0][1],100);self.assertLess(middle[0][1],100)
  self.assertTrue(end[1]);self.assertAlmostEqual(end[0][0],foot_target(39.999999,0,100,1,0)[0][0],places=4)
 def test_knee_lengths(self):
  hip=(0,0);foot=(10,50);k=knee(hip,foot,30,30)
  self.assertAlmostEqual(math.dist(hip,k),30);self.assertAlmostEqual(math.dist(foot,k),30)
 def test_no_backward_ball(self):
  seq=[rolling(i*.1,3,2)[0] for i in range(50)]
  self.assertTrue(all(a<=b for a,b in zip(seq,seq[1:])))
if __name__=='__main__':unittest.main()
