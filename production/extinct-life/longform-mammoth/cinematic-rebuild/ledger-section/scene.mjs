// Evidence-ledger section — the three tiers of confidence (689-759 s).
//
// The narration spends seventy seconds separating what the evidence supports from what
// is merely plausible and from what has not been established at all. That distinction
// is the film's central epistemic claim, so the picture is a ledger, not a reveal:
// three columns, entries appearing as they are spoken, and a closing block that says
// the categories do not have to compete.
//
// Nothing here adds confidence the narration does not claim. No cause is illustrated.
import * as T from 'three';
const W=1280,H=720,FPS=30,DURATION=70;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
await document.fonts.load('700 24px Manrope');await document.fonts.load('500 20px Manrope');
const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};const lerp=(a,b,u)=>a+(b-a)*u;
const SHOTS=[{n:'what can we say',s:0,e:3},{n:'supported',s:3,e:24},{n:'plausible, not proven',s:24,e:36.5},{n:'not established',s:36.5,e:45},{n:'a possibility is not a verdict',s:45,e:70}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
function text(str,x,y,size,weight='700',alpha=1,align='left',color='32,38,40'){
 g.fillStyle=`rgba(${color},${alpha})`;g.font=`${weight} ${size}px Manrope`;g.textAlign=align;g.fillText(str,x,y);
}
// Three tiers. `at` is the local time the narration reaches that entry; nothing appears
// before it is spoken. Lines are pre-wrapped so the column widths stay fixed.
const TIERS=[
 {key:'supported',head:'SUPPORTED',col:'56,86,96',x:96,
  items:[[2.0,['Severe bottleneck, then a','modelled recovery']],
         [8.4,['Reduced diversity,','increased homozygosity']],
         [12.0,['Persistent genetic strain']],
         [15.4,['Dietary isotopes broadly stable']],
         [21.0,['Other signals read as possible','water-quality change']]]},
 {key:'plausible',head:'PLAUSIBLE, NOT PROVEN',col:'140,104,40',x:470,
  items:[[24.9,['A severe icing event']],
         [29.6,['Disease']],
         [30.6,['Poorer water']],
         [32.5,['Human involvement']],
         [35.4,['A combination of pressures','on a small, isolated population']]]},
 {key:'notestablished',head:'NOT ESTABLISHED',col:'150,64,52',x:844,
  items:[[36.6,['A single named killer']],
         [39.9,['A directly recorded fatal winter']],
         [42.7,['A genetic test proving the cause']]]},
];
const COLW=340;
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;
 g.fillStyle='#f0ede4';g.fillRect(0,0,W,H);
 const grd=g.createLinearGradient(0,0,0,H);grd.addColorStop(0,'rgba(255,253,246,.6)');grd.addColorStop(1,'rgba(206,200,186,.30)');
 g.fillStyle=grd;g.fillRect(0,0,W,H);
 for(let k=0;k<2400;k++){const h1=(Math.imul(k+1,2654435761)>>>0)/4294967296,h2=(Math.imul(k+7,1597334677)>>>0)/4294967296,h3=(Math.imul(k+13,2246822519)>>>0)/4294967296;
  g.fillStyle=h3<.5?`rgba(78,72,60,${.012+h2*.018})`:`rgba(255,255,255,${.012+h2*.018})`;g.fillRect(h1*W,h2*H,1+h3*2,1+h3*2)}
 const intro=smooth(t/1.6);
 // --- title: the narration's own question -----------------------------------------
 text('WHAT CAN WE SAY?',96,124,40,'700',.92*intro);
 text('Three tiers of confidence, in the narration’s own terms',96,162,20,'500',.64*intro,'left','52,58,58');
 g.fillStyle=`rgba(32,38,40,${.20*intro})`;g.fillRect(96,184,1088,2);

 // --- closing block fades the ledger back ------------------------------------------
 const late=smooth((t-62.4)/1.6);
 const ledgerAlpha=1-.42*late;

 // --- columns ----------------------------------------------------------------------
 let revealed=0;
 TIERS.forEach((tier)=>{
  const headA=smooth((t-(tier.x===96?2.6:tier.x===470?24.6:36.6))/.9);
  const colY=206;
  if(headA<=0)return;
  g.save();g.globalAlpha=headA*ledgerAlpha;
  g.fillStyle='rgba(255,253,246,.42)';g.fillRect(tier.x-18,colY,COLW+36,344);
  g.strokeStyle=`rgba(${tier.col},.22)`;g.lineWidth=1;g.strokeRect(tier.x-18.5,colY+.5,COLW+37,344);
  g.restore();
  text(tier.head,tier.x,236,15,'700',.9*headA*ledgerAlpha,'left',tier.col);
  g.save();g.globalAlpha=headA*ledgerAlpha;g.fillStyle=`rgba(${tier.col},.75)`;g.fillRect(tier.x,246,COLW,2);g.restore();
  let y=284;
  tier.items.forEach(([at,lines])=>{
   const a=smooth((t-at)/.9);if(a<=0)return;revealed++;
   g.save();g.globalAlpha=a*ledgerAlpha;
   g.fillStyle=`rgba(${tier.col},.85)`;g.fillRect(tier.x,y-9,12,2);
   g.restore();
   lines.forEach((ln,i)=>text(ln,tier.x+22,y+i*20,15,'500',.82*a*ledgerAlpha,'left','46,52,54'));
   y+=lines.length*20+13;
  });
 });

 // --- closing block ------------------------------------------------------------------
 const stageA=smooth((t-45.3)/1.5)*smooth((51.2-t)/1.2);
 if(stageA>0){
  text('THE FINAL GENERATIONS ARE ABSENT FROM THE LARGER GENOME DATASET',96,592,23,'700',.9*stageA);
  text('The largest genomic dataset does not reach the last generations. Absence there is',96,624,17,'500',.66*stageA,'left','58,64,64');
  text('not the same as absence of any evidence.',96,646,17,'500',.66*stageA,'left','58,64,64');
 }
 // The closing block hands off beat by beat, one headline at a time, so the three
 // statements never stack into a wall of type.
 const verdict=smooth((t-51.4)/1.6)*(1-smooth((t-62.4)/.8));
 const comp=smooth((t-62.9)/1.5);
 if(verdict>0){
  text('A POSSIBILITY IS NOT A VERDICT',96,592,27,'700',.94*verdict);
  // The supporting lines hold while the headline stands; only the final beat replaces them.
  if(verdict>0.15){
   text('The evidence does not show the herd was always healthy, that people arrived',96,624,17,'500',.66*verdict,'left','58,64,64');
   text('too late to matter, or that the final decline followed one known pattern.',96,646,17,'500',.66*verdict,'left','58,64,64');
  }
 }
 // Final beat, deliberately its own block: the categories are complementary, not rivals.
 if(comp>0){
  text('THESE CATEGORIES DO NOT HAVE TO COMPETE',96,592,26,'700',.92*comp);
  text('Vulnerability and a sudden event could work together — but that is a hypothesis,',96,634,17,'500',.68*comp,'left','58,64,64');
  text('not the answer to this particular case.',96,658,17,'500',.68*comp,'left','58,64,64');
 }
 text('SCHEMATIC · TIERS AS STATED IN THE NARRATION · NOT A FINDING OF THIS PRODUCTION',1184,H-16,12,'700',.4,'right');
 return{time:t,shot:shotIndex(t),shot_name:SHOTS[shotIndex(t)].n,animals:0,triangles:0,historical_geography:false,tiers:3,entries:revealed,possibilityNotVerdict:verdict,categoriesCompete:comp,late};
}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
