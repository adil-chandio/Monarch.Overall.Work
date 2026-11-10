// Animation inspection scene, not a documentary shot or approved rig.
import * as T from 'three';
import {GLTFLoader} from '/GLTFLoader.js';
const W=1280,H=720;
await document.fonts.load('700 15px Manrope');
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(1);renderer.setSize(W,H);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.02;
const c=document.createElement('canvas');c.id='final';c.width=W;c.height=H;document.body.appendChild(c);const ctx=c.getContext('2d');
const scene=new T.Scene();scene.background=new T.Color(0x111c22);scene.fog=new T.Fog(0x111c22,15,35);
scene.add(new T.HemisphereLight(0xb4d0e0,0x201c19,1.35));
let key=new T.DirectionalLight(0xffdcb2,2.3);key.position.set(-3,7,5);scene.add(key);
let rim=new T.DirectionalLight(0x8ed1e7,1.4);rim.position.set(3,6,-5);scene.add(rim);
const mat=(color,metal=0,rough=.7)=>new T.MeshStandardMaterial({color,metalness:metal,roughness:rough});
function box(x,y,z,w,h,d,m){let a=new T.Mesh(new T.BoxGeometry(w,h,d),m);a.position.set(x,y,z);scene.add(a);return a;}
const floor=mat(0x17272b,.2,.8),wall=mat(0x1a2b31,.15,.85),edge=mat(0x556667,.5,.4),pedestal=mat(0x242d2e,.18,.8),warm=mat(0xc3a376,.35,.45);
box(0,-.2,0,30,.4,24,floor);box(0,3,-7,30,6,.3,wall);
for(let x=-12;x<=12;x+=3)box(x,3,-6.78,.045,5.8,.04,edge);
box(0,.14,0,3.9,.28,6.8,pedestal);box(0,.29,0,3.88,.04,6.8,edge);
// Experimental modified static model, see README for attribution and limitations.
const asset=await new GLTFLoader().loadAsync('/baby.glb');const obj=asset.scene;
const mixer=new T.AnimationMixer(obj);const walk=mixer.clipAction(asset.animations.find(x=>x.name==='WalkInPlace_Experimental'));walk.play();
let meshes=0,triangles=0;
obj.traverse(o=>{if(o.isMesh){meshes++;triangles+=o.geometry.index ? o.geometry.index.count/3 : o.geometry.attributes.position.count/3;}});
const bounds=new T.Box3().setFromObject(obj);obj.position.y=.31-bounds.min.y;scene.add(obj);
// Physical display rails provide scale and support; they are a designed reconstruction.
for(let z of [-3.5,3.5]){box(-2.15,.58,z,.05,1.16,.05,warm);box(2.15,.58,z,.05,1.16,.05,warm);box(0,.90,z,4.35,.04,.04,warm);}
for(let x of [-2.15,2.15])box(x,.90,0,.04,.04,7,warm);
for(let i=-2;i<=2;i++){box(i*3,5.55,-6.4,1.4,.10,.20,mat(0xabbeb8,.3,.45));let l=new T.PointLight(0xd8b38e,13,8);l.position.set(i*3,5.2,-5.8);scene.add(l);}
const cam=new T.PerspectiveCamera(38,W/H,.1,100);const lerp=(a,b,t)=>a+(b-a)*t;const sm=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t)};
function draw(t){t=Math.max(0,Math.min(11.99,t));let shot,p,target;
 if(t<6){shot='walk-test';p=[2.6,1.5,3.0];target=[0,1.0,0];}
 else{shot='inspection-close';let u=sm((t-6)/6);p=[lerp(2.6,2.1,u),lerp(1.7,1.6,u),lerp(3.0,2.6,u)];target=[0,1.0,0];}
 mixer.setTime(t);cam.position.set(...p);cam.lookAt(...target);renderer.render(scene,cam);ctx.clearRect(0,0,W,H);ctx.drawImage(renderer.domElement,0,0);
 ctx.font='700 14px Manrope';ctx.textAlign='right';ctx.fillStyle='rgba(238,242,234,.9)';ctx.fillText('EXPERIMENTAL WALK · NOT FINAL',W-28,33);
 return {time:t,shot,meshes,triangles,camera:cam.position.toArray(),bounds:{min:bounds.min.toArray(),max:bounds.max.toArray()}};
}
window.__seek=draw;window.__ready=true;draw(0);
