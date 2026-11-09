"""Third-person fictional celebrity day. 3D geometry and CC0 animation, no plates."""
import os,sys,argparse,math,json,subprocess,tempfile,shutil
from pathlib import Path
import bpy
from mathutils import Vector
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'celebrity_3d'))
from action_timeline import Clip,apply
parser=argparse.ArgumentParser();parser.add_argument('--start',type=int,default=0);parser.add_argument('--end',type=int,default=60);parser.add_argument('--samples',type=int,default=2);parser.add_argument('--width',type=int,default=480);parser.add_argument('--stills',action='store_true');parser.add_argument('--output',default='deliverables/celebrity-third-person-3d.mp4');args=parser.parse_args()
FPS=24;W=args.width;H=round(W*9/16);H+=H%2
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=args.samples;sc.cycles.use_denoising=True;sc.render.use_persistent_data=True;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=W;sc.render.resolution_y=H;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX';sc.world=bpy.data.worlds.new('Atmosphere');sc.world.color=(.18,.15,.19)

def mat(name,c,metal=0,rough=.6,em=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if em:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=em
 return m
cols={'wall':(.24,.18,.23),'trim':(.08,.07,.09),'floor':(.17,.105,.095),'cream':(.61,.55,.50),'white':(.8,.79,.73),'red':(.42,.035,.055),'dark':(.025,.026,.035),'gold':(.59,.36,.16),'sky':(.73,.39,.29),'sky2':(.35,.26,.35),'glass':(.13,.19,.24),'grass':(.12,.20,.13),'green':(.18,.25,.17),'black':(.012,.014,.02),'skin':(.42,.25,.19),'blue':(.085,.12,.16),'screen':(.6,.72,.73),'lamp':(.9,.61,.38)}
M={k:mat(k,c,metal=.5 if k=='gold' else 0,rough=.3 if k in ('gold','glass') else .7,em=.35 if k in ('sky','screen','lamp') else 0) for k,c in cols.items()}
def box(name,loc,dim,k,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(M[k])
 if bevel:m=o.modifiers.new('bevel','BEVEL');m.width=bevel;m.segments=2;o.modifiers.new('normals','WEIGHTED_NORMAL')
 return o
def sphere(name,loc,scale,k):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(M[k]);bpy.ops.object.shade_smooth();return o
def rod(name,a,b,r,k):
 a,b=Vector(a),Vector(b);v=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=v.length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.data.materials.append(M[k]);return o
def area(loc,target,power,size,color):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def base(x,wall='wall',floor='floor'):
 box('floor',(x,0,-.1),(13,12,.2),floor);box('wall',(x,4,2.9),(13,.15,5.8),wall)
 for xx in range(-6,7,2):box('wall trim',(x+xx,3.9,2.9),(.025,.03,5.8),'trim')
 area((x-3,-4,5),(x,0,1),700,5,(1,.65,.47));area((x+3,1,5),(x,0,1),420,4,(.53,.59,1))
def window(x):
 box('sunset window',(x,3.88,2.8),(5.5,.06,3.8),'sky')
 for j in range(22):
  xx=x-2.6+j*.25;h=.3+(j*43%19)*.095;box('skyline',(xx,3.75,1.03+h/2),(.19,.10,h),'sky2')
  for k in range(int(h/.25)):
   if (j+k)%3:box('lit window',(xx,3.685,1.13+k*.22),(.035,.02,.05),'lamp')
 sphere('low sun',(x+1.25,3.78,3.15),(.36,.04,.36),'lamp')
 for xx in (x-2.75,x,x+2.75):box('window frames',(xx,3.68,2.8),(.075,.1,3.85),'trim')
 box('window sill',(x,3.65,.88),(5.7,.35,.12),'wood' if 'wood' in M else 'floor')
ATTACHMENTS=[]
def rig(x,y,shirt='cream',size=1):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(P.parent/'celebrity_3d/assets/human.glb'));added=set(bpy.context.scene.objects)-before
 o=next(q for q in added if q.type=='ARMATURE');mesh=next(q for q in added if q.type=='MESH' and q.parent==o)
 for q in added:
  if q.type=='MESH' and q.parent is None:bpy.data.objects.remove(q,do_unlink=True)
 o.location=(x,y,0);o.rotation_euler.z=math.pi;o.scale=(size,)*3
 m=bpy.data.materials.new('tailored '+shirt);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF'];p.inputs['Roughness'].default_value=.75
 tex=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['Generated'],sep.inputs[0]);cmp=n.new('ShaderNodeMath');cmp.operation='GREATER_THAN';cmp.inputs[1].default_value=.5;l.new(sep.outputs['Z'],cmp.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(*cols['dark'],1);mix.inputs[2].default_value=(*cols[shirt],1);l.new(cmp.outputs[0],mix.inputs[0]);head=n.new('ShaderNodeMath');head.operation='GREATER_THAN';head.inputs[1].default_value=.84;l.new(sep.outputs['Z'],head.inputs[0]);mix2=n.new('ShaderNodeMixRGB');mix2.inputs[2].default_value=(*cols['skin'],1);l.new(mix.outputs[0],mix2.inputs[1]);l.new(head.outputs[0],mix2.inputs[0]);l.new(mix2.outputs[0],p.inputs['Base Color']);mesh.data.materials.clear();mesh.data.materials.append(m)
 # Stylised round face and eyes are real meshes attached to the head bone.
 for nm,loc,sz,col in (('head',(x,y,1.68*size),(.155*size,.14*size,.19*size),'dark'),('eye L',(x-.055*size,y-.134*size,1.70*size),(.027*size,.017*size,.03*size),'white'),('eye R',(x+.055*size,y-.134*size,1.70*size),(.027*size,.017*size,.03*size),'white')):
  part=sphere(nm,loc,sz,col);bpy.context.view_layer.update();relative=(o.matrix_world @ o.data.bones['DEF-head'].matrix_local).inverted() @ part.matrix_world.copy();ATTACHMENTS.append((part,o,relative))
 return o
# Apartment: tailored room, city, practical lamp, bed, wardrobe.
base(0);window(0)
box('bed base',(-2,1,.35),(2.2,2.6,.5),'dark',.07);box('mattress',(-2,1,.68),(2.12,2.5,.2),'cream',.07);box('throw',(-2,.3,.81),(2.05,1,.08),'blue',.03);box('pillows',(-2,1.8,.84),(1.8,.5,.15),'white',.05)
box('side table',(1.9,2.3,.5),(.8,.7,1),'floor',.04);rod('lamp stem',(1.9,2.3,1),(1.9,2.3,1.65),.025,'gold');sphere('lamp',(1.9,2.3,1.65),(.22,.22,.14),'lamp')
box('phone',(.8,.45,.93),(.18,.32,.035),'black',.015);box('phone screen',(.8,.45,.952),(.14,.27,.008),'screen',.008);box('console',(.8,.45,.45),(.9,.7,.9),'floor',.04)
box('wardrobe',(-5,2,1.5),(1.3,1.4,3),'trim',.03)
home=rig(.15,.35,'cream');apply(home,[Clip('Idle_Loop_Rig',0,3.5,.2,True),Clip('Interact_Rig',3.3,7.1,.2),Clip('PickUp_Table_Rig',7,12.5,.2),Clip('Walk_Loop_Rig',19,25.6,.2,True),Clip('Idle_Loop_Rig',53.3,60,.2,True)])
# Studio training, wall mirrors and benches.
base(20,'sky2','dark')
for j in range(4):
 box('mirror',(17.2+j*1.8,3.86,2.3),(1.65,.06,3),'glass');box('mirror frame',(16.36+j*1.8,3.75,2.3),(.05,.1,3),'gold')
for xx in (16,24):
 rod('rack bar',(xx,2,.2),(xx,2,2.2),.045,'dark')
 for z in (.5,1,1.5):rod('rack horizontal',(xx-.45,2,z),(xx+.45,2,z),.025,'gold')
box('bench seat',(21,1,.52),(2,.65,.15),'dark',.06)
for xx in (20.2,21.8):box('bench legs',(xx,1,.25),(.1,.5,.5),'trim')
for xx in (18,19,22,23):sphere('weight',(xx,-.5,.12),(.14,.14,.14),'trim')
gym=rig(20,0,'red');apply(gym,[Clip('Jog_Fwd_Loop_Rig',12.5,15.9,.2,True),Clip('Punch_Jab_Rig',15.7,17.5,.2),Clip('Punch_Cross_Rig',17.3,19.1,.2)])
# Studio: camera rig, set, interview chair.
base(40,'sky2','floor');box('studio accent',(40,3.85,2.5),(5,.05,3),'wall');box('studio sofa',(41,1,.5),(2.2,.9,.5),'blue',.12);box('studio back',(41,1.4,.95),(2.2,.2,.95),'blue',.1)
for xx in (36.5,43.5):
 rod('light stand',(xx,1,.1),(xx,1,2.7),.035,'trim');box('softbox',(xx,.95,2.6),(.75,.22,.6),'lamp',.04)
box('camera',(37.2,-1.2,1.6),(.85,.6,.5),'dark',.08);sphere('lens',(37.2,-.85,1.6),(.28,.14,.28),'glass')
for xx,yy in ((36.9,-1.5),(37.5,-1.5),(37.2,-.9)):rod('tripod',(37.2,-1.2,1.4),(xx,yy,0),.035,'trim')
studio=rig(40,.5,'cream');apply(studio,[Clip('Idle_Loop_Rig',32.3,34,.2,True),Clip('Interact_Rig',33.8,39.4,.2)])
# Press event: carpet, metal barriers, spotlights, crowd.
base(60,'wall','dark');box('red carpet',(60,0,.02),(3.6,10,.04),'red');box('feature wall',(60,3.85,2.6),(8,.06,3.8),'blue')
for xx in (57.5,62.5):
 for yy in (-3,-1,1,3):rod('stanchion',(xx,yy,0),(xx,yy,1),.04,'gold');sphere('post cap',(xx,yy,1.03),(.09,.09,.09),'gold')
 for z in (.65,.9):rod('railing',(xx,-3,z),(xx,3,z),.025,'gold')
 for yy in (-2.5,-.5,1.5):
  cam=box('camera phone',(xx+(.35 if xx<60 else -.35),yy,1.45),(.20,.10,.32),'black',.02)
  box('phone screen',(cam.location.x,yy-.055,1.45),(.14,.01,.24),'screen')
  sphere('photographer head',(xx+(.6 if xx<60 else -.6),yy,1.65),(.16,.16,.19),'skin')
  box('photographer body',(xx+(.6 if xx<60 else -.6),yy,1.1),(.48,.3,.8),'dark',.08)
fan=rig(61.35,1.1,'blue',.9);apply(fan,[Clip('Idle_Loop_Rig',25.5,39.2,.2,True),Clip('Interact_Rig',39.3,46.7,.2),Clip('Idle_Loop_Rig',46.8,53.4,.2,True)])
red=rig(60,.5,'red');apply(red,[Clip('Walk_Formal_Loop_Rig',25.5,31,.2,True),Clip('Interact_Rig',30.8,32.5,.2),Clip('Interact_Rig',39.3,46.7,.2),Clip('Walk_Formal_Loop_Rig',46.5,53.5,.2,True)])
# camera tracks a subject in third-person at every cut.
bpy.ops.object.camera_add();cam=bpy.context.object;sc.camera=cam;cam.data.lens=38;cam.data.sensor_width=36
cuts=[0,3.4,7,12.5,16,19,25.5,28.7,32.3,36,39.3,43,46.7,50.3,53.4,57.4,60]
def update(t):
 if t<3.4:focus=(.15,.35,1.35);pos=(-2.8,-6,2.6);lens=37
 elif t<7:focus=(.15,.35,1.5);pos=(1.15,-4.2,1.95);lens=52
 elif t<12.5:focus=(.15,.35,1.25);pos=(-1.4,-4.5,2.3);lens=45
 elif t<16:focus=(20,0,1.1);pos=(17.5,-5.3,2.3);lens=38
 elif t<19:focus=(20,0,1.3);pos=(21.7,-4.6,2.0);lens=48
 elif t<25.5:focus=(.15,.35,1.15);pos=(1.6,-5.3,2.2);lens=40
 elif t<28.7:focus=(60,.5,1.25);pos=(58,-6,2.2);lens=38
 elif t<32.3:focus=(60,.5,1.4);pos=(61.4,-4.4,2);lens=50
 elif t<36:focus=(40,.5,1.3);pos=(38.6,-5,2.1);lens=45
 elif t<39.3:focus=(40,.5,1.45);pos=(41,-4.1,1.9);lens=55
 elif t<43:focus=(60,.5,1.25);pos=(58,-5,2.0);lens=44
 elif t<46.7:focus=(60,.5,1.35);pos=(61.3,-4.2,2.0);lens=52
 elif t<50.3:focus=(60,.5,1.3);pos=(58.8,-6.2,2.1);lens=40
 elif t<53.4:focus=(60,.5,1.5);pos=(61.2,-4,1.9);lens=55
 elif t<57.4:focus=(.15,.35,1.2);pos=(-1,-5.7,2.15);lens=42
 else:focus=(.15,.35,1.45);pos=(1,-4.5,2);lens=50
 local=t-max(c for c in cuts if c<=t);cam.location=(pos[0]+local*.025,pos[1]+local*.045,pos[2]);cam.rotation_euler=(Vector(focus)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 # Small root paths on the walking segments. Motion remains kinematic.
 home.location.x= -.4+.12*(t-19) if 19<=t<25.5 else .15
 red.location.y= 1.0-.17*(t-25.5) if 25.5<=t<31 else (1.0-.18*(t-46.7) if 46.7<=t<53.4 else .5)
def render(t,path):
 sc.frame_set(round(t*FPS));update(t);bpy.context.view_layer.update()
 for obj,rig,relative in ATTACHMENTS:obj.matrix_world=rig.matrix_world @ rig.pose.bones['DEF-head'].matrix @ relative
 sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
def overlay(p,t):
 im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im,'RGBA');bar=round(H*.055);d.rectangle((0,0,W,bar),fill=(0,0,0,255));d.rectangle((0,H-bar,W,H),fill=(0,0,0,255));font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',max(9,round(W*.019)))
 d.text((int(W*.035),bar+6),'A DAY IN THE SPOTLIGHT',font=font,fill=(240,225,206,220));d.text((int(W*.97),bar+6),'FICTIONAL',font=font,fill=(240,225,206,200),anchor='ra')
 return im
if args.stills:
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/'frame.png'
  for t in (1,5,9,14,17,21,27,30,34,37,41,44,49,52,56,58):render(t,p);overlay(p,t).save(P/f'preview-{t}.jpg',quality=92)
else:
 out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);ff=imageio_ffmpeg.get_ffmpeg_exe()
 with tempfile.TemporaryDirectory() as td:
  tmp=Path(td);frame=tmp/'frame.png';proc=subprocess.Popen([ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(out)],stdin=subprocess.PIPE)
  for n in range(FPS*args.start,FPS*args.end):
   t=n/FPS;render(t,frame);proc.stdin.write(overlay(frame,t).tobytes())
   if n%48==0:print('RENDER_PROGRESS',n,flush=True)
  proc.stdin.close()
  if proc.wait():raise RuntimeError('encode failed')
 print('OUTPUT',out,flush=True)
