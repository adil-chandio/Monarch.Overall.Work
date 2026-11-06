import assert from 'node:assert/strict';
import {footState,mammalState,flightState,PERIOD,DUTY} from './motion.mjs';
for(const phase of [0,.25,.5,.75])for(let t=0;t<23;t+=.013){
 const a=footState(t,phase),b=footState(t+.0001,phase);assert(a.lift>=0&&a.lift<=.230001);assert(Number.isFinite(a.z));
 if(a.stance&&b.stance){const wa=mammalState(t).position[2]+a.z,wb=mammalState(t+.0001).position[2]+b.z;assert(Math.abs(wb-wa)<1e-8,'Planted foot slides in world space');assert.equal(a.lift,0);}
}
for(const boundary of [DUTY,1]){const a=footState(PERIOD*boundary-1e-5),b=footState(PERIOD*boundary+1e-5);assert(Math.abs(a.z-b.z)<.0001);assert(Math.abs(a.lift-b.lift)<.0001);}
let last=flightState(0),starts=0;for(let t=.01;t<23;t+=.01){const a=flightState(t);if(a.flight&&!last.flight)starts++;if(a.flight&&last.flight)assert(a.position[2]<=last.position[2]+1e-8,'Takeoff returns/restarts');assert(a.retract>=0&&a.retract<=1);last=a;}assert.equal(starts,1);
console.log('Planted-foot world-space locking, swing continuity, nonnegative lift, one takeoff and no flight return passed. These are mechanical checks, NOT anatomical/biological validation.');
