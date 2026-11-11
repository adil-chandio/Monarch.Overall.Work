// Other islands section — St Paul, and why regional clues differ (114-130 s).
//
// Two statements follow each other quickly here and neither is a claim this production
// can illustrate literally: St Paul Island's mammoths lasted until about 5,600 years
// ago, and isotopic changes from different regions give clues about diet and environment
// "although the details are not the same everywhere".
//
// So the plate carries the St Paul duration as a labelled bar against the Wrangel span
// already used in `isolation-section`, then opens a *regional comparison* in which the
// columns visibly differ — because that difference is the point. Nothing is mapped and
// no coastline is traced.
import * as T from 'three';
const W=1280,H=720,FPS=30,DURATION=16;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
await document.fonts.load('700 24px Manrope');await document.fonts.load('500 20px Manrope');
const S=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};
const SHOTS=[{n:'st paul',s:0,e:8.6},{n:'the details differ',s:8.6,e:16}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
function text(str,x,y,size,weight='700',alpha=1,align='left',color='32,38,40'){
 g.fillStyle=`rgba(${color},${alpha})`;g.font=`${weight} ${size}px Manrope`;g.textAlign=align;g.fillText(str,x,y);
}
// Three regional signatures, drawn as different *shapes* rather than plotted values.
// The narration says the details are not the same everywhere; equal shapes would deny it
// and precise values would invent data.
const REGIONS=[
 {l:'ST PAUL ISLAND',lines:['a separate island record,','ending later than Wrangel'],at:9.4},
 {l:'WRANGEL ISLAND',lines:['the record this film','follows most closely'],at:10.6},
 {l:'MAINLAND SITES',lines:['other regions, with','their own conditions'],at:11.8}];
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;
 g.fillStyle='#f0ede4';g.fillRect(0,0,W,H);
 const grd=g.createLinearGradient(0,0,0,H);grd.addColorStop(0,'rgba(255,253,246,.6)');grd.addColorStop(1,'rgba(206,200,186,.30)');
 g.fillStyle=grd;g.fillRect(0,0,W,H);
 for(let k=0;k<2400;k++){const h1=(Math.imul(k+1,2654435761)>>>0)/4294967296,h2=(Math.imul(k+7,1597334677)>>>0)/4294967296,h3=(Math.imul(k+13,2246822519)>>>0)/4294967296;
  g.fillStyle=h3<.5?`rgba(78,72,60,${.012+h2*.018})`:`rgba(255,255,255,${.012+h2*.018})`;g.fillRect(h1*W,h2*H,1+h3*2,1+h3*2)}
 const intro=S(t/1.3);
 text('ANOTHER ISLAND, ANOTHER ANSWER',96,124,38,'700',.92*intro);
 text('St Paul lasted longer than the mainland — and regional clues are not uniform',96,162,19,'500',.62*intro,'left','52,58,58');
 g.fillStyle=`rgba(32,38,40,${.20*intro})`;g.fillRect(96,184,1088,2);

 // --- shot 0: St Paul's span --------------------------------------------------------
 const sp=S((t-0.7)/1.3)*(1-S((t-8.0)/1.2));
 if(sp>0){
  text('ST PAUL ISLAND, ALASKA',96,236,22,'700',.88*sp);
  const bx=96,bw=1088,by=286;
  // One bar, ending at the spoken date. No start date is spoken, so the left end is
  // drawn as an open fade rather than a number.
  const a=sp*S((t-1.8)/1.2);
  if(a>0){
   // A span bounded at one end only. The right edge is the spoken date; the left edge is
   // drawn as an open bracket, because the narration gives no start date and a bar of
   // arbitrary length would invent one.
   const yTop=by+6,yBot=by+96;
   g.save();g.globalAlpha=.5*a;
   g.fillStyle='rgba(56,86,96,.10)';g.fillRect(bx,yTop,bw,yBot-yTop);
   g.strokeStyle='rgba(56,86,96,.55)';g.lineWidth=1.4;
   g.beginPath();g.moveTo(bx,yTop);g.lineTo(bx+bw,yTop);g.moveTo(bx,yBot);g.lineTo(bx+bw,yBot);g.stroke();
   g.restore();
   // the open left end
   g.save();g.globalAlpha=.75*a;g.strokeStyle='rgba(32,38,40,.55)';g.lineWidth=2;
   g.beginPath();g.moveTo(bx-8,yTop);g.lineTo(bx,yTop);g.moveTo(bx-8,yBot);g.lineTo(bx,yBot);g.stroke();
   g.setLineDash([5,6]);g.beginPath();g.moveTo(bx-20,(yTop+yBot)/2);g.lineTo(bx,(yTop+yBot)/2);g.stroke();g.setLineDash([]);
   g.restore();
   // the dated right edge
   g.save();g.globalAlpha=.9*a;g.strokeStyle='rgba(32,38,40,.7)';g.lineWidth=2.5;
   g.beginPath();g.moveTo(bx+bw,yTop-12);g.lineTo(bx+bw,yBot+12);g.stroke();g.restore();
   text('LASTED UNTIL ABOUT 5,600 YEARS AGO',bx+bw,yTop-18,15,'700',.84*a,'right','32,38,40');
   text('not dated here',bx+8,(yTop+yBot)/2+5,13.5,'700',.5*a,'left','92,96,96');
   text('The narration gives no start date for this record, so none is drawn.',bx,by+124,13.5,'500',.44*a,'left','70,76,76');
  }
  const b=sp*S((t-4.6)/1.3);
  if(b>0){
   g.save();g.globalAlpha=.16*b;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,454,1088,1);g.restore();
   text('A LATER LOSS IS A DIFFERENT HISTORY',96,494,20,'700',.86*b);
   text('The three populations did not end together, and a date on one island is not a',96,526,17,'500',.6*b,'left','58,64,64');
   text('statement about the others.',96,550,17,'500',.6*b,'left','58,64,64');
  }
 }

 // --- shot 1: the details are not the same everywhere --------------------------------
 const diff=S((t-8.7)/1.4);
 if(diff>0){
  text('THE DETAILS ARE NOT THE SAME EVERYWHERE',96,236,23,'700',.9*diff);
  const a=diff*S((t-9.2)/1.1);
  if(a>0)text('Isotopic changes can point to shifts in diet and environment — but the pattern differs by region.',96,266,16,'500',.56*a,'left','58,64,64');
  REGIONS.forEach((r,i)=>{
   const q=diff*S((t-r.at)/1.1);if(q<=0)return;
   const x=96+i*368,y=310,wd=336,ht=118;
   g.save();g.globalAlpha=.34*q;g.fillStyle='rgba(255,253,246,.8)';g.fillRect(x,y,wd,ht);
   g.strokeStyle='rgba(32,38,40,.15)';g.lineWidth=1;g.strokeRect(x+.5,y+.5,wd,ht);g.restore();
   text(r.l,x+16,y+30,12.5,'700',.7*q,'left',i===1?'56,86,96':'70,76,76');
   // Each card names the kind of record it holds, not a trend: a drawn series would read
   // as measured isotope values this production does not have.
   r.lines.forEach((ln,i)=>text(ln,x+16,y+62+i*22,14.5,'500',.54*q,'left','58,64,64'));
  });
  const d=diff*S((t-12.6)/1.2);
  if(d>0)text('No series is drawn here: the narration describes a difference in pattern, not values.',96,462,15,'500',.44*d,'left','70,76,76');
  const c=diff*S((t-13.4)/1.3);
  if(c>0){
   g.save();g.globalAlpha=.16*c;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,492,1088,1);g.restore();
   text('A pattern from one region cannot be carried straight across to another.',96,532,18,'500',.66*c,'left','58,64,64');
  }
 }
 text('SCHEMATIC · NO COASTLINE IS MAPPED · PATTERNS ARE NOT MEASURED SERIES',1184,H-16,12,'700',.4,'right');
 return{time:t,shot:shotIndex(t),shot_name:SHOTS[shotIndex(t)].n,animals:0,triangles:0,historical_geography:false,
  coastlineTraced:false,valuesPrinted:false,regions:3};
}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
