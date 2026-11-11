import sys,math,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import render
from motion import foot_target,rolling,knee
class SceneTests(unittest.TestCase):
 def test_paths_use_reachable_leg_targets(self):
  for shot,(origin,end,duration,scale) in render.WALK_PATHS.items():
   for k in range(int(duration*60)+1):
    x=render.path_x(shot,k/60);phase=(x-origin)/(40*scale)*math.tau
    hy=-56*scale-abs(math.sin(phase))*1.5*scale
    for j,shift in enumerate((0,.5)):
     foot,_=foot_target(x,origin,0,scale,shift);hip=(x+(-6 if j==0 else 6)*scale,hy)
     self.assertLess(math.dist(foot,hip),68*scale)
     q=knee(hip,foot,34*scale,34*scale,-1)
     self.assertAlmostEqual(math.dist(q,foot),34*scale,places=4)
 def test_footstep_cues_are_actual_landings(self):
  for shot in render.WALK_PATHS:
   self.assertGreater(len(render.step_times(shot)),0)
   self.assertTrue(all(render.CUTS[shot]<=t<render.CUTS[shot+1] for t in render.step_times(shot)))
 def test_ball_contact_and_roll(self):
  for u in (0,.5,1.03):self.assertEqual(render.dribble_pose(u)[:2],(526,416))
  bx,by,fx,fy=render.dribble_pose(1.04)
  self.assertAlmostEqual(math.dist((bx,by),(fx+33,fy-12)),25)
  bx2,by2,_,_=render.dribble_pose(1.3)
  self.assertGreater(bx2,bx);self.assertLess(by2,by)
 def test_authored_third_person_kick_touch(self):
  t=.98;q=render.anim(t,[(0,0),(.4,-.65),(.8,-.65),(1.12,1),(1.6,.4),(2.5,0)])
  toe=(420+(15+43*q)*1.2+8*1.2,462-17*max(q,0)*1.2)
  self.assertLess(abs(math.dist(toe,(475,450))-12),.5)
  self.assertEqual(rolling(-.001,420,145)[0],0)
  self.assertGreater(rolling(.1,420,145)[0],0)
 def test_repeatable_and_action_changes(self):
  for t in (1,4,7,9,17,19.54,25,39,46,57):
   a=render.compose(t);self.assertEqual(a.size,(960,540));render.compose(2);self.assertEqual(a.tobytes(),render.compose(t).tobytes())
  for a,b in ((.2,1.8),(6.2,7.2),(16.7,17.2),(19.4,19.8),(24.4,25.4)):
   self.assertNotEqual(render.compose(a).tobytes(),render.compose(b).tobytes())
if __name__=='__main__':unittest.main()
