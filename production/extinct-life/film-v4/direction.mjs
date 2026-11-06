// Pure deterministic camera mathematics, also used by frame-by-frame continuity tests.
export function smooth(x){x=Math.max(0,Math.min(1,x));return x*x*x*(x*(x*6-15)+10);}
const lerp=(a,b,t)=>a+(b-a)*t;
export function hermite(keys,t){
 if(keys.length===1)return [...keys[0].value];
 let i=0;while(i<keys.length-2&&t>keys[i+1].time)i++;
 const a=keys[i],b=keys[i+1],before=keys[Math.max(0,i-1)],after=keys[Math.min(keys.length-1,i+2)],span=b.time-a.time;
 const u=Math.max(0,Math.min(1,(t-a.time)/span)),u2=u*u,u3=u2*u;
 return a.value.map((v,k)=>{
  const m0=(b.value[k]-before.value[k])/Math.max(.001,b.time-before.time),m1=(after.value[k]-a.value[k])/Math.max(.001,after.time-a.time);
  return (2*u3-3*u2+1)*v+(u3-2*u2+u)*span*m0+(-2*u3+3*u2)*b.value[k]+(u3-u2)*span*m1;
 });
}
export function tracks(sequence,focus){
 const keys=sequence.keys.map(k=>({time:(k.frame-sequence.start_frame)/30,value:[...focus[k.mode].at,focus[k.mode].r]}));
 // An end key advances the dolly; do not stop or reset at the old beat windows.
 const last=keys.at(-1),end=(sequence.end_frame-sequence.start_frame)/30;
 if(last.time<end)keys.push({time:end,value:[...last.value.slice(0,3),last.value[3]*.93]});
 return keys;
}
export function cameraPose(sequence,focus,frame){
 const age=Math.max(0,(frame-sequence.start_frame)/30),values=hermite(tracks(sequence,focus),age);
 const target=values.slice(0,3);target[1]=Math.max(.12,target[1]);const radius=Math.max(.8,values[3]);
 const angle=.52+(sequence.seed%1000)/2600+age*.009;const elevation=['habit','coast','river'].includes(sequence.world)?.24:.27;
 const sign=['habit','coast','river'].includes(sequence.world)?-1:1;
 return {position:[target[0]+Math.sin(angle)*radius,Math.max(.22,target[1]+radius*elevation),target[2]+sign*Math.cos(angle)*radius],target,age};
}
export function activeSequence(schedule,frame){return schedule.sequences.find(s=>frame>=s.start_frame&&frame<s.end_frame)||schedule.sequences.at(-1);}
export function eventAt(sequence,frame){let current=sequence.keys[0],previous=current;for(const key of sequence.keys){if(key.frame>frame)break;previous=current;current=key;}return {current,previous,weight:smooth((frame-current.frame)/45)};}
