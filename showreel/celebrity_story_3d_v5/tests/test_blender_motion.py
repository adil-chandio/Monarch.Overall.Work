"""Evaluated-rig seam check. Requires bpy 4.2 and the pinned asset."""
import math,unittest,os
from pathlib import Path
try:import bpy
except ImportError:bpy=None
@unittest.skipUnless(bpy,'requires Blender Python')
class RigChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  path=Path(os.environ.get('CELEBRITY_ASSETS','/home/user/celebrity-lookdev-assets'))/'ryan.glb'
  if not path.is_file():raise unittest.SkipTest('pinned character asset not found')
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path))
  cls.rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');cls.rig.animation_data.action=bpy.data.actions['Walk_Rig']
 def pos(self,frame,offset):
  s=bpy.context.scene;s.frame_set(math.floor(frame),subframe=frame%1);self.rig.location.y=offset;self.rig.rotation_euler.z=math.pi;bpy.context.view_layer.update()
  return (self.rig.matrix_world @ self.rig.pose.bones['mixamorig:Hips'].matrix).translation.copy()
 def test_hip_position_at_walk_wrap(self):
  end=self.pos(28.799,0);start=self.pos(0,-1.2127)
  self.assertLess((end-start).length,.07)
if __name__=='__main__':unittest.main()
