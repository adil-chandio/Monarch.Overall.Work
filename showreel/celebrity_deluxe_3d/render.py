"""An upgraded, still stylized Cycles production of the fictional story.

The ten established story cues and 3D character rigs are preserved.  New
physical set dressing, motivated shot coverage, a hand-attached phone and
revised dusk/night lighting improve the earlier reconstruction. No photos are
used for backgrounds. See ASSET_CREDITS.txt and README.md for limitations.
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import bpy
from mathutils import Matrix, Quaternion, Vector
from showreel.celebrity_cinematic_3d import render as cinema

base = cinema.base
old = cinema.old
FPS = cinema.FPS


def _to_xyzw(q):
    return (q.x, q.y, q.z, q.w)


def bone_position(actor, bone):
    p = actor.rig.pose.bones['mixamorig:' + bone]
    return actor.rig.matrix_world @ p.head


def curl_toward(actor, side, target, weight):
    """Bend visible finger segments toward a prop/other palm, without IK.

    The animation clip resets the finger channels first; we apply small world
    rotations about each actual joint head. This is still an approximation,
    not a collision-aware hand rig.
    """
    if weight <= 0:
        return
    rig = actor.rig
    target = Vector(target)
    for finger in ('Index', 'Middle', 'Ring', 'Pinky'):
        for segment, angle in ((1, .13), (2, .27)):
            a = rig.pose.bones.get(f'mixamorig:{side}Hand{finger}{segment}')
            b = rig.pose.bones.get(f'mixamorig:{side}Hand{finger}{segment+1}')
            if not a or not b:
                continue
            across = bone_position(actor, side+'HandIndex1') - bone_position(actor, side+'HandPinky1')
            if across.length < 1e-5:
                continue
            across.normalize()
            pivot = rig.matrix_world @ a.head
            tip = rig.matrix_world @ b.head
            tangent = across.cross(tip - pivot)
            sign = 1 if tangent.dot(target - tip) >= 0 else -1
            rotation = Quaternion(across, sign * angle * weight)
            transform = Matrix.Translation(pivot) @ rotation.to_matrix().to_4x4() @ Matrix.Translation(-pivot)
            a.matrix = rig.matrix_world.inverted() @ transform @ rig.matrix_world @ a.matrix
            bpy.context.view_layer.update()


class DeluxeRig(cinema.CinematicRig):
    def animate(self, proxy, base_pos, yaw, sit, walk, targets, smile, t):
        # Some source clips omit individual finger curves. Resetting them first
        # prevents our procedural curls accumulating as frames are rendered.
        for side in ('Left', 'Right'):
            for finger in ('Thumb', 'Index', 'Middle', 'Ring', 'Pinky'):
                for n in (1, 2, 3):
                    bone = self.rig.pose.bones.get(f'mixamorig:{side}Hand{finger}{n}')
                    if bone:
                        bone.matrix_basis.identity()
        super().animate(proxy, base_pos, yaw, sit, walk, targets, smile, t)


# premium.Actor resolves this name at construction time, including extras.
old.RigPuppet = DeluxeRig


def fabric_cover(material):
    """A UV-mapped, gently folded blanket rather than a single flat cuboid."""
    nx, ny = 32, 42
    vertices, faces = [], []
    for j in range(ny+1):
        y = -.35 + 1.35*j/ny
        for i in range(nx+1):
            x = -1.11 + 1.62*i/nx
            # Restrained, broad folds with the strongest falloff near the foot.
            broad = .008*math.sin((x+.3)*12 + y*1.3) * math.exp(-((y+.06)/.60)**2)
            fine = .003*math.sin(x*22-y*5) * math.exp(-((y-.25)/.72)**2)
            vertices.append((x, y, .602 + broad + fine))
    for j in range(ny):
        for i in range(nx):
            a = j*(nx+1)+i
            faces.append((a, a+1, a+nx+2, a+nx+1))
    mesh = bpy.data.meshes.new('woven duvet with folds')
    mesh.from_pydata(vertices, [], faces); mesh.update()
    uv = mesh.uv_layers.new(name='UVMap')
    for poly in mesh.polygons:
        poly.use_smooth = True
        for loop in poly.loop_indices:
            co = mesh.vertices[mesh.loops[loop].vertex_index].co
            uv.data[loop].uv = ((co.x+1.11)/1.62, (co.y+.35)/1.35)
    ob = bpy.data.objects.new('folded linen duvet', mesh)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(material)
    solid = ob.modifiers.new('stitched edge thickness', 'SOLIDIFY'); solid.thickness = .030
    return ob


def modeled_mug(material):
    """Create a hollow ceramic cup and open loop handle at real-world scale."""
    segments = 48
    # Radius and height profile: outside, rim, inside and a solid bottom.
    profile = [(0.,-.055),(.039,-.055),(.048,-.050),(.051,-.040),
               (.051,.047),(.049,.055),(.043,.055),(.042,.047),
               (.042,-.037),(.037,-.044),(0.,-.044)]
    vertices, faces = [], []
    for radius,z in profile:
        for i in range(segments):
            a=math.tau*i/segments
            vertices.append((radius*math.cos(a),radius*math.sin(a),z))
    for j in range(len(profile)-1):
        for i in range(segments):
            a=j*segments+i; b=j*segments+(i+1)%segments
            faces.append((a,b,b+segments,a+segments))
    mesh=bpy.data.meshes.new('hollow cup ceramic')
    mesh.from_pydata(vertices,[],faces); mesh.update()
    body=bpy.data.objects.new('ceramic coffee cup',mesh)
    bpy.context.scene.collection.objects.link(body)
    body.data.materials.append(material)
    for face in mesh.polygons:face.use_smooth=True
    # Elliptical torus in XZ; the interior is really open, not a solid oval.
    vertices,faces=[],[]
    around,tube=36,12
    for i in range(around):
        a=math.tau*i/around
        for j in range(tube):
            b=math.tau*j/tube
            vertices.append((.053+(.031+.008*math.cos(b))*math.cos(a),
                             .008*math.sin(b), .002+(.039+.008*math.cos(b))*math.sin(a)))
    for i in range(around):
        for j in range(tube):
            a=i*tube+j; b=((i+1)%around)*tube+j
            c=((i+1)%around)*tube+(j+1)%tube; d=i*tube+(j+1)%tube
            faces.append((a,b,c,d))
    mesh=bpy.data.meshes.new('open handle'); mesh.from_pydata(vertices,[],faces); mesh.update()
    handle=bpy.data.objects.new('open ceramic handle',mesh)
    bpy.context.scene.collection.objects.link(handle)
    handle.data.materials.append(material)
    for face in mesh.polygons:face.use_smooth=True
    return body, handle


def add_microtexture(material, scale=75, strength=.15, distance=.004):
    nodes, links = material.node_tree.nodes, material.node_tree.links
    bs = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    if bs.inputs['Normal'].is_linked:
        return
    tex = nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = scale
    tex.inputs['Detail'].default_value = 2
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = strength
    bump.inputs['Distance'].default_value = distance
    links.new(tex.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bs.inputs['Normal'])


class Film(cinema.Film):
    def reset(self, kind):
        if self.w is not None:
            # Shards that straddle a cut otherwise retain the previous set's
            # meshes, textures, armatures and Cycles cache until process exit.
            self.w.scene.render.use_persistent_data = False
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)
            bpy.ops.outliner.orphans_purge(do_recursive=True)
        super().reset(kind)
        sc = self.w.scene
        # More samples plus a tighter adaptive error threshold preserve fabric,
        # facades and hair better; OIDN still means motion can show some flicker.
        sc.cycles.adaptive_threshold = .025
        sc.cycles.denoising_prefilter = 'ACCURATE'
        sc.cycles.denoising_quality = 'HIGH'
        lights = {o.name: o for o in sc.objects if o.type == 'LIGHT'}
        changes = {
            'bedroom': {'Dawn window': 370, 'Bedside warmth': 180, 'Rim': 170, 'Bedside practical': 55},
            'kitchen': {'Morning key': 520, 'Warm bounce': 180, 'Back edge': 180},
            'street': {'Open sky': 760, 'Cool edge': 420},
            'car': {'Open sky': 620, 'Warm side': 220, 'Cool edge': 340, 'Cabin face fill': 100},
            'night': {'Window edge': 175, 'Quiet warm fill': 48, 'Face lift': 45,
                      'Warm apartment bounce': 45, 'City blue bounce': 130},
        }
        for name, energy in changes[kind].items():
            if name in lights:
                lights[name].data.energy = energy
        sc.view_settings.exposure = {'bedroom': -.88, 'kitchen': -.78, 'street': -.95,
                                     'car': -.90, 'night': -1.22}[kind]
        if kind == 'night':
            bg = sc.world.node_tree.nodes.get('Background')
            bg.inputs['Strength'].default_value = .11

    def dress_bedroom(self):
        super().dress_bedroom()
        w = self.w
        # Replace the perfectly flat cover and block-shaped pillows with a
        # modeled linen surface and CC0 scanned throw pillows.
        for ob in list(w.scene.objects):
            if ob.name.startswith('soft cushion') and (ob.location-Vector((-.30, .35, .59))).length < .015:
                ob.hide_render = True
        fabric_cover(self.mats['fabric'])
        # Two small scanned throw cushions sit behind the sleeping pillows.
        cinema.import_fit('pillow.glb', (-.30, 1.28, .76), (1.35, .54, .22))
        # Architectural paneling and a framed, abstract wall artwork.
        panel = cinema.paint('bedroom panel shadow', (.12, .16, .19), .72)
        canvas = cinema.paint('linen artwork', (.40, .38, .33), .9)
        for x in (-1.70, 1.75):
            cinema.box(w, (x, 2.275, 1.73), (.34, .025, .61), panel)
            cinema.box(w, (x, 2.242, 1.73), (.31, .008, .58), canvas)
            disk = w.oval((x-.09,2.228,1.91),(.13,.005,.13),(.16,.19,.20,1))
            stroke = cinema.box(w,(x+.035,2.226,1.57),(.20,.004,.012),self.brass)
            stroke.rotation_mode = 'XYZ'
            stroke.rotation_euler.y = -.30
            cinema.box(w,(x-.04,2.224,1.76),(.15,.004,.009),self.navy)
        # A screen that lies on the table before it is picked up.
        self.props['phone_lenses'] = []
        for dx, dz in ((-.020,.047), (.0,.047), (-.020,.027)):
            ob = w.oval((0,0,-20), (.0052,.003,.0052), (.012,.016,.019,1))
            self.props['phone_lenses'].append((ob, Vector((dx,.009,dz))))

    def dress_kitchen(self):
        super().dress_kitchen()
        w = self.w
        # Keep the original motion markers but replace the cylinder and solid
        # oval with a hollow cup, an open handle, and coffee below the rim.
        self.props['cup'].hide_render = True
        self.props['handle'].hide_render = True
        ceramic = cinema.paint('glazed ceramic', (.74,.72,.66), .26)
        self.props['mug_body'], self.props['mug_handle'] = modeled_mug(ceramic)
        # Recessed hardware and subtle grout vary the cabinet silhouette.
        for x in (-1.2, -.4, .4, 1.2):
            for z in (1.70, 2.10):
                cinema.box(w, (x, 1.805, z+.03), (.12, .008, .004), self.darkmetal)
        # Small cutting board and an under-cabinet light, placed off the action.
        board = cinema.paint('oiled cutting board', (.30,.19,.10), .6)
        cinema.soft_box(w, (-.85, .28, 1.003), (.24,.16,.013), board, .012)
        for x in (-2.12, 2.12):
            cinema.box(w, (x, 1.98, 1.25), (.02,.012,.47), self.brass)

    def dress_street(self):
        super().dress_street()
        w = self.w
        add_microtexture(bpy.data.materials['cinema:asphalt'], 110, .18, .004)
        # Extra background onlookers remain to the sides of the doorway and
        # never occupy the tracked hero's path.
        self.side_crowd = [old.Actor(w, (.28,.29,.36,1), False),
                           old.Actor(w, (.28,.29,.36,1), False)]
        # Panel frames and ledges add scale to the reverse-angle streetscape.
        for x in (-8.1, -5.4, -2.7, 0., 2.7, 5.4):
            cinema.box(w, (x, -11.09, .34), (1.15,.025,.06), self.darkmetal)
            for dx in (-1.10, 1.10):
                cinema.box(w, (x+dx, -11.08, 1.55), (.025,.03,1.20), self.darkmetal)
        # Street-level planting and slender safety bollards.
        for x in (-4.8, 4.8):
            cinema.cylinder(w, (x,-2.50,.32), .07,.64,self.darkmetal)
            cinema.cylinder(w, (x,-2.50,.62), .075,.035,self.brass)

    def dress_car(self):
        super().dress_car()
        w = self.w
        # Contrasting piping in the upholstered rear seat.
        for x in (-.14, .22, .56):
            cinema.box(w, (x,.365,1.08), (.003,.007,.26), self.cream)
        # A lightly reflective transparent pane and upper frame establish that
        # the moving foreground element is a vehicle door, not a railing.
        pane = cinema.paint('car window', (.16,.24,.29), .14, .05)
        pane.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value = .015
        self.props['door_glass'] = cinema.box(w, (0,0,-20), (.49,.006,.27), pane)
        self.props['door_window_top'] = cinema.box(w, (0,0,-20), (.51,.015,.012), self.darkmetal)
        self.props['door_window_end'] = cinema.box(w, (0,0,-20), (.014,.015,.27), self.darkmetal)
        self.props['door_window_end'].hide_render = True  # never cross the face

    def dress_night(self):
        before = set(self.w.objects)
        super().dress_night()
        w = self.w
        # Hide the former plain skyline and build layered towers with modeled
        # mullions, individual panes, ledges and a varied pattern of light.
        for ob in w.objects:
            if ob not in before and ob.type == 'MESH' and ob.location.y > 4.0:
                ob.hide_render = True
        for ob in w.objects:
            if any((ob.location-Vector(p)).length < .01 for p in
                   [(1.05,-.3,.37), (1.05,-.3,.72)]):
                ob.hide_render = True
        # A real table silhouette replaces the large featureless cube.
        cinema.soft_box(w, (1.05,-.30,.72), (.48,.40,.028), self.mats['wood'], .012)
        for x in (.66,1.44):
            for y in (-.60,.0):
                cinema.box(w, (x,y,.36), (.028,.028,.34), self.mats['wood'])
        cinema.box(w, (1.05,-.30,.17), (.40,.31,.018), self.mats['wood'])
        cinema.box(w, (1.27,-.48,.759), (.12,.08,.008), self.cream)
        # Deep-toned curtain panels and a narrow polished window ledge.
        curtain = cinema.paint('night curtains', (.095,.105,.12), .95)
        for x in (-1.46,1.46):
            cinema.soft_box(w, (x,1.79,1.83), (.12,.045,1.03), curtain, .025)
            for dx in (-.065,0,.065):
                cinema.box(w, (x+dx,1.735,1.83), (.005,.004,1.0), self.darkmetal)
        cinema.box(w, (0,1.77,.78), (1.48,.06,.025), self.darkmetal)
        tower_tones = ((.035,.060,.095),(.045,.075,.11),(.055,.082,.115),(.028,.048,.075))
        glow_warm = cinema.paint('night windows warm', (.68,.43,.18), .8, 0, 1.15)
        glow_cool = cinema.paint('night windows cool', (.24,.39,.56), .8, 0, .75)
        dark_window = cinema.paint('night windows unlit', (.025,.04,.06), .34, .12)
        for k,(x,y,half,height) in enumerate([(-9.7,13.8,1.05,8.0),(-7.5,12.4,.95,7.1),
                                             (-5.5,13.6,1.00,9.0),(-3.3,12.7,1.00,7.2),
                                             (-1.1,14.1,1.05,9.5),(1.15,12.2,1.,6.9),
                                             (3.4,13.2,1.,8.2),(5.6,12.1,1.,7.0)]):
            facade = cinema.paint('deluxe tower '+str(k), tower_tones[k%4], .72, .1, .35)
            cinema.box(w, (x,y,height/2), (half,.28,height/2), facade)
            front = y-.29
            for floor in range(1, int(height/.43)):
                z = floor*.43
                cinema.box(w,(x,front-.008,z-.18),(half*.96,.009,.009), self.darkmetal)
                for col in range(5):
                    px=x+(col-2)*half*.34
                    lit=(k*17+floor*11+col*7+floor*col*3)%11
                    mat = glow_warm if lit in (0,2,5,8) else glow_cool if lit in (3,9) else dark_window
                    cinema.box(w,(px,front-.020,z),(.075,.008,.13),mat)
            for col in (-2,-1,0,1,2):
                cinema.box(w,(x+col*half*.34,front-.014,height/2),(.008,.01,height/2-.12),self.darkmetal)
        old.add_area('Night table pool', (2.1,-.5,1.8), (1.05,-.3,.6), (1.,.56,.30), 55, 1.1)

    def update_bedroom(self, t):
        result = super().update_bedroom(t)
        w = self.w
        actor = self.hero.visible_actor
        wrist = bone_position(actor, 'LeftHand')
        finger = bone_position(actor, 'LeftHandMiddle1')
        lift = base.smooth((t-3.8)/1.3)
        grip = base.smooth((t-3.25)/.45)
        resting = Vector((.70,-.53,.795))
        held = wrist.lerp(finger, .80) + Vector((0,0,.035*lift))
        phone = resting.lerp(held, grip)
        # Screen up on the tabletop, then turned toward its reader.
        q = Quaternion((0,0,1), math.pi*lift) @ Quaternion((1,0,0), -.5*math.pi*(1-lift))
        w.move(self.props['phone'], phone, _to_xyzw(q))
        w.move(self.props['screen'], phone+q@Vector((0,-.011,0)), _to_xyzw(q))
        self.props['clock'].location = phone+q@Vector((0,-.014,.018))
        self.props['clock'].rotation_mode = 'QUATERNION'
        self.props['clock'].rotation_quaternion = q @ Quaternion((1,0,0), math.pi/2)
        for ob, offset in self.props['phone_lenses']:
            w.move(ob, phone+q@offset, _to_xyzw(q))
        curl_toward(actor, 'Left', phone, grip*.80)
        return result

    def update_kitchen(self, t):
        w=self.w; u=t-11.914; b=base.vec((-.05,.55,0))
        take=base.smooth((u-1.0)/.6)
        lift=base.smooth((u-1.8)/.65)*(1-base.smooth((u-3.25)/.8))
        put=base.smooth((u-4.1)/.55)
        # The cup's bottom rests on the counter, not halfway inside it.
        resting=base.vec((.31,.18,1.052))
        cup=base.blend(resting,base.vec((.12,.16,1.47)),lift)
        if put>0:
            cup=base.blend(cup,resting,put)
        hand=base.blend(b+base.vec((.27,-.03,.93)),cup+base.vec((.068,0,0)),take*(1-put))
        self.hero.pose(b,targets={1:hand},headyaw=-.12*lift)
        for key in ('cup','mug_body','mug_handle'):
            w.move(self.props[key],cup)
        w.move(self.props['coffee'],cup+base.vec((0,0,.043)))
        w.move(self.props['handle'],cup+base.vec((.06,0,.0)))
        return w.view((2.35,-4.1,2.42),(.08,.15,1.16))

    def update_street(self, t):
        result = super().update_street(t)
        for n, actor in enumerate(self.side_crowd):
            pos = base.vec(((-2.8 if n == 0 else 2.8), -1.45, 0))
            actor.pose(pos, yaw=math.pi+(.18 if n == 0 else -.18),
                       headyaw=.05*math.sin(t*1.6+n))
        weight = base.smooth((t-40.5)/.7)*(1-base.smooth((t-43.4)/.8))
        if weight:
            hero, fan = self.hero.visible_actor, self.fan.visible_actor
            hp, fp = hero.hand_position('Left'), fan.hand_position('Left')
            # Meet at the palms rather than merely touching the fingertips.
            delta = (hp-fp) * (.34*weight)
            fan.contact('Left', bone_position(fan,'LeftHand') + delta)
            hero.contact('Left', bone_position(hero,'LeftHand') - delta)
            bpy.context.view_layer.update()
            hp, fp = hero.hand_position('Left'), fan.hand_position('Left')
            curl_toward(hero, 'Left', fp, weight)
            curl_toward(fan, 'Left', hp, weight)
        return result

    def update_car(self, t):
        result = super().update_car(t)
        u = t - 46.293
        angle = -.65 * (1-base.smooth((u-.7)/1.9))
        pivot = base.vec((-.52,-.72,0))
        for name, offset in (('door_glass', (.59,0,1.47)),
                             ('door_window_top', (.59,0,1.75)),
                             ('door_window_end', (1.09,0,1.47))):
            self.w.move(self.props[name], pivot+base.rot(offset,angle), base.qz(angle))
        return result

    def cinematography(self, t):
        super().cinematography(t)
        # The previous wide kitchen shot let the island dominate the image.
        # Move to a close, motivated coffee shot after the hand reaches the mug.
        if 13.8 <= t < 17.237:
            u = base.smooth((t-13.8)/(17.237-13.8))
            eye = Vector((1.12,-2.20,1.72)).lerp(Vector((1.01,-2.08,1.69)), u)
            target = Vector((.02,.32,1.39))
            old.look_camera(self.w.scene, eye, target, 33.5, 5.0)
        elif 3.8 <= t < 11.914:
            # Slow lateral dolly with a restrained push, not a static crop.
            u = base.smooth((t-3.8)/(11.914-3.8))
            eye = Vector((1.42,-3.05,1.58)).lerp(Vector((1.20,-2.91,1.55)),u)
            target = Vector((-.04,-.58,.95))
            old.look_camera(self.w.scene, eye, target, 37, 5.6)
        elif 48.7 <= t < 50.544:
            # Once the car door has almost shut, cut inside for a quieter
            # portrait without the near-side frame crossing the face.
            u = base.smooth((t-48.7)/(50.544-48.7))
            eye = Vector((1.05,-.66,1.52)).lerp(Vector((.99,-.62,1.51)),u)
            old.look_camera(self.w.scene, eye, Vector((0,-.02,1.34)), 46, 5.0)
        elif t >= 50.544:
            u = base.smooth((t-50.544)/(60-50.544))
            eye = Vector((3.05,-4.50,2.35)).lerp(Vector((2.82,-4.28,2.25)),u)
            old.look_camera(self.w.scene, eye, Vector((.10,.60,1.25)), 42, 6.3)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--width', type=int, default=720)
    p.add_argument('--samples', type=int, default=16)
    p.add_argument('--start', type=float, default=0)
    p.add_argument('--end', type=float, default=60)
    p.add_argument('--stills', default='')
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if not 0 <= a.start < a.end <= 60 or a.width < 16 or a.samples < 1:
        raise SystemExit('invalid render settings')
    a.out.mkdir(parents=True, exist_ok=True)
    film = Film(a.width, a.samples)
    jobs = ([(round(float(s)*FPS), float(s), f'still_{float(s):05.2f}.png') for s in a.stills.split(',')]
            if a.stills else
            [(f, f/FPS, f'frame_{f:05d}.png') for f in range(math.ceil(a.start*FPS), math.ceil(a.end*FPS))])
    started = time.monotonic()
    print('JOBS', len(jobs), 'WIDTH', a.width, 'SAMPLES', a.samples, flush=True)
    for i, (frame, t, name) in enumerate(jobs):
        film.render_time(t, a.out/name)
        if i % 6 == 0 or i == len(jobs)-1:
            print('FRAME', frame, 'done', i+1, '/', len(jobs), 'elapsed', round(time.monotonic()-started, 1), flush=True)
    print('DONE', a.out, round(time.monotonic()-started, 1), flush=True)


if __name__ == '__main__':
    main()
