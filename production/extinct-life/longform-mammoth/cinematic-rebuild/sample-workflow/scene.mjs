// Illustrative modern sample transfer, not footage or the published lab protocol.
import * as T from 'three';
import {GLTFLoader} from '/GLTFLoader.js';
const W=1280,H=720;await document.fonts.load('700 14px Manrope');
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(1);renderer.setSize(W,H);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.12;
const out=document.createElement('canvas');out.id='final';out.width=W;out.height=H;document.body.appendChild(out);const ctx=out.getContext('2d');
const scene=new T.Scene();scene.background=new T.Color(0x0a1a21);scene.fog=new T.Fog(0x0a1a21,8,35);
scene.add(new T.HemisphereLight(0xc6e8ef,0x292325,1.5));const key=new T.DirectionalLight(0xd0efff,3);key.position.set(-3,6,4);scene.add(key);const rim=new T.DirectionalLight(0xffd5a4,2);rim.position.set(3,5,-4);scene.add(rim);const point=new T.PointLight(0x70c9d7,5,8);point.position.set(0,3,1);scene.add(point);
const sm=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)},mix=(a,b,u)=>a+(b-a)*u;
const mat=(c,m=0,r=.5)=>new T.MeshStandardMaterial({color:c,metalness:m,roughness:r});
const bench=mat(0x263e43,.4,.58),dark=mat(0x14272e,.45,.42),steel=mat(0xa6bdc1,.75,.28),bone=mat(0xbea486,0,.88),glove=mat(0x87b6c1,0,.65),fabric=mat(0xd1d9d6,0,.82),amber=mat(0xc49d6c,.48,.42);
function box(parent,p,s,m){const o=new T.Mesh(new T.BoxGeometry(...s),m);o.position.set(...p);parent.add(o);return o}
function sphere(parent,p,s,m){const o=new T.Mesh(new T.SphereGeometry(1,24,16),m);o.position.set(...p);o.scale.set(...s);parent.add(o);return o}
function line(parent,a,b,r,m){const v=new T.Vector3(...a),w=new T.Vector3(...b);const o=new T.Mesh(new T.CylinderGeometry(r,r,v.distanceTo(w),12),m);o.position.copy(v).add(w).multiplyScalar(.5);o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),w.sub(v).normalize());parent.add(o);return o}
function cylinder(parent,p,r1,r2,h,m){const o=new T.Mesh(new T.CylinderGeometry(r1,r2,h,32),m);o.position.set(...p);parent.add(o);return o}
// Bench and edge rails create real spatial surfaces.
box(scene,[0,-.16,0],[9,.32,5],bench);box(scene,[0,.012,0],[9,.024,5],mat(0x38535a,.33,.45));box(scene,[0,2,-2.5],[9,4,.2],dark);for(let i=-4;i<=4;i+=2)box(scene,[i,2,-2.38],[.025,3.7,.03],mat(0x48606a,.45,.4));
box(scene,[-1,.07,0],[1.48,.12,1.25],dark);box(scene,[-1,.14,0],[1.34,.04,1.12],steel);
// Procedural bone fragments are invented generic material, never actual specimen.
const boneTex=document.createElement('canvas');boneTex.width=boneTex.height=256;const bc=boneTex.getContext('2d');bc.fillStyle='#bba181';bc.fillRect(0,0,256,256);let seed=4192;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};for(let i=0;i<2500;i++){bc.fillStyle=rand()>.5?'rgba(50,34,24,.08)':'rgba(248,226,190,.12)';bc.fillRect(rand()*256,rand()*256,1+rand()*5,1+rand()*3)}const bt=new T.CanvasTexture(boneTex);bt.colorSpace=T.SRGBColorSpace;const boneMat=new T.MeshStandardMaterial({map:bt,roughness:.96});
function fragment(x,z,scale,rot){const geom=new T.IcosahedronGeometry(1,3),p=geom.attributes.position;for(let i=0;i<p.count;i++){let x=p.getX(i),y=p.getY(i),z=p.getZ(i);let n=1+.12*Math.sin(x*8+y*13)*Math.sin(z*19+y*8)+.08*Math.cos(x*17-z*13);p.setXYZ(i,x*.35*n,y*.16*n,z*.23*n)}geom.computeVertexNormals();const o=new T.Mesh(geom,boneMat);o.position.set(x,.29,z);o.rotation.y=rot;o.scale.setScalar(scale);scene.add(o)}
fragment(-1.24,-.16,1.05,.45);fragment(-.75,.25,.73,-.4);
// Clear open sample vessel: transparent wall and visible interior.
const glass=new T.MeshPhongMaterial({color:0xb2d9db,transparent:true,opacity:.24,shininess:100,depthWrite:false,side:T.DoubleSide});
const tube=new T.Group();tube.position.set(.95,0,0);scene.add(tube);cylinder(tube,[0,.39,0],.19,.17,.56,glass);cylinder(tube,[0,.11,0],.17,.17,.045,steel);const rimGeo=new T.TorusGeometry(.19,.018,10,32);let lip=new T.Mesh(rimGeo,steel);lip.rotation.x=Math.PI/2;lip.position.y=.67;tube.add(lip);
// Context equipment is arranged behind the work area.
box(scene,[1.78,.11,-.84],[1.42,.22,.72],dark);for(let i=0;i<4;i++){const x=1.29+i*.29;cylinder(scene,[x,.4,-.84],.045,.045,.55,glass);cylinder(scene,[x,.69,-.84],.065,.065,.06,amber)}
box(scene,[-2.75,.18,-.83],[1.30,.35,.65],dark);box(scene,[-2.75,.37,-.83],[1.18,.035,.56],steel);
// Forceps tips approach the specimen from above; hand is an approximate glove,
// not a performance capture. A shared transform does not prove physical contact.
const tool=new T.Group();scene.add(tool);
const jaws=[line(tool,[-.06,.62,0],[-.074,.07,0],.012,steel),line(tool,[.06,.62,0],[.074,.07,0],.012,steel)];line(tool,[-.06,.62,0],[.06,.62,0],.014,steel);
function placeJaw(o,a,b){let v=new T.Vector3(...a),w=new T.Vector3(...b),delta=w.clone().sub(v);o.position.copy(v).add(w).multiplyScalar(.5);o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),delta.clone().normalize());o.scale.y=delta.length()/.55018;}
// Adapted third-party rig: a posed, recoloured glove; see README for CC BY.
const handAsset=await new GLTFLoader().loadAsync('/glove.glb');const hand=handAsset.scene;hand.scale.setScalar(.26);hand.rotation.x=-Math.PI/2;hand.position.set(-.03,.89,.17);tool.add(hand);
const fingerChains=[['Index_Finger','Lower001','Middle001','Top001'],['Middle_Finger','Lower002','Middle002','Top002'],['Ring_Finger','Lower003','Middle003','Top003'],['Pinky','Lower004','Middle004','Top004']];
for(const chain of fingerChains){[15,35,35,15].forEach((d,i)=>{const b=hand.getObjectByName(chain[i]);if(b)b.rotateX(T.MathUtils.degToRad(d))})}
const thumb=hand.getObjectByName('Thumb');thumb.rotateX(T.MathUtils.degToRad(20));thumb.rotateY(T.MathUtils.degToRad(20));thumb.rotateZ(T.MathUtils.degToRad(50));for(const [n,d] of [['Middle',30],['Top',11.5]]){const b=hand.getObjectByName(n);if(b)b.rotateX(T.MathUtils.degToRad(d))}
hand.traverse(o=>{if(o.isMesh){o.frustumCulled=false;const mats=Array.isArray(o.material)?o.material:[o.material];o.material=mats.map(m=>{let c=m.clone();c.color.set(m.name==='Glove'?0x93bdc2:0xd2dedc);c.metalness=0;c.roughness=.72;return c});if(o.material.length===1)o.material=o.material[0]}});
// Simplified sleeve joins the wrist and exits the top of frame; not an anatomical arm.
line(tool,[-.014,1.14,-.014],[.38,2.15,.08],.16,fabric);
const sample=new T.Mesh(new T.IcosahedronGeometry(.085,0),boneMat);scene.add(sample);
const cam=new T.PerspectiveCamera(34,W/H,.05,50);
function draw(t){t=Math.max(0,Math.min(14,t));let x=-1,y=.22;
 if(t>=1.4&&t<3.8)y=mix(.22,.92,sm((t-1.4)/2.4));
 else if(t>=3.8&&t<7){y=.92;x=mix(-1,.95,sm((t-3.8)/3.2))}
 else if(t>=7&&t<9.4){x=.95;y=mix(.92,.39,sm((t-7)/2.4))}
 else if(t>=9.4){x=.95;y=mix(.39,1.12,sm((t-9.65)/2.1))}
 tool.position.set(x,y,0);const opened=sm((t-9.2)/.5),spread=mix(.074,.16,opened);placeJaw(jaws[0],[-.06,.62,0],[-spread,.07,0]);placeJaw(jaws[1],[.06,.62,0],[spread,.07,0]);const fallen=t<9.4?y+.07:Math.max(.205,.46-4.9*(t-9.4)**2);sample.position.set(t<9.4?x:.95,fallen,0);
 const q=sm(Math.min(1,t/14));cam.position.set(mix(2.4,2.05,q),mix(2.5,2.13,q),mix(5.5,4.5,q));cam.lookAt(mix(-.5,.45,q),.45,0);
 renderer.render(scene,cam);ctx.clearRect(0,0,W,H);ctx.drawImage(renderer.domElement,0,0);ctx.textAlign='right';ctx.fillStyle='rgba(230,240,239,.9)';ctx.font='700 14px Manrope';ctx.fillText('ILLUSTRATIVE SAMPLE PREPARATION',W-28,33);
 return {time:t,tool:tool.position.toArray(),sample:sample.position.toArray(),released:t>=9.4};}
window.__handProbe=(t)=>{draw(t);scene.updateMatrixWorld(true);return ['Top','Top001','Top002','Top003','Top004','Wrist'].map(n=>{const bone=hand.getObjectByName(n);const p=new T.Vector3();bone.getWorldPosition(p);return {name:n,relative:tool.worldToLocal(p).toArray()}})};
window.__seek=draw;window.__ready=true;draw(0);
