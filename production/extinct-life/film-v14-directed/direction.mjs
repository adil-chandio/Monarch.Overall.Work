// Explicit shot contracts. Pure, seekable and tested independently of the renderer.
import {smooth as S} from './motion.mjs';
export function communitySubject(t){return t<.94?'hare':t<1.91?'reindeer':t<2.74?'goose':t<3.71?'rodent':t<6.2?'mastodon':t<14?'plants':'ensemble';}
export function encounterBeat(t){return t<4.4?'approach':t<11.5?'takeoff':t<23?'reconstruction-limit':t<29?'transport':'uncertain-portrait';}
export function directedView(kind,t,state){
 const a=state.mastodon_position||[2.6,0,0],g=state.goose_position||[5.1,0,-.4],h=state.hare_position||[-.7,0,1],d=state.deer_position||[-1.1,0,0];
 if(kind==='community'){
  const subject=communitySubject(t);
  const shots={hare:{position:[-3.9,.60,-1.6],target:[h[0],.25,h[2]]},reindeer:{position:[-3.1,1.3,-4.0],target:[d[0],.9,d[2]]},goose:{position:[7.0,.70,-2.1],target:[g[0],g[1]+.3,g[2]]},rodent:{position:[-2.4,.38,-1.25],target:[-2.1,.15,.9]},mastodon:{position:[-.4,1.8,-4.5],target:[a[0],1.55,a[2]]},plants:{position:[-7.0,1.8,-2.0],target:[-2.8,2.1,-8.2]},ensemble:{position:[-5.6,2.1,-5.8],target:[.4,1.15,-.8]}};
  return {...shots[subject],subject,mode:'reconstruction-observer'};
 }
 if(kind==='encounter'){
  const beat=encounterBeat(t);
  if(beat==='takeoff')return {position:[8.2,1.2+g[1]*.2,2.7],target:[g[0],g[1]+.32,g[2]],subject:'goose',mode:'reconstruction-observer'};
  if(beat==='transport')return {position:[7.5,1.2,-2.0],target:[5.1,.05,-6.8-S((t-23)/6)*2],subject:'transport',mode:'conceptual-transport'};
  if(beat==='reconstruction-limit')return {position:[-6.5,1.8,-.8],target:[-2.8,1.9,-8.2],subject:'plants',mode:'reconstruction-observer'};
  return {position:[7.8,1.8,3.8],target:[a[0],1.4,a[2]],subject:'mastodon',mode:'reconstruction-observer'};
 }
 if(kind==='closing')return {position:[.15+S((t-9)/17)*1.5, .65+S((t-9)/17)*1.15,.9+S((t-9)/17)*4.8],target:[-.3*S((t-9)/17),.24+S((t-9)/17)*.75,-.3-S((t-9)/17)*4],subject:'sample',mode:'field'};
 return null;
}
