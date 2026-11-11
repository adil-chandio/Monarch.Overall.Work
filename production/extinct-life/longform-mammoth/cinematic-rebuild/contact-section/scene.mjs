// Human-contact section — what the dates can and cannot carry (411-455 s).
//
// The narration is careful in a way that is easy to lose on screen: archaeological
// evidence at ~3,600 cal BP is centuries *after* the youngest known mammoth remains,
// but earliest evidence is not first arrival, and the 2019 researchers could not rule
// out a human contribution because direct evidence of an encounter would be hard to
// find. Elsewhere tells us the two species met; it does not transfer here.
//
// So this is a two-page register: what the dates establish, and what remains unresolved.
// The divider between the pages is the whole point, and it never opens.
import * as T from 'three';
const W=1280,H=720,FPS=30,DURATION=44;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
await document.fonts.load('700 24px Manrope');await document.fonts.load('500 20px Manrope');
const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};
const SHOTS=[{n:'two registers',s:0,e:14.0},{n:'hard to find',s:14.0,e:27.0},{n:'elsewhere is not here',s:27.0,e:33.4},{n:'neither proof',s:33.4,e:41.6},{n:'three witnesses',s:41.6,e:44}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
function text(str,x,y,size,weight='700',alpha=1,align='left',color='32,38,40'){
 g.fillStyle=`rgba(${color},${alpha})`;g.font=`${weight} ${size}px Manrope`;g.textAlign=align;g.fillText(str,x,y);
}
// The two registers. `at` is local seconds; every line appears when it is spoken.
const KNOWN=[{at:1.6,l:['Archaeological evidence at','~3,600 cal BP']},
             {at:2.6,l:['Centuries after the youngest','known mammoth remains']}];
const UNRESOLVED=[{at:3.2,l:['First arrival']},
                  {at:5.0,l:['A human contribution']},
                  {at:7.4,l:['Direct evidence of an','encounter']}];
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;
 g.fillStyle='#f0ede4';g.fillRect(0,0,W,H);
 const grd=g.createLinearGradient(0,0,0,H);grd.addColorStop(0,'rgba(255,253,246,.6)');grd.addColorStop(1,'rgba(206,200,186,.30)');
 g.fillStyle=grd;g.fillRect(0,0,W,H);
 for(let k=0;k<2400;k++){const h1=(Math.imul(k+1,2654435761)>>>0)/4294967296,h2=(Math.imul(k+7,1597334677)>>>0)/4294967296,h3=(Math.imul(k+13,2246822519)>>>0)/4294967296;
  g.fillStyle=h3<.5?`rgba(78,72,60,${.012+h2*.018})`:`rgba(255,255,255,${.012+h2*.018})`;g.fillRect(h1*W,h2*H,1+h3*2,1+h3*2)}
 const intro=smooth(t/1.5);
 text('WHAT THE DATES CAN CARRY',96,124,38,'700',.92*intro);
 text('Two registers, kept apart for the length of this passage',96,162,20,'500',.64*intro,'left','52,58,58');
 g.fillStyle=`rgba(32,38,40,${.20*intro})`;g.fillRect(96,184,1088,2);

 // --- shot 0: the two registers ---------------------------------------------------
 const pages=1-smooth((t-13.4)/1.4);
 if(pages>0.01){
  const py=228,ph=272;
  [{x:96,head:'ESTABLISHED BY THE DATES',col:'56,86,96',items:KNOWN,w:520},
   {x:664,head:'NOT RESOLVED BY THE DATES',col:'150,64,52',items:UNRESOLVED,w:520}].forEach((pg,pi)=>{
   const ha=smooth((t-(0.9+pi*.5))/.9)*pages;if(ha<=0)return;
   g.save();g.globalAlpha=.42*ha;g.fillStyle='rgba(255,253,246,.8)';
   g.fillRect(pg.x,py,pg.w,ph);
   g.strokeStyle='rgba(32,38,40,.18)';g.lineWidth=1;g.strokeRect(pg.x+.5,py+.5,pg.w,ph);g.restore();
   text(pg.head,pg.x+22,py+34,14,'700',.84*ha,'left',pg.col);
   g.save();g.globalAlpha=.5*ha;g.fillStyle=`rgba(${pg.col},.7)`;g.fillRect(pg.x+22,py+46,pg.w-44,2);g.restore();
   let y=py+88;
   pg.items.forEach((it)=>{
    const a=smooth((t-it.at)/.9)*pages;if(a<=0){y+=it.l.length*24+22;return}
    g.save();g.globalAlpha=a;g.fillStyle=`rgba(${pg.col},.8)`;g.fillRect(pg.x+22,y-8,10,2);g.restore();
    it.l.forEach((ln,i)=>text(ln,pg.x+44,y+i*24,17,'500',.84*a,'left','44,50,52'));
    y+=it.l.length*24+22;
   });
  });
  // the divider that never opens
  const da=smooth((t-2.2)/1.2)*pages;
  if(da>0){
   g.save();g.globalAlpha=.5*da;g.strokeStyle='rgba(32,38,40,.45)';g.lineWidth=1.5;
   g.setLineDash([5,7]);g.beginPath();g.moveTo(640,228);g.lineTo(640,500);g.stroke();g.setLineDash([]);g.restore();
   text('KEPT SEPARATE',640,516,12,'700',.5*da,'center','70,76,76');
  }
 }

 // --- shot 1: hard to find --------------------------------------------------------
 const find=smooth((t-14.1)/1.5)*pages;
 if(find>0){
  text('DIRECT EVIDENCE WOULD BE HARD TO FIND',96,232,26,'700',.9*find);
  // a search field: many plausible places, nothing recovered. Dashed outlines, no objects.
  const bx=96,by=276,bw=1088,bh=150;
  g.save();g.globalAlpha=find;
  for(let r=0;r<3;r++)for(let c=0;c<12;c++){
   const x=bx+c*90,y=by+r*48;
   g.strokeStyle='rgba(32,38,40,.11)';g.lineWidth=1;g.setLineDash([3,5]);
   g.strokeRect(x+.5,y+.5,84,42);
  }
  g.setLineDash([]);g.restore();
  const a=smooth((t-17.2)/1.4)*find;
  if(a>0){
   text('An encounter between a few people and a few animals leaves little that survives,',96,468,18,'500',.7*a,'left','58,64,64');
   text('and a site would have to be found, dated and read correctly to register at all.',96,496,18,'500',.7*a,'left','58,64,64');
  }
  const b=smooth((t-21.0)/1.4)*find;
  if(b>0)text('So a human contribution could not be ruled out.',96,548,21,'700',.85*b);
  const c=smooth((t-23.4)/1.3)*find;
  if(c>0)text('Not ruled out is not the same as established — in either direction.',96,584,18,'500',.64*c,'left','58,64,64');
 }

 // --- shot 2: elsewhere is not here ------------------------------------------------
 const trans=smooth((t-27.1)/1.5)*(1-smooth((t-32.9)/1.1));
 if(trans>0){
  text('ELSEWHERE IS NOT HERE',96,232,26,'700',.9*trans);
  const ly=306;
  text('OTHER SITES',96,ly+6,13,'700',.7*trans,'left','56,86,96');
  text('humans and mammoths interacted',96,ly+30,17,'500',.66*trans,'left','58,64,64');
  // an arrow that stops short of the island: the transfer is refused
  const ax0=438,ax1=690,ay=ly+18;
  const draw1=smooth((t-29.0)/1.2);
  g.save();g.globalAlpha=.7*trans*draw1;
  g.strokeStyle='rgba(32,38,40,.5)';g.lineWidth=2;
  g.beginPath();g.moveTo(ax0,ay);g.lineTo(ax1,ay);g.stroke();
  g.beginPath();g.moveTo(ax1-9,ay-6);g.lineTo(ax1,ay);g.lineTo(ax1-9,ay+6);g.stroke();
  g.restore();
  const stop=smooth((t-30.4)/1.0);
  if(stop>0){
   g.save();g.globalAlpha=.9*trans*stop;
   g.strokeStyle='rgba(150,64,52,.85)';g.lineWidth=2.5;
   g.beginPath();g.moveTo(ax1+22,ay-14);g.lineTo(ax1+46,ay+14);g.moveTo(ax1+46,ay-14);g.lineTo(ax1+22,ay+14);g.stroke();
   g.restore();
   text('NOT TRANSFERABLE',ax1+58,ay+5,12.5,'700',.82*trans*stop,'left','150,64,52');
  }
  text('THIS ISLAND',1006,ly+6,13,'700',.7*trans,'left','32,38,40');
  text('needs its own evidence',1006,ly+30,17,'500',.66*trans,'left','58,64,64');
  const a=smooth((t-31.8)/1.4)*trans;
  if(a>0){
   g.save();g.globalAlpha=.16*a;g.fillStyle='rgba(32,38,40,.5)';g.fillRect(96,432,1088,1);g.restore();
   text('Archaeology shows the two species met. Evidence from another place cannot',96,472,18,'500',.68*a,'left','58,64,64');
   text('automatically be transferred to this island.',96,500,18,'500',.68*a,'left','58,64,64');
   g.save();g.globalAlpha=.13*a;g.fillStyle='rgba(255,253,246,.7)';g.fillRect(96,540,1088,84);
   g.strokeStyle='rgba(32,38,40,.14)';g.lineWidth=1;g.strokeRect(96.5,540.5,1087,84);g.restore();
   text('WHAT WOULD CHANGE THE PICTURE',114,568,13,'700',.66*a,'left','150,64,52');
   text('A dated site on the island with mammoth remains and unambiguous human traces.',114,594,17,'500',.6*a,'left','52,58,58');
   text('None has been found. That is an absence of evidence, not evidence of absence.',114,614,15,'500',.48*a,'left','70,76,76');
  }
 }

 // --- shot 3: neither proof --------------------------------------------------------
 // "Human involvement is possible, but the known dates do not establish it" (444.2 s),
 // then "the apparent gap is not proof of innocence, and it is not proof of hunting" (446.4).
 const neu=smooth((t-33.5)/1.4)*(1-smooth((t-41.2)/1.0));
 if(neu>0){
  text('AN APPARENT GAP IS NOT A VERDICT',96,232,26,'700',.9*neu);
  const a=smooth((t-34.2)/1.2)*neu;
  if(a>0)text('Human involvement is possible. The known dates do not establish it.',96,286,20,'700',.82*a);
  // two equal, closed verdicts — struck through, not chosen between
  [[96,'PROOF OF INNOCENCE'],[560,'PROOF OF HUNTING']].forEach(([x,l],i)=>{
   const s2=smooth((t-(37.0+i*.4))/.9)*neu;if(s2<=0)return;
   g.save();g.globalAlpha=.55*s2;g.strokeStyle='rgba(32,38,40,.35)';g.lineWidth=1;
   g.strokeRect(x+.5,340.5,384,46);g.restore();
   text(l,x+18,370,15,'700',.5*s2,'left','70,76,76');
   const st=smooth((t-(37.6+i*.4))/.8)*neu;
   if(st>0){g.save();g.globalAlpha=.75*st;g.strokeStyle='rgba(150,64,52,.8)';g.lineWidth=2;
    g.beginPath();g.moveTo(x+18,364);g.lineTo(x+18+354,364);g.stroke();g.restore();}
  });
  const b=smooth((t-38.8)/1.2)*neu;
  if(b>0){
   text('The gap between the youngest remains and the earliest people is not',96,448,18,'500',.68*b,'left','58,64,64');
   text('proof of innocence, and it is not proof of hunting.',96,474,18,'500',.68*b,'left','58,64,64');
  }
  const c=smooth((t-40.2)/1.1)*neu;
  if(c>0)text('It is a gap in the record, and both verdicts would need evidence the record does not hold.',96,520,16,'500',.5*c,'left','70,76,76');
 }
 // --- shot 4: the hand-off to the closing argument ---------------------------------
 // "Three witnesses have offered clues; none has shown the final moment" (452.9 s).
 const three=smooth((t-41.8)/1.1);
 if(three>0){
  text('THREE WITNESSES HAVE OFFERED CLUES',96,238,30,'700',.92*three);
  const a=smooth((t-42.8)/.9)*three;
  if(a>0)text('None has shown the final moment.',96,286,22,'500',.72*a,'left','58,64,64');
  const b=smooth((t-43.2)/.8)*three;
  if(b>0){
   [['GENOMES',96],['ISOTOPES',452],['ARCHAEOLOGY',808]].forEach(([l,x],i)=>{
    const q=smooth((t-(42.4+i*.16))/.7)*three;if(q<=0)return;
    g.save();g.globalAlpha=.55*q;g.fillStyle='rgba(32,38,40,.45)';g.fillRect(x,336,368,1);g.restore();
    text(l,x,372,16,'700',.78*q);
    text('offered a clue',x,398,14,'500',.55*q,'left','70,76,76');
   });
  }
 }
 text('SCHEMATIC · DATES ARE THE ONES SPOKEN IN THE NARRATION · NO ENCOUNTER IS DEPICTED',1184,H-16,12,'700',.4,'right');
 return{time:t,shot:shotIndex(t),shot_name:SHOTS[shotIndex(t)].n,animals:0,people:0,triangles:0,historical_geography:false,registers:2,dividerClosed:true,encounterDepicted:false};
}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
