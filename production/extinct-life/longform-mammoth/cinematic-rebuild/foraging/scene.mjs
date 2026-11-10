// Native 3D opening world; experimental shots, not the finished documentary.
import * as T from 'three';
import {GLTFLoader} from '/GLTFLoader.js';
import {clone} from '/utils/SkeletonUtils.js';
const W=1280,H=720,FPS=30,PI=Math.PI;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const g=canvas.getContext('2d');
const scene=new T.Scene();scene.background=new T.Color(0xa5c4d2);scene.fog=new T.Fog(0xb2c7cb,22,94);
scene.add(new T.HemisphereLight(0xc7e8ff,0x514741,2.1));const sun=new T.DirectionalLight(0xffe3bd,3);sun.position.set(-15,19,5);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-16;sun.shadow.camera.right=16;sun.shadow.camera.top=16;sun.shadow.camera.bottom=-16;sun.shadow.camera.near=.5;sun.shadow.camera.far=65;sun.shadow.bias=-.0003;sun.shadow.normalBias=.003;scene.add(sun);
let randSeed=831211;const rand=()=>{randSeed=(Math.imul(randSeed,1664525)+1013904223)>>>0;return randSeed/4294967296};const mix=(a,b,u)=>a+(b-a)*u;const smooth=u=>{u=Math.min(1,Math.max(0,u));return u*u*(3-2*u)};
// Gradient sky is a generated shader, not a photographic backdrop.
const sky=new T.Mesh(new T.SphereGeometry(180,32,16),new T.ShaderMaterial({side:T.BackSide,depthWrite:false,vertexShader:`varying vec3 world;void main(){vec4 p=modelMatrix*vec4(position,1.);world=p.xyz;gl_Position=projectionMatrix*viewMatrix*p;}`,fragmentShader:`varying vec3 world;void main(){float h=clamp(normalize(world).y*.8+.20,0.,1.); vec3 c=mix(vec3(.78,.78,.70),vec3(.19,.38,.52),smoothstep(0.,.9,h)); gl_FragColor=vec4(c,1.);}`}));scene.add(sky);
const snowCanvas=document.createElement('canvas');snowCanvas.width=snowCanvas.height=512;const sg=snowCanvas.getContext('2d');sg.fillStyle='#d9e1dc';sg.fillRect(0,0,512,512);
for(let i=0;i<14000;i++){const a=.015+rand()*.045;sg.fillStyle=`rgba(65,93,94,${a})`;let x=rand()*512,y=rand()*512;sg.fillRect(x,y,1+rand()*6,1+rand()*2)}
const snowTex=new T.CanvasTexture(snowCanvas);snowTex.colorSpace=T.SRGBColorSpace;snowTex.wrapS=snowTex.wrapT=T.RepeatWrapping;snowTex.repeat.set(25,25);
const tundra=await new T.TextureLoader().loadAsync('/tundra.jpg');tundra.colorSpace=T.SRGBColorSpace;tundra.wrapS=tundra.wrapT=T.RepeatWrapping;tundra.repeat.set(25,25);
const snow=new T.MeshStandardMaterial({color:0xd9dcd2,map:tundra,roughness:1,vertexColors:true});
snow.onBeforeCompile=shader=>{shader.uniforms.snowMap={value:snowTex};shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 terrainPos;').replace('#include <begin_vertex>','#include <begin_vertex>\nterrainPos=position;');shader.fragmentShader=shader.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 terrainPos;uniform sampler2D snowMap;').replace('#include <map_fragment>',`#ifdef USE_MAP
float shape=sin(terrainPos.x*.29+sin(terrainPos.z*.22))*cos(terrainPos.z*.26+sin(terrainPos.x*.12));
float region=smoothstep(.12,.62,shape)*smoothstep(3.,7.,abs(terrainPos.z));
vec4 soil=texture2D(map,vMapUv),white=texture2D(snowMap,vMapUv);
diffuseColor*=mix(white,soil,region*.82);
#endif`)};
// Floor has real geometry. A near-flat strip beneath animals supports the
// current flat-ground kinematic experiment; hills farther out are illustrative.
const groundGeo=new T.PlaneGeometry(160,140,100,80);groundGeo.rotateX(-PI/2);let pos=groundGeo.attributes.position;const colors=[];
for(let i=0;i<pos.count;i++){let x=pos.getX(i),z=pos.getZ(i);let margin=smooth((Math.abs(z)-5)/7);let height=margin*(.42*Math.sin(x*.17)*Math.cos(z*.13)+.24*Math.sin(x*.29+z*.21));pos.setY(i,height-.055);let n=.93+.07*Math.sin(x*.29+z*.16);colors.push(n,n,n)}
groundGeo.setAttribute('color',new T.Float32BufferAttribute(colors,3));groundGeo.computeVertexNormals();const ground=new T.Mesh(groundGeo,snow);ground.receiveShadow=true;scene.add(ground);
// Faceted mountains carry spatial depth rather than flat painted plates.
// A continuous terrain mesh with irregular ridges, rather than cone-like peaks.
const ridgeGeo=new T.PlaneGeometry(160,62,220,90);ridgeGeo.rotateX(-PI/2);const rp=ridgeGeo.attributes.position;let rc=[];
for(let i=0;i<rp.count;i++){const x=rp.getX(i),z=rp.getZ(i);const depth=smooth((z+31)/18)*smooth((31-z)/12);const crest=4.0+2.8*Math.sin(x*.105)+2.0*Math.sin(x*.23+1.2)+1.1*Math.sin(x*.49-1.5);const rough=.65*Math.sin(x*.65+z*.29)+.36*Math.cos(x*1.32-z*.37)+.16*Math.sin(x*2.8+z*1.9);const h=Math.max(0,depth*(crest+rough));rp.setY(i,h);let v=.86+Math.min(1,h/10)*.12;rc.push(v,v,v)}
ridgeGeo.setAttribute('color',new T.Float32BufferAttribute(rc,3));ridgeGeo.computeVertexNormals();const ridge=new T.Mesh(ridgeGeo,new T.MeshStandardMaterial({color:0x91aab4,vertexColors:true,roughness:1}));ridge.position.set(0,-.5,-48);scene.add(ridge);
// Low tufts use intersecting tapered blades, each individually coloured.
const verts=[];for(let j=0;j<5;j++){const a=j*PI/5,dx=Math.cos(a),dz=Math.sin(a),bend=(j%2?.13:-.13),height=.33+j*.045;const at=(v,side)=>[dx*side*.025*(1-v)+bend*v*v,height*v,dz*side*.025*(1-v)+bend*.3*v*v];for(let k=0;k<3;k++){const u=k/3,v=(k+1)/3;verts.push(...at(u,-1),...at(u,1),...at(v,-1),...at(u,1),...at(v,1),...at(v,-1))}}
const grassGeo=new T.BufferGeometry();grassGeo.setAttribute('position',new T.Float32BufferAttribute(verts,3));grassGeo.computeVertexNormals();const grassMat=new T.MeshStandardMaterial({color:0xc3b68a,roughness:1,side:T.DoubleSide});const windClock={value:0};grassMat.onBeforeCompile=shader=>{shader.uniforms.windClock=windClock;shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nuniform float windClock;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x+=sin(windClock*1.1+instanceMatrix[3].x*.6+instanceMatrix[3].z*.4)*position.y*position.y*.14;')};const grass=new T.InstancedMesh(grassGeo,grassMat,2200);const dummy=new T.Object3D();
for(let i=0;i<2200;i++){let x=rand()*85-47,z=(rand()<.5?-1:1)*(2.4+rand()*26);dummy.position.set(x,-.035,z);dummy.rotation.set(0,rand()*PI,.08*(rand()-.5));let scale=.35+rand()*.8;dummy.scale.set(scale,scale,scale);dummy.updateMatrix();grass.setMatrixAt(i,dummy.matrix);grass.setColorAt(i,new T.Color().setHSL(.10+rand()*.05,.16+rand()*.16,.33+rand()*.2))}scene.add(grass);
const flakeGeo=new T.BufferGeometry(),snowPoints=new Float32Array(350*3);for(let i=0;i<350;i++){snowPoints[3*i]=(rand()-.5)*35;snowPoints[3*i+1]=rand()*9;snowPoints[3*i+2]=(rand()-.5)*22}flakeGeo.setAttribute('position',new T.BufferAttribute(snowPoints,3));const flakeMaterial=new T.PointsMaterial({color:0xe5f4f5,size:.045,transparent:true,opacity:.45,depthWrite:false});flakeMaterial.onBeforeCompile=shader=>{shader.uniforms.windClock=windClock;shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nuniform float windClock;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x+=.16*sin(windClock*.7+position.y+position.z*.2);transformed.y=mod(position.y-windClock*.35+900.,9.);')};const flakes=new T.Points(flakeGeo,flakeMaterial);scene.add(flakes);
const asset=await new GLTFLoader().loadAsync('/mammoth.glb');const model=asset.scene;let triangleCount=0;model.traverse(o=>{if(o.isMesh)triangleCount+=o.geometry.index?o.geometry.index.count/3:o.geometry.attributes.position.count/3});
const clip=asset.animations.find(a=>a.name==='Idle_Experimental');if(!clip)throw Error('idle clip missing');
// Blender export begins at frame 1 (1/30 sec); subtract that leading offset
// so the end of the 72-frame cycle meets its beginning without a held frame.
const start=Math.min(...clip.tracks.map(track=>track.times[0]));for(const track of clip.tracks)track.times=Float32Array.from(track.times,t=>t-start);clip.resetDuration();
const PERIOD=clip.duration,STANCE=.75,STRIDE=.14,SCALE=2.45,SPEED=STRIDE*SCALE/(PERIOD*STANCE);
const shCanvas=document.createElement('canvas');shCanvas.width=shCanvas.height=128;const sh=shCanvas.getContext('2d');const grad=sh.createRadialGradient(64,64,5,64,64,64);grad.addColorStop(0,'rgba(20,29,30,.55)');grad.addColorStop(1,'rgba(20,29,30,0)');sh.fillStyle=grad;sh.fillRect(0,0,128,128);const shadowTex=new T.CanvasTexture(shCanvas);shadowTex.colorSpace=T.SRGBColorSpace;
function makeAnimal(x,z,phase,scale){const root=new T.Group(),obj=clone(model);obj.traverse(o=>{if(o.isMesh)o.castShadow=true});obj.scale.setScalar(scale);root.add(obj);scene.add(root);const mixer=new T.AnimationMixer(obj);mixer.clipAction(clip).play();const shadow=new T.Mesh(new T.PlaneGeometry(5.8,3.1),new T.MeshBasicMaterial({map:shadowTex,transparent:true,depthWrite:false,opacity:.65}));shadow.rotation.x=-PI/2;shadow.visible=false;scene.add(shadow);return{root,obj,mixer,x,z,phase,scale,shadow}}
const animals=[makeAnimal(0,0,0,SCALE)];
// Experimental, manually authored trunk performance. This is not motion capture.
const a=animals[0],head=a.obj.getObjectByName('head'),upper=a.obj.getObjectByName('trunk_upper'),lower=a.obj.getObjectByName('trunk_lower');if(!upper||!lower)throw Error('missing trunk bones');
const restHead=head?.quaternion.clone(),restUpper=upper.quaternion.clone(),restLower=lower.quaternion.clone();
let mesh;a.obj.traverse(o=>{if(o.isSkinnedMesh)mesh=o});const p=mesh.geometry.attributes.position,tipVertices=[];for(let i=0;i<p.count;i++){if(p.getX(i)<-.56&&p.getX(i)>-.72&&p.getY(i)<.10&&p.getZ(i)>.43&&p.getZ(i)<.58)tipVertices.push(i)}
function pose(t,up,low){a.root.position.set(0,.044*a.scale-.055,0);a.shadow.position.set(.05,-.049,.40*a.scale);if(head){head.quaternion.copy(restHead);head.rotateZ(.04*smooth((t-1)/2)*(1-smooth((t-5)/2)))}upper.quaternion.copy(restUpper);lower.quaternion.copy(restLower);upper.rotateZ(up);lower.rotateZ(low);scene.updateMatrixWorld(true)}
function tip(){let sum=new T.Vector3(),v=new T.Vector3();for(const i of tipVertices){v.fromBufferAttribute(p,i);mesh.applyBoneTransform(i,v);mesh.localToWorld(v);sum.add(v)}return sum.multiplyScalar(1/tipVertices.length)}
// One illustrative clump, deliberately positioned at the sampled trunk-tip
// contact point. The clump bends and springs back when the trunk withdraws;
// this is hand-authored motion, not a force, botanical or soft-body simulation.
const plant=new T.Group();scene.add(plant);const target=new T.Vector3(-1.944,-.055,1.334);
const geo=new T.BufferGeometry(),pv=[],indices=[];let sr=832;const rnd=()=>{sr=(Math.imul(sr,1664525)+1013904223)>>>0;return sr/4294967296};
for(let j=0;j<14;j++){let angle=rnd()*2*PI,lean=.08+rnd()*.11,height=.27+rnd()*.12,width=.016+rnd()*.014,offx=(rnd()-.5)*.075,offz=(rnd()-.5)*.075;let dx=Math.cos(angle),dz=Math.sin(angle),bx=-dz,bz=dx;let base=pv.length/3;for(let k=0;k<=4;k++){let v=k/4,shift=lean*v*v,w=width*(1-v);pv.push(offx+dx*shift-bx*w,height*v,offz+dz*shift-bz*w,offx+dx*shift+bx*w,height*v,offz+dz*shift+bz*w)}for(let k=0;k<4;k++){let n=base+2*k;indices.push(n,n+1,n+2,n+1,n+3,n+2)}}geo.setAttribute('position',new T.Float32BufferAttribute(pv,3));geo.setIndex(indices);geo.computeVertexNormals();plant.add(new T.Mesh(geo,new T.MeshStandardMaterial({color:0xa29557,roughness:1,side:T.DoubleSide})));
const cam=new T.PerspectiveCamera(39,W/H,.05,120);
function draw(t){t=Math.max(0,Math.min(12,t));windClock.value=t;let up=.2*smooth((t-1)/2)-.2*smooth((t-5)/2),low=.1*smooth((t-1)/2)-.9*smooth((t-5)/2)+.8*smooth((t-9.5)/2);pose(t,up,low);const contact=tip();let pressure=smooth((t-2.7)/.8)*(1-smooth((t-5)/.6));plant.position.copy(target);plant.rotation.z=.18*pressure+.04*Math.sin(t*1.3)*(1-pressure);
 let move=smooth((t-3.5)/4);cam.position.set(mix(-1.7,-.9,move),mix(1.8,2.5,move),mix(6.2,7.5,move));cam.lookAt(mix(-1.15,-.7,move),mix(.78,1.3,move),1.05);renderer.render(scene,cam);g.clearRect(0,0,W,H);g.drawImage(renderer.domElement,0,0);return {time:t,tip:contact.toArray(),tipVertices:tipVertices.length,up,low,plant:plant.position.toArray(),pressure}}

window.__probe=(t,up,lo)=>{pose(t,up,lo);return {tip:tip().toArray(),n:tipVertices.length,bones:[upper.name,lower.name],upper:upper.getWorldPosition(new T.Vector3()).toArray(),lower:lower.getWorldPosition(new T.Vector3()).toArray()}};
window.__contactProbe=t=>{draw(t);scene.updateMatrixWorld(true);const blade=plant.children[0],gp=blade.geometry.attributes.position;let closest=Infinity;const v=new T.Vector3(),w=new T.Vector3();for(const i of tipVertices){v.fromBufferAttribute(p,i);mesh.applyBoneTransform(i,v);mesh.localToWorld(v);for(let j=0;j<gp.count;j++){w.fromBufferAttribute(gp,j);blade.localToWorld(w);closest=Math.min(closest,v.distanceTo(w))}}return {time:t,closestVertexDistance:closest}};
window.__seek=draw;window.__ready=true;draw(0);
