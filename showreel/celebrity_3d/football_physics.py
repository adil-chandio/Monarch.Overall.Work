"""Deterministic football blocking simulation for offline animation tests.

Metres, seconds, kilograms. Simple spherical ball and spherical foot proxy;
not a substitute for collision meshes, full angular dynamics, or a rigid-body solver.
The simulation is baked in fixed substeps so rendering frames out of order is safe.
"""
from dataclasses import dataclass
from math import sqrt, isfinite


def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(a,s): return tuple(x*s for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def length(v): return sqrt(dot(v,v))

@dataclass(frozen=True)
class Ball:
    position: tuple
    velocity: tuple = (0.,0.,0.)
    # Integrated yaw-free roll angle around an axis perpendicular to the
    # horizontal travel direction, as a visual approximation only.
    roll: float = 0.

@dataclass(frozen=True)
class Parameters:
    radius: float = .11
    mass: float = .43
    gravity: float = 9.81
    ground_restitution: float = .48
    rolling_friction: float = .12
    foot_radius: float = .09
    foot_restitution: float = .55
    effective_foot_mass: float = 2.5

    def __post_init__(self):
        values = (self.radius,self.mass,self.gravity,self.ground_restitution,
                  self.rolling_friction,self.foot_radius,self.foot_restitution,
                  self.effective_foot_mass)
        if not all(isfinite(v) for v in values): raise ValueError('parameters must be finite')
        if min(self.radius,self.mass,self.gravity,self.foot_radius,self.effective_foot_mass)<=0: raise ValueError('positive physical dimensions required')
        if self.rolling_friction<0 or not 0<=self.ground_restitution<=1 or not 0<=self.foot_restitution<=1: raise ValueError('invalid friction/restitution')


def step(ball, dt, p=Parameters(), foot=None, foot_velocity=(0.,0.,0.)):
    """Return (state, contacted). foot is proxy center at this time step.

    One-dimensional collision impulse along the contact normal. Ground contact
    is projected after integration; bounce is damped and tiny hops are stopped.
    """
    if not isfinite(dt) or dt<=0: raise ValueError('dt must be finite and positive')
    if len(ball.position)!=3 or len(ball.velocity)!=3 or not all(isfinite(v) for v in (*ball.position,*ball.velocity,ball.roll)):
        raise ValueError('ball state must be finite 3D values')
    x,v=ball.position,ball.velocity
    touched=False
    if foot is not None:
        if len(foot)!=3 or len(foot_velocity)!=3 or not all(isfinite(q) for q in (*foot,*foot_velocity)):
            raise ValueError('foot state must be finite 3D values')
        delta=sub(x,foot);dist=length(delta);minimum=p.radius+p.foot_radius
        if 0 < dist <= minimum:
            normal=mul(delta,1/dist)
            # Relative foot velocity along the normal must be closing.
            closing=dot(sub(foot_velocity,v),normal)
            if closing>0:
                impulse=(1+p.foot_restitution)*closing/(1/p.mass+1/p.effective_foot_mass)
                v=add(v,mul(normal,impulse/p.mass));touched=True
            x=add(foot,mul(normal,minimum))
    grounded = x[2] <= p.radius+1e-7 and v[2]<=0
    if grounded:
        speed=sqrt(v[0]**2+v[1]**2)
        if speed:
            new_speed=max(0.,speed-p.rolling_friction*p.gravity*dt)
            v=(v[0]*new_speed/speed,v[1]*new_speed/speed,0.)
        else: v=(0.,0.,0.)
    else: v=(v[0],v[1],v[2]-p.gravity*dt)
    x=add(x,mul(v,dt))
    if x[2]<p.radius:
        x=(x[0],x[1],p.radius)
        bounce=-v[2]*p.ground_restitution
        v=(v[0],v[1],bounce if bounce>.15 else 0.)
    roll=ball.roll+(sqrt(v[0]**2+v[1]**2)*dt/p.radius if x[2]<=p.radius+1e-7 else 0.)
    return Ball(x,v,roll),touched


def bake(initial, duration, foot_at=None, fps=24, substeps=20, p=Parameters()):
    """Bake fixed steps; foot_at(t) returns (position, velocity), or None.

    Return samples including t=0 plus impact times. This does not solve limb IK;
    use evaluated animated foot transforms as inputs and verify visual contact.
    """
    if not isfinite(duration) or duration<=0 or not isinstance(fps,int) or not isinstance(substeps,int) or fps<=0 or substeps<=0:
        raise ValueError('duration, fps and substeps must be positive')
    frames=round(duration*fps)
    if abs(frames-duration*fps)>1e-7: raise ValueError('duration must end on a frame boundary')
    dt=1/(fps*substeps);state=initial;out=[state];contacts=[]
    for i in range(frames*substeps):
        t=(i+1)*dt;sample=foot_at(t) if foot_at else None
        state,hit=step(state,dt,p,*(sample or (None,(0.,0.,0.))))
        if hit: contacts.append(t)
        if (i+1)%substeps==0:out.append(state)
    return out,contacts
