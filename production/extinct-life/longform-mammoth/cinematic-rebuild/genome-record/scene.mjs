// Conceptual 3D evidence staging; does not depict actual specimens or a laboratory protocol.
import * as T from 'three';
const W=1280,H=720;await document.fonts.load('700 24px Manrope');
const r=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});r.setPixelRatio(1);r.setSize(W,H);r.outputColorSpace=T.SRGBColorSpace;r.toneMapping=T.ACESFilmicToneMapping;r.toneMappingExposure=1.12;
const output=document.createElement('canvas');output.id='final';output.width=W;output.height=H;document.body.appendChild(output);const ctx=output.getContext('2d');
const scene=new T.Scene();scene.background=new T.Color(0xefece3);scene.fog=new T.Fog(0xefece3,18,40);
scene.add(new T.HemisphereLight(0xffffff,0xb9b3a4,2.5));let key=new T.DirectionalLight(0xfff6e8,1.5);key.position.set(-2,8,6);scene.add(key);let edge=new T.DirectionalLight(0xd9c9a8,1.0);edge.position.set(6,4,-5);scene.add(edge);
const metal=new T.MeshStandardMaterial({color:0xd8d2c4,metalness:.05,roughness:.85}), edgeMat=new T.MeshStandardMaterial({color:0xc4bcab,metalness:.08,roughness:.8}), coreA=new T.MeshStandardMaterial({color:0x3a6b78,metalness:.2,roughness:.4}),coreB=new T.MeshStandardMaterial({color:0xd7b786,metalness:.25,roughness:.43});
function box(x,y,z,w,h,d,mat){let m=new T.Mesh(new T.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);scene.add(m);return m}
box(0,-.16,0,14,.25,10,metal);box(0,-.01,0,12,.035,6,new T.MeshStandardMaterial({color:0xe6e1d5,metalness:.05,roughness:.9}));
// A pair of shallow indexed trays provides physical spatial continuity.
function tray(cx,width){box(cx,.05,0,width,.12,3.1,metal);box(cx,.125,0,width-.07,.03,3.02,edgeMat);box(cx,.15,0,width-.14,.025,2.95,new T.MeshStandardMaterial({color:0xdfd8c9,roughness:.9,metalness:.05}))}
tray(-2.75,2.75);tray(1.45,5.35);
const tileMat=new T.MeshStandardMaterial({color:0xd6cfbe,metalness:.05,roughness:.85});const lipMat=new T.MeshStandardMaterial({color:0xb9b1a0,metalness:.1,roughness:.75});const tiles=[];
function tile(x,z,group,n){const object=new T.Group();object.position.set(x,.18,z);scene.add(object);
 let body=new T.Mesh(new T.BoxGeometry(.50,.095,.80),tileMat);body.position.y=.05;object.add(body);
 let inset=new T.Mesh(new T.BoxGeometry(.42,.02,.70),lipMat);inset.position.y=.105;object.add(inset);
 let well=new T.Mesh(new T.BoxGeometry(.37,.015,.65),new T.MeshStandardMaterial({color:0xe9e3d6,metalness:.04,roughness:.85}));well.position.y=.121;object.add(well);
 let cm=(group==='mainland'?coreA:coreB).clone();cm.emissive.set(group==='mainland'?0x2f5d6a:0x8a6420);let core=new T.Mesh(new T.CylinderGeometry(.038,.038,.48,12),cm);core.rotation.x=Math.PI/2;core.position.y=.15;object.add(core);
 let bands=new T.Mesh(new T.BoxGeometry(.24,.008,.018),group==='mainland'?coreA:coreB);bands.position.set(0,.132,.28);object.add(bands);
 tiles.push({object,group,n,core})}
for(let i=0;i<7;i++)tile(-3.55+(i%3)*.80,-.9+Math.floor(i/3)*.9,'mainland',i);
for(let i=0;i<14;i++)tile(-.42+(i%5)*.80,-.9+Math.floor(i/5)*.9,'island',i);
const cam=new T.PerspectiveCamera(35,W/H,.1,50);const smooth=u=>{u=T.MathUtils.clamp(u,0,1);return u*u*(3-2*u)},mix=T.MathUtils.lerp;
function text(txt,x,y,size,color='#2a3032'){ctx.font=`700 ${size}px Manrope`;ctx.fillStyle=color;ctx.fillText(txt,x,y)}
function draw(t){t=T.MathUtils.clamp(t,0,16);const p=smooth(t/8),q=smooth((t-8)/4),v=smooth((t-12)/4);cam.position.set(mix(-4.5,1,p)-.8*q+1.6*v,mix(5.4,8.7,p)-.4*q,mix(7.1,10.1,p)-.6*q);cam.lookAt(mix(-1.8,-.2,p)-.6*q+1.4*v,0,0);
 // Light reveals the whole record, then emphasis changes as spoken origins are named.
 for(const v of tiles){let reveal=smooth((t-.5-(v.group==='mainland'?v.n*.13:.6+v.n*.095))/.8);v.object.visible=reveal>0;v.object.scale.setScalar(.80+.20*reveal);const active=v.group==='mainland'?smooth((t-8.4)/.7)*(1-smooth((t-11.6)/.8)):smooth((t-12.5)/.7);const sweep=Math.exp(-Math.pow((t-(v.group==='mainland'?8.4:12.5)-v.n*.12)/.35,2));v.core.material.emissiveIntensity=.12+.45*active+.8*sweep}
 r.render(scene,cam);ctx.clearRect(0,0,W,H);ctx.drawImage(r.domElement,0,0);
 let a=smooth((t-2.5)/.6);ctx.globalAlpha=a;ctx.textAlign='left';text('THE 2024 GENOME STUDY',55,69,20,'#7d8486');text('21',55,133,53,'#232a2c');text('WOOLLY MAMMOTH GENOMES',142,127,20,'#2a3032');text('THE RECORD SPANS ~50,000 YEARS',56,161,15,'#82898a');
 ctx.globalAlpha=smooth((t-8.4)/.8);text('7  MAINLAND',55,620,22,'#2f5d6a');ctx.globalAlpha=smooth((t-12.5)/.8);text('14  WRANGEL',55,654,22,'#8a6420');ctx.globalAlpha=a;ctx.textAlign='right';text('SCHEMATIC · ONE POSITION PER GENOME',1220,672,14,'#8d9391');text('Dehasque et al. · Cell, 2024',1220,697,14,'#8d9391');ctx.globalAlpha=1;
 return {time:t,tiles:tiles.length,mainland:tiles.filter(x=>x.group==='mainland').length,island:tiles.filter(x=>x.group==='island').length,illustrative:true};}
window.__seek=draw;window.__ready=true;draw(0);
