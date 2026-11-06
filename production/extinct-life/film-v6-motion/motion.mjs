// Pure absolute-time motion. Mechanical checks are not biological validation.
export const clamp=x=>Math.max(0,Math.min(1,x));
export const smooth=x=>{x=clamp(x);return x*x*x*(x*(x*6-15)+10);};
export const SPEED=.24,PERIOD=3.7,DUTY=.68;
export function footState(t,phase=0){
 const q=((t/PERIOD+phase)%1+1)%1,stride=SPEED*PERIOD*DUTY;
 if(q<DUTY)return {z:-stride/2+SPEED*PERIOD*q,lift:0,pitch:0,stance:true,q};
 const u=(q-DUTY)/(1-DUTY),u2=u*u,u3=u2*u,m=SPEED*PERIOD*(1-DUTY);
 const z=(2*u3-3*u2+1)*stride/2+(u3-2*u2+u)*m+(-2*u3+3*u2)*-stride/2+(u3-u2)*m;
 return {z,lift:.23*Math.sin(Math.PI*u)**2,pitch:.13*Math.sin(Math.PI*u),stance:false,q};
}
export function mammalState(t){return {position:[-2,0,2.8-SPEED*t],rotation:0};}
export function flightState(t,start=5.55){
 const age=Math.max(0,t-start),flight=t>=start,dist=age<2?.35*age*age:1.4*(age-1),blend=smooth(age/.65);
 return {age,flight,blend,position:[4.3+.22*dist,-.08+3*smooth(age/4.8),.7-dist],retract:smooth((age-.35)/.8)};
}
