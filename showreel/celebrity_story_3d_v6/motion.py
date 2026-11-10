"""Motion and contact helpers shared by the actors and the renderer.

Everything here reads the *evaluated* pose, so a hand placed by a clip and a prop
placed by these helpers always agree.  No IK constraints: Rocketbox skinning tears
when they are added, so props are fitted to the posed palm instead.
"""
import math
import bpy
from mathutils import Vector, Quaternion, Matrix

WALK_TRAVEL = Vector((0.056, 1.213, 0.0))   # metres per Walk_Rig cycle (28.8 f)
WALK_FRAMES = 28.8


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def smoothstep(a, b, x):
    if b == a:
        return 0.0 if x < a else 1.0
    return ease((x - a) / (b - a))


class WalkDriver:
    """Baked-root walk: the clip supplies the gait, we supply the distance.

    Rocketbox walk cycles travel 1.213 m per 28.8 frames along their own +Y, so
    the offset below is pure clip travel and steps never skate.
    """

    def __init__(self, speed=1.0):
        self.speed = speed
        self.per_frame = WALK_TRAVEL / WALK_FRAMES          # metres per frame
        self.frames_per_metre = WALK_FRAMES / WALK_TRAVEL.y

    def pose(self, t, speed=1.0):
        f = t * 24.0 * speed
        off = self.per_frame * f
        return f % WALK_FRAMES, off


def grasp_frame(rig, side='Right', depth=0.55):
    """Palm matrix of a posed hand: fingers close around objects at this point.

    Rocketbox hands point down their local +Y with the palm facing local -X, so
    the grip centre is a small offset along the palm normal, not the wrist.
    """
    pb = rig.pose.bones.get(f'mixamorig:{side}Hand')
    if pb is None:
        raise KeyError(f'no hand bone {side}')
    m = rig.matrix_world @ pb.matrix
    palm = m @ Vector((0.045 * depth, 0.012, 0.0))
    q = m.to_quaternion()
    return palm, q


def attach(obj, pos, quat):
    """Pin an object to a spot in world space with a fixed orientation."""
    obj.location = Vector(pos)
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = quat.copy()


def look_at(rig, target, weight=0.85, limit=math.radians(32)):
    """Aim the head with a clamped yaw/pitch, keeping the neck natural."""
    head = rig.pose.bones.get('mixamorig:Head')
    if head is None or target is None:
        return
    head.rotation_mode = 'QUATERNION'
    origin = (rig.matrix_world @ head.matrix).translation
    d = Vector(target) - origin
    if d.length < 1e-4:
        return
    local = (rig.matrix_world.to_quaternion().inverted() @ d).normalized()
    yaw = math.atan2(local.x, local.y)
    pitch = math.atan2(local.z, math.hypot(local.x, local.y))
    yaw = max(-limit, min(limit, yaw)) * weight
    pitch = max(-limit * .6, min(limit * .6, pitch)) * weight
    head.rotation_quaternion = Quaternion((0, 0, 1), -yaw) @ Quaternion((1, 0, 0), pitch)


# --------------------------------------------------------------------- hands
# Rest-pose curl baseline, measured once per rig, so repeated calls inside a
# frame loop do not accumulate (this bug made fingers close through the palm).
_REST = {}


def _rest_quat(rig, side, finger, i):
    key = (rig.name, side, finger, i)
    if key in _REST:
        return _REST[key]
    name = f'mixamorig:{side}Hand{finger}{i}' if finger else f'mixamorig:{side}Hand{i}'
    b = rig.data.bones.get(name)
    if b is None:
        return None
    _REST[key] = b.matrix_local.to_quaternion()
    return _REST[key]


def solve_thumb_axis(rig, side='Right'):
    """Thumb folds across the palm; pick the axis that closes it inward."""
    hand = rig.data.bones.get(f'mixamorig:{side}Hand')
    thumb = rig.data.bones.get(f'mixamorig:{side}HandThumb1')
    if hand is None or thumb is None:
        return (1, 0, 0)
    rel = hand.matrix_local.inverted() @ thumb.matrix_local
    t = rel.translation
    return Vector((0.15, -math.copysign(1.0, t.y) * .35, -1.0)).normalized()


def curl_hand(rig, side='Right', amount=1.0, thumb=True):
    """Close the fingers by a fraction of a natural fist, from the rest pose."""
    amount = max(0.0, min(1.0, amount))
    for finger in ('Index', 'Middle', 'Ring', 'Pinky'):
        for i in (1, 2, 3):
            pb = rig.pose.bones.get(f'mixamorig:{side}Hand{finger}{i}')
            if pb is None:
                continue
            rest = _rest_quat(rig, side, finger, i)
            pb.rotation_mode = 'QUATERNION'
            fold = Quaternion((1, 0, 0), math.radians(78 * amount * (1.0 if i > 1 else .75)))
            pb.rotation_quaternion = fold @ rest if rest else fold
    if not thumb:
        return
    axis = solve_thumb_axis(rig, side)
    for i in (1, 2, 3):
        pb = rig.pose.bones.get(f'mixamorig:{side}HandThumb{i}')
        if pb is None:
            continue
        rest = _rest_quat(rig, side, 'Thumb', i)
        pb.rotation_mode = 'QUATERNION'
        fold = Quaternion(axis, math.radians(46 * amount))
        pb.rotation_quaternion = fold @ rest if rest else fold


# ------------------------------------------------------------------ blinking
def blink_amount(t):
    """Roughly every 3.6 s, a fast 140 ms blink, never on the beat."""
    cycle = 3.6
    u = (t + 0.7) % cycle
    if u < 0.06 or u > 0.14:
        return 0.0
    return math.sin((u - 0.06) / 0.08 * math.pi) ** 1.5
