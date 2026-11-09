"""Fictional third-person celebrity day, modeled and rendered as real 3D scenes.
Character/motion: Rocketbox MIT via avatar-studio. Furniture: Poly Haven CC0.
"""
from pathlib import Path
import argparse,math,sys,subprocess,tempfile
import bpy
from mathutils import Vector,Matrix,Quaternion
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));from motion import walk,blink
FPS=18; W,H=480,270
p=argparse.ArgumentParser();p.add_argument('--assets',default='/home/user/celebrity-lookdev-assets');p.add_argument('--output',default='deliverables/celebrity-story-third-person-3d-v4.mp4');p.add_argument('--start',type=int,default=0);p.add_argument('--end',type=int,default=60);p.add_argument('--samples',type=int,default=1);p.add_argument('--width',type=int,default=480);p.add_argument('--fps',type=int,default=18);p.add_argument('--audit',action='store_true');p.add_argument('--probe',action='store_true');p.add_argument('--stills',action='store_true');args=p.parse_args();A=Path(args.assets);W=args.width;H=round(W*9/16);H+=H%2;FPS=args.fps
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.render.use_persistent_data=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.world=bpy.data.worlds.new('World');s.world.color=(.13,.11,.14)
def material(name,col,rough=.6,metal=0,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 if emit:bs.inputs['Emission Color'].default_value=(*col,1);bs.inputs['Emission Strength'].default_value=emit
 return m
cs={'floor':(.13,.085,.07),'wall':(.24,.18,.22),'dark':(.022,.022,.03),'metal':(.48,.30,.13),'sky':(.82,.45,.28),'silhouette':(.07,.065,.09),'blue':(.045,.08,.12),'red':(.33,.025,.045),'cream':(.65,.61,.55),'plant':(.055,.2,.09),'white':(.8,.78,.71),'screen':(.44,.67,.8),'studio':(.09,.11,.15),'road':(.055,.055,.065),'black':(.01,.012,.016),'skin':(.4,.23,.16)}
M={k:material(k,c,metal=.65 if k=='metal' else 0,rough=.3 if k in ('metal','screen') else .65,emit=.5 if k in ('sky','screen') else 0) for k,c in cs.items()}
# Fine procedural relief: real shaded surfaces, not photographic background plates.
for name,scale,strength in (('floor',110,.12),('wall',160,.10),('road',140,.10)):
 mat=M[name];nodes=mat.node_tree.nodes;links=mat.node_tree.links;noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=2.5;bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=.035;links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],nodes['Principled BSDF'].inputs['Normal'])
# Physical sky gradient with a separate sun disk.
sky=M['sky'];nodes=sky.node_tree.nodes;links=sky.node_tree.links;tex=nodes.new('ShaderNodeTexCoord');xyz=nodes.new('ShaderNodeSeparateXYZ');ramp=nodes.new('ShaderNodeValToRGB');ramp.name='Horizon gradient';ramp.color_ramp.elements[0].color=(.85,.43,.28,1);ramp.color_ramp.elements[1].color=(.32,.25,.38,1);links.new(tex.outputs['Generated'],xyz.inputs[0]);links.new(xyz.outputs['Z'],ramp.inputs[0]);links.new(ramp.outputs['Color'],nodes['Principled BSDF'].inputs['Base Color']);links.new(ramp.outputs['Color'],nodes['Principled BSDF'].inputs['Emission Color']);M['sun']=material('sun',(1,.71,.43),emit=1.1)

def box(name,loc,dim,key,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(M[key])
 if bevel:mod=o.modifiers.new('Soft edges','BEVEL');mod.width=bevel;mod.segments=2;o.modifiers.new('Normal','WEIGHTED_NORMAL')
 return o
def sph(name,loc,scale,key):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(M[key]);bpy.ops.object.shade_smooth();return o
def rod(name,a,b,r,key):
 a,b=Vector(a),Vector(b);v=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=v.length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.data.materials.append(M[key]);return o
def light(loc,target,power,size,col):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=col;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def model(name,loc,rotation=0,scale=1):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(A/name));added=set(bpy.context.scene.objects)-before
 for o in added:
  if o.parent is None:o.location+=Vector(loc);o.scale*=scale;o.rotation_euler.z+=rotation
 return added
def base(x,wall='wall',floor='floor'):
 box('floor',(x,0,-.12),(14,13,.24),floor);box('backdrop',(x,4,2.7),(14,.15,5.4),wall)
 for dx in range(-6,7,2):box('panel seam',(x+dx,3.9,2.7),(.025,.035,5.3),'dark')
 light((x-3,-4,4.5),(x,0,1.2),420,4,(1,.71,.5));light((x+3,2.7,4.5),(x,0,1.2),550,3,(1,.5,.30));light((x+4,-3,3),(x,0,1.2),160,3,(.46,.60,1))
def skyline(x):
 box('sunset glazing',(x,3.92,2.8),(8,.04,3.6),'sky')
 sph('sun disk',(x+2.2,3.80,2.7),(.44,.025,.44),'sun')
 # Irregular real 3D structures at differing depths instead of equal bars.
 for j in range(18):
  xx=x-3.9+j*.45;h=.55+(j*37%24)*.07;width=.28+(j%4)*.045;depth=3.70-(j%3)*.045
  box('building',(xx,depth,1+h/2),(width,.12,h),'silhouette')
  if j%4==0:box('rooftop',(xx,depth,1+h+.09),(width*.4,.10,.18),'silhouette')
  for k in range(int(h/.25)):
   for col in (-1,1):
    if (j*7+k*3+col)%4:box('building window',(xx+col*width*.22,depth-.075,1.10+k*.22),(.024,.025,.045),'screen')
 for xx in (-4,-2,0,2,4):box('window frame',(x+xx,3.48,2.8),(.09,.14,3.7),'dark')
 box('window ledge',(x,3.44,.95),(8,.35,.1),'metal')

def greenery(x,y):
 box('planter',(x,y,.25),(.5,.5,.5),'dark',.05)
 for i in range(8):
  ang=i*2.4;end=(x+.3*math.sin(ang),y+.3*math.cos(ang),1.25+(i%3)*.18);rod('stem',(x,y,.35),end,.014,'plant');sph('leaf',end,(.17,.08,.24),'plant')
# Living room: actual Poly Haven geometry and sculptural details.
base(0);skyline(0);model('sofa.glb',(-1.6,1.6,0));model('armchair.glb',(2.4,1.25,0),rotation=-.4);home_table=model('coffee-table.glb',(-1.5,-1.25,0));model('bookcase.glb',(-4.2,2.8,0));model('nightstand.glb',(3.7,2.6,0));greenery(3.8,2)
box('rug',(0,.1,.008),(4.8,2.8,.015),'cream')
for i in range(16):box('rug weave',(-2.25+i*.3,.1,.018),(.015,2.6,.008),'wall')
for j in range(16):box('book',(-4.45+(j%4)*.14,2.79,.28+(j//4)*.34),(.10,.18,.23),'red' if j%3==0 else 'blue',.01)

# Artwork, shelf decor, a table tray and varied area rug details.
for j in range(3):
 box('frame',(-5.4,2.2-j*.9,2.8),(.08,.73,.85),'metal',.02);box('art',(-5.34,2.2-j*.9,2.8),(.03,.62,.74),'blue')
box('coffee table tray',(-1.5,-1.25,.47),(.56,.30,.035),'metal',.02);sph('decorative bowl',(-1.5,-1.25,.53),(.14,.14,.055),'cream')
for i in range(7):
 sph('shelf ornament',(-4.12,2.62,.38+i*.20),(.07,.07,.08),'metal' if i%2 else 'cream')
rod('lamp',(3.7,2.6,.75),(3.7,2.6,1.45),.03,'metal');sph('lamp shade',(3.7,2.6,1.55),(.28,.28,.18),'sky')
# Reception corridor and entrance with flooring, panels and plants.
base(20,'studio','road');skyline(20);greenery(17,2.6);greenery(23,2.6)
for j in range(7):box('ceiling light',(17+j,1,4.8),(.48,.20,.06),'screen')
for i in range(-4,5):box('floor seam',(20+i*.8,0,.006),(.012,10,.015),'metal')
box('double door frame',(20,3.65,2),(3.2,.14,3.9),'metal');box('doors',(20,3.52,1.95),(3,.09,3.7),'blue');box('door dividing line',(20,3.45,1.95),(.04,.08,3.7),'metal')
# Red carpet / press event.
base(40,'studio','road');box('carpet',(40,0,.015),(3.6,10,.03),'red')
box('step and repeat panel',(40,3.86,2.5),(8,.06,3.8),'blue')
for j in range(8):
 for k in range(3):box('backdrop pattern',(36.7+j*.95,3.80,1.15+k*.9),(.32,.01,.06),'metal')
for side in (-1,1):
 xx=40+side*2.35
 for yy in (-3,-1,1,3):rod('barrier post',(xx,yy,0),(xx,yy,1.05),.035,'metal');sph('post knob',(xx,yy,1.08),(.075,.075,.075),'metal')
 for z in (.72,.98):rod('barrier rail',(xx,-3,z),(xx,3,z),.025,'metal')

# Architectural layers provide more spatial depth without photographic plates.
for xx in (36.1,43.9):
 box('event column',(xx,3.55,2.15),(.30,.32,4.3),'dark',.03)
 for zz in (1.0,2.0,3.0):box('column inlay',(xx,3.35,zz),(.22,.03,.04),'metal')
for xx in (36.65,43.35):
 rod('event uplight stand',(xx,3.25,.1),(xx,3.25,.55),.06,'dark')
 light((xx,3.0,.5),(xx,3.75,3),75,1.1,(.95,.35,.15))
# A physical 3D event title grounds the red carpet in a fictional venue.
bpy.ops.object.text_add(location=(40,3.72,3.22),rotation=(math.pi/2,0,0));sign=bpy.context.object;sign.name='event title';sign.data.body='THE SPOTLIGHT';sign.data.align_x='CENTER';sign.data.size=.28;sign.data.extrude=.002;sign.data.materials.append(M['metal'])
# Framed panels, wall sconces and foreground architectural detail.
for xx in (-3.5,3.5):
 box('home wall sconce',(xx,3.72,3.7),(.35,.12,.08),'metal',.02)
 light((xx,3.25,3.5),(xx,0,1.0),65,1.0,(1,.58,.3))
for yy in (-3,0,3):
 box('corridor wall rib',(15.35,yy,2.4),(.13,.14,4.8),'metal')
 box('corridor ceiling strip',(20,yy,4.7),(7,.07,.035),'screen')
# Interview studio.
base(60,'studio','floor');box('acoustic backdrop',(60,3.8,2.7),(7,.08,4),'blue')
for j in range(12):box('acoustic slat',(57+j*.55,3.72,2.7),(.04,.08,4),'metal')
model('armchair.glb',(59,1.5,0),rotation=.12);model('armchair.glb',(61.7,1.5,0),rotation=-.18);studio_table=model('coffee-table.glb',(58.45,-.6,0));greenery(56.3,2.8);greenery(63.7,2.8)
for x in (56.8,63.2):
 rod('light stand',(x,-.4,0),(x,-.4,2.9),.03,'dark');box('softbox',(x,-.35,2.9),(.95,.16,.65),'screen',.03)
box('studio camera',(57.3,-2,1.7),(.6,.55,.4),'dark',.05);sph('lens',(57.3,-1.65,1.7),(.2,.11,.2),'blue')
for x,y in ((57,-2.3),(57.6,-2.3),(57.3,-1.6)):rod('camera tripod',(57.3,-2,1.5),(x,y,0),.025,'dark')
# Characters from original rigged and textured assets, not celebrity likenesses.
def person(file):
 objs=model(file,(0,0,0));rig=next(o for o in objs if o.type=='ARMATURE')
 for o in objs:
  if o.type=='MESH' and o.name.split('.')[0] in ('Outfit_formal','Skin_formal','Top_shirt','Skin_shirt','Top_tee','Skin_tee','Trousers','Shoes'):o.hide_render=True
 rig.animation_data_create();rig.rotation_euler.z=math.pi
 return rig,objs
hero,hero_objs=person('ryan.glb');actions={a.name:a for a in bpy.data.actions};guest,guest_objs=person('emma.glb')
# Two skinned background attendees replace the previous block-figure photographers.
attendee_a,attendee_a_objs=person('marcus.glb');attendee_b,attendee_b_objs=person('aisha.glb')
attendee_phone_a=box('audience phone A',(0,0,0),(.06,.012,.12),'black',.005)
attendee_phone_b=box('audience phone B',(0,0,0),(.06,.012,.12),'black',.005)
flash_a=sph('flash A',(0,0,0),(.035,.035,.035),'sun');flash_b=sph('flash B',(0,0,0),(.035,.035,.035),'sun')

def outfit(objs, formal):
 selected={'Outfit_formal','Skin_formal'} if formal else {'Outfit_original','Skin_original'}
 clothing={'Outfit_formal','Skin_formal','Outfit_original','Skin_original','Top_shirt','Skin_shirt','Top_tee','Skin_tee','Trousers','Shoes'}
 for obj in objs:
  if obj.type=='MESH':
   name=obj.name.split('.')[0]
   if name in clothing:obj.hide_render=name not in selected

def expression(objs,t,smile,brow=0):
 # Shape keys are shared across facial pieces in each imported avatar; values
 # are set after animation evaluation, not via a simulated emotion detector.
 b=blink(t)
 for obj in objs:
  if obj.type!='MESH' or not obj.data.shape_keys:continue
  keys=obj.data.shape_keys.key_blocks
  for name,value in (('eyeBlinkLeft',b),('eyeBlinkRight',b),('mouthSmileLeft',smile),('mouthSmileRight',smile),('browInnerUp',brow)):
   if name in keys:keys[name].value=value

# Props are attached to the animated right hand with a baked local transform;
# this is an approximate grip, not collision solving.
phone=box('handheld phone',(0,0,0),(.068,.012,.137),'black',.006);phone_screen=box('phone screen',(0,0,0),(.054,.002,.119),'blue',.001)
# Hollow cup with visible liquid and handle; it remains an authored grip, not physics.
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.043,depth=.077,location=(0,0,0));cup=bpy.context.object;cup.name='coffee mug';cup.data.materials.append(M['white'])
bev=cup.modifiers.new('cup edge','BEVEL');bev.width=.006;bev.segments=3
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.035,depth=.002,location=(0,0,0));coffee=bpy.context.object;coffee.name='coffee surface';coffee.data.materials.append(M['floor'])
bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=8,location=(0,0,0),major_radius=.024,minor_radius=.006);handle=bpy.context.object;handle.name='mug handle';handle.data.materials.append(M['white'])

# Camera: all shots remain external, third-person.
bpy.ops.object.camera_add();camera=bpy.context.object;s.camera=camera;camera.data.sensor_width=36
cuts=(0,3.5,7.2,10.6,13.5,16.8,19.7,23.5,27.6,31.8,36.4,40.2,44.3,48.2,52.2,56.2,60)
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def update(t):
 # Evaluate a shot-local portion of each real motion clip, then position roots.
 if t<7.2:x=0;hero_y=.25;act='Phone_Rig';af=(t/7.2)*150
 elif t<13.5:x=0;hero_y=.25;act='Drink_Rig';af=((t-7.2)/6.3)*235
 elif t<19.7:
  x=20;af,hero_y=walk(t-13.5);act='Walk_Rig'
 elif t<27.6:
  x=40;af,hero_y=walk(t-19.7);act='Walk_Rig' if t<23.5 else 'Wave_Rig'
  if t>=23.5:hero_y=.45;af=((t-23.5)/4.1)*67
 elif t<36.4:x=60;hero_y=.2;act='Talk_Rig';af=((t-27.6)/8.8)*200
 elif t<44.3:x=40;hero_y=.25;act='Wave_Rig';af=((t-36.4)/7.9)*67
 elif t<52.2:
  x=40;af,hero_y=walk(t-44.3);act='Walk_Rig'
 else:x=0;hero_y=.25;act='Think_Rig';af=((t-52.2)/7.8)*250
 hero.animation_data.action=actions[act];guest.animation_data.action=actions['Talk_Rig'];attendee_a.animation_data.action=actions['Wave_Rig'];attendee_b.animation_data.action=actions['Wave_Rig'];s.frame_set(math.floor(af),subframe=af%1);hero.location=(x,hero_y,0);hero.rotation_euler.z=math.pi+(.35 if 36.4<=t<44.3 else 0)
 # Interviewer/fan stays in a separate location otherwise, so never enters other shots.
 guest.location=(61.35,.65,0) if 27.6<=t<36.4 else (100,0,0)
 # Imported roots are quaternion-driven: setting Euler alone had no effect.
 # Use quaternion rotations explicitly for a face-to-face conversational eyeline.
 hero.rotation_mode='QUATERNION';guest.rotation_mode='QUATERNION'
 hero.rotation_quaternion=Quaternion((0,0,1),.85 if 27.6<=t<36.4 else (.55 if 36.4<=t<44.3 else 0))
 guest.rotation_quaternion=Quaternion((0,0,1),-.85 if 27.6<=t<36.4 else (-.6 if 36.4<=t<44.3 else 0))
 public=19.7<=t<27.6 or 36.4<=t<52.2
 attendee_a.location=((42.75,.5,0) if 36.4<=t<44.3 else (36.85,.0,0)) if public else (100,0,0);attendee_b.location=(43.15,2.5,0) if public else (100,2,0)
 attendee_a.rotation_mode='QUATERNION';attendee_a.rotation_quaternion=Quaternion((0,0,1),-.6 if 36.4<=t<44.3 else .55)
 attendee_b.rotation_mode='QUATERNION';attendee_b.rotation_quaternion=Quaternion((0,0,1),-.55)
 outfit(hero_objs,19.7<=t<52.2);outfit(attendee_a_objs,False);outfit(attendee_b_objs,False)
 smile=(.38 if 23.5<=t<27.6 or 36.4<=t<52.2 else (.12 if 27.6<=t<36.4 else .03))
 expression(hero_objs,t,smile,.12 if 52.2<=t<60 else .02);expression(guest_objs,t+.7,.28 if 27.6<=t<44.3 else 0)
 # Cooler twilight for the final return; preserve the warm earlier horizon.
 gradient=M['sky'].node_tree.nodes['Horizon gradient'].color_ramp
 gradient.elements[0].color=(.23,.22,.38,1) if t>=52.2 else (.85,.43,.28,1)
 gradient.elements[1].color=(.075,.10,.22,1) if t>=52.2 else (.32,.25,.38,1)
 for ob in bpy.data.objects:
  if ob.name.startswith('sun disk'):ob.hide_render=t>=52.2
 bpy.context.view_layer.update()
 flash_times=(20.3,21.2,22.9,24.6,26.2,38.8,40.7,45.1,46.4,48.8,50.2)
 for j,(actor,prop,flare) in enumerate(((attendee_a,attendee_phone_a,flash_a),(attendee_b,attendee_phone_b,flash_b))):
  wrist=(actor.matrix_world @ actor.pose.bones['mixamorig:RightHand'].matrix).translation
  pos=wrist+Vector((.012,-.03,.04));prop.matrix_world=Matrix.Translation(pos);prop.hide_render=not public
  flare.location=pos+Vector((0,-.012,.045));flare.hide_render=not (public and any(abs(t-at)<.065 and k%2==j for k,at in enumerate(flash_times)))
 # Phone and cup anchored to the right wrist; grip position approximates the source motion.
 hand=hero.matrix_world @ hero.pose.bones['mixamorig:RightHand'].matrix
 phone.hide_render=not (0<=t<7.2);phone_screen.hide_render=phone.hide_render
 for obj in (cup,coffee,handle):obj.hide_render=not (7.2<=t<13.5)
 # Upright device follows the wrist in world space; moved to the outside of the ear.
 hp=hand.translation;phonepos=hp+Vector((.012,-.035,.04));phone.matrix_world=Matrix.Translation(phonepos);phone_screen.matrix_world=Matrix.Translation(phonepos+Vector((0,-.007,0)))
 # Keep mug in the palm and gently tip it during the drinking beat.
 drink=ease((t-9.5)/1.1)*(1-ease((t-11.6)/1.0));cup_pos=hp+Vector((.045,-.06,.05));cm=Matrix.Translation(cup_pos) @ Matrix.Rotation(-.45*drink,4,'X')
 cup.matrix_world=cm;coffee.matrix_world=cm @ Matrix.Translation((0,0,.036));handle.matrix_world=cm @ Matrix.Translation((-.042,0,.0)) @ Matrix.Rotation(math.pi/2,4,'X')
 # Alternating wide, medium and close frames. Look at faces rather than a first-person camera.
 if t<3.5:pos=(1.1,-4.0,1.85);focus=(0,.25,1.4);lens=55
 elif t<7.2:pos=(-1.35,-3.7,1.9);focus=(0,.25,1.45);lens=55
 elif t<10.6:pos=(-2.8,-5.3,2.3);focus=(0,.2,1.25);lens=45
 elif t<13.5:pos=(-1.35,-3.6,2);focus=(0,.2,1.42);lens=55
 elif t<16.8:pos=(17.5,-5.8,2.5);focus=(20,.4,1.25);lens=39
 elif t<19.7:pos=(21.2,-4.4,2);focus=(20,.1,1.3);lens=50
 elif t<23.5:pos=(37.5,-6.2,2.3);focus=(40,.35,1.25);lens=40
 elif t<27.6:pos=(41,-4.1,2.0);focus=(40,.35,1.4);lens=55
 elif t<31.8:pos=(57.7,-5.3,2.2);focus=(60.5,.5,1.25);lens=40
 elif t<36.4:pos=(61.2,-4,2);focus=(60,.3,1.4);lens=52
 elif t<40.2:pos=(38.1,-6.1,2.3);focus=(41.2,.4,1.3);lens=36
 elif t<44.3:pos=(40.15,-3.65,1.85);focus=(42.65,.5,1.42);lens=57
 elif t<48.2:pos=(37.5,-6,2.2);focus=(40,hero_y,1.3);lens=42
 elif t<52.2:pos=(41.2,-4,2);focus=(40,hero_y,1.4);lens=55
 elif t<56.2:pos=(-2.7,-5.5,2.4);focus=(0,.25,1.2);lens=43
 else:pos=(1.3,-4.2,2.0);focus=(0,.25,1.4);lens=52
 start=max(c for c in cuts if c<=t);end=min(c for c in cuts if c>t);u=ease((t-start)/(end-start));camera.location=(pos[0]+(.16 if t<19.7 else -.12)*u,pos[1]+(.22 if t<27.6 else .12)*u,pos[2]+.025*u);camera.rotation_euler=(Vector(focus)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=lens
 camera.data.dof.use_dof=True;camera.data.dof.focus_distance=(Vector(focus)-camera.location).length;camera.data.dof.aperture_fstop=8.0
def render(t,path):
 update(t);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
def overlay(path,t):
 im=Image.open(path).convert('RGB');d=ImageDraw.Draw(im,'RGBA');b=round(H*.052);d.rectangle((0,0,W,b),fill=(0,0,0,255));d.rectangle((0,H-b,W,H),fill=(0,0,0,255));font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',max(8,round(W*.016)));d.text((int(W*.025),b+4),'A DAY IN THE SPOTLIGHT',font=font,fill=(238,225,209,225));d.text((int(W*.975),b+4),'FICTIONAL',font=font,fill=(238,225,209,205),anchor='ra')
 if t<.35:im=Image.blend(Image.new('RGB',(W,H)),im,ease(t/.35))
 if t>59.5:im=Image.blend(im,Image.new('RGB',(W,H)),ease((t-59.5)/.5))
 return im
if args.audit:
 import json
 def bounds(objects):
  coords=[o.matrix_world @ Vector(corner) for o in objects if o.type=='MESH' for corner in o.bound_box]
  return (min(v.x for v in coords),max(v.x for v in coords),min(v.y for v in coords),max(v.y for v in coords))
 bpy.context.view_layer.update();table_bounds={'home':bounds(home_table),'studio':bounds(studio_table)};violations=[];nearest=100.0
 for i in range(240):
  t=i/4;update(t)
  active='home' if t<13.5 or t>=52.2 else ('studio' if 27.6<=t<36.4 else None)
  if not active:continue
  xmin,xmax,ymin,ymax=table_bounds[active]
  for name in ('mixamorig:LeftFoot','mixamorig:RightFoot','mixamorig:LeftToeBase','mixamorig:RightToeBase'):
   if name not in hero.pose.bones:continue
   point=(hero.matrix_world @ hero.pose.bones[name].matrix).translation
   dx=max(xmin-point.x,0,point.x-xmax);dy=max(ymin-point.y,0,point.y-ymax);dist=math.hypot(dx,dy);nearest=min(nearest,dist)
   if dist<.10:violations.append({'time':t,'bone':name,'separation':round(dist,4),'table':active})
 report={'sample_interval_seconds':.25,'table_bounds_xy':table_bounds,'min_foot_landmark_to_table_aabb_m':round(nearest,4),'foot_proxy_radius_m':.10,'violations':violations,'limitation':'Bounding box and foot landmarks only: not full mesh collision verification.'}
 print('AUDIT_JSON',json.dumps(report),flush=True)
 if violations:raise SystemExit('foot landmark near table bounding box')
 raise SystemExit(0)
if args.probe:
 for t in (0,1,2,3,4,5,6,7,8,9,10,11,12,13):
  update(t)
  for bone in ('mixamorig:RightHand','mixamorig:RightHandIndex1','mixamorig:Head'):
   print('PROBE',t,bone,tuple(round(v,4) for v in (hero.matrix_world @ hero.pose.bones[bone].matrix).translation),flush=True)
  print('PROP',t,tuple(round(v,4) for v in phone.matrix_world.translation),tuple(round(v,4) for v in cup.matrix_world.translation),flush=True)
 raise SystemExit(0)
if args.stills:
 out=Path('/home/user/celebrity-story-v4-stills');out.mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory() as td:
  frame=Path(td)/'frame.png'
  for t in (1,4,8,11,14,18,21,25,29,33,38,42,46,50,54,58):render(t,frame);overlay(frame,t).save(out/f'preview-{t}.jpg',quality=92)
else:
 ff=imageio_ffmpeg.get_ffmpeg_exe();out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as td:
  frame=Path(td)/'frame.png';proc=subprocess.Popen([ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(out)],stdin=subprocess.PIPE)
  for n in range(FPS*args.start,FPS*args.end):
   t=n/FPS;render(t,frame);proc.stdin.write(overlay(frame,t).tobytes())
   if n%(FPS*2)==0:print('RENDER_PROGRESS',n, '/',FPS*60,flush=True)
  proc.stdin.close()
  if proc.wait():raise RuntimeError('encode failed')
 print('OUTPUT',out,flush=True)
