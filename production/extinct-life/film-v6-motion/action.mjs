import CUES from './action-cues.json' with {type:'json'};
import {clamp,smooth} from './motion.mjs';
export {CUES};
export const channelX=z=>-.25*Math.sin(z*.28);
export function bankHeight(x,z){const bank=smooth((Math.abs(x-channelX(z))-1.1)/1.4);return -.32+bank*(.52+.1*Math.sin(z*.7)+.06*Math.sin(x*1.2+z));}
export function riverLeaf(t){
 const fall=smooth(t/CUES.river_leaf_land),travel=clamp((t-CUES.river_leaf_land)/(CUES.river_leaf_arrive-CUES.river_leaf_land));
 const z=7.8-15.8*travel,x=channelX(z)-.7*(1-fall)+.17*Math.sin(travel*Math.PI*3)*Math.sin(travel*Math.PI);
 return {position:[x,.055+1.7*(1-fall),z],landed:t>=CUES.river_leaf_land,arrived:travel===1,travel};
}
export function traceState(t,i){
 const start=i*.21+(Math.sin(i*127.1)*43758.5453%1+1)%1*.14,age=t-start,u=clamp(age/15.8),z=7.6-15.6*u;
 return {visible:age>=0,arrived:u===1,stopTime:start+15.8,position:[channelX(z)+(.55*Math.sin(i*2.399)+.18*Math.sin(u*9+i))*(1-smooth((u-.87)/.13)),.055+.01*Math.sin(t*2+i)*(1-u),z],scale:.65+(i%4)*.1};
}
export function layerGrowth(t,i){return i<2?1:smooth((t-(i-2)*CUES.deposition_layer_interval)/CUES.deposition_layer_interval);}
export function depositSurface(t){let y=-.72;for(let i=2;i<7;i++)y+=.34*layerGrowth(t,i);return y;}
export function depositionTrace(t,i){
 const cohort=i%3,age=t-CUES.deposition_cohort_starts[cohort]-Math.floor(i/3)*.035,u=smooth(age/.9),target=-.38+cohort*.68;
 return {visible:age>=0,cohort,landed:age>=.9,position:[Math.sin(i*2.4)*2,3.1*(1-u)+(target+.045)*u,2.03]};
}
export function branchLeaf(t,i=0){
 const release=CUES.branch_leaf_release+i*.12,age=t-release,u=clamp(age/(CUES.branch_leaf_land-CUES.branch_leaf_release));
 const j=8+i,q=j*2.4,lx=Math.sin(q)*.26,ly=1.35+j*.115,lz=Math.cos(q)*.26,relative=.8-(2.8-.24*release);
 const contact=Math.max(0,.94*Math.sqrt(Math.max(0,1-(relative/1.6)**2))-.85),rz=-contact/1.85,rx=.012*Math.sin(release*1.4);
 const x0=-1.15+lx*Math.cos(rz)-ly*Math.sin(rz),ry=lx*Math.sin(rz)+ly*Math.cos(rz),y0=-.045+ry*Math.cos(rx)-lz*Math.sin(rx),z0=.8+ry*Math.sin(rx)+lz*Math.cos(rx);
 return {visible:age>=0,landed:u===1,position:[x0+.30*u+.12*Math.sin(u*Math.PI*3),y0*(1-u*u)-.025*u*u,z0-.48*u]};
}
