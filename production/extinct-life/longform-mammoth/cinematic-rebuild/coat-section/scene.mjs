// Coat section — five illustrative shots under the FOXQ1/coat passage (250-284 s).
// Everything here is authored: terrain, weather, herd size and animal positions are
// invented; the fur close-up is a texture, not a specimen or a micrograph.
// Not a reconstruction of Wrangel. Third-party rig; see ../mammoth-rig/README.md.
// The on-screen text is a disclosure line only; no dates or place claims.
import * as T from 'three';
import {GLTFLoader} from '/GLTFLoader.js';
import {clone} from '/utils/SkeletonUtils.js';
const W=1280,H=720,PI=Math.PI,FPS=30,DURATION=34;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.04;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
const scene=new T.Scene();scene.fog=new T.Fog(0xa8b8bd,26,140);
let seed=773311;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};const lerp=(a,b,u)=>a+(b-a)*u;
// --- sky and light -----------------------------------------------------------
const uSky={value:0},uStorm={value:0};
const sky=new T.Mesh(new T.SphereGeometry(250,36,20),new T.ShaderMaterial({side:T.BackSide,depthWrite:false,uniforms:{uSky,uStorm},vertexShader:`varying vec3 w;void main(){w=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*modelMatrix*vec4(position,1.);}`,fragmentShader:`uniform float uSky;uniform float uStorm;varying vec3 w;void main(){vec3 d=normalize(w);float h=clamp(d.y,0.,1.);vec3 low=mix(vec3(.72,.78,.80),vec3(.30,.42,.50),smoothstep(0.,.75,h));vec3 high=mix(vec3(.55,.66,.72),vec3(.20,.34,.48),smoothstep(0.,.9,h));vec3 c=mix(low,high,smoothstep(.12,.85,uSky));c=mix(c,vec3(.60,.65,.67),uStorm*.55);gl_FragColor=vec4(c,1.);}`}));scene.add(sky);
const sun=new T.DirectionalLight(0xfff0dc,2.2);sun.position.set(-18,15,14);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-24;sun.shadow.camera.right=24;sun.shadow.camera.top=24;sun.shadow.camera.bottom=-24;sun.shadow.camera.near=.5;sun.shadow.camera.far=100;sun.shadow.bias=-.00035;sun.shadow.normalBias=.004;scene.add(sun);
const hemi=new T.HemisphereLight(0xd6e6ee,0x54503f,2.05);scene.add(hemi);
const fill=new T.DirectionalLight(0xdfeaf2,.40);fill.position.set(16,9,22);scene.add(fill);
// --- ground -----------------------------------------------------------------
const snowCanvas=document.createElement('canvas');snowCanvas.width=snowCanvas.height=512;const sg=snowCanvas.getContext('2d');sg.fillStyle='#e4e8e2';sg.fillRect(0,0,512,512);for(let i=0;i<12000;i++){sg.fillStyle=`rgba(66,86,86,${.012+rand()*.036})`;sg.fillRect(rand()*512,rand()*512,1+rand()*6,1+rand()*2)}
const snowTex=new T.CanvasTexture(snowCanvas);snowTex.colorSpace=T.SRGBColorSpace;snowTex.wrapS=snowTex.wrapT=T.RepeatWrapping;snowTex.repeat.set(38,38);
const tundra=await new T.TextureLoader().loadAsync('/tundra.jpg');tundra.colorSpace=T.SRGBColorSpace;tundra.wrapS=tundra.wrapT=T.RepeatWrapping;tundra.repeat.set(30,30);
const groundMat=new T.MeshStandardMaterial({color:0xd8ded6,map:tundra,roughness:1});
groundMat.onBeforeCompile=sh=>{sh.uniforms.snowMap={value:snowTex};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 tP;').replace('#include <begin_vertex>','#include <begin_vertex>\ntP=position;');sh.fragmentShader=sh.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 tP;uniform sampler2D snowMap;').replace('#include <map_fragment>','#ifdef USE_MAP\nfloat lp=.5+.5*(sin(tP.x*.19+sin(tP.z*.13))*cos(tP.z*.23+tP.x*.06)*.7+sin(tP.x*.71-tP.z*.53)*.3);\nfloat cover=smoothstep(.30,.60,lp);\nvec4 soil=texture2D(map,vMapUv),snow=texture2D(snowMap,vMapUv);\nvec3 bare=mix(vec3(.38,.37,.30),vec3(.58,.53,.39),lp);\ndiffuseColor.rgb=mix(bare,snow.rgb*.98,cover*.9);\n#endif')};
function terrain(x,z){const flat=smooth((Math.abs(z)-3)/12);return flat*(.42*Math.sin(x*.11)*Math.cos(z*.09)+.24*Math.sin(x*.29+z*.15))-.05}
const groundGeo=new T.PlaneGeometry(220,180,150,120);groundGeo.rotateX(-PI/2);const gp=groundGeo.attributes.position;
for(let i=0;i<gp.count;i++)gp.setY(i,terrain(gp.getX(i),gp.getZ(i)));
groundGeo.computeVertexNormals();const ground=new T.Mesh(groundGeo,groundMat);ground.receiveShadow=true;scene.add(ground);
const ridgeGeo=new T.PlaneGeometry(220,90,180,60);ridgeGeo.rotateX(-PI/2);const rp=ridgeGeo.attributes.position;
for(let i=0;i<rp.count;i++){const x=rp.getX(i),z=rp.getZ(i);const dep=smooth((z+44)/22)*smooth((45-z)/14);const crest=3.4+1.9*Math.sin(x*.068+1.4)+1.2*Math.sin(x*.16+2.9)+.5*Math.sin(x*.34);rp.setY(i,Math.max(0,dep*crest))}
ridgeGeo.computeVertexNormals();const ridge=new T.Mesh(ridgeGeo,new T.MeshStandardMaterial({color:0x91a3ae,roughness:1}));ridge.position.set(0,-.6,-62);scene.add(ridge);
const sea=new T.Mesh(new T.PlaneGeometry(520,240,120,50),new T.MeshStandardMaterial({color:0x2e4348,roughness:.55,metalness:.05}));sea.rotation.x=-PI/2;sea.position.set(0,-1.35,-150);scene.add(sea);
// --- vegetation -------------------------------------------------------------
const verts=[];for(let j=0;j<6;j++){const a=j*PI/6,dx=Math.cos(a),dz=Math.sin(a),bend=(j%2?.14:-.13),ht=.32+j*.05;const at=(v,side)=>[dx*side*.024*(1-v)+bend*v*v,ht*v,dz*side*.024*(1-v)+bend*.3*v*v];for(let k=0;k<3;k++){const u=k/3,v=(k+1)/3;verts.push(...at(u,-1),...at(u,1),...at(v,-1),...at(u,1),...at(v,1),...at(v,-1))}}
const tuftGeo=new T.BufferGeometry();tuftGeo.setAttribute('position',new T.Float32BufferAttribute(verts,3));tuftGeo.computeVertexNormals();
const wind={value:0};const tuftMat=new T.MeshStandardMaterial({color:0xb0a580,roughness:1,side:T.DoubleSide});
tuftMat.onBeforeCompile=sh=>{sh.uniforms.wind={value:wind};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nuniform float wind;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x+=sin(wind*1.05+instanceMatrix[3].x*.55)*position.y*position.y*(.11+step(2.,instanceMatrix[3].z)*.06);')};
const tufts=new T.InstancedMesh(tuftGeo,tuftMat,4600);const dm=new T.Object3D();
for(let i=0;i<4600;i++){const x=rand()*120-60,z=rand()*76-34;dm.position.set(x,terrain(x,z)+.01,z);dm.rotation.set(0,rand()*PI,.07*(rand()-.5));dm.scale.setScalar(.3+rand()*.85);dm.updateMatrix();tufts.setMatrixAt(i,dm.matrix);tufts.setColorAt(i,new T.Color().setHSL(.11,.14,.28+rand()*.18))}scene.add(tufts);
const stoneMat=new T.MeshStandardMaterial({color:0x5c645f,roughness:1});
for(let i=0;i<80;i++){const x=rand()*76-38,z=rand()*44-22;const r=.04+rand()*.18;const o=new T.Mesh(new T.DodecahedronGeometry(1,1),stoneMat);o.position.set(x,terrain(x,z)+r*.25,z);o.scale.set(r,r*(.3+rand()*.35),r*(.7+rand()*.5));o.rotation.set(rand()*.4,rand()*PI,rand()*.3);o.castShadow=true;o.receiveShadow=true;scene.add(o)}
// --- drifting snow ----------------------------------------------------------
const snowGeo=new T.BufferGeometry();const SPN=1200;const sp=new Float32Array(SPN*3);
for(let i=0;i<SPN;i++){sp[3*i]=rand()*70-35;sp[3*i+1]=rand()*8;sp[3*i+2]=rand()*46-23}
snowGeo.setAttribute('position',new T.BufferAttribute(sp,3));
const snowMat=new T.PointsMaterial({color:0xeef4f4,size:.06,transparent:true,opacity:.42,depthWrite:false});
snowMat.onBeforeCompile=sh=>{sh.uniforms.wind={value:wind};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nuniform float wind;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x=mod(position.x+wind*1.15+35.,70.)-35.;transformed.y=mod(position.y-wind*.13+800.,8.);transformed.z+=sin(wind*.45+position.x*.3)*1.1;')};
const snowfall=new T.Points(snowGeo,snowMat);scene.add(snowfall);
// --- animals -----------------------------------------------------------------
const asset=await new GLTFLoader().loadAsync('/mammoth.glb');const model=asset.scene;let triangles=0;model.traverse(o=>{if(o.isMesh)triangles+=o.geometry.index?o.geometry.index.count/3:o.geometry.attributes.position.count/3});
const clip=asset.animations.find(a=>a.name==='WalkInPlace_Experimental');if(!clip)throw Error('walk clip missing');
const t0=Math.min(...clip.tracks.map(t=>t.times[0]));for(const tr of clip.tracks)tr.times=Float32Array.from(tr.times,t=>t-t0);clip.resetDuration();
const PERIOD=clip.duration,STANCE=.75,STRIDE=.14,SCALE=2.45,SPEED=STRIDE*SCALE/(PERIOD*STANCE);
const blobCanvas=document.createElement('canvas');blobCanvas.width=blobCanvas.height=128;const bg=blobCanvas.getContext('2d');const grd=bg.createRadialGradient(64,64,4,64,64,64);grd.addColorStop(0,'rgba(14,20,22,.40)');grd.addColorStop(1,'rgba(14,20,22,0)');bg.fillStyle=grd;bg.fillRect(0,0,128,128);const blobTex=new T.CanvasTexture(blobCanvas);blobTex.colorSpace=T.SRGBColorSpace;
function makeAnimal(scale,heading){const root=new T.Group(),obj=clone(model);obj.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});obj.scale.setScalar(scale);root.add(obj);scene.add(root);
 const mixer=new T.AnimationMixer(obj);const action=mixer.clipAction(clip);action.play();
 const blob=new T.Mesh(new T.PlaneGeometry(5.0,2.6),new T.MeshBasicMaterial({map:blobTex,transparent:true,depthWrite:false,opacity:.32}));blob.rotation.x=-PI/2;scene.add(blob);
 const bones={};obj.traverse(o=>{if(o.isBone&&(o.name==='trunk_lower'||o.name==='trunk_upper'||o.name==='head'))bones[o.name]=o});
 return{root,obj,mixer,action,scale,heading,blob,bones}}
const herd=[makeAnimal(SCALE,0),makeAnimal(2.22,-.25),makeAnimal(2.05,.34),makeAnimal(1.20,.1),makeAnimal(2.10,-.6)];
function place(a,x,z,y,heading,phase,t,walking=true){
// The rig faces local -X (head/trunk sit at negative x). Zero heading therefore means
// "facing +X", so every animal must be spun by PI before it can walk along +X.
 a.root.position.set(x,y,z);a.obj.rotation.y=heading+PI;
 if(walking)a.mixer.setTime(t+phase*PERIOD);
 a.blob.position.set(x+.04,y+.004,z+.40*a.scale);a.blob.scale.setScalar(a.scale/SCALE);
}
// The rig ships only a walk and an idle clip, so the trunk reach is authored here:
// a slow sweep over the snow toward vegetation, then a lift. It is kinematic.
// The third-party rig ships only walk and idle clips; its trunk bones barely
// respond to hand-authored rotation (measured: +-0.6 rad moves the tip ~6 cm),
// so a "trunk reaching for grass" performance is NOT attempted here. The section
// stays with what the rig can actually do: locomotion and mass.
// --- camera ------------------------------------------------------------------
const cam=new T.PerspectiveCamera(36,W/H,.04,420);const look=new T.Vector3(),pos=new T.Vector3();
const SHOTS=[{n:'the coat, up close',s:0,e:9},{n:'flank and feet',s:9,e:17},{n:'weight on the legs',s:17,e:25},{n:'herd in the wind',s:25,e:31},{n:'hold on the plain',s:31,e:34}];
function shotIndex(t){for(let i=SHOTS.length-1;i>=0;i--)if(t>=SHOTS[i].s)return i;return 0}
function layout(i,t){const a=herd;
 if(i===1){ // very close flank, animal walking past; camera stays put
  const u=(t-SHOTS[1].s)/8;const wx=-9.5+SPEED*t*1.15;
  place(a[0],wx,.6,.02,0,.0,t);
  place(a[3],wx-6.5,4.4,.03,.08,.45,t);
  place(a[1],wx-15,2.2,.02,-.2,.31,t);place(a[2],wx-23,-1.4,.02,.2,.62,t);
  place(a[4],wx+16,8.5,.03,-.7,0,t,false);
  return{cam:{x:wx-1.1+u*.5,y:1.55,z:6.9},look:{x:wx+1.5,y:1.30,z:.4}}}
 if(i===2){ // low on the legs: weight transfer, snow breaking under the feet
  const u=(t-SHOTS[2].s)/8;const wx=-4.2+SPEED*t*1.25;
  place(a[0],wx,.35,.02,.05,.0,t);
  place(a[3],wx+3.4,2.9,.02,.10,.45,t);
  place(a[1],wx-8.5,-1.9,.02,-.14,.31,t);place(a[2],wx-15.5,3.4,.02,.14,.62,t);
  place(a[4],wx+13,7.5,.03,-.6,0,t,false);
  return{cam:{x:wx+2.55-u*.35,y:.62,z:5.4},look:{x:wx-.55,y:.72,z:.25}}}
 if(i===3){ // herd walking into a low sun with wind in the grass
  const u=(t-SHOTS[3].s)/6;const wx=-2+SPEED*t*.85;
  place(a[0],wx,-.2,.02,0,.0,t);place(a[1],wx-8.5,2.2,.03,-.16,.31,t);place(a[3],wx-4.6,4.0,.03,.10,.45,t);
  place(a[2],wx-15,-2.4,.02,.12,.62,t);place(a[4],wx+11,7.5,.03,-.55,0,t,false);
  return{cam:{x:wx+7.4,y:1.85,z:14.5},look:{x:wx-2.4,y:1.25,z:1.0}}}
 if(i===4){ // final hold: small in the landscape, big sky
  const u=(t-SHOTS[4].s)/3;
  place(a[0],-1.6+u*.45,1.4,.01,0,.0,t);place(a[1],-7.8+u*.4,3.8,.02,-.2,.31,t);place(a[3],-4.0+u*.4,5.4,.02,.12,.45,t);
  place(a[2],-13.5+u*.35,-1.0,.02,.2,.62,t);place(a[4],8.5,8.0,.03,-.7,0,t,false);
  return{cam:{x:1.2-u*.3,y:1.95,z:19.5},look:{x:-2.6,y:1.30,z:2.0}}}
 // shot 0 renders the fur texture pass instead of the world (see composite below)
 place(a[0],-2.0,1.0,.02,0,.0,t);place(a[1],-9,3.4,.02,-.2,.31,t);place(a[2],-16,-1.2,.02,.2,.62,t);place(a[3],-.6,3.8,.03,.1,.45,t);place(a[4],9,7,.03,-.7,0,t,false);
 return{cam:{x:2.0,y:1.75,z:12.0},look:{x:-2.0,y:1.3,z:1.0}};
}
// --- macro fur pass ---------------------------------------------------------
const fur=await new T.TextureLoader().loadAsync('/fur.jpg');fur.colorSpace=T.SRGBColorSpace;fur.wrapS=fur.wrapT=T.RepeatWrapping;
const macroScene=new T.Scene();
const macroMat=new T.ShaderMaterial({uniforms:{map:{value:fur},uTime:{value:0}},vertexShader:`varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,0.,1.);}`,fragmentShader:`uniform sampler2D map;uniform float uTime;varying vec2 vUv;
void main(){
 vec2 uv=vUv*vec2(1.55,.91)+vec2(uTime*.0085,sin(uTime*.19)*.008);
 vec3 c=texture2D(map,uv).rgb;
 vec3 c2=texture2D(map,uv*vec2(2.1,2.1)+vec2(.37,.11)).rgb;
 c=mix(c,c2*.82,.34);
 float band=smoothstep(.70,0.,abs(vUv.x-(.5+.42*sin(uTime*.33))));
 c*=min(2.35,1.10+1.55*band);
 c*=mix(vec3(1.),vec3(.94,.97,1.03),vUv.y);
 float vig=smoothstep(1.30,.30,length(vUv-.5));
 c*=mix(.58,1.,vig);
 gl_FragColor=vec4(c,1.);
}`});
macroScene.add(new T.Mesh(new T.PlaneGeometry(2,2),macroMat));
const macroCam=new T.OrthographicCamera(-1,1,1,-1,0,1);
// --- per-shot weather -------------------------------------------------------
const LOOK=[{sky:.16,storm:.10,fog:0x9fb0b6,fogFar:120,exp:1.02,sun:2.1,hemi:2.0},
 {sky:.22,storm:.06,fog:0xa9b8bd,fogFar:125,exp:1.03,sun:2.35,hemi:2.0},
 {sky:.34,storm:.05,fog:0xb4c1c2,fogFar:110,exp:1.05,sun:2.5,hemi:2.05},
 {sky:.52,storm:.14,fog:0xa9b7b6,fogFar:118,exp:1.02,sun:2.45,hemi:1.72},
 {sky:.62,storm:.10,fog:0xa9b5b7,fogFar:130,exp:1.0,sun:1.75,hemi:1.9}];
let frame=0;
function smoothFog(fog,color,far){fog.color.setHex(color);fog.near=Math.min(28,far*.22);fog.far=far}
function draw(t){t=Math.max(0,Math.min(DURATION,t));frame++;wind.value=t;
 const i=shotIndex(t),prev=Math.max(0,i-1);
 const lt=t-SHOTS[i].s;
 const w=smooth(Math.min(1,lt/.8));
 const L=LOOK[i],P=LOOK[prev];
 const mixv=k=>lerp(P[k],L[k],w);
 uSky.value=mixv('sky');uStorm.value=mixv('storm');
 smoothFog(scene.fog,mixv('fog'),mixv('fogFar'));
 renderer.toneMappingExposure=mixv('exp');sun.intensity=mixv('sun');hemi.intensity=mixv('hemi');
 snowMat.opacity=.06+.40*mixv('storm');
 const ang=lerp(-.5,1.9,uSky.value);sun.position.set(Math.cos(ang)*24,lerp(16,9,uSky.value),Math.sin(ang)*18+9);
 const L2=layout(i,t);pos.set(L2.cam.x,L2.cam.y,L2.cam.z);look.set(L2.look.x,L2.look.y,L2.look.z);
 pos.x+=.009*Math.sin(t*.58);pos.y+=.006*Math.sin(t*.44+1.1);
 cam.position.copy(pos);cam.updateProjectionMatrix();cam.lookAt(look);
 g.clearRect(0,0,W,H);renderer.render(scene,cam);g.drawImage(renderer.domElement,0,0);
 // Fur pass: full frame at the top of the section, dissolving into the animal.
 const macroA=t<8?1:t<9.4?smooth(1-(t-8)/1.4):0;
 if(macroA>0){macroMat.uniforms.uTime.value=t;renderer.setRenderTarget(null);renderer.clear();renderer.render(macroScene,macroCam);
  const off=document.createElement('canvas');off.width=W;off.height=H;off.getContext('2d').drawImage(renderer.domElement,0,0);
  g.globalAlpha=macroA;g.drawImage(off,0,0);g.globalAlpha=1;
  // a soft dark edge so the texture reads as a lens, not a wallpaper
  const e=g.createRadialGradient(W*.5,H*.5,H*.34,W*.5,H*.5,H*.92);e.addColorStop(0,'rgba(0,0,0,0)');e.addColorStop(1,`rgba(6,9,10,${.55*macroA})`);g.fillStyle=e;g.fillRect(0,0,W,H);}
 // Grade: cold lift, gentle bloom, vignette, grain.
 g.globalCompositeOperation='soft-light';g.fillStyle=`rgba(150,176,192,${.10+.03*macroA})`;g.fillRect(0,0,W,H);g.globalCompositeOperation='source-over';
 const bg2=g.createRadialGradient(W*.30,H*.40,10,W*.30,H*.40,W*.62);
 bg2.addColorStop(0,'rgba(255,238,214,.07)');bg2.addColorStop(1,'rgba(0,0,0,0)');
 g.globalCompositeOperation='screen';g.fillStyle=bg2;g.fillRect(0,0,W,H);g.globalCompositeOperation='source-over';
 const vg=g.createRadialGradient(W*.5,H*.5,H*.30,W*.5,H*.5,H*.9);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(6,10,12,.34)');g.fillStyle=vg;g.fillRect(0,0,W,H);
 for(let k=0;k<1500;k++){const gx=(k*89+((frame*131)%877))%W,gy=(k*57+((frame*47)%563))%H;g.fillStyle=k%3?'rgba(255,255,255,.024)':'rgba(0,0,0,.038)';g.fillRect(gx,gy,1,1)}
 const label=macroA>.35?'ILLUSTRATIVE COAT TEXTURE · NOT AN OBSERVED ANIMAL':'WRANGEL · ILLUSTRATIVE RECONSTRUCTION';
 g.fillStyle='rgba(240,244,240,.88)';g.shadowColor='rgba(8,14,16,.95)';g.shadowBlur=7;g.font='700 14px Manrope';g.textAlign='left';
 g.fillText(label,30,690);g.shadowBlur=0;
 return{time:t,shot:i,shot_name:SHOTS[i].n,animals:5,triangles,historical_geography:false,macro:macroA,storm:uStorm.value,snow:snowMat.opacity,trunk:a=>a}}
function setTimeOnly(t){return draw(t)}
window.__seek=t=>{frame=Math.round(t*30);return setTimeOnly(t)};window.__probe=window.__seek;
window.__shotList=SHOTS;
window.__ready=true;draw(0);
