import assert from 'node:assert/strict';
import {communitySubject,encounterBeat,directedView} from './direction.mjs';
const state={mastodon_position:[2.6,0,2],goose_position:[5.1,.1,-.4],hare_position:[-3.5,0,.8],deer_position:[-1.1,0,-.1]};
for(const [t,subject] of [[.33,'hare'],[1.33,'reindeer'],[2.33,'goose'],[3.16,'rodent'],[4.6,'mastodon'],[9,'plants'],[20,'ensemble']]){
 assert.equal(communitySubject(t),subject);const shot=directedView('community',t,state);assert.equal(shot.subject,subject);assert(shot.position.every(Number.isFinite));assert(shot.target.every(Number.isFinite));
}
assert.equal(encounterBeat(5.55),'takeoff');assert.equal(encounterBeat(25),'transport');
for(let t=4.5;t<11.5;t+=.1){const shot=directedView('encounter',t,state);assert.equal(shot.subject,'goose');assert(shot.position[0]>7,'Takeoff observed from the unobstructed opposite bank');}
for(const kind of ['community','encounter','closing'])for(let t=0;t<40;t+=.1){const s=directedView(kind,t,state);assert(s.position.every(Number.isFinite)&&s.target.every(Number.isFinite));assert(Math.hypot(...s.position.map((v,i)=>v-s.target[i]))>.25);}
assert.notDeepEqual(directedView('community',4,state).position,directedView('encounter',4,state).position);
console.log('Explicit species, takeoff, transport and closing shot contracts pass. Rendered actor-occlusion checks are separate.');
