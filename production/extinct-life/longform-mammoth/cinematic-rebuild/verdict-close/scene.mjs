// Verdict close — the last argument over the island (734-759 s).
//
// The assembled film ended with 107 s of printed plate, then two shots of animals. The
// ledger is the right form for the film's *enumeration* of what is supported, plausible
// and unestablished — but the last twenty-six seconds are not an enumeration, they are
// the argument, and an argument belongs over a place, not a table.
//
// So the ledger now ends at 734 s, and this section carries "a possibility is not a
// verdict" and "these categories do not have to compete" as restrained lower-thirds over
// native picture. The film finishes on the island it has been talking about.
//
// Illustrative only: invented terrain, weather, herd size and camera moves. The animals
// are the same third-party rig (../mammoth-rig/README.md), rights unresolved.
import * as T from 'three';
import {GLTFLoader} from '/GLTFLoader.js';
import {clone} from '/utils/SkeletonUtils.js';
const W=1280,H=720,PI=Math.PI,FPS=30,DURATION=25;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);
renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.02;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
const scene=new T.Scene();scene.fog=new T.Fog(0xb9c2bd,30,170);
let seed=4410277;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};const S=smooth;const lerp=(a,b,u)=>a+(b-a)*u;
// --- sky ----------------------------------------------------------------------
const uSky={value:0};
const sky=new T.Mesh(new T.SphereGeometry(300,36,20),new T.ShaderMaterial({side:T.BackSide,depthWrite:false,uniforms:{uSky},vertexShader:`varying vec3 w;void main(){w=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*modelMatrix*vec4(position,1.);}`,fragmentShader:`uniform float uSky;varying vec3 w;void main(){vec3 d=normalize(w);float h=clamp(d.y,0.,1.);
vec3 low=mix(vec3(.80,.79,.74),vec3(.55,.63,.68),smoothstep(0.,.55,h));
vec3 high=mix(vec3(.44,.56,.66),vec3(.22,.36,.52),smoothstep(.05,.95,h));
vec3 c=mix(low,high,smoothstep(.10,.80,uSky));
c=mix(c,vec3(.88,.85,.78),smoothstep(.35,0.,h)*.25);
gl_FragColor=vec4(c,1.);}`}));scene.add(sky);
const sun=new T.DirectionalLight(0xffe9cf,2.18);sun.position.set(-30,13,16);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-34;sun.shadow.camera.right=34;sun.shadow.camera.top=34;sun.shadow.camera.bottom=-34;sun.shadow.camera.near=.5;sun.shadow.camera.far=130;sun.shadow.bias=-.0004;sun.shadow.normalBias=.005;scene.add(sun);
const hemi=new T.HemisphereLight(0xd3e3ea,0x6a6252,1.85);scene.add(hemi);
const fill=new T.DirectionalLight(0xdfeaf0,.36);fill.position.set(22,10,28);scene.add(fill);
// --- ground -------------------------------------------------------------------
const snowCanvas=document.createElement('canvas');snowCanvas.width=snowCanvas.height=512;const sg=snowCanvas.getContext('2d');sg.fillStyle='#e6e9e2';sg.fillRect(0,0,512,512);
for(let i=0;i<13000;i++){sg.fillStyle=`rgba(70,88,84,${.010+rand()*.034})`;sg.fillRect(rand()*512,rand()*512,1+rand()*7,1+rand()*2)}
const snowTex=new T.CanvasTexture(snowCanvas);snowTex.colorSpace=T.SRGBColorSpace;snowTex.wrapS=snowTex.wrapT=T.RepeatWrapping;snowTex.repeat.set(30,30);
const tundra=await new T.TextureLoader().loadAsync('/tundra.jpg');tundra.colorSpace=T.SRGBColorSpace;tundra.wrapS=tundra.wrapT=T.RepeatWrapping;tundra.repeat.set(24,24);
const groundMat=new T.MeshStandardMaterial({color:0xdbe0d8,map:tundra,roughness:1});
groundMat.onBeforeCompile=sh=>{sh.uniforms.snowMap={value:snowTex};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 tP;').replace('#include <begin_vertex>','#include <begin_vertex>\ntP=position;');
 sh.fragmentShader=sh.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 tP;uniform sampler2D snowMap;').replace('#include <map_fragment>','#ifdef USE_MAP\nfloat lp=.5+.5*(sin(tP.x*.15+sin(tP.z*.11))*cos(tP.z*.21+tP.x*.05)*.72+sin(tP.x*.63-tP.z*.47)*.28);\nfloat cover=smoothstep(.26,.58,lp);\nvec4 soil=texture2D(map,vMapUv),snow=texture2D(snowMap,vMapUv);\nvec3 bare=mix(vec3(.40,.39,.31),vec3(.60,.55,.40),lp);\ndiffuseColor.rgb=mix(bare,snow.rgb*.99,cover*.93);\n#endif')};
// Deliberately low relief so the mass of the sky dominates the frame.
function terrain(x,z){const flat=smooth((Math.abs(z)-6)/16);return flat*(.30*Math.sin(x*.085)*Math.cos(z*.07)+.16*Math.sin(x*.21+z*.13))-.05}
const groundGeo=new T.PlaneGeometry(260,190,140,110);groundGeo.rotateX(-PI/2);const gp=groundGeo.attributes.position;
for(let i=0;i<gp.count;i++)gp.setY(i,terrain(gp.getX(i),gp.getZ(i)));
groundGeo.computeVertexNormals();const ground=new T.Mesh(groundGeo,groundMat);ground.receiveShadow=true;scene.add(ground);
const ridgeGeo=new T.PlaneGeometry(260,80,150,50);ridgeGeo.rotateX(-PI/2);const rp=ridgeGeo.attributes.position;
for(let i=0;i<rp.count;i++){const x=rp.getX(i),z=rp.getZ(i);const dep=smooth((z+42)/20)*smooth((40-z)/16);const crest=1.9+1.05*Math.sin(x*.052+.8)+.72*Math.sin(x*.118+2.1)+.34*Math.sin(x*.27);rp.setY(i,Math.max(0,dep*crest))}
ridgeGeo.computeVertexNormals();const ridge=new T.Mesh(ridgeGeo,new T.MeshStandardMaterial({color:0x93a3aa,roughness:1}));ridge.position.set(0,-.7,-70);scene.add(ridge);
// --- vegetation and stones ----------------------------------------------------
const verts=[];for(let j=0;j<5;j++){const a=j*PI/5,dx=Math.cos(a),dz=Math.sin(a),bend=(j%2?.12:-.12),ht=.30+j*.04;const at=(v,side)=>[dx*side*.021*(1-v)+bend*v*v,ht*v,dz*side*.021*(1-v)+bend*.3*v*v];for(let k=0;k<3;k++){const u=k/3,v=(k+1)/3;verts.push(...at(u,-1),...at(u,1),...at(v,-1),...at(u,1),...at(v,1),...at(v,-1))}}
const tuftGeo=new T.BufferGeometry();tuftGeo.setAttribute('position',new T.Float32BufferAttribute(verts,3));tuftGeo.computeVertexNormals();
const wind={value:0};const tuftMat=new T.MeshStandardMaterial({color:0xb2a782,roughness:1,side:T.DoubleSide});
tuftMat.onBeforeCompile=sh=>{sh.uniforms.wind={value:wind};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nuniform float wind;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x+=sin(wind*.92+instanceMatrix[3].x*.42)*position.y*position.y*(.10+step(3.,instanceMatrix[3].z)*.05);')};
const tufts=new T.InstancedMesh(tuftGeo,tuftMat,5200);const dm=new T.Object3D();
for(let i=0;i<5200;i++){const x=rand()*150-75,z=rand()*86-38;dm.position.set(x,terrain(x,z)+.01,z);dm.rotation.set(0,rand()*PI,.06*(rand()-.5));dm.scale.setScalar(.26+rand()*.72);dm.updateMatrix();tufts.setMatrixAt(i,dm.matrix);tufts.setColorAt(i,new T.Color().setHSL(.11,.13,.27+rand()*.17))}scene.add(tufts);
const stoneMat=new T.MeshStandardMaterial({color:0x5f6661,roughness:1});
for(let i=0;i<70;i++){const x=rand()*90-45,z=rand()*54-26;const r=.04+rand()*.20;const o=new T.Mesh(new T.DodecahedronGeometry(1,1),stoneMat);o.position.set(x,terrain(x,z)+r*.24,z);o.scale.set(r,r*(.28+rand()*.32),r*(.7+rand()*.5));o.rotation.set(rand()*.35,rand()*PI,rand()*.28);o.castShadow=true;o.receiveShadow=true;scene.add(o)}
// --- drifting snow ------------------------------------------------------------
const snowGeo=new T.BufferGeometry();const SPN=900;const sp=new Float32Array(SPN*3);
for(let i=0;i<SPN;i++){sp[3*i]=rand()*80-40;sp[3*i+1]=rand()*9;sp[3*i+2]=rand()*56-28}
snowGeo.setAttribute('position',new T.BufferAttribute(sp,3));
const snowMat=new T.PointsMaterial({color:0xf0f6f6,size:.05,transparent:true,opacity:.30,depthWrite:false});
snowMat.onBeforeCompile=sh=>{sh.uniforms.wind={value:wind};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nuniform float wind;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x=mod(position.x+wind*.85+40.,80.)-40.;transformed.y=mod(position.y-wind*.10+800.,9.);transformed.z+=sin(wind*.4+position.x*.26)*1.1;')};
scene.add(new T.Points(snowGeo,snowMat));
// --- animals ------------------------------------------------------------------
const asset=await new GLTFLoader().loadAsync('/mammoth.glb');const model=asset.scene;let triangles=0;model.traverse(o=>{if(o.isMesh)triangles+=o.geometry.index?o.geometry.index.count/3:o.geometry.attributes.position.count/3});
const clip=asset.animations.find(a=>a.name==='WalkInPlace_Experimental');if(!clip)throw Error('walk clip missing');
const t0=Math.min(...clip.tracks.map(t=>t.times[0]));for(const tr of clip.tracks)tr.times=Float32Array.from(tr.times,t=>t-t0);clip.resetDuration();
const PERIOD=clip.duration,STANCE=.75,STRIDE=.14,SCALE=2.45,SPEED=STRIDE*SCALE/(PERIOD*STANCE);
const blobCanvas=document.createElement('canvas');blobCanvas.width=blobCanvas.height=128;const bg=blobCanvas.getContext('2d');const grd=bg.createRadialGradient(64,64,4,64,64,64);grd.addColorStop(0,'rgba(14,20,22,.38)');grd.addColorStop(1,'rgba(14,20,22,0)');bg.fillStyle=grd;bg.fillRect(0,0,128,128);const blobTex=new T.CanvasTexture(blobCanvas);blobTex.colorSpace=T.SRGBColorSpace;
function makeAnimal(scale){const root=new T.Group(),obj=clone(model);obj.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});obj.scale.setScalar(scale);root.add(obj);scene.add(root);
 const mixer=new T.AnimationMixer(obj);const action=mixer.clipAction(clip);action.play();
 const blob=new T.Mesh(new T.PlaneGeometry(5.0,2.6),new T.MeshBasicMaterial({map:blobTex,transparent:true,depthWrite:false,opacity:.30}));blob.rotation.x=-PI/2;scene.add(blob);
 return{root,obj,mixer,scale,blob}}
const herd=[makeAnimal(SCALE),makeAnimal(2.20),makeAnimal(2.06),makeAnimal(1.18)];
function place(a,x,z,y,heading,phase,t){a.root.position.set(x,y,z);a.obj.rotation.y=heading+PI;/* rig faces -X */
 a.mixer.setTime(t+phase*PERIOD);
 a.blob.position.set(x+.04,y+.004,z+.40*a.scale);a.blob.scale.setScalar(a.scale/SCALE);}
// --- camera -------------------------------------------------------------------
const cam=new T.PerspectiveCamera(34,W/H,.05,460);const look=new T.Vector3(),pos=new T.Vector3();
const SHOTS=[{n:'the herd, still',s:0,e:13},{n:'settle and hold',s:13,e:25}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
// Two very slow moves, almost static: this section is an argument, not a spectacle.
function layout(i,t){const a=herd;
 // Two moves only, and both nearly static: this is the film's last image, so it should
 // settle rather than travel. The herd never fills the frame and is never counted.
 if(i===0){const u=t/13;
  place(a[0],-10+u*.8,-9,.02,0,.0,t);place(a[1],-18+u*.75,-5,.02,-.1,.31,t);place(a[2],-25+u*.7,-1,.02,.12,.62,t);place(a[3],-14+u*.75,-12.5,.03,.08,.45,t);
  return{cam:{x:4.0-u*.5,y:1.30,z:24.5-u*1.0},look:{x:-9.0,y:1.10,z:-5.0}}}
 const u=(t-13)/12;
 place(a[0],-11+u*.5,-9.5,.02,0,.0,t);place(a[1],-19+u*.45,-5.5,.02,-.1,.31,t);place(a[2],-26+u*.4,-1.5,.02,.12,.62,t);place(a[3],-15+u*.45,-13,.03,.08,.45,t);
 return{cam:{x:6.6-u*.4,y:1.62,z:27.5},look:{x:-11.0,y:1.26,z:-6.4}};
}
// Late light: the film's one warm beat, kept restrained so it reads as evening rather
// than as a conclusion the evidence does not support.
const LOOK=[{sky:.52,fog:0xb4bcb6,fogFar:176,exp:1.01,sun:2.02,hemi:1.78},
 {sky:.72,fog:0xaba8a0,fogFar:194,exp:1.00,sun:1.86,hemi:1.70}];
let frame=0;
function smoothFog(fog,color,far){fog.color.setHex(color);fog.near=Math.min(34,far*.24);fog.far=far}
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;wind.value=t;
 const i=shotIndex(t),prev=Math.max(0,i-1),lt=t-SHOTS[i].s,w=smooth(Math.min(1,lt/1.1));
 const L=LOOK[i],P=LOOK[prev],mixv=k=>lerp(P[k],L[k],w);
 uSky.value=mixv('sky');smoothFog(scene.fog,mixv('fog'),mixv('fogFar'));
 renderer.toneMappingExposure=mixv('exp');sun.intensity=mixv('sun');hemi.intensity=mixv('hemi');
 snowMat.opacity=.18+.16*mixv('sky');
 const ang=lerp(-.62,.55,uSky.value);sun.position.set(Math.cos(ang)*30,lerp(12,7.5,uSky.value),Math.sin(ang)*24+12);
 const L2=layout(i,t);pos.set(L2.cam.x,L2.cam.y,L2.cam.z);look.set(L2.look.x,L2.look.y,L2.look.z);
 pos.x+=.006*Math.sin(t*.41);pos.y+=.005*Math.sin(t*.33+.9);
 cam.position.copy(pos);cam.updateProjectionMatrix();cam.lookAt(look);
 g.clearRect(0,0,W,H);renderer.render(scene,cam);g.drawImage(renderer.domElement,0,0);
 // Grade: cool shadow, warm horizon, restrained vignette; the sky should carry weight.
 g.globalCompositeOperation='soft-light';g.fillStyle='rgba(154,176,186,.11)';g.fillRect(0,0,W,H);g.globalCompositeOperation='source-over';
 const hz=g.createLinearGradient(0,0,0,H*.62);hz.addColorStop(0,'rgba(255,236,214,.07)');hz.addColorStop(1,'rgba(0,0,0,0)');
 g.globalCompositeOperation='screen';g.fillStyle=hz;g.fillRect(0,0,W,H*.62);g.globalCompositeOperation='source-over';
 const vg=g.createRadialGradient(W*.5,H*.52,H*.36,W*.5,H*.5,H*.95);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(6,10,12,.30)');g.fillStyle=vg;g.fillRect(0,0,W,H);
 for(let k=0;k<1500;k++){const gx=(k*89+((frame*131)%877))%W,gy=(k*57+((frame*47)%563))%H;g.fillStyle=k%3?'rgba(255,255,255,.022)':'rgba(0,0,0,.034)';g.fillRect(gx,gy,1,1)}
 g.fillStyle='rgba(240,244,240,.85)';g.shadowColor='rgba(8,14,16,.95)';g.shadowBlur=7;g.font='700 14px Manrope';g.textAlign='left';
 g.fillText('WRANGEL · ILLUSTRATIVE RECONSTRUCTION',30,690);g.shadowBlur=0;
 // Lower-thirds: the two closing statements only, and nothing else. They carry no
 // numbers; the enumeration they qualify is left back on the plate at 689-733 s.
  // Timed to the narration, not to a timer: "A possibility is not a verdict" is spoken at
 // 736.6-740.1 (local 2.6-6.1) and "These categories do not have to compete" at
 // 749.1-751.5 (local 15.1-17.5).
 const L1=S((t-1.9)/1.2)*(1-S((t-7.2)/1.1));
 if(L1>0){
  // A soft scrim from the lower-left, not a box: a hard panel over this picture reads as
  // a slide laid on top of it.
  const gr=g.createLinearGradient(0,720,0,440);gr.addColorStop(0,'rgba(12,16,18,.60)');gr.addColorStop(1,'rgba(12,16,18,0)');
  g.save();g.globalAlpha=L1;g.fillStyle=gr;g.fillRect(0,440,W,280);g.restore();
  g.save();g.globalAlpha=L1;g.fillStyle='rgba(248,246,240,.95)';
  g.font='700 25px Manrope';g.textAlign='left';g.fillText('A POSSIBILITY IS NOT A VERDICT',114,598);g.restore();
 }
 const LT2=S((t-14.5)/1.3);
 if(LT2>0){
  const gr2=g.createLinearGradient(0,720,0,440);gr2.addColorStop(0,'rgba(12,16,18,.60)');gr2.addColorStop(1,'rgba(12,16,18,0)');
  g.save();g.globalAlpha=LT2;g.fillStyle=gr2;g.fillRect(0,440,W,280);g.restore();
  g.save();g.globalAlpha=LT2;g.fillStyle='rgba(248,246,240,.95)';
  g.font='700 25px Manrope';g.textAlign='left';g.fillText('THESE CATEGORIES DO NOT HAVE TO COMPETE',114,598);g.restore();
 }
 return{time:t,shot:i,shot_name:SHOTS[i].n,animals:4,triangles,historical_geography:false,sky:uSky.value,fog_far:scene.fog.far,claimMade:false,lowerThird:L1>0.5?1:(LT2>0.5?2:0)}}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;window.__ready=true;draw(0);
