import math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from football_physics import Ball,Parameters,bake,step

class PhysicsTests(unittest.TestCase):
    def test_rest_stays_on_ground(self):
        states,hits=bake(Ball((0,0,.11)),2)
        self.assertEqual(hits,[])
        self.assertTrue(all(s.position==(0.,0.,.11) and s.velocity==(0.,0.,0.) for s in states))
    def test_foot_only_impacts_while_closing_and_in_contact(self):
        ball=Ball((0,0,.11)); foot=(-.19,0,.11)
        _,hit=step(ball,.001,foot=foot,foot_velocity=(-1,0,0));self.assertFalse(hit)
        s,hit=step(ball,.001,foot=foot,foot_velocity=(3,0,0));self.assertTrue(hit)
        self.assertGreater(s.velocity[0],0)
        _,hit=step(ball,.001,foot=(-1,0,.11),foot_velocity=(3,0,0));self.assertFalse(hit)
    def test_ball_bounces_and_never_falls_through_floor(self):
        s,_=bake(Ball((0,0,1)),2)
        self.assertTrue(all(x.position[2]>=.11 for x in s))
        self.assertTrue(any(x.velocity[2]>0 for x in s))
    def test_rolling_slows_without_reversing_and_rolls(self):
        s,_=bake(Ball((0,0,.11),(1,0,0)),2)
        self.assertGreater(s[-1].position[0],0);self.assertGreater(s[-1].roll,0)
        self.assertTrue(all(x.velocity[0]>=0 for x in s));self.assertEqual(s[-1].velocity[0],0)
    def test_repeatable_fixed_step_and_impact(self):
        def foot(t): return ((-.4+3*t,0,.11),(3,0,0)) if t<.15 else None
        a,imp=bake(Ball((0,0,.11)),1,foot)
        b,imp2=bake(Ball((0,0,.11)),1,foot)
        self.assertEqual(a,b);self.assertEqual(imp,imp2);self.assertGreater(len(imp),0)
        self.assertGreater(a[-1].position[0],0)
    def test_invalid_parameters(self):
        for kw in ({'radius':0},{'mass':-1},{'ground_restitution':2},{'gravity':float('nan')}):
            with self.assertRaises(ValueError): Parameters(**kw)
        with self.assertRaises(ValueError):bake(Ball((0,0,.11)),1.01)
if __name__=='__main__':unittest.main()
