"""Fast signal-design tests; no human listening approval is inferred."""
import unittest
import numpy as np
from sound import material,control_envelope,design,audit,SR

class SoftSoundTests(unittest.TestCase):
    def test_each_material_has_silent_edges_and_finite_samples(self):
        for kind in ['foot','water','grain','leaf']:
            a=material(kind,.65,np.random.default_rng(3))
            self.assertTrue(np.isfinite(a).all())
            self.assertEqual(a[0],0);self.assertEqual(a[-1],0)
            self.assertLessEqual(np.max(np.abs(a)),1.00001)
            self.assertLess(np.max(np.abs(a[:round(.005*SR)])),.05)
    def test_materials_are_not_the_same_impact_with_different_gain(self):
        a=material('foot',.65,np.random.default_rng(3))
        b=material('water',.65,np.random.default_rng(3))
        self.assertLess(abs(np.corrcoef(a,b)[0,1]),.9)
    def test_gain_control_has_a_slow_release_not_sample_level_pumping(self):
        v=np.zeros(SR);v[SR//4:SR//2]=.1
        e=control_envelope(v)
        self.assertGreater(e[SR//2+round(.1*SR)],.03)
        self.assertLess(np.max(np.abs(np.diff(e))),.0001)
    def test_short_scene_safe_no_out_of_bounds_or_bad_pan(self):
        cues={'river_leaf_land':.2,'goose_takeoff':5.55,'deposition_cohort_starts':[0,1.64,3.28],'branch_leaf_release':8.3,'branch_leaf_land':10.0}
        schedule={'segments':[{'start_frame':0},{'start_frame':9},{'start_frame':15}]}
        v=np.ones(SR,dtype=np.float32)*.06
        out,_,r=design(v,schedule,cues)
        self.assertEqual(out.shape,(SR,2));self.assertTrue(np.isfinite(out).all())
        self.assertTrue(np.all(out[0]==0));self.assertTrue(np.all(out[-1]==0))
        self.assertFalse(r['human_listening_approval'])
        self.assertLessEqual(max(abs(e['pan']) for e in r['events']),.25)
        self.assertTrue(audit(out,v)['endpoints_zero'])

if __name__=='__main__':unittest.main()
