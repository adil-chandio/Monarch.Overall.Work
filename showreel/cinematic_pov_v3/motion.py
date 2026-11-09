"""Deterministic 2D blocking helpers; illustrative kinematics, not biomechanics."""
import math

def smooth(u):
 u=max(0.,min(1.,u));return u*u*(3.-2.*u)

def rolling(distance_time, initial_speed, deceleration):
 """Return rolling distance and speed under constant opposing deceleration.

 Units are arbitrary but must be consistent (e.g. pixels and seconds). The ball
 comes to rest without reversing. Instantaneous impact is a deliberate simplification.
 """
 if not all(math.isfinite(x) for x in (distance_time,initial_speed,deceleration)):
  raise ValueError('finite inputs required')
 if initial_speed<0 or deceleration<0:raise ValueError('speed and deceleration must be nonnegative')
 t=max(0.,distance_time)
 if deceleration==0:return initial_speed*t,initial_speed
 t=min(t,initial_speed/deceleration)
 return initial_speed*t-.5*deceleration*t*t,max(0.,initial_speed-deceleration*t)

def foot_target(x,origin,ground,scale,shift,stride=40.,stance=.6):
 """Plant foot in world space for stance; swing to next contact based on distance.

 phase advances with travelled distance, not time; if actor stops, feet stop.
 Forward travel only; this is a stylized 2D gait, not a gait physics solver.
 """
 if scale<=0 or stride<=0 or not 0<stance<1 or not all(math.isfinite(z) for z in (x,origin,ground,scale,shift,stride,stance)):
  raise ValueError('invalid gait parameters')
 d=max(0.,x-origin);step=stride*scale;q=d/step+shift;n=math.floor(q);phase=q-n
 anchor=origin+(n-shift+.65)*step
 if phase<stance:return (anchor,ground),True
 u=(phase-stance)/(1-stance)
 return (anchor+step*smooth(u),ground-11*scale*math.sin(math.pi*u)),False

def knee(hip,foot,upper,lower,side=1):
 """Two-link inverse kinematics; targets outside reach are projected to the boundary."""
 if upper<=0 or lower<=0:raise ValueError('positive limb lengths required')
 dx,dy=foot[0]-hip[0],foot[1]-hip[1];d=math.hypot(dx,dy)
 if d<1e-9:return (hip[0]+side*upper,hip[1])
 # Projection guards against numerical issues at singular configurations.
 dist=min(max(d,abs(upper-lower)+1e-7),upper+lower-1e-7)
 along=(upper*upper-lower*lower+dist*dist)/(2*dist)
 height=math.sqrt(max(0.,upper*upper-along*along));ux,uy=dx/d,dy/d
 return (hip[0]+ux*along-side*uy*height,hip[1]+uy*along+side*ux*height)
