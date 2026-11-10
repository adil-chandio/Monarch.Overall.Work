// Compressed-time illustrative rain-on-snow mechanism, not evidence of a Wrangel event.
import * as T from 'three';
import {GLTFLoader} from '/GLTFLoader.js';
const W=1280,H=720,PI=Math.PI;
await document.fonts.load('700 14px Manrope');
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(1);renderer.setSize(W,H);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=.92;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const ctx=canvas.getContext('2d');
const scene=new T.Scene();scene.background=new T.Color(0x899ca1);scene.fog=new T.Fog(0x9dacaf,3,9);
// Overcast sky is shader geometry; no photographic plate.
const sky=new T.Mesh(new T.SphereGeometry(25,48,24),new T.ShaderMaterial({side:T.BackSide,depthWrite:false,vertexShader:`varying vec3 v;void main(){v=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,fragmentShader:`varying vec3 v;void main(){float h=clamp(v.y,0.,1.);float cloud=sin(v.x*19.+v.y*13.)*sin(v.z*16.-v.y*11.);vec3 col=mix(vec3(.69,.73,.70),vec3(.32,.42,.46),smoothstep(0.,.8,h));col+=cloud*.025*smoothstep(.03,.32,h);gl_FragColor=vec4(col,1.);}`}));scene.add(sky);
scene.add(new T.HemisphereLight(0xcadfe6,0x3a4342,1.6));const key=new T.DirectionalLight(0xe5e8dc,2.5);key.position.set(-3,5,3);key.castShadow=true;key.shadow.mapSize.set(1024,1024);key.shadow.camera.left=-4;key.shadow.camera.right=4;key.shadow.camera.top=4;key.shadow.camera.bottom=-4;key.shadow.bias=-.0002;scene.add(key);const rim=new T.DirectionalLight(0xa6d7e0,1.4);rim.position.set(4,3,-3);scene.add(rim);
let seed=761225;function rand(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296}const clamp=T.MathUtils.clamp,mix=T.MathUtils.lerp;const smooth=x=>{x=clamp(x,0,1);return x*x*(3-2*x)};
function height(x,z){return .032*Math.sin(x*2.3+Math.sin(z*1.1))+.018*Math.cos(z*3.1-x*.7)+.008*Math.sin(x*7+z*5)}
// Granular snow texture on a displaced geometry, not an image plate.
const tc=document.createElement('canvas');tc.width=tc.height=512;let x=tc.getContext('2d');x.fillStyle='#cbd5d1';x.fillRect(0,0,512,512);
for(let i=0;i<35000;i++){let white=rand()>.54;x.fillStyle=white?`rgba(252,255,247,${.06+rand()*.16})`:`rgba(74,100,103,${.025+rand()*.07})`;let a=rand()*512,b=rand()*512,s=.4+rand()*2.1;x.fillRect(a,b,s,s)}
const tex=new T.CanvasTexture(tc);tex.colorSpace=T.SRGBColorSpace;tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.repeat.set(4,4);
const loader=new T.TextureLoader();const [snowAlbedo,snowNormal,snowRough]=await Promise.all(['/SnowColor.jpg','/SnowNormal.jpg','/SnowRough.jpg'].map(u=>loader.loadAsync(u)));for(const m of [snowAlbedo,snowNormal,snowRough]){m.wrapS=m.wrapT=T.RepeatWrapping;m.repeat.set(15,15)}snowAlbedo.colorSpace=T.SRGBColorSpace;
const groundGeo=new T.PlaneGeometry(15,15,130,130);groundGeo.rotateX(-PI/2);let gp=groundGeo.attributes.position;for(let i=0;i<gp.count;i++)gp.setY(i,height(gp.getX(i),gp.getZ(i)));groundGeo.computeVertexNormals();
const ground=new T.Mesh(groundGeo,new T.MeshStandardMaterial({map:snowAlbedo,normalMap:snowNormal,normalScale:new T.Vector2(.45,.45),roughnessMap:snowRough,color:0xe5e9e1,roughness:1}));ground.receiveShadow=true;scene.add(ground);
// Small uneven snow aggregates are geometry, locally embedded in the surface.
const grains=new T.InstancedMesh(new T.IcosahedronGeometry(1,0),new T.MeshStandardMaterial({color:0xd9e8e5,roughness:.85}),3000);let dmy=new T.Object3D();for(let i=0;i<3000;i++){let gx=(rand()-.5)*7,gz=(rand()-.5)*7,size=.004+rand()*.009;dmy.position.set(gx,height(gx,gz)+size*.15,gz);dmy.scale.set(size*(.6+rand()),size*.28,size*(.6+rand()));dmy.rotation.y=rand()*PI;dmy.updateMatrix();grains.setMatrixAt(i,dmy.matrix)}scene.add(grains);
// Separate slightly raised, translucent surface: animated suggestive glaze, not fluid simulation.
const iceGeo=groundGeo.clone(),ip=iceGeo.attributes.position;for(let i=0;i<ip.count;i++)ip.setY(i,ip.getY(i)+.014);iceGeo.computeVertexNormals();
const iceMat=new T.MeshPhysicalMaterial({color:0xa9d4dc,transparent:true,opacity:0,roughness:.14,metalness:.02,clearcoat:1,clearcoatRoughness:.05,depthWrite:false});const glaze=new T.Mesh(iceGeo,iceMat);scene.add(glaze);
// Twigs and blades grow from the snow. Ice is a widening clear shell around each blade;
// it is an artistic, time-compressed explanation rather than observed plant anatomy.
const stemMat=new T.MeshStandardMaterial({color:0x93865e,roughness:.95,side:T.DoubleSide});
const frostMat=new T.MeshPhysicalMaterial({color:0xb7e4e8,roughness:.15,metalness:0,transparent:true,opacity:0,clearcoat:1,clearcoatRoughness:.05,depthWrite:false});
const stalks=[];function stem(px,pz,h,lean,thick){const pivot=new T.Group();pivot.position.set(px,height(px,pz)-.01,pz);scene.add(pivot);
 const dir=rand()*PI*2,dx=Math.cos(dir),dz=Math.sin(dir);const points=[new T.Vector3(0,0,0),new T.Vector3(dx*lean*.20,h*.30,dz*lean*.20),new T.Vector3(dx*lean*.66,h*.72,dz*lean*.66),new T.Vector3(dx*lean,h,dz*lean)];const curve=new T.CatmullRomCurve3(points);
 const verts=[],inds=[];for(let k=0;k<=12;k++){let v=k/12,q=curve.getPoint(v),w=thick*(2.5*(1-v)+.02);verts.push(q.x-dz*w,q.y,q.z+dx*w,q.x+dz*w,q.y,q.z-dx*w);if(k<12){let n=2*k;inds.push(n,n+1,n+2,n+1,n+3,n+2)}}const bladeGeo=new T.BufferGeometry();bladeGeo.setAttribute('position',new T.Float32BufferAttribute(verts,3));bladeGeo.setIndex(inds);bladeGeo.computeVertexNormals();const blade=new T.Mesh(bladeGeo,stemMat);blade.castShadow=true;pivot.add(blade);
 const iceGeo=new T.TubeGeometry(curve,10,thick*1.25,7,false),pos=iceGeo.attributes.position;for(let i=0;i<=10;i++){const v=i/10,c=curve.getPointAt(v),n=(1-v*.96);for(let j=0;j<=7;j++){let k=i*8+j;pos.setXYZ(k,c.x+(pos.getX(k)-c.x)*n,c.y+(pos.getY(k)-c.y)*n,c.z+(pos.getZ(k)-c.z)*n)}}iceGeo.computeVertexNormals();const ice=new T.Mesh(iceGeo,frostMat);pivot.add(ice);
 stalks.push({pivot,ice,phase:rand()*PI*2,h,px,pz});}
// Main clump central foreground plus low background vegetation.
for(let i=0;i<8;i++){let a=rand()*PI*2,r=Math.sqrt(rand())*.30;stem(Math.cos(a)*r,Math.sin(a)*r,.16+rand()*.25,.09+rand()*.22,.003+rand()*.002)}
for(let i=0;i<80;i++){let a=rand()*PI*2,r=.9+rand()*5;stem(Math.cos(a)*r,Math.sin(a)*r,.12+rand()*.32,.06+rand()*.12,.004+rand()*.003)}
// Background cover uses a simplified 3D Poly Haven grass derivative; per-plant
// swaying is kinematic and these plants are not evidence of historic flora.
const grassAsset=await new GLTFLoader().loadAsync('/grass.glb');const extras=[], grassIce={value:0};
for(let i=0;i<11;i++){let a=rand()*PI*2,r=.8+rand()*3,px=i===0?0:Math.cos(a)*r,pz=i===0?0:Math.sin(a)*r;const group=grassAsset.scene.clone(true);group.position.set(px,height(px,pz)-.018,pz);group.rotation.y=rand()*PI*2;group.scale.setScalar(i===0?3.0:.75+rand()*1.3);group.traverse(o=>{if(o.isMesh){o.material=o.material.clone();o.material.color.set(0xe3dcc2);o.material.emissive.set(0xa39b75);o.material.emissiveMap=o.material.map;o.material.emissiveIntensity=.6;o.material.alphaTest=.3;o.material.transparent=false;o.material.side=T.DoubleSide;o.material.onBeforeCompile=shader=>{shader.uniforms.grassIce=grassIce;shader.fragmentShader=shader.fragmentShader.replace('#include <common>','#include <common>\nuniform float grassIce;').replace('#include <color_fragment>','#include <color_fragment>\ndiffuseColor.rgb=mix(diffuseColor.rgb,vec3(.53,.68,.69),grassIce*.72);')}}});scene.add(group);extras.push({group,phase:rand()*PI*2})}
// Snow-covered stones embedded at ground height.
const rockMat=new T.MeshStandardMaterial({color:0x778987,roughness:.95});for(let i=0;i<33;i++){let a=rand()*PI*2,r=1.1+rand()*5.5,px=Math.cos(a)*r,pz=Math.sin(a)*r,size=.035+rand()*.13;let o=new T.Mesh(new T.IcosahedronGeometry(1,1),rockMat);o.position.set(px,height(px,pz)+size*.14,pz);o.scale.set(size,size*(.3+rand()*.3),size*(.8+rand()));o.rotation.y=rand()*PI;scene.add(o)}
// Rain segments follow analytic trajectories and stop at the snow. Drops and splash
// rings are synchronized by shared phase; impact is kinematic and not fluid dynamics.
const N=260,rainData=[];const rainPos=new Float32Array(N*6),rainGeo=new T.BufferGeometry();rainGeo.setAttribute('position',new T.BufferAttribute(rainPos,3));const rainMat=new T.LineBasicMaterial({color:0xd9eff0,transparent:true,opacity:0,depthWrite:false});const rain=new T.LineSegments(rainGeo,rainMat);scene.add(rain);
for(let i=0;i<N;i++)rainData.push({x:(rand()-.5)*8,z:(rand()-.5)*7,phase:rand(),speed:.85+rand()*.4});
const rippleMat=new T.MeshBasicMaterial({color:0xc7e7e8,transparent:true,opacity:0,side:T.DoubleSide,depthWrite:false});const ripples=[];
for(let i=0;i<18;i++){let o=new T.Mesh(new T.RingGeometry(.028,.036,24),rippleMat.clone());o.rotation.x=-PI/2;scene.add(o);ripples.push(o)}
// Thin, shallow crack-like ribbons reveal after icing. These are not measured fractures.
const crackGeo=new T.BufferGeometry(),cr=[];for(let j=0;j<9;j++){let px=(rand()-.5)*2,pz=(rand()-.5)*2,a=rand()*PI*2;for(let k=0;k<5;k++){let nx=px+Math.cos(a)*(.10+rand()*.13),nz=pz+Math.sin(a)*(.10+rand()*.13);cr.push(px,height(px,pz)+.022,pz,nx,height(nx,nz)+.022,nz);px=nx;pz=nz;a+=(rand()-.5)*.9}}
crackGeo.setAttribute('position',new T.Float32BufferAttribute(cr,3));const crackMat=new T.LineBasicMaterial({color:0xe3f5f4,transparent:true,opacity:0,depthWrite:false});scene.add(new T.LineSegments(crackGeo,crackMat));
const cam=new T.PerspectiveCamera(38,W/H,.03,35);let tmp=new T.Vector3();
function draw(t){t=clamp(t,0,14);let rainIn=smooth((t-.8)/1.2),rainOut=1-smooth((t-6.6)/2),rainStrength=rainIn*rainOut,freeze=smooth((t-5.2)/4.2),move=smooth(t/14);
 for(let e of extras)e.group.rotation.z=.015*Math.sin(t*1.2+e.phase)*(1-freeze*.7);
 for(let s of stalks){s.pivot.rotation.z=.035*Math.sin(t*1.7+s.phase)*(1-freeze*.72)+rainStrength*.025; s.pivot.rotation.x=.022*Math.sin(t*1.3+s.phase*1.3)*(1-freeze*.72);}
 grassIce.value=freeze;iceMat.opacity=.34*freeze;frostMat.opacity=.40*freeze;crackMat.opacity=.32*freeze;rainMat.opacity=.48*rainStrength;
 for(let i=0;i<N;i++){const d=rainData[i],cycle=(t*d.speed+d.phase)%1,groundY=height(d.x,d.z)+.025,y=groundY+(1-cycle)*3.8;const p=i*6;rainPos[p]=d.x-.10*(1-cycle);rainPos[p+1]=y;rainPos[p+2]=d.z;rainPos[p+3]=d.x-.10*(1-cycle)-.016;rainPos[p+4]=Math.max(groundY,y-.20);rainPos[p+5]=d.z;}
 rainGeo.attributes.position.needsUpdate=true;
 for(let i=0;i<ripples.length;i++){let d=rainData[i],f=(t*d.speed+d.phase)%1,age=f<.15?f/.15:1,o=ripples[i];o.position.set(d.x,height(d.x,d.z)+.025,d.z);o.scale.setScalar(.25+age*2);o.material.opacity=rainStrength*.4*(1-age)}
 cam.position.set(mix(1.05,.76,move),mix(.68,.62,move),mix(1.85,1.42,move));tmp.set(mix(.05,0,move),mix(.30,.28,move),0);cam.lookAt(tmp);
 renderer.render(scene,cam);ctx.clearRect(0,0,W,H);ctx.drawImage(renderer.domElement,0,0);
 ctx.fillStyle='rgba(239,246,241,.92)';ctx.shadowColor='rgba(18,34,38,.9)';ctx.shadowBlur=6;ctx.font='700 16px Manrope';ctx.textAlign='left';ctx.fillText('POSSIBLE ICING EVENT · ILLUSTRATIVE, TIME COMPRESSED',30,690);ctx.shadowBlur=0;
 return {time:t,rainStrength,freeze,stalks:stalks.length,iceOpacity:iceMat.opacity,claim:'hypothesis-not-observed'};
}
window.__seek=draw;window.__ready=true;draw(0);
