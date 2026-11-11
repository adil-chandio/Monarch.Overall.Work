// Island chapter — seven illustrative shots in one invented Arctic world.
// Not a reconstruction of Wrangel: terrain, stream, weather, herd size and every
// animal position are authored. Third-party rig; see ../mammoth-rig/README.md.
// The only text on screen is a disclosure line; no dates or place claims.
import * as T from 'three';
import {GLTFLoader} from '/GLTFLoader.js';
import {clone} from '/utils/SkeletonUtils.js';
const W=1280,H=720,PI=Math.PI,FPS=30,DURATION=60;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.06;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
const scene=new T.Scene();scene.fog=new T.Fog(0xb9c6c8,24,150);
let seed=1204457;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};const lerp=(a,b,u)=>a+(b-a)*u;
// --- sky and light -----------------------------------------------------------
const uSky={value:0},uStorm={value:0};
const sky=new T.Mesh(new T.SphereGeometry(250,36,20),new T.ShaderMaterial({side:T.BackSide,depthWrite:false,uniforms:{uSky,uStorm},vertexShader:`varying vec3 w;void main(){w=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*modelMatrix*vec4(position,1.);}`,fragmentShader:`uniform float uSky;uniform float uStorm;varying vec3 w;void main(){vec3 d=normalize(w);float h=clamp(d.y,0.,1.);vec3 dawn=mix(vec3(.83,.72,.60),vec3(.26,.40,.55),smoothstep(0.,.8,h));vec3 day=mix(vec3(.76,.80,.80),vec3(.28,.46,.64),smoothstep(0.,.85,h));vec3 dusk=mix(vec3(.72,.55,.44),vec3(.10,.18,.32),smoothstep(0.,.7,h));vec3 c=mix(dawn,day,smoothstep(0.,.35,uSky));c=mix(c,dusk,smoothstep(.62,1.,uSky));c=mix(c,vec3(.62,.66,.68),uStorm*.72);c=mix(c,vec3(.34,.38,.41),uStorm*smoothstep(.15,.9,h));gl_FragColor=vec4(c,1.);}`}));scene.add(sky);
const sun=new T.DirectionalLight(0xffe6c6,2.5);sun.position.set(-24,17,12);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-26;sun.shadow.camera.right=26;sun.shadow.camera.top=26;sun.shadow.camera.bottom=-26;sun.shadow.camera.near=.5;sun.shadow.camera.far=110;sun.shadow.bias=-.00035;sun.shadow.normalBias=.004;scene.add(sun);
const hemi=new T.HemisphereLight(0xcfe2ee,0x54503f,1.95);scene.add(hemi);
const fill=new T.DirectionalLight(0xd9e8f2,.45);fill.position.set(18,10,26);scene.add(fill);
// --- ground, ridge, sea ------------------------------------------------------
const snowCanvas=document.createElement('canvas');snowCanvas.width=snowCanvas.height=512;const sg=snowCanvas.getContext('2d');sg.fillStyle='#e3e8e3';sg.fillRect(0,0,512,512);for(let i=0;i<12000;i++){sg.fillStyle=`rgba(64,88,90,${.012+rand()*.038})`;sg.fillRect(rand()*512,rand()*512,1+rand()*6,1+rand()*2)}
const snowTex=new T.CanvasTexture(snowCanvas);snowTex.colorSpace=T.SRGBColorSpace;snowTex.wrapS=snowTex.wrapT=T.RepeatWrapping;snowTex.repeat.set(34,34);
const tundra=await new T.TextureLoader().loadAsync('/tundra.jpg');tundra.colorSpace=T.SRGBColorSpace;tundra.wrapS=tundra.wrapT=T.RepeatWrapping;tundra.repeat.set(34,34);
const groundMat=new T.MeshStandardMaterial({color:0xd6dbd4,map:tundra,roughness:1});
groundMat.onBeforeCompile=sh=>{sh.uniforms.snowMap={value:snowTex};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 tP;').replace('#include <begin_vertex>','#include <begin_vertex>\ntP=position;');sh.fragmentShader=sh.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 tP;uniform sampler2D snowMap;').replace('#include <map_fragment>','#ifdef USE_MAP\nfloat lp=.5+.5*(sin(tP.x*.23+sin(tP.z*.17))*cos(tP.z*.19+tP.x*.07)*.75+sin(tP.x*.83-tP.z*.61)*.25);\nfloat cover=smoothstep(.34,.62,lp+.12);\nvec4 soil=texture2D(map,vMapUv),snow=texture2D(snowMap,vMapUv);\nvec3 bare=mix(vec3(.35,.35,.28),vec3(.52,.48,.36),lp);\ndiffuseColor.rgb=mix(bare,snow.rgb*.97,cover*.92);\n#endif')};
// A shallow braided channel cuts across the plain for the wading shot.
const CH={z0:-6.4,z1:-3.2};
function channel(x,z){const w=.5+.35*Math.sin(x*.21+.6)+.22*Math.sin(x*.57-1.1);const d=Math.abs(z-(CH.z0+CH.z1)/2)-w;return {depth:-.15*(1-smooth(d/.9)),near:d<.55}}
const groundGeo=new T.PlaneGeometry(200,170,150,120);groundGeo.rotateX(-PI/2);const gp=groundGeo.attributes.position;
function terrain(x,z){const flat=smooth((Math.abs(z)-4)/10);const roll=flat*(.5*Math.sin(x*.12)*Math.cos(z*.1)+.28*Math.sin(x*.27+z*.17));const ch=channel(x,z);return roll-.04+ch.depth*(ch.near?1:0)}
for(let i=0;i<gp.count;i++)gp.setY(i,terrain(gp.getX(i),gp.getZ(i)));
groundGeo.computeVertexNormals();const ground=new T.Mesh(groundGeo,groundMat);ground.receiveShadow=true;scene.add(ground);
// Ridge behind; snowline carries the dawn/dusk palette.
const ridgeGeo=new T.PlaneGeometry(200,80,180,60);ridgeGeo.rotateX(-PI/2);const rp=ridgeGeo.attributes.position;
for(let i=0;i<rp.count;i++){const x=rp.getX(i),z=rp.getZ(i);const dep=smooth((z+40)/20)*smooth((40-z)/13);const crest=2.9+1.7*Math.sin(x*.075+.9)+1.1*Math.sin(x*.17+2.3)+.55*Math.sin(x*.36);rp.setY(i,Math.max(0,dep*crest))}
ridgeGeo.computeVertexNormals();const ridge=new T.Mesh(ridgeGeo,new T.MeshStandardMaterial({color:0x93a5b0,roughness:1}));ridge.position.set(0,-.55,-58);scene.add(ridge);
const seaClock={value:0};const seaGeo=new T.PlaneGeometry(520,240,140,60);seaGeo.rotateX(-PI/2);
const sea=new T.Mesh(seaGeo,new T.ShaderMaterial({uniforms:{time:seaClock},vertexShader:`uniform float time;varying vec3 lp;void main(){vec3 p=position;float w=sin(p.x*.22+p.z*.41+time*.55)*.05+sin(p.x*.51-p.z*.24+time*.4)*.025;w*=1.-smoothstep(40.,120.,120.-p.z);p.y+=w;lp=p;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,fragmentShader:`uniform float time;varying vec3 lp;void main(){float s=sin(lp.x*.9+sin(lp.z*.27+time*.1)+time*.33)*sin(lp.z*.62+lp.x*.15-time*.25);vec3 c=mix(vec3(.13,.22,.26),vec3(.34,.44,.46),clamp(s*.5+.5,0.,1.));c+=pow(max(0.,s),18.)*.30;float haze=smoothstep(20.,110.,120.-lp.z);c=mix(c,vec3(.55,.60,.60),haze*.85);gl_FragColor=vec4(c,1.);}`}));sea.position.set(0,-1.05,-150);scene.add(sea);
// Stream water inside the channel, with a pebble bed under it.
const streamClock={value:0};const streamGeo=new T.PlaneGeometry(160,3.6,120,12);streamGeo.rotateX(-PI/2);
const stream=new T.Mesh(streamGeo,new T.ShaderMaterial({transparent:true,uniforms:{time:streamClock},vertexShader:`uniform float time;varying vec3 lp;varying float h;void main(){vec3 p=position;float w=sin(p.x*.9+p.z*1.7+time*1.6)*.018+sin(p.x*2.1-p.z*.8+time*2.3)*.008;p.y+=w;lp=p;h=w;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,fragmentShader:`uniform float time;varying vec3 lp;varying float h;void main(){float s=sin(lp.x*2.2+time*1.4)*sin(lp.z*3.1-lp.x*.7-time*.9);vec3 c=mix(vec3(.16,.28,.31),vec3(.40,.52,.54),clamp(h*22.+.5,0.,1.));c+=pow(max(0.,s),12.)*.35;gl_FragColor=vec4(c,.82);}`}));
stream.position.set(0,-.055,(CH.z0+CH.z1)/2);scene.add(stream);
const pebbleGeo=new T.BufferGeometry();const PN=420;const pp=new Float32Array(PN*3);const pc=new Float32Array(PN*3);
for(let i=0;i<PN;i++){const x=rand()*90-45;const ch=channel(x,0);const z=(CH.z0+CH.z1)/2+(rand()-.5)*2.2;pp[3*i]=x;pp[3*i+1]=-.16+rand()*.03;pp[3*i+2]=z;const v=.34+rand()*.28;pc[3*i]=v;pc[3*i+1]=v*.96;pc[3*i+2]=v*.9}
pebbleGeo.setAttribute('position',new T.BufferAttribute(pp,3));pebbleGeo.setAttribute('color',new T.BufferAttribute(pc,3));
const pebbles=new T.Points(pebbleGeo,new T.PointsMaterial({size:.05,vertexColors:true,transparent:true,opacity:.85}));scene.add(pebbles);
// Vegetation: tufts on the plain, a denser patch where the trunk reaches.
const verts=[];for(let j=0;j<6;j++){const a=j*PI/6,dx=Math.cos(a),dz=Math.sin(a),bend=(j%2?.13:-.12),ht=.30+j*.045;const at=(v,side)=>[dx*side*.022*(1-v)+bend*v*v,ht*v,dz*side*.022*(1-v)+bend*.3*v*v];for(let k=0;k<3;k++){const u=k/3,v=(k+1)/3;verts.push(...at(u,-1),...at(u,1),...at(v,-1),...at(u,1),...at(v,1),...at(v,-1))}}
const tuftGeo=new T.BufferGeometry();tuftGeo.setAttribute('position',new T.Float32BufferAttribute(verts,3));tuftGeo.computeVertexNormals();
const wind={value:0};const tuftMat=new T.MeshStandardMaterial({color:0xb3a884,roughness:1,side:T.DoubleSide});
tuftMat.onBeforeCompile=sh=>{sh.uniforms.wind={value:wind};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nuniform float wind;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x+=sin(wind*1.15+instanceMatrix[3].x*.5)*position.y*position.y*(.10+step(2.,instanceMatrix[3].z)*.05);')};
const tufts=new T.InstancedMesh(tuftGeo,tuftMat,4200);const dm=new T.Object3D();
for(let i=0;i<4200;i++){const x=rand()*110-55,z=rand()*70-32;if(Math.abs(z-(CH.z0+CH.z1)/2)<2.4){i--;continue}dm.position.set(x,terrain(x,z)+.01,z);dm.rotation.set(0,rand()*PI,.07*(rand()-.5));dm.scale.setScalar(.3+rand()*.8);dm.updateMatrix();tufts.setMatrixAt(i,dm.matrix);tufts.setColorAt(i,new T.Color().setHSL(.11,.13,.30+rand()*.18))}scene.add(tufts);
// Stones and low snow drift shapes.
const stoneMat=new T.MeshStandardMaterial({color:0x5e6660,roughness:1});
for(let i=0;i<90;i++){const x=rand()*70-35,z=rand()*40-20;if(Math.abs(z-(CH.z0+CH.z1)/2)<2.2)continue;const r=.04+rand()*.20;const o=new T.Mesh(new T.DodecahedronGeometry(1,1),stoneMat);o.position.set(x,terrain(x,z)+r*.25,z);o.scale.set(r,r*(.3+rand()*.35),r*(.7+rand()*.5));o.rotation.set(rand()*.4,rand()*PI,rand()*.3);o.castShadow=true;o.receiveShadow=true;scene.add(o)}
// Spindrift: one particle field, strength driven per shot.
const snowGeo=new T.BufferGeometry();const SPN=1400;const sp=new Float32Array(SPN*3);
for(let i=0;i<SPN;i++){sp[3*i]=rand()*70-35;sp[3*i+1]=rand()*8;sp[3*i+2]=rand()*46-23}
snowGeo.setAttribute('position',new T.BufferAttribute(sp,3));
const snowMat=new T.PointsMaterial({color:0xeef4f4,size:.085,transparent:true,opacity:.5,depthWrite:false});
snowMat.onBeforeCompile=sh=>{sh.uniforms.wind={value:wind};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nuniform float wind;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x=mod(position.x+wind*1.35+35.,70.)-35.;transformed.y=mod(position.y-wind*.16+800.,8.);transformed.z+=sin(wind*.5+position.x*.3)*1.2;')};
const snowfall=new T.Points(snowGeo,snowMat);scene.add(snowfall);
// A second, coarser flake layer rides with the camera. Small distant specks do not
// read as weather; a squall needs visible flakes sweeping past the lens.
const nearGeo=new T.BufferGeometry();const NSN=520;const nsp=new Float32Array(NSN*3);
for(let i=0;i<NSN;i++){nsp[3*i]=rand()*12-6;nsp[3*i+1]=rand()*6;nsp[3*i+2]=rand()*12-6}
nearGeo.setAttribute('position',new T.BufferAttribute(nsp,3));
const nearMat=new T.PointsMaterial({color:0xf4f8f8,size:.075,transparent:true,opacity:0,depthWrite:false,sizeAttenuation:true});
nearMat.onBeforeCompile=sh=>{sh.uniforms.wind={value:wind};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nuniform float wind;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x=mod(position.x+wind*2.6+6.,12.)-6.;transformed.y=mod(position.y-wind*.55+600.,6.);transformed.z=mod(position.z+wind*.35+6.,12.)-6.;')};
const nearSnow=new T.Points(nearGeo,nearMat);nearSnow.frustumCulled=false;scene.add(nearSnow);
// --- animals -----------------------------------------------------------------
const asset=await new GLTFLoader().loadAsync('/mammoth.glb');const model=asset.scene;let triangles=0;model.traverse(o=>{if(o.isMesh)triangles+=o.geometry.index?o.geometry.index.count/3:o.geometry.attributes.position.count/3});
const clip=asset.animations.find(a=>a.name==='WalkInPlace_Experimental');if(!clip)throw Error('walk clip missing');
const t0=Math.min(...clip.tracks.map(t=>t.times[0]));for(const tr of clip.tracks)tr.times=Float32Array.from(tr.times,t=>t-t0);clip.resetDuration();
const PERIOD=clip.duration,STANCE=.75,STRIDE=.14,SCALE=2.45,SPEED=STRIDE*SCALE/(PERIOD*STANCE);
const blobCanvas=document.createElement('canvas');blobCanvas.width=blobCanvas.height=128;const bg=blobCanvas.getContext('2d');const grd=bg.createRadialGradient(64,64,4,64,64,64);grd.addColorStop(0,'rgba(14,20,22,.42)');grd.addColorStop(1,'rgba(14,20,22,0)');bg.fillStyle=grd;bg.fillRect(0,0,128,128);const blobTex=new T.CanvasTexture(blobCanvas);blobTex.colorSpace=T.SRGBColorSpace;
function makeAnimal(scale,heading,mode){const root=new T.Group(),obj=clone(model);obj.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});obj.scale.setScalar(scale);root.add(obj);scene.add(root);const mixer=new T.AnimationMixer(obj);const action=mixer.clipAction(clip);action.play();const blob=new T.Mesh(new T.PlaneGeometry(5.0,2.6),new T.MeshBasicMaterial({map:blobTex,transparent:true,depthWrite:false,opacity:.34}));blob.rotation.x=-PI/2;scene.add(blob);return{root,obj,mixer,action,scale,heading,mode,blob}}
const herd=[makeAnimal(SCALE,0,'walk'),makeAnimal(2.22,-.25,'walk'),makeAnimal(2.05,.34,'walk'),makeAnimal(1.20,.1,'walk'),makeAnimal(2.10,-.6,'stand')];
function place(a,x,z,y,heading,phase,t,walking=true){
// The rig faces local -X (head/trunk sit at negative x). Zero heading therefore means
// "facing +X", so every animal must be spun by PI before it can walk along +X.
 a.root.position.set(x,y,z);a.obj.rotation.y=heading+PI;
 if(walking)a.mixer.setTime(t+phase*PERIOD);
 a.blob.position.set(x+.04,y+.004,z+.40*a.scale);a.blob.scale.setScalar(a.scale/SCALE);
}
// --- camera ------------------------------------------------------------------
const cam=new T.PerspectiveCamera(37,W/H,.04,420);const look=new T.Vector3(),pos=new T.Vector3();
const SHOTS=[{n:'dawn herd on the ridge',s:0,e:9},{n:'walking past the lens',s:9,e:18},{n:'trunk to the grass',s:18,e:27},{n:'calf behind the adult',s:27,e:36},{n:'crossing the shallow stream',s:36,e:45},{n:'snow squall',s:45,e:54},{n:'dusk on the plain',s:54,e:60}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
// Per-shot layout: positions and headings are authored, not simulated.
function layout(i,t){const a=herd;
 if(i===0){ // wide dawn: herd crests a low rise, moving right
  const u=(t-SHOTS[0].s)/9;
  place(a[0],-5+3.2*u,1.2,.30,0,.0,t);
  place(a[1],-11+3.0*u,4.2,.34,-.2,.31,t);
  place(a[2],-16.5+2.9*u,-.4,.28,.2,.62,t);
  place(a[3],-1.2+3.3*u,3.4,.32,.1,.45,t);
  place(a[4],10.5,9.0,.34,-.7,0,t,false);
  return {cam:{x:-2.2+1.1*u,y:2.35,z:20.5},look:{x:-3.6+1.6*u,y:1.5,z:1.0}}}
 if(i===1){ // side tracking close on the lead animal, feet in frame
  const u=(t-SHOTS[1].s)/9;const wx=-6+SPEED*t*1.0;
  place(a[0],wx,1.0,.02,0,.0,t);
  place(a[1],wx-7.5,2.6,.05,-.06,.31,t);place(a[2],wx-15.5,-.6,.02,.05,.62,t);
  place(a[3],wx-3.2,3.9,.04,.1,.45,t);place(a[4],wx+13,6.0,.03,-.7,0,t,false);
  return {cam:{x:wx+3.6,y:1.42,z:7.4},look:{x:wx+.4,y:1.18,z:.2}}}
 if(i===2){ // low, close: trunk down into a grass clump
  const u=(t-SHOTS[2].s)/9;const sway=.10*Math.sin(u*PI*1.2);
  place(a[0],-2.0+u*.55,-.55,.0,sway,.0,t,false);
  a[0].mixer.setTime(1.72+u*.35);a[0].obj.rotation.x=.035*smooth(u*1.4);
  place(a[1],-9.5,3.2,.02,-.2,.31,t);place(a[2],-16.5,-1.2,.02,.2,.62,t);
  place(a[3],4.2,2.6,.03,.2,.45,t);place(a[4],13,7,.03,-.7,0,t,false);
  return {cam:{x:.55,y:.78,z:2.2},look:{x:-1.95,y:.62,z:-.95}}}
 if(i===3){ // calf follows the adult, both cross frame left to right
  const u=(t-SHOTS[3].s)/9;const wx=-8+SPEED*t*1.35;
  place(a[3],wx+.4,2.35,.02,0,.2,t);
  place(a[0],wx-3.4,2.9,.02,0,.0,t);
  place(a[1],wx-10,4.6,.03,-.15,.31,t);place(a[2],wx-17,0.4,.02,.12,.62,t);
  place(a[4],wx+11,8.5,.03,-.6,0,t,false);
  return {cam:{x:wx+5.6,y:1.62,z:10.8},look:{x:wx-1.0,y:1.12,z:1.2}}}
 if(i===4){ // wading the channel: fixed low camera on the far bank, herd walks through
  const u=(t-SHOTS[4].s)/9;
  // The camera is static so the animals actually traverse frame; only a slow
  // lateral drift keeps the composition alive. Tracking them 1:1 made the shot
  // read as a still.
  place(a[0],-6.2+u*10.4,CH.z0+.5,-.07,0,.0,t);
  place(a[1],-11.0+u*10.2,CH.z0+.05,-.07,-.05,.31,t);
  place(a[3],-8.4+u*10.5,CH.z1-.1,-.05,.08,.45,t);
  place(a[2],-17.5+u*10.0,CH.z0+.9,-.05,.05,.62,t);
  place(a[4],-1.0+u*.8,CH.z1+6,.04,-.5,0,t,false);
  return {cam:{x:-1.1+u*.5,y:.52,z:CH.z0-9.5},look:{x:-1.9+u*1.5,y:.34,z:CH.z0+.1}}}
 if(i===5){ // squall: low camera, herd held 12-20 m out in the murk as silhouettes
  const u=(t-SHOTS[5].s)/9;
  // Weather has to be drawn with near-lens spindrift and distance haze: the
  // animals must stay far enough away to read as shapes, not clean grey models.
  place(a[0],-3.4-u*.45,-11.5,.02,.40,.0,t,false);
  place(a[1],-8.8-u*.35,-13.6,.02,.52,.31,t,false);
  place(a[3],-6.2-u*.30,-9.8,.02,.60,.45,t,false);
  place(a[2],-14.2-u*.25,-14.9,.02,.36,.62,t,false);
  place(a[4],-18.0,-17.6,.03,-.34,0,t,false);
  for(const q of a){q.mixer.setTime(1.9+q.scale)} // all standing still in the wind
  return {cam:{x:-1.9+u*.55,y:.46,z:3.4},look:{x:-6.4-u*.25,y:.72,z:-13.0}}}
 // dusk: wide again, herd small, big sky
 const u=(t-SHOTS[6].s)/6;
 place(a[0],-2.5+u*.6,2.0,.01,0,.0,t);place(a[1],-8.6+u*.6,4.4,.02,-.2,.31,t);
 place(a[2],-14.5+u*.6,-.8,.02,.2,.62,t);place(a[3],1.6+u*.6,3.2,.02,.1,.45,t);place(a[4],9,9,.03,-.7,0,t,false);
 return {cam:{x:1.8-u*.5,y:2.15,z:21-u*1.2},look:{x:-3.0,y:1.35,z:1.5}};
}
// Weather and palette per shot, cross-faded over 0.7 s so shots breathe rather than cut hard.
const LOOK=[{sky:.05,storm:0,fog:0xb9c6c8,fogFar:150,exp:1.04,sun:2.35,sunCol:0xffe2c2,hemi:1.95},
 {sky:.20,storm:0,fog:0xbcc7c6,fogFar:130,exp:1.04,sun:2.5,sunCol:0xfff0da,hemi:1.9},
 {sky:.35,storm:0,fog:0xc0cac7,fogFar:105,exp:1.05,sun:2.6,sunCol:0xfff2e0,hemi:1.95},
 {sky:.42,storm:.05,fog:0xbfc9c6,fogFar:120,exp:1.06,sun:2.55,sunCol:0xffefd8,hemi:1.9},
 {sky:.30,storm:.10,fog:0xb7c3c0,fogFar:95,exp:1.03,sun:2.0,sunCol:0xeae6dc,hemi:2.0},
 {sky:.45,storm:.95,fog:0x9faaab,fogFar:27,exp:.94,sun:.45,sunCol:0xcfd8dc,hemi:1.45},
 {sky:.95,storm:.12,fog:0x5c6675,fogFar:150,exp:1.02,sun:.55,sunCol:0xffbd86,hemi:.95}];
const cur={sky:.05,storm:0,fog:150};
let frame=0;
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;wind.value=t;seaClock.value=t;streamClock.value=t;
 const i=shotIndex(t),prev=Math.max(0,i-1);
 const lt=t-SHOTS[i].s,span=SHOTS[i].e-SHOTS[i].s;
 // ease into a shot's weather in its first 0.8 s
 const w=smooth(Math.min(1,lt/.8));
 const L=LOOK[i],P=LOOK[prev];
 const mixv=(k)=>lerp(P[k],L[k],w);
 uSky.value=mixv('sky');uStorm.value=mixv('storm');
 smoothFog(scene.fog,mixv('fog'),mixv('fogFar'));
 renderer.toneMappingExposure=mixv('exp');sun.intensity=mixv('sun');
 sun.color.setHex(L.sunCol);hemi.intensity=mixv('hemi');
 snowMat.opacity=.12+.62*mixv('storm');nearMat.opacity=.10+.72*mixv('storm');nearMat.size=.05+.055*mixv('storm');
 // dawn/dusk sun direction shifts slowly with the sky value
 const ang=lerp(-.55,2.55,uSky.value);sun.position.set(Math.cos(ang)*26,lerp(15,6.5,uSky.value),Math.sin(ang)*20+8);
 const L2=layout(i,t);pos.set(L2.cam.x,L2.cam.y,L2.cam.z);look.set(L2.look.x,L2.look.y,L2.look.z);
 // a whisper of handheld drift
 pos.x+=.010*Math.sin(t*.61);pos.y+=.007*Math.sin(t*.47+1.2);
 cam.position.copy(pos);cam.updateProjectionMatrix();cam.lookAt(look);nearSnow.position.copy(pos);
 g.clearRect(0,0,W,H);renderer.render(scene,cam);g.drawImage(renderer.domElement,0,0);
 // Grade: warm-cool split by time of day, gentle bloom near the sun, vignette, grain.
 const warm=i===0?.10:i===6?.16:.05;
 g.globalCompositeOperation='soft-light';g.fillStyle=`rgba(${i===6?'196,150,120':'150,178,196'},${warm+.10})`;g.fillRect(0,0,W,H);g.globalCompositeOperation='source-over';
 const bg2=g.createRadialGradient(W*.28,H*.42,10,W*.28,H*.42,W*.6);
 bg2.addColorStop(0,i===6?'rgba(255,186,130,.10)':'rgba(255,236,208,.07)');bg2.addColorStop(1,'rgba(0,0,0,0)');
 g.globalCompositeOperation='screen';g.fillStyle=bg2;g.fillRect(0,0,W,H);g.globalCompositeOperation='source-over';
 const vg=g.createRadialGradient(W*.5,H*.5,H*.30,W*.5,H*.5,H*.9);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(6,10,12,.36)');g.fillStyle=vg;g.fillRect(0,0,W,H);
 for(let k=0;k<1500;k++){const gx=(k*89+((frame*131)%877))%W,gy=(k*57+((frame*47)%563))%H;g.fillStyle=k%3?'rgba(255,255,255,.025)':'rgba(0,0,0,.04)';g.fillRect(gx,gy,1,1)}
 // Driven snow: the 3D point layers alone read as specks, so the squall is sold
 // with near-lens streaks and a veil drawn onto the composite.
 const st=uStorm.value;
 if(st>.02){
  g.fillStyle=`rgba(222,231,233,${.03+.06*st})`;g.fillRect(0,0,W,H);
  g.lineCap='round';
  // Gusts: a slow travelling envelope makes bands of denser snow instead of an
  // evenly stippled field. Flakes are drawn at a wind angle, not flat horizontal.
  const gust=(x)=>Math.max(0,Math.sin((x*.007)+frame*.03+1.1))**.6;
  for(let k=0;k<210;k++){
   const sp3=.9+((k*53)%17)*.13;
   const y=((k*97+((k*k*13)%H))%H);
   const gg=gust(k*61.7+y*.3);
   if(gg<.12)continue;
   const x=((k*241+y*1.7+frame*(7+k%11)*sp3)%(W+420))-210;
   const len=(7+(k%13)*4.6)*(.4+.9*st)*(1+gg*.7);
   g.strokeStyle='rgba(252,254,254,'+((.02+.11*st)*gg*(.5+.5*(k%3))).toFixed(3)+')';
   g.lineWidth=k%7?.8:1.5;
   g.beginPath();g.moveTo(x,y);g.lineTo(x+len*1.0,y+len*.30);g.stroke();
  }
 }
 g.fillStyle='rgba(240,244,240,.88)';g.shadowColor='rgba(8,14,16,.95)';g.shadowBlur=7;g.font='700 14px Manrope';g.textAlign='left';
 g.fillText('WRANGEL · ILLUSTRATIVE RECONSTRUCTION',30,690);g.shadowBlur=0;
 return{time:t,shot:i,shot_name:SHOTS[i].n,animals:5,triangles,historical_geography:false,storm:uStorm.value,speed:SPEED,snow:snowMat.opacity}}
function smoothFog(fog,color,far){fog.color.setHex(color);fog.near=Math.min(26,far*.22);fog.far=far}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;
window.__ready=true;draw(0);
