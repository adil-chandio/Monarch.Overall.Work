// Two-trends section — the 2024 result, and what it does not settle (577-629.1 s).
//
// The narration makes three moves here and each one limits the previous:
//   1. a difference in coverage could be mistaken for a difference between the animals,
//      so the bias has to be tested first;
//   2. after accounting for it, two opposing trends appear — the highest-impact variants
//      became less common (selection purging), moderately harmful ones accumulated
//      (drift outpacing selection);
//   3. these are PREDICTED EFFECTS, not medical examinations, and neither finding by
//      itself says what caused the extinction.
//
// So the plate is a test register, then a two-direction trend diagram, then a record that
// visibly stops short of the final generations. Nothing here is drawn as severity, damage
// or an animal's condition, and the trends are never presented as a settled cause.
import * as T from 'three';
const W=1280,H=720,FPS=30,DURATION=52.0667;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
await document.fonts.load('700 24px Manrope');await document.fonts.load('500 20px Manrope');
const S=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};
const SHOTS=[{n:'test the bias first',s:0,e:11.0},{n:'two opposing trends',s:11.0,e:28.5},{n:'no accelerating collapse',s:28.5,e:38.5},{n:'neither finding alone',s:38.5,e:52.0667}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
function text(str,x,y,size,weight='700',alpha=1,align='left',color='32,38,40'){
 g.fillStyle=`rgba(${color},${alpha})`;g.font=`${weight} ${size}px Manrope`;g.textAlign=align;g.fillText(str,x,y);
}
// Row spacing for the record band in shot 2. Fixed marks, no random walk: this is a
// schematic span, not a sequence of measurements.
const HATCH=[];
for(let i=0;i<64;i++){
 const h1=(Math.imul(i+5,2654435761)>>>0)/4294967296;
 const h2=(Math.imul(i+17,1597334677)>>>0)/4294967296;
 HATCH.push({u:(i+0.5)/64,y:h1,v:h2});
}
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;
 g.fillStyle='#f0ede4';g.fillRect(0,0,W,H);
 const grd=g.createLinearGradient(0,0,0,H);grd.addColorStop(0,'rgba(255,253,246,.6)');grd.addColorStop(1,'rgba(206,200,186,.30)');
 g.fillStyle=grd;g.fillRect(0,0,W,H);
 for(let k=0;k<2400;k++){const h1=(Math.imul(k+1,2654435761)>>>0)/4294967296,h2=(Math.imul(k+7,1597334677)>>>0)/4294967296,h3=(Math.imul(k+13,2246822519)>>>0)/4294967296;
  g.fillStyle=h3<.5?`rgba(78,72,60,${.012+h2*.018})`:`rgba(255,255,255,${.012+h2*.018})`;g.fillRect(h1*W,h2*H,1+h3*2,1+h3*2)}
 const intro=S(t/1.5);
 text('TWO TRENDS, AND THEIR LIMITS',96,124,38,'700',.92*intro);
 text('What the 2024 analysis found after accounting for how much of each genome is readable',96,162,19,'500',.62*intro,'left','52,58,58');
 g.fillStyle=`rgba(32,38,40,${.20*intro})`;g.fillRect(96,184,1088,2);

 // --- shot 0: the bias has to be tested first ---------------------------------------
 const bias=S((t-0.9)/1.4)*(1-S((t-10.5)/1.3));
 if(bias>0){
  text('THE DIFFERENCE COULD BE IN THE DATA',96,236,26,'700',.9*bias);
  const cols=[{x:96,head:'BEFORE THE TEST',sub:'a genome with more readable sequence',col:'150,64,52',at:2.0},
              {x:672,head:'AFTER THE TEST',sub:'compared like with like',col:'56,86,96',at:5.4}];
  cols.forEach(c=>{
   const a=bias*S((t-c.at)/1.1);if(a<=0)return;
   g.save();g.globalAlpha=.4*a;g.fillStyle='rgba(255,253,246,.8)';g.fillRect(c.x,278,512,120);
   g.strokeStyle=`rgba(${c.col},.28)`;g.lineWidth=1;g.strokeRect(c.x+.5,278.5,512,120);g.restore();
   text(c.head,c.x+22,310,12.5,'700',.68*a,'left',c.col);
   text(c.sub,c.x+22,344,16,'500',.66*a,'left','46,52,54');
  });
  const a=bias*S((t-2.0)/1.2);
  if(a>0)text('A difference in the data is not automatically a difference between the animals.',672+22,376,14,'500',.5*a,'left','70,76,76');
  const b=bias*S((t-6.8)/1.3);
  if(b>0){
   g.save();g.globalAlpha=.16*b;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,438,1088,1);g.restore();
   text('WITHOUT TESTING THAT BIAS, THE RESULT WOULD BE UNREADABLE',96,478,20,'700',.86*b);
   text('Coverage and data quality are conditions of the measurement, so they are tested',96,510,17,'500',.58*b,'left','58,64,64');
   text('before any difference is attributed to the animals.',96,534,17,'500',.58*b,'left','58,64,64');
  }
 }

 // --- shot 1: two trends, in opposite directions ------------------------------------
 const trends=S((t-11.1)/1.5)*(1-S((t-28.0)/1.3));
 if(trends>0){
  text('AFTER ACCOUNTING FOR THOSE DIFFERENCES, TWO TRENDS',96,236,24,'700',.9*trends);
  const cx=560,half=380;
  const rows=[
   {y:322,label:'VARIANTS PREDICTED TO HAVE THE HIGHEST IMPACT',dir:-1,word:'BECAME LESS COMMON',
    note:'consistent with natural selection purging some of them',col:'56,86,96',at:13.2,sub:15.6},
   {y:414,label:'MODERATELY HARMFUL VARIANTS',dir:1,word:'ACCUMULATED',
    note:'consistent with genetic drift outpacing selection',col:'140,104,40',at:19.4,sub:21.6}];
  g.save();g.globalAlpha=.18*trends;g.strokeStyle='rgba(32,38,40,.6)';g.lineWidth=1.2;
  g.beginPath();g.moveTo(cx,292);g.lineTo(cx,452);g.stroke();g.restore();
  rows.forEach(r=>{
   const a=trends*S((t-r.at)/1.1);if(a<=0)return;
   const x1=cx+r.dir*half;
   // Row label sits above the axis, left-aligned, so it never crosses the arrow.
   text(r.label,96,r.y-24,12.5,'700',.76*a,'left',r.col);
   g.save();g.globalAlpha=.8*a;g.strokeStyle=`rgba(${r.col},.85)`;g.lineWidth=12;
   g.beginPath();g.moveTo(cx,r.y);g.lineTo(x1,r.y);g.stroke();
   g.fillStyle=`rgba(${r.col},.85)`;
   g.beginPath();g.moveTo(x1,r.y-8);g.lineTo(x1+r.dir*13,r.y);g.lineTo(x1,r.y+8);g.closePath();g.fill();
   g.restore();
   text(r.word,r.dir<0?x1-16:x1+16,r.y+6,13,'700',.84*a,r.dir<0?'right':'left',r.col);
   const b=trends*S((t-r.sub)/1.2);
   if(b>0)text(r.note,96,r.y+40,14.5,'500',.58*b,'left','58,64,64');
  });
  const a=trends*S((t-23.6)/1.4);
  if(a>0){
   g.save();g.globalAlpha=.16*a;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,496,1088,1);g.restore();
   text('PREDICTED EFFECTS — NOT MEDICAL EXAMINATIONS',96,536,21,'700',.9*a);
   text('These are predictions about variants in a genome. They are not examinations of',96,568,17,'500',.6*a,'left','58,64,64');
   text('individual mammoths, and no animal is diagnosed by them.',96,592,17,'500',.6*a,'left','58,64,64');
  }
 }

 // --- shot 2: no accelerating collapse, and a record that stops early ----------------
 const flat=S((t-28.6)/1.5)*(1-S((t-38.0)/1.3));
 if(flat>0){
  text('NO CLEAR ACCELERATING COLLAPSE',96,236,26,'700',.9*flat);
  const bx=96,bw=1088,by=290,bh=120;
  const a=flat*S((t-30.0)/1.4);
  if(a>0){
   // the sampled span, drawn as a field of fixed marks — not a rising or falling series
   g.save();g.globalAlpha=a*.5;
   for(const h of HATCH){
    const x=bx+h.u*bw*0.72;
    g.fillStyle=`rgba(56,86,96,${.20+h.v*.30})`;g.fillRect(x,by+16+h.y*70,3,3);
   }
   g.restore();
   g.save();g.globalAlpha=.55*a;g.strokeStyle='rgba(56,86,96,.7)';g.lineWidth=1.5;
   g.beginPath();g.moveTo(bx,by+10);g.lineTo(bx+bw*0.72,by+10);g.moveTo(bx,by+bh);g.lineTo(bx+bw*0.72,by+bh);g.stroke();
   g.restore();
   text('SAMPLED GENOMES',bx,by+bh+30,12.5,'700',.58*a,'left','56,86,96');
  }
  const b=flat*S((t-32.4)/1.4);
  if(b>0){
   // the final generations: dashed, empty, and explicitly outside the dataset
   g.save();g.globalAlpha=.5*b;g.setLineDash([5,6]);
   g.strokeStyle='rgba(150,64,52,.6)';g.lineWidth=1.5;
   g.strokeRect(bx+bw*0.72+8,by+10,bw*0.28-8,bh-10);g.setLineDash([]);g.restore();
   text('FINAL GENERATIONS · NOT IN THE LARGER DATASET',bx+bw*0.72+8,by+bh+30,12.5,'700',.62*b,'left','150,64,52');
  }
  const c=flat*S((t-33.4)/1.3);
  if(c>0)text('The sampled genomes show no clear accelerating genomic collapse across their history.',96,470,18,'500',.66*c,'left','58,64,64');
  const d=flat*S((t-35.6)/1.3);
  if(d>0){
   text('A POPULATION CAN RECOVER DEMOGRAPHICALLY AND STILL CARRY LASTING STRAIN',96,516,18,'700',.84*d);
   text('The youngest genome predates the final generations, so the record ends before the end.',96,548,16,'500',.54*d,'left','70,76,76');
  }
 }

 // --- shot 3: neither finding alone --------------------------------------------------
 const alone=S((t-38.6)/1.5);
 if(alone>0){
  text('NEITHER FINDING, BY ITSELF',96,236,26,'700',.9*alone);
  const a=alone*S((t-40.2)/1.4);
  if(a>0)text('Two opposing trends are not a resolution. Purging and accumulation can both be',96,286,18,'500',.68*a,'left','58,64,64');
  const b=alone*S((t-41.8)/1.3);
  if(b>0)text('real and still leave the question of the extinction exactly where it was.',96,314,18,'500',.68*b,'left','58,64,64');
  [[96,'PURGING'], [452,'ACCUMULATION'], [808,'THE EXTINCTION']].forEach(([x,l],i)=>{
   const q=alone*S((t-(43.4+i*.5))/.9);if(q<=0)return;
   g.save();g.globalAlpha=.28*q;g.strokeStyle='rgba(32,38,40,.4)';g.lineWidth=1;
   g.strokeRect(x+.5,360.5,368,86);g.restore();
   text(l,x+18,394,14,'700',.7*q,'left', i===2?'150,64,52':'70,76,76');
   text(i===2?'not identified here':i===0?'a trend':'a trend',x+18,420,13,'500',.44*q,'left','92,96,96');
  });
  const c=alone*S((t-45.6)/1.4);
  if(c>0)text('So neither trend, on its own, tells us what caused the extinction.',96,492,18,'500',.62*c,'left','58,64,64');
  const d=alone*S((t-48.6)/1.4);
  if(d>0){
   g.save();g.globalAlpha=.16*d;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,528,1088,1);g.restore();
   text('HERE IS THE MISSING WITNESS',96,572,24,'700',.9*d);
   text('What the genomes can speak to depends on which animals are in them.',96,604,16,'500',.54*d,'left','70,76,76');
  }
 }
 text('SCHEMATIC · TRENDS ARE PREDICTED EFFECTS, NOT MEASUREMENTS OF INDIVIDUALS',1184,H-16,12,'700',.4,'right');
 return{time:t,shot:shotIndex(t),shot_name:SHOTS[shotIndex(t)].n,animals:0,triangles:0,historical_geography:false,
  trendsShown:trends>0.02,predictedLabeled:true,recordStopsEarly:flat>0.02,collapseClaimed:false,sickAnimal:false};
}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
