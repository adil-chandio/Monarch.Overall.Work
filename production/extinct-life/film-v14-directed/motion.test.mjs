import assert from 'node:assert/strict';
import {actorClock,leafTrajectory,gooseTrajectory} from './motion.mjs';
import {footState,SPEED} from '../film-v6-motion/motion.mjs';
for(const t of [5,8,13,16]){const a=actorClock(t-1e-5,true),b=actorClock(t+1e-5,true);assert(Math.abs(a.clock-b.clock)<.00003);assert(Math.abs(a.weight-b.weight)<.00003);}
for(let t=8;t<13;t+=.1){const a=actorClock(t,true);assert.equal(a.clock,6.5);assert.equal(a.weight,0);}
for(const phase of [0,.25,.5,.75])for(let t=0;t<35;t+=.025){const a=footState(t,phase),b=footState(t+.001,phase);if(a.stance&&b.stance){const za=2.8-SPEED*t+a.z,zb=2.8-SPEED*(t+.001)+b.z;assert(Math.abs(za-zb)<1e-9,'Grounded foot must not skate while root advances');assert.equal(a.lift,0);}}
assert(!leafTrajectory(9.99).landed);assert(leafTrajectory(10.01).landed);assert(Math.abs(leafTrajectory(10).y+.02)<1e-6);
for(const t of [5.55,7.55,10.35]){const a=gooseTrajectory(t-1e-6),b=gooseTrajectory(t+1e-6);for(const k of ['x','y','z'])assert(Math.abs(a[k]-b[k])<1e-4);}
console.log('Continuous root velocity, stationary browse, planted stance, leaf contact and goose trajectory pass. Not biological expert validation.');
