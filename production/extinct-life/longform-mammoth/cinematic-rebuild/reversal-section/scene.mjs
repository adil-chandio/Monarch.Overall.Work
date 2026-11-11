// 2024 reversal section — the modelled bottleneck and its recovery (473-517 s).
//
// This is the chapter's payoff and the easiest place in the film to mislead a viewer.
// The narration says the effective population size fell to eight or fewer and
// recovered to two to three hundred "within roughly twenty generations", then says
// plainly that effective size is a model parameter and NOT a census. So the picture
// is a labelled model curve, not a herd: no animal count, no surviving-eight-animals
// tableau, no recovering herd that "proves" the number.
//
// The curve is drawn from the model's own reported numbers and is explicitly marked
// as MODELLED. Everything else — paper, type, axes — is authored production design.
import * as T from 'three';
const W=1280,H=720,FPS=30,DURATION=22;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
await document.fonts.load('700 24px Manrope');await document.fonts.load('500 20px Manrope');
const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};const lerp=(a,b,u)=>a+(b-a)*u;
// Model numbers, exactly as spoken. The 8 is an upper bound ("eight or fewer").
const N0=8,N1=250,TRIM=8; // effective size floor, recovered plateau, duration model
// A two-phase curve: near-linear recovery over ~20 generations, then a long plateau.
function ne(gen){if(gen<=0)return N0;const t=Math.min(1,gen/20);return N0+(N1-N0)*(1-Math.pow(1-t,1.9));}
const PLOT={x0:188,x1:1092,y0:286,y1:600};
const GEN_MAX=60,NE_MAX=300;
const px=g=>lerp(PLOT.x0,PLOT.x1,g/GEN_MAX),py=n=>lerp(PLOT.y1,PLOT.y0,n/NE_MAX);
const SHOTS=[{n:'twenty one genomes',s:0,e:6},{n:'the bottleneck',s:6,e:12},{n:'the modelled recovery',s:12,e:18},{n:'not a head count',s:18,e:22}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
function text(str,x,y,size,weight='700',alpha=1,align='left',color='32,38,40'){
 g.fillStyle=`rgba(${color},${alpha})`;g.font=`${weight} ${size}px Manrope`;g.textAlign=align;g.fillText(str,x,y);
}
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;
 // Paper ground: fixed hash noise, so a repeated seek redraws identically.
 g.fillStyle='#f0ede4';g.fillRect(0,0,W,H);
 const grd=g.createLinearGradient(0,0,0,H);grd.addColorStop(0,'rgba(255,253,246,.6)');grd.addColorStop(1,'rgba(206,200,186,.30)');
 g.fillStyle=grd;g.fillRect(0,0,W,H);
 for(let k=0;k<2400;k++){const h1=(Math.imul(k+1,2654435761)>>>0)/4294967296,h2=(Math.imul(k+7,40503)>>>0)/4294967296,h3=(Math.imul(k+13,2246822519)>>>0)/4294967296;
  g.fillStyle=h3<.5?`rgba(78,72,60,${.012+h2*.018})`:`rgba(255,255,255,${.012+h2*.018})`;g.fillRect(h1*W,h2*H,1+h3*2,1+h3*2)}
 const intro=smooth(t/1.5);
 text('THE MODELLED BOTTLENECK',96,132,40,'700',.92*intro);
 text('Effective population size — a genetic estimate, not a head count',96,170,20,'500',.66*intro,'left','52,58,58');
 g.fillStyle=`rgba(32,38,40,${.20*intro})`;g.fillRect(96,192,660,2);
 // --- the 21-genome tally (shot 0) ------------------------------------------------
 const tally=smooth((t-1.0)/2.2),tallyOut=1-smooth((t-4.2)/1.6);
 if(tally>.01&&tallyOut>.01){
  const a=tally*tallyOut;
  // Seven mainland and fourteen Wrangel marks: one per genome, not a photo array.
  for(let i=0;i<21;i++){
   const row=i<7?0:1,col=i<7?i:i-7;
   const x=196+col*44,y=262+row*54;
   g.save();g.globalAlpha=a;
   g.strokeStyle=i<7?'rgba(56,86,96,.9)':'rgba(150,110,52,.9)';g.lineWidth=2;
   g.beginPath();g.moveTo(x,y-13);g.lineTo(x+9,y-9);g.lineTo(x+9,y+11);g.lineTo(x,y+15);g.lineTo(x-9,y+11);g.lineTo(x-9,y-9);g.closePath();g.stroke();
   g.restore();
  }
  text('7 MAINLAND',196,384,16,'700',.72*a);
  text('14 WRANGEL',196,442,16,'700',.72*a);
  text('21 GENOMES · ~50,000 YEARS',196,486,15,'500',.56*a,'left','86,92,92');
 }
 // --- axes (from shot 1 on) -------------------------------------------------------
 const axes=smooth((t-5.6)/1.8);
 if(axes>0){
  g.strokeStyle=`rgba(32,38,40,${.45*axes})`;g.lineWidth=1.6;
  g.beginPath();g.moveTo(PLOT.x0,PLOT.y0);g.lineTo(PLOT.x0,PLOT.y1);g.lineTo(PLOT.x1,PLOT.y1);g.stroke();
  // Horizontal guide at the recovered plateau.
  g.setLineDash([5,6]);g.strokeStyle=`rgba(150,110,52,${.5*axes})`;
  g.beginPath();g.moveTo(PLOT.x0,py(N1));g.lineTo(PLOT.x1,py(N1));g.stroke();g.setLineDash([]);
  text('~250',PLOT.x0-12,py(N1)+5,14,'700',.6*axes,'right','150,110,52');
  text('8 or fewer',PLOT.x0-12,py(N0)+5,14,'700',.6*axes,'right','120,64,52');
  text('GENERATIONS AFTER ISOLATION →',PLOT.x1,PLOT.y1+34,14,'700',.5*axes,'right','86,92,92');
  text('EFFECTIVE SIZE',PLOT.x0-12,PLOT.y0-14,14,'700',.5*axes,'right','86,92,92');
 }
 // --- the curve (shot 2) ----------------------------------------------------------
 const drawCurve=smooth((t-11.4)/3.2);
 if(drawCurve>0){
  const upTo=GEN_MAX*drawCurve;
  g.strokeStyle='rgba(150,64,52,.95)';g.lineWidth=3.4;g.lineJoin='round';
  g.beginPath();
  for(let gen=0;gen<=upTo;gen+=.4){const x=px(gen),y=py(ne(gen));gen===0?g.moveTo(x,y):g.lineTo(x,y)}
  g.stroke();
  // Fill under the curve, faint.
  g.fillStyle='rgba(150,64,52,.07)';g.beginPath();g.moveTo(px(0),py(ne(0)));
  for(let gen=0;gen<=upTo;gen+=.4)g.lineTo(px(gen),py(ne(gen)));
  g.lineTo(px(upTo),PLOT.y1);g.lineTo(px(0),PLOT.y1);g.closePath();g.fill();
  // Label goes BELOW the plateau line, clear of the curve and the tick label.
  text('MODELLED',px(24),py(N1)+34,15,'700',.8*drawCurve,'left','150,64,52');
  text('not measured, not counted',px(24),py(N1)+53,13,'500',.58*drawCurve,'left','150,64,52');
 }
 // The narration's only quoted rate: ~20 generations to recover.
 if(drawCurve>.55){
  const mx=px(20),a=smooth((drawCurve-.55)/.3);
  g.setLineDash([3,5]);g.strokeStyle=`rgba(32,38,40,${.32*a})`;g.lineWidth=1.2;
  g.beginPath();g.moveTo(mx,PLOT.y0);g.lineTo(mx,PLOT.y1);g.stroke();g.setLineDash([]);
  text('~20 GENERATIONS',mx+8,PLOT.y0+16,13,'700',.55*a,'left','86,92,92');
 }
 // --- the warning (shot 3) --------------------------------------------------------
 const warn=smooth((t-17.2)/1.8);
 if(warn>0){
  g.fillStyle=`rgba(240,237,228,${.92*warn})`;g.fillRect(96,640,1090,54);
  text('EFFECTIVE SIZE ≠ HEADCOUNT',96,674,22,'700',.92*warn);
  text('Eight becoming three hundred is a model parameter, not a count of animals.',520,674,17,'500',.7*warn,'left','58,64,64');
 }
 text('SCHEMATIC · NUMBERS AS SPOKEN IN THE NARRATION · AFTER DEHASQUE ET AL. 2024',96,H-24,13,'700',.42);
 return{time:t,shot:shotIndex(t),shot_name:SHOTS[shotIndex(t)].n,animals:0,triangles:0,historical_geography:false,curve:drawCurve,warn,axes}}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
