// New lead section — the 2025 microbial study, and why "related" is not "responsible"
// (652-689 s).
//
// This is the section where a dramatic reveal is cheapest and most dishonest: a
// pathogen, a plague, a dying herd. The narration's own sentence is "Related does not
// mean responsible", and the study did not identify a disease. So the picture is an
// evidence ladder — what was found, what it is related to, and the gap where a
// diagnosis would go — with the empty rung left visibly empty.
import * as T from 'three';
const W=1280,H=720,FPS=30,DURATION=37;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
await document.fonts.load('700 24px Manrope');await document.fonts.load('500 20px Manrope');
const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};const lerp=(a,b,u)=>a+(b-a)*u;
const SHOTS=[{n:'hundreds of specimens',s:0,e:10},{n:'related, not responsible',s:10,e:20},{n:'the controls',s:20,e:29},{n:'the rung that is missing',s:29,e:37}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
function text(str,x,y,size,weight='700',alpha=1,align='left',color='32,38,40'){
 g.fillStyle=`rgba(${color},${alpha})`;g.font=`${weight} ${size}px Manrope`;g.textAlign=align;g.fillText(str,x,y);
}
// Specimen ticks: a count band, not a photograph array. Seeded, so seeks are stable.
const TICKS=[];
for(let i=0;i<160;i++){
 const h1=(Math.imul(i+1,2654435761)>>>0)/4294967296;
 const h2=(Math.imul(i+7,1597334677)>>>0)/4294967296;
 TICKS.push({x:h1,y:h2*.85});
}
const LADDER=[{label:'MICROBIAL DNA RECOVERED',state:'found',y:0},
 {label:'RELATED TO KNOWN PATHOGENS',state:'related',y:1},
 {label:'AUTHENTICATED · CONTROLS',state:'checked',y:2},
 {label:'A DISEASE THAT KILLED THEM',state:'missing',y:3}];
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;
 g.fillStyle='#f0ede4';g.fillRect(0,0,W,H);
 const grd=g.createLinearGradient(0,0,0,H);grd.addColorStop(0,'rgba(255,253,246,.6)');grd.addColorStop(1,'rgba(206,200,186,.30)');
 g.fillStyle=grd;g.fillRect(0,0,W,H);
 for(let k=0;k<2400;k++){const h1=(Math.imul(k+1,2654435761)>>>0)/4294967296,h2=(Math.imul(k+7,1597334677)>>>0)/4294967296,h3=(Math.imul(k+13,2246822519)>>>0)/4294967296;
  g.fillStyle=h3<.5?`rgba(78,72,60,${.012+h2*.018})`:`rgba(255,255,255,${.012+h2*.018})`;g.fillRect(h1*W,h2*H,1+h3*2,1+h3*2)}
 const intro=smooth(t/1.5);
 text('A NEWER LEAD',96,124,40,'700',.92*intro);
 text('Hundreds of specimens, microbial DNA, and a diagnosis that did not arrive',96,162,20,'500',.64*intro,'left','52,58,58');
 g.fillStyle=`rgba(32,38,40,${.20*intro})`;g.fillRect(96,184,780,2);

 // --- shot 0: the specimen band ---------------------------------------------------
 const band=smooth((t-1.2)/2.4),bandOut=1-smooth((t-9.0)/2.0);
 if(band>.01&&bandOut>.01){
  const a=band*bandOut;
  const bx=96,by=226,bw=1088,bh=150;
  g.save();g.globalAlpha=a;
  for(const k of TICKS){
   const x=bx+k.x*bw,y=by+k.y*bh;
   g.strokeStyle='rgba(56,86,96,.55)';g.lineWidth=1.4;
   g.beginPath();g.moveTo(x,y);g.lineTo(x,y+9);g.stroke();
  }
  // a subtle bounding rule, not a frame
  g.strokeStyle='rgba(32,38,40,.18)';g.lineWidth=1;
  g.beginPath();g.moveTo(bx,by+bh+14);g.lineTo(bx+bw,by+bh+14);g.stroke();
  g.restore();
  text('HUNDREDS OF SPECIMENS · INCLUDING MATERIAL OLDER THAN THE ISLAND POPULATION',96,by+bh+42,14,'700',.62*a);
 }

 // --- shot 1-3: the ladder --------------------------------------------------------
 const ladder=smooth((t-10.4)/1.8);
 if(ladder>0){
  const x0=170;
  LADDER.forEach((row,i)=>{
   const a=ladder*smooth((t-(11.0+i*1.9))/.9);if(a<=0)return;
   const y=268+i*80;
   // rung
   g.strokeStyle='rgba(32,38,40,.22)';g.lineWidth=1.2;
   g.beginPath();g.moveTo(x0,y+34);g.lineTo(x0+880,y+34);g.stroke();
   // state chip
   const col=row.state==='missing'?'150,64,52':row.state==='related'?'140,104,40':'56,86,96';
   g.save();g.globalAlpha=a;
   if(row.state==='missing'){
    g.setLineDash([6,6]);g.strokeStyle=`rgba(${col},.85)`;g.lineWidth=2;
    g.strokeRect(x0,y+2,250,32);g.setLineDash([]);
   }else{
    g.strokeStyle=`rgba(${col},.9)`;g.lineWidth=2;g.strokeRect(x0,y+2,250,32);
   }
   g.restore();
   text(row.state==='missing'?'NOT ESTABLISHED':'ESTABLISHED',x0+14,y+24,14,'700',.85*a,'left',col);
   text(row.label,x0+280,y+25,19,'700',row.state==='missing'?.72*a:.86*a,'left',row.state==='missing'?'62,66,66':'40,46,48');
   if(row.state==='missing'){
    // the empty rung: an explicit absence, not a hidden one
    g.save();g.globalAlpha=.5*a;g.setLineDash([3,5]);
    g.strokeStyle='rgba(150,64,52,.8)';g.lineWidth=1.4;
    g.beginPath();g.moveTo(x0+600,y+30);g.lineTo(x0+880,y+30);g.stroke();g.restore();
    text('no disease was identified',x0+600,y-4,13,'500',.6*a,'left','150,64,52');
   }
  });
 }
 // --- shot 1 callout and shot 2 caveat --------------------------------------------
 const related=smooth((t-16.6)/1.4)*smooth((20.6-t)/1.2);
 if(related>0){
  text('RELATED DOES NOT MEAN RESPONSIBLE',96,610,26,'700',.9*related);
  text('A bacterium resembling a known pathogen is a lead, not a cause of death.',96,644,18,'500',.66*related,'left','58,64,64');
 }
 const ctrl=smooth((t-20.6)/1.6);
 if(ctrl>0&&t<29.6){
  text('AUTHENTICATION AND CONTAMINATION CONTROL COME FIRST',96,610,24,'700',.88*ctrl);
  text('Ancient microbial DNA is easy to introduce and hard to authenticate; the study',96,644,18,'500',.66*ctrl,'left','58,64,64');
  text('compared against living relatives to open questions, not to close them.',96,668,18,'500',.66*ctrl,'left','58,64,64');
 }
 // --- shot 3 ---------------------------------------------------------------------
 const end=smooth((t-29.6)/1.6);
 if(end>0){
  text('THE DIAGNOSIS IS STILL MISSING',96,610,30,'700',.92*end);
  text('No disease has been identified as the killer of the Wrangel mammoths.',96,648,18,'500',.68*end,'left','58,64,64');
  text('The health effects of the ancient microbes remain uncertain.',96,672,18,'500',.68*end,'left','58,64,64');
 }
 text('SCHEMATIC · STATES AS DESCRIBED IN THE NARRATION · 2025 MICROBIAL STUDY',1130,H-16,12,'700',.4,'right');
 return{time:t,shot:shotIndex(t),shot_name:SHOTS[shotIndex(t)].n,animals:0,triangles:0,historical_geography:false,ticks:TICKS.length,ladder,diagnosisMissing:end}}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
