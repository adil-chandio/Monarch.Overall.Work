// Coverage section — why "more damage" can just mean "more readable" (557-585 s).
//
// The narration's own analogy is a room seen through windows of different sizes: the
// larger window reveals more of the same room without the room being worse. That is
// drawn literally here, because the analogy is the argument and any substitution
// (glowing genomes, cracked DNA) would smuggle in a claim the section is refusing.
//
// Two plates: the size mismatch, then the same room at equal coverage with the
// difference gone. No sequence, no specimens, no damage rendered as physical damage.
import * as T from 'three';
const W=1280,H=720,FPS=30,DURATION=20;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
await document.fonts.load('700 24px Manrope');await document.fonts.load('500 20px Manrope');
const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};const lerp=(a,b,u)=>a+(b-a)*u;
const SHOTS=[{n:'unequal windows',s:0,e:7},{n:'the same room',s:7,e:14},{n:'coverage is not condition',s:14,e:20}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
function text(str,x,y,size,weight='700',alpha=1,align='left',color='32,38,40'){
 g.fillStyle=`rgba(${color},${alpha})`;g.font=`${weight} ${size}px Manrope`;g.textAlign=align;g.fillText(str,x,y);
}
// The "room": a fixed field of marks in normalised 0-1 space. It never changes.
const ROOM=[];
// Every multiplier must be large enough to spread the low bits; a small one (40503)
// collapsed every y value onto the same line and the plate drew as empty windows.
for(let i=0;i<140;i++){
 const h1=(Math.imul(i+1,2654435761)>>>0)/4294967296;
 const h2=(Math.imul(i+7,1597334677)>>>0)/4294967296;
 const h3=(Math.imul(i+13,2246822519)>>>0)/4294967296;
 ROOM.push({x:.05+h1*.90,y:.05+h2*.90,dark:h3<.5})}
// A window crops the room by taking a sub-rectangle of that same space. The small
// window sees fewer marks because it sees less of the room — nothing else differs.
const SUB={small:{x0:.34,y0:.34,x1:.62,y1:.62},large:{x0:.06,y0:.08,x1:.94,y1:.92}};
const WIN={small:{x:236,y:300,w:196,h:196},large:{x:556,y:250,w:340,h:340}};
function inSub(r,sb){return r.x>=sb.x0&&r.x<=sb.x1&&r.y>=sb.y0&&r.y<=sb.y1}
function countMarks(sb){let n=0;for(const r of ROOM)if(inSub(r,sb))n++;return n}
function drawWindow(win,sb,alpha,label,col){
 g.save();g.globalAlpha=alpha;
 g.fillStyle='rgba(255,253,246,.86)';g.fillRect(win.x,win.y,win.w,win.h);
 // faint rule grid so both windows read as the same instrument
 g.strokeStyle='rgba(32,38,40,.09)';g.lineWidth=1;
 for(let i=1;i<6;i++){const gx=win.x+win.w*i/6,gy=win.y+win.h*i/6;
  g.beginPath();g.moveTo(gx,win.y);g.lineTo(gx,win.y+win.h);g.stroke();
  g.beginPath();g.moveTo(win.x,gy);g.lineTo(win.x+win.w,gy);g.stroke();}
 for(const r of ROOM){
  if(!inSub(r,sb))continue;
  const rx=win.x+((r.x-sb.x0)/(sb.x1-sb.x0))*win.w;
  const ry=win.y+((r.y-sb.y0)/(sb.y1-sb.y0))*win.h;
  g.fillStyle=r.dark?'rgba(60,56,48,.66)':`rgba(${col},.92)`;
  g.beginPath();g.arc(rx,ry,3.4,0,Math.PI*2);g.fill();
 }
 g.strokeStyle=`rgba(${col},.95)`;g.lineWidth=3;g.strokeRect(win.x,win.y,win.w,win.h);
 g.restore();
 text(label,win.x,win.y-18,15,'700',alpha,'left',col);
 text(countMarks(sb)+' MARKS IN VIEW',win.x,win.y+win.h+30,15,'700',alpha*.72,'left',col);
}
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;
 g.fillStyle='#f0ede4';g.fillRect(0,0,W,H);
 const grd=g.createLinearGradient(0,0,0,H);grd.addColorStop(0,'rgba(255,253,246,.6)');grd.addColorStop(1,'rgba(206,200,186,.30)');
 g.fillStyle=grd;g.fillRect(0,0,W,H);
 for(let k=0;k<2400;k++){const h1=(Math.imul(k+1,2654435761)>>>0)/4294967296,h2=(Math.imul(k+7,40503)>>>0)/4294967296,h3=(Math.imul(k+13,2246822519)>>>0)/4294967296;
  g.fillStyle=h3<.5?`rgba(78,72,60,${.012+h2*.018})`:`rgba(255,255,255,${.012+h2*.018})`;g.fillRect(h1*W,h2*H,1+h3*2,1+h3*2)}
 const intro=smooth(t/1.4);
 text('COVERAGE IS NOT CONDITION',96,132,40,'700',.92*intro);
 text('A shallow sequence can miss what a better-covered genome shows',96,170,20,'500',.64*intro,'left','52,58,58');
 g.fillStyle=`rgba(32,38,40,${.20*intro})`;g.fillRect(96,192,700,2);
 const s0=shotIndex(t)<2;
 // --- plate one / two: the two windows -------------------------------------------
 if(t<14.2){
  const a1=smooth((t-1.2)/1.2)*smooth((14.2-t)/1.2);
  drawWindow(WIN.small,SUB.small,a1,'SHALLOW · FEWER READABLE BASES','150,64,52');
  drawWindow(WIN.large,SUB.large,a1,'DEEPER · MORE READABLE BASES','56,86,96');
  const note=smooth((t-4.6)/1.4)*smooth((14.2-t)/1.2);
  text('Same room. The larger window simply shows more of it.',96,652,20,'500',.78*note,'left','58,64,64');
  text('Counting more marks is not the same as the room being worse.',96,680,20,'500',.78*note,'left','58,64,64');
 }
 // --- plate three: equal coverage, difference gone -------------------------------
 const eq=smooth((t-14.4)/1.6);
 if(eq>0){
  g.save();g.globalAlpha=eq;
  g.fillStyle='rgba(255,253,246,.86)';g.fillRect(340,250,600,330);
  g.strokeStyle='rgba(32,38,40,.09)';g.lineWidth=1;
  for(let i=1;i<6;i++){const gx=340+600*i/6,gy=228+330*i/6;
   g.beginPath();g.moveTo(gx,228);g.lineTo(gx,558);g.stroke();
   g.beginPath();g.moveTo(340,gy);g.lineTo(940,gy);g.stroke();}
  for(const r of ROOM){g.fillStyle=r.dark?'rgba(60,56,48,.60)':'rgba(52,58,60,.92)';
   g.beginPath();g.arc(340+r.x*600,228+r.y*330,3.4,0,Math.PI*2);g.fill();}
  g.strokeStyle='rgba(52,58,60,.92)';g.lineWidth=3;g.strokeRect(340,228,600,330);
  g.restore();
  text('MATCHED COVERAGE',340,210,15,'700',.85*eq,'left','52,58,60');
  text('Compare like with like, and the difference must be tested —',96,646,21,'700',.9*eq);
  text('not assumed to belong to the animals.',96,676,21,'700',.9*eq);
 }
 text('SCHEMATIC · THE WINDOW ANALOGY IS THE NARRATION\'S OWN',1130,H-16,12,'700',.4,'right');
 return{time:t,shot:shotIndex(t),shot_name:SHOTS[shotIndex(t)].n,animals:0,triangles:0,historical_geography:false,room:ROOM.length,windows:t<14.2?2:1,equal:eq}}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
