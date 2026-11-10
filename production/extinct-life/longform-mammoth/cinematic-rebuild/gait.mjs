// Deterministic kinematic approximation for a slow proboscidean walk.
// Not a physics simulation or a measurement of extinct mammoth behaviour.
// Uses living Asian elephant studies only as an imperfect movement reference.
export const PARAMS = Object.freeze({stride: 0.782, speed: 0.34, rampSeconds: 2,
  stance: 0.76, maxLift: 0.09});
// Index order: LF, RF, LH, RH. Touchdowns: LH, LF, RH, RF.
export const touchdown = Object.freeze([0.25, 0.75, 0.0, 0.50]);
const fract = x => x-Math.floor(x);
const smooth = x => x*x*(3-2*x);

// Continuous velocity and acceleration at the endpoints of the start ramp.
export function distanceAt(t, p=PARAMS) {
  t=Math.max(0,t);
  if(t>=p.rampSeconds) return p.speed*(t-p.rampSeconds/2);
  const u=t/p.rampSeconds;
  return p.speed*p.rampSeconds*(u*u*u-0.5*u*u*u*u);
}
export function velocityAt(t,p=PARAMS) {
  if(t<=0)return 0;
  return p.speed*(t>=p.rampSeconds?1:smooth(t/p.rampSeconds));
}

export function footAt(t,index,p=PARAMS){
  if(!Number.isInteger(index)||index<0||index>3)throw new RangeError('leg index');
  const distance=distanceAt(t,p), phase=fract(distance/p.stride-touchdown[index]);
  if(phase < p.stance) return {distance,phase,stance:true,offset:p.stride*(p.stance/2-phase),lift:0};
  const u=(phase-p.stance)/(1-p.stance);
  // Cubic Hermite interpolation matches stance velocity at liftoff/touchdown.
  const a=p.stride*p.stance/2, tangent=-p.stride*(1-p.stance);
  const u2=u*u,u3=u2*u;
  const offset=(2*u3-3*u2+1)*(-a)+(u3-2*u2+u)*tangent+(-2*u3+3*u2)*a+(u3-u2)*tangent;
  return {distance,phase,stance:false,offset,lift:p.maxLift*Math.sin(Math.PI*u)**2};
}
