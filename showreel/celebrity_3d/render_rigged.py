"""Original fictional celebrity-day POV: rendered 3D geometry, no image plates.
Stylized character is not a likeness, and the story is not factual biography.
"""
import argparse,math,os,subprocess,tempfile,wave
from pathlib import Path
import bpy, numpy as np
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parent; VOICE=ROOT.parent/'celebrity_pov'/'audio'
FPS=24;DURATION=60;W,H=360,640
CUTS=[0,8,16,24,42,51,60]
WORDS=[(0.35,3.6,'YOU WAKE UP AS','CRISTIANO RONALDO.'),(3.6,7.8,'THE VIEW IS INCREDIBLE.','BUT THERE IS MORE.'),(8,11.2,'BREAKFAST FUELS','THE DAY AHEAD.'),(11.2,15.7,'TRAINING LIKE A CHAMPION','IS ANOTHER STORY.'),(16.2,19.8,'ON THE TRAINING PITCH,','EVERY TOUCH MATTERS.'),(19.8,23.9,'STRENGTH. MOVEMENT.','SKILL.'),(24.15,27.6,'NOW YOU STEP OUTSIDE.','FANS RECOGNIZE YOU.'),(27.6,33.2,'A QUICK TRIP BECOMES','CAMERAS AND CROWDS.'),(33.6,37.4,'THE SPOTLIGHT OPENS','DOORS...'),(37.4,41.6,'BUT PRIVATE MOMENTS','GET HARDER TO FIND.'),(41.85,45.7,'AFTER THE NOISE,','TIME TO RECOVER.'),(45.7,50.6,'AND BE CLOSE TO','THE PEOPLE YOU LOVE.'),(51,54.4,'LUXURY. DISCIPLINE.','ATTENTION.'),(54.4,59.8,'WOULD YOU TAKE','THIS LIFE FOR A DAY?')]
P=argparse.ArgumentParser();P.add_argument('--output',default='deliverables/monarch-celebrity-pov-3d.mp4');P.add_argument('--stills',action='store_true');P.add_argument('--samples',type=int,default=2);P.add_argument('--width',type=int,default=W);P.add_argument('--start',type=int,default=0);P.add_argument('--end',type=int,default=60);P.add_argument('--silent',action='store_true');P.add_argument('--experimental-sequences',action='store_true');P.add_argument('--experimental-kick',action='store_true');args=P.parse_args()
W=args.width;H=round(W*16/9); H+=H%2
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=args.samples;scene.cycles.use_denoising=True;scene.render.use_persistent_data=True;scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=W;scene.render.resolution_y=H;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX';scene.world=bpy.data.worlds.new('World');scene.world.color=(.22,.22,.22)

def mat(name,color,metal=0,rough=.65,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emit:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 return m
M={}
for k,c in {'ink':(.025,.035,.065),'navy':(.04,.075,.13),'cream':(.72,.68,.59),'white':(.8,.83,.79),'stone':(.21,.23,.26),'wood':(.23,.115,.065),'gold':(.8,.49,.13),'skin':(.42,.22,.13),'hair':(.025,.018,.014),'red':(.55,.025,.035),'green':(.055,.25,.12),'grass2':(.07,.32,.15),'black':(.008,.012,.018),'blue':(.055,.15,.26),'glass':(.15,.35,.42),'pink':(.5,.20,.18)}.items(): M[k]=mat(k,c,metal=.35 if k=='gold' else 0,rough=.42 if k in ('gold','glass') else .72)
M['lamp']=mat('warm_light',(.95,.69,.38),emit=1.5);M['screen']=mat('cool_screen',(.24,.57,.75),emit=.6)

def linkmat(o,key):o.data.materials.append(M[key]);return o

def box(name,loc,scale,key,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;linkmat(o,key)
 if bevel:
  mod=o.modifiers.new('Soft edges','BEVEL');mod.width=bevel;mod.segments=2;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o

def ball(name,loc,scale,key,segments=12,rings=8):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;linkmat(o,key)
 for p in o.data.polygons:p.use_smooth=True
 return o

def rod(name,a,b,r,key):
 a,b=Vector(a),Vector(b);v=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=v.length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();linkmat(o,key);return o

def putrod(obj,a,b):
 a,b=Vector(a),Vector(b);v=b-a;obj.location=(a+b)/2;obj.rotation_euler=v.to_track_quat('Z','Y').to_euler();obj.scale.z=v.length/obj.get('base_length',v.length)

def area(loc,energy,size,color):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector((loc[0],0,0.5))-o.location).to_track_quat('-Z','Y').to_euler();return o

def world_base(x,back='navy',floor='stone'):
 box('floor',(x,0,-.11),(12,12,.2),floor);box('rear wall',(x,3,3),(12,.2,6),back)
 for j in range(5):box('wall trim',(x-5+j*2.5,2.85,2.8),(.025,.025,5.6),'gold')
 area((x-3,-3,6),650,5,(1,.78,.55));area((x+4,0,5),450,4,(.47,.66,1))

def city_window(x):
 box('window recess',(x,2.84,2.9),(5.4,.10,3.9),'glass');box('glowing horizon',(x,2.70,2.5),(5.1,.05,2.9),'screen')
 for i in range(17):
  xx=x-2.5+i*.31;h=.4+(i*37%15)*.08;box('city tower',(xx,2.6,1.65+h/2),(.22,.08,h),'navy')
  for j in range(int(h/.35)):
   if (i+j)%3:box('city light',(xx,2.53,1.8+j*.28),(.04,.02,.06),'lamp')
 for xx in (x-2.7,x,x+2.7):box('window frame',(xx,2.52,2.9),(.09,.09,4),'ink')
 box('window frame',(x,2.52,2.9),(5.4,.09,.09),'ink')

def person(x,y,z=0,shirt='white',shorts='ink',scale=1):
    # CC0 Quaternius articulated human, imported as editable 3D geometry.
    old=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets'/'human.glb'))
    added=set(bpy.context.scene.objects)-old
    rig=next(o for o in added if o.type=='ARMATURE')
    mesh=next(o for o in added if o.type=='MESH' and o.parent==rig)
    for o in added:
        if o.type=='MESH' and o.parent is None: bpy.data.objects.remove(o,do_unlink=True)
    rig.location=(x,y,z);rig.scale=(scale,scale,scale)
    rig.rotation_euler.z=math.pi
    rig.animation_data_clear();rig.animation_data_create()
    # Choose natural motion rather than independent spheres/rods.
    action=bpy.data.actions.get('Walk_Loop_Rig' if x>40 and x<70 else 'Idle_Loop_Rig')
    rig.animation_data.action=action
    for fc in action.fcurves:
        if not any(m.type=='CYCLES' for m in fc.modifiers):fc.modifiers.new('CYCLES')
    # Material regions follow height in object coordinates, without a painted background.
    mat=bpy.data.materials.new('Outfit');mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links
    bs=nodes.get('Principled BSDF');geo=nodes.new('ShaderNodeTexCoord');sep=nodes.new('ShaderNodeSeparateXYZ');links.new(geo.outputs['Generated'],sep.inputs[0])
    split1=nodes.new('ShaderNodeMath');split1.operation='GREATER_THAN';split1.inputs[1].default_value=.47;links.new(sep.outputs['Z'],split1.inputs[0])
    split2=nodes.new('ShaderNodeMath');split2.operation='GREATER_THAN';split2.inputs[1].default_value=.83;links.new(sep.outputs['Z'],split2.inputs[0])
    mix1=nodes.new('ShaderNodeMixRGB');mix1.blend_type='MIX';mix1.inputs[1].default_value=(*M[shorts].diffuse_color[:3],1);mix1.inputs[2].default_value=(*M[shirt].diffuse_color[:3],1);links.new(split1.outputs[0],mix1.inputs[0])
    mix2=nodes.new('ShaderNodeMixRGB');mix2.blend_type='MIX';mix2.inputs[2].default_value=(*M['skin'].diffuse_color[:3],1);links.new(mix1.outputs[0],mix2.inputs[1]);links.new(split2.outputs[0],mix2.inputs[0]);links.new(mix2.outputs[0],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.75
    mesh.data.materials.clear();mesh.data.materials.append(mat)
    return {'rig':rig}

def animate_person(p,t,mode='idle'):
    # Animation driven by imported CC0 rig and its looping baked action.
    return

# Hotel room: depth layers are real 3D geometry, not background images.
world_base(0,'navy','wood');city_window(0)
box('bed frame',(-1.7,.4,.33),(2.3,2,.45),'ink',.08);box('mattress',(-1.7,.4,.61),(2.2,1.9,.27),'cream',.1);box('pillow',(-1.7,1,.81),(1.3,.5,.13),'white',.08);box('blanket',(-1.7,-.15,.81),(2.0,.8,.12),'blue',.05)
box('nightstand',(1.85,1.0,.45),(.7,.7,.9),'wood',.04);rod('lampstem',(1.85,1, .9),(1.85,1,1.7),.035,'gold');ball('lamp',(1.85,1,1.7),(.26,.26,.14),'lamp')
hero0=person(.75,.2,shirt='white',shorts='ink')
# Breakfast table.
world_base(22,'cream','wood');city_window(22)
box('table',(22,.25,.75),(3,1.5,.15),'wood',.08)
for x in (20.75,23.25):
 for y in (-.25,.75):box('table leg',(x,y,.38),(.12,.12,.76),'wood')
for x,y in [(21.5,.05),(22.2,.1),(22.6,.5)]:
 ball('plate',(x,y,.84),(.38,.28,.025),'white');ball('breakfast',(x,y,.89),(.14,.12,.05),'gold')
rod('glass',(21.7,.7,.82),(21.7,.7,1.15),.11,'glass');hero1=person(22.3,1.45,shirt='white',shorts='ink')
# Training pitch, football and goal.
box('pitch',(44,0,-.12),(14,15,.24),'green')
for i in range(8):box('pitch stripe',(38+i*1.8,0,.008),(.9,15,.012),'grass2')
for x in (40,48):box('touchline',(x,0,.02),(.04,15,.02),'white')
for x in (42,46):rod('goal post',(x,3,0),(x,3,2.3),.06,'white')
rod('crossbar',(42,3,2.3),(46,3,2.3),.06,'white');area((42,-2,7),950,6,(1,.85,.67));area((48,2,7),600,5,(.57,.74,1))
hero2=person(43.8,.1,shirt='red',shorts='ink');football=ball('football',(44.4,-.2,.18),(.18,.18,.18),'white',16,10)
for i in range(5):box('training cone',(41.3+i*1.3,1.0,.09),(.16,.16,.18),'gold',.03)
# Press corridor / fans.
world_base(66,'ink','stone');box('gold feature',(66,2.8,2.8),(4,.12,3.8),'gold');box('dark feature',(66,2.69,2.8),(3.75,.08,3.55),'navy')
for i in range(7):box('light strips',(63+i,2.55,4.6),(.5,.06,.06),'lamp')
hero3=person(66,.3,shirt='red',shorts='ink');fans=[person(64.8,-.1,shirt='blue',shorts='ink',scale=.74),person(67.2,.3,shirt='pink',shorts='ink',scale=.74)]
for x in (64.4,67.65):box('camera phone',(x,-.48,1.65),(.22,.08,.4),'ink',.04);box('phone screen',(x,-.53,1.65),(.16,.02,.28),'screen')
# Quiet lounge.
world_base(88,'blue','wood');city_window(88)
box('sofa',(88,.9,.55),(3,1.05,.5),'cream',.09);box('sofa back',(88,1.35,1.0),(3,.25,.9),'cream',.08)
box('coffee table',(88,-.4,.45),(1.8,.8,.12),'wood',.04);ball('vase',(88,-.35,.67),(.18,.18,.28),'gold')
hero4=person(87.35,1.0,shirt='white',shorts='blue',scale=.9);family=person(88.75,1.0,shirt='pink',shorts='blue',scale=.75)
# Optional experiment: action clips replace one repeating animation per character.
# These motions are generic; they are not a finished performance or football kick.
if args.experimental_sequences or args.experimental_kick:
 from action_timeline import Clip, apply
 apply(hero0['rig'], [Clip('Idle_Loop_Rig',0,4.25,.2,True), Clip('Interact_Rig',4,8,.2)])
 apply(hero1['rig'], [Clip('Idle_Loop_Rig',8,10.25,.2,True), Clip('PickUp_Table_Rig',10,12,.2), Clip('Idle_Loop_Rig',11.75,16,.2,True)])
 apply(hero2['rig'], [Clip('Idle_Loop_Rig',16,24,.2,True)] if args.experimental_kick else [Clip('Jog_Fwd_Loop_Rig',16,19.25,.2,True), Clip('Interact_Rig',19,21,.2), Clip('Jog_Fwd_Loop_Rig',20.75,24,.2,True)])
 apply(hero3['rig'], [Clip('Walk_Loop_Rig',24,31.25,.2,True), Clip('Interact_Rig',31,33,.2), Clip('Walk_Formal_Loop_Rig',32.75,42,.2,True)])
 apply(hero4['rig'], [Clip('Idle_Loop_Rig',42,47.25,.2,True), Clip('Interact_Rig',47,49,.2), Clip('Idle_Loop_Rig',48.75,60,.2,True)])

# Ball is baked from the animated toe proxy, not an independent sine wave.
# This is a rough blocking test and has not been visually approved.
if args.experimental_kick:
 from football_physics import Ball
 from kick_experiment import bake as bake_kick, install_kick
 football.scale=(.11,.11,.11)
 install_kick(hero2['rig'])
 kick_states,kick_impacts=bake_kick(scene,hero2['rig'],Ball((43.42,.39,.11)))
 print('EXPERIMENTAL_KICK_IMPACTS',kick_impacts,flush=True)
 if not kick_impacts:
  raise RuntimeError('Kick blocking failed: no foot-ball contact occurred')

# Rendering camera.
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.lens=42;camera.data.sensor_width=36

def update(t):
 if t<8:i=0;x=0;focus=(.2,0,1.35);pos=(.35+0.16*math.sin(t*.35),-7.4+0.13*t,2.55)
 elif t<16:i=1;x=22;focus=(22,.35,1.0);pos=(22.25+.2*math.sin(t*.4),-6.3,2.5)
 elif t<24:
  i=2;x=44
  if args.experimental_kick and 18.3<=t<20.4:
   # Cut to an action angle; track toward the field with the ball after contact.
   idx=min(max(round((t-16)*FPS),0),len(kick_states)-1)
   target=kick_states[idx].position
   follow=min(1,max(0,(t-19.0)*1.8))
   focus=(43.5+(target[0]-43.5)*follow,target[1]*follow,.48)
   pos=(41.8,-3.5,1.35)
  else:focus=(44,0,1.05);pos=(44+.25*math.sin(t*.55),-7.1,2.35)
 elif t<42:i=3;x=66;focus=(66,.2,1.25);pos=(66+.35*math.sin(t*.33),-7.0+.1*math.sin(t*.5),2.4)
 else:i=4;x=88;focus=(88,.55,1.2);pos=(88+.25*math.sin(t*.3),-7.0,2.35)
 camera.location=pos;camera.rotation_euler=(Vector(focus)-camera.location).to_track_quat('-Z','Y').to_euler()
 animate_person(hero0,t,'idle');animate_person(hero1,t,'idle');animate_person(hero2,t,'walk');animate_person(hero3,t,'walk' if t<32 else 'wave');animate_person(hero4,t,'idle');animate_person(family,t,'wave')
 for j,p in enumerate(fans):animate_person(p,t+j*.7,'wave')
 if args.experimental_kick and 16<=t<24:
  state=kick_states[min(round((t-16)*FPS),len(kick_states)-1)]
  football.location=state.position
  football.rotation_euler=(state.roll,0,0)
 else:
  football.location.x=44.45+.24*math.sin((t-16)*2.0);football.rotation_euler.y=t*2
 return i

def overlay(frame,t):
 im=Image.open(frame).convert('RGB');d=ImageDraw.Draw(im,'RGBA');scale=W/360
 def font(sz):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',int(sz*scale))
 d.rounded_rectangle((int(16*scale),int(20*scale),int(153*scale),int(43*scale)),radius=int(6*scale),fill=(8,14,25,195));d.text((int(24*scale),int(25*scale)),'A DAY IN HIS LIFE',font=font(10),fill=(250,227,182,255))
 d.text((int(W*.95),int(26*scale)),'FICTIONAL',font=font(9),fill=(240,235,222,230),anchor='ra')
 d.rounded_rectangle((int(15*scale),int(H-112*scale),int(W-15*scale),int(H-44*scale)),radius=int(10*scale),fill=(4,10,19,205))
 for start,end,a,b in WORDS:
  if start<=t<end:
   d.text((W//2,int(H-99*scale)),a,font=font(14 if len(a)<24 else 12),fill=(250,248,236,255),anchor='ma',stroke_width=1,stroke_fill=(0,0,0,160));d.text((W//2,int(H-77*scale)),b,font=font(14 if len(b)<24 else 12),fill=(247,194,99,255),anchor='ma',stroke_width=1,stroke_fill=(0,0,0,160));break
 d.rounded_rectangle((int(18*scale),int(H-24*scale),int(W-18*scale),int(H-21*scale)),radius=2,fill=(255,255,255,80));d.rectangle((int(18*scale),int(H-24*scale),int(18*scale+(W-36*scale)*t/60),int(H-21*scale)),fill=(243,186,85,255))
 return im

def bed(path):
 sr=48000;t=np.arange(sr*DURATION,dtype=np.float32)/sr;a=np.zeros_like(t);notes=[110,138.59,164.81,207.65,123.47,146.83,185,220]
 for i in range(120):
  pos=int(i*.5*sr);n=min(int(.9*sr),len(a)-pos)
  if n<=0:break
  u=np.arange(n,dtype=np.float32)/sr;env=np.minimum(u/.025,1)*np.exp(-u*3.8);f=notes[(i//8*4+i%4)%len(notes)];a[pos:pos+n]+=.022*env*(np.sin(2*np.pi*f*u)+.28*np.sin(2*np.pi*f*2*u))
 for at in CUTS[:-1]:
  pos=int(at*sr);n=min(int(.45*sr),len(a)-pos);u=np.arange(n,dtype=np.float32)/sr;a[pos:pos+n]+=.028*np.sin(2*np.pi*(90*u-30*u*u))*np.exp(-9*u)
 a*=np.minimum(1,np.minimum(t,(DURATION-t))).clip(0,1)
 with wave.open(str(path),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes((a*32767).astype('<i2').tobytes())

def render(t,path):
 scene.frame_set(round(t*FPS));update(t);scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
if args.stills:
 with tempfile.TemporaryDirectory() as tmp:
  for t in [2,10,19,27,36,45,55]:
   p=Path(tmp)/'frame.png';render(t,p);overlay(p,t).save(ROOT/f'preview-{t}.jpg',quality=92)
else:
 out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);ff=imageio_ffmpeg.get_ffmpeg_exe()
 with tempfile.TemporaryDirectory() as td:
  tmp=Path(td);p=tmp/'frame.png';picture=tmp/'picture.mp4';score=tmp/'score.wav';bed(score)
  cmd=[ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(picture)]
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  for n in range(FPS*args.start,FPS*args.end):
   t=n/FPS;render(t,p);proc.stdin.write(overlay(p,t).tobytes())
   if n%120==0:print(f'RENDER_PROGRESS {n}/{FPS*args.end}',flush=True)
  proc.stdin.close()
  if proc.wait():raise RuntimeError('encode failed')
  if args.silent:
   import shutil;shutil.copyfile(picture,out);print('OUTPUT',out,flush=True);raise SystemExit(0)
  inputs=[]
  for k in range(1,8):inputs+=['-i',str(VOICE/f'{k:02}.wav')]
  offsets=[.35,8,16.2,24.15,33.6,41.85,51];filters=[f'[{i}:a]aresample=48000,adelay={int(at*1000)}:all=1[v{i}]' for i,at in enumerate(offsets,1)]
  filters+=['[8:a]volume=0.55[m]',''.join(f'[v{i}]' for i in range(1,8))+'[m]amix=inputs=8:duration=longest:normalize=0,highpass=f=35,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[a]']
  subprocess.run([ff,'-y','-v','error','-i',str(picture),*inputs,'-i',str(score),'-filter_complex',';'.join(filters),'-map','0:v','-map','[a]','-t','60','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)
 print('OUTPUT',out,flush=True)
