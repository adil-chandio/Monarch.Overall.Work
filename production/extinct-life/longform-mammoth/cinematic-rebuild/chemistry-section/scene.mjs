// Chemistry section — the isotopic witnesses (305-354 s).
//
// The narration calls chemistry "the second witness". So the plate is a witness
// register, not a graph: four isotope systems and what each one can report on, then the
// 2019 Wrangel comparison, then the caveat that carries the whole passage — an isotope
// value is a record of particular animals and tissues, not a weather station.
//
// No isotope numbers, no axes and no fabricated series appear anywhere. The narration
// says "broadly stable"; a band labelled stable is what honesty permits here.
import * as T from 'three';
const W=1280,H=720,FPS=30,DURATION=49;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
await document.fonts.load('700 24px Manrope');await document.fonts.load('500 20px Manrope');
const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};
const SHOTS=[{n:'the second witness',s:0,e:16.5},{n:'the 2019 comparison',s:16.5,e:34.5},{n:'not a weather station',s:34.5,e:49}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
function text(str,x,y,size,weight='700',alpha=1,align='left',color='32,38,40'){
 g.fillStyle=`rgba(${color},${alpha})`;g.font=`${weight} ${size}px Manrope`;g.textAlign=align;g.fillText(str,x,y);
}
// Four witnesses, each with what the narration says it can speak to.
const SYSTEMS=[
 {sym:'C',name:'CARBON',about:'diet',at:3.3},
 {sym:'N',name:'NITROGEN',about:'diet and trophic position',at:7.4},
 {sym:'S',name:'SULFUR',about:'water and bedrock weathering',at:10.1},
 {sym:'Sr',name:'STRONTIUM',about:'local geology and water',at:13.0}];
// Irregular sample spacing for the sparse-record diagram. Seeded, never re-randomised
// inside draw(), so seeks stay reproducible.
const SAMPLES=[];
for(let i=0;i<11;i++){
 const h=(Math.imul(i+3,2654435761)>>>0)/4294967296;
 SAMPLES.push({x:0.02+i*0.089+h*0.024,y:0.5+(((Math.imul(i+11,1597334677)>>>0)/4294967296)-0.5)*0.5});
}
SAMPLES.sort((a,b)=>a.x-b.x);
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;
 g.fillStyle='#f0ede4';g.fillRect(0,0,W,H);
 const grd=g.createLinearGradient(0,0,0,H);grd.addColorStop(0,'rgba(255,253,246,.6)');grd.addColorStop(1,'rgba(206,200,186,.30)');
 g.fillStyle=grd;g.fillRect(0,0,W,H);
 for(let k=0;k<2400;k++){const h1=(Math.imul(k+1,2654435761)>>>0)/4294967296,h2=(Math.imul(k+7,1597334677)>>>0)/4294967296,h3=(Math.imul(k+13,2246822519)>>>0)/4294967296;
  g.fillStyle=h3<.5?`rgba(78,72,60,${.012+h2*.018})`:`rgba(255,255,255,${.012+h2*.018})`;g.fillRect(h1*W,h2*H,1+h3*2,1+h3*2)}
 const intro=smooth(t/1.5);
 text('THE SECOND WITNESS IS CHEMISTRY',96,124,38,'700',.92*intro);
 text('Carbon, nitrogen, sulfur and strontium, read from collagen and bone',96,162,20,'500',.64*intro,'left','52,58,58');
 g.fillStyle=`rgba(32,38,40,${.20*intro})`;g.fillRect(96,184,1088,2);

 // --- shot 0: the register of witnesses -------------------------------------------
 const regOut=1-smooth((t-15.8)/1.8);
 if(regOut>0.01){
  SYSTEMS.forEach((s,i)=>{
   const a=smooth((t-s.at)/.9)*regOut;if(a<=0)return;
   const x=96+i*272,y=238;
   g.save();g.globalAlpha=a*.55;
   g.fillStyle='rgba(255,253,246,.55)';g.fillRect(x,y,248,164);
   g.strokeStyle='rgba(32,38,40,.20)';g.lineWidth=1;g.strokeRect(x+.5,y+.5,248,164);
   g.restore();
   text(s.sym,x+18,y+62,40,'700',.9*a,'left',i%2?'140,104,40':'56,86,96');
   text(s.name,x+18,y+92,14,'700',.72*a);
   text('reports on',x+18,y+118,12,'700',.46*a,'left','70,76,76');
   text(s.about,x+18,y+140,13.5,'500',.72*a,'left','46,52,54');
  });
  const a=smooth((t-14.0)/1.4)*regOut;
  if(a>0)text('Each system answers a different question; none of them answers all of them.',96,444,17,'500',.6*a,'left','58,64,64');
  const b=smooth((t-13.6)/1.5)*regOut;
  if(b>0){
   g.save();g.globalAlpha=.18*b;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,486,1088,1);g.restore();
   text('EVERY VALUE COMES FROM A PARTICULAR ANIMAL, TISSUE AND SPAN OF TIME',96,522,16,'700',.74*b);
   text('A bone, a tooth and a collagen sample do not average the same years — so the record',96,556,16.5,'500',.58*b,'left','58,64,64');
   text('is a set of observations, not a continuous log.',96,580,16.5,'500',.58*b,'left','58,64,64');
  }
 }

 // --- shots 1-2: comparison then the sparse record ---------------------------------
 const cmp=smooth((t-16.6)/1.5)*(1-smooth((t-33.9)/1.6));
 if(cmp>0){
  text('2019 · WRANGEL COMPARED WITH OTHER NORTHERN REGIONS',96,232,15,'700',.72*cmp);
  // Two rows, each a sampled band rather than a plotted series. The label says what the
  // narration says: the values stayed broadly stable.
  const rows=[{y:300,label:'CARBON',col:'56,86,96'},{y:388,label:'NITROGEN',col:'140,104,40'}];
  rows.forEach((r,i)=>{
   const a=cmp*smooth((t-(19.2+i*1.6))/.9);if(a<=0)return;
   text(r.label,96,r.y+20,14,'700',.8*a,'left',r.col);
   const bx=240,bw=760;
   g.save();g.globalAlpha=a*.30;g.fillStyle=`rgba(${r.col},.55)`;
   g.fillRect(bx,r.y+6,bw,26);g.restore();
   g.save();g.globalAlpha=a;
   g.strokeStyle=`rgba(${r.col},.85)`;g.lineWidth=2;
   g.beginPath();g.moveTo(bx,r.y+6);g.lineTo(bx+bw,r.y+6);g.moveTo(bx,r.y+32);g.lineTo(bx+bw,r.y+32);g.stroke();
   g.restore();
   text('BROADLY STABLE ACROSS THE SAMPLES STUDIED',bx,r.y+54,12.5,'700',.66*a,'left',r.col);
  });
  const a=smooth((t-24.9)/1.4)*cmp;
  if(a>0)text('That weighs against some gradual dietary changes.',96,498,19,'700',.8*a);
  const b=smooth((t-28.3)/1.4)*cmp;
  if(b>0){
   text('It does not prove the herd was healthy, or that the island always offered easy conditions.',96,532,17,'500',.66*b,'left','58,64,64');
   text('This is a comparison of the samples studied — not of every season the island had.',96,562,17,'500',.5*b,'left','70,76,76');
  }
 }

 // --- shot 2: the sparse record ----------------------------------------------------
 const sparse=smooth((t-34.6)/1.6);
 if(sparse>0){
  text('NOT A WEATHER STATION',96,232,26,'700',.92*sparse);
  const bx=96,by=286,bw=1088,bh=186;
  g.save();g.globalAlpha=sparse;
  // the unrecorded span between samples, drawn as the dominant area
  g.fillStyle='rgba(150,64,52,.09)';g.fillRect(bx,by+34,bw,bh-34);
  g.strokeStyle='rgba(32,38,40,.28)';g.lineWidth=1.4;
  g.beginPath();g.moveTo(bx,by+34);g.lineTo(bx+bw,by+34);g.moveTo(bx,by+bh);g.lineTo(bx+bw,by+bh);g.stroke();
  g.restore();
  SAMPLES.forEach((s,i)=>{
   const a=sparse*smooth((t-(36.0+i*0.32))/.7);if(a<=0)return;
   const x=bx+s.x*bw,y=by+52+s.y*(bh-72);
   g.save();g.globalAlpha=a;g.fillStyle='rgba(56,86,96,.9)';
   g.beginPath();g.arc(x,y,5,0,Math.PI*2);g.fill();g.restore();
  });
  const a=smooth((t-39.9)/1.5)*sparse;
  if(a>0)text('SAMPLE · ONE PARTICULAR ANIMAL AND TISSUE',bx,by+bh+30,13,'700',.62*a,'left','56,86,96');
  const b=smooth((t-42.0)/1.5)*sparse;
  if(b>0)text('UNRECORDED · A RAPID EVENT COULD FALL HERE',bx+bw,by+bh+30,13,'700',.62*b,'right','150,64,52');
  const c=smooth((t-44.4)/1.5)*sparse;
  if(c>0){
   text('A stable sampled signal can coexist with seasonal stress,',96,576,19,'700',.82*c);
   text('and a rapid event can escape a record that is sparse in time.',96,606,19,'700',.82*c);
  }
 }
 text('SCHEMATIC · NO ISOTOPE VALUES OR AXES ARE DEPICTED · 2019 COMPARISON',1184,H-16,12,'700',.4,'right');
 return{time:t,shot:shotIndex(t),shot_name:SHOTS[shotIndex(t)].n,animals:0,triangles:0,historical_geography:false,systems:4,samples:SAMPLES.length,sparseRecord:sparse,numericAxis:false};
}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
