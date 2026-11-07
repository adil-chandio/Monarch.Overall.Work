"""Fresh, continuous-geometry Cycles look development. No prior film frames or image plates.
All coordinates, materials, cameras and animation are authored here. Reconstructions illustrative.
Run using the pinned bpy wheel, no desktop Blender required.
"""
import bpy, math, random, argparse, os, json, time
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.noise import noise_vector
P=argparse.ArgumentParser();P.add_argument('--from',dest='start',type=int,default=0);P.add_argument('--to',dest='end',type=int,default=1);P.add_argument('--width',type=int,default=1920);P.add_argument('--samples',type=int,default=24);P.add_argument('--out',default='.cache/extinct-v8/frames');P.add_argument('--step',type=int,default=1);a=P.parse_args()
R=Path.cwd();OUT=R/a.out;OUT.mkdir(parents=True,exist_ok=True)
random.seed(81042)
def sat(x):return max(0.,min(1.,x))
def ease(x):x=sat(x);return x*x*(3-2*x)
def lerp(a,b,u):return Vector(a).lerp(Vector(b),u)
def track(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def material(name,color,rough=.6,metal=0,scale=5,bump=.1,subsurface=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');s=n.new('ShaderNodeBsdfPrincipled');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;s.inputs['Subsurface Weight'].default_value=subsurface;l.new(s.outputs['BSDF'],out.inputs['Surface'])
 if bump:
  tc=n.new('ShaderNodeTexCoord');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=5;tex.inputs['Roughness'].default_value=.72;l.new(tc.outputs['Generated'],tex.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.12;r.color_ramp.elements[0].color=tuple(c*.45 for c in color)+(1,);r.color_ramp.elements[1].position=.85;r.color_ramp.elements[1].color=tuple(min(1,c*1.35) for c in color)+(1,);l.new(tex.outputs['Fac'],r.inputs[0]);l.new(r.outputs['Color'],s.inputs['Base Color']);bn=n.new('ShaderNodeBump');bn.inputs['Strength'].default_value=bump;bn.inputs['Distance'].default_value=.07;l.new(tex.outputs['Fac'],bn.inputs['Height']);l.new(bn.outputs[0],s.inputs['Normal'])
 return m

def mesh(name,v,f,mat,parent=None):
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
 if parent:o.parent=parent
 for p in o.data.polygons:p.use_smooth=True
 return o

def ell(name,loc,scale,mat,segments=32,rings=20):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for p in o.data.polygons:p.use_smooth=True
 return o

def box(name,loc,scale,mat,bevel=.035):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:
  mod=o.modifiers.new('Machined edge highlights','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o

def tube(name,points,radii,mat,sides=12):
 pts=[Vector(p) for p in points];v=[];f=[]
 for i,p in enumerate(pts):
  tangent=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized();u=tangent.cross(Vector((0,1,0)))
  if u.length<.05:u=tangent.cross(Vector((1,0,0)))
  u.normalize();w=tangent.cross(u).normalized();r=radii[i] if hasattr(radii,'__len__') else radii
  for j in range(sides):v.append(tuple(p+r*(math.cos(j*math.tau/sides)*u+math.sin(j*math.tau/sides)*w)))
 for i in range(len(pts)-1):
  for j in range(sides):x=i*sides+j;y=i*sides+(j+1)%sides;f.append((x,y,y+sides,x+sides))
 f.extend([tuple(range(sides-1,-1,-1)),tuple((len(pts)-1)*sides+j for j in range(sides))]);return mesh(name,v,f,mat)

def curve(name,pts,r,mat):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=r;c.bevel_resolution=2;s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 for p,co in zip(s.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o

def camera(loc,target,lens=48,fstop=4):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.data.lens=lens;o.data.sensor_width=36;o.data.clip_end=500;o.data.dof.use_dof=True;o.data.dof.aperture_fstop=fstop;track(o,target);o.data.dof.focus_distance=(Vector(loc)-Vector(target)).length;bpy.context.scene.camera=o;return o

def area(name,loc,target,power,color,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size;track(o,target)

def setup(kind):
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.065;s.cycles.max_bounces=5;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=3;s.cycles.transmission_bounces=4;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=a.width;s.render.resolution_y=round(a.width*9/16);s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.fps=30;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.film_transparent=False
 w=bpy.data.worlds.new('Cold skylight' if kind=='coast' else 'Environment fill');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.23,.34,.43,1) if kind=='coast' else (.29,.34,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.35 if kind=='coast' else .25;s.world=w
 s.use_nodes=True;n=s.node_tree.nodes;n.clear();r=n.new('CompositorNodeRLayers');gl=n.new('CompositorNodeGlare');gl.glare_type='FOG_GLOW';gl.quality='HIGH';gl.threshold=2;gl.mix=-.94;out=n.new('CompositorNodeComposite');s.node_tree.links.new(r.outputs['Image'],gl.inputs['Image']);s.node_tree.links.new(gl.outputs['Image'],out.inputs['Image'])
 return s

def ground(mat,cold=False,size=35):
 N=100;v=[];f=[]
 for j in range(N+1):
  y=-size/2+j*size/N
  for i in range(N+1):
   x=-size/2+i*size/N;z=.045*math.sin(x*2.1+y*.7)+.04*math.sin(y*3.7-x*.6)
   if cold:z+=.7*math.sin(x*.15)*math.sin(y*.11)
   v.append((x,y,z))
 for j in range(N):
  for i in range(N):q=j*(N+1)+i;f.append((q,q+1,q+N+2,q+N+1))
 return mesh('Sculpted terrain',v,f,mat)

def rocks(mat,count=90,spread=18):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);master=bpy.context.object;master.name='Stratified stone';master.data.materials.append(mat)
 for v in master.data.vertices:v.co*=1+.2*math.sin(v.co.x*12+v.co.z*8)
 for i in range(count):
  o=master if i==0 else bpy.data.objects.new('Rock',master.data)
  if i:bpy.context.collection.objects.link(o)
  x=random.uniform(-spread,spread);y=random.uniform(-spread,spread);r=random.uniform(.045,.4);o.location=(x,y,r*.3);o.scale=(r*1.4,r,r*.6);o.rotation_euler=(random.random()*.5,random.random()*.5,random.random()*6)

def leafmesh(name,loc,scale,mat,angle=0):
 v=[];f=[]
 for i in range(9):
  t=i/8;w=math.sin(t*math.pi)*.22
  for q in [-1,0,1]:v.append((w*q,t,.07*math.sin(t*math.pi)-abs(q)*.035))
 for i in range(8):
  for j in range(2):k=i*3+j;f.append((k,k+1,k+4,k+3))
 o=mesh(name,v,f,mat);o.location=loc;o.scale=(scale,scale,scale);o.rotation_euler=(.2,random.random()*.4,angle);return o

def vegetation():
 bark=material('Willow bark',(.16,.12,.075),.95,scale=12,bump=.65);leaves=material('Willow leaf veins',(.18,.25,.075),.78,scale=24,bump=.28,subsurface=.1);grass=material('Tundra grasses',(.20,.25,.09),.85,scale=5,bump=.12)
 for k in range(11):
  x=random.uniform(-10,10);y=random.uniform(1,11)
  for j in range(4):
   h=random.uniform(.8,2);curve('Flexible willow branch',[(x,y,0),(x+.1*j,y,.5),(x+.3*(j-1),y+.13*j,h)],.017,bark)
   for z in range(7):leafmesh('Willow leaf',(x+.25*(j-1)*z/7,y+.12*j*z/7,.4+(h-.4)*z/7),.18,leaves,(z%2)*math.pi+z*.6)
 v=[];f=[]
 for k in range(1100):
  x=random.uniform(-14,14);y=random.uniform(-9,14)
  if abs(x)<1.35 and -3<y<2:continue
  for j in range(4):
   h=random.uniform(.14,.45);rot=random.random()*6;dx=math.cos(rot)*.025;dy=math.sin(rot)*.025;q=len(v);v.extend([(x-dx,y-dy,0),(x+dx,y+dy,0),(x+.06,y+.05,h*.6),(x+.09,y+.06,h)]);f.append((q,q+1,q+2,q+3))
 mesh('Individual bent grass blades',v,f,grass)
 return leaves

def mastodon():
 skin=material('Warm umber skin, two-scale folds',(.175,.105,.062),.85,scale=24,bump=.4,subsurface=.045)
 # Distorted directional folds are subordinate to the authored continuous silhouette.
 n=skin.node_tree.nodes;l=skin.node_tree.links;s=next(x for x in n if x.type=='BSDF_PRINCIPLED');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3;tex.inputs['Detail'].default_value=2;wave=n.new('ShaderNodeTexWave');wave.wave_type='BANDS';wave.bands_direction='Z';wave.inputs['Scale'].default_value=36;wave.inputs['Distortion'].default_value=8;l.new(tex.outputs['Color'],wave.inputs['Vector']);bn=n.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.23;bn.inputs['Distance'].default_value=.025;l.new(wave.outputs['Color'],bn.inputs['Height']);old=s.inputs['Normal'].links[0].from_socket;l.new(old,bn.inputs['Normal']);l.new(bn.outputs[0],s.inputs['Normal'])
 parts=[]
 for name,loc,sc in [('Barrel',(0,.12,2.38),(1.05,1.8,1.08)),('Shoulders',(0,-.9,2.45),(1,1,1.13)),('Rump',(0,1.25,2.32),(.93,.95,.94)),('Neck',(0,-1.32,2.6),(.76,.8,.84)),('Low cranium',(0,-1.93,2.84),(.65,.71,.73)),('Cheeks',(0,-2.12,2.4),(.54,.52,.55))]:parts.append(ell(name,loc,sc,skin))
 leg_centers=[]
 for x in [-.68,.68]:
  for y in [-1.03,1.17]:
   parts.extend([ell('Upper leg',(x,y,1.43),(.39,.46,.92),skin),ell('Foreleg taper',(x,y-.025,.67),(.27,.31,.65),skin),ell('Wide weight-bearing foot',(x,y-.12,.16),(.33,.43,.2),skin)]);leg_centers.append((x,y))
 for i in range(13):
  t=i/12;parts.append(ell('Continuous trunk',(0,-2.45-.26*math.sin(t*2),2.48-1.95*t),(.24-.15*t,.24-.15*t,.25),skin,20,12))
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();body=bpy.context.object;body.name='Unified sculpt — no separate ball joints';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 mod=body.modifiers.new('Continuous anatomical union','REMESH');mod.mode='VOXEL';mod.voxel_size=.055;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Sculpt relaxation','SMOOTH');mod.factor=1.15;mod.iterations=5;bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Surface refinement','SUBSURF');mod.levels=1;mod.render_levels=1
 bind=np.array([v.co[:] for v in body.data.vertices],np.float32);headparts=[];ears=[]
 ivory=material('Worn ivory',(.72,.62,.43),.32,scale=45,bump=.16);eye=material('Moist dark eyes',(.012,.008,.005),.14,bump=0);dark=material('Nostrils and crease',(.025,.017,.012),.75,bump=0)
 for side in [-1,1]:
  # Broad, small fan, not a circular primitive ear.
  v=[(side*.56,-1.59,2.9)];N=24
  for i in range(N+1):u=i/N*math.tau;v.append((side*(.59+.36*(1+math.cos(u))),-1.53+.12*math.sin(u),2.68+.56*math.sin(u)))
  ear=mesh('Sculpted fan ear',v,[(0,i+1,i+2) for i in range(N)],skin);mod=ear.modifiers.new('Ear thickness','SOLIDIFY');mod.thickness=.035;mod=ear.modifiers.new('Soft ear edge','SUBSURF');mod.levels=2;ears.append(ear)
  pts=[(side*.29,-2.32,2.23),(side*.43,-2.65,2.07),(side*.52,-3.0,2.03),(side*.55,-3.36,2.15)]
  tusk=tube('Gently curved tapered tusk',pts,[.13,.12,.085,.006],ivory,24);mod=tusk.modifiers.new('Tusk polish','SUBSURF');mod.levels=2;headparts.append(tusk)
  headparts.append(ell('Eye socket',(side*.52,-2.24,2.93),(.12,.065,.105),skin));headparts.append(ell('Eye',(side*.579,-2.283,2.94),(.046,.036,.045),eye));headparts.append(curve('Upper eyelid',[(side*.555,-2.30,2.955),(side*.583,-2.30,2.985),(side*.615,-2.27,2.961)],.014,skin))
  for j in range(3):ell('Blunt nail',(side*.68+(j-1)*.15,-1.43,.14),(.065,.035,.065),ivory)
 for side in [-1,1]:ell('Trunk nostril',(side*.035,-2.704,.52),(.025,.02,.032),dark)
 tail=curve('Tail',[(0,1.85,2.3),(.08,2.03,1.7),(.1,2.1,1.08)],.035,skin)
 # Short fur is generated on the continuous surface, not painted onto a sphere.
 fur=material('Short warm coat',(.095,.052,.026),.87,scale=12,bump=.08);body.data.materials.append(fur)
 vg=body.vertex_groups.new(name='Coat density')
 for v in body.data.vertices:
  if v.co.z>1.25 and v.co.y> -2.2:vg.add([v.index],sat((v.co.z-1.2)*2), 'REPLACE')
 bpy.context.view_layer.objects.active=body;body.select_set(True);bpy.ops.object.particle_system_add();ps=body.particle_systems[-1];ps.settings.type='HAIR';ps.settings.count=2200;ps.settings.hair_length=.055;ps.settings.hair_step=2;ps.settings.child_type='INTERPOLATED';ps.settings.rendered_child_count=5;ps.settings.child_percent=3;ps.settings.material=2;ps.vertex_group_density=vg.name;ps.settings.root_radius=.25;ps.settings.tip_radius=.025;ps.settings.radius_scale=.012
 headbind=[(o,np.array(o.location[:])) for o in headparts]
 def update(t):
  z=bind[:,2];y=bind[:,1];out=bind.copy();breath=.008*math.sin(t*1.5);out[:,2]+=breath*np.clip((z-1.3)/1.5,0,1)
  # One supported forefoot placement; no generic perpetual walk cycle.
  lift=.2*(1-ease(t/2.6));m=np.exp(-((bind[:,0]+.68)/.38)**4-((y+1.03)/.55)**4)*np.clip((1.65-z)/1.2,0,1);out[:,2]+=m*lift;out[:,1]-=m*.08*(1-ease(t/2.6))
  trunk=np.clip((-y-2.32)/.3,0,1)*np.clip((2.65-z)/1.6,0,1);out[:,0]+=.12*math.sin(t*.65)*trunk;out[:,1]-=.06*math.sin(t*.8)*trunk
  body.data.vertices.foreach_set('co',out.ravel());body.data.update()
  for i,e in enumerate(ears):e.rotation_euler.z=(i*2-1)*.035*math.sin(t*.9)
  tail.rotation_euler.y=.045*math.sin(t*.8)
 return body,update

def forest_scene():
 soil=material('Wet organic earth',(.095,.076,.042),.87,scale=45,bump=.65);stone=material('Slate inclusions',(.23,.24,.20),.78,scale=15,bump=.6);ground(soil);rocks(stone,100);vegetation();body,animalupdate=mastodon();area('Low amber sun',(-7,-6,10),(0,0,1),2300,(1,.69,.4),6);area('Large cool sky',(6,-1,9),(0,0,1),1600,(.57,.73,1),8);area('Coat rim',(-1,7,8),(0,0,2),2600,(1,.85,.59),5)
 water=material('Reflective quiet channel',(.09,.15,.13),.16,metal=.3,scale=16,bump=.12);box('Watercourse',(4,1,-.025),(4,35,.035),water,.01)
 cam=camera((7,-9,3.4),(0,-.7,1.8),48,4)
 # A specific leaf transfer, not a shower of arbitrary glowing DNA beads.
 lm=material('Detached organic leaf',(.29,.23,.075),.8,scale=30,bump=.3);leaf=leafmesh('Leaf to water',(2.8,1.7,1.2),.32,lm,1.5)
 def update(t,late=False):
  animalupdate(t if not late else t+4)
  if not late:
   u=ease(t/6.1);cam.location=lerp((7,-9,3.4),(4.7,-6.1,2.5),u);target=lerp((0,-.7,1.8),(-.15,-1.25,1.35),u)
  else:
   u=ease(t/7.667);cam.location=lerp((7,-6,3),(5,-3.2,1.7),u);target=lerp((0,-.5,1.8),(1.2,-.8,1.2),u);d=ease((t-2)/3.5);leaf.location=(2.8+.5*d,1.7-1.3*d,1.2*(1-d)+.015);leaf.rotation_euler.y=.5*d;leaf.rotation_euler.z=1.5+2*d
  track(cam,target);cam.data.dof.focus_distance=(cam.location-target).length
 return update

def macro_scene():
 mat=material('Layered clay mineral',(.21,.135,.073),.82,scale=7,bump=.65);pale=material('Illustrative fragment backbone',(.58,.47,.28),.38,scale=32,bump=.12);base=ell('Asymmetric mineral grain',(0,0,-.15),(2.5,1.8,.75),mat,64,40)
 for v in base.data.vertices:v.co.z+=.09*math.sin(v.co.x*10+v.co.y*3)*math.sin(v.co.y*12)
 grains=[]
 for k in range(40):
  x=random.uniform(-2,2);y=random.uniform(-1.5,1.5);r=random.uniform(.025,.08);grains.append(ell('Fine mineral inclusion',(x,y,.45+.035*math.sin(x*10)),(r,r*.7,r*.4),mat,12,8))
 strands=[]
 for k in range(4):
  cx=-.9+k*.48;cy=(-1)**k*.22
  for side in [-1,1]:
   pts=[(cx+side*.085*math.cos(i*.65),cy+i*.10,.77+.085*math.sin(i*.65)*side) for i in range(7-k%2)];strands.append(tube('Short broken illustrative fragment',pts,.018,pale,8))
  for j in range(6-k%2):
   t=j*.65;strands.append(tube('Short paired rung',[(cx-.085*math.cos(t),cy+j*.1,.77-.085*math.sin(t)),(cx+.085*math.cos(t),cy+j*.1,.77+.085*math.sin(t))],.012,pale,6))
 area('Macro softbox',(-3,-4,5),(0,0,0),430,(1,.77,.48),3);area('Macro edge',(2,3,4),(0,0,0),560,(.6,.76,1),2);cam=camera((2.3,-4.2,2.7),(0,.1,.6),55,5.6)
 def update(t):
  u=ease(t/7.32);cam.location=lerp((2.3,-4.2,2.7),(1.4,-3.0,2.1),u);target=Vector((-.12,.15,.57));track(cam,target);cam.data.dof.focus_distance=(cam.location-target).length
  for j,o in enumerate(strands):o.location.z=.16*(1-ease((t-.6)/4));o.location.x=.03*math.sin(t*.6)*(1-ease(t/5))
 return update

def coast_scene():
 terrain=material('Polar desert — frost and shale',(.31,.32,.29),.94,scale=35,bump=.7);rock=material('Exposed weathered strata',(.24,.25,.24),.91,scale=21,bump=.65);snow=material('Old frost',(.63,.72,.75),.88,scale=45,bump=.3);ground(terrain,True,100);rocks(rock,190,35)
 # Distant ridges have authored silhouettes, not texture-only backgrounds.
 for k in range(5):
  pts=[];f=[]
  for j in range(50):x=-80+j*3.3;y=30+k*8;h=3+k*1.3+2*math.sin(j*.29+k)+.7*math.sin(j*1.7);pts.extend([(x,y,-1),(x,y,h)])
  for j in range(49):q=j*2;f.append((q,q+1,q+3,q+2))
  mesh('Far eroded ridge',pts,f,rock)
 water=material('Cold fjord',(.12,.23,.29),.19,metal=.25,scale=55,bump=.17);box('Fjord surface',(0,-18,-.3),(160,30,.08),water,.01)
 for j in range(45):
  x=random.uniform(-30,30);y=random.uniform(-.5,24);r=random.uniform(.18,1.2);ell('Snow retained in hollows',(x,y,.02),(r,r*.55,.045),snow,16,8)
 area('Arctic overcast',(-10,-8,22),(0,0,0),5800,(.73,.86,1),18);area('Horizon light',(20,22,10),(0,0,1),2700,(1,.84,.65),12);cam=camera((11,-9,4.4),(0,8,1.8),36,11)
 def update(t):
  u=ease(t/12.31);cam.location=lerp((11,-9,4.4),(6,-4.2,3.1),u);target=Vector((-2,12,2));track(cam,target);cam.data.dof.focus_distance=35
 return update

def strata_scene():
 mats=[material('Sediment layer '+str(i),c,.9,scale=30,bump=.55) for i,c in enumerate([(.24,.16,.09),(.32,.23,.14),(.19,.15,.105),(.38,.29,.19),(.26,.21,.15)])];metal=material('Brushed support steel',(.42,.47,.48),.28,.82,scale=45,bump=.13);rubber=material('Grip rubber',(.045,.055,.05),.75,scale=32,bump=.18);plant=material('Plant remnant, not fresh leaf',(.13,.095,.04),.92,scale=50,bump=.45)
 for j in range(15):
  o=box('Exposed sediment bed',(0,0,.12+j*.17),(5.5,2.2,.17),mats[j%5],.015)
  for v in o.data.vertices:v.co.z+=.018*math.sin(v.co.x*6+j)*math.cos(v.co.y*4)
 # Field support/guide visibly constrains the sampling sleeve.
 box('Sampler base',(2.1,-.25,2.73),(.6,1.05,.15),metal);box('Vertical guide',(2.3,.05,3.4),(.12,.12,1.5),metal)
 sleeve=box('Guided sample carriage',(1.99,-.2,3.1),(.43,.43,.55),metal);handle=box('Carriage top grip',(2,-.2,3.48),(.55,.2,.12),rubber)
 leaf=leafmesh('Preserved plant remain',(-.4,-1.12,1.46),.72,plant,.6);leaf.rotation_euler=(math.pi/2,0,.4)
 for j in range(7):curve('Plant vein',[(-.4,-1.14,1.46),(-.4+.11*j,-1.15,1.46+.065*j),(-.15+.07*j,-1.15,1.55+.07*j)],.006,plant)
 area('Field sidelight',(-4,-6,8),(0,0,1),1800,(1,.77,.51),5);area('Field sky',(5,2,8),(0,0,1),1600,(.63,.78,1),7);cam=camera((6,-8,4.4),(0,0,1.6),52,6.3)
 def update(t):
  u=ease(t/11.35);cam.location=lerp((6,-8,4.4),(1.5,-4.8,2.3),u);target=lerp((.4,0,1.7),(-.15,-.9,1.6),ease((t-4)/5));track(cam,target);cam.data.dof.focus_distance=(cam.location-target).length;sleeve.location.z=3.1-.30*ease((t-1)/3);handle.location.z=3.48-.30*ease((t-1)/3)
 return update

def archive_scene():
 clay=material('Ochre sediment interior',(.26,.16,.075),.93,scale=42,bump=.7);evidence=material('Short incomplete evidence markers',(.65,.53,.31),.5,scale=25,bump=.16);pieces=[]
 for k in range(16):
  x=(k%4-1.5)*.65;y=(k//4-1.5)*.52;r=.3+random.random()*.15;o=ell('Broken clay aggregate',(x,y,.12),(r,r*.8,r*.6),clay,24,16);pieces.append((o,Vector((x,y,.12))))
 fragments=[]
 for k in range(5):
  x=(k-2)*.38;y=.13*math.sin(k*2)
  pts=[(x+j*.035,y+j*.07,.32+.025*math.sin(j*2)) for j in range(4+k%3)];fragments.append(tube('Incomplete fragment, not a genome',pts,.019,evidence,10))
 area('Evidence grazing light',(-3,-3,4),(0,0,0),480,(1,.77,.45),3);area('Cool mineral edge',(2,2,4),(0,0,0),600,(.58,.79,1),2);cam=camera((.4,-3.8,3.2),(0,0,.3),57,5.6)
 def update(t):
  d=ease((t-.5)/6)
  for o,p in pieces:o.location=p+Vector((p.x*.25*d,p.y*.3*d,-.08*d))
  u=ease(t/9.367);cam.location=lerp((.4,-3.8,3.2),(1.8,-3.1,2.4),u);target=Vector((0,.1,.28));track(cam,target);cam.data.dof.focus_distance=(cam.location-target).length
 return update

def lab_scene():
 ceramic=material('Off-white laboratory ceramic',(.57,.63,.60),.36,scale=25,bump=.06);steel=material('Satin machined steel',(.34,.40,.43),.25,.85,scale=65,bump=.1);black=material('Anodized fixture',(.025,.045,.052),.37,.6,scale=40,bump=.08);soil=material('Sediment in sample well',(.18,.12,.065),.9,scale=35,bump=.55)
 box('Work surface',(0,0,-.25),(8,6,.35),ceramic,.1);box('Instrument base',(0,.3,.04),(2.8,2,.22),black,.1);box('Supported vertical column',(1.1,.8,1.2),(.22,.24,2.4),steel);box('Supported cantilever',(.35,.8,2.32),(1.65,.25,.18),steel);box('Optical head',(-.3,.55,1.9),(.55,.6,.65),ceramic,.12)
 tray=box('Sliding sample receiver',(-1.3,-.25,.32),(1.2,1,.14),steel,.06);sample=ell('Sediment specimen',(-1.3,-.25,.45),(.38,.29,.1),soil)
 for side in [-1,1]:box('Linear slide rail',(side*.65,-.2,.19),(.055,2.2,.07),steel,.02)
 for k in range(8):box('Background specimen tray',(k*.6-2,2,.02),(.45,.6,.05),ceramic,.03)
 area('Large laboratory key',(-3,-4,6),(0,0,1),1400,(.75,.88,1),4);area('Warm separating edge',(3,3,5),(0,0,1),1600,(1,.78,.49),3);area('Instrument lamp',(-.3,.5,1.57),(0,-.3,.3),35,(.78,.92,1),.4);cam=camera((3.3,-4.6,2.8),(0,0,.9),53,5)
 def update(t):
  u=ease(t/6.893);cam.location=lerp((3.3,-4.6,2.8),(2.1,-3.5,2.0),u);target=Vector((-.1,.15,.8));track(cam,target);cam.data.dof.focus_distance=(cam.location-target).length;pos=-1.3+1.0*ease((t-.5)/3.8);tray.location.x=pos;sample.location.x=pos
 return update

# The master remains unchanged; this development film includes the first complete 61 s.
SHOTS=[(0,183,'forest'),(183,403,'macro'),(403,772,'coast'),(772,1112,'strata'),(1112,1393,'archive'),(1393,1600,'lab'),(1600,1830,'forest-late')]
last=None;records=[]
for frame in range(a.start,a.end,a.step):
 row=next(r for r in SHOTS if r[0]<=frame<r[1]);start,end,kind=row
 if kind!=last:
  random.seed(81042);setup(kind)
  if kind.startswith('forest'):fn=forest_scene()
  elif kind=='coast':fn=coast_scene()
  elif kind=='strata':fn=strata_scene()
  elif kind=='lab':fn=lab_scene()
  elif kind=='archive':fn=archive_scene()
  else:fn=macro_scene()
  last=kind;print('BUILT',kind,'objects',len(bpy.data.objects),flush=True)
 t=(frame-start)/30
 if kind=='forest-late':fn(t,True)
 else:fn(t)
 bpy.context.view_layer.update();s=bpy.context.scene;s.render.filepath=str(OUT/f'{frame:05}.png');begin=time.time();bpy.ops.render.render(write_still=True);records.append({'frame':frame,'scene':kind,'render_seconds':round(time.time()-begin,2)});print('FRAME',frame,kind,records[-1]['render_seconds'],flush=True)
(OUT.parent/f'render-{a.start}-{a.end}.json').write_text(json.dumps({'frames':records,'width':a.width,'fps':30,'engine':'Cycles CPU','samples':a.samples,'source_frames_reused':False,'scene_image_plates':False},indent=2))
# bpy wheel shutdown has a known occasional finalizer crash; all files flush before exit.
os._exit(0)
