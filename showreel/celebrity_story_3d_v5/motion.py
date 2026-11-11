"""Small, deterministic timing helpers; not a full physics simulation."""
import math
WALK_DURATION=1.2
ROOT_PER_CYCLE=1.2127
WALK_RATE=.38

def walk(t,rate=WALK_RATE):
 if t<0 or rate<=0:raise ValueError('walk time must be nonnegative and rate positive')
 u=t*rate;cycle=math.floor(u/WALK_DURATION)
 return (u%WALK_DURATION)*24, .6-cycle*ROOT_PER_CYCLE

def blink(t):
 q=(t+.3)%4.6
 return max(0,1-abs(q-.14)/.14)
