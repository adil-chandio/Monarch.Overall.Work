"""Small regression checks for the character renderer."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from vfx3d import engine, world


class FigureTests(unittest.TestCase):
    def test_capsules_remain_traceable(self):
        primitive = engine._flatten([world.Capsule((0, -1, 0), (0, 1, 0), .2, 'skin')])[0]
        ro = np.array([[[0, 0, 3]]], dtype=np.float32)
        rd = np.array([[[0, 0, -1]]], dtype=np.float32)
        distances = np.full((1, 1), np.inf, np.float32)
        materials = np.zeros((1, 1), np.int16)
        normals = np.zeros((1, 1, 3), np.float32)
        engine.Frame.__new__(engine.Frame)._intersect(
            primitive, None, None, distances, materials, normals,
            0, 1, 0, 1, ro, rd)
        self.assertAlmostEqual(float(distances[0, 0]), 2.8, places=4)
        self.assertEqual(int(materials[0, 0]), world.MAT_ID['skin'])
        np.testing.assert_allclose(normals[0, 0], [0, 0, 1], atol=1e-5)

    def test_run_period_uses_requested_cycle_frequency(self):
        a = world.gait_angles(0, speed=2.75, run=True)
        b = world.gait_angles(1 / 2.75, speed=2.75, run=True)
        self.assertAlmostEqual(a['thighL'], b['thighL'])
        self.assertAlmostEqual(a['kneeL'], b['kneeL'])

    def test_head_does_not_add_capsule_above_hair(self):
        pose = world.pose_at(0, run=True)
        self.assertNotIn('head', [seg[0] for seg in pose['segs']])
        self.assertTrue(world.figure_solids(pose))


if __name__ == '__main__':
    unittest.main()
