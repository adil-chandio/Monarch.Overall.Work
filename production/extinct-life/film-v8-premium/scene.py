"""Fresh, continuous-geometry Cycles look development. No prior film frames or image plates.
All coordinates, materials, cameras and animation are authored here. Reconstructions illustrative.
Run using the pinned bpy wheel, no desktop Blender required.
"""
import bpy, math, random, argparse, os, json, time, hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.noise import noise_vector
P=argparse.ArgumentParser();P.add_argument('--from',dest='start',type=int,default=0);P.add_argument('--to',dest='end',type=int,default=1);P.add_argument('--width',type=int,default=1920);P.add_argument('--samples',type=int,default=24);P.add_argument('--out',default='.cache/extinct-v8/frames');P.add_argument('--step',type=int,default=1);P.add_argument('--lock-camera',action='store_true');a=P.parse_args()
R=Path.cwd();OUT=R/a.out;OUT.mkdir(parents=True,exist_ok=True)
random.seed(81042)
def sat(x):return max(0.,min(1.,x))
def ease(x):x=sat(x);return x*x*(3-2*x)
def lerp(a,b,u):return Vector(a).lerp(Vector(b),u)
def track(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def material(name,color,rough=.6,metal=0,scale=5,bump=.1,subsurface=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');s=n.new('ShaderNodeBsdfPrincipled');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;s.inputs['Subsurface Weight'].default_value=subsurface;l.new(s.outputs['BSDF'],out.inputs['Surface'])
 if bump:
  tc=n.new('ShaderNodeTexCoord');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=5;tex.inputs['Roughness'].default_value=.72;l.new(tc.outputs['Object'],tex.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.12;r.color_ramp.elements[0].color=tuple(c*.45 for c in color)+(1,);r.color_ramp.elements[1].position=.85;r.color_ramp.elements[1].color=tuple(min(1,c*1.35) for c in color)+(1,);l.new(tex.outputs['Fac'],r.inputs[0]);l.new(r.outputs['Color'],s.inputs['Base Color']);bn=n.new('ShaderNodeBump');bn.inputs['Strength'].default_value=bump;bn.inputs['Distance'].default_value=.012;l.new(tex.outputs['Fac'],bn.inputs['Height']);l.new(bn.outputs[0],s.inputs['Normal'])
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
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.065;s.cycles.max_bounces=5;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=3;s.cycles.transmission_bounces=4;s.render.threads_mode='FIXED';s.render.threads=min(4,os.cpu_count() or 2);s.render.use_persistent_data=True;s.render.resolution_x=a.width;s.render.resolution_y=round(a.width*9/16);s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.fps=30;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.film_transparent=False
 w=bpy.data.worlds.new('Cold skylight' if kind=='coast' else 'Environment fill');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.23,.34,.43,1) if kind=='coast' else (.29,.34,.35,1);w.node_tree.nodes['Background'].inputs[1].default_value=.35 if kind=='coast' else .25;s.world=w
 if kind in ('forest','forest-late','coast'):
  nodes=w.node_tree.nodes;links=w.node_tree.links;sky=nodes.new('ShaderNodeTexSky');sky.sky_type='NISHITA';sky.sun_elevation=.18 if kind=='coast' else .3;sky.sun_rotation=2.5;sky.altitude=20;sky.air_density=1.15;sky.dust_density=.6;links.new(sky.outputs[0],nodes['Background'].inputs[0]);nodes['Background'].inputs[1].default_value=.035 if kind=='coast' else .04
 s.use_nodes=True;n=s.node_tree.nodes;n.clear();r=n.new('CompositorNodeRLayers');gl=n.new('CompositorNodeGlare');gl.glare_type='FOG_GLOW';gl.quality='HIGH';gl.threshold=2;gl.mix=-.94;out=n.new('CompositorNodeComposite');s.node_tree.links.new(r.outputs['Image'],gl.inputs['Image']);s.node_tree.links.new(gl.outputs['Image'],out.inputs['Image'])
 return s

def height(x,y,cold=False):
 z=.045*math.sin(x*2.1+y*.7)+.04*math.sin(y*3.7-x*.6)
 if cold:
  z*=.18
  z+=.27*math.sin(x*.15)*math.sin(y*.11)-.85*ease((-x-8)/9)
  z+=ease((y-18)/18)*(4.8+2.0*math.sin(x*.12+y*.08)+1.3*math.sin(x*.31-y*.14)+.6*math.sin(x*.75+y*.4))
 else:z-=.23*ease((x-1.8)/.4)
 return z

def ground(mat,cold=False,size=35):
 N=160 if cold else 110;v=[];f=[]
 for j in range(N+1):
  y=-size/2+j*size/N
  for i in range(N+1):
   x=-size/2+i*size/N;v.append((x,y,height(x,y,cold)))
 for j in range(N):
  for i in range(N):q=j*(N+1)+i;f.append((q,q+1,q+N+2,q+N+1))
 return mesh('Continuous sculpted terrain',v,f,mat)

def rocks(mat,count=90,spread=18,cold=False):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);master=bpy.context.object;master.name='Stratified stone';master.data.materials.append(mat)
 for v in master.data.vertices:v.co*=1+.2*math.sin(v.co.x*12+v.co.z*8)
 for poly in master.data.polygons:poly.use_smooth=True
 for i in range(count):
  o=master if i==0 else bpy.data.objects.new('Rock',master.data)
  if i:bpy.context.collection.objects.link(o)
  x=random.uniform(-spread,spread);y=random.uniform(-spread,spread);r=random.uniform(.045,.4);o.location=(x,y,height(x,y,cold)+r*.17);o.scale=(r*1.4,r,r*.6);o.rotation_euler=(random.random()*.25,random.random()*.25,random.random()*6)

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
  if (abs(x)<1.35 and -3<y<2) or x>2:continue
  for j in range(4):
   h=random.uniform(.14,.45);rot=random.random()*6;dx=math.cos(rot)*.025;dy=math.sin(rot)*.025;q=len(v);z=height(x,y);v.extend([(x-dx,y-dy,z),(x+dx,y+dy,z),(x+.06,y+.05,z+h*.6),(x+.09,y+.06,z+h)]);f.append((q,q+1,q+2,q+3))
 mesh('Individual bent grass blades',v,f,grass)
 # Layered 3D canopy: trunks/branches and individual leaves, no image billboard.
 for k in range(25):
  x=random.uniform(-22,22);y=random.uniform(9,23);h=random.uniform(3.6,6.5)
  curve('Distant tree trunk',[(x,y,height(x,y)),(x+.12,y,h*.5),(x+.25,y,h)],.07,bark)
  for j in range(6):
   ang=j*2.4;dx=math.cos(ang);dy=math.sin(ang);z=h*(.42+j*.075);tip=(x+dx*1.3,y+dy*1.2,z+.9)
   curve('Canopy branch',[(x+.12,y,z),((x+tip[0])/2,(y+tip[1])/2,z+.35),tip],.019,bark)
   for q in range(20):
    u=random.random();leafmesh('Canopy leaf',(x+dx*1.3*u+random.uniform(-.45,.45),y+dy*1.2*u+random.uniform(-.45,.45),z+.9*u+random.uniform(-.25,.3)),random.uniform(.20,.35),leaves,random.random()*6.28)
 return leaves

def mastodon():
 before=set(bpy.data.objects)
 skin=material('Warm umber skin, subtle pore scale',(.12,.075,.043),.83,scale=72,bump=.22,subsurface=.045)
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
  ear=mesh('Sculpted fan ear',v,[(0,i+1,i+2) for i in range(N)],skin);pivot=Vector((side*.56,-1.59,2.9))
  for vert in ear.data.vertices:vert.co-=pivot
  ear.location=pivot;mod=ear.modifiers.new('Ear thickness','SOLIDIFY');mod.thickness=.035;mod=ear.modifiers.new('Soft ear edge','SUBSURF');mod.levels=2;ears.append(ear)
  pts=[(side*.29,-2.32,2.23),(side*.43,-2.65,2.07),(side*.52,-3.0,2.03),(side*.55,-3.36,2.15)]
  tusk=tube('Gently curved tapered tusk',pts,[.13,.12,.085,.006],ivory,24);mod=tusk.modifiers.new('Tusk polish','SUBSURF');mod.levels=2;headparts.append(tusk)
  headparts.append(ell('Eye socket',(side*.52,-2.24,2.93),(.12,.065,.105),skin));headparts.append(ell('Eye',(side*.579,-2.283,2.94),(.046,.036,.045),eye));headparts.append(curve('Upper eyelid',[(side*.555,-2.30,2.955),(side*.583,-2.30,2.985),(side*.615,-2.27,2.961)],.014,skin))
  for j in range(3):ell('Blunt nail',(side*.68+(j-1)*.15,-1.43,.14),(.065,.035,.065),ivory)
 nostrils=[ell('Trunk nostril',(side*.035,-2.704,.52),(.025,.02,.032),dark) for side in [-1,1]]
 tail=curve('Tail',[(0,1.85,2.3),(.08,2.03,1.7),(.1,2.1,1.08)],.035,skin)
 # Short fur is generated on the continuous surface, not painted onto a sphere.
 fur=material('Short warm coat',(.095,.052,.026),.87,scale=12,bump=.08);body.data.materials.append(fur)
 vg=body.vertex_groups.new(name='Coat density')
 for v in body.data.vertices:
  if v.co.z>1.25 and v.co.y> -2.2:vg.add([v.index],sat((v.co.z-1.2)*2), 'REPLACE')
 bpy.context.view_layer.objects.active=body;body.select_set(True);bpy.ops.object.particle_system_add();ps=body.particle_systems[-1];ps.settings.type='HAIR';ps.settings.count=2200;ps.settings.hair_length=.027;ps.settings.hair_step=2;ps.settings.child_type='INTERPOLATED';ps.settings.rendered_child_count=5;ps.settings.child_percent=3;ps.settings.material=2;ps.vertex_group_density=vg.name;ps.settings.root_radius=.10;ps.settings.tip_radius=.025;ps.settings.radius_scale=.002
 headbind=[(o,np.array(o.location[:])) for o in headparts]
 def update(t):
  z=bind[:,2];y=bind[:,1];out=bind.copy();breath=.008*math.sin(t*1.5);out[:,2]+=breath*np.clip((z-1.3)/1.5,0,1)
  # One supported forefoot placement; no generic perpetual walk cycle.
  lift=.2*(1-ease(t/2.6));m=np.exp(-((bind[:,0]+.68)/.38)**4-((y+1.03)/.55)**4)*np.clip((1.65-z)/1.2,0,1);out[:,2]+=m*lift;out[:,1]-=m*.08*(1-ease(t/2.6))
  trunk=np.clip((-y-2.32)/.3,0,1)*np.clip((2.65-z)/1.6,0,1);out[:,0]+=.12*math.sin(t*.65)*trunk;out[:,1]-=.06*math.sin(t*.8)*trunk
  body.data.vertices.foreach_set('co',out.ravel());body.data.update()
  for i,o in enumerate(nostrils):o.location.x=(i*2-1)*.035+.12*math.sin(t*.65);o.location.y=-2.704-.06*math.sin(t*.8)
  for i,e in enumerate(ears):e.rotation_euler.z=(i*2-1)*.035*math.sin(t*.9)
  tail.rotation_euler.y=.045*math.sin(t*.8)
 root=bpy.data.objects.new('Reconstruction root',None);bpy.context.collection.objects.link(root)
 for o in set(bpy.data.objects)-before-{root}:
  if o.parent is None:o.parent=root
 return root,update

def forest_scene(late=False):
 if late:random.seed(81295)
 soil=material('Wet organic earth',(.065,.052,.031),.91,scale=24,bump=.42);stone=material('Slate inclusions',(.23,.24,.20),.78,scale=15,bump=.6);ground(soil,size=65);rocks(stone,100);vegetation();body,animalupdate=mastodon();area('Low amber sun',(-7,-6,10),(0,0,1),2300,(1,.69,.4),6);area('Large cool sky',(6,-1,9),(0,0,1),1600,(.57,.73,1),8);area('Coat rim',(-1,7,8),(0,0,2),2600,(1,.85,.59),5)
 water=material('Reflective quiet channel',(.04,.09,.095),.18,metal=.22,scale=8,bump=.15);box('Watercourse',(4,1,-.025),(4,35,.035),water,.01)
 cam=camera((8.8,-11,3.6),(0,-.5,1.85),42,2.8)
 if late:
  body.rotation_euler.z=.5
  curve('Willow at water edge',[(1.35,-2.35,0),(1.37,-2.36,.45),(1.42,-2.37,.8)],.014,soil)
 # A specific leaf transfer, not a shower of arbitrary glowing DNA beads.
 lm=material('Detached organic leaf',(.29,.23,.075),.8,scale=30,bump=.3);leaf=leafmesh('Leaf to water',(1.42,-2.37,.8),.32,lm,1.5)
 waternode=next(n for n in water.node_tree.nodes if n.type=='TEX_NOISE');waternode.noise_dimensions='4D'
 def update(t,late=False):
  animalupdate(t if not late else t+4);waternode.inputs['W'].default_value=t*.15
  if not late:
   u=ease(t/6.1);cam.location=lerp((8.8,-11,3.6),(6.7,-8.5,3.3),u);target=lerp((0,-.5,1.85),(0,-1,1.7),u)
  else:
   u=ease(t/7.667);cam.location=lerp((8,-9,3.8),(4.8,-5.5,1.5),u);target=lerp((.8,-1.4,1.55),(2.8,-2.15,.3),u);d=ease((t-2)/3.5);leaf.location=(1.42+1.7*d,-2.37+.25*d,.8*(1-d)+.015);leaf.rotation_euler.y=.5*d;leaf.rotation_euler.z=1.5+2*d
  track(cam,target);cam.data.dof.focus_distance=(cam.location-target).length
 return update

def molecular_fragment(cx,cy,z,length,ivory,teal):
 result=[]
 for side in [-1,1]:
  pts=[(cx+side*.065*math.cos(i/40*4.6),cy+i/40*length,z+side*.065*math.sin(i/40*4.6)) for i in range(41)];result.append(tube('Incomplete smooth backbone',pts,.018,ivory if side<0 else teal,10))
 for j in range(5):
  t=j/4*4.6;yy=cy+j/4*length;result.append(tube('Paired illustrative rung',[(cx-.065*math.cos(t),yy,z-.065*math.sin(t)),(cx+.065*math.cos(t),yy,z+.065*math.sin(t))],.011,ivory,8))
 return result

def macro_scene():
 mat=material('Clay mineral surface',(.19,.12,.065),.86,scale=35,bump=.38);ivory=material('Fragment ivory',(.55,.49,.35),.39,scale=65,bump=.10);teal=material('Fragment muted teal',(.075,.23,.22),.4,scale=55,bump=.08)
 v=[];f=[];N=80
 for j in range(N+1):
  y=-2+j*4/N
  for i in range(N+1):
   x=-3+i*6/N;v.append((x,y,-.06+.025*math.sin(x*5)*math.cos(y*5)))
 for j in range(N):
  for i in range(N):q=j*(N+1)+i;f.append((q,q+1,q+N+2,q+N+1))
 mesh('Mineral contact patch',v,f,mat);strands=[]
 for k in range(3):strands.extend(molecular_fragment(-.65+k*.65,-.3+(k%2)*.22,.005,.7-k*.1,ivory,teal))
 for k in range(32):
  x=random.uniform(-2.6,2.6);y=random.uniform(-1.8,1.8);r=random.uniform(.018,.065);ell('Mineral inclusion',(x,y,-.05),(r,r*.7,r*.35),mat,12,8)
 area('Macro softbox',(-3,-4,5),(0,0,0),430,(1,.77,.48),3);area('Macro edge',(2,3,4),(0,0,0),560,(.6,.76,1),2);cam=camera((1.8,-3,1.9),(0,.03,0),62,3.5)
 def update(t):
  u=ease(t/7.32);cam.location=lerp((1.8,-3,1.9),(1.2,-2.5,1.4),u);target=Vector((-.02,.02,0));track(cam,target);cam.data.dof.focus_distance=(cam.location-target).length
  for j,o in enumerate(strands):o.location.z=.12*(1-ease((t-.2)/4.5));o.location.x=.03*math.sin(t*.6)*(1-ease(t/5))
 return update

def coast_scene():
 terrain=material('Polar desert — frost and shale',(.31,.32,.29),.94,scale=35,bump=.7);rock=material('Exposed weathered strata',(.24,.25,.24),.91,scale=21,bump=.65);snow=material('Old frost',(.63,.72,.75),.88,scale=45,bump=.3);ground(terrain,True,100);rocks(rock,190,35,True)
 water=material('Cold fjord',(.12,.23,.29),.19,metal=.25,scale=55,bump=.17);wn=next(n for n in water.node_tree.nodes if n.type=='TEX_NOISE');wn.noise_dimensions='4D';box('Fjord surface',(-25,0,-.35),(32,120,.08),water,.01)
 for j in range(45):
  x=random.uniform(-25,25);y=random.uniform(-.5,24);r=random.uniform(.18,1.2);v=[(x,y,height(x,y,True)+.025)]
  for j in range(25):
   ang=j/24*math.tau;xx=x+math.cos(ang)*r*(1+.12*math.sin(ang*5));yy=y+math.sin(ang)*r*.6;v.append((xx,yy,height(xx,yy,True)+.025))
  mesh('Conforming snow hollow',v,[(0,j+1,j+2) for j in range(24)],snow)
 area('Arctic overcast',(-10,-8,22),(0,0,0),5800,(.73,.86,1),18);area('Horizon light',(20,22,10),(0,0,1),2700,(1,.84,.65),12);cam=camera((6,-3,1.8),(0,5,.7),36,11)
 def update(t):
  wn.inputs['W'].default_value=t*.12;u=ease(t/12.31);cam.location=lerp((6,-3,1.8),(9,-12,6.8),u);target=lerp((0,5,.7),(-5,12,1.3),u);track(cam,target);cam.data.dof.focus_distance=35
 return update

def strata_scene():
 mats=[material('Sediment layer '+str(i),c,.9,scale=30,bump=.55) for i,c in enumerate([(.24,.16,.09),(.32,.23,.14),(.19,.15,.105),(.38,.29,.19),(.26,.21,.15)])];metal=material('Brushed support steel',(.42,.47,.48),.28,.82,scale=45,bump=.13);rubber=material('Grip rubber',(.045,.055,.05),.75,scale=32,bump=.18);plant=material('Plant remnant, not fresh leaf',(.13,.095,.04),.92,scale=50,bump=.45)
 for j in range(15):
  v=[];f=[];N=48
  for k in range(N+1):
   x=-2.75+5.5*k/N
   for yy in [-1.1,1.1]:
    for q in [j,j+1]:v.append((x,yy+.014*math.sin(x*9+q),q*.17+.024*math.sin(x*3+q*.4)))
  for k in range(N):
   n=k*4;f.extend([(n,n+4,n+5,n+1),(n+2,n+3,n+7,n+6),(n,n+2,n+6,n+4),(n+1,n+5,n+7,n+3)])
  f.extend([(0,1,3,2),(N*4,N*4+2,N*4+3,N*4+1)]);bed=mesh('Irregular exposed sediment bed',v,f,mats[j%5])
  for poly in bed.data.polygons:poly.use_smooth=False
 # Field support/guide visibly constrains the sampling sleeve.
 box('Sampler base',(2.1,-.25,2.73),(.6,1.05,.15),metal);box('Vertical guide',(2.3,.05,3.4),(.12,.12,1.5),metal)
 sleeve=box('Guided sample carriage',(1.99,-.2,3.1),(.43,.43,.55),metal);handle=box('Carriage top grip',(2,-.2,3.48),(.55,.2,.12),rubber)
 leaf=leafmesh('Preserved plant remain',(-.4,-1.12,1.46),.72,plant,.6);leaf.rotation_euler=(math.pi/2,0,.4)
 for j in range(1,7):
  t=j/8
  for side in [-1,1]:
   vein=curve('Embedded leaf vein',[(0,t-.1,.07*math.sin((t-.1)*math.pi)+.006),(side*.08,t,.07*math.sin(t*math.pi)+.006),(side*.18*math.sin(t*math.pi),t+.03,.035)],.003,plant);vein.parent=leaf
 area('Field sidelight',(-4,-6,8),(0,0,1),1800,(1,.77,.51),5);area('Field sky',(5,2,8),(0,0,1),1600,(.63,.78,1),7);cam=camera((6,-8,4.4),(0,0,1.6),52,6.3)
 def update(t):
  u=ease(t/11.35);cam.location=lerp((6,-8,4.4),(1.5,-4.8,2.3),u);target=lerp((.4,0,1.7),(-.15,-.9,1.6),ease((t-4)/5));track(cam,target);cam.data.dof.focus_distance=(cam.location-target).length;sleeve.location.z=3.1-.30*ease((t-1)/3);handle.location.z=3.48-.30*ease((t-1)/3)
 return update

def archive_scene():
 clay=material('Irregular clay aggregate',(.19,.12,.062),.91,scale=35,bump=.45);ivory=material('Partial evidence backbone',(.58,.5,.32),.45,scale=50,bump=.1);teal=material('Partial evidence counterpart',(.07,.2,.19),.48,scale=45,bump=.1);pieces=[]
 box('Sediment beneath aggregates',(0,0,-.17),(6,5,.2),clay,.08)
 for k in range(25):
  x=random.uniform(-1.8,1.8);y=random.uniform(-1.4,1.4);r=random.uniform(.12,.45);bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1);o=bpy.context.object;o.name='Irregular fractured aggregate';o.data.materials.append(clay)
  for v in o.data.vertices:v.co*=1+.2*math.sin(v.co.x*8+v.co.z*5)
  o.scale=(r,r*.8,r*.45);o.location=(x,y,-.02);o.rotation_euler.z=random.random()*6
  for poly in o.data.polygons:poly.use_smooth=True
  pieces.append((o,Vector((x,y,-.02))))
 for k in range(3):molecular_fragment((k-1)*.55,-.18+k*.1,.18,.28+.08*k,ivory,teal)
 area('Evidence grazing light',(-3,-3,4),(0,0,0),480,(1,.77,.45),3);area('Cool mineral edge',(2,2,4),(0,0,0),600,(.58,.79,1),2);cam=camera((.4,-3.8,2.5),(0,0,.15),63,3.5)
 def update(t):
  d=ease((t-.5)/6)
  for o,p in pieces:o.location=p+Vector((p.x*.15*d,p.y*.18*d,-.02*d))
  u=ease(t/9.367);cam.location=lerp((.4,-3.8,2.5),(1.7,-3.3,1.8),u);target=Vector((0,.1,.16));track(cam,target);cam.data.dof.focus_distance=(cam.location-target).length
 return update

def lab_scene():
 ceramic=material('Off-white laboratory ceramic',(.57,.63,.60),.36,scale=25,bump=.06);steel=material('Satin machined steel',(.34,.40,.43),.25,.85,scale=65,bump=.1);black=material('Anodized fixture',(.025,.045,.052),.37,.6,scale=40,bump=.08);soil=material('Sediment in sample well',(.18,.12,.065),.9,scale=35,bump=.55)
 box('Laboratory back wall',(0,3.4,1.65),(10,.18,3.8),ceramic,.03)
 for level in [.65,1.8]:box('Background shelf',(0,2.85,level),(6,.7,.065),steel,.025)
 glass=material('Frosted sample containers',(.22,.36,.37),.23,scale=40,bump=.035)
 for k in range(7):
  x=-2.3+k*.65;ell('Closed background specimen container',(x,2.8,2.04),(.1,.1,.22),glass,20,12);box('Closed cap',(x,2.8,2.26),(.18,.18,.06),ceramic,.02)
 box('Work surface',(0,0,-.25),(8,6,.35),ceramic,.1);box('Instrument base',(0,.3,.04),(2.8,2,.22),black,.1);box('Supported vertical column',(1.1,.8,1.2),(.22,.24,2.4),steel);box('Supported cantilever',(.35,.8,2.32),(1.65,.25,.18),steel);box('Optical head',(-.3,.55,1.9),(.55,.6,.65),ceramic,.12)
 tray=box('Sliding sample receiver',(-1.3,-.25,.32),(1.2,1,.14),steel,.06);sample=ell('Sediment specimen',(-1.3,-.25,.45),(.38,.29,.1),soil)
 for side in [-1,1]:box('Linear slide rail',(0,side*.42-.25,.19),(2.8,.055,.07),steel,.02)
 for k in range(8):box('Background specimen tray',(k*.6-2,2,.02),(.45,.6,.05),ceramic,.03)
 area('Large laboratory key',(-3,-4,6),(0,0,1),1400,(.75,.88,1),4);area('Warm separating edge',(3,3,5),(0,0,1),1600,(1,.78,.49),3);area('Instrument lamp',(-.3,.5,1.57),(0,-.3,.3),35,(.78,.92,1),.4);cam=camera((3.8,-5.3,3.1),(0,.15,1.1),45,4)
 def update(t):
  u=ease(t/6.893);cam.location=lerp((3.8,-5.3,3.1),(2.8,-4.5,2.8),u);target=Vector((0,.15,1.1));track(cam,target);cam.data.dof.focus_distance=(cam.location-target).length;pos=-1.3+1.0*ease((t-.5)/3.8);tray.location.x=pos;sample.location.x=pos
 return update

# The master remains unchanged; this development film includes the first complete 61 s.
SHOTS=[(0,183,'forest'),(183,403,'macro'),(403,772,'coast'),(772,1112,'strata'),(1112,1393,'archive'),(1393,1600,'lab'),(1600,1830,'forest-late')]
last=None;records=[];locked=None
for frame in range(a.start,a.end,a.step):
 row=next(r for r in SHOTS if r[0]<=frame<r[1]);start,end,kind=row
 if kind!=last:
  random.seed(81042);setup(kind)
  if kind.startswith('forest'):fn=forest_scene(kind=='forest-late')
  elif kind=='coast':fn=coast_scene()
  elif kind=='strata':fn=strata_scene()
  elif kind=='lab':fn=lab_scene()
  elif kind=='archive':fn=archive_scene()
  else:fn=macro_scene()
  last=kind;locked=None;print('BUILT',kind,'objects',len(bpy.data.objects),flush=True)
 t=(frame-start)/30
 if kind=='forest-late':fn(t,True)
 else:fn(t)
 bpy.context.view_layer.update();s=bpy.context.scene
 if a.lock_camera:
  if locked is None:locked=s.camera.matrix_world.copy()
  else:s.camera.matrix_world=locked.copy()
 bpy.context.view_layer.update();s=bpy.context.scene;s.render.filepath=str(OUT/f'{frame:05}.png');begin=time.time();bpy.ops.render.render(write_still=True);animal=next((o for o in bpy.data.objects if o.name.startswith('Unified sculpt')),None);pose=None
 if animal:
  coords=np.empty(len(animal.data.vertices)*3,np.float32);animal.data.vertices.foreach_get('co',coords);pose=hashlib.sha256(coords.tobytes()).hexdigest()
 records.append({'frame':frame,'scene':kind,'render_seconds':round(time.time()-begin,2),'camera_matrix':[list(r) for r in s.camera.matrix_world],'animal_surface_sha256':pose});print('FRAME',frame,kind,records[-1]['render_seconds'],flush=True)
(OUT.parent/f'render-{a.start}-{a.end}.json').write_text(json.dumps({'frames':records,'width':a.width,'fps':30,'engine':'Cycles CPU','samples':a.samples,'source_frames_reused':False,'scene_image_plates':False,'locked_camera':a.lock_camera},indent=2))
# bpy wheel shutdown has a known occasional finalizer crash; all files flush before exit.
os._exit(0)
