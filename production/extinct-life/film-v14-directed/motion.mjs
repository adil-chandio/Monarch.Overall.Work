// Absolute-time kinematics, in metres and seconds. Illustrative, not rigid-body simulation.
export const clamp=x=>Math.max(0,Math.min(1,x));
export const smooth=x=>{x=clamp(x);return x*x*x*(x*(x*6-15)+10);};
const integral=u=>u**6-3*u**5+2.5*u**4;
export function actorClock(t,pause=false){
 if(!pause)return {clock:t,weight:1,browse:0};
 let clock,weight;if(t<5){clock=t;weight=1;}else if(t<8){const u=(t-5)/3;clock=5+3*(u-integral(u));weight=1-smooth(u);}else if(t<13){clock=6.5;weight=0;}else if(t<16){const u=(t-13)/3;clock=6.5+3*integral(u);weight=smooth(u);}else{clock=t-8;weight=1;}
 return {clock,weight,browse:smooth((t-7)/1.3)*(1-smooth((t-12)/2))};
}
export function leafTrajectory(t,release=8.3){const u=clamp((t-release)/1.7);return {x:2.895+1.205*smooth(u),y:.95*(1-u*u)-.02+.035*Math.sin(u*Math.PI*4)*Math.sin(u*Math.PI),z:-1.45-.25*u-Math.max(0,t-release-1.7)*.24,landed:t>=release+1.7};}
export function gooseTrajectory(t){const age=Math.max(0,t-5.55),distance=age<2?.35*age*age:1.4*(age-1);return {x:5.1+.1*distance,y:-.015+.95*smooth(age/.75)+1.85*smooth((age-.6)/4.2),z:-.4-distance,flight:smooth((age-.14)/.65)};}
