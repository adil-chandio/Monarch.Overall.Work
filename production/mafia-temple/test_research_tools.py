"""Deterministic checks for local study-building helpers, not visual QA."""
import unittest
import numpy as np
from assemble_research_study import fit_cover
from research_depth_camera import depth_reproject


class ResearchToolsTests(unittest.TestCase):
 def test_camera_identity_without_motion_or_crop(self):
  rng=np.random.default_rng(7)
  image=rng.integers(0,256,(24,40,3),dtype=np.uint8)
  depth=rng.random((24,40),dtype=np.float32)
  self.assertTrue(np.array_equal(depth_reproject(image,depth,0,crop=1),image))

 def test_camera_rejects_mismatched_depth_and_invalid_phase(self):
  image=np.zeros((24,40,3),dtype=np.uint8)
  with self.assertRaises(ValueError): depth_reproject(image,np.zeros((20,40),dtype=np.float32),0)
  with self.assertRaises(ValueError): depth_reproject(image,np.zeros((24,40),dtype=np.float32),1.01)

 def test_center_crop_preserves_source_proportions(self):
  # A deliberately very wide frame: cover crops horizontally, not vertically.
  image=np.zeros((536,1280,3),dtype=np.uint8)
  image[:,128:1152]=[11,29,43]
  out=fit_cover(image)
  self.assertEqual(out.shape,(720,1280,3))
  self.assertTrue(np.all(out[360,640]==[11,29,43]))
  self.assertTrue(np.all(out[360,0]==[11,29,43]))
  self.assertTrue(np.all(out[360,-1]==[11,29,43]))

if __name__=='__main__': unittest.main()
