// Isolation section — sea level rises and the island is cut off (86-114 s).
//
// Honest scope: this is a SCHEMATIC of a process, not a palaeogeographic
// reconstruction. The real ancient shoreline of the Wrangel shelf is not known at
// the precision a coastline drawing would imply, so the plate shows a labelled
// cross-section — land, shelf, rising water — rather than a map pretending to be
// 10,000 years old. No modern coastline is traced here.
//
// It also carries the "other populations" beat: three separate lifelines, marked at
// the approximations the narration speaks, never compared as a single story.
import * as T from 'three';
const W=1280,H=720,FPS=30,DURATION=28;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
await document.fonts.load('700 24px Manrope');await document.fonts.load('500 20px Manrope');
const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};const lerp=(a,b,u)=>a+(b-a)*u;
const SHOTS=[{n:'the shelf, before',s:0,e:9},{n:'the water rises',s:9,e:18},{n:'separate histories',s:18,e:28}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
function text(str,x,y,size,weight='700',alpha=1,align='left',color='32,38,40'){
 g.fillStyle=`rgba(${color},${alpha})`;g.font=`${weight} ${size}px Manrope`;g.textAlign=align;g.fillText(str,x,y);
}
// Cross-section geometry, in screen space.
const SEC={x0:150,x1:1130,seaY:404};const landY=300;
const MAINLAND={x0:150,x1:470};
const ISLAND={x0:760,x1:1000};
// Waterline rises from the shelf floor to the present sea level across shot 1.
function seaLevel(t){const u=smooth((t-9)/7.5);return lerp(SEC.seaY+48,SEC.seaY,u)}
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;
 g.fillStyle='#f0ede4';g.fillRect(0,0,W,H);
 const grd=g.createLinearGradient(0,0,0,H);grd.addColorStop(0,'rgba(255,253,246,.6)');grd.addColorStop(1,'rgba(206,200,186,.30)');
 g.fillStyle=grd;g.fillRect(0,0,W,H);
 for(let k=0;k<2400;k++){const h1=(Math.imul(k+1,2654435761)>>>0)/4294967296,h2=(Math.imul(k+7,1597334677)>>>0)/4294967296,h3=(Math.imul(k+13,2246822519)>>>0)/4294967296;
  g.fillStyle=h3<.5?`rgba(78,72,60,${.012+h2*.018})`:`rgba(255,255,255,${.012+h2*.018})`;g.fillRect(h1*W,h2*H,1+h3*2,1+h3*2)}
 const intro=smooth(t/1.4);
 text('TEN THOUSAND YEARS AGO',96,126,40,'700',.92*intro);
 text('Sea level rises; a population loses its route back',96,164,20,'500',.64*intro,'left','52,58,58');
 g.fillStyle=`rgba(32,38,40,${.20*intro})`;g.fillRect(96,186,760,2);

 const sea=seaLevel(t);
 // --- cross-section ---------------------------------------------------------------
 // Shelf and land masses are drawn as flat shapes; this is a diagram, not terrain.
 g.save();
 // water sits only BETWEEN the two land masses, so it never cuts through them
 const waterTop=Math.min(sea,SEC.seaY);
 g.fillStyle='rgba(86,140,160,.42)';g.fillRect(MAINLAND.x1,waterTop,ISLAND.x0-MAINLAND.x1,SEC.seaY+64-waterTop);
 g.strokeStyle='rgba(56,110,132,.85)';g.lineWidth=2.2;
 g.beginPath();g.moveTo(MAINLAND.x1,waterTop);g.lineTo(ISLAND.x0,waterTop);g.stroke();
 // a thin sea line beyond each coast, drawn UNDER the land silhouette
 g.strokeStyle='rgba(56,110,132,.45)';g.lineWidth=1.6;
 g.beginPath();g.moveTo(SEC.x0,SEC.seaY);g.lineTo(MAINLAND.x0,SEC.seaY);g.stroke();
 g.beginPath();g.moveTo(ISLAND.x1,SEC.seaY);g.lineTo(SEC.x1,SEC.seaY);g.stroke();
 // land masses (mainland left, island right, both above the current waterline)
 const landFill='rgba(122,112,88,.92)',landEdge='rgba(72,64,46,.95)';
 for(const m of [MAINLAND,ISLAND]){
  g.fillStyle=landFill;g.strokeStyle=landEdge;g.lineWidth=2.4;
  g.beginPath();g.moveTo(m.x0,SEC.seaY+64);g.lineTo(m.x0,landY);
  g.quadraticCurveTo((m.x0+m.x1)/2,landY-34,m.x1,landY);g.lineTo(m.x1,SEC.seaY+64);g.closePath();g.fill();g.stroke();
 }
 // the connecting shelf: floods as the water rises
 const shelfTop=lerp(SEC.seaY+40,SEC.seaY+8,smooth((t-9)/7.5));
 g.fillStyle=`rgba(122,112,88,${.55*(1-smooth((t-11)/6))})`;
 g.fillRect(MAINLAND.x1,shelfTop,ISLAND.x0-MAINLAND.x1,Math.max(0,SEC.seaY+64-shelfTop));
 g.restore();
 // labels
 const l1=smooth((t-1.6)/1.2);
 text('MAINLAND',(MAINLAND.x0+MAINLAND.x1)/2,landY-52,16,'700',.75*l1,'center','52,46,34');
 text('SHELF',(MAINLAND.x1+ISLAND.x0)/2,landY+58,15,'700',.55*l1*(1-smooth((t-13)/3)),'center','72,64,46');
 text('ISLAND',(ISLAND.x0+ISLAND.x1)/2,landY-52,16,'700',.75*l1,'center','52,46,34');
 const cut=smooth((t-14)/2.4);
 text('ROUTE CUT',(MAINLAND.x1+ISLAND.x0)/2,landY+18,17,'700',.9*cut,'center','150,64,52');
 // --- separate histories (shot 2) --------------------------------------------------
 const sep=smooth((t-18.2)/1.8);
 if(sep>0){
  g.fillStyle=`rgba(240,237,228,${.96*sep})`;g.fillRect(0,486,W,H-486);
  text('THREE POPULATIONS, THREE HISTORIES',96,530,22,'700',.9*sep);
  const rows=[['WRANGEL ISLAND','persisted for thousands of years'],
              ['EAST EUROPEAN PLAIN','gone ~15,000 years ago'],
              ['ST PAUL ISLAND, ALASKA','gone ~5,600 years ago']];
  rows.forEach((r,i)=>{
   const a=sep*smooth((t-18.6-i*.55)/.9);if(a<=0)return;
   const y=566+i*30;
   text(r[0],96,y,15,'700',.8*a);
   text(r[1],400,y,15,'500',.66*a,'left','58,64,64');
  });
  text('Dates are the approximations spoken in the narration.',96,682,13,'500',.5*sep,'left','86,92,92');
 }
 text('SCHEMATIC CROSS-SECTION · NOT A PALAEOGEOGRAPHIC RECONSTRUCTION',1130,H-16,12,'700',.44,'right');
 return{time:t,shot:shotIndex(t),shot_name:SHOTS[shotIndex(t)].n,animals:0,triangles:0,historical_geography:false,sea_level:sea,cut,separate:sep}}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
