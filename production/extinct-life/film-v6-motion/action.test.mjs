import assert from 'node:assert/strict';
import {CUES,channelX,bankHeight,riverLeaf,traceState,layerGrowth,depositSurface,depositionTrace,branchLeaf} from './action.mjs';
for(let t=0;t<26;t+=.021){
 const leaf=riverLeaf(t);assert(leaf.position.every(Number.isFinite));
 if(leaf.landed)assert(leaf.position[1]>.02);
 for(let i=0;i<36;i++){
  const a=traceState(t,i),[x,y,z]=a.position;assert(Math.abs(x-channelX(z))<.75);assert(y>0);assert(bankHeight(x,z)<-.3,'Trace submerged by opaque bank');
  if(t>0){const prev=traceState(Math.max(0,t-.021),i);assert(z<=prev.position[2]+1e-8,'Trace reverses/reset');}
 }
 for(let i=0;i<7;i++){const g=layerGrowth(t,i);assert(g>=0&&g<=1);}
 if(t>0)assert(depositSurface(t)>=depositSurface(Math.max(0,t-.021))-1e-10);
}
assert.equal(depositSurface(0),-.72);assert(Math.abs(depositSurface(5)-.98)<1e-9);
for(let i=0;i<30;i++){const a=depositionTrace(6,i);assert(a.landed);assert(Math.abs(a.position[1]-(-.335+(i%3)*.68))<1e-8);}
for(let i=0;i<2;i++){
 const release=CUES.branch_leaf_release+i*.12,a=branchLeaf(release-1e-7,i),b=branchLeaf(release+1e-7,i);assert(!a.visible&&b.visible);assert(Math.hypot(...a.position.map((p,k)=>p-b.position[k]))<1e-5);assert(branchLeaf(12,i).landed);assert.equal(branchLeaf(12,i).position[1],-.025);
}
console.log('Visible channel-bound traces, one-way advection, monotonic five-band deposition, distinct exposed cohorts, continuous leaf release/ground landing passed. Illustrative mechanics, NOT measured ancient physics.');
