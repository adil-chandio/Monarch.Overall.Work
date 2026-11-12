"""A rebuilt 60-second 3D celebrity preview, rendered with Bullet's TinyRenderer.

This is a new reconstruction, not a recovery of the lost Blender render. All
sets, props and actors are modeled geometry. Bodies and props move every frame;
no still photograph backgrounds are used. It uses the original ten v6 takes.
"""
from __future__ import annotations
import argparse, json, math, os, subprocess, tempfile, time, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import imageio_ffmpeg
import pybullet as p

HERE=Path(__file__).resolve().parent
V6=HERE.parent/'celebrity_story_3d_v6'
FPS=24
W,H=320,568
FF=imageio_ffmpeg.get_ffmpeg_exe()

# The source mesh is a smoothed unit sphere, scaled into each sculpted part.
def sphere_mesh(path):
    if path.exists(): return
    lines=[]; rings=18; sides=32
    for j in range(rings+1):
        v=math.pi*j/rings
        for i in range(sides):
            u=math.tau*i/sides
            x,y,z=math.sin(v)*math.cos(u),math.sin(v)*math.sin(u),math.cos(v)
            lines.append(f'v {x:.7f} {y:.7f} {z:.7f}\n')
    for j in range(rings):
        for i in range(sides):
            a=j*sides+i+1;b=j*sides+(i+1)%sides+1;c=(j+1)*sides+(i+1)%sides+1;d=(j+1)*sides+i+1
            lines.append(f'f {a} {b} {c}\nf {a} {c} {d}\n')
    path.write_text(''.join(lines))
MESH=Path(tempfile.gettempdir())/'celebrity-recovery-unit-sphere.obj'
sphere_mesh(MESH)

def vec(v): return np.array(v,dtype=float)
def smooth(x):
    x=max(0.,min(1.,x));return x*x*(3-2*x)
def blend(a,b,t): return vec(a)*(1-t)+vec(b)*t
def qz(yaw):return p.getQuaternionFromEuler((0,0,float(yaw)))
def rot(v,yaw):
    c,s=math.cos(yaw),math.sin(yaw); x,y,z=v
    return vec((c*x-s*y,s*x+c*y,z))
def align_z(d):
    d=vec(d); n=np.linalg.norm(d)
    if n<1e-9:return (0,0,0,1)
    x,y,z=d/n
    if z < -.999999:return (1,0,0,0)
    q=np.array((-y,x,0,1+z));q/=np.linalg.norm(q)
    return tuple(q)
def bone_joint(a,b,l1,l2,pole):
    a=vec(a);b=vec(b);d=b-a; dist=float(np.linalg.norm(d))
    if dist<1e-7:d=vec((0,0,-1));dist=1e-7
    d/=dist; dist=min(dist,l1+l2-1e-5)
    b=a+d*dist
    along=(l1*l1-l2*l2+dist*dist)/(2*dist)
    offset=math.sqrt(max(0,l1*l1-along*along))
    side=vec(pole)-d*np.dot(pole,d)
    n=np.linalg.norm(side)
    if n<1e-6:
        side=np.cross(d,(0,1,0));n=np.linalg.norm(side)
    side/=max(n,1e-8)
    return a+d*along+side*offset,b

class World:
    def __init__(self):
        self.cid=p.connect(p.DIRECT)
        p.setGravity(0,0,-9.8,physicsClientId=self.cid)
        self.cache={}
    def close(self):p.disconnect(self.cid)
    def shape(self,kind,dims,color):
        key=(kind,tuple(round(float(v),5) for v in dims),tuple(color))
        if key not in self.cache:
            if kind=='box':
                vis=p.createVisualShape(p.GEOM_BOX,halfExtents=dims,rgbaColor=color,physicsClientId=self.cid)
            elif kind=='ellipsoid':
                vis=p.createVisualShape(p.GEOM_MESH,fileName=str(MESH),meshScale=dims,rgbaColor=color,physicsClientId=self.cid)
            elif kind=='cylinder':
                vis=p.createVisualShape(p.GEOM_CYLINDER,radius=dims[0],length=dims[1],rgbaColor=color,physicsClientId=self.cid)
            else: raise ValueError(kind)
            self.cache[key]=vis
        return self.cache[key]
    def add(self,kind,dims,color,pos=(0,0,0),q=(0,0,0,1)):
        b=p.createMultiBody(baseMass=0,baseVisualShapeIndex=self.shape(kind,dims,color),
                            basePosition=pos,baseOrientation=q,physicsClientId=self.cid)
        return b
    def box(self,pos,dims,color): return self.add('box',dims,color,pos)
    def oval(self,pos,dims,color): return self.add('ellipsoid',dims,color,pos)
    def cylinder(self,pos,radius,length,color):return self.add('cylinder',(radius,length),color,pos)
    def move(self,obj,pos,q=(0,0,0,1)):
        p.resetBasePositionAndOrientation(obj,tuple(float(x) for x in pos),q,physicsClientId=self.cid)
    def view(self,eye,target,width=W,height=H,light=1.):
        view=p.computeViewMatrix(eye,target,(0,0,1))
        proj=p.computeProjectionMatrixFOV(42,width/height,.05,80)
        _,_,rgba,_,_=p.getCameraImage(width,height,view,proj,renderer=p.ER_TINY_RENDERER,
            flags=p.ER_NO_SEGMENTATION_MASK,shadow=1,lightDirection=(2,-5,8),
            lightColor=(light,light,light),lightAmbientCoeff=.62,lightDiffuseCoeff=.75,
            lightSpecularCoeff=.2,physicsClientId=self.cid)
        return np.asarray(rgba,dtype=np.uint8).reshape(height,width,4)[:,:,:3].copy()

# Muted colors, intentionally stylized rather than real-person likeness.
DARK=(.045,.055,.068,1); HAIR=(.045,.038,.035,1); SKIN=(.91,.90,.84,1)
BLACK=(.025,.025,.028,1); WHITE=(.93,.92,.88,1); BLUE=(.12,.38,.40,1)
PAVING=(.38,.41,.40,1); FLOOR=(.25,.22,.21,1); WALL=(.48,.46,.43,1)

class Actor:
    """Separate modeled limbs, with a two-bone joint at each elbow and knee."""
    def __init__(self,w,coat=DARK,beard=True):
        self.w=w;self.coat=coat;self.beard=beard
        o=lambda dims,col:w.oval((0,0,-20),dims,col)
        self.torso=o((.225,.13,.31),coat); self.hip=o((.18,.13,.13),coat)
        self.shirt=o((.073,.025,.14),WHITE) if beard else None
        self.neck=o((.07,.07,.08),SKIN)
        self.hair=o((.245,.195,.26),HAIR);self.face=o((.20,.12,.215),SKIN)
        self.fringe=o((.202,.040,.055),HAIR)
        self.ears=[o((.047,.038,.063),SKIN) for _ in range(2)]
        self.eyes=[o((.024,.022,.027),BLACK) for _ in range(2)]
        self.brows=[o((.054,.012,.012),HAIR) for _ in range(2)]
        self.nose=o((.033,.040,.033),SKIN)
        self.mouth=o((.065,.014,.013),HAIR)
        self.chin=o((.155,.039,.052),HAIR) if beard else None
        self.stache=[o((.044,.020,.013),HAIR) for _ in range(2)] if beard else []
        self.arms={};self.legs={}
        for side in (-1,1):
            self.arms[side]=(o((.057,.057,.155),coat),o((.049,.049,.14),coat),o((.065,.05,.07),WHITE))
            self.legs[side]=(o((.069,.069,.20),DARK),o((.057,.057,.195),DARK),o((.105,.16,.055),WHITE))
    def pose(self,base=(0,0,0),yaw=0,headyaw=0,sit=0,walk=0,
             targets=None,smile=0):
        w=self.w;base=vec(base); targets=targets or {}
        shift=-.25*sit
        def wp(pos):return base+rot(pos,yaw)
        def put(obj,pos,angle=yaw):w.move(obj,wp(pos),qz(angle))
        put(self.torso,(0,0,1.10+shift));put(self.hip,(0,.0,.81+shift));put(self.neck,(0,0,1.40+shift))
        if self.shirt:put(self.shirt,(0,-.128,1.20+shift))
        headbase=wp((0,0,1.64+shift));hy=yaw+headyaw
        def faceput(obj,offset):w.move(obj,headbase+rot(offset,hy),qz(hy))
        faceput(self.hair,(0,.025,.025));faceput(self.face,(0,-.105,0));faceput(self.fringe,(0,-.195,.160))
        for j,side in enumerate((-1,1)):
            faceput(self.ears[j],(side*.218,-.01,-.018))
            faceput(self.eyes[j],(side*.075,-.223,.035))
            faceput(self.brows[j],(side*.078,-.221,.095))
        faceput(self.nose,(0,-.238,-.015));faceput(self.mouth,(0,-.225,-.105+.012*smile))
        if self.chin: faceput(self.chin,(0,-.185,-.165))
        for j,side in enumerate((-1,1)):
            if self.stache:faceput(self.stache[j],(side*.045,-.225,-.078+.012*smile))
        for side in (-1,1):
            shoulder=wp((side*.215,0,1.29+shift))
            default=wp((side*.26,-.015,.93+shift))
            target=vec(targets.get(side,default))
            elbow,hand=bone_joint(shoulder,target,.30,.27,rot((side*.25,-.05,-1),yaw))
            upper,lower,palm=self.arms[side]
            w.move(upper,(shoulder+elbow)*.5,align_z(elbow-shoulder))
            w.move(lower,(elbow+hand)*.5,align_z(hand-elbow));w.move(palm,hand,qz(yaw))
            hip=wp((side*.105,0,.82+shift))
            swing=math.sin(walk+side*math.pi/2) if walk else 0
            lift=max(0,swing)*.11 if walk else 0
            foot=wp((side*.11,-.08-.17*swing-.22*sit,.11+lift))
            knee,ankle=bone_joint(hip,foot,.39,.37,rot((0,-1,-.1),yaw))
            upper,lower,shoe=self.legs[side]
            w.move(upper,(hip+knee)*.5,align_z(knee-hip));w.move(lower,(knee+ankle)*.5,align_z(ankle-knee))
            w.move(shoe,ankle+rot((0,-.04,-.025),yaw),qz(yaw))
        return {k:vec(v) for k,v in targets.items()}

class Film:
    def __init__(self): self.w=None;self.kind=None
    def reset(self,kind):
        if self.w:self.w.close()
        self.w=World();self.kind=kind;self.hero=Actor(self.w);self.props={}
        getattr(self,'build_'+kind)()
    def ground(self,color=FLOOR): self.w.box((0,0,-.09),(8,8,.08),color)
    def wall(self,pos,dims,col=WALL):return self.w.box(pos,dims,col)
    def build_bedroom(self):
        w=self.w;self.ground((.22,.20,.19,1))
        self.wall((0,2.4,3.0),(4,.07,3.1),(.31,.32,.34,1));self.wall((-3,0,3.0),(.07,3,3.1),(.25,.25,.27,1))
        w.box((-.3,.40,.37),(.85,1.12,.30),(.18,.14,.12,1));w.box((-.3,.40,.70),(.83,1.1,.10),(.66,.66,.63,1))
        w.box((-.3,1.1,.83),(.70,.32,.10),(.80,.80,.76,1));w.box((-.3,1.5,.95),(.88,.07,.58),(.17,.16,.16,1))
        w.box((.85,-.48,.38),(.34,.34,.38),(.32,.23,.17,1));w.box((.85,-.48,.77),(.37,.37,.035),(.49,.34,.23,1))
        w.cylinder((1.1,-.30,.90),.14,.035,(.82,.68,.39,1));w.cylinder((1.1,-.30,1.18),.022,.55,(.25,.21,.16,1));w.oval((1.1,-.30,1.43),(.18,.18,.12),(.86,.74,.47,1))
        self.props['phone']=w.box((.70,-.53,.825),(.055,.012,.105),(.03,.04,.06,1))
        self.props['screen']=w.box((.70,-.545,.825),(.047,.004,.09),(.30,.53,.62,1))
        self.props['handhold']=vec((.70,-.55,.83))
        # Slatted window makes the dawn location unmistakable.
        w.box((1.75,2.30,1.75),(.62,.035,.72),(.15,.22,.28,1))
        for x in (1.20,1.75,2.30):w.box((x,2.24,1.75),(.025,.035,.72),(.33,.31,.29,1))
    def build_kitchen(self):
        w=self.w;self.ground((.28,.27,.25,1));self.wall((0,2.1,3.0),(4,.07,3.1),(.62,.59,.54,1))
        w.box((0,-.15,.47),(1.6,.48,.46),(.27,.25,.23,1));w.box((0,-.15,.95),(1.62,.50,.045),(.72,.71,.66,1))
        for x in (-1.1,-.55,0,.55,1.1):w.box((x,-.645,.48),(.013,.01,.38),(.15,.14,.13,1))
        for x in (-1.2,-.4,.4,1.2):w.box((x,1.95,1.9),(.36,.11,.31),(.37,.34,.30,1))
        self.props['cup']=w.cylinder((.55,-.24,1.04),.085,.17,WHITE)
        self.props['coffee']=w.cylinder((.55,-.24,1.13),.069,.005,(.13,.07,.04,1))
        self.props['handle']=w.oval((.65,-.24,1.06),(.07,.035,.075),WHITE)
        w.box((-1.1,-.12,1.05),(.23,.24,.08),(.12,.14,.15,1))
    def build_street(self):
        w=self.w;self.ground(PAVING)
        self.wall((0,6,3),(12,.06,3.2),(.45,.53,.58,1))
        # Facade and doorway, rail and the approaching character share one scene.
        self.wall((-1.35,1.75,3.0),(1.35,.13,3.1),(.46,.42,.37,1));self.wall((1.35,1.75,3.0),(.85,.13,3.1),(.46,.42,.37,1))
        self.wall((0,1.75,3.75),(1.05,.13,1.5),(.46,.42,.37,1))
        w.box((0,1.83,1.18),(.83,.04,1.18),(.12,.15,.17,1))
        self.props['door']=w.box((0,1.67,1.18),(.80,.045,1.18),(.16,.24,.27,1))
        self.props['knob']=w.oval((.60,1.60,1.1),(.035,.03,.035),(.78,.62,.25,1))
        for x in (-2,-1,0,1,2):w.cylinder((x,-.57,.52),.035,1.04,(.34,.36,.37,1))
        w.box((0,-.57,.99),(2.15,.027,.028),(.63,.66,.65,1));w.box((0,-.57,.48),(2.15,.023,.023),(.54,.57,.57,1))
        for x in np.arange(-1.8,2,.25):w.box((float(x),-.57,.73),(.012,.018,.24),(.50,.53,.53,1))
        self.fan=Actor(w,BLUE,False);self.press=Actor(w,(.24,.27,.32,1),False)
        self.props['camera']=w.box((-.95,-1.08,1.35),(.11,.07,.08),(.055,.055,.06,1))
        self.props['flash']=w.oval((-20,-20,-20),(.065,.065,.065),WHITE)
    def build_car(self):
        w=self.w;self.ground((.31,.33,.33,1));
        self.wall((0,6,3),(12,.06,3.2),(.40,.49,.54,1))
        # Cutaway cabin: the near-side hinged door is animated separately.
        w.box((0,0,.28),(1.65,.73,.25),(.09,.11,.13,1));w.box((-1.32,0,.57),(.36,.72,.18),(.10,.12,.14,1))
        w.box((1.40,0,.62),(.25,.72,.24),(.10,.12,.14,1))
        w.box((.16,.0,1.95),(1.03,.68,.06),(.12,.14,.16,1))
        for x in (-.80,1.1):
            for y in (-.58,.58):w.box((x,y,1.30),(.045,.045,.62),(.12,.14,.16,1))
        for x in (-1.0,1.0):
            for y in (-.73,.73):
                tire=w.cylinder((x,y,.29),.25,.13,BLACK);w.move(tire,(x,y,.29),p.getQuaternionFromEuler((math.pi/2,0,0)))
        self.props['door']=w.box((0,-.75,.69),(.59,.055,.39),(.12,.16,.19,1))
        self.props['door_top']=w.box((0,-.75,1.18),(.59,.035,.035),(.15,.19,.21,1))
        self.props['door_pillar']=w.box((0,-.75,1.02),(.035,.035,.18),(.15,.19,.21,1))
        w.box((.2,.12,.70),(.38,.24,.12),(.15,.13,.13,1))
    def build_night(self):
        w=self.w;self.ground((.15,.15,.16,1));self.wall((0,2,3.0),(8,.09,3.1),(.16,.18,.21,1))
        # Glass and skyline are all physical, untextured objects.
        w.box((0,1.88,1.8),(1.50,.025,1.05),(.055,.11,.16,1))
        for x in (-1.48,-.50,.50,1.48):w.box((x,1.83,1.8),(.035,.03,1.06),(.25,.27,.29,1))
        w.box((0,1.82,1.17),(1.5,.03,.035),(.25,.27,.29,1))
        for x,z,h in ((-1.2,1.1,.38),(-.86,1.0,.47),(-.4,1.1,.36),(.2,1.,.48),(.75,1.05,.42),(1.16,1.08,.39)):
            w.box((x,1.79,z),(.17,.02,h),(.09,.13,.17,1))
            for dz in (-.18,0,.18): w.box((x,1.755,z+dz),(.03,.008,.03),(.60,.71,.70,1))
        w.box((1.05,-.3,.37),(.45,.38,.34),(.23,.19,.17,1));w.box((1.05,-.3,.72),(.48,.40,.03),(.39,.32,.26,1))
        self.props['phone']=w.box((1.03,-.30,.78),(.055,.012,.105),(.03,.04,.05,1))
    def render(self,t):
        if t<11.914:kind='bedroom'
        elif t<17.237:kind='kitchen'
        elif t<46.293:kind='street'
        elif t<50.544:kind='car'
        else:kind='night'
        if kind!=self.kind:self.reset(kind)
        return getattr(self,'update_'+kind)(t)
    def update_bedroom(self,t):
        w=self.w; base=vec((-.24,-.63,0));s=smooth((t-2.0)/1.4); lift=smooth((t-3.8)/1.3)
        resting=base+vec((.26,-.05,.83-.25));table=self.props['handhold'];read=base+vec((.21,-.30,1.27-.25))
        target=blend(blend(resting,table,s),read,lift)
        # Take the phone, look down at it, and make a second hand tap.
        self.hero.pose(base,sit=1,headyaw=-.15*lift,targets={1:target,-1:blend(base+vec((-.26,-.03,.68)),target+vec((-.10,-.02,.02)),smooth((t-6.4)/1.0)*(1-smooth((t-8.5)/.8)))})
        phone=blend(vec((.70,-.53,.83)),target+vec((.02,-.025,.08)),s)
        w.move(self.props['phone'],phone);w.move(self.props['screen'],phone+vec((0,-.016,0)))
        return w.view((2.4,-4.0,2.35),(.10,-.1,1.05))
    def update_kitchen(self,t):
        w=self.w;u=t-11.914;base=vec((-.05,.55,0));take=smooth((u-1.0)/.6);lift=smooth((u-1.8)/.65)*(1-smooth((u-3.25)/.8));put=smooth((u-4.1)/.55)
        cup=blend(vec((.55,-.24,1.04)),vec((.17,.18,1.38)),lift)
        if put>0:cup=blend(cup,vec((.55,-.24,1.04)),put)
        for key,delta in (('cup',(0,0,0)),('coffee',(0,0,.09)),('handle',(.10,0,.02))): w.move(self.props[key],cup+vec(delta))
        hand=blend(base+vec((.27,-.03,.93)),cup+vec((.09,0,0)),take*(1-put))
        self.hero.pose(base,targets={1:hand},headyaw=-.12*lift)
        return w.view((2.35,-4.1,2.42),(.08,.15,1.16))
    def update_street(self,t):
        w=self.w
        door=smooth((t-22.9)/1.2)*1.25; pivot=vec((-.8,1.67,0))
        def doorpos(local):return pivot+rot(local,door)
        w.move(self.props['door'],doorpos((.8,0,1.18)),qz(door));w.move(self.props['knob'],doorpos((1.4,-.07,1.10)))
        emerge=smooth((t-23.7)/4.1);walkphase=(t-23.7)*7 if 23.7<t<28.4 else 0
        base=blend((0,2.1,0),(-.12,-.24,0),emerge)
        close=smooth((t-35.0)/3.3);base=blend(base,(-.12,-.30,0),close)
        reach=smooth((t-40.0)/1.2)*(1-smooth((t-43.5)/1.1));mid=vec((.36,-.55,1.09))
        arm=blend(base+vec((.26,-.03,.93)),mid,reach)
        self.hero.pose(base,walk=walkphase,targets={1:arm},smile=smooth((t-30.8)/1.0)*(1-smooth((t-34.7)/.3)))
        fanbase=vec((.77,-1.00,0));fanhand=blend(fanbase+vec((-.26,.02,.95)),mid,reach)
        # Fan faces the celebrity across the rail and waves before he arrives.
        if 17.237<=t<23: fanhand=fanbase+vec((-.34,.05,1.13+.11*math.sin((t-17)*3)))
        self.fan.pose(fanbase,yaw=math.pi-.3,targets={1:fanhand},headyaw=.05*math.sin(t*2))
        pressbase=vec((-1.85,-1.13,0));presshand=pressbase+vec((.15,.12,1.23))
        self.press.pose(pressbase,yaw=math.pi,targets={-1:presshand})
        w.move(self.props['camera'],pressbase+vec((.04,.10,1.30)))
        flash=any(abs(t-x)<.08 for x in (30.45,31.27,32.05,32.88,33.53,34.15))
        w.move(self.props['flash'],pressbase+vec((.04,.18,1.31)) if flash else (-20,-20,-20))
        if t<23:
            return w.view((-2.8,-4.8,2.30),(.48,-.35,1.08))
        if t<34.793:
            return w.view((-2.8,-4.5,2.20),(.28,-.10,1.15),light=1.25 if flash else 1.)
        return w.view((-3.1,-4.4,2.15),(.31,-.52,1.10))
    def update_car(self,t):
        w=self.w;u=t-46.293;angle=-1.08*(1-smooth((u-.7)/1.9));pivot=vec((-.52,-.72,0))
        center=pivot+rot((.59,0,.69),angle)
        w.move(self.props['door'],center,qz(angle));w.move(self.props['door_top'],pivot+rot((.59,0,1.18),angle),qz(angle));w.move(self.props['door_pillar'],pivot+rot((1.15,0,1.02),angle),qz(angle))
        base=vec((.0,-.02,.20));pull=smooth((u-.0)/.5)*(1-smooth((u-2.2)/.5))
        target=blend(base+vec((.25,-.1,.72)),pivot+rot((.65,.05,.88),angle),pull)
        self.hero.pose(base,sit=1,targets={1:target})
        return w.view((3.0,-5.0,1.85),(.05,0,1.08))
    def update_night(self,t):
        w=self.w;u=t-50.544;move=smooth((u-1.5)/4.2);angle=math.pi*smooth((u-1.3)/1.7)
        base=blend((.55,-.4,0),(.05,.75,0),move);put=smooth((u-.2)/1.15)
        hand=blend(base+rot((.27,-.1,1.04),angle),vec((1.03,-.30,.78)),(1-put)*.65)
        self.hero.pose(base,yaw=angle,walk=(u-1.5)*5.5 if 1.5<u<5.7 else 0,targets={1:hand},headyaw=.20*smooth((u-7)/1.1))
        phone=blend(hand+vec((0,-.02,.04)),vec((1.03,-.30,.77)),put)
        w.move(self.props['phone'],phone,p.getQuaternionFromEuler((math.pi/2*put,0,0)))
        return w.view((3.5,-5.0,2.7),(.12,.35,1.2),light=.72)

CAPTIONS=[
 ['At five forty in the morning,\\Nthe city is still asleep.','His phone is already awake.'],
 ['Three missed calls.\\NTwo shoot days.','One hour before the car arrives.'],
 ['So he does what he always does.\\NCoffee first.','Everything else can wait a minute.'],
 ['By eight, the street outside\\Nhis building has changed.','They know the car.\\NThey know the windows.'],
 ['The door opens, and the noise\\Nhits him all at once.','His name, from every direction.'],
 ['Then the flashes start,\\Nand the smile is not fake.','It is just practiced.'],
 ['One girl at the barrier\\Nis not holding a phone.','She is shaking.\\NHe stops walking.'],
 ['He reaches over the barrier,\\Nand for a second he is not a headline.','He is just someone who listened.'],
 ['Then the car door closes,\\Nand the street goes quiet again.'],
 ['Hours later, the apartment is dark.\\NHe stands at the glass,','the phone face down behind him.\\NNobody is watching.']]
SPLITS=(4.08,2.50,3.17,3.24,3.91,3.32,2.88,4.07,None,3.89)
def ass_time(x):
    cs=round(x*100);return f'{cs//360000}:{(cs//6000)%60:02d}:{(cs//100)%60:02d}.{cs%100:02d}'
def captions(cues,path):
    header='''[Script Info]\nScriptType: v4.00+\nPlayResX: 320\nPlayResY: 568\nWrapStyle: 0\nScaledBorderAndShadow: yes\n[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\nStyle: Caption,DejaVu Sans,15,&H00FFFFFF,&H0000FFFF,&H0011171A,&H80000000,-1,0,0,0,100,100,0,0,1,2.2,0.7,2,18,18,30,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
    lines=[]
    for cue,parts,split in zip(cues,CAPTIONS,SPLITS):
        cur=cue['start']; ends=[cue['start']+split,cue['start']+cue['duration']] if split else [cue['start']+cue['duration']]
        for txt,end in zip(parts,ends):
            lines.append(f'Dialogue: 0,{ass_time(cur)},{ass_time(end)},Caption,,0,0,0,,{txt}')
            cur=end
    path.write_text(header+'\n'.join(lines)+'\n')

def audio(cues,path):
    sr=48000;n=60*sr; mix=np.zeros(n,np.float32)
    for i,cue in enumerate(cues,1):
        with wave.open(str(V6/'trimmed'/f'{i:02d}.wav'),'rb') as f:
            assert f.getsampwidth()==2 and f.getnchannels()==1
            hz=f.getframerate(); x=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float32)/32768
        idx=np.arange(round(len(x)*sr/hz))*hz/sr
        x=np.interp(idx,np.arange(len(x)),x).astype(np.float32)
        at=round(cue['start']*sr);mix[at:min(n,at+len(x))]+=.93*x[:max(0,n-at)]
    # Original synthesized, quiet chord bed and restrained notes.
    music=np.zeros(n,np.float32)
    chords=[(0,12,(146.83,174.61,220)),(12,23,(116.54,174.61,233.08)),(23,35,(130.81,174.61,220)),(35,47,(116.54,146.83,233.08)),(47,60,(146.83,174.61,220))]
    for start,end,notes in chords:
        tt=np.arange((end-start)*sr,dtype=np.float32)/sr;env=np.minimum(np.clip(tt/1.5,0,1),np.clip((end-start-tt)/1.5,0,1))
        for f in notes: music[start*sr:end*sr]+=.0035*np.sin(2*np.pi*f*tt)*env
    for at,f in ((1.2,293.66),(3.5,349.23),(6.6,440),(9.5,392),(12.5,349.23),(15,293.66),(19,233.08),(22.8,293.08),(26.2,349.23),(30.3,392),(33.3,440),(36.2,349),(39,293.66),(42.5,349),(45.8,440),(49.3,293.66),(52.1,220),(55,293.66),(57.2,349.23)):
        tt=np.arange(sr*2,dtype=np.float32)/sr;x=.012*np.sin(2*np.pi*f*tt)*np.exp(-2*tt)*(1-np.exp(-tt*38))
        k=round(at*sr);m=min(len(x),n-k);music[k:k+m]+=x[:m]
    mix+=music
    # Shutter and quiet footstep transients; no invented spoken crowd.
    rng=np.random.default_rng(315)
    for at in (24.8,25.8,26.8,27.8,35.5,36.5,37.5,53.4,54.4,55.4):
        tt=np.arange(int(.14*sr),dtype=np.float32)/sr;k=round(at*sr)
        mix[k:k+len(tt)]+=.011*np.sin(2*np.pi*90*tt)*np.exp(-tt*24)
    for at in (30.45,31.27,32.05,32.88,33.53,34.15):
        tt=np.arange(int(.10*sr),dtype=np.float32)/sr;k=round(at*sr)
        mix[k:k+len(tt)]+=.015*rng.standard_normal(len(tt)).astype(np.float32)*np.exp(-tt*75)
    peak=float(np.max(np.abs(mix)))
    if peak>.95:mix*=.95/peak
    pcm=(np.clip(mix,-1,1)*32767).astype('<i2')
    with wave.open(str(path),'wb') as out:out.setnchannels(1);out.setsampwidth(2);out.setframerate(sr);out.writeframes(pcm.tobytes())
    print('audio peak',round(peak,4),'duration',len(mix)/sr,flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stills',default='');ap.add_argument('--out',type=Path,default=Path('deliverables/celebrity-rebuilt-3d-preview.mp4'));ap.add_argument('--quality',type=int,default=20);a=ap.parse_args()
    film=Film()
    if a.stills:
        root=Path('/home/user/celebrity-recovery-stills');root.mkdir(exist_ok=True)
        for t in [float(x) for x in a.stills.split(',')]:
            f=root/f'still_{t:05.2f}.png';Image.fromarray(film.render(t)).save(f);print('still',f,flush=True)
        if film.w:film.w.close()
        return
    a.out.parent.mkdir(exist_ok=True,parents=True)
    with tempfile.TemporaryDirectory(prefix='celebrity-rebuild-') as td:
        td=Path(td);clean=td/'picture.mp4';ass=td/'captions.ass';wav=td/'mix.wav'
        cmd=[FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf',str(a.quality),'-pix_fmt','yuv420p',str(clean)]
        enc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        started=time.monotonic()
        try:
            for i in range(60*FPS):
                enc.stdin.write(film.render(i/FPS).tobytes())
                if i%120==0: print(f'frame {i}/1440 elapsed {time.monotonic()-started:.1f}s',flush=True)
        finally:
            enc.stdin.close()
            if film.w:film.w.close()
        if enc.wait()!=0:raise RuntimeError('picture encoding failed')
        cues=json.loads((V6/'script.json').read_text());audio(cues,wav);captions(cues,ass)
        vf=f'fade=t=in:st=0:d=0.3,fade=t=out:st=59.45:d=0.55,ass={ass}'
        subprocess.run([FF,'-y','-v','error','-i',str(clean),'-i',str(wav),'-vf',vf,'-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-t','60',str(a.out)],check=True)
        subprocess.run([FF,'-v','error','-i',str(a.out),'-f','null','-'],check=True)
    print('READY',a.out,a.out.stat().st_size,'bytes elapsed',round(time.monotonic()-started,1),flush=True)

if __name__=='__main__':main()
