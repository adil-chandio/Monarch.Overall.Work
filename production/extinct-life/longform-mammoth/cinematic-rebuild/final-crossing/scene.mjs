// Closing scene: a herd crosses at low sun, the camera settles on one footprint.
// Illustrative; invented place/weather; same third-party rig (../mammoth-rig/README.md).
import * as T from 'three';
import {GLTFLoader} from '/GLTFLoader.js';
import {clone} from '/utils/SkeletonUtils.js';
const W=1280,H=720,PI=Math.PI;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.16;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
const scene=new T.Scene();scene.fog=new T.Fog(0xcdbfa9,26,150);
let seed=771903;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};const lerp=(a,b,u)=>a+(b-a)*u;
const sky=new T.Mesh(new T.SphereGeometry(320,32,18),new T.ShaderMaterial({side:T.BackSide,depthWrite:false,vertexShader:`varying vec3 w;void main(){w=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*modelMatrix*vec4(position,1.);}`,fragmentShader:`varying vec3 w;void main(){vec3 d=normalize(w);float h=clamp(d.y,0.,1.);float sun=pow(max(0.,dot(d,normalize(vec3(-.72,.13,-.68)))),7.);vec3 horizon=vec3(.86,.72,.56);vec3 upper=vec3(.30,.42,.55);vec3 c=mix(horizon,upper,smoothstep(0.,.72,h));c+=sun*vec3(.30,.20,.06);gl_FragColor=vec4(c,1.);}`}));scene.add(sky);
const sunDisc=new T.Mesh(new T.CircleGeometry(6.5,40),new T.MeshBasicMaterial({color:0xffd9a6,fog:false,transparent:true,opacity:.9}));sunDisc.position.set(-150,-6,-152);sunDisc.scale.setScalar(1.5);sunDisc.lookAt(0,6,0);scene.add(sunDisc);
scene.add(new T.HemisphereLight(0xbcd6ea,0x6b6255,2.35));
const sun=new T.DirectionalLight(0xffd6a8,2.5);sun.position.set(-44,16,26);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-46;sun.shadow.camera.right=46;sun.shadow.camera.top=46;sun.shadow.camera.bottom=-46;sun.shadow.camera.near=.5;sun.shadow.camera.far=150;sun.shadow.bias=-.00035;sun.shadow.normalBias=.004;scene.add(sun);
const fill=new T.DirectionalLight(0xd9e6ee,1.15);fill.position.set(18,9,30);scene.add(fill);
// Snow shader: pale base with cool shadow tint, subtle sparkle and drift banding.
const snowCanvas=document.createElement('canvas');snowCanvas.width=snowCanvas.height=512;const sg=snowCanvas.getContext('2d');sg.fillStyle='#e7ece8';sg.fillRect(0,0,512,512);for(let i=0;i<14000;i++){sg.fillStyle=`rgba(72,98,104,${.012+rand()*.04})`;sg.fillRect(rand()*512,rand()*512,1+rand()*7,1+rand()*2)}
const snowTex=new T.CanvasTexture(snowCanvas);snowTex.colorSpace=T.SRGBColorSpace;snowTex.wrapS=snowTex.wrapT=T.RepeatWrapping;snowTex.repeat.set(26,26);
const tundra=await new T.TextureLoader().loadAsync('/tundra.jpg');tundra.colorSpace=T.SRGBColorSpace;tundra.wrapS=tundra.wrapT=T.RepeatWrapping;tundra.repeat.set(26,26);
const groundMat=new T.MeshStandardMaterial({color:0xdfe5e2,map:tundra,roughness:.92,vertexColors:true});
groundMat.onBeforeCompile=sh=>{sh.uniforms.snowMap={value:snowTex};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 tP;').replace('#include <begin_vertex>','#include <begin_vertex>\ntP=position;');sh.fragmentShader=sh.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 tP;uniform sampler2D snowMap;').replace('#include <map_fragment>','#ifdef USE_MAP\nvec4 soil=texture2D(map,vMapUv),snow=texture2D(snowMap,vMapUv);\nfloat band=.5+.5*sin(tP.x*.19+sin(tP.z*.14)*1.4);\ndiffuseColor.rgb=mix(snow.rgb*.93,soil.rgb*.55,band*.30);\ndiffuseColor.rgb+=snow.rgb*.05*smoothstep(.9,.97,sin(tP.x*2.1+tP.z*1.7));\n#endif')};
const groundGeo=new T.PlaneGeometry(190,150,120,96);groundGeo.rotateX(-PI/2);const gp=groundGeo.attributes.position;const gc=[];
const shore=x=>1.1*Math.sin(x*.13)+.6*Math.sin(x*.31);
function terrain(x,z){const flat=smooth((Math.abs(z)-5)/9);const roll=flat*(.5*Math.sin(x*.12)*Math.cos(z*.1)+.3*Math.sin(x*.26+z*.16));return roll-.055-3.2*smooth((-z-5+shore(x))/9)}
for(let i=0;i<gp.count;i++){const x=gp.getX(i),z=gp.getZ(i);gp.setY(i,terrain(x,z));const n=.9+.1*Math.sin(x*.29+z*.14);gc.push(n,n*.998,n*.985)}
groundGeo.setAttribute('color',new T.Float32BufferAttribute(gc,3));groundGeo.computeVertexNormals();const ground=new T.Mesh(groundGeo,groundMat);ground.receiveShadow=true;scene.add(ground);
const ridgeGeo=new T.PlaneGeometry(190,70,190,64);ridgeGeo.rotateX(-PI/2);const rp=ridgeGeo.attributes.position;const rc=[];
for(let i=0;i<rp.count;i++){const x=rp.getX(i),z=rp.getZ(i);const depth=smooth((z+35)/19)*smooth((35-z)/12);const crest=2.55+1.35*Math.sin(x*.061+.4)+.95*Math.sin(x*.135+2.2)+.5*Math.sin(x*.29+1.1);const rough=.42*Math.sin(x*.47+z*.19)+.22*Math.cos(x*.93-z*.27);const h=Math.max(0,depth*(crest+rough));rp.setY(i,h);const v=.8+Math.min(1,h/10)*.16;rc.push(v*.97,v,v*.97)}
ridgeGeo.setAttribute('color',new T.Float32BufferAttribute(rc,3));ridgeGeo.computeVertexNormals();const ridge=new T.Mesh(ridgeGeo,new T.MeshStandardMaterial({color:0x9aa7ae,vertexColors:true,roughness:1}));ridge.position.set(0,-.9,-64);scene.add(ridge);
// Low snowbanks break the sea/land seam so the horizon is not a hard line.
const bankMat=new T.MeshStandardMaterial({color:0xdde5e3,roughness:1});
for(const [bx,bz,bw,bh] of [[-26,-30,24,1.1],[-4,-42,30,1.35],[22,-34,22,1.0],[42,-46,26,1.25]]){const b=new T.Mesh(new T.SphereGeometry(1,26,12,0,PI*2,0,PI*.5),bankMat);b.position.set(bx,-.35,bz);b.scale.set(bw,bh,bw*.55);b.receiveShadow=true;scene.add(b)}
// Thin sea strip at the horizon; a shader surface, not a measured shoreline.
const seaClock={value:0};const seaGeo=new T.PlaneGeometry(500,120,120,40);seaGeo.rotateX(-PI/2);
const sea=new T.Mesh(seaGeo,new T.ShaderMaterial({uniforms:{time:seaClock},vertexShader:`uniform float time;varying vec3 lp;void main(){vec3 p=position;float w=sin(p.x*.24+p.z*.5+time*.5)*.04;w*=1.-smoothstep(10.,45.,60.-p.z);p.y+=w;lp=p;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,fragmentShader:`uniform float time;varying vec3 lp;void main(){float s=sin(lp.x*1.3+time*.3)*sin(lp.z*.9-lp.x*.2);vec3 c=mix(vec3(.20,.25,.27),vec3(.42,.44,.43),clamp(s*.5+.5,0.,1.));c+=pow(max(0.,s),16.)*.30*vec3(.95,.82,.62);
float haze=smoothstep(4.,50.,60.-lp.z);c=mix(c,vec3(.55,.54,.51),haze*.75);gl_FragColor=vec4(c,1.);}`}));sea.position.set(0,-1.05,-112);scene.add(sea);
// Vegetation: sparse dry tufts, plus a low ground mist band behind the herd.
const verts=[];for(let j=0;j<5;j++){const a=j*PI/5,dx=Math.cos(a),dz=Math.sin(a),bend=(j%2?.12:-.12),ht=.3+j*.045;const at=(v,side)=>[dx*side*.022*(1-v)+bend*v*v,ht*v,dz*side*.022*(1-v)+bend*.3*v*v];for(let k=0;k<3;k++){const u=k/3,v=(k+1)/3;verts.push(...at(u,-1),...at(u,1),...at(v,-1),...at(u,1),...at(v,1),...at(v,-1))}}
const tuftGeo=new T.BufferGeometry();tuftGeo.setAttribute('position',new T.Float32BufferAttribute(verts,3));tuftGeo.computeVertexNormals();const wind={value:0};
const tuftMat=new T.MeshStandardMaterial({color:0xb0a481,roughness:1,side:T.DoubleSide});
tuftMat.onBeforeCompile=sh=>{sh.uniforms.wind={value:wind};sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nuniform float wind;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x+=sin(wind*1.15+instanceMatrix[3].x*.5)*position.y*position.y*.15;')};
const tufts=new T.InstancedMesh(tuftGeo,tuftMat,2200);const dm=new T.Object3D();
for(let i=0;i<2200;i++){const x=rand()*100-50,z=(rand()<.4?1:-1)*(2.2+rand()*28);dm.position.set(x,terrain(x,z)+.005,z);dm.rotation.set(0,rand()*PI,.06*(rand()-.5));dm.scale.setScalar(.3+rand()*.75);dm.updateMatrix();tufts.setMatrixAt(i,dm.matrix);tufts.setColorAt(i,new T.Color().setHSL(.11,.17,.34+rand()*.2))}scene.add(tufts);
for(let i=0;i<52;i++){const x=rand()*60-30,z=-2.4-rand()*2.6+shore(x),size=.05+rand()*.19;const o=new T.Mesh(new T.DodecahedronGeometry(1,1),new T.MeshStandardMaterial({color:0x5d625c,roughness:1}));o.position.set(x,terrain(x,z)+size*.18,z);o.scale.set(size*(.7+rand()),size*(.3+rand()*.3),size*(.7+rand()));o.rotation.set(rand()*.4,rand()*PI,rand()*.3);o.castShadow=true;scene.add(o)}
const mistMat=new T.MeshBasicMaterial({color:0xd9cbbc,transparent:true,opacity:.14,depthWrite:false});
for(let i=0;i<2;i++){const m=new T.Mesh(new T.PlaneGeometry(150,.55),mistMat);m.position.set(0,.30+i*.26,-13-i*6);m.renderOrder=1;scene.add(m)}
const asset=await new GLTFLoader().loadAsync('/mammoth.glb');const model=asset.scene;let triangles=0;model.traverse(o=>{if(o.isMesh)triangles+=o.geometry.index?o.geometry.index.count/3:o.geometry.attributes.position.count/3});
const clip=asset.animations.find(a=>a.name==='WalkInPlace_Experimental');if(!clip)throw Error('walk clip missing');
const t0=Math.min(...clip.tracks.map(t=>t.times[0]));for(const tr of clip.tracks)tr.times=Float32Array.from(tr.times,t=>t-t0);clip.resetDuration();
const PERIOD=clip.duration,STANCE=.75,STRIDE=.14,SCALE=2.45,SPEED=STRIDE*SCALE/(PERIOD*STANCE);
const blobCanvas=document.createElement('canvas');blobCanvas.width=blobCanvas.height=128;const bg=blobCanvas.getContext('2d');const grad=bg.createRadialGradient(64,64,4,64,64,64);grad.addColorStop(0,'rgba(24,26,30,.42)');grad.addColorStop(1,'rgba(24,26,30,0)');bg.fillStyle=grad;bg.fillRect(0,0,128,128);const blobTex=new T.CanvasTexture(blobCanvas);blobTex.colorSpace=T.SRGBColorSpace;
function makeAnimal(x,z,phase,scale,heading,speed){const root=new T.Group(),obj=clone(model);obj.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});obj.scale.setScalar(scale);obj.rotation.y=heading;root.add(obj);scene.add(root);const mixer=new T.AnimationMixer(obj);mixer.clipAction(clip).play();const blob=new T.Mesh(new T.PlaneGeometry(4.9,2.4),new T.MeshBasicMaterial({map:blobTex,transparent:true,depthWrite:false,opacity:.30}));blob.rotation.x=-PI/2;scene.add(blob);return{root,obj,mixer,x,z,phase,scale,speed,heading,blob,y:terrain(x,z)+.03}}
// The herd crosses left to right and leaves the frame; one print stays behind.
// Timed so the leading animals pass the footprint's position around 8 s and
// walk out of frame right by the end, leaving the print as the last subject.
const herd=[makeAnimal(-10.4,0.5,0,SCALE,0,1),makeAnimal(-16.0,1.9,.30,2.2,0,.94),makeAnimal(-21.6,-0.9,.62,2.32,0,1.03),makeAnimal(-7.2,1.4,.45,1.22,0,1.05)];
// Footprint: a painted impression decal on the snow. Pale pressed sole, four
// separated toe lobes and a lit rim where snow is pushed up. Stylised — not a
// measured specimen, and the deformation is authored rather than simulated.
const printCanvas=document.createElement('canvas');printCanvas.width=printCanvas.height=768;const pc=printCanvas.getContext('2d');
function ellipse(cx,cy,rx,ry,rot,tone,blur){pc.save();pc.translate(cx,cy);pc.rotate(rot);if(blur)pc.filter=`blur(${blur}px)`;pc.fillStyle=tone;pc.beginPath();pc.ellipse(0,0,rx,ry,0,0,PI*2);pc.fill();pc.restore();pc.filter='none'}
// Sheared snow bank behind the print lip: bright on the sunlit side.
ellipse(384,250,250,110,-.05,'rgba(250,253,253,.30)',42);
// Pressed sole: deeper, cooler interior. Sharper edge than the drift around it.
ellipse(384,440,205,236,0,'rgba(120,141,152,.80)',13);
ellipse(384,470,178,196,0,'rgba(96,118,131,.86)',9);
ellipse(384,505,150,152,0,'rgba(80,102,116,.88)',7);
// Four toe impressions with clear gaps.
for(const [cx,cy,rx,ry,rot] of [[262,292,62,76,-.24],[352,250,58,74,-.03],[444,254,58,74,.05],[532,300,62,76,.24]]){
 ellipse(cx,cy-4,rx*.20,ry*.16,rot,'rgba(236,246,248,.42)',9);                         // sunlit lip inside the toe
 ellipse(cx,cy+7,rx+.09*ry,ry+.09*ry,rot,'rgba(228,240,244,.40)',8);                    // pale rim of pushed snow
 ellipse(cx,cy,rx,ry,rot,'rgba(104,126,140,.86)',4);                                    // pressed toe, same family as sole
 ellipse(cx,cy+ry*.28,rx*.80,ry*.46,rot,'rgba(80,102,118,.80)',4);}                     // deeper front edge of the toe
// Rim of pushed-up snow on the leading edge, plus a broken lip at the heel.
pc.filter='blur(7px)';pc.strokeStyle='rgba(252,255,255,.70)';pc.lineWidth=13;pc.beginPath();pc.ellipse(384,330,196,182,0,PI*1.13,PI*1.87);pc.stroke();
pc.strokeStyle='rgba(150,175,186,.55)';pc.lineWidth=9;pc.beginPath();pc.ellipse(384,530,178,140,0,PI*.18,PI*.82);pc.stroke();pc.filter='none';
// A few displaced grains, brighter on the sun side.
for(let i=0;i<200;i++){const a=rand()*PI*2,r=215+rand()*130;pc.fillStyle=Math.cos(a)<0?`rgba(250,254,254,${.06+rand()*.16})`:`rgba(84,106,120,${.05+rand()*.14})`;pc.beginPath();pc.arc(384+Math.cos(a)*r,420+Math.sin(a)*r*.98,1.5+rand()*4,0,PI*2);pc.fill()}
const printTex=new T.CanvasTexture(printCanvas);printTex.colorSpace=T.SRGBColorSpace;printTex.anisotropy=4;
const printMat=new T.MeshStandardMaterial({map:printTex,transparent:true,opacity:.97,roughness:1,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-3});
function makePrint(x,z,rot,scale){const m=new T.Mesh(new T.PlaneGeometry(1.05,1.35),printMat);m.rotation.x=-PI/2;m.rotation.z=rot;m.scale.setScalar(scale);m.position.set(x,terrain(x,z)+.006,z);m.receiveShadow=true;scene.add(m);return m}
// The lead animal's print, then the trail it left; later prints are smaller and fainter.
const foregroundPrint=makePrint(-1.28,1.85,.16,1.0);foregroundPrint.material=printMat.clone();foregroundPrint.material.opacity=.98;
const trail=[];for(let k=0;k<5;k++){const x=-4.2-k*2.6,z=1.55+Math.sin(k*.9)*.20;const m=makePrint(x,z,.18+Math.sin(k)*.3,.82-k*.10);m.material=printMat.clone();m.material.opacity=Math.max(.10,.46-k*.08);trail.push(m)}
const cam=new T.PerspectiveCamera(39,W/H,.04,340);const pos=new T.Vector3(),look=new T.Vector3();
const easeInOut=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};
// One continuous move: follow the crossing, then descend and settle low over the
// print now that the animals have passed. No cut.
const wideP=new T.Vector3(6.2,2.35,16.8),wideL=new T.Vector3(-6.6,1.70,0.2);
const midP=new T.Vector3(3.6,1.55,11.2),midL=new T.Vector3(-5.4,1.15,1.6);
const closeP=new T.Vector3(-.55,.62,4.05),closeL=new T.Vector3(-1.28,.20,1.85);
function cameraAt(t){
 const a=easeInOut(t/7.4),b=easeInOut((t-6.4)/6.4);
 pos.copy(wideP).lerp(midP,a);look.copy(wideL).lerp(midL,a);
 pos.lerp(closeP,b);look.lerp(closeL,b);
 cam.position.copy(pos);cam.updateProjectionMatrix();cam.lookAt(look);return cam}
let frame=0;
function draw(t){t=Math.max(0,Math.min(13,t));frame++;wind.value=t;seaClock.value=t;
 for(const a of herd){const x=a.x+a.speed*SPEED*t*4.9;a.root.position.set(x,a.y,a.z);a.mixer.setTime(t*a.speed+a.phase*PERIOD);a.blob.position.set(x+.05,a.y+.004,a.z+.42*a.scale);a.blob.scale.setScalar(a.scale/SCALE);a.blob.visible=x<40}
 mistMat.opacity=.11+.04*Math.sin(t*.27);
 const c=cameraAt(t);g.clearRect(0,0,W,H);renderer.render(scene,c);g.drawImage(renderer.domElement,0,0);
 // Warm low-sun grade, vignette and fine grain; the image stays a render, not a plate.
 g.globalCompositeOperation='soft-light';g.fillStyle='rgba(232,166,98,.22)';g.fillRect(0,0,W,H);g.globalCompositeOperation='source-over';
 const vg=g.createRadialGradient(W*.5,H*.52,H*.28,W*.5,H*.5,H*.9);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(18,12,8,.44)');g.fillStyle=vg;g.fillRect(0,0,W,H);
 for(let i=0;i<2200;i++){const gx=(i*97+((frame*137)%911))%W,gy=(i*61+((frame*53)%577))%H;g.fillStyle=i%3?'rgba(255,244,228,.03)':'rgba(0,0,0,.05)';g.fillRect(gx,gy,1,1)}
 g.fillStyle='rgba(246,242,232,.86)';g.shadowColor='rgba(20,12,6,.9)';g.shadowBlur=7;g.font='700 14px Manrope';g.textAlign='left';g.fillText('ILLUSTRATIVE RECONSTRUCTION · NOT A SPECIFIC HERD',30,690);g.shadowBlur=0;
 return{time:t,animals:herd.length,triangles,footprint_visible:true,historical_geography:false}}
window.__seek=t=>{frame=Math.round(t*30);return draw(t)};
window.__probe=t=>{const st=draw(t);const out=[foregroundPrint,...trail].map(m=>({x:m.position.x,z:m.position.z,y:m.position.y}));return{...st,prints:out.length,lead_x:herd[0].root.position.x}}
window.__ready=true;draw(0);
