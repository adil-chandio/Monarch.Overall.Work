// Invented modern workbench: not a study location, original sample or protocol.
import * as T from 'three';
import {GLTFLoader} from '/GLTFLoader.js';
const W=1280,H=720,PI=Math.PI;
await document.fonts.load('700 16px Manrope');
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(1);renderer.setSize(W,H);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;
const out=document.createElement('canvas');out.id='final';out.width=W;out.height=H;document.body.appendChild(out);const ctx=out.getContext('2d');
const scene=new T.Scene();scene.background=new T.Color(0x182428);scene.fog=new T.Fog(0x182428,8,25);scene.add(new T.HemisphereLight(0xd4e1da,0x22252a,1.1));
const key=new T.DirectionalLight(0xe6ecdf,2.3);key.position.set(-3,6,3);key.castShadow=true;key.shadow.mapSize.set(1024,1024);key.shadow.camera.left=-4;key.shadow.camera.right=4;key.shadow.camera.top=4;key.shadow.camera.bottom=-4;key.shadow.normalBias=.001;scene.add(key);
const fill=new T.DirectionalLight(0x9dbac0,1.1);fill.position.set(3,2,-2);scene.add(fill);
let seed=30780;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};const clamp=T.MathUtils.clamp,mix=T.MathUtils.lerp,sm=x=>{x=clamp(x,0,1);return x*x*(3-2*x)};
const mat=(color,metalness=0,roughness=.7)=>new T.MeshStandardMaterial({color,metalness,roughness});const steel=mat(0x8c9895,.75,.4),darkSteel=mat(0x35464a,.65,.45),paper=mat(0xd6d2bd,0,.95),rubber=mat(0x263231,.02,.82),black=mat(0x111a1c,.32,.42);
function box(parent,p,s,m){let x=new T.Mesh(new T.BoxGeometry(...s),m);x.position.set(...p);x.castShadow=true;x.receiveShadow=true;parent.add(x);return x}
function cyl(parent,p,r1,r2,h,m){let o=new T.Mesh(new T.CylinderGeometry(r1,r2,h,32),m);o.position.set(...p);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o}
// Surfaces and side rails in true 3D, with deliberately subdued markings.
const surfaceCanvas=document.createElement('canvas');surfaceCanvas.width=surfaceCanvas.height=512;const sc=surfaceCanvas.getContext('2d');sc.fillStyle='#7d8a87';sc.fillRect(0,0,512,512);for(let i=0;i<8000;i++){let x=rand()*512,y=rand()*512;sc.fillStyle=rand()>.5?'rgba(240,240,225,.015)':'rgba(22,35,34,.025)';sc.fillRect(x,y,5+rand()*80,.3+rand()*.5)}const surfaceTex=new T.CanvasTexture(surfaceCanvas);surfaceTex.colorSpace=T.SRGBColorSpace;surfaceTex.wrapS=surfaceTex.wrapT=T.RepeatWrapping;surfaceTex.repeat.set(3,2);const worktop=new T.MeshStandardMaterial({map:surfaceTex,metalness:.45,roughness:.68});
box(scene,[0,-.10,0],[7,.2,4.6],darkSteel);box(scene,[0,.006,0],[7,.014,4.6],worktop);box(scene,[0,1.0,-2.25],[7,2,.12],mat(0x334348,.18,.75));
for(let i=-3;i<4;i++){box(scene,[i,1,-2.18],[.012,1.9,.012],mat(0x506267,.4,.65))}
// Specimen pads and tiny paper slips. Wording is context, not a fabricated ID.
function label(text){let c=document.createElement('canvas');c.width=512;c.height=128;let x=c.getContext('2d');x.fillStyle='#e3dfd0';x.fillRect(0,0,512,128);x.fillStyle='#25322f';x.font='bold 27px Manrope, sans-serif';x.fillText(text,18,43);x.font='22px Manrope, sans-serif';x.fillText('ILLUSTRATIVE · NOT AN ORIGINAL SPECIMEN',18,84);const tx=new T.CanvasTexture(c);tx.colorSpace=T.SRGBColorSpace;return tx}
function tray(x,title){let group=new T.Group();group.position.x=x;scene.add(group);box(group,[0,.045,0],[1.8,.09,1.35],darkSteel);box(group,[0,.097,0],[1.69,.018,1.24],paper);for(let i=0;i<5;i++){let g=mat(0xaaa995,0,.92);box(group,[-.75+i*.37,.108,0],[.006,.003,1.1],g)}
 let slip=new T.Mesh(new T.PlaneGeometry(.92,.23),new T.MeshStandardMaterial({map:label(title),roughness:1,side:T.DoubleSide}));slip.rotation.x=-PI/2;slip.position.set(0,.115,.46);group.add(slip);return group}
const trays=[tray(-1.08,'SIBERIAN MAINLAND'),tray(1.08,'WRANGEL ISLAND')];
// Both props derive from the same unverified reference mesh, transformed as
// generic comparison material. They are not the actual sequenced samples.
const boneCan=document.createElement('canvas');boneCan.width=boneCan.height=512;let b=boneCan.getContext('2d');b.fillStyle='#b7a68b';b.fillRect(0,0,512,512);for(let i=0;i<14000;i++){let x=rand()*512,y=rand()*512;b.fillStyle=rand()>.5?'rgba(53,47,35,.09)':'rgba(241,227,198,.12)';b.fillRect(x,y,1+rand()*5,1+rand()*4)}let tex=new T.CanvasTexture(boneCan);tex.colorSpace=T.SRGBColorSpace;tex.wrapS=tex.wrapT=T.RepeatWrapping;const boneMat=new T.MeshStandardMaterial({map:tex,roughness:.94,side:T.DoubleSide});
const models=await Promise.all(['/mainland-prop.glb','/island-prop.glb'].map(x=>new GLTFLoader().loadAsync(x)));const fragments=[];
for(let i=0;i<2;i++){let obj=models[i].scene.clone(true);obj.scale.setScalar(i?.78:.87);obj.rotation.set(0,i?-.35:.3,0);obj.position.set(i?.08:-.05,.24,-.12);obj.traverse(o=>{if(o.isMesh){o.geometry.computeVertexNormals();o.material=boneMat;o.castShadow=true;o.receiveShadow=true}});trays[i].add(obj);obj.updateMatrixWorld(true);let bounds=new T.Box3().setFromObject(obj);obj.position.y+=.116-bounds.min.y;obj.updateMatrixWorld(true);fragments.push(obj)}
// The researcher's hand carries a small lamp across the trays. It does not
// touch, cut, or transfer a sample and is not a reconstruction of a protocol.
const arm=new T.Group();scene.add(arm);
const gloveData=await new GLTFLoader().loadAsync('/glove.glb');const hand=gloveData.scene;hand.scale.setScalar(.19);hand.rotation.x=-PI/2;hand.rotation.z=.24;hand.position.set(0,.42,.15);arm.add(hand);
for(const chain of [['Index_Finger','Lower001','Middle001','Top001'],['Middle_Finger','Lower002','Middle002','Top002'],['Ring_Finger','Lower003','Middle003','Top003'],['Pinky','Lower004','Middle004','Top004']]){[15,35,35,15].forEach((d,i)=>{const o=hand.getObjectByName(chain[i]);if(o)o.rotateX(T.MathUtils.degToRad(d))})}
const th=hand.getObjectByName('Thumb');if(th){th.rotateX(T.MathUtils.degToRad(20));th.rotateY(T.MathUtils.degToRad(20));th.rotateZ(T.MathUtils.degToRad(50))}for(const [n,d] of [['Middle',30],['Top',11.5]]){let o=hand.getObjectByName(n);if(o)o.rotateX(T.MathUtils.degToRad(d))}
hand.traverse(o=>{if(o.isMesh){o.frustumCulled=false;let ms=Array.isArray(o.material)?o.material:[o.material];o.material=ms.map(m=>{let a=m.clone();a.color.set(m.name==='Glove'?0xadc7c3:0xcbd8d1);a.roughness=.8;a.metalness=0;return a});if(o.material.length===1)o.material=o.material[0];o.castShadow=true}});
cyl(arm,[0,.22,0],.055,.055,.40,rubber);cyl(arm,[0,.04,0],.085,.073,.12,black);cyl(arm,[0,-.027,0],.069,.069,.015,new T.MeshBasicMaterial({color:0xffe8bd}));
let sleeve=cyl(arm,[.23,1.0,.03],.16,.14,1.0,mat(0xc8d2ca,0,.9));sleeve.rotation.z=-.37;
const spot=new T.SpotLight(0xffe9c6,2.6,3,PI/5,.75,1.2);spot.position.set(0,0,0);spot.target.position.set(0,-1,0);arm.add(spot);arm.add(spot.target);
// Labels on-screen are editorial context, not claims about the props' identity.
const cam=new T.PerspectiveCamera(33,W/H,.05,35);const target=new T.Vector3();
function draw(t){t=clamp(t,0,20);let u=sm((t-9.8)/3.2),x=mix(-1.08,1.08,u);arm.position.set(x,.82,-.12);arm.rotation.z=.045*Math.sin(t*.9);let close=sm((t-.4)/2.8);cam.position.set(mix(-1.15,mix(-.95,1.0,u),close),mix(2.3,1.35,close),mix(4.25,2.25,close));target.set(mix(-.58,mix(-1.08,1.08,u),close),mix(.30,.20,close),-.08);cam.lookAt(target);renderer.render(scene,cam);ctx.clearRect(0,0,W,H);ctx.drawImage(renderer.domElement,0,0);
 ctx.textAlign='left';ctx.fillStyle='rgba(241,242,232,.93)';ctx.shadowColor='rgba(0,0,0,.9)';ctx.shadowBlur=5;ctx.font='700 14px Manrope';ctx.fillText('ILLUSTRATIVE COMPARISON · NOT ORIGINAL SPECIMENS',28,H-29);
 ctx.font='700 17px Manrope';ctx.textAlign='right';ctx.fillText('2017 GENOME COMPARISON · TWO INDIVIDUALS',W-28,34);ctx.shadowBlur=0;
 return {time:t,light_x:x,comparison:'2017 two individuals',original_specimens:false,actual_protocol:false};}
window.__seek=draw;window.__ready=true;draw(0);
