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
// Distinct motivated camera cuts, timed to the narration rather than arbitrary motion.
const labCuts=[
 {id:'lab-specimen',end:5.2,keys:[{t:0,p:[2.9,2.0,4.5],target:[-1.35,.5,0]},{t:5.2,p:[1.9,1.40,3.1],target:[-1.35,.5,0]}]},
 {id:'lab-mainland',end:10.3,keys:[{t:5.2,p:[.15,1.28,3.15],target:[.65,.68,.42]},{t:10.3,p:[.43,1.16,2.5],target:[.65,.68,.42]}]},
 {id:'lab-wrangel',end:15.7,keys:[{t:10.3,p:[1.90,1.23,3.25],target:[1.58,.68,.42]},{t:15.7,p:[1.73,1.13,2.48],target:[1.58,.68,.42]}]},
 {id:'lab-comparison',end:20.1,keys:[{t:15.7,p:[2.65,1.4,3.25],target:[1.1,.68,.42]},{t:20.1,p:[4.2,2.2,5.2],target:[.5,.70,0]}]}
];
const dnaKeys=[{t:20.1,p:[3.6,1.8,7.3],target:[0,0,0]},{t:25,p:[3.5,1.5,7.1],target:[0,0,0]},{t:29.767,p:[3.25,1.25,7.0],target:[0,0,0]}];
function draw(t){t=Math.min(29.7666,Math.max(0,t));const isDNA=t>=20.1;
 if(isDNA){cameraPath(t,dnaKeys);helix.rotation.set(-.23,.16+.09*Math.sin(t*.23),.10);helix.position.z=-.15*(t-20.1);motes.rotation.z=.035*(t-20.1);rung.forEach((r,i)=>{r.visible=true;r.scale.setScalar(1);});renderer.render(dna,cam);}
 else{const cut=labCuts.find(x=>t<x.end)||labCuts.at(-1);cameraPath(t,cut.keys);carriage.position.x=-1.4+3.0*sm((t-1.5)/16.0);dust.rotation.y=t*.007;renderer.render(lab,cam);}
 ctx.clearRect(0,0,W,H);ctx.drawImage(renderer.domElement,0,0);ctx.font='700 14px Manrope';ctx.textAlign='right';ctx.fillStyle='rgba(230,241,239,.82)';ctx.fillText(isDNA?'SCHEMATIC · NOT ACTUAL SEQUENCE':'RECONSTRUCTED LABORATORY',W-28,33);
 return {time:t,shot:isDNA?'schematic-dna':(labCuts.find(x=>t<x.end)||labCuts.at(-1)).id,carriageX:carriage.position.x,camera:cam.position.toArray()};
}
window.__seek=draw;window.__ready=true;draw(0);
