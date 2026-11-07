// Analytic illustrative trajectories in metres/seconds. Not a collision/rigid-body engine.
export const GRAVITY=9.81;
export const SOURCE=[-.118,-.077,-.45],DESTINATION=[-.118,-.25,-.45];
export const FALL_TIME=Math.sqrt(2*(SOURCE[1]-DESTINATION[1])/GRAVITY);
export const RESTITUTION=.15;
export function grainPose(age,side=0,z=0){
 if(age<0)return {visible:false,phase:'waiting',position:[SOURCE[0]+side,SOURCE[1],SOURCE[2]+z]};
 if(age<FALL_TIME)return {visible:true,phase:'fall',position:[SOURCE[0]+side,SOURCE[1]-.5*GRAVITY*age*age,SOURCE[2]+z]};
 const b=age-FALL_TIME,velocity=GRAVITY*FALL_TIME*RESTITUTION,duration=2*velocity/GRAVITY;
 const height=b<duration?Math.max(0,velocity*b-.5*GRAVITY*b*b):0;
 return {visible:age<.85,phase:b<duration?'bounce':'rest',position:[DESTINATION[0]+side,DESTINATION[1]+height,DESTINATION[2]+z]};
}
