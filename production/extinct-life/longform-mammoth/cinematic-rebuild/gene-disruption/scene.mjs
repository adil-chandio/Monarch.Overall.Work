// Gene-disruption section — the 2017 result in detail (192.733-220.0 s).
//
// This passage lists three kinds of change that can disrupt a gene, states that the
// island genome carried an excess of them, gives one number the narration gives (an
// effective size "more than forty three times lower"), and then immediately restricts
// it: that number is a genetic estimate, not a head count. It closes by explaining what
// a premature stop and a deletion actually do.
//
// So the plate is a variant ledger and then an explanation. No sequence, no helix, no
// protein structure is invented; nothing is drawn that would imply a diagnosis, and the
// 43x figure appears only with its own caveat on screen beside it.
import * as T from 'three';
const W=1280,H=720,FPS=30,DURATION=27.2667;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
await document.fonts.load('700 24px Manrope');await document.fonts.load('500 20px Manrope');
const S=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};
const SHOTS=[{n:'an excess of disruptive changes',s:0,e:9.9},{n:'not a head count',s:9.9,e:16.0},{n:'what these changes do',s:16.0,e:27.2667}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
function text(str,x,y,size,weight='700',alpha=1,align='left',color='32,38,40'){
 g.fillStyle=`rgba(${color},${alpha})`;g.font=`${weight} ${size}px Manrope`;g.textAlign=align;g.fillText(str,x,y);
}
// Three kinds of change, in the narration's order. The tick counts are decorative
// quantities only — no count is spoken and none is printed as a number.
const KINDS=[
 {l:'DELETIONS',sub:'pieces of the genome removed',at:1.6,ticks:14},
 {l:'DELETIONS AFFECTING GENES',sub:'removals that land inside a gene',at:4.2,ticks:9},
 {l:'PREMATURE STOP SIGNALS',sub:'instructions cut short',at:6.2,ticks:11}];
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;
 g.fillStyle='#f0ede4';g.fillRect(0,0,W,H);
 const grd=g.createLinearGradient(0,0,0,H);grd.addColorStop(0,'rgba(255,253,246,.6)');grd.addColorStop(1,'rgba(206,200,186,.30)');
 g.fillStyle=grd;g.fillRect(0,0,W,H);
 for(let k=0;k<2400;k++){const h1=(Math.imul(k+1,2654435761)>>>0)/4294967296,h2=(Math.imul(k+7,1597334677)>>>0)/4294967296,h3=(Math.imul(k+13,2246822519)>>>0)/4294967296;
  g.fillStyle=h3<.5?`rgba(78,72,60,${.012+h2*.018})`:`rgba(255,255,255,${.012+h2*.018})`;g.fillRect(h1*W,h2*H,1+h3*2,1+h3*2)}
 const intro=S(t/1.4);
 text('AN EXCESS OF GENE-DISRUPTING CHANGES',96,124,36,'700',.92*intro);
 text('What the 2017 island genome carried more of than the mainland genome',96,162,19,'500',.62*intro,'left','52,58,58');
 g.fillStyle=`rgba(32,38,40,${.20*intro})`;g.fillRect(96,184,1088,2);

 // --- shot 0: the three kinds -------------------------------------------------------
 const kinds=S((t-0.8)/1.3)*(1-S((t-9.3)/1.2));
 if(kinds>0){
  const bx=96;
  KINDS.forEach((k,i)=>{
   const a=kinds*S((t-k.at)/1.0);if(a<=0)return;
   const y=252+i*104;
   g.save();g.globalAlpha=.34*a;g.fillStyle='rgba(255,253,246,.75)';g.fillRect(bx,y,640,84);
   g.strokeStyle='rgba(32,38,40,.15)';g.lineWidth=1;g.strokeRect(bx+.5,y+.5,640,84);g.restore();
   text(k.l,bx+20,y+34,16,'700',.8*a,'left','56,86,96');
   text(k.sub,bx+20,y+60,13.5,'500',.5*a,'left','70,76,76');
   // No tick field and no per-row badge: any count of marks would read as a measured
   // quantity, and the narration gives none. The claim is made once, in words, below.
  });
  const a=kinds*S((t-7.4)/1.2);
  if(a>0){
   text('THE ISLAND GENOME CARRIED AN EXCESS OF ALL THREE',96,540,21,'700',.88*a);
   text('compared with the single mainland genome it was set against',96,568,16,'500',.54*a,'left','70,76,76');
  }
 }

 // --- shot 1: the number and its caveat ---------------------------------------------
 const num=S((t-10.0)/1.3)*(1-S((t-15.4)/1.2));
 if(num>0){
  text('THE ESTIMATED EFFECTIVE SIZE',96,232,13,'700',.66*num,'left','70,76,76');
  const a=num*S((t-10.6)/1.1);
  if(a>0){
   text('MORE THAN 43× LOWER',96,296,54,'700',.94*a,'left','150,64,52');
   text('than the mainland animal’s estimate',96,330,17,'500',.6*a,'left','58,64,64');
  }
  const b=num*S((t-12.4)/1.2);
  if(b>0){
   g.save();g.globalAlpha=.16*b;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,372,1088,1);g.restore();
   text('THAT NUMBER IS A GENETIC ESTIMATE, NOT A HEAD COUNT',96,418,22,'700',.9*b);
   text('It is not a census. It describes the genetic relationships the sample implies, and',96,452,17,'500',.6*b,'left','58,64,64');
   text('it does not say how many animals were alive.',96,476,17,'500',.6*b,'left','58,64,64');
  }
  const c=num*S((t-14.0)/1.1);
  if(c>0)text('Nor is it a count of sick animals.',96,522,16,'500',.46*c,'left','70,76,76');
 }

 // --- shot 2: what the changes actually do --------------------------------------------
 const mech=S((t-16.1)/1.4);
 if(mech>0){
  text('WHAT THESE CHANGES DO',96,232,24,'700',.9*mech);
  // Two explanations, each with a small diagram: a line interrupted, a line with a gap.
  const a=mech*S((t-17.0)/1.2);
  if(a>0){
   text('A PREMATURE STOP',96,286,13,'700',.68*a,'left','150,64,52');
   // instruction line that stops early
   g.save();g.globalAlpha=.8*a;g.strokeStyle='rgba(56,86,96,.8)';g.lineWidth=3;
   g.beginPath();g.moveTo(96,318);g.lineTo(430,318);g.stroke();
   g.strokeStyle='rgba(150,64,52,.9)';g.beginPath();g.moveTo(430,306);g.lineTo(430,330);g.stroke();
   g.restore();
   text('can interrupt the instructions for a protein',96,352,16,'500',.62*a,'left','58,64,64');
  }
  const b=mech*S((t-19.4)/1.2);
  if(b>0){
   text('A DELETION',680,286,13,'700',.68*b,'left','150,64,52');
   g.save();g.globalAlpha=.8*b;g.strokeStyle='rgba(56,86,96,.8)';g.lineWidth=3;
   g.beginPath();g.moveTo(680,318);g.lineTo(820,318);g.moveTo(880,318);g.lineTo(1014,318);g.stroke();
   g.setLineDash([3,4]);g.strokeStyle='rgba(150,64,52,.7)';g.lineWidth=1.4;
   g.beginPath();g.moveTo(820,318);g.lineTo(880,318);g.stroke();g.setLineDash([]);
   g.restore();
   text('can remove pieces of the genome',680,352,16,'500',.62*b,'left','58,64,64');
  }
  const c=mech*S((t-21.6)/1.3);
  if(c>0){
   g.save();g.globalAlpha=.16*c;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,396,1088,1);g.restore();
   text('WHAT THIS DOES NOT SAY',96,438,13,'700',.66*c,'left','70,76,76');
   text('A disruptive change is a change in instructions. It is not, by itself, a cause of death,',96,468,17,'500',.6*c,'left','58,64,64');
   text('and nothing here identifies what affected any individual animal.',96,492,17,'500',.6*c,'left','58,64,64');
  }
  const d=mech*S((t-24.4)/1.2);
  if(d>0)text('The study also reported losses affecting some smell-related receptors.',96,548,16,'500',.5*d,'left','70,76,76');
 }
 text('SCHEMATIC · DIAGRAMS ARE NOT DATA · THE 43× FIGURE IS AS SPOKEN',1184,H-16,12,'700',.4,'right');
 return{time:t,shot:shotIndex(t),shot_name:SHOTS[shotIndex(t)].n,animals:0,triangles:0,historical_geography:false,
  kinds:3,headCountClaim:false,diagnosis:false,sequenceDepicted:false};
}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
