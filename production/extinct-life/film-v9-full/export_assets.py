"""Author small reusable GLBs from original organic sculpts; never render image plates.
Blender source V8 is used as an asset-authoring library, not as an old movie.
"""
from pathlib import Path
import sys,json,hashlib
R=Path.cwd();B=R/'production/extinct-life/film-v9-full';out=B/'native-meshes';out.mkdir(exist_ok=True)
source=(B.parent/'film-v8-premium/scene.py').read_text();sys.argv=[sys.argv[0]]
ns={'__name__':'asset_authoring'};exec(compile(source[:source.index('# The master remains unchanged')],'original_sculpt_library','exec'),ns)
bpy=ns['bpy'];ell=ns['ell'];tube=ns['tube'];material=ns['material'];setup=ns['setup']
records=[]
def save(kind):
 for o in list(bpy.data.objects):
  if o.type not in ['MESH','CURVE','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
 # A static exported coat is a material feature; no simulation caches or rendered plates.
 for o in list(bpy.data.objects):
  if o.type=='MESH':
   for mod in list(o.modifiers):
    if mod.type=='PARTICLE_SYSTEM':o.modifiers.remove(mod)
 for mat in bpy.data.materials:
  if mat.use_nodes:
   for node in mat.node_tree.nodes:
    if node.type=='BSDF_PRINCIPLED':
     for key in ['Base Color','Normal']:
      for link in list(node.inputs[key].links):mat.node_tree.links.remove(link)
     node.inputs['Base Color'].default_value=mat.diffuse_color
 bpy.ops.preferences.addon_enable(module='io_scene_gltf2')
 path=out/(kind+'.glb')
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_yup=True,export_apply=True,export_animations=False,export_cameras=False,export_lights=False,export_materials='EXPORT')
 records.append({'kind':kind,'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'original_authored':True})
def union(parts,name,mat,voxel=.035):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 mod=o.modifiers.new('Continuous organic union','REMESH');mod.mode='VOXEL';mod.voxel_size=voxel;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name)
 mod=o.modifiers.new('Anatomical relaxation','SMOOTH');mod.factor=.8;mod.iterations=4;bpy.ops.object.modifier_apply(modifier=mod.name)
 mod=o.modifiers.new('Sculpt refinement','SUBSURF');mod.levels=1
 return o
setup('forest');root,update=ns['mastodon']();update(3);save('mastodon')
setup('forest');fur=material('Reindeer coat',(.22,.17,.10),.86,scale=40,bump=.16);pale=material('Pale throat',(.48,.43,.32),.87,scale=55,bump=.12);dark=material('Hoof and eyes',(.025,.024,.019),.4,bump=0)
parts=[ell('Torso',(0,.15,1.12),(.37,.83,.43),fur),ell('Shoulder',(0,-.5,1.25),(.3,.43,.5),fur),ell('Neck',(0,-.72,1.5),(.22,.28,.54),fur),ell('Cranium',(0,-.97,1.96),(.19,.32,.26),fur),ell('Muzzle',(0,-1.2,1.83),(.14,.26,.15),fur)]
for x in [-.24,.24]:
 for y in [-.5,.65]:
  parts.extend([ell('Upper leg',(x,y,.76),(.095,.13,.41),fur),ell('Lower leg',(x,y,.30),(.06,.075,.31),fur)])
union(parts,'Unified reindeer',fur)
for side in [-1,1]:
 ell('Ear',(side*.25,-.87,2.14),(.19,.1,.065),fur)
 ell('Eye',(side*.17,-1.08,2.0),(.024,.035,.025),dark)
 tube('Antler',[(side*.11,-.89,2.13),(side*.22,-.73,2.5),(side*.32,-.87,2.9),(side*.44,-1.08,3.05)],[.035,.032,.018,.003],pale)
 for k in range(3):tube('Antler tine',[(side*(.17+k*.065),-.76,2.38+k*.16),(side*(.36+k*.09),-1.04,2.57+k*.19)],[.019,.003],pale)
 for y in [-.5,.65]:ell('Hoof',(side*.24,y-.025,.055),(.075,.12,.065),dark)
save('reindeer')
setup('forest');feather=material('Goose feather',(.34,.32,.25),.84,scale=60,bump=.12);dark=material('Goose eye and flight feathers',(.035,.04,.03),.7,bump=0);beak=material('Beak and feet',(.35,.25,.12),.64,bump=0)
parts=[ell('Body',(0,0,.37),(.23,.47,.27),feather),ell('Breast',(0,-.27,.46),(.18,.22,.23),feather),ell('Neck',(0,-.4,.72),(.075,.09,.31),feather),ell('Head',(0,-.48,.99),(.11,.16,.12),feather)]
union(parts,'Unified goose',feather,.023);ell('Beak',(0,-.66,.97),(.055,.13,.035),beak)
for side in [-1,1]:
 ell('Eye',(side*.101,-.54,1.01),(.012,.015,.014),dark)
 # Independent layered flight wings; rotation pivot at shoulder, not world origin.
 wing=ns['mesh']('Flight wing '+str(side),[(0,0,0),(side*.82,.1,0),(side*.96,-.18,-.05),(side*.47,-.42,-.02),(side*.12,-.3,-.02)],[(0,1,2,3,4)],feather);wing.location=(side*.17,-.1,.5);mod=wing.modifiers.new('Feather thickness','SOLIDIFY');mod.thickness=.018
 for j in range(6):
  f=ell('Primary feather',(side*(.38+j*.07),.12+j*.04,.48),(.055,.27,.018),dark);f.parent=wing;f.location-=wing.location
 ell('Foot',(side*.09,-.05,.055),(.065,.13,.025),beak)
save('goose')
setup('forest');coat=material('Hare winter coat',(.48,.46,.39),.88,scale=70,bump=.15);dark=material('Hare eyes',(.015,.019,.014),.2,bump=0)
parts=[ell('Body',(0,.08,.29),(.2,.35,.25),coat),ell('Head',(0,-.22,.48),(.15,.19,.17),coat),ell('Muzzle',(0,-.36,.44),(.09,.11,.08),coat)]
for side in [-1,1]:
 parts.extend([ell('Haunch',(side*.14,.2,.19),(.13,.2,.18),coat),ell('Foreleg',(side*.1,-.18,.13),(.06,.07,.14),coat),ell('Ear',(side*.075,-.18,.82),(.045,.07,.28),coat)])
union(parts,'Unified hare',coat,.018)
for side in [-1,1]:ell('Eye',(side*.13,-.31,.52),(.016,.022,.021),dark)
save('hare')
(out/'ASSETS.json').write_text(json.dumps({'licensing':'Original procedural sculpts authored for this production; no reference assets copied','assets':records,'anatomical_expert_validation':False},indent=2))
print(json.dumps(records,indent=2),flush=True);import os;os._exit(0)
