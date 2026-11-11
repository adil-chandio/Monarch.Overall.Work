// People section — the human-evidence passage (391-455 s), built as a dated record
// rather than a scene with people in it.
//
// Deliberate choice: no hunters, no figures, no tools "just being found", no staged
// encounter. Every attempt at procedural people and props in this project has read as
// a toy, and inventing an encounter would assert something the narration explicitly
// leaves open. What is shown instead is a plain, off-white field record: two dated
// positions, the uncertain space between them, and a hand-written-looking scale line.
// The numbers and the wording are the point; the picture is a plate, not a claim.
//
// The landscape is invented and appears only as a faint ground plane. Nothing here is
// a photograph, a map, a site plan or an artefact.
import * as T from 'three';
const W=1280,H=720,FPS=30,DURATION=20;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
await document.fonts.load('700 24px Manrope');await document.fonts.load('500 20px Manrope');
let seed=90211;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};const lerp=(a,b,u)=>a+(b-a)*u;
// --- one faint ground plane, projected for a very shallow camera ------------------
const scene=new T.Scene();scene.fog=new T.Fog(0xd2cfc2,40,300);
scene.add(new T.HemisphereLight(0xf2efe6,0x8e8a7c,2.4));
const sun=new T.DirectionalLight(0xfff6e8,1.15);sun.position.set(-30,26,20);scene.add(sun);
const ground=new T.Mesh(new T.PlaneGeometry(600,600,1,1),new T.MeshStandardMaterial({color:0xcfcabb,roughness:1}));
ground.rotation.x=-Math.PI/2;scene.add(ground);
const cam=new T.PerspectiveCamera(24,W/H,.1,900);cam.position.set(0,9,64);cam.lookAt(0,7.4,0);
// --- timing ---------------------------------------------------------------------
const SHOTS=[{n:'the record opens',s:0,e:7},{n:'the space between',s:7,e:14},{n:'not proof either way',s:14,e:20}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
// Evidence positions, drawn as fractions of a fixed in-frame rail.
const RAIL={x0:150,x1:1130,y:560};
function railX(u){return lerp(RAIL.x0,RAIL.x1,u)}
const MARKS=[{u:.26,label:'MAMMOTH REMAINS',sub:'youngest known — ~4,000 cal BP',side:-1},
 {u:.70,label:'ARCHAEOLOGICAL EVIDENCE',sub:'earliest known people — ~3,600 cal BP',side:1}];
function text(str,x,y,size,weight='700',alpha=1,align='left',color='32,38,40'){
 g.fillStyle=`rgba(${color},${alpha})`;g.font=`${weight} ${size}px Manrope`;g.textAlign=align;g.fillText(str,x,y);
}
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;
 const i=shotIndex(t),lt=t-SHOTS[i].s;
 // Very slow push in across the whole section; the plate should feel held, not animated.
 const push=1-.045*smooth(t/DURATION);
 cam.position.set(0,9*lerp(1,.96,smooth(t/DURATION)),64*push);cam.lookAt(0,7.4*lerp(1,.99,smooth(t/DURATION)),0);
 renderer.render(scene,cam);
 g.clearRect(0,0,W,H);
 // Paper: warm off-white, subtle fibre, no vignette theatrics.
 g.fillStyle='#efece3';g.fillRect(0,0,W,H);
 const grd=g.createLinearGradient(0,0,0,H);grd.addColorStop(0,'rgba(255,252,244,.55)');grd.addColorStop(1,'rgba(206,201,188,.35)');
 g.fillStyle=grd;g.fillRect(0,0,W,H);
 // Fixed hash noise, NOT the shared RNG: a seek must redraw the identical plate.
 for(let k=0;k<2600;k++){const h1=(Math.imul(k+1,2654435761)>>>0)/4294967296,h2=(Math.imul(k+7,40503)>>>0)/4294967296,h3=(Math.imul(k+13,2246822519)>>>0)/4294967296;
  g.fillStyle=h3<.5?`rgba(80,74,62,${.014+h2*.02})`:`rgba(255,255,255,${.014+h2*.02})`;g.fillRect(h1*W,h2*H,1+h3*2,1+h3*2)}
 // Title block.
 const intro=smooth(t/1.6);
 text('THE THIRD WITNESS',96,150,44,'700',.90*intro);
 text('What the dated record can and cannot show',96,190,22,'500',.66*intro,'left','52,58,58');
 g.fillStyle=`rgba(32,38,40,${.22*intro})`;g.fillRect(96,214,520,2);
 // Rail: revealed left to right, always with the empty stretch visible in the middle.
 const reveal=smooth((t-2.2)/3.4);
 g.strokeStyle='rgba(32,38,40,.55)';g.lineWidth=2;
 g.beginPath();g.moveTo(railX(0),RAIL.y);g.lineTo(railX(0)+(RAIL.x1-RAIL.x0)*reveal,RAIL.y);g.stroke();
 // Tick marks every 5% of the rail, faint.
 for(let k=0;k<=20;k++){const x=railX(k/20);if(x>railX(0)+(RAIL.x1-RAIL.x0)*reveal)break;
  g.strokeStyle=`rgba(32,38,40,${k%5===0?.30:.14})`;g.lineWidth=1;
  g.beginPath();g.moveTo(x,RAIL.y-6);g.lineTo(x,RAIL.y+6);g.stroke();}
 // The marks: a bone-symbol outline (not an illustration of a specimen) and a square.
 MARKS.forEach((m,idx)=>{
  const appear=smooth((t-(3.4+idx*1.5))/1.2);if(appear<=0)return;
  const x=railX(m.u),y=RAIL.y;
  g.save();g.globalAlpha=appear;
  if(idx===0){
   g.strokeStyle='rgba(122,101,72,.95)';g.lineWidth=2.4;
   g.beginPath();g.moveTo(x-11,y-4);g.quadraticCurveTo(x-4,y-16,x+2,y-8);g.quadraticCurveTo(x+8,y-2,x+12,y-10);g.stroke();
   g.beginPath();g.moveTo(x-11,y-4);g.quadraticCurveTo(x-6,y+10,x+2,y+2);g.stroke();
  }else{
   g.strokeStyle='rgba(56,86,96,.95)';g.lineWidth=2.4;
   g.strokeRect(x-10,y-13,20,20);
   g.beginPath();g.moveTo(x-4,y-6);g.lineTo(x+5,y-6);g.stroke();
  }
  g.restore();
  // Both labels sit below the rail, far enough apart that they cannot collide;
  // the bracket owns the space above it.
  const ly=RAIL.y+52;
  const la=.72*appear;
  text(m.label,x,ly,18,'700',la,'center','40,46,48');
  text(m.sub,x,ly+23,15,'500',la,'center','86,92,92');
 });
 // The interval bracket: the whole point of the plate.
 const bb=smooth((t-7.4)/2.6);
 if(bb>0){
  const a=railX(MARKS[0].u),b=railX(MARKS[1].u),y=RAIL.y-118;
  g.strokeStyle=`rgba(150,64,52,${.75*bb})`;g.lineWidth=2;
  g.beginPath();g.moveTo(a,y+12);g.lineTo(a,y);g.lineTo(b,y);g.lineTo(b,y+12);g.stroke();
  text('APPROXIMATELY 400 YEARS',(a+b)/2,y-14,17,'700',.85*bb,'center','150,64,52');
 }
 // Shot 2 caption.
 const cap=smooth((t-14.2)/1.6);
 if(cap>0){
  text('EARLIEST EVIDENCE ≠ FIRST ARRIVAL',96,308,30,'700',.9*cap);
  text('A human contribution could not be ruled out; direct evidence of an encounter',96,352,20,'500',.68*cap,'left','58,64,64');
  text('would be difficult to find. The gap is not proof of innocence, nor of hunting.',96,380,20,'500',.68*cap,'left','58,64,64');
 }
 // Footer: disclosure and the one thing this plate must never imply.
 text('SCHEMATIC · DATES ARE THE ONES SPOKEN IN THE NARRATION',96,H-56,14,'700',.52);
 text('NOT A SITE, MAP OR ARTEFACT · ILLUSTRATIVE',96,H-36,14,'700',.44,'left','90,96,96');
 return{time:t,shot:i,shot_name:SHOTS[i].n,animals:0,triangles:0,historical_geography:false,marks:MARKS.length,bracket:bb,reveal}}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
