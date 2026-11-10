// Original three-dimensional visual system for the documentary. Backgrounds
// are AI-generated illustrations, never evidence images. The labelled charts
// are schematic, with narration carrying the source-qualified interpretation.
import * as T from 'three';
const plan = await (await fetch('/timeline.json')).json();
await Promise.all([document.fonts.load("400 57px Anton"), document.fonts.load("700 21px Manrope")]);
await document.fonts.ready;
const W = 1280, H = 720;
const renderer = new T.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});
renderer.setSize(W,H,false); renderer.outputColorSpace=T.SRGBColorSpace;
renderer.toneMapping=T.ACESFilmicToneMapping; renderer.toneMappingExposure=1.05;
const canvas=document.createElement('canvas'); canvas.width=W; canvas.height=H;
canvas.id='final'; document.body.appendChild(canvas); const ctx=canvas.getContext('2d');
const scene=new T.Scene(), camera=new T.PerspectiveCamera(36,W/H,.1,100);
camera.position.set(0,0,15); camera.lookAt(0,0,0);
scene.add(new T.HemisphereLight(0xd0eaff,0x15253e,2.2));
const light=new T.DirectionalLight(0xffd3a8,2.5);light.position.set(-5,7,10);scene.add(light);
const rim=new T.DirectionalLight(0x56cbf7,2.8);rim.position.set(8,-1,-2);scene.add(rim);
const texLoader=new T.TextureLoader();
const names=[...new Set(plan.shots.map(s=>s.background))];
const textures=Object.fromEntries(await Promise.all(names.map(async n=>{
 const t=await texLoader.loadAsync(`/assets/${n}.jpg`);t.colorSpace=T.SRGBColorSpace;return [n,t];
})));
const groups={};
const mat=(c,metal=.2)=>new T.MeshStandardMaterial({color:c,metalness:metal,roughness:.38});
const cyan=mat(0x42d5eb), pale=mat(0xcde3e3), gold=mat(0xe9ad68), red=mat(0xe08269), dark=mat(0x163d52);
function sphere(r,m){return new T.Mesh(new T.SphereGeometry(r,18,12),m)}
function tube(points,r,m){return new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3(points),Math.max(24,points.length*2),r,7,false),m)}
function wire(w,h,d=0.06,color=0x6bd2e5){const geo=new T.BoxGeometry(w,h,d);const mesh=new T.LineSegments(new T.EdgesGeometry(geo),new T.LineBasicMaterial({color,transparent:true,opacity:.8}));return mesh}
function helix(){const g=new T.Group();let a=[],b=[];for(let i=0;i<=100;i++){let t=i/100*6*Math.PI,y=(i/100-.5)*5.2;a.push(new T.Vector3(Math.cos(t)*.72,y,Math.sin(t)*.72));b.push(new T.Vector3(-Math.cos(t)*.72,y,-Math.sin(t)*.72))}g.add(tube(a,.065,cyan),tube(b,.065,gold));for(let j=3;j<98;j+=5){let m=new T.Mesh(new T.CylinderGeometry(.022,.022,a[j].distanceTo(b[j]),6),pale);m.position.copy(a[j]).add(b[j]).multiplyScalar(.5);m.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),b[j].clone().sub(a[j]).normalize());g.add(m)}return g}
function globe(){const g=new T.Group();const core=sphere(2,dark);g.add(core);for(let i=-3;i<=3;i++){let phi=i*Math.PI/8;const pts=[];for(let j=0;j<=90;j++){let th=j/90*2*Math.PI;pts.push(new T.Vector3(2.015*Math.cos(phi)*Math.cos(th),2.015*Math.sin(phi),2.015*Math.cos(phi)*Math.sin(th)))}g.add(tube(pts,.009,cyan))}for(let i=0;i<9;i++){const pts=[];let th=i*Math.PI/9;for(let j=0;j<=60;j++){let ph=(j/60-.5)*Math.PI;pts.push(new T.Vector3(2.015*Math.cos(ph)*Math.cos(th),2.015*Math.sin(ph),2.015*Math.cos(ph)*Math.sin(th)))}g.add(tube(pts,.008,pale))}let marker=sphere(.13,gold);marker.position.set(.8,1.65,1.05);g.add(marker);return g}
function timeline(){const g=new T.Group();const line=new T.Mesh(new T.CylinderGeometry(.025,.025,5.2,10),cyan);line.rotation.z=Math.PI/2;g.add(line);for(let i=0;i<4;i++){let p=sphere(i===3?.18:.12,i===3?gold:pale);p.position.set(-2.3+i*1.55,0,0);g.add(p);let stem=new T.Mesh(new T.CylinderGeometry(.012,.012,.7,5),pale);stem.position.set(-2.3+i*1.55,-.36,0);g.add(stem)}return g}
function atom(){const g=new T.Group();const core=sphere(.34,gold);g.add(core);for(let i=0;i<3;i++){const p=[];for(let j=0;j<=80;j++){const a=j*Math.PI*2/80;p.push(new T.Vector3(Math.cos(a)*1.8,Math.sin(a)*.62,0))}const ring=tube(p,.018,cyan);ring.rotation.x=i*Math.PI/3;ring.rotation.z=i*Math.PI/3;g.add(ring);const dot=sphere(.11,pale);dot.position.set(Math.cos(i*2)*1.8,Math.sin(i*2)*.62,0);ring.add(dot)}return g}
function bars(){
 const g=new T.Group(), diversity=new T.Group(), homo=new T.Group(), schematic=new T.Group();
 function pair(parent,a,b){
  for (let i=0;i<2;i++) {const value=[a,b][i];const h=value*3.4;
   const mesh=new T.Mesh(new T.BoxGeometry(1.1,h,.55),i?gold:cyan);
   mesh.position.set(i?1.05:-1.05,h/2-1.7,0);parent.add(mesh)}
  parent.add(wire(4.6,4,.05));
 }
 // Heterozygosity: 0.75 -> 0.43 per kb, common scale, symbolic but proportional.
 pair(diversity,.75,.43);
 // Runs of homozygosity: ~10% -> ~42% on a shared scale.
 pair(homo,.10,.42);
 pair(schematic,.25,.68);
 g.add(diversity,homo,schematic);g.userData={diversity,homo,schematic};return g;
}
function stableChart(){
 const g=new T.Group(), pts=[];
 for(let i=0;i<=40;i++){let x=-2.35+i*4.7/40;pts.push(new T.Vector3(x,.07*Math.sin(i*.43),0))}
 g.add(tube(pts,.035,cyan),wire(5.2,3.3,.05));
 for(let i=0;i<5;i++){let m=sphere(.10,gold);m.position.copy(pts[i*10]);g.add(m)}return g;
}
function recoveryBars(){
 const g=new T.Group();for(let i=0;i<2;i++){const h=i?3.1:.10;let m=new T.Mesh(new T.BoxGeometry(1.1,h,.55),i?gold:cyan);m.position.set(i?1.05:-1.05,h/2-1.6,0);g.add(m)}g.add(wire(4.6,4,.05));return g;
}
function verdictPanels(){const g=new T.Group();for(let i=0;i<3;i++){let f=wire(1.22,2.9,.1,[0x42d5eb,0xe9ad68,0xe08269][i]);f.position.x=(i-1)*1.55;g.add(f)}return g;}

function variants(){const g=new T.Group();for(let x=0;x<6;x++)for(let y=0;y<7;y++){const m=new T.Mesh(new T.BoxGeometry(.5,.35,.22),((x*7+y)%9===0)?red:((x+y)%3===0?cyan:pale));m.position.set((x-2.5)*.7,(y-3)*.55,Math.sin(x+y)*.1);g.add(m)}return g}
function ice(){const g=new T.Group();for(let i=0;i<10;i++){let m=new T.Mesh(new T.ConeGeometry(.35+(i%3)*.13,2.1+(i%4)*.36,5),i%3?cyan:pale);m.position.set((i%5-2)*.5,Math.floor(i/5)*1.1-1,Math.sin(i)*.5);m.rotation.z=(i-5)*.08;g.add(m)}return g}
function microbe(){const g=new T.Group();for(let i=0;i<12;i++){const m=new T.Mesh(new T.CapsuleGeometry(.18,.65,5,10),i%3===0?gold:cyan);m.position.set(Math.sin(i*5)*1.8,Math.cos(i*2.4)*1.7,Math.sin(i*3.1));m.rotation.set(i*.4,i*.6,i*.25);g.add(m)}return g}
function water(){const g=new T.Group();let o=sphere(.55,cyan),h1=sphere(.24,pale),h2=sphere(.24,pale);h1.position.set(-1,.65,0);h2.position.set(1,.65,0);g.add(o,h1,h2);for(let h of [h1,h2]){let m=new T.Mesh(new T.CylinderGeometry(.09,.09,h.position.length(),8),pale);m.position.copy(h.position).multiplyScalar(.5);m.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),h.position.clone().normalize());g.add(m)}g.scale.setScalar(1.3);return g}
function panes(){const g=new T.Group();for(let i=0;i<2;i++){const f=wire(i?2.3:1.5,3.8,.1,i?0xe9ad68:0x42d5eb);f.position.x=i?1.35:-1.35;g.add(f);for(let j=0;j<(i?7:4);j++){let p=sphere(.07, j%2?gold:cyan);p.position.set(f.position.x+Math.sin(j*3)*.65,Math.cos(j*2)*1.3,0);g.add(p)}}return g}
function make(k){switch(k){case'globe':case'island':return globe();case'dna':case'coat':return helix();case'timeline':return timeline();case'isotopes':case'water':return atom();case'chart':return stableChart();case'bars':return bars();case'population':return recoveryBars();case'verdict':return verdictPanels();case'variants':return variants();case'ice':return ice();case'cells':case'microbe':return microbe();case'windows':case'compare':return panes();case'missing':case'evidence':case'archaeology':{let g=new T.Group();g.add(wire(3.8,3.2,.3));let h=k==='missing'?helix():atom();h.scale.setScalar(.38);g.add(h);return g}default:return atom()}}
for(const k of new Set(plan.shots.map(x=>x.kind))){let g=make(k);g.position.set(2.15,-.15,0);g.visible=false;scene.add(g);groups[k]=g}
let last=null;
function draw(t){const shot=plan.shots.find(s=>t>=s.start&&t<s.end)||plan.shots.at(-1);const u=Math.max(0,Math.min(1,(t-shot.start)/(shot.end-shot.start)));for(const g of Object.values(groups))g.visible=false;
 const g=groups[shot.kind];g.visible=true;if(g.userData.diversity){g.userData.diversity.visible=shot.title==='DIVERSITY FELL';g.userData.homo.visible=shot.title==='HOMOZYGOSITY ROSE';g.userData.schematic.visible=!g.userData.diversity.visible&&!g.userData.homo.visible;}g.rotation.y=.20+Math.sin(t*.11)*.16;g.rotation.z=Math.sin(t*.13)*.045;g.position.y=-.15+Math.sin(t*.3)*.06;
 renderer.render(scene,camera);const bg=textures[shot.background].image;ctx.clearRect(0,0,W,H);
 // Slow pan and push across the illustrative background, while the foreground
 // is true 3D geometry rendered at a reduced temporal sampling rate.
 const zoom=1.07+.035*u, w=W*zoom,h=H*zoom;const x=-(w-W)*(.25+.35*u),y=-(h-H)*.45;
 ctx.drawImage(bg,x,y,w,h);ctx.fillStyle='rgba(2,13,25,.58)';ctx.fillRect(0,0,W,H);
 const grad=ctx.createLinearGradient(0,0,W*.75,0);grad.addColorStop(0,'rgba(2,11,21,.88)');grad.addColorStop(.65,'rgba(3,15,27,.34)');grad.addColorStop(1,'rgba(2,12,23,.05)');ctx.fillStyle=grad;ctx.fillRect(0,0,W,H);
 ctx.drawImage(renderer.domElement,0,0); // transparent WebGL background
 const fade=Math.min(1,u*7,(1-u)*7);ctx.globalAlpha=Math.max(.15,fade);
 ctx.fillStyle='#74d7e7';ctx.fillRect(78,170,42,4);ctx.font='700 17px Manrope';ctx.letterSpacing='3px';ctx.fillText('THE LAST MAMMOTHS',78,156);ctx.letterSpacing='0px';
 function wrap(s,max){let parts=s.split(' '),lines=[],line='';for(const p of parts){const test=line?line+' '+p:p;if(ctx.measureText(test).width>max && line){lines.push(line);line=p}else line=test}if(line)lines.push(line);return lines}
 ctx.font='400 57px Anton';ctx.fillStyle='#f6f2e9';let lines=wrap(shot.title,570);lines.forEach((line,i)=>ctx.fillText(line,78,246+i*67));
 ctx.font='700 21px Manrope';ctx.fillStyle='#bad3d6';let y2=260+lines.length*67;wrap(shot.detail,570).forEach((line,i)=>ctx.fillText(line,78,y2+i*29));
 ctx.globalAlpha=1;ctx.font='700 12px Manrope';ctx.fillStyle='rgba(220,234,234,.8)';ctx.textAlign='right';ctx.fillText('ARTIST’S ILLUSTRATION',W-44,48);if(['chart','bars','population'].includes(shot.kind))ctx.fillText('SCHEMATIC GRAPHIC',W-44,68);ctx.textAlign='left';
 last=shot.id;return shot.id;
}
window.__seek=draw;window.__ready=true;draw(60);
