// A conceptual 3D exhibit illustrating the 2024 genome dataset's temporal gap.
import * as T from 'three';
const W=1280,H=720;await document.fonts.load('700 24px Manrope');const r=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});r.setPixelRatio(1);r.setSize(W,H);r.outputColorSpace=T.SRGBColorSpace;r.toneMapping=T.ACESFilmicToneMapping;r.toneMappingExposure=1.1;
const out=document.createElement('canvas');out.id='final';out.width=W;out.height=H;document.body.appendChild(out);const ctx=out.getContext('2d');
const scene=new T.Scene();scene.background=new T.Color(0x08141a);scene.fog=new T.Fog(0x08141a,15,30);scene.add(new T.HemisphereLight(0x99c3ce,0x132527,1.6));let l=new T.DirectionalLight(0xffe5b4,2.6);l.position.set(-2,5,5);scene.add(l);
const metal=new T.MeshStandardMaterial({color:0x4e7880,emissive:0x14343c,emissiveIntensity:.5,roughness:.38,metalness:.35}),dark=new T.MeshStandardMaterial({color:0x18353c,roughness:.65,metalness:.25}),pale=new T.MeshStandardMaterial({color:0xc9e4de,emissive:0x385b58,emissiveIntensity:.4,roughness:.35}),gold=new T.MeshStandardMaterial({color:0xe2b979,emissive:0x9a6831,emissiveIntensity:.35,roughness:.4});
function box(x,y,z,w,h,d,m){let o=new T.Mesh(new T.BoxGeometry(w,h,d),m);o.position.set(x,y,z);scene.add(o);return o}box(0,-.18,0,14,.3,9,metal);box(0,.01,0,10.5,.05,4.6,dark);box(0,.12,-.7,8.5,.13,.065,metal);box(0,.12,1.05,8.5,.13,.065,metal);
// Two independent evidence lanes. Position is an approximate calendar-age illustration,
// not a population curve, or a claim that the remains were continuously sampled.
const xFor=age=>(4400-age)/400*7.4-3.7;const geneX=xFor(4300),boneX=xFor(4000);
for(let age=4400;age>=4000;age-=100){let x=xFor(age);box(x,.16,-.70,.026,.12,.22,metal);box(x,.16,1.05,.026,.12,.22,metal)}
let rod=box(geneX,.22,-.7,.12,.28,.12,pale);let last=box(boneX,.22,1.05,.12,.28,.12,gold);rod.visible=false;last.visible=false;
const dots=[];for(let i=0;i<15;i++){const o=box(mix0(geneX,boneX,(i+1)/16),.225,-.7,.13,.04,.09,new T.MeshStandardMaterial({color:0x93babe,emissive:0x355e62,emissiveIntensity:.55}));o.visible=false;dots.push(o)}function mix0(a,b,u){return a+(b-a)*u}
let lamp=new T.PointLight(0x80d0d0,3,3);scene.add(lamp);let ball=new T.Mesh(new T.SphereGeometry(.065,16,10),pale);scene.add(ball);
const cam=new T.PerspectiveCamera(35,W/H,.1,50),sm=u=>{u=T.MathUtils.clamp(u,0,1);return u*u*(3-2*u)},mix=T.MathUtils.lerp;
function text(s,x,y,size,color){ctx.font=`700 ${size}px Manrope`;ctx.fillStyle=color;ctx.fillText(s,x,y)}
function draw(t){t=T.MathUtils.clamp(t,0,17);let u=sm(t/17);cam.position.set(mix(-2,1.5,u),mix(6.2,7,u),mix(10,9,u));cam.lookAt(0,0,0);const x=mix(-3.7,geneX,sm(t/4));lamp.position.set(x,.65,-.7);ball.position.set(x,.36,-.7);rod.visible=t>=3.3;dots.forEach((d,i)=>d.visible=t>=5+i*.1);last.visible=t>=11;
 r.render(scene,cam);ctx.clearRect(0,0,W,H);ctx.drawImage(r.domElement,0,0);
 ctx.textAlign='left';ctx.globalAlpha=sm(t/.8);text('THE MISSING WITNESS',50,64,22,'#c6dddd');text('2024 GENOME DATASET',50,102,18,'#91b5bb');ctx.textAlign='right';text('PAST  →  MORE RECENT',1230,64,16,'#a7c2c1');ctx.textAlign='left';
 const project=(x,z)=>{const p=new T.Vector3(x,.38,z).project(cam);return [(p.x*.5+.5)*W,(-p.y*.5+.5)*H]};const pg=project(geneX,-.7),pb=project(boneX,1.05);
 ctx.globalAlpha=sm((t-3)/.7);ctx.strokeStyle='#ccebe7';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(pg[0],pg[1]-5);ctx.lineTo(pg[0],pg[1]-62);ctx.lineTo(pg[0]+125,pg[1]-62);ctx.stroke();ctx.textAlign='left';text('YOUNGEST GENOME',pg[0]+8,pg[1]-98,16,'#d4e9e5');text('≈ 4,300 CAL BP',pg[0]+8,pg[1]-72,21,'#eff8f3');
 ctx.globalAlpha=sm((t-5)/.7);ctx.textAlign='left';text('FINAL ~300 YEARS NOT IN THIS GENOME DATASET',50,665,19,'#e4c390');
 ctx.globalAlpha=sm((t-11)/.8);ctx.strokeStyle='#e0c89d';ctx.beginPath();ctx.moveTo(pb[0],pb[1]+5);ctx.lineTo(pb[0],pb[1]+55);ctx.lineTo(pb[0]-170,pb[1]+55);ctx.stroke();ctx.textAlign='right';text('OTHER REMAINS EXTEND LATER',pb[0]-8,pb[1]+81,16,'#e0c89d');text('≈ 4,000 CAL BP',pb[0]-8,pb[1]+107,20,'#e0c89d');
 ctx.globalAlpha=1;ctx.textAlign='right';text('DATES APPROXIMATE · NOT AN ABSENCE OF ALL EVIDENCE',1230,699,13,'#9eb3b3');
 return {time:t,youngest_genome_cal_bp:4300,last_remains_approx_bp:4000,genome_gap_only:true};}
window.__seek=draw;window.__ready=true;draw(0);
