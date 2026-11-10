// Experimental illustrative Arctic coast; not a historical shoreline reconstruction or finished film.
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
function shoreOffset(x){return .6*Math.sin(x*.20)+.35*Math.sin(x*.43)}
function groundHeight(x,z){let margin=smooth((Math.abs(z)-5)/7);return margin*(.42*Math.sin(x*.17)*Math.cos(z*.13)+.24*Math.sin(x*.29+z*.21))-.055-3*smooth((-z-2+shoreOffset(x))/8)}
for(let i=0;i<pos.count;i++){let x=pos.getX(i),z=pos.getZ(i);pos.setY(i,groundHeight(x,z));let n=.93+.07*Math.sin(x*.29+z*.16);colors.push(n,n,n)}
groundGeo.setAttribute('color',new T.Float32BufferAttribute(colors,3));groundGeo.computeVertexNormals();const ground=new T.Mesh(groundGeo,snow);ground.receiveShadow=true;scene.add(ground);
// Animated sea is a continuous mesh; the coastline is imaginary and must not
// be read as a geographic or sea-level reconstruction of ancient Wrangel.
const seaClock={value:0};const waterGeo=new T.PlaneGeometry(500,500,250,200);waterGeo.rotateX(-PI/2);
const waterMat=new T.ShaderMaterial({uniforms:{time:seaClock},vertexShader:`uniform float time;varying vec3 localPos;varying float ripple;void main(){vec3 p=position;float wave=sin(p.x*.31+p.z*.42+time*.8)*.045+sin(p.x*.6-p.z*.3+time*.58)*.024;wave*=1.-smoothstep(55.,150.,250.-p.z);p.y+=wave;localPos=p;ripple=wave;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,fragmentShader:`varying vec3 localPos;varying float ripple;uniform float time;void main(){float signal=sin(localPos.x*1.43+sin(localPos.z*.31+time*.11)+time*.45)*sin(localPos.z*.77+localPos.x*.22-time*.35);float fleck=pow(max(0.,signal),14.);vec3 base=mix(vec3(.10,.23,.29),vec3(.30,.44,.47),clamp((ripple+.07)*4.,0.,1.));base+=fleck*.13*(1.-smoothstep(55.,150.,250.-localPos.z));float haze=smoothstep(20.,135.,250.-localPos.z);base=mix(base,vec3(.55,.62,.60),haze*.9);gl_FragColor=vec4(base,1.);}`});
const ocean=new T.Mesh(waterGeo,waterMat);ocean.position.set(0,-.45,-252);scene.add(ocean);
// Open horizon: no implied historically exact mainland or distant landmass.
// Low tufts use intersecting tapered blades, each individually coloured.
const verts=[];for(let j=0;j<5;j++){const a=j*PI/5,dx=Math.cos(a),dz=Math.sin(a),bend=(j%2?.13:-.13),height=.33+j*.045;const at=(v,side)=>[dx*side*.025*(1-v)+bend*v*v,height*v,dz*side*.025*(1-v)+bend*.3*v*v];for(let k=0;k<3;k++){const u=k/3,v=(k+1)/3;verts.push(...at(u,-1),...at(u,1),...at(v,-1),...at(u,1),...at(v,1),...at(v,-1))}}
const grassGeo=new T.BufferGeometry();grassGeo.setAttribute('position',new T.Float32BufferAttribute(verts,3));grassGeo.computeVertexNormals();const grassMat=new T.MeshStandardMaterial({color:0xc3b68a,roughness:1,side:T.DoubleSide});const windClock={value:0};grassMat.onBeforeCompile=shader=>{shader.uniforms.windClock=windClock;shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nuniform float windClock;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x+=sin(windClock*1.1+instanceMatrix[3].x*.6+instanceMatrix[3].z*.4)*position.y*position.y*.14;')};const grass=new T.InstancedMesh(grassGeo,grassMat,2200);const dummy=new T.Object3D();
for(let i=0;i<2200;i++){let x=rand()*85-47,z=-1.5+rand()*28;dummy.position.set(x,groundHeight(x,z)+.02,z);dummy.rotation.set(0,rand()*PI,.08*(rand()-.5));let scale=.35+rand()*.8;dummy.scale.set(scale,scale,scale);dummy.updateMatrix();grass.setMatrixAt(i,dummy.matrix);grass.setColorAt(i,new T.Color().setHSL(.10+rand()*.05,.16+rand()*.16,.33+rand()*.2))}scene.add(grass);
// Irregular coastal stones are instanced geometry and partly submerged.
const stones=new T.InstancedMesh(new T.DodecahedronGeometry(1,1),new T.MeshStandardMaterial({color:0x6f7771,roughness:1}),90);stones.castShadow=true;
for(let i=0;i<90;i++){let x=rand()*75-40,z=-2.4-rand()*2.4+shoreOffset(x);let size=.08+rand()*.28;dummy.position.set(x,groundHeight(x,z)+size*.26,z);dummy.rotation.set(rand(),rand()*PI,rand());dummy.scale.set(size*(.7+rand()),size*(.35+rand()*.4),size*(.7+rand()));dummy.updateMatrix();stones.setMatrixAt(i,dummy.matrix);stones.setColorAt(i,new T.Color().setHSL(.12,.08,.25+rand()*.18))}scene.add(stones);
const flakeGeo=new T.BufferGeometry(),snowPoints=new Float32Array(350*3);for(let i=0;i<350;i++){snowPoints[3*i]=(rand()-.5)*35;snowPoints[3*i+1]=rand()*9;snowPoints[3*i+2]=(rand()-.5)*22}flakeGeo.setAttribute('position',new T.BufferAttribute(snowPoints,3));const flakeMaterial=new T.PointsMaterial({color:0xe5f4f5,size:.045,transparent:true,opacity:.45,depthWrite:false});flakeMaterial.onBeforeCompile=shader=>{shader.uniforms.windClock=windClock;shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nuniform float windClock;').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x+=.16*sin(windClock*.7+position.y+position.z*.2);transformed.y=mod(position.y-windClock*.35+900.,9.);')};const flakes=new T.Points(flakeGeo,flakeMaterial);scene.add(flakes);
const asset=await new GLTFLoader().loadAsync('/mammoth.glb');const model=asset.scene;let triangleCount=0;model.traverse(o=>{if(o.isMesh)triangleCount+=o.geometry.index?o.geometry.index.count/3:o.geometry.attributes.position.count/3});
const clip=asset.animations.find(a=>a.name==='WalkInPlace_Experimental');if(!clip)throw Error('walk clip missing');
// Blender export begins at frame 1 (1/30 sec); subtract that leading offset
// so the end of the 72-frame cycle meets its beginning without a held frame.
const start=Math.min(...clip.tracks.map(track=>track.times[0]));for(const track of clip.tracks)track.times=Float32Array.from(track.times,t=>t-start);clip.resetDuration();
const PERIOD=clip.duration,STANCE=.75,STRIDE=.14,SCALE=2.45,SPEED=STRIDE*SCALE/(PERIOD*STANCE);
const shCanvas=document.createElement('canvas');shCanvas.width=shCanvas.height=128;const sh=shCanvas.getContext('2d');const grad=sh.createRadialGradient(64,64,5,64,64,64);grad.addColorStop(0,'rgba(20,29,30,.55)');grad.addColorStop(1,'rgba(20,29,30,0)');sh.fillStyle=grad;sh.fillRect(0,0,128,128);const shadowTex=new T.CanvasTexture(shCanvas);shadowTex.colorSpace=T.SRGBColorSpace;
function makeAnimal(x,z,phase,scale){const root=new T.Group(),obj=clone(model);obj.traverse(o=>{if(o.isMesh)o.castShadow=true});obj.scale.setScalar(scale);root.add(obj);scene.add(root);const mixer=new T.AnimationMixer(obj);mixer.clipAction(clip).play();const shadow=new T.Mesh(new T.PlaneGeometry(5.8,3.1),new T.MeshBasicMaterial({map:shadowTex,transparent:true,depthWrite:false,opacity:.65}));shadow.rotation.x=-PI/2;shadow.visible=false;scene.add(shadow);return{root,obj,mixer,x,z,phase,scale,shadow}}
const animals=[makeAnimal(2,1,0,SCALE),makeAnimal(7,3.4,.33,2.25),makeAnimal(10.6,.1,.64,2.15)];
// Approximate depressions placed where each contact begins on the flat strip.
// They are dark shallow disks rather than claimed snow-deformation physics.
const marks=[];const foot=[[-.206,-.325],[-.203,-.544],[.498,-.213],[.427,-.441]],offset=[.25,.75,0,.5];
let printGeo=new T.CircleGeometry(1,18);printGeo.rotateX(-PI/2);const printMat=new T.MeshBasicMaterial({color:0x728f96,transparent:true,opacity:.22,depthWrite:false});
for(const animal of animals.slice(0,1)){for(let i=0;i<4;i++){for(let cycle=-1;cycle<16;cycle++){const contact=(cycle-offset[i])*PERIOD;if(contact<0||contact>31)continue;const px=animal.x-SPEED*contact+(foot[i][0]-STRIDE/2)*animal.scale;const pz=animal.z-foot[i][1]*animal.scale;const mark=new T.Mesh(printGeo,printMat);mark.position.set(px,-.051,pz);mark.scale.set(.20,1,.17);scene.add(mark);marks.push({mark,contact})}}}
const cameras=Array.from({length:3},()=>new T.PerspectiveCamera(39,W/H,.05,220));const temp=new T.Vector3();
function cameraAt(index,t){let p=animals[0].root.position;let c=cameras[index];
 if(index===0){c.fov=38;c.position.set(p.x-3,3.2,p.z+9);temp.set(p.x+1,1.4,p.z-2.0)}
 else if(index===1){c.fov=38;c.position.set(p.x-6,5.1,p.z+15);temp.set(p.x+2.5,1.2,p.z-3.0)}
 else{c.fov=38;c.position.set(p.x+7,2.9,p.z+11);temp.set(p.x+2,1.25,p.z-3.0)}
 c.updateProjectionMatrix();c.lookAt(temp);return c;
}
function draw(t){t=Math.max(0,Math.min(30,t));windClock.value=t;seaClock.value=t;for(let a of animals){a.root.position.set(a.x-STRIDE*a.scale/(PERIOD*STANCE)*t,.044*a.scale-.055,a.z);a.mixer.setTime(t+a.phase*PERIOD);a.shadow.position.set(a.root.position.x+.05,-.049,a.root.position.z+.40*a.scale);a.shadow.scale.setScalar(a.scale/SCALE)}
 for(const {mark,contact} of marks)mark.visible=t>=contact;
 flakes.position.set(-SPEED*t*.12,0,0);flakes.rotation.y=.015*Math.sin(t*.2);
 // Two motivated scale changes: weight/contact -> animal -> herd/place.
 let i=t<6?0:t<13?1:2;let boundary=i===1?6:i===2?13:-1;let alpha=boundary<0?1:smooth((t-boundary)/.7);
 const c=cameraAt(i,t);g.clearRect(0,0,W,H);
 if(alpha<1){renderer.render(scene,cameraAt(i-1,t));g.drawImage(renderer.domElement,0,0);renderer.render(scene,c);g.globalAlpha=alpha;g.drawImage(renderer.domElement,0,0);g.globalAlpha=1}else{renderer.render(scene,c);g.drawImage(renderer.domElement,0,0)}
 g.fillStyle='rgba(242,247,240,.92)';g.shadowColor='rgba(15,30,33,.8)';g.shadowBlur=6;g.font='700 14px sans-serif';g.textAlign='left';g.fillText('WRANGEL ISLAND · ILLUSTRATIVE LANDSCAPE',28,690);g.shadowBlur=0;return {time:t,shot:['animal and coast','herd and shore','shoreline view'][i],triangles:triangleCount,animals:animals.length,marks:marks.filter(m=>m.mark.visible).length,clip_duration:clip.duration,historical_geography:false};
}
// Development probe: measures deformed mesh vertices, not just bone targets.
// Sample near-flat sole vertices, grouped by nearest source foot position.
const skinned=[];animals[0].obj.traverse(o=>{if(o.isSkinnedMesh)skinned.push(o)});
const probes=foot.map(()=>[]);for(const mesh of skinned){const p=mesh.geometry.attributes.position;for(let v=0;v<p.count;v++){const x=p.getX(v),y=p.getY(v),z=p.getZ(v);if(y>-.025)continue;let k=0,best=Infinity;for(let i=0;i<foot.length;i++){let d=(x-foot[i][0])**2+(z+foot[i][1])**2;if(d<best){best=d;k=i}}if(best<.11*.11)probes[k].push({mesh,index:v,base:new T.Vector3(x,y,z)})}}
window.__gaitProbe=(t)=>{draw(t);scene.updateMatrixWorld(true);return probes.map(points=>{let out=new T.Vector3(),minY=Infinity,maxY=-Infinity;for(const {mesh,index,base} of points){const p=base.clone();mesh.applyBoneTransform(index,p);mesh.localToWorld(p);out.add(p);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y)}if(points.length)out.multiplyScalar(1/points.length);return {count:points.length,xyz:out.toArray(),minY,maxY}})};
window.__shoreProbe=t=>{const x=0,z=200;let fade=smooth((150-(250-z))/(150-55));let wave=(Math.sin(x*.31+z*.42+t*.8)*.045+Math.sin(x*.6-z*.3+t*.58)*.024)*fade;return {time:t,sampledWaterY:-.45+wave,waterMaximumY:-.381,leadGroundY:groundHeight(animals[0].x,animals[0].z)}};
window.__seek=draw;window.__ready=true;draw(0);
