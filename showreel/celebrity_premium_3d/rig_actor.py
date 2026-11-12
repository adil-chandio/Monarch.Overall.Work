"""Drive licensed, skinned Rocketbox actors in the reconstructed 3D scenes.

A procedural puppet supplies blocking and prop targets.  The visible model is
an animated armature with baked Rocketbox motion, facial blend shapes and
joint-head CCD for authored contacts. It is a generic fictional person,
not a likeness of a real celebrity.
"""
import math
import re
import bpy
from mathutils import Vector, Matrix, Quaternion

_CLOTHING = {'Outfit_formal', 'Skin_formal', 'Outfit_original', 'Skin_original',
             'Top_shirt', 'Skin_shirt', 'Top_tee', 'Skin_tee', 'Trousers', 'Shoes'}
_GROUPS = {
    'formal': {'Outfit_formal', 'Skin_formal'},
    'smart': {'Outfit_original', 'Skin_original'},
    'shirt': {'Top_shirt', 'Skin_shirt', 'Trousers', 'Shoes'},
}
_CURVE = re.compile(r'^pose\.bones\["([^"]+)"\]\.(location|rotation_quaternion|scale)$')


def smooth(x):
    x=max(0.0,min(1.0,x))
    return x*x*(3.0-2.0*x)


class RigPuppet:
    def __init__(self, asset, kind, role):
        self.role=role;self.kind=kind
        old_objects=set(bpy.data.objects);old_actions=set(bpy.data.actions)
        bpy.ops.import_scene.gltf(filepath=str(asset))
        added=[o for o in bpy.data.objects if o not in old_objects]
        self.rig=next(o for o in added if o.type=='ARMATURE')
        self.rig.name='Rig '+role
        self.rig.animation_data_create();self.rig.animation_data.action=None
        self.rig.rotation_mode='QUATERNION'
        self.meshes=[o for o in added if o.type=='MESH' and o.name.split('.')[0]!='Icosphere']
        for o in added:
            if o.type=='MESH' and o.name.split('.')[0]=='Icosphere':bpy.data.objects.remove(o,do_unlink=True)
        self.actions={a.name.split('.')[0]:a for a in bpy.data.actions if a not in old_actions}
        self.curves={}
        for name,action in self.actions.items():
            curves=[]
            for f in action.fcurves:
                match=_CURVE.match(f.data_path)
                if match:
                    bone=self.rig.pose.bones.get(match.group(1))
                    if bone is not None:
                        bone.rotation_mode='QUATERNION';curves.append((bone,match.group(2),f.array_index,f))
            self.curves[name]=curves
        outfit='formal' if kind in ('street','car') and role in ('hero','press') else 'shirt' if role=='hero' else 'smart'
        self.outfit(outfit)
        if role=='hero' and outfit=='shirt':
            # Keep the source's fabric texture while moving the white outfit
            # away from the pale bed and kitchen cabinetry.
            for obj in self.meshes:
                part=obj.name.split('.')[0]
                tint=(.42,.56,.68,1) if part=='Top_shirt' else (.28,.34,.42,1) if part=='Trousers' else None
                if not tint:continue
                for mat in obj.data.materials:
                    if not mat or not mat.use_nodes:continue
                    bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
                    if not bs or not bs.inputs['Base Color'].is_linked:continue
                    links=mat.node_tree.links;source=bs.inputs['Base Color'].links[0].from_socket
                    mix=mat.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1
                    mix.inputs[2].default_value=tint;links.new(source,mix.inputs[1]);links.new(mix.outputs[0],bs.inputs['Base Color'])

    def outfit(self, name):
        keep=_GROUPS[name]
        for o in self.meshes:
            part=o.name.split('.')[0]
            o.hide_render=part in _CLOTHING and part not in keep

    def contact(self, side, target, influence=1.0, group='hand'):
        """Solve against actual joint heads, not the exported dummy bone tails.

        Rocketbox's converted bone tails do not coincide with the next joint,
        so Blender's ordinary IK constraints distort the mesh. A short CCD
        solve against evaluated wrist/ankle positions avoids that mismatch.
        """
        if influence<=.001:return
        if group=='hand':end='Hand';chain=('ForeArm','Arm')
        else:end='Foot';chain=('Leg','UpLeg')
        endpoint=self.rig.pose.bones['mixamorig:'+side+end]
        here=self.rig.matrix_world@endpoint.head
        target=here.lerp(Vector(target),max(0.,min(1.,influence)))
        for _ in range(4):
            for suffix in chain:
                joint=self.rig.pose.bones['mixamorig:'+side+suffix]
                pivot=self.rig.matrix_world@joint.head
                current=(self.rig.matrix_world@endpoint.head)-pivot
                desired=target-pivot
                if current.length<1e-5 or desired.length<1e-5:continue
                turn=current.rotation_difference(desired)
                if turn.angle>math.radians(50):turn=Quaternion(turn.axis,math.radians(50))
                world=Matrix.Translation(pivot)@turn.to_matrix().to_4x4()@Matrix.Translation(-pivot)
                joint.matrix=self.rig.matrix_world.inverted()@world@self.rig.matrix_world@joint.matrix
                bpy.context.view_layer.update()

    def hand_position(self, side='Left'):
        """Approximate the grip centre using the posed wrist and finger root."""
        hand=self.rig.pose.bones['mixamorig:'+side+'Hand']
        finger=self.rig.pose.bones.get('mixamorig:'+side+'HandMiddle1')
        a=self.rig.matrix_world@hand.head
        b=self.rig.matrix_world@finger.head if finger else a
        return a.lerp(b,.45)

    def look(self, target, yaw, weight=.6):
        head=self.rig.pose.bones['mixamorig:Head'];origin=self.rig.matrix_world@head.head
        delta=Vector(target)-origin
        if delta.length<1e-4:return
        front=Quaternion((0,0,1),yaw)@Vector((0,-1,0))
        turn=front.rotation_difference(delta.normalized())
        angle=min(turn.angle,math.radians(28))*weight
        turn=Quaternion(turn.axis,angle)
        world=Matrix.Translation(origin)@turn.to_matrix().to_4x4()@Matrix.Translation(-origin)
        head.matrix=self.rig.matrix_world.inverted()@world@self.rig.matrix_world@head.matrix
        bpy.context.view_layer.update()

    def animate(self, proxy, base, yaw, sit, walk, targets, smile, t):
        """Evaluate separate motion clips without changing the global frame."""
        kind=self.kind;role=self.role
        if role=='hero' and walk:
            name='Walk_Rig';frame=(abs(walk)/(2*math.pi)*28.8)%28.8
        elif role=='fan' and kind=='street' and t<23:
            name='Wave_Rig';frame=(8+t*9)%67.2
        elif role=='extra':
            name='Cheer_Rig';frame=(40+t*12)%590
        else:
            name='Idle_Rig';frame=(45+t*10)%280
        # Reset clip data on every frame; no pose accumulation across cuts.
        for bone,prop,idx,curve in self.curves[name]:
            getattr(bone,prop)[idx]=curve.evaluate(frame)
        self.rig.rotation_quaternion=(math.cos(yaw/2),0,0,math.sin(yaw/2))
        self.rig.location=(float(base[0]),float(base[1]),float(base[2])-.25*sit)
        # Suppress baked clip root travel; the authored blocking already moves
        # the whole rig. This keeps the two independent translations from adding.
        bpy.context.view_layer.update()
        hips=self.rig.pose.bones['mixamorig:Hips']
        hipworld=self.rig.matrix_world @ hips.head
        self.rig.location.x+=float(base[0])-hipworld.x
        self.rig.location.y+=float(base[1])-hipworld.y
        if role=='fan' and 34.793<t<40.117:
            # Small, non-accumulating nervous tremor in the waiting fan.
            self.rig.location.x+=.0025*math.sin(t*39.1)
        bpy.context.view_layer.update()
        if sit:
            for side,sign in (('Left',1),('Right',-1)):
                shoe=proxy.legs[sign][2]
                self.contact(side,shoe.location+Vector((0,.04,.025)),1.0,'foot')
        if role=='hero':
            amount=0.
            if kind=='bedroom':amount=1.
            elif kind=='kitchen':amount=smooth((t-12.35)/.45)*(1-smooth((t-16.4)/.7))
            elif kind=='street':amount=smooth((t-39.5)/.6)*(1-smooth((t-44.1)/.5))
            elif kind=='car':amount=1-smooth((t-48.5)/.7)
            elif kind=='night':amount=1-smooth((t-51.4)/.5)
            for side,sign in (('Left',1),('Right',-1)):
                if sign in targets:self.contact(side,proxy.arms[sign][2].location,amount)
        elif role=='fan' and kind=='street':
            amount=smooth((t-39.5)/.6)*(1-smooth((t-44.1)/.5))
            self.contact('Left',proxy.arms[1][2].location,amount)
        if role=='hero' and kind=='bedroom':self.look(proxy.arms[1][2].location,yaw,.6)
        elif role=='hero' and kind=='kitchen':self.look(proxy.arms[1][2].location,yaw,.35)
        elif role=='hero' and kind=='street' and 39<t<45:self.look((.77,-1.,1.55),yaw,.55)
        elif role=='fan' and kind=='street' and 39<t<45:self.look((-.12,-.24,1.58),yaw,.5)
        # The ARKit-compatible mesh shapes give a blink and restrained smile.
        blink_cycle=(t+.7)%3.6
        blink=math.sin((blink_cycle-.06)/.08*math.pi)**1.5 if .06<blink_cycle<.14 else 0
        for obj in self.meshes:
            if not obj.data.shape_keys:continue
            keys=obj.data.shape_keys.key_blocks
            for key,val in (('eyeBlinkLeft',blink),('eyeBlinkRight',blink),('mouthSmileLeft',smile*.38),('mouthSmileRight',smile*.38)):
                if key in keys:keys[key].value=val
