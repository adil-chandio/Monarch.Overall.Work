// Island through compressed seasons — illustrative 3D, not a reconstruction.
// Same third-party rig as the other scenes (see ../mammoth-rig/README.md).
// Geography, vegetation, animal count and weather are invented. No cut: one
// continuous camera move while winter thaws, summer passes and snow returns.
import * as T from 'three';
import {GLTFLoader} from '/GLTFLoader.js';
import {clone} from '/utils/SkeletonUtils.js';
const W=1280,H=720,PI=Math.PI,FPS=30;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
const scene=new T.Scene();scene.fog=new T.Fog(0xb8c8c7,30,150);
let seed=920441;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};
// Season state: winter -> thaw -> summer -> autumn -> winter, one uniform tree.
const uSky={value:0},uSnow={value:1},uGround={value:0},uSun={value:0};
const sky=new T.Mesh(new T.SphereGeometry(300,32,20),new T.ShaderMaterial({side:T.BackSide,depthWrite:false,uniforms:{uSky},vertexShader:`varying vec3 w;void main(){w=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*modelMatrix*vec4(position,1.);}`,fragmentShader:`uniform float uSky;varying vec3 w;void main(){float h=clamp(normalize(w).y,0.,1.);vec3 cold=mix(vec3(.74,.77,.74),vec3(.20,.36,.52),smoothstep(0.,.85,h));vec3 warm=mix(vec3(.83,.80,.71),vec3(.20,.43,.62),smoothstep(0.,.85,h));gl_FragColor=vec4(mix(cold,warm,uSky),1.);}`}));scene.add(sky);
const hemi=new T.HemisphereLight(0xd8e8ee,0x4a4b44,2.05);scene.add(hemi);
const sun=new T.DirectionalLight(0xfff0dc,2.35);sun.position.set(-26,21,9);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-18;sun.shadow.camera.right=18;sun.shadow.camera.top=18;sun.shadow.camera.bottom=-18;sun.shadow.camera.near=.5;sun.shadow.camera.far=90;sun.shadow.bias=-.0003;sun.shadow.normalBias=.004;scene.add(sun);
const snowCanvas=document.createElement('canvas');snowCanvas.width=snowCanvas.height=512;const sg=snowCanvas.getContext('2d');sg.fillStyle='#e2e7e1';sg.fillRect(0,0,512,512);for(let i=0;i<11000;i++){sg.fillStyle=`rgba(58,84,86,${.012+rand()*.035})`;sg.fillRect(rand()*512,rand()*512,1+rand()*6,1+rand()*2)}
const snowTex=new T.CanvasTexture(snowCanvas);snowTex.colorSpace=T.SRGBColorSpace;snowTex.wrapS=snowTex.wrapT=T.RepeatWrapping;snowTex.repeat.set(30,30);
const tundra=await new T.TextureLoader().loadAsync('/tundra.jpg');tundra.colorSpace=T.SRGBColorSpace;tundra.wrapS=tundra.wrapT=T.RepeatWrapping;tundra.repeat.set(30,30);
// Ground is real geometry. Snow amount is a shader-driven cover pattern that
// retreats into hollows and north-facing hollows first, then returns.
const groundMat=new T.MeshStandardMaterial({color:0xcfd6cd,map:tundra,roughness:1,vertexColors:true});
groundMat.onBeforeCompile=sh=>{groundMat.userData.sh=sh;sh.uniforms.uSnow=uSnow;sh.uniforms.uGround=uGround;sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 tP;').replace('#include <begin_vertex>','#include <begin_vertex>\ntP=position;');sh.fragmentShader=sh.fragmentShader.replace('#include <common>','#include <common>\nuniform float uSnow;uniform float uGround;varying vec3 tP;').replace('#include <map_fragment>',`#ifdef USE_MAP
float coverPattern=.5+.5*(sin(tP.x*.33+sin(tP.z*.21))*cos(tP.z*.29+tP.x*.07)*.7+sin(tP.x*.91-tP.z*.63)*.3);
float cover=smoothstep(coverPattern-.22,coverPattern+.10,uSnow);
vec4 soil=texture2D(map,vMapUv);
vec3 dry=mix(vec3(.35,.36,.24),vec3(.60,.53,.33),smoothstep(.2,.9,coverPattern));
vec3 bare=mix(dry,vec3(.34,.36,.28),uGround*.35);
float grain=.72+.5*dot(soil.rgb,vec3(.33));\ndiffuseColor.rgb=mix(bare,vec3(.92,.95,.94)*grain,cover*.95);
#endif`)};const ground=new T.Mesh(new T.PlaneGeometry(190,160,120,96),groundMat);
const gp=ground.geometry.attributes.position;const gcols=[];
const shore=x=>1.4*Math.sin(x*.11)+.8*Math.sin(x*.29+.7);
function terrain(x,z){const flat=smooth((Math.abs(z)-5)/9);const roll=flat*(.55*Math.sin(x*.13)*Math.cos(z*.1)+.32*Math.sin(x*.27+z*.17));return roll-.06-3.6*smooth((-z-4+shore(x))/10)}
for(let i=0;i<gp.count;i++){const x=gp.getX(i),z=gp.getZ(i);gp.setY(i,terrain(x,z));const n=.9+.1*Math.sin(x*.31+z*.12);gcols.push(n,n*.995,n*.96)}
ground.geometry.setAttribute('color',new T.Float32BufferAttribute(gcols,3));ground.geometry.computeVertexNormals();ground.rotation.x=0;ground.receiveShadow=true;scene.add(ground);
// Low island ridge behind the plain, with a snowline that follows the season.
const ridgeGeo=new T.PlaneGeometry(190,70,200,70);ridgeGeo.rotateX(-PI/2);const rp=ridgeGeo.attributes.position;const rcol=[];
for(let i=0;i<rp.count;i++){const x=rp.getX(i),z=rp.getZ(i);const depth=smooth((z+35)/20)*smooth((35-z)/13);const crest=3.2+2.4*Math.sin(x*.09+.4)+1.7*Math.sin(x*.21+1.9)+.9*Math.sin(x*.44-.6);const rough=.6*Math.sin(x*.6+z*.24)+.34*Math.cos(x*1.2-z*.33);const h=Math.max(0,depth*(crest+rough));rp.setY(i,h);const v=.84+Math.min(1,h/9)*.14;rcol.push(v*.97,v,v*.99)}
ridgeGeo.setAttribute('color',new T.Float32BufferAttribute(rcol,3));ridgeGeo.computeVertexNormals();
const ridgeMat=new T.MeshStandardMaterial({color:0x8ea3ac,vertexColors:true,roughness:1});const ridge=new T.Mesh(ridgeGeo,ridgeMat);ridge.position.set(0,-.4,-52);scene.add(ridge);
// Sea: shader waves; no physical shoreline or historic sea level is claimed.
const seaClock={value:0};const waterGeo=new T.PlaneGeometry(700,520,240,180);waterGeo.rotateX(-PI/2);
const waterMat=new T.ShaderMaterial({uniforms:{time:seaClock},vertexShader:`uniform float time;varying vec3 lp;varying float h;void main(){vec3 p=position;float w=sin(p.x*.29+p.z*.37+time*.7)*.06+sin(p.x*.63-p.z*.31+time*.5)*.03;w*=1.-smoothstep(60.,170.,340.-p.z);p.y+=w;lp=p;h=w;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,fragmentShader:`uniform float time;varying vec3 lp;varying float h;void main(){float s=sin(lp.x*1.1+sin(lp.z*.3+time*.12)+time*.4)*sin(lp.z*.8+lp.x*.2-time*.3);float glint=pow(max(0.,s),18.);vec3 base=mix(vec3(.075,.15,.19),vec3(.20,.33,.38),clamp((h+.09)*4.,0.,1.));base+=glint*.22;float haze=smoothstep(25.,150.,340.-lp.z);base=mix(base,vec3(.46,.55,.56),haze*.85);gl_FragColor=vec4(base,1.);}`});
const sea=new T.Mesh(waterGeo,waterMat);sea.position.set(0,-.62,-300);scene.add(sea);
// Vegetation density changes with the season on the same instanced tufts.
const verts=[];for(let j=0;j<5;j++){const a=j*PI/5,dx=Math.cos(a),dz=Math.sin(a),bend=(j%2?.12:-.12),ht=.32+j*.04;const at=(v,side)=>[dx*side*.023*(1-v)+bend*v*v,ht*v,dz*side*.023*(1-v)+bend*.3*v*v];for(let k=0;k<3;k++){const u=k/3,v=(k+1)/3;verts.push(...at(u,-1),...at(u,1),...at(v,-1),...at(u,1),...at(v,1),...at(v,-1))}}
const tuftGeo=new T.BufferGeometry();tuftGeo.setAttribute('position',new T.Float32BufferAttribute(verts,3));tuftGeo.computeVertexNormals();
const wind={value:0};const tuftMat=new T.MeshStandardMaterial({color:0xb9ae8a,roughness:1,side:T.DoubleSide});
tuftMat.onBeforeCompile=sh=>{sh.uniforms.wind={value:wind};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nuniform float wind;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x+=sin(wind*1.25+instanceMatrix[3].x*.55)*position.y*position.y*.16;')};
const tufts=new T.InstancedMesh(tuftGeo,tuftMat,2600);const dm=new T.Object3D();
for(let i=0;i<2600;i++){const x=rand()*100-50,z=(rand()<.55?1:-1)*(2.4+rand()*30);dm.position.set(x,terrain(x,z)+.01,z);dm.rotation.set(0,rand()*PI,.07*(rand()-.5));const s=.32+rand()*.8;dm.scale.setScalar(s);dm.updateMatrix();tufts.setMatrixAt(i,dm.matrix);tufts.setColorAt(i,new T.Color().setHSL(.11+rand()*.05,.18+rand()*.14,.3+rand()*.18))}scene.add(tufts);
const stoneMat=new T.MeshStandardMaterial({color:0x6c7268,roughness:1});for(let i=0;i<64;i++){const x=rand()*66-33,z=-2.6-rand()*2.8+shore(x),size=.05+rand()*.22;const o=new T.Mesh(new T.DodecahedronGeometry(1,1),stoneMat);o.position.set(x,terrain(x,z)+size*.2,z);o.scale.set(size*(.7+rand()),size*(.34+rand()*.3),size*(.7+rand()));o.rotation.set(rand()*.4,rand()*PI,rand()*.3);o.castShadow=true;scene.add(o)}
// Two low foreground boulders plus tufts give a near plane; they sit below the
// lens axis so they do not block the herd. Snow is a thin, offset cap, not a disc.
const boulderMat=new T.MeshStandardMaterial({color:0x53595a,roughness:.95});
const boulders=[[-8.2,6.4,1.15],[6.4,7.1,.95]];
for(const [bx,bz,bs] of boulders){const o=new T.Mesh(new T.IcosahedronGeometry(1,2),boulderMat);o.position.set(bx,terrain(bx,bz)+bs*.18,bz);o.scale.set(bs*1.25,bs*.40,bs*.85);o.rotation.set(.12,rand()*PI,.09);o.castShadow=true;o.receiveShadow=true;scene.add(o);
 const cap=new T.Mesh(new T.IcosahedronGeometry(1,1),new T.MeshStandardMaterial({color:0xcfdad8,roughness:1}));cap.position.set(bx-bs*.12,terrain(bx,bz)+bs*.36,bz+bs*.05);cap.scale.set(bs*.92,bs*.13,bs*.62);cap.rotation.y=o.rotation.y;cap.receiveShadow=true;scene.add(cap)}
const nearTuftMat=new T.MeshStandardMaterial({color:0x9d9578,roughness:1,side:T.DoubleSide});
for(let i=0;i<26;i++){const x=-9+rand()*3.2,z=5.4+rand()*2.4;const o=new T.Mesh(tuftGeo,nearTuftMat);o.position.set(x,terrain(x,z),z);o.scale.setScalar(.9+rand()*.9);o.rotation.y=rand()*PI;o.castShadow=true;scene.add(o)}
const spindriftGeo=new T.BufferGeometry(),spp=new Float32Array(460*3);for(let i=0;i<460;i++){spp[3*i]=(rand()-.5)*44;spp[3*i+1]=rand()*9;spp[3*i+2]=(rand()-.5)*28}spindriftGeo.setAttribute('position',new T.BufferAttribute(spp,3));
const spindriftMat=new T.PointsMaterial({color:0xe8f1f0,size:.045,transparent:true,opacity:.5,depthWrite:false});
spindriftMat.onBeforeCompile=sh=>{sh.uniforms.wind={value:wind};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nuniform float wind;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x+=mod(position.x+wind*1.1+220.,44.)-22.;transformed.y=mod(position.y-wind*.12+400.,9.);')};const spindrift=new T.Points(spindriftGeo,spindriftMat);scene.add(spindrift);
const asset=await new GLTFLoader().loadAsync('/mammoth.glb');const model=asset.scene;let triangles=0;model.traverse(o=>{if(o.isMesh)triangles+=o.geometry.index?o.geometry.index.count/3:o.geometry.attributes.position.count/3});
const clip=asset.animations.find(a=>a.name==='WalkInPlace_Experimental');if(!clip)throw Error('walk clip missing');
const t0=Math.min(...clip.tracks.map(t=>t.times[0]));for(const tr of clip.tracks)tr.times=Float32Array.from(tr.times,t=>t-t0);clip.resetDuration();
const PERIOD=clip.duration,STANCE=.75,STRIDE=.14,SCALE=2.45,SPEED=STRIDE*SCALE/(PERIOD*STANCE);
const blobCanvas=document.createElement('canvas');blobCanvas.width=blobCanvas.height=128;const bg=blobCanvas.getContext('2d');const grad=bg.createRadialGradient(64,64,4,64,64,64);grad.addColorStop(0,'rgba(16,26,28,.46)');grad.addColorStop(1,'rgba(16,26,28,0)');bg.fillStyle=grad;bg.fillRect(0,0,128,128);const blobTex=new T.CanvasTexture(blobCanvas);blobTex.colorSpace=T.SRGBColorSpace;
// mode: 'walk' uses the cycle; 'stand' freezes a stance phase; 'graze' tips the head down.
function makeAnimal(x,z,phase,scale,heading,mode){const root=new T.Group(),obj=clone(model);const baseHeading=heading;obj.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});obj.scale.setScalar(scale);obj.rotation.y=heading;root.add(obj);scene.add(root);const mixer=new T.AnimationMixer(obj);const action=mixer.clipAction(clip);action.play();if(mode==='stand'){action.paused=true;mixer.setTime(phase*PERIOD*.75)}const blob=new T.Mesh(new T.PlaneGeometry(5.6,3.1),new T.MeshBasicMaterial({map:blobTex,transparent:true,depthWrite:false,opacity:.55}));blob.rotation.x=-PI/2;scene.add(blob);return{root,obj,mixer,action,x,z,phase,scale,mode,blob,y:terrain(x,z)+.028}}
// Five animals at different scales, headings and behaviours; still the same mesh.
const herd=[makeAnimal(2.2,1.0,0,SCALE,0,'walk'),makeAnimal(-15.5,6.8,.62,2.2,-.42,'stand'),makeAnimal(18.5,9.4,.18,2.28,.2,'graze')];
const cam=new T.PerspectiveCamera(37,W/H,.05,340);const look=new T.Vector3(),pos=new T.Vector3();
// Four framing keys for one continuous move; each keeps the herd inside frame
// while the light and ground change. Interpolated with smoothstep, not cuts.
const keys=[
 {p:[-9.5,1.9,13.5],l:[1.4,1.25,.2]},
 {p:[-3.6,2.25,11.0],l:[2.6,1.15,-.6]},
 {p:[4.2,2.55,8.4],l:[.9,1.0,-1.6]},
 {p:[9.6,4.0,14.5],l:[.2,1.0,-2.2]}];
const ease=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};
function cameraAt(t){const ft=Math.min(3,Math.max(0,t/11.5)),i=Math.min(2,Math.floor(ft)),k=ease(ft-i);
 pos.set(T.MathUtils.lerp(keys[i].p[0],keys[i+1].p[0],k),T.MathUtils.lerp(keys[i].p[1],keys[i+1].p[1],k),T.MathUtils.lerp(keys[i].p[2],keys[i+1].p[2],k));
 look.set(T.MathUtils.lerp(keys[i].l[0],keys[i+1].l[0],k),T.MathUtils.lerp(keys[i].l[1],keys[i+1].l[1],k),T.MathUtils.lerp(keys[i].l[2],keys[i+1].l[2],k));
 cam.position.copy(pos);cam.updateProjectionMatrix();cam.lookAt(look);return cam}
// Season curve: winter at the start, thaw, brief summer, autumn, snow returns.
function seasonAt(t){
 const thaw=smooth((t-4)/9),grow=smooth((t-13)/6),autumn=smooth((t-25)/6),winter=smooth((t-30.5)/5.5);
 const bare=thaw*(1-autumn);
 const snow=1-thaw*(1-.12)+winter*thaw*(1-.12);
 return{thaw,grow,autumn,winter,bare,snow}}
let frame=0;
function draw(t){t=Math.max(0,Math.min(36,t));frame++;const s=seasonAt(t);wind.value=t;seaClock.value=t;
 uSky.value=Math.min(1,s.bare*.85+s.grow*.15);uSnow.value=Math.min(1,s.snow);uGround.value=Math.min(1,s.grow*.5+s.autumn*.6);
 hemi.color.setHSL(.55,.16,.78-.06*s.winter);hemi.groundColor.setHSL(.11,.1,.22+.05*s.bare);hemi.intensity=2.0-.25*s.winter;
 sun.intensity=2.35-.5*s.winter;sun.color.setHSL(.10,.28,.86-.05*s.winter);
 scene.fog.color.setHSL(.52,.1,.62-.05*s.winter);
 tuftMat.color.setHSL(.11,.14,.62-.1*s.grow-.16*s.winter);
 // Herd: the walking lead crosses the strip, then slows to browse; others vary.
 for(const a of herd){const w=a.mode==='walk'?Math.min(t,27):0;a.root.position.set(a.x-(a.mode==='walk'?SPEED*.55*w:0),a.y,a.z-(a.mode==='walk'?.16*SPEED*w*.2:0));if(a.mode==='walk')a.mixer.setTime(t*1.02+a.phase*PERIOD);else a.mixer.setTime(a.phase*PERIOD*.8);
  if(a.mode==='graze'){a.obj.rotation.x=Math.sin(t*.7+a.phase)*.012;a.obj.rotation.z=-.055+.02*Math.sin(t*.5)}
  if(a.mode==='stand')a.obj.rotation.y=a.baseHeading+.05*Math.sin(t*.35+a.phase);
  a.blob.position.set(a.root.position.x+.05,a.y+.004,a.root.position.z+.42*a.scale);a.blob.scale.setScalar(a.scale/SCALE)}
 spindriftMat.opacity=.18+.42*(1-s.snow*.4)*(1-s.bare*.6)+.16*s.winter;
 const c=cameraAt(t);g.clearRect(0,0,W,H);renderer.render(scene,c);g.drawImage(renderer.domElement,0,0);
 // Warm highlights / cool shadows grade and a soft vignette; no letterbox or plate.
 g.globalCompositeOperation='soft-light';g.fillStyle=s.bare>.5?'rgba(196,150,96,.16)':'rgba(120,160,180,.14)';g.fillRect(0,0,W,H);
 g.globalCompositeOperation='source-over';const vg=g.createRadialGradient(W*.5,H*.46,H*.30,W*.5,H*.5,H*.86);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(4,10,12,.42)');g.fillStyle=vg;g.fillRect(0,0,W,H);
 // Static-seeded grain keeps the render from looking like flat vector art.
 for(let i=0;i<1800;i++){const gx=(i*97+((frame*137)%911))%W,gy=(i*61+((frame*53)%577))%H;g.fillStyle=i%3?'rgba(255,255,255,.035)':'rgba(0,0,0,.045)';g.fillRect(gx,gy,1,1)}
 // Lower third carries a persistent, quiet disclosure rather than a claim of place.
 const a=.86;g.fillStyle=`rgba(238,244,241,${a})`;g.shadowColor='rgba(12,26,30,.9)';g.shadowBlur=7;g.font='700 15px Manrope';g.textAlign='left';
 g.fillText('WRANGEL · SEASONS COMPRESSED · ILLUSTRATIVE',30,690);g.shadowBlur=0;
 return{time:t,season:s,animals:herd.length,triangles,historical_geography:false,behaviour_observed:false}}
window.__seasonProbe=t=>{const st=draw(t);return{time:t,snow:uSnow.value,bare:st.season.bare,winter:st.season.winter,sky:uSky.value}}
// Sole probes reuse the documented foot sample positions on the lead animal.
const skinned=[];herd[0].obj.traverse(o=>{if(o.isSkinnedMesh)skinned.push(o)});
const foot=[[-.206,-.325],[-.203,-.544],[.498,-.213],[.427,-.441]],probes=foot.map(()=>[]);
for(const mesh of skinned){const p=mesh.geometry.attributes.position;for(let v=0;v<p.count;v++){const x=p.getX(v),y=p.getY(v),z=p.getZ(v);if(y>-.03)continue;let k=0,best=Infinity;for(let i=0;i<4;i++){const d=(x-foot[i][0])**2+(z+foot[i][1])**2;if(d<best){best=d;k=i}}if(best<.0012)probes[k].push({mesh,index:v,base:new T.Vector3(x,y,z)})}}
window.__soleProbe=t=>{draw(t);scene.updateMatrixWorld(true);return probes.map(pts=>{const o=new T.Vector3();let minY=Infinity,maxY=-Infinity;for(const{mesh,index,base}of pts){const p=base.clone();mesh.applyBoneTransform(index,p);mesh.localToWorld(p);o.add(p);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y)}if(pts.length)o.multiplyScalar(1/pts.length);return{count:pts.length,xyz:o.toArray(),minY,maxY}})};
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__ready=true;draw(0);
