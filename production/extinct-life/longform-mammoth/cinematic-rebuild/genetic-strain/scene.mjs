// Genetic strain section — what the genomes do and do not say (495-557 s).
//
// Two traps govern this passage. The first: a group of immune-response genes lost more
// diversity than the genome as a whole, which is a genetic finding and NOT a diagnosis
// of infection. The second: effective population size fell to eight or fewer and
// recovered to roughly 250 in about twenty generations — a model parameter, not a
// census of animals.
//
// `reversal-section` already owns the curve itself (473-495 s). This section therefore
// must not repeat it. It works in bars, gaps and labels instead: two diversity measures
// that are related but different, an explicit refusal to read them as sick animals, and
// the model-versus-headcount correction stated beside the numbers, not drawn as animals.
import * as T from 'three';
const W=1280,H=720,FPS=30,DURATION=62;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
await document.fonts.load('700 24px Manrope');await document.fonts.load('500 20px Manrope');
const S=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};
const SHOTS=[{n:'two related measures',s:0,e:16.0},{n:'immune genes',s:16.0,e:30.0},{n:'a model parameter',s:30.0,e:46.0},{n:'comparatively stable',s:46.0,e:62.0}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
function text(str,x,y,size,weight='700',alpha=1,align='left',color='32,38,40'){
 g.fillStyle=`rgba(${color},${alpha})`;g.font=`${weight} ${size}px Manrope`;g.textAlign=align;g.fillText(str,x,y);
}
// Bar lengths are schematic proportions, not measured values. Nothing is to scale and
// the plate says so; no percentage is printed because none is spoken.
const DIVERSITY={genome:0.62,immune:0.29};
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;
 g.fillStyle='#f0ede4';g.fillRect(0,0,W,H);
 const grd=g.createLinearGradient(0,0,0,H);grd.addColorStop(0,'rgba(255,253,246,.6)');grd.addColorStop(1,'rgba(206,200,186,.30)');
 g.fillStyle=grd;g.fillRect(0,0,W,H);
 for(let k=0;k<2400;k++){const h1=(Math.imul(k+1,2654435761)>>>0)/4294967296,h2=(Math.imul(k+7,1597334677)>>>0)/4294967296,h3=(Math.imul(k+13,2246822519)>>>0)/4294967296;
  g.fillStyle=h3<.5?`rgba(78,72,60,${.012+h2*.018})`:`rgba(255,255,255,${.012+h2*.018})`;g.fillRect(h1*W,h2*H,1+h3*2,1+h3*2)}
 const intro=S(t/1.5);
 text('THE GENETIC STRAIN',96,124,38,'700',.92*intro);
 text('What the genomes show, and what they cannot be asked to show',96,162,20,'500',.64*intro,'left','52,58,58');
 g.fillStyle=`rgba(32,38,40,${.20*intro})`;g.fillRect(96,184,1088,2);

 // --- shot 0: two related but different measures ------------------------------------
 const two=S((t-1.0)/1.4)*(1-S((t-15.4)/1.4));
 if(two>0){
  text('TWO MEASURES, ONE GENOME',96,232,24,'700',.9*two);
  // Both arrows are drawn the same length on purpose: only the direction of the
  // relationship is shown. A longer bar would invent a magnitude nothing states.
  const cx=640,half=300;
  g.save();g.globalAlpha=.22*two;g.strokeStyle='rgba(32,38,40,.6)';g.lineWidth=1.2;
  g.beginPath();g.moveTo(cx,262);g.lineTo(cx,398);g.stroke();g.restore();
  const arrows=[{y:312,l:'GENETIC DIVERSITY',sub:'falls',col:'56,86,96',dir:-1,at:1.8},
                {y:356,l:'HOMOZYGOSITY',sub:'rises',col:'140,104,40',dir:1,at:3.4}];
  arrows.forEach(r=>{
   const a=two*S((t-r.at)/1.1);if(a<=0)return;
   const x0=cx,x1=cx+r.dir*half;
   g.save();g.globalAlpha=.78*a;g.strokeStyle=`rgba(${r.col},.85)`;g.lineWidth=14;
   g.beginPath();g.moveTo(x0,r.y);g.lineTo(x1,r.y);g.stroke();
   g.fillStyle=`rgba(${r.col},.85)`;
   g.beginPath();g.moveTo(x1,r.y-9);g.lineTo(x1+r.dir*14,r.y);g.lineTo(x1,r.y+9);g.closePath();g.fill();
   g.restore();
   // Label anchored at the axis end, direction word at the arrow tip: the two ends of
   // one statement, so neither row can be read as a magnitude.
   text(r.l,r.dir<0?cx-16:cx+16,r.y-16,13,'700',.8*a,r.dir<0?'right':'left',r.col);
   text(r.sub.toUpperCase(),r.dir<0?cx-half-16:cx+half+16,r.y+22,12.5,'700',.62*a,r.dir<0?'right':'left','70,76,76');
  });
  const lab=two*S((t-4.4)/1.2);
  if(lab>0)text('SAME GENOME · OPPOSITE DIRECTIONS',cx,432,12.5,'700',.56*lab,'center','70,76,76');
  const a=two*S((t-5.2)/1.4);
  if(a>0)text('Related, but not the same thing — one can rise while the other falls.',96,490,18,'500',.68*a,'left','58,64,64');
  const b=two*S((t-7.4)/1.4);
  if(b>0){
   g.save();g.globalAlpha=.16*b;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,520,1088,1);g.restore();
   text('NEITHER IS A DIRECT COUNT OF SICK ANIMALS',96,558,21,'700',.86*b);
   text('Homozygosity and diversity describe the genome. They do not describe the health',96,590,17,'500',.6*b,'left','58,64,64');
   text('of any individual mammoth, and this film does not use them as if they did.',96,614,17,'500',.6*b,'left','58,64,64');
  }
 }

 // --- shot 1: the immune-gene finding, held as a finding ----------------------------
 const imm=S((t-16.1)/1.4)*(1-S((t-29.4)/1.4));
 if(imm>0){
  text('A GROUP OF IMMUNE-RESPONSE GENES',96,232,24,'700',.9*imm);
  const bx=340,bw=620;
  [[296,'GENOME-WIDE DIVERSITY',DIVERSITY.genome,'56,86,96',17.0],
   [372,'IMMUNE-RESPONSE GENES',DIVERSITY.immune,'150,64,52',18.2]].forEach(([y,l,v,col,at])=>{
   const a=imm*S((t-at)/1.1);if(a<=0)return;
   text(l,96,y+6,13,'700',.74*a,'left',col);
   g.save();g.globalAlpha=.16*a;g.fillStyle=`rgba(${col},.6)`;g.fillRect(bx,y-12,bw,26);g.restore();
   g.save();g.globalAlpha=a;g.fillStyle=`rgba(${col},.72)`;g.fillRect(bx,y-12,bw*v,26);g.restore();
  });
  const a=imm*S((t-20.0)/1.3);
  if(a>0)text('It declined more than the genome as a whole.',96,446,18,'500',.68*a,'left','58,64,64');
  const b=imm*S((t-23.4)/1.4);
  if(b>0){
   g.save();g.globalAlpha=.16*b;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,486,1088,1);g.restore();
   text('A GENETIC FINDING, NOT A DIAGNOSIS',96,524,21,'700',.86*b);
   text('Losing immune-gene diversity is not evidence of a specific infection. No pathogen',96,556,17,'500',.6*b,'left','58,64,64');
   text('is identified here, and none should be inferred from this bar.',96,580,17,'500',.6*b,'left','58,64,64');
  }
 }

 // --- shot 2: effective size is a model parameter -----------------------------------
 const model=S((t-30.1)/1.4)*(1-S((t-45.4)/1.4));
 if(model>0){
  text('THEN CAME THE SURPRISE',96,232,24,'700',.9*model);
  const cards=[{x:96,head:'AT THE BOTTLENECK',val:'EIGHT OR FEWER',sub:'modelled effective size',col:'150,64,52',at:31.6},
               {x:672,head:'AFTER RECOVERY',val:'~200–300',sub:'within roughly 20 generations',col:'56,86,96',at:34.4}];
  cards.forEach(c=>{
   const a=model*S((t-c.at)/1.1);if(a<=0)return;
   g.save();g.globalAlpha=.4*a;g.fillStyle='rgba(255,253,246,.8)';g.fillRect(c.x,282,496,116);
   g.strokeStyle=`rgba(${c.col},.28)`;g.lineWidth=1;g.strokeRect(c.x+.5,282.5,496,116);g.restore();
   text(c.head,c.x+22,312,12.5,'700',.66*a,'left',c.col);
   text(c.val,c.x+22,354,32,'700',.9*a,'left',c.col);
   text(c.sub,c.x+22,380,14,'500',.56*a,'left','70,76,76');
  });
  const a=model*S((t-37.6)/1.3);
  if(a>0){
   text('EFFECTIVE SIZE IS A MODEL PARAMETER — NOT A HEADCOUNT',96,458,21,'700',.88*a);
   text('It is not eight mammoths becoming three hundred. The curve models genetic',96,492,17,'500',.62*a,'left','58,64,64');
   text('relationships; it does not count animals, and no animal is drawn here.',96,516,17,'500',.62*a,'left','58,64,64');
  }
  const b=model*S((t-41.4)/1.3);
  if(b>0)text('The same model that shows recovery also shows strain persisting through it.',96,566,17,'500',.5*b,'left','70,76,76');
 }

 // --- shot 3: comparatively stable, and what comes next ------------------------------
 const stab=S((t-46.1)/1.5);
 if(stab>0){
  text('COMPARATIVELY STABLE — ACROSS THE SAMPLES',96,232,24,'700',.9*stab);
  const a=stab*S((t-48.0)/1.4);
  if(a>0){
   text('Across the years the samples represent, the population looked comparatively stable.',96,286,18,'500',.68*a,'left','58,64,64');
   text('Recovery did not mean the genetic risks disappeared.',96,314,18,'500',.68*a,'left','58,64,64');
  }
  const b=stab*S((t-51.0)/1.4);
  if(b>0){
   g.save();g.globalAlpha=.16*b;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,352,1088,1);g.restore();
   text('DIVERSITY AND HOMOZYGOSITY ARE NOT THE ONLY THINGS TO COMPARE',96,392,20,'700',.86*b);
   // three comparison channels opening towards the next passage, left deliberately blank
   ['VARIANTS PREDICTED TO BE HARMFUL','HOW MUCH SEQUENCE IS READABLE','DATA QUALITY'].forEach((l,i)=>{
    const q=stab*S((t-(51.6+i*.45))/.9);if(q<=0)return;
    const x=96+i*368;
    g.save();g.globalAlpha=.34*q;g.strokeStyle='rgba(32,38,40,.35)';g.lineWidth=1;g.setLineDash([4,6]);
    g.strokeRect(x+.5,428.5,336,74);g.setLineDash([]);g.restore();
    text(l,x+16,470,12.5,'700',.62*q,'left','70,76,76');
   });
   const c=stab*S((t-54.4)/1.3);
   if(c>0)text('The next question is whether a difference in the data is a difference in the animals.',96,552,17,'500',.62*c,'left','58,64,64');
   const d=stab*S((t-57.2)/1.2);
   if(d>0)text('That question needs its own test, and the next section gives it one.',96,578,15,'500',.46*d,'left','70,76,76');
  }
 }
 text('SCHEMATIC · BAR LENGTHS ARE NOT TO SCALE · NO VALUES OR COUNTS PRINTED',1184,H-16,12,'700',.4,'right');
 return{time:t,shot:shotIndex(t),shot_name:SHOTS[shotIndex(t)].n,animals:0,triangles:0,historical_geography:false,curveDrawn:false,scaleClaim:false,sickAnimals:false};
}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
