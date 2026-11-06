import fs from 'node:fs';import assert from 'node:assert/strict';
import {cameraPose,activeSequence} from './direction.mjs';
// Parse just the authored focus constants; no browser/texture download needed.
const source=fs.readFileSync(new URL('./worlds.mjs',import.meta.url),'utf8');
const match=source.match(/export const focus=({[\s\S]*?\n});/);assert(match);const focus=Function('return ('+match[1]+')')();
const s=JSON.parse(fs.readFileSync(new URL('./schedule.json',import.meta.url)));let cursor=0,maxStep=0,maxAcceleration=0;
assert.equal(s.sequences.length,18);assert.equal(new Set(s.sequences.map(x=>x.seed)).size,18);assert.equal(new Set(s.sequences.map(x=>x.design)).size,18);
const distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
for(const seq of s.sequences){
 assert.equal(seq.start_frame,cursor);assert(seq.end_frame>cursor);assert(seq.keys.length);cursor=seq.end_frame;
 if(seq.start_frame)assert(seq.blend_frames>=30,'A world switch needs a full-frame scale bridge, not a hard cut');
 let before=null,velocity=null;
 for(let f=seq.start_frame;f<seq.end_frame;f++){
  const pose=cameraPose(seq,focus,f);assert(pose.position.every(Number.isFinite));assert(pose.position[1]>=.22);
  if(before){maxStep=Math.max(maxStep,distance(pose.position,before));const v=pose.position.map((x,i)=>x-before[i]);if(velocity)maxAcceleration=Math.max(maxAcceleration,distance(v,velocity));velocity=v;}before=pose.position;
 }
}
assert.equal(cursor,s.total_frames);assert(maxStep<.45,'Camera teleports or whip moves');assert(maxAcceleration<.06,'Camera acceleration discontinuity');
let auditBoundaryJumps=0;
for(const chapter of s.chapters)for(const beat of chapter.shots.slice(1)){
 const f=chapter.start_frame+beat.start_frame,a=activeSequence(s,f-1),b=activeSequence(s,f);
 if(a.id===b.id){assert(distance(cameraPose(a,focus,f-1).position,cameraPose(b,focus,f).position)<.45);auditBoundaryJumps++;}
}
console.log(JSON.stringify({continuous_sequences:18,old_three_second_boundaries_without_camera_reset:auditBoundaryJumps,frames_evaluated:s.total_frames,max_camera_step_metres_per_frame:maxStep,max_acceleration_metres_per_frame_squared:maxAcceleration,unique_set_designs:18,unique_set_seeds:18,hard_world_cuts:0,note:'Mathematical continuity checks are not creative approval.'},null,2));
