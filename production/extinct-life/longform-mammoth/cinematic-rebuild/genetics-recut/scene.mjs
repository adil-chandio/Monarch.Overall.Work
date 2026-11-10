// Experimental documentary scene: reconstructed research bench and schematic DNA.
// Geometry, lighting and camera are 3D; no image plates or photographs.
import * as T from 'three';
const W=1280,H=720;
await document.fonts.load('700 15px Manrope'); await document.fonts.ready;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
renderer.setSize(W,H,false);renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;
renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.14;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const ctx=canvas.getContext('2d');
const cam=new T.PerspectiveCamera(38,W/H,.08,200);
const sm=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
const lerp=(a,b,u)=>a+(b-a)*u;
const V=a=>new T.Vector3(...a);
function cameraPath(t,keys){let i=0;while(i<keys.length-2&&t>keys[i+1].t)i++;const a=keys[i],b=keys[i+1],u=sm((t-a.t)/(b.t-a.t));cam.position.copy(V(a.p).lerp(V(b.p),u));cam.lookAt(V(a.target).lerp(V(b.target),u));}
const mat=(color,metal=0,rough=.6)=>new T.MeshStandardMaterial({color,metalness:metal,roughness:rough});
function mesh(g,m,p,parent){let o=new T.Mesh(g,m);o.position.set(...p);parent.add(o);return o;}
function box(p,s,m,parent){return mesh(new T.BoxGeometry(...s),m,p,parent)}
function cyl(p,r1,r2,h,m,parent,n=24){return mesh(new T.CylinderGeometry(r1,r2,h,n),m,p,parent)}
function lineBetween(a,b,r,m,parent){const av=V(a),bv=V(b),o=mesh(new T.CylinderGeometry(r,r,av.distanceTo(bv),9),m,[0,0,0],parent);o.position.copy(av).add(bv).multiplyScalar(.5);o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),bv.sub(av).normalize());return o;}
function canvasTexture(w,h,draw){const c=document.createElement('canvas');c.width=w;c.height=h;draw(c.getContext('2d'),w,h);const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;return t;}
const labelTex=(title,sub)=>canvasTexture(512,180,(c,w,h)=>{c.fillStyle='#c5b99e';c.fillRect(0,0,w,h);c.fillStyle='#282b29';c.font='bold 34px Manrope';c.fillText(title,25,70);c.font='23px Manrope';c.fillText(sub,25,120);});
const steel=mat(0x273b45,.72,.32),black=mat(0x101b22,.25,.4),brass=mat(0xb9a270,.64,.36),cream=mat(0x9f8a6c,0,.88), white=mat(0xc9d7d8,.15,.48), blue=mat(0x18718a,.15,.45);
const lightPanel=new T.MeshBasicMaterial({color:0x90eaff});
const lab=new T.Scene();lab.background=new T.Color(0x08131b);lab.fog=new T.FogExp2(0x08131b,.022);
lab.add(new T.HemisphereLight(0xa7ddf0,0x12100d,1.35));
let a=new T.DirectionalLight(0xbedff9,2.2);a.position.set(-4,7,6);lab.add(a);
let b=new T.DirectionalLight(0xffd4a1,1.4);b.position.set(5,5,-6);lab.add(b);
const lamp=new T.PointLight(0x5ec7e5,30,12,2);lamp.position.set(0,3,1.5);lab.add(lamp);
box([0,-.32,0],[20,.6,12],mat(0x26343a,.25,.8),lab);
box([0,.005,0],[20,.04,12],mat(0x13232b,.38,.56),lab);
box([0,2.35,-3.3],[20,4.7,.25],mat(0x12252d,.18,.82),lab);
for(let x=-8;x<=8;x+=2.4){box([x,2.3,-3.14],[.045,4.4,.03],mat(0x36515b,.6,.4),lab);}
// Workbench rail for the instrument. Geometry is explicitly attached to the base.
box([.2,.12,-.15],[6.6,.24,3.05],black,lab);
box([.2,.25,-.15],[6.45,.055,2.95],steel,lab);
for(let x of [-2.5,2.9])box([x,.40,-.15],[.10,.2,2.72],brass,lab);
for(let z of [-1.42,1.12])box([.2,.36,z],[5.5,.08,.08],steel,lab);
// Bone fragments are an illustrative generic material, not specific recovered specimens.
const boneTex=canvasTexture(512,512,(g,w,h)=>{g.fillStyle='#a99578';g.fillRect(0,0,w,h);let seed=392811;const R=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296};for(let i=0;i<3800;i++){let x=R()*w,y=R()*h;g.fillStyle=R()>.5?'rgba(52,40,28,.08)':'rgba(242,221,186,.08)';g.beginPath();g.ellipse(x,y,1+R()*8,1+R()*4,R()*3,0,7);g.fill();}});
const boneMat=new T.MeshStandardMaterial({map:boneTex,color:0xe8d4b6,roughness:.92});
function fragment(x,z,r,len,tilt){const geo=new T.CapsuleGeometry(r,len,7,20);const p=geo.attributes.position;for(let i=0;i<p.count;i++){let x=p.getX(i),y=p.getY(i),z=p.getZ(i);let n=1+.07*Math.sin(y*12+z*9)*Math.sin(x*11-y*4)+.035*Math.sin(y*27+x*15);p.setXYZ(i,x*n,y,z*n)}geo.computeVertexNormals();let o=mesh(geo,boneMat,[x,.49,z],lab);o.rotation.set(1.22,tilt,.08);return o;}
const trayMat=mat(0x273b40,.62,.36);box([-1.45,.30,0],[2.05,.055,1.55],trayMat,lab);for(const [x,z,r,l,ang] of [[-1.65,-.15,.29,1.05,.22],[-1.12,.18,.19,.70,-.38],[-1.85,.40,.16,.48,.64]])fragment(x,z,r,l,ang);
// Two illustrative containers; the labels are physical 3D surface textures, not slides.
const glass=new T.MeshPhongMaterial({color:0xb7dfe5,transparent:true,opacity:.27,shininess:100,depthWrite:false,side:T.DoubleSide});
function vial(x,z,title,sub){const g=new T.Group();g.position.set(x,.278,z);lab.add(g);cyl([0,.43,0],.22,.22,.86,glass,g);cyl([0,.08,0],.195,.195,.16,cream,g);cyl([0,.88,0],.25,.25,.10,steel,g);cyl([0,.95,0],.24,.24,.04,brass,g);let label=mesh(new T.PlaneGeometry(.56,.19),new T.MeshBasicMaterial({map:labelTex(title,sub)}),[0,.47,.225],g);return g;}
vial(.65,.42,'MAINLAND','approx. 45,000 years');vial(1.58,.42,'WRANGEL','approx. 4,300 years');
// Coherent linear scan head moves along a horizontal track; light and carriage are attached.
box([.45,2.18,-.65],[6.05,.14,.22],steel,lab);box([-2.44,1.24,-.65],[.12,1.85,.16],steel,lab);box([3.35,1.24,-.65],[.12,1.85,.16],steel,lab);
const carriage=new T.Group();lab.add(carriage);box([0,2.18,-.65],[.53,.23,.37],brass,carriage);box([0,1.78,-.65],[.17,.70,.17],steel,carriage);cyl([0,1.32,-.65],.29,.19,.35,black,carriage);cyl([0,1.135,-.65],.115,.115,.03,lightPanel,carriage);
const scanLight=new T.PointLight(0x7ce4ff,3.0,2.0,2);scanLight.position.set(0,1.10,-.65);carriage.add(scanLight);
// Equipment is attached to the bench: rack, capped pipettes and screw fixtures.
const rack=mat(0x385b65,.35,.48);
box([-3.46,.37,.66],[1.05,.19,.84],rack,lab);
for(let i=0;i<4;i++)for(let j=0;j<2;j++){
 const x=-3.82+i*.24,z=.43+j*.35;
 cyl([x,.61,z],.037,.037,.43,white,lab,10);
 cyl([x,.85,z],.05,.05,.06,blue,lab,10);
}
for(let x of [-2.92,3.25])for(let z of [-1.25,.96])cyl([x,.30,z],.035,.035,.035,brass,lab,10);
// Closed reagent containers remain stationary during the shot.
for(let i=0;i<3;i++){const x=3.45+i*.54;cyl([x,.295,-1.85],.18,.2,.55,white,lab);cyl([x,.61,-1.85],.19,.19,.08,black,lab);}
// Backdrop equipment: understated forms and moving indicator lights, not evidence props.
for(let i=0;i<4;i++){box([-7.5+i*2.0,.83,-2.2],[1.65,1.65,.9],steel,lab);box([-7.5+i*2,1.10,-1.73],[1.16,.70,.015],black,lab);for(let j=0;j<3;j++)mesh(new T.SphereGeometry(.035,8,5),j===1?lightPanel:brass,[-8+i*2+j*.15,.57,-1.72],lab);}
// Small environment glints, kept dim to avoid presenting contamination as lab practice.
let dustSeed=81502;const rb=()=>{dustSeed=(1664525*dustSeed+1013904223)>>>0;return dustSeed/4294967296};const gp=new Float32Array(110*3);for(let i=0;i<110;i++){gp[3*i]=(rb()-.5)*15;gp[3*i+1]=.4+rb()*4;gp[3*i+2]=(rb()-.5)*8;}
const dustGeo=new T.BufferGeometry();dustGeo.setAttribute('position',new T.BufferAttribute(gp,3));const dust=new T.Points(dustGeo,new T.PointsMaterial({color:0x9bbfc5,size:.018,transparent:true,opacity:.08}));lab.add(dust);
// Schematic right-handed helix: 10 pairs per turn, proportions illustrative.
const dna=new T.Scene();dna.background=new T.Color(0x07151c);dna.fog=new T.FogExp2(0x07151c,.035);
dna.add(new T.HemisphereLight(0xaad9ec,0x0a171f,1.4));let dl=new T.DirectionalLight(0xd7f6ff,2.5);dl.position.set(5,6,8);dna.add(dl);let dr=new T.PointLight(0xe2a25e,28,24);dr.position.set(-4,0,3);dna.add(dr);
const helix=new T.Group();dna.add(helix);const strand1=mat(0x58c4d9,.22,.32),strand2=mat(0xe4a75e,.18,.36),bases=[mat(0xbed6d7,.08,.45),mat(0x5ba69d,.12,.46),mat(0xe9c092,.06,.45),mat(0x9b7470,.1,.5)];
const R=.53,pitch=1.7,pairs=50,turns=5;
for(let side of [0,1]){let points=[];for(let i=0;i<=400;i++){const f=i/400,th=f*turns*Math.PI*2+side*Math.PI;points.push(new T.Vector3(Math.cos(th)*R,Math.sin(th)*R,(f-.5)*turns*pitch));}let tube=new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3(points),400,.052,9,false),side?strand2:strand1);helix.add(tube);}
const rung=[];for(let i=0;i<=pairs;i++){const f=i/pairs,th=f*turns*Math.PI*2,z=(f-.5)*turns*pitch,x=Math.cos(th)*R,y=Math.sin(th)*R;const g=new T.Group();helix.add(g);let which=i%2?0:2;lineBetween([x,y,z],[0,0,z],.035,bases[which],g);lineBetween([0,0,z],[-x,-y,z],.035,bases[which+1],g);rung.push(g);}
const motes=new T.Group();dna.add(motes);for(let i=0;i<100;i++){let o=mesh(new T.SphereGeometry(.025+(i%3)*.008,6,4),i%3?strand1:strand2,[(Math.sin(i*13.1)*2.8),(Math.cos(i*7.3)*2.3),(i%19-9)*.49],motes);o.userData.i=i;}
// Deletion is a conceptual cutaway, not a literal genome or a measured variant.
// A few linked rungs move out of a continuous helical fragment, leaving a visible gap.
const delScene=new T.Scene();delScene.background=new T.Color(0x101b23);delScene.fog=new T.FogExp2(0x101b23,.035);
delScene.add(new T.HemisphereLight(0xc3e8f1,0x201915,1.5));const key=new T.DirectionalLight(0xffe5b8,2.2);key.position.set(3,6,8);delScene.add(key);
const deletion=new T.Group();delScene.add(deletion);const deleted=new T.Group();deletion.add(deleted);
const xStep=.34; const helixPoint=(i,side)=>{let angle=i*Math.PI/5+side*Math.PI;return [(i-10)*xStep,Math.cos(angle)*.60,Math.sin(angle)*.60]};
for(let i=0;i<=20;i++){
 const group=(i>=8&&i<=10)?deleted:deletion;
 const a=helixPoint(i,0),b=helixPoint(i,1);
 lineBetween(a,b,.045,bases[i%4],group);
 for(let side=0;side<2;side++){
  let q=helixPoint(i,side);mesh(new T.SphereGeometry(.072,12,8),side?strand2:strand1,q,group);
  // Segment belongs to fragment only if both ends belong to it; boundary gaps are deliberate.
  if(i<20 && ![7,10].includes(i))lineBetween(q,helixPoint(i+1,side),.052,side?strand2:strand1,group);
 }
}
// Marker posts are positioned in 3D and draw the eye to the missing section.
const marker=mat(0xe7a75c,.3,.32);let leftMarker=mesh(new T.SphereGeometry(.085,12,8),marker,helixPoint(7,0),deletion);let rightMarker=mesh(new T.SphereGeometry(.085,12,8),marker,helixPoint(11,0),deletion);

// A simplified translation machine and RNA triplets convey what a stop signal means.
// UAA is an example RNA stop codon, not a claimed sequence from the specimen.
const trans=new T.Scene();trans.background=new T.Color(0x122328);trans.fog=new T.FogExp2(0x122328,.035);
trans.add(new T.HemisphereLight(0xc6e8eb,0x182025,1.6));let tlight=new T.DirectionalLight(0xffe4b4,2.5);tlight.position.set(3,5,8);trans.add(tlight);
const machinery=new T.Group();trans.add(machinery);
const riboMat=mat(0x79989c,.2,.46),riboDark=mat(0x436b70,.2,.5),rnaMat=mat(0xe3b26f,.25,.39),peptideMat=mat(0x80cad4,.18,.37);
function ellipsoid(g,p,scale,m){let o=mesh(new T.SphereGeometry(1,32,18),m,p,g);o.scale.set(...scale);return o;}
ellipsoid(machinery,[0,.56,0],[1.30,.60,.70],riboMat);ellipsoid(machinery,[0,-.38,0],[1.05,.30,.63],riboDark);
// Irregular lobes suggest a complex molecular machine, not a smooth disc.
let rs=1337;const rand=()=>{rs=(1664525*rs+1013904223)>>>0;return rs/4294967296};
const gran=new T.InstancedMesh(new T.IcosahedronGeometry(1,1),riboMat,420);const dummy=new T.Object3D();
for(let i=0;i<420;i++){let phi=rand()*Math.PI*2,ct=2*rand()-1,st=Math.sqrt(1-ct*ct);dummy.position.set(1.22*st*Math.cos(phi),.56+.54*ct,.65*st*Math.sin(phi));let rad=.05+rand()*.095;dummy.scale.set(rad,rad*(.65+rand()*.7),rad);dummy.updateMatrix();gran.setMatrixAt(i,dummy.matrix);}machinery.add(gran);
// Soft, out-of-focus-looking molecular forms supply depth without extra text.
const backMat=mat(0x29494e,.05,.8);
for(let i=0;i<15;i++){let o=ellipsoid(trans,[(rand()-.5)*12,(rand()-.5)*6,-3-rand()*4],[.25+rand()*.5,.18+rand()*.35,.25],backMat);o.rotation.z=rand()*3;}
// Front-facing tiles are objects on the 3D RNA, not image-backed slides.
function tileTexture(letter,stop){return canvasTexture(128,128,(c,w,h)=>{c.fillStyle=stop?'#e29771':'#e2b77b';c.fillRect(0,0,w,h);c.fillStyle='#202e31';c.font='bold 78px Manrope';c.textAlign='center';c.textBaseline='middle';c.fillText(letter,w/2,h/2+3);});}
const tiles=new T.Group();trans.add(tiles);const letters='AUGGCUUAACCU'; // AUG | GCU | UAA | CCU: UAA is an example stop codon
for(let i=0;i<letters.length;i++){
 let tile=mesh(new T.BoxGeometry(.40,.40,.16),rnaMat,[(i-5.5)*.44,-.18,.84],tiles);
 mesh(new T.PlaneGeometry(.34,.34),new T.MeshBasicMaterial({map:tileTexture(letters[i],i>=6&&i<=8)}),[(i-5.5)*.44,-.18,.93],tiles);
}
const peptide=new T.Group();machinery.add(peptide);
for(let i=0;i<7;i++){let x=.14*Math.sin(i*.8),y=.9+i*.30,z=.05+.12*Math.cos(i*.9);mesh(new T.SphereGeometry(.13,14,9),peptideMat,[x,y,z],peptide);if(i)lineBetween([.14*Math.sin((i-1)*.8),.9+(i-1)*.30,.05+.12*Math.cos((i-1)*.9)],[x,y,z],.06,peptideMat,peptide);}

// Cuts are motivated by the spoken evidence. Each shot is short, but remains readable.
const labCuts=[
 {id:'lab-specimen',end:3.0,keys:[{t:0,p:[2.9,2.0,4.5],target:[-1.35,.5,0]},{t:3,p:[1.9,1.40,3.1],target:[-1.35,.5,0]}]},
 {id:'lab-detail',end:5.2,keys:[{t:3,p:[-2.85,1.5,2.2],target:[-1.5,.45,0]},{t:5.2,p:[-2.4,1.27,1.85],target:[-1.45,.5,0]}]},
 {id:'lab-mainland',end:8.3,keys:[{t:5.2,p:[.15,1.28,3.15],target:[.65,.68,.42]},{t:8.3,p:[.43,1.16,2.5],target:[.65,.68,.42]}]},
 {id:'lab-mainland-detail',end:10.3,keys:[{t:8.3,p:[-.35,1.00,2.18],target:[.65,.68,.42]},{t:10.3,p:[.02,.95,1.9],target:[.65,.68,.42]}]},
 {id:'lab-wrangel',end:13.1,keys:[{t:10.3,p:[1.90,1.23,3.25],target:[1.58,.68,.42]},{t:13.1,p:[1.73,1.13,2.48],target:[1.58,.68,.42]}]},
 {id:'lab-wrangel-detail',end:15.7,keys:[{t:13.1,p:[2.20,1.05,2.1],target:[1.58,.68,.42]},{t:15.7,p:[2.0,.95,1.8],target:[1.58,.68,.42]}]},
 {id:'lab-comparison',end:18.2,keys:[{t:15.7,p:[2.65,1.4,3.25],target:[1.1,.68,.42]},{t:18.2,p:[3.4,1.7,4.2],target:[.8,.70,0]}]},
 {id:'lab-pullback',end:20.1,keys:[{t:18.2,p:[4.2,2.2,5.2],target:[.5,.70,0]},{t:20.1,p:[5.0,2.7,5.7],target:[.2,.70,0]}]}
];
const dnaKeys=[{t:20.1,p:[2.2,1.0,5.8],target:[0,0,0]},{t:23.33,p:[1.4,.6,4.6],target:[0,0,0]}];
const deletionCuts=[
 {id:'deletion-wide',end:25.55,keys:[{t:23.33,p:[0,1.6,8.4],target:[0,0,0]},{t:25.55,p:[.4,1.3,7],target:[0,-.1,0]}]},
 {id:'deletion-detail',end:27.69,keys:[{t:25.55,p:[.45,1.2,5.1],target:[-.25,-.2,0]},{t:27.69,p:[.75,.8,4.5],target:[-.2,-.3,0]}]}
];
function draw(t){t=Math.min(29.7666,Math.max(0,t));let shot,label;
 if(t<20.1){const cut=labCuts.find(x=>t<x.end)||labCuts.at(-1);shot=cut.id;label='RECONSTRUCTED LABORATORY';cameraPath(t,cut.keys);carriage.position.x=-1.4+3.0*sm((t-1.5)/16.0);dust.rotation.y=t*.007;renderer.render(lab,cam);}
 else if(t<23.33){shot='schematic-dna';label='SCHEMATIC · NOT ACTUAL SEQUENCE';cameraPath(t,dnaKeys);helix.rotation.set(-.23,.16+.09*Math.sin(t*.23),.10);helix.position.z=-.15*(t-20.1);motes.rotation.z=.035*(t-20.1);renderer.render(dna,cam);}
 else if(t<27.69){const cut=deletionCuts.find(x=>t<x.end)||deletionCuts.at(-1);shot=cut.id;label='DELETION · CONCEPTUAL SCHEMATIC';cameraPath(t,cut.keys);const u=sm((t-23.75)/1.5);deleted.position.set(0,-u*.95,u*.25);deleted.rotation.z=-u*.20;deletion.rotation.y=.10+.04*(t-23.33);renderer.render(delScene,cam);}
 else {shot='translation-stop';label='TRANSLATION · CONCEPTUAL SCHEMATIC';const u=sm((t-27.69)/1.45);cameraPath(t,[{t:27.69,p:[.25,2.0,8.2],target:[0,.55,0]},{t:29.766,p:[.4,1.75,7.0],target:[0,.6,0]}]);tiles.position.x=-.66*u;machinery.position.y=.03*Math.sin(t*2);peptide.scale.y=.72+.28*u;peptide.rotation.z=.05*Math.sin(t*2);renderer.render(trans,cam);}
 ctx.clearRect(0,0,W,H);ctx.drawImage(renderer.domElement,0,0);ctx.font='700 14px Manrope';ctx.textAlign='right';ctx.fillStyle='rgba(230,241,239,.82)';ctx.fillText(label,W-28,33);
 return {time:t,shot,carriageX:carriage.position.x,camera:cam.position.toArray(),deletedY:deleted.position.y};
}
window.__seek=draw;window.__ready=true;draw(0);
