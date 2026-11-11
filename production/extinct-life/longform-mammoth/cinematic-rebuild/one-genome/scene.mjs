// One-genome section — what a single comparison can and cannot carry (274-305 s).
//
// The 2017 result is the film's first genetic warning, and it is also the weakest
// evidence it presents: ONE island genome against ONE mainland genome. The narration
// says exactly that, then says seven years later a larger study found a bottleneck, a
// recovery, and lasting strain.
//
// So the plate is a sample ledger. It shows two single marks, states the limits of two
// marks, then shows the larger sample arriving — without drawing the 2024 curve, which
// reversal-section owns at 473 s and must not be pre-empted here.
import * as T from 'three';
const W=1280,H=720,FPS=30,DURATION=31;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
await document.fonts.load('700 24px Manrope');await document.fonts.load('500 20px Manrope');
const S=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};
const SHOTS=[{n:'a clue, not a likeness',s:0,e:10.0},{n:'one against one',s:10.0,e:20.5},{n:'seven years later',s:20.5,e:31}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
function text(str,x,y,size,weight='700',alpha=1,align='left',color='32,38,40'){
 g.fillStyle=`rgba(${color},${alpha})`;g.font=`${weight} ${size}px Manrope`;g.textAlign=align;g.fillText(str,x,y);
}
// The 2024 sample: 21 genomes = 7 mainland + 14 Wrangel, as in genome-record.
const SMALL=[{x:0,side:-1},{x:1,side:1}];
const LARGE=[];
for(let i=0;i<21;i++){
 const h=(Math.imul(i+3,2654435761)>>>0)/4294967296;
 const h2=(Math.imul(i+11,1597334677)>>>0)/4294967296;
 LARGE.push({x:0.02+((i%11)/11)*0.96,y:0.5+(h-0.5)*0.75,mainland:i%3===0,size:h2});
}
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;
 g.fillStyle='#f0ede4';g.fillRect(0,0,W,H);
 const grd=g.createLinearGradient(0,0,0,H);grd.addColorStop(0,'rgba(255,253,246,.6)');grd.addColorStop(1,'rgba(206,200,186,.30)');
 g.fillStyle=grd;g.fillRect(0,0,W,H);
 for(let k=0;k<2400;k++){const h1=(Math.imul(k+1,2654435761)>>>0)/4294967296,h2=(Math.imul(k+7,1597334677)>>>0)/4294967296,h3=(Math.imul(k+13,2246822519)>>>0)/4294967296;
  g.fillStyle=h3<.5?`rgba(78,72,60,${.012+h2*.018})`:`rgba(255,255,255,${.012+h2*.018})`;g.fillRect(h1*W,h2*H,1+h3*2,1+h3*2)}
 const intro=S(t/1.5);
 text('WHAT ONE GENOME CAN CARRY',96,124,38,'700',.92*intro);
 text('The 2017 result, and why it needed a larger sample',96,162,20,'500',.64*intro,'left','52,58,58');
 g.fillStyle=`rgba(32,38,40,${.20*intro})`;g.fillRect(96,184,1088,2);

 // --- shot 0: DNA is a clue, not a likeness ----------------------------------------
 const clue=S((t-0.9)/1.4)*(1-S((t-9.6)/1.3));
 if(clue>0){
  text('A CLUE, NOT A LIKENESS',96,236,24,'700',.9*clue);
  // Two columns: what DNA preserves, what it cannot tell us.
  const a=clue*S((t-2.0)/1.2);
  if(a>0){
   text('WHAT DNA PRESERVES',96,286,12.5,'700',.66*a,'left','56,86,96');
   text('A record of ancestry, relatedness and variants.',96,314,17,'500',.64*a,'left','46,52,54');
  }
  const b=clue*S((t-3.6)/1.2);
  if(b>0){
   text('WHAT IT CANNOT TELL US',680,286,12.5,'700',.66*b,'left','150,64,52');
   text('How the animal looked.',680,314,17,'500',.64*b,'left','46,52,54');
   text('How it coped with Arctic conditions.',680,340,17,'500',.64*b,'left','46,52,54');
  }
  const c=clue*S((t-5.6)/1.4);
  if(c>0){
   g.save();g.globalAlpha=.16*c;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,384,1088,1);g.restore();
   text('A genome is evidence about inheritance. It is not a portrait of a living animal.',96,424,19,'700',.82*c);
   text('That distinction holds for every genetic claim in this film.',96,456,16,'500',.5*c,'left','70,76,76');
  }
  const d=clue*S((t-7.4)/1.3);
  if(d>0)text('So when DNA suggests a genetic effect, the suggestion still needs a sample.',96,506,15,'500',.48*d,'left','70,76,76');
 }

 // --- shot 1: one against one -------------------------------------------------------
 const one=S((t-10.1)/1.5)*(1-S((t-19.9)/1.3));
 if(one>0){
  text('ONE ISLAND GENOME, ONE MAINLAND GENOME',96,236,24,'700',.9*one);
  // Two marks only. Their emptiness is the argument.
  const a=one*S((t-11.4)/1.1);
  if(a>0){
   // Two panels, each holding a single mark. The emptiness of each panel is the point:
   // one genome per place cannot separate isolation from the animals sampled.
   const py=262,ph=136;
   [[96,'ISLAND'],[660,'MAINLAND']].forEach(([x,l])=>{
    g.save();g.globalAlpha=.32*a;g.fillStyle='rgba(255,253,246,.75)';g.fillRect(x,py,524,ph);
    g.strokeStyle='rgba(32,38,40,.16)';g.lineWidth=1;g.strokeRect(x+.5,py+.5,524,ph);g.restore();
    text(l,x+22,py+32,12.5,'700',.7*a,'left','56,86,96');
    g.save();g.globalAlpha=.85*a;g.fillStyle='rgba(56,86,96,.9)';
    g.beginPath();g.arc(x+262,py+80,7,0,Math.PI*2);g.fill();g.restore();
    text('one genome',x+22,py+114,13,'500',.5*a,'left','70,76,76');
   });
   g.save();g.globalAlpha=.3*a;g.strokeStyle='rgba(32,38,40,.4)';g.lineWidth=1.2;
   g.setLineDash([4,6]);g.beginPath();g.moveTo(632,py+68);g.lineTo(648,py+68);g.stroke();g.setLineDash([]);g.restore();
  }
  const b=one*S((t-13.6)/1.4);
  if(b>0){
   text('THE 2017 RESULT RAISED A WARNING',96,436,20,'700',.86*b);
   text('about the genetic effects of isolation.',96,464,17,'500',.6*b,'left','58,64,64');
  }
  const c=one*S((t-16.0)/1.4);
  if(c>0){
   g.save();g.globalAlpha=.16*c;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,508,1088,1);g.restore();
   text('A WARNING FROM TWO GENOMES IS A WARNING, NOT A MEASUREMENT',96,546,18,'700',.84*c);
   text('One comparison cannot separate a genetic effect of isolation from the particular',96,566,16,'500',.54*c,'left','58,64,64');
   text('animals that happened to be sequenced.',96,588,16,'500',.54*c,'left','58,64,64');
  }
 }

 // --- shot 2: seven years later -------------------------------------------------------
 const later=S((t-20.6)/1.5);
 if(later>0){
  text('SEVEN YEARS LATER, A LARGER STUDY',96,236,24,'700',.9*later);
  const a=later*S((t-22.0)/1.4);
  if(a>0){
   // the same comparison, now with a real sample behind it
   const bx=96,by=282,bw=1088,bh=132;
   g.save();g.globalAlpha=.14*a;g.fillStyle='rgba(32,38,40,.4)';g.fillRect(bx,by+30,bw,bh-30);g.restore();
   LARGE.forEach((s,i)=>{
    const q=later*S((t-(22.4+i*0.11))/.6);if(q<=0)return;
    const x=bx+s.x*bw,y=by+30+s.y*(bh-30);
    g.save();g.globalAlpha=.85*q;g.fillStyle=s.mainland?'rgba(140,104,40,.85)':'rgba(56,86,96,.85)';
    g.beginPath();g.arc(x,y,3+s.size*2.2,0,Math.PI*2);g.fill();g.restore();
   });
   text('21 GENOMES · 7 MAINLAND, 14 WRANGEL',bx,by+bh+30,13,'700',.66*a);
  }
  const b=later*S((t-24.6)/1.4);
  if(b>0){
   text('A severe bottleneck and a surprising recovery.',96,472,19,'700',.82*b);
   text('The possibility of lasting genetic strain was not removed.',96,500,17,'500',.6*b,'left','58,64,64');
  }
  const c=later*S((t-27.0)/1.3);
  if(c>0){
   g.save();g.globalAlpha=.16*c;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,532,1088,1);g.restore();
   text('A larger sample can support a claim the first could only raise.',96,572,17,'500',.56*c,'left','70,76,76');
  }
 }
 text('SCHEMATIC · SAMPLE COUNTS FOLLOW THE NARRATION · NO DATES OR VALUES PRINTED',1184,H-16,12,'700',.4,'right');
 return{time:t,shot:shotIndex(t),shot_name:SHOTS[shotIndex(t)].n,animals:0,triangles:0,historical_geography:false,
  smallSample:2,largeSample:21,curveDrawn:false,portrait:false};
}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
