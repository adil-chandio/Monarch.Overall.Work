import assert from 'node:assert/strict';
import {grainPose,FALL_TIME,GRAVITY,SOURCE,DESTINATION,RESTITUTION} from './kinematics.mjs';
assert.equal(grainPose(-.1).visible,false);
assert.deepEqual(grainPose(0).position,SOURCE);
let previous=SOURCE[1];
for(let i=0;i<100;i++){
 const t=FALL_TIME*i/100,p=grainPose(t);
 assert.equal(p.phase,'fall');
 assert.ok(p.position[1]<=previous+1e-12);
 assert.ok(p.position[1]>=DESTINATION[1]);
 assert.ok(Math.abs(p.position[1]-(SOURCE[1]-.5*GRAVITY*t*t))<1e-12);
 previous=p.position[1];
}
for(const t of [FALL_TIME-1e-7,FALL_TIME+1e-7])assert.ok(Math.abs(grainPose(t).position[1]-DESTINATION[1])<1e-6);
const apex=FALL_TIME+FALL_TIME*RESTITUTION;
assert.ok(grainPose(apex).position[1]>DESTINATION[1]);
assert.ok(grainPose(apex).position[1]-DESTINATION[1]<.005);
assert.equal(grainPose(.5).phase,'rest');
assert.deepEqual(grainPose(.5).position,DESTINATION);
assert.equal(grainPose(1).visible,false);
assert.deepEqual(grainPose(.1),grainPose(.1));
console.log('Analytic gravity, impact continuity, restitution-limited bounce, rest and absolute-time determinism passed. Not rigid-body simulation validation.');
