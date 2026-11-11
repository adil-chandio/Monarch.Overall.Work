"""Rocketbox actors with measured prop contacts.

The source GLBs bundle four overlapping outfits (plus a stray icosphere); only one
is ever visible.  Outfits are whole sets: you cannot mix a formal jacket with tee
trousers, so `outfit()` switches the whole set at once.
"""
import math
import bpy
from mathutils import Vector, Quaternion
import motion

ASSETS = '/home/user/celebrity-lookdev-assets'
_CLOTHING = {'Outfit_formal', 'Skin_formal', 'Outfit_original', 'Skin_original',
             'Top_shirt', 'Skin_shirt', 'Top_tee', 'Skin_tee', 'Trousers', 'Shoes'}
_GROUPS = {
    'formal': {'Outfit_formal', 'Skin_formal'},
    'smart': {'Outfit_original', 'Skin_original'},
    'shirt': {'Top_shirt', 'Skin_shirt', 'Trousers', 'Shoes'},
    'tee': {'Top_tee', 'Skin_tee', 'Trousers', 'Shoes'},
}


class Actor:
    def __init__(self, name, asset, loc=(0, 0, 0), rot=0.0, outfit='formal', scale=1.0):
        before = set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=f'{ASSETS}/{asset}')
        added = [o for o in bpy.context.scene.objects if o not in before]
        self.rig = next(o for o in added if o.type == 'ARMATURE')
        self.meshes = [o for o in added if o.type == 'MESH']
        for o in list(self.meshes):
            base = o.name.split('.')[0]
            if base == 'Icosphere':
                self.meshes.remove(o)
                bpy.data.objects.remove(o, do_unlink=True)
                continue
            o.name = f'{name} {base}'
        self.rig.name = f'{name} rig'
        self.rig.animation_data_create()
        self.rig.rotation_mode = 'QUATERNION'
        self.rig.rotation_quaternion = Quaternion((0, 0, 1), rot)
        self.rig.location = loc
        if scale != 1.0:
            self.rig.scale = (scale, scale, scale)
        self.actions = {a.name: a for a in bpy.data.actions if a.name.endswith('_Rig')}
        self.keep = _GROUPS[outfit]
        self.show(True)
        self._t = 0.0

    # visibility ---------------------------------------------------------
    def show(self, on):
        for o in self.meshes:
            base = o.name.split(' ')[-1].split('.')[0]
            o.hide_render = (not on) or (base in _CLOTHING and base not in self.keep)
        self.rig.hide_render = not on

    def outfit(self, which):
        self.keep = _GROUPS[which]
        self.show(True)

    def ensure(self):
        """Keep the current outfit visible even if another act called show()."""
        self.show(True)

    # animation ----------------------------------------------------------
    def action(self, name, frame):
        act = self.actions.get(name) or self.actions['Idle_Rig']
        if self.rig.animation_data.action is not act:
            self.rig.animation_data.action = act
        bpy.context.scene.frame_set(int(frame), subframe=frame - int(frame))

    def place(self, x, y, z=0.0, rot=None):
        self.rig.location = (x, y, z)
        if rot is not None:
            self.rig.rotation_quaternion = Quaternion((0, 0, 1), rot)

    def bone(self, name):
        return self.rig.pose.bones.get(f'mixamorig:{name}')

    def world_bone(self, name):
        b = self.bone(name)
        return (self.rig.matrix_world @ b.matrix).translation.copy() if b else None

    def grip(self, side='Right', amount=1.0):
        motion.curl_hand(self.rig, side, amount)

    def grasp(self, side='Right', depth=.55):
        return motion.grasp_frame(self.rig, side, depth)

    def look(self, target, weight=.85, limit=math.radians(32)):
        motion.look_at(self.rig, target, weight=weight, limit=limit)

    def expression(self, t, smile=0.0, brow=0.0, jaw=0.0, squint=0.0):
        b = motion.blink_amount(t)
        vals = {'eyeBlinkLeft': b, 'eyeBlinkRight': b,
                'mouthSmileLeft': smile, 'mouthSmileRight': smile,
                'browInnerUp': brow, 'browOuterUpLeft': brow * .6, 'browOuterUpRight': brow * .6,
                'jawOpen': jaw, 'eyeSquintLeft': squint, 'eyeSquintRight': squint,
                'cheekSquintLeft': smile * .5, 'cheekSquintRight': smile * .5}
        for o in self.meshes:
            if not o.data.shape_keys:
                continue
            keys = o.data.shape_keys.key_blocks
            for k, v in vals.items():
                if k in keys:
                    keys[k].value = max(0.0, min(1.0, v))

    def tremble(self, amount, t, seed=0.0):
        if amount <= 0:
            return
        for i, name in enumerate(('RightHand', 'LeftHand')):
            b = self.bone(name)
            if b is None:
                continue
            n = math.sin(t * 37 + seed + i * 2.1) * .6 + math.sin(t * 61 + seed) * .4
            m = math.sin(t * 43 + seed + i) * .5 + math.sin(t * 71 + seed) * .5
            b.rotation_mode = 'QUATERNION'
            b.rotation_quaternion = (b.rotation_quaternion
                                     @ Quaternion((1, 0, 0), math.radians(amount * n))
                                     @ Quaternion((0, 0, 1), math.radians(amount * m)))
