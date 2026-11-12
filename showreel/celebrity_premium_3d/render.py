"""Blender/Cycles rebuild of the existing one-minute animated celebrity story.

Geometry and pose timing derive from the previous reconstruction. This new
revision uses skinned Rocketbox characters, mocap walk clips and authored
prop-contact poses, with a new Cycles camera, lighting and material pass.
It remains a stylized, fictional preview, not a photorealistic master.
"""
from __future__ import annotations
import argparse, math, os, subprocess, sys, tempfile, time
from pathlib import Path

# Permit execution as a script from either a runner or the project root.
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import bpy
from mathutils import Vector, Quaternion
import numpy as np
from showreel.celebrity_recovery_3d import render as base
from showreel.celebrity_premium_3d.rig_actor import RigPuppet

FPS=24
COLORS={'warm':(1.0,.78,.60),'cool':(.55,.72,1.0),'day':(.90,.95,1.0)}
ASSETS=Path(os.environ.get('CINEMA_ASSETS','/home/user/cinema-assets'))

def track(obj,target):
    direction=Vector(target)-obj.location
    if direction.length:obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()

def look_camera(scene,eye,target,angle=42,focus=5.6):
    cam=scene.camera;cam.location=tuple(eye);track(cam,target)
    cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=24
    cam.data.lens=24/(2*math.tan(math.radians(angle)/2))
    cam.data.clip_start=.03;cam.data.clip_end=100
    cam.data.dof.use_dof=True;cam.data.dof.focus_distance=max(.2,(Vector(target)-Vector(eye)).length)
    cam.data.dof.aperture_fstop=focus


def add_area(name,pos,target,color,energy,size):
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.color=color;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(ob);ob.location=pos;track(ob,target)
    return ob


def init_meshes():
    bpy.ops.mesh.primitive_cube_add(size=2)
    cube=bpy.context.object
    mod=cube.modifiers.new('softened edges','BEVEL');mod.width=.018;mod.segments=3
    bpy.context.view_layer.objects.active=cube;bpy.ops.object.modifier_apply(modifier=mod.name)
    cube.data.name='rounded box base';cm=cube.data; bpy.data.objects.remove(cube,do_unlink=True)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,radius=1)
    sphere=bpy.context.object
    for face in sphere.data.polygons:face.use_smooth=True
    sphere.data.name='smooth sculpt base';sm=sphere.data;bpy.data.objects.remove(sphere,do_unlink=True)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=1,depth=2)
    cylinder=bpy.context.object
    for face in cylinder.data.polygons:face.use_smooth=len(face.vertices)==4
    cylinder.data.name='cylinder base';cy=cylinder.data;bpy.data.objects.remove(cylinder,do_unlink=True)
    return {'box':cm,'ellipsoid':sm,'cylinder':cy}


def material(color,kind):
    key='Mat_'+kind+'_'+'_'.join(f'{v:.3f}' for v in color)
    m=bpy.data.materials.get(key)
    if m:return m
    m=bpy.data.materials.new(key);m.diffuse_color=color;m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=color
    avg=sum(color[:3])/3
    rough=.52;metal=.0
    if color[:3] == base.HAIR[:3]:rough=.47
    if color[:3] == base.DARK[:3]:rough=.72
    if color[:3] == base.SKIN[:3]:
        rough=.58
        if 'Subsurface Weight' in bs.inputs:bs.inputs['Subsurface Weight'].default_value=.055
    if color[:3] == base.WHITE[:3]:rough=.43
    if color[:3] == (.34,.36,.37):rough=.27;metal=.72
    if color[:3] == (.63,.66,.65):rough=.24;metal=.68
    if color[:3] in ((.09,.11,.13),(.10,.12,.14),(.12,.14,.16)):
        rough=.27;metal=.50
    bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    textured={(.22,.20,.19),(.31,.32,.34),(.18,.14,.12),(.66,.66,.63),(.39,.45,.50),(.46,.42,.37),(.27,.25,.23)}
    if kind=='box' and color[:3] in textured:
        noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=75
        noise.inputs['Detail'].default_value=2
        bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.004
        m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    if color[:3] == (.60,.71,.70) and 'Emission Color' in bs.inputs:
        bs.inputs['Emission Color'].default_value=(.55,.68,.70,1)
        bs.inputs['Emission Strength'].default_value=1.5
    return m


def capsule_mesh(radius,half_length):
    """A closed, smooth, rounded tube rather than disconnected ellipsoid bones."""
    radius_ratio=min(.95,radius/half_length); rings=[]
    # Unit-radius mesh; scaling by (radius,radius,half_length) gives exact size.
    for i in range(9):
        a=-math.pi/2+(math.pi/2)*i/8
        rings.append((math.cos(a),-1+radius_ratio+radius_ratio*math.sin(a)))
    for i in range(9):
        a=(math.pi/2)*i/8
        rings.append((math.cos(a),1-radius_ratio+radius_ratio*math.sin(a)))
    verts=[];faces=[];n=24
    for r,z in rings:
        for i in range(n):
            a=math.tau*i/n;verts.append((r*math.cos(a),r*math.sin(a),z))
    for row in range(len(rings)-1):
        for i in range(n):
            a=row*n+i;b=row*n+(i+1)%n;c=(row+1)*n+(i+1)%n;d=(row+1)*n+i
            faces.append((a,b,c,d))
    mesh=bpy.data.meshes.new('rounded limb');mesh.from_pydata(verts,[],faces);mesh.update()
    for face in mesh.polygons:face.use_smooth=True
    return mesh


class BlenderWorld:
    def __init__(self,kind,width,samples,quality='FAST'):
        # A fresh scene for each set. No persistent file/mesh side effects.
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        self.scene=bpy.context.scene;self.kind=kind;self.t=0.;self.meshes=init_meshes();self.cache={};self.objects=[]
        sc=self.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=samples
        sc.cycles.use_denoising=True;sc.cycles.denoiser='OPENIMAGEDENOISE'
        sc.cycles.denoising_prefilter='FAST';sc.cycles.denoising_quality=quality
        sc.cycles.use_adaptive_sampling=True;sc.cycles.adaptive_threshold=.055;sc.render.use_persistent_data=True
        sc.cycles.max_bounces=4;sc.cycles.diffuse_bounces=2;sc.cycles.glossy_bounces=2;sc.cycles.transmission_bounces=2
        sc.render.resolution_x=width;sc.render.resolution_y=round(width*16/9);sc.render.resolution_y+=sc.render.resolution_y%2;sc.render.resolution_percentage=100
        sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.film_transparent=False
        sc.render.threads_mode='FIXED';sc.render.threads=max(1,int(os.getenv('CINEMA_THREADS','2')))
        sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
        sc.view_settings.exposure=-.90 if kind!='night' else -1.20
        if sc.world is None:sc.world=bpy.data.worlds.new('World')
        sc.world.use_nodes=True;bg=sc.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.12,.16,.23,1);bg.inputs['Strength'].default_value=.23
        cd=bpy.data.cameras.new('Story camera');cam=bpy.data.objects.new('Story camera',cd);sc.collection.objects.link(cam);sc.camera=cam
        if kind=='bedroom':
            add_area('Dawn window',(2.4,-3.6,4.7),(0,0,1),COLORS['cool'],560,4.2)
            add_area('Bedside warmth',(1.2,-1.8,2.8),(0,0,1),COLORS['warm'],260,2.1)
            add_area('Rim',(-2,2,3.6),(0,0,1.1),COLORS['day'],280,3)
        elif kind=='kitchen':
            add_area('Morning key',(1.8,-3.5,4.5),(0,0,1),COLORS['day'],750,4.1)
            add_area('Warm bounce',(-3,-1,2.9),(0,0,1),COLORS['warm'],290,3)
            add_area('Back edge',(1,2.2,3.2),(0,0,1),COLORS['cool'],240,2.5)
        elif kind in ('street','car'):
            add_area('Open sky',(1,-1,6),(0,0,0),COLORS['day'],950,6)
            add_area('Warm side',(-3,-2,3),(0,0,1),COLORS['warm'],350,3)
            add_area('Cool edge',(2,3,4),(0,0,1),COLORS['cool'],520,3)
            if kind=='car':add_area('Cabin face fill',(0,-2.0,1.8),(0,0,1.25),COLORS['warm'],130,1.4)
        else:
            bg.inputs['Color'].default_value=(.055,.09,.16,1);bg.inputs['Strength'].default_value=.27
            add_area('Window edge',(0,2,3),(.1,0,1.2),COLORS['cool'],520,2.7)
            add_area('Quiet warm fill',(2,-2,2.8),(0,0,1),COLORS['warm'],170,3.2)
            add_area('Face lift',(-3,-2,3),(0,0,1),COLORS['cool'],120,3)
    def close(self):pass
    def _mesh(self,kind,col):
        key=(kind,tuple(col))
        if key not in self.cache:
            data=self.meshes[kind].copy();data.materials.clear();data.materials.append(material(tuple(col),kind));self.cache[key]=data
        return self.cache[key]
    def add(self,kind,dims,color,pos=(0,0,0),q=(0,0,0,1)):
        limb_dims={(.057,.057,.155),(.049,.049,.14),(.069,.069,.20),(.057,.057,.195)}
        rounded=tuple(round(float(x),3) for x in dims)
        if kind=='ellipsoid' and rounded in limb_dims:
            key=('limb',rounded,tuple(color))
            if key not in self.cache:
                mesh=capsule_mesh(dims[0],dims[2]);mesh.materials.append(material(tuple(color),kind));self.cache[key]=mesh
            mesh=self.cache[key]
        else:mesh=self._mesh(kind,color)
        obj=bpy.data.objects.new(kind,mesh);self.scene.collection.objects.link(obj)
        if kind=='cylinder':obj.scale=(dims[0],dims[0],dims[1]/2)
        else:obj.scale=dims
        obj['shape']=kind;obj['dimensions_local']=list(dims);obj['original_pos']=list(pos)
        self.objects.append(obj);self.move(obj,pos,q)
        return obj
    def box(self,pos,dims,color):return self.add('box',dims,color,pos)
    def oval(self,pos,dims,color):return self.add('ellipsoid',dims,color,pos)
    def cylinder(self,pos,radius,length,color):return self.add('cylinder',(radius,length),color,pos)
    def move(self,obj,pos,q=(0,0,0,1)):
        obj.location=tuple(float(x) for x in pos);obj.rotation_mode='QUATERNION';obj.rotation_quaternion=(q[3],q[0],q[1],q[2])
    def view(self,eye,target,width=None,height=None,light=1.):
        self.requested_eye=Vector(eye);self.requested_target=Vector(target);self.flash=light>1.05
        return None
    def render(self,path):
        self.scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)

BaseActor=base.Actor
class Actor(BaseActor):
    def __init__(self,w,coat=base.DARK,beard=True):
        first=len(w.objects)
        super().__init__(w,coat,beard);self.w=w;self.basecoat=coat;self.ishero=beard
        o=lambda dims,col:w.oval((0,0,-20),dims,col)
        self.eye_white=[o((.034,.011,.040),base.SKIN) for _ in range(2)]
        self.catch=[o((.005,.004,.006),base.WHITE) for _ in range(2)]
        for eye in self.eyes:eye.scale=(.017,.010,.021)
        self.fringe.scale=(.18,.024,.037)
        if self.chin:self.chin.hide_render=True
        self.beard_parts=[o((.032,.014,.065),base.HAIR),o((.032,.014,.065),base.HAIR),o((.115,.014,.023),base.HAIR)] if beard else []
        self.joints={s:[o((.055,.055,.055),coat),o((.055,.055,.055),base.DARK)] for s in (-1,1)}
        self.fingers={s:[o((.014,.014,.036),base.WHITE) for _ in range(4)] for s in (-1,1)}
        self.thumb={s:o((.018,.018,.032),base.WHITE) for s in (-1,1)}
        if self.shirt:self.shirt.hide_render=True
        self.collar=[w.box((0,0,-20),(.053,.012,.016),base.WHITE) for _ in range(2)] if beard else []
        self.tie=o((.018,.012,.090),(.08,.09,.11,1)) if beard else None
        self.buttons=[o((.009,.007,.009),(.32,.34,.35,1)) for _ in range(3)] if beard else []
        self.strands=[o((.065,.022,.025),base.HAIR) for _ in range(4)]
        self.proxy_objects=w.objects[first:]
        role='hero' if beard else ('fan' if tuple(coat)==tuple(base.BLUE) else ('extra' if coat[:3]==(.28,.29,.36) else 'press'))
        asset='ryan.glb' if role=='hero' else ('emma.glb' if role=='fan' else 'marcus.glb')
        self.visible_actor=RigPuppet(ASSETS/asset,w.kind,role)
        for obj in self.proxy_objects:obj.hide_render=True
    def pose(self,base=(0,0,0),yaw=0,headyaw=0,sit=0,walk=0,targets=None,smile=0):
        w=self.w;b=base_module_vec(base);shift=-.25*sit;targets=dict(targets or {})
        # Relaxed hands and a small opposing arm swing replace the constant
        # hands-on-hips silhouette of the earlier preview.
        for s in (-1,1):
            if s not in targets:targets[s]=b+base_module_rot((s*.26,-.02,.84+shift),yaw)
        if self.ishero and w.kind=='street' and 28.4<=w.t<39.8:
            targets[1]=b+base_module_rot((.26,-.02,.84+shift),yaw)
        if self.ishero and walk and w.kind in ('street','night'):
            for s in (-1,1):
                swing=math.sin(walk+s*math.pi/2)
                targets[s]=b+base_module_rot((s*.26,.13*swing,.89+shift),yaw)
        if self.ishero and w.kind=='bedroom' and 7.35<w.t<8.15 and -1 in targets:
            tap=math.sin(math.pi*base_smooth((w.t-7.35)/.80))
            targets[-1]=targets[-1]+base_module_rot((.025*tap,-.015*tap,0),yaw)
        result=super().pose(base=base,yaw=yaw,headyaw=headyaw,sit=sit,walk=walk,targets=targets,smile=smile)
        hy=yaw+headyaw
        head=b+base_module_rot((0,0,1.64+shift),yaw)
        t=w.t;blink=max(0,1-abs(((t+.31)%3.7)-.07)/.07) if ((t+.31)%3.7)<.14 else 0
        def hp(offset):return head+base_module_rot(offset,hy)
        for i,s in enumerate((-1,1)):
            w.move(self.eye_white[i],hp((s*.075,-.218,.035)),base_module_qz(hy))
            w.move(self.eyes[i],hp((s*.075,-.231,.035)),base_module_qz(hy))
            w.move(self.catch[i],hp((s*.069,-.242,.045)),base_module_qz(hy))
            self.eye_white[i].scale.z=.040*max(.11,1-.9*blink);self.eyes[i].scale.z=.021*max(.12,1-.9*blink)
            self.catch[i].hide_render=blink>.65
        w.move(self.fringe,hp((0,-.190,.175)),base_module_qz(hy))
        for i,obj in enumerate(self.strands):w.move(obj,hp((-.115+i*.065,-.198,.172+.018*math.sin(i))),base_module_qz(hy))
        if self.beard_parts:
            w.move(self.beard_parts[0],hp((-.13,-.184,-.115)),base_module_qz(hy))
            w.move(self.beard_parts[1],hp((.13,-.184,-.115)),base_module_qz(hy))
            w.move(self.beard_parts[2],hp((0,-.199,-.185)),base_module_qz(hy))
        if self.collar:
            for i,s in enumerate((-1,1)):
                q=bpy_quat_mul(base_module_qz(yaw),base_module_euler(0,s*.40,s*.18))
                w.move(self.collar[i],b+base_module_rot((s*.045,-.143,1.30+shift),yaw),q)
            w.move(self.tie,b+base_module_rot((0,-.143,1.19+shift),yaw),base_module_qz(yaw))
            for i,obj in enumerate(self.buttons):w.move(obj,b+base_module_rot((.035,-.139,1.13+shift-i*.065),yaw),base_module_qz(yaw))
        if self.ishero and walk and w.kind in ('street','night'):
            # Stance targets are evaluated in world space from the root path.
            # Blend at start/stop to avoid stepping pops across a shot boundary.
            if w.kind=='street':
                start,end,omega=23.7,28.4,7.0
                root_at=lambda tt: base_blend((0,2.1,0),(-.12,-.24,0),base_smooth((tt-23.7)/4.1))
                yaw_at=lambda tt:0.
            else:
                start,end,omega=52.044,56.244,5.5
                root_at=lambda tt: base_blend((.55,-.4,0),(.05,.75,0),base_smooth((tt-52.044)/4.2))
                yaw_at=lambda tt:math.pi*base_smooth((tt-51.844)/1.7)
            period=math.tau/omega
            ramp=base_smooth((w.t-start)/.35)*(1-base_smooth((w.t-(end-.4))/.4))
            for s in (-1,1):
                phase=(walk/math.tau+(0 if s<0 else .5))%1;contact=w.t-phase*period
                def planted(tt):return root_at(tt)+base_module_rot((s*.11,-.15,.08),yaw_at(tt))
                a=planted(contact);c=planted(contact+period)
                if phase<.48:foot=a
                else:
                    u=(phase-.48)/.52;foot=base_blend(a,c,base_smooth(u));foot[2]+=.095*math.sin(math.pi*u)
                rest=b+base_module_rot((s*.11,-.08,.11),yaw)
                foot=base_blend(rest,foot,ramp)
                hip=b+base_module_rot((s*.105,0,.82+shift),yaw)
                knee,ankle=base_joint(hip,foot,.39,.37,base_module_rot((0,-1,-.1),yaw))
                upper,lower,shoe=self.legs[s]
                w.move(upper,(hip+knee)*.5,base_align_z(knee-hip));w.move(lower,(knee+ankle)*.5,base_align_z(ankle-knee))
                w.move(shoe,ankle+base_module_rot((0,-.04,-.025),yaw),base_module_qz(yaw))
        for s in (-1,1):
            upper,lower,palm=self.arms[s];legup,leglow,shoe=self.legs[s]
            # Segment local Z points at its distal end.
            elbow=upper.location+upper.rotation_quaternion@Vector((0,0,.15))
            knee=legup.location+legup.rotation_quaternion@Vector((0,0,.195))
            w.move(self.joints[s][0],elbow);w.move(self.joints[s][1],knee)
            hand=Vector(palm.location);armvec=hand-Vector(lower.location)
            if armvec.length<1e-5:armvec=Vector((0,0,-1))
            armvec.normalize();across=Vector((math.cos(yaw),math.sin(yaw),0))
            for i,finger in enumerate(self.fingers[s]):
                p0=hand+armvec*.052+across*((i-1.5)*.024)
                w.move(finger,p0,base_align_z(armvec))
            w.move(self.thumb[s],hand+armvec*.015+across*(s*.064),base_align_z(armvec+across*s*.55))
        self.visible_actor.animate(self,b,yaw,sit,walk,targets,smile,t)
        for obj in self.proxy_objects:obj.hide_render=True
        return result

# Name helpers are bound before monkey-patching the base module's Actor class.
base_module_vec=base.vec;base_module_rot=base.rot;base_module_qz=base.qz;base_align_z=base.align_z;base_smooth=base.smooth;base_joint=base.bone_joint;base_blend=base.blend
base.Actor=Actor  # inherited set builders create the same upgraded secondary characters

def base_module_euler(x,y,z):
    q=bpy.mathutils.Quaternion() if False else Quaternion((1,0,0,0))
    from mathutils import Euler
    q=Euler((x,y,z)).to_quaternion();return (q.x,q.y,q.z,q.w)
def bpy_quat_mul(a,b):
    x=Quaternion((a[3],a[0],a[1],a[2]));y=Quaternion((b[3],b[0],b[1],b[2]));q=x@y
    return (q.x,q.y,q.z,q.w)


def hide_at(w,pos,threshold=.02):
    for obj in w.objects:
        if (obj.location-Vector(pos)).length<threshold:obj.hide_render=True


def place_glb(path,target,box):
    if not path.exists():raise FileNotFoundError(f'asset not found: {path}')
    before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path))
    objs=[o for o in bpy.data.objects if o not in before]; roots=[o for o in objs if o.parent is None]
    bpy.context.view_layer.update(); pts=[]
    for ob in objs:
        if ob.type=='MESH':pts.extend(ob.matrix_world@Vector(v) for v in ob.bound_box)
    if not pts:raise RuntimeError(f'no mesh in {path}')
    lo=Vector(tuple(min(v[i] for v in pts) for i in range(3)));hi=Vector(tuple(max(v[i] for v in pts) for i in range(3)))
    size=hi-lo;factor=min(box[i]/max(size[i],1e-6) for i in range(3));center=(lo+hi)*.5
    root=bpy.data.objects.new('licensed furniture: '+path.stem,None);bpy.context.scene.collection.objects.link(root)
    for ob in roots:ob.parent=root
    root.scale=(factor,)*3;root.location=Vector(target)-center*factor
    return root

class Film(base.Film):
    def __init__(self,width,samples):self.w=None;self.kind=None;self.width=width;self.samples=samples;self.extra=[]
    def reset(self,kind):
        self.w=BlenderWorld(kind,self.width,self.samples);self.kind=kind;self.extra=[];self.props={}
        self.hero=Actor(self.w);getattr(self,'build_'+kind)();self.dress(kind)
    def dress(self,kind):
        w=self.w
        if kind=='bedroom':
            # Replace the crude cube table with a verified CC0 textured GLB.
            hide_at(w,(.85,-.48,.38));hide_at(w,(.85,-.48,.77))
            place_glb(ASSETS/'nightstand.glb',(.85,-.48,.39),(.68,.68,.78))
            # Linen panel and warm wall trim keep depth without photo plates.
            for x in (-2.2,-1.35,-.5,.35,1.2,2.05):w.box((x,2.30,1.35),(.012,.015,1.30),(.25,.25,.27,1))
            w.box((-.30,.31,.82),(.78,.72,.045),(.39,.45,.50,1))
            lamp=bpy.data.lights.new('Bedside practical','POINT');lamp.energy=28;lamp.color=COLORS['warm'];lamp.shadow_soft_size=.18
            ob=bpy.data.objects.new('Bedside practical',lamp);w.scene.collection.objects.link(ob);ob.location=(1.10,-.30,1.40)
            face=bpy.data.curves.new('Phone clock','FONT');face.body='05:40';face.align_x='CENTER';face.size=.025;face.extrude=.0001
            label=bpy.data.objects.new('Phone clock',face);w.scene.collection.objects.link(label);label.rotation_euler=(math.pi/2,0,0)
            face.materials.append(material((.055,.10,.13,1),'box'));self.props['clock']=label
        elif kind=='kitchen':
            for key in ('cup','coffee','handle'):self.props[key].scale*=.65
            for x in np.arange(-2.0,2.2,.4):w.box((float(x),2.01,1.22),(.006,.006,.27),(.45,.43,.40,1))
            for x in (-1.2,-.4,.4,1.2):w.box((x,1.82,1.90),(.23,.012,.015),(.62,.58,.51,1))
            for x in (-1.0,-.55):w.cylinder((x,.00,1.05),.07,.18,(.39,.48,.43,1))
        elif kind=='street':
            for x in (-2,-1.6,1.4,1.8):w.box((x,1.60,1.55),(.025,.025,1.42),(.28,.30,.31,1))
            for x in (-1.7,1.65):w.box((x,1.58,2.15),(.18,.016,.34),(.20,.31,.36,1))
            # Modeled carpet, doorway details and planters give the public
            # arrival a readable physical setting without an image plate.
            w.box((0,.50,.004),(.56,1.08,.014),(.30,.045,.052,1))
            for x in (-2.05,2.05):
                w.cylinder((x,.95,.19),.18,.38,(.22,.20,.19,1))
                for dx,dy,z in ((0,0,.60),(.12,.04,.51),(-.1,-.03,.53)):
                    w.oval((x+dx,.95+dy,z),(.20,.16,.26),(.15,.30,.21,1))
            # A third moving member of the press, placed clear of the hero.
            self.extra=[Actor(w,(.28,.29,.36,1),False)]
            for x in (-1.75,1.75):
                w.box((x,-.52,.055),(.10,.11,.055),(.22,.22,.22,1))
        elif kind=='car':
            # Lower the roof and rake the pillars into a coupe silhouette.
            # The old vertical white-box pillars are removed, not layered.
            for ob in w.objects:
                original=Vector(ob['original_pos'])
                if (original-Vector((.16,0,1.95))).length<.01:ob.location.z=1.97
                if any((original-Vector((x,y,1.30))).length<.01 for x in (-.80,1.10) for y in (-.58,.58)):
                    ob.hide_render=True
            for y in (-.58,.58):
                for a,b in (((-1.03,y,.72),(-.70,y,1.95)),((1.35,y,.72),(.94,y,1.95))):
                    a=Vector(a);b=Vector(b);rod=w.box((a+b)*.5,(.045,.045,(b-a).length/2),(.12,.14,.16,1))
                    w.move(rod,(a+b)*.5,base.align_z(b-a))
            # Upholstery is behind the seated character, never between the
            # camera and the face. The door is animated by the base scene.
            w.box((.2,.40,1.02),(.38,.09,.33),(.15,.13,.13,1))
            w.box((.05,.40,1.48),(.13,.07,.14),(.13,.12,.12,1))
            self.props['inside_handle']=w.box((0,0,-20),(.10,.018,.018),(.42,.44,.44,1))
            for x in (-2.0,0,2.0):w.box((x,5.85,1.7),(.55,.02,1.7),(.23,.30,.35,1))
            # Rims, bumpers and lamp lenses make the vehicle legible as a car.
            for x in (-1.0,1.0):
                hub=w.cylinder((x,-.805,.29),.135,.02,(.48,.51,.52,1))
                w.move(hub,(x,-.805,.29),base.p.getQuaternionFromEuler((math.pi/2,0,0)))
            w.box((-1.62,-.02,.28),(.035,.70,.07),(.24,.27,.29,1))
            w.box((1.63,-.02,.28),(.035,.70,.07),(.24,.27,.29,1))
            for y in (-.45,.45):
                w.box((-1.67,y,.59),(.025,.15,.065),(.82,.80,.65,1))
                w.box((1.67,y,.57),(.025,.15,.06),(.52,.06,.05,1))
            w.box((.15,.63,1.26),(.81,.018,.37),(.16,.28,.35,1))
            # Spare pieces stay hidden unless explicitly posed for a shot.
            self.props['steering_rim']=[w.box((0,0,-20),(.12,.018,.018),(.07,.075,.08,1)) for _ in range(4)]
        elif kind=='night':
            w.box((0,1.78,2.72),(1.50,.04,.04),(.28,.31,.34,1))
            w.box((0,1.78,.79),(1.50,.04,.04),(.28,.31,.34,1))

    def update_bedroom(self,t):
        # Place the pelvis on the front edge of the mattress, not inside its
        # solid base. The shot still follows the original phone story beats.
        w=self.w;b=base.vec((-.05,-.82,0));sit=.5
        reach=base.smooth((t-2.0)/1.4);lift=base.smooth((t-3.8)/1.3)
        resting=b+base.vec((.26,-.05,.83-.25*sit))
        table=self.props['handhold'];read=b+base.vec((.21,-.30,1.27-.25*sit))
        target=base.blend(base.blend(resting,table,reach),read,lift)
        other=base.blend(b+base.vec((-.26,-.03,.68)),target+base.vec((-.10,-.02,.02)),base.smooth((t-6.4)/1.0)*(1-base.smooth((t-8.5)/.8)))
        self.hero.pose(b,sit=sit,headyaw=-.15*lift,targets={1:target,-1:other})
        phone=base.blend(base.vec((.70,-.53,.83)),target+base.vec((.02,-.025,.08)),reach)
        w.move(self.props['phone'],phone);w.move(self.props['screen'],phone+base.vec((0,-.016,0)))
        self.props['clock'].location=tuple(phone+base.vec((0,-.021,.025)))
        return w.view((2.4,-4.0,2.35),(.10,-.1,1.05))

    def update_kitchen(self,t):
        w=self.w;u=t-11.914;b=base.vec((-.05,.55,0))
        take=base.smooth((u-1.0)/.6);lift=base.smooth((u-1.8)/.65)*(1-base.smooth((u-3.25)/.8));put=base.smooth((u-4.1)/.55)
        # Keep the resting mug within arm's reach, so the hand meets the
        # handle before the cup rises and stays with it through the put-down.
        resting=base.vec((.31,.18,1.005))
        cup=base.blend(resting,base.vec((.17,.18,1.44)),lift)
        if put>0:cup=base.blend(cup,resting,put)
        for key,delta in (('cup',(0,0,0)),('coffee',(0,0,.058)),('handle',(.065,0,.013))):w.move(self.props[key],cup+base.vec(delta))
        hand=base.blend(b+base.vec((.27,-.03,.93)),cup+base.vec((.06,0,0)),take*(1-put))
        self.hero.pose(b,targets={1:hand},headyaw=-.12*lift)
        return w.view((2.35,-4.1,2.42),(.08,.15,1.16))

    def update_car(self,t):
        w=self.w;u=t-46.293;angle=-.65*(1-base.smooth((u-.7)/1.9));pivot=base.vec((-.52,-.72,0))
        w.move(self.props['door'],pivot+base.rot((.59,0,.69),angle),base.qz(angle))
        w.move(self.props['door_top'],pivot+base.rot((.59,0,1.18),angle),base.qz(angle))
        w.move(self.props['door_pillar'],pivot+base.rot((1.15,0,1.02),angle),base.qz(angle))
        b=base.vec((0,-.02,.20));pull=base.smooth(u/.5)*(1-base.smooth((u-2.2)/.5))
        target=base.blend(b+base.vec((.25,-.1,.72)),pivot+base.rot((.65,.05,.88),angle),pull)
        self.hero.pose(b,sit=1,targets={1:target})
        return w.view((3,-5,1.85),(.05,0,1.08))

    def render_time(self,t,path):
        if t<11.914:kind='bedroom'
        elif t<17.237:kind='kitchen'
        elif t<46.293:kind='street'
        elif t<50.544:kind='car'
        else:kind='night'
        if kind!=self.kind:self.reset(kind)
        self.w.t=t;getattr(self,'update_'+kind)(t)
        if kind=='car':
            # Door handle follows the same hinge as the near-side door.
            u=t-46.293;angle=-.65*(1-base.smooth((u-.7)/1.9));pivot=base.vec((-.52,-.72,0))
            position=pivot+base.rot((.90,-.065,.83),angle)
            self.w.move(self.props['inside_handle'],position,base.qz(angle))
        if kind=='street' and self.extra:
            extra_base=base.vec((1.54,-1.20,0));arm=extra_base+base.vec((-.26,.06,1.0+.10*math.sin(t*3.3)))
            self.extra[0].pose(extra_base,yaw=math.pi-.1,targets={1:arm},headyaw=.1*math.sin(t))
        self.cinematography(t)
        self.w.render(path)
    def cinematography(self,t):
        w=self.w;eye=w.requested_eye.copy();target=w.requested_target.copy();angle=42;fstop=6.3
        if t<3.8:
            eye=Vector((2.1,-4.4,2.1));target=Vector((.16,-.38,1.05));angle=48;start,end=0,3.8
        elif t<11.914:
            eye=Vector((1.55,-2.95,1.95));target=Vector((-.08,-.48,1.20));angle=38;start,end=3.8,11.914
        elif t<17.237:
            eye=Vector((2.0,-3.5,2.05));target=Vector((.02,.30,1.23));angle=38;start,end=11.914,17.237
        elif t<23:
            start,end=17.237,23
        elif t<29.81:
            # Tracking position follows the animated torso, not a guessed path.
            torso=Vector(self.hero.torso.location);target=Vector((torso.x,torso.y,1.22))
            eye=target+Vector((-2.5,-4.0,.95));angle=39;start,end=23,29.81
        elif t<34.793:
            torso=Vector(self.hero.torso.location);target=Vector((torso.x,torso.y,1.53))
            eye=target+Vector((-1.25,-2.6,.20));angle=36;fstop=4.5;start,end=29.81,34.793
        elif t<40.117:
            # Reverse angle reveals the fan's face before the wide contact.
            eye=Vector((1.90,.42,1.82));target=Vector((.77,-1.00,1.38));angle=39;start,end=34.793,40.117
        elif t<46.293:
            start,end=40.117,46.293
        elif t<50.544:
            eye=Vector((1.15,-2.45,1.45));target=Vector((.02,-.02,1.37));angle=30;start,end=46.293,50.544
        else:
            eye=Vector((3.0,-4.4,2.30));target=Vector((.22,.42,1.22));angle=39;start,end=50.544,60
        # Motivated, restrained push: no shakes, whip transitions or forced DOF.
        u=base.smooth((t-start)/max(.01,end-start));eye=eye+(target-eye)*(.065*u)
        look_camera(w.scene,eye,target,angle,fstop)
        for o in w.scene.objects:
            if o.type=='LIGHT' and o.name=='Warm side':o.data.energy=950 if w.flash else 350


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--width',type=int,default=540);ap.add_argument('--samples',type=int,default=6)
    ap.add_argument('--start',type=float,default=0);ap.add_argument('--end',type=float,default=60)
    ap.add_argument('--stills',default='');ap.add_argument('--out',type=Path,default=Path('/home/user/cinema-premium-frames'));a=ap.parse_args()
    if not 0<=a.start<a.end<=60:raise SystemExit('invalid range')
    a.out.mkdir(parents=True,exist_ok=True);film=Film(a.width,a.samples);started=time.monotonic()
    if a.stills: jobs=[(round(float(s)*FPS),float(s),f'still_{float(s):05.2f}.png') for s in a.stills.split(',')]
    else:jobs=[(f,f/FPS,f'frame_{f:05d}.png') for f in range(math.ceil(a.start*FPS),math.ceil(a.end*FPS))]
    print('JOBS',len(jobs),'WIDTH',a.width,'SAMPLES',a.samples,flush=True)
    for i,(f,t,name) in enumerate(jobs):
        film.render_time(t,a.out/name)
        if i%12==0 or i==len(jobs)-1: print('FRAME',f,'done',i+1,'/',len(jobs),'elapsed',round(time.monotonic()-started,1),flush=True)
    print('DONE',a.out,round(time.monotonic()-started,1),flush=True)

if __name__=='__main__':main()
