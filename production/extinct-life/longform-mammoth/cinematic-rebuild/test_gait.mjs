import {test} from 'node:test';
import assert from 'node:assert/strict';
import {PARAMS, distanceAt, velocityAt, footAt} from './gait.mjs';

const tolerance=(a,b,eps)=>assert.ok(Math.abs(a-b)<eps,`${a} differs from ${b}`);
test('distance and start velocity are continuous and differentiable at ramp boundaries',()=>{
  const h=1e-5; tolerance(distanceAt(0),0,1e-12); tolerance(velocityAt(0),0,1e-12);
  for (const t of [.5,1,2,3]) tolerance((distanceAt(t+h)-distanceAt(t-h))/(2*h),velocityAt(t),1e-7);
  tolerance(velocityAt(PARAMS.rampSeconds),PARAMS.speed,1e-12);
});
test('planted feet do not slide horizontally over flat ground in the analytic model',()=>{
  const dt=1/300;
  for(let t=0;t<22;t+=dt)for(let i=0;i<4;i++){
    const a=footAt(t,i),b=footAt(t+dt,i);
    if(a.stance&&b.stance&&b.phase>=a.phase) {
      tolerance(a.distance+a.offset,b.distance+b.offset,1e-10);
      assert.equal(a.lift,0);assert.equal(b.lift,0);
    }
    assert.ok(a.lift>=0&&a.lift<=PARAMS.maxLift+1e-10);
  }
});
test('slow walk maintains at least three stance feet; touchdowns are lateral-sequence',()=>{
  let landed=[];
  for(let t=0;t<20;t+=1/300){
    let phases=Array.from({length:4},(_,i)=>footAt(t,i));
    assert.ok(phases.filter(p=>p.stance).length>=3);
    if(t>3){for(let i=0;i<4;i++){let prev=footAt(t-1/300,i);if(!prev.stance&&phases[i].stance)landed.push(i);}}
  }
  const expected=[2,0,3,1];
  for(let i=1;i<landed.length;i++)assert.equal(landed[i],expected[(expected.indexOf(landed[i-1])+1)%4]);
  assert.ok(landed.length>=8);
});
test('foot position and velocity remain continuous at stance/swing changes',()=>{
  // Check local position and derivative around both cycle boundaries at steady speed.
  const h=1e-5, cycle=PARAMS.stride/PARAMS.speed;
  for(const i of [0,1,2,3]) for(let t=3;t<12;t+=1/3000){
    const a=footAt(t-h,i),b=footAt(t,i),c=footAt(t+h,i);
    if(a.stance!==c.stance){
      assert.ok(Math.abs(c.offset-a.offset)<1e-4);
      tolerance((b.offset-a.offset)/h,(c.offset-b.offset)/h,0.001);
      assert.ok(c.lift<1e-7&&a.lift<1e-7);
    }
  }
  assert.ok(cycle>2 && cycle<2.5);
});
