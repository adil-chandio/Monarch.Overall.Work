// Generic evidence excavation, not footage or a reconstruction of a specific find.
import * as T from 'three';
import {GLTFLoader} from '/GLTFLoader.js';
const W=1280,H=720,PI=Math.PI;await document.fonts.load('700 14px Manrope');
const r=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});r.setSize(W,H);r.setPixelRatio(1);r.shadowMap.enabled=true;r.shadowMap.type=T.PCFSoftShadowMap;r.outputColorSpace=T.SRGBColorSpace;r.toneMapping=T.ACESFilmicToneMapping;r.toneMappingExposure=1.05;
const out=document.createElement('canvas');out.id='final';out.width=W;out.height=H;document.body.appendChild(out);const ctx=out.getContext('2d');
const scene=new T.Scene();scene.background=new T.Color(0x8c9999);scene.fog=new T.Fog(0x8c9999,4.5,15);scene.add(new T.HemisphereLight(0xd4e4e4,0x57473b,2.1));const sun=new T.DirectionalLight(0xffe8c8,1.8);sun.position.set(-3,5,4);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-3;sun.shadow.camera.right=3;sun.shadow.camera.top=3;sun.shadow.camera.bottom=-3;sun.shadow.bias=-.00015;sun.shadow.normalBias=.001;scene.add(sun);
let seed=91631;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296},clamp=T.MathUtils.clamp,mix=T.MathUtils.lerp,sm=u=>{u=clamp(u,0,1);return u*u*(3-2*u)};
const loader=new T.TextureLoader();const [soilCol,soilNormal,soilRough]=await Promise.all(['/earth-color.jpg','/earth-normal.jpg','/earth-rough.jpg'].map(p=>loader.loadAsync(p)));for(const t of [soilCol,soilNormal,soilRough]){t.wrapS=t.wrapT=T.RepeatWrapping;t.repeat.set(6,6)}soilCol.colorSpace=T.SRGBColorSpace;
const progress={value:0};
const geo=new T.PlaneGeometry(12,12,240,240);geo.rotateX(-PI/2);const terrain=geo.attributes.position;for(let i=0;i<terrain.count;i++){let x=terrain.getX(i),z=terrain.getZ(i);let y=.012*Math.sin(x*3+z*4)+.008*Math.sin(x*11-z*7)+.004*Math.cos(z*18+x*6);terrain.setY(i,y)}geo.computeVertexNormals();
const dirt=new T.MeshStandardMaterial({map:soilCol,normalMap:soilNormal,normalScale:new T.Vector2(.36,.36),roughnessMap:soilRough,roughness:1,color:0xb4ada0});
dirt.onBeforeCompile=shader=>{shader.uniforms.progress=progress;shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nuniform float progress;').replace('#include <begin_vertex>',`#include <begin_vertex>
float front=mix(-.72,.72,progress);float swept=(1.-smoothstep(front-.13,front+.07,position.x))*smoothstep(-.86,-.68,position.x)*(1.-smoothstep(.68,.86,position.x));float trench=1.-smoothstep(.11,.34,abs(position.z));transformed.y-=.24*swept*trench*smoothstep(0.,.02,progress);`)};
const ground=new T.Mesh(geo,dirt);ground.receiveShadow=true;scene.add(ground);
// A generated dirt-stained material for the selected reference-mesh component.
// The setting is invented; it is not an identified Wrangel specimen.
const bc=document.createElement('canvas');bc.width=bc.height=512;let bg=bc.getContext('2d');bg.fillStyle='#a59176';bg.fillRect(0,0,512,512);for(let i=0;i<24000;i++){let a=rand(),x=rand()*512,y=rand()*512;bg.fillStyle=a>.45?`rgba(225,211,178,${.05+rand()*.12})`:`rgba(49,39,30,${.04+rand()*.12})`;bg.fillRect(x,y,1+rand()*8,1+rand()*3)}for(let i=0;i<130;i++){bg.strokeStyle=`rgba(60,45,35,${.03+rand()*.12})`;bg.lineWidth=.5+rand()*1.5;bg.beginPath();let x=rand()*512,y=rand()*512;bg.moveTo(x,y);bg.lineTo(x+rand()*30,y+(rand()-.5)*3);bg.stroke()}
const boneTex=new T.CanvasTexture(bc);boneTex.colorSpace=T.SRGBColorSpace;boneTex.wrapS=boneTex.wrapT=T.RepeatWrapping;boneTex.repeat.set(1,1);
// Candidate shape derived from a component of the third-party skeleton mesh.
// This is not the actual excavated sample or an authenticated historical find.
const boneAsset=await new GLTFLoader().loadAsync('/fragment.glb');const bone=boneAsset.scene;bone.scale.setScalar(.7);bone.rotation.z=-PI/2;bone.position.y=-.205;bone.traverse(o=>{if(o.isMesh){o.geometry.computeVertexNormals();o.material=new T.MeshStandardMaterial({map:boneTex,color:0xd6cbb9,roughness:.92,side:T.DoubleSide});o.castShadow=true;o.receiveShadow=true}});scene.add(bone);
// Small stones set partly into the terrain, never sourced to a real excavation.
const stoneMat=new T.MeshStandardMaterial({color:0x665c50,roughness:.95});for(let i=0;i<85;i++){let x=(rand()-.5)*4,z=(rand()-.5)*4;if(Math.abs(x)<1.3&&Math.abs(z)<.45)continue;let size=.008+rand()*.045,o=new T.Mesh(new T.IcosahedronGeometry(1,1),stoneMat);o.position.set(x,size*.12,z);o.scale.set(size,size*.4,size*(.7+rand()*.6));o.rotation.set(rand(),rand()*PI,rand());o.castShadow=true;scene.add(o)}
const tool=new T.Group();scene.add(tool);const wood=new T.MeshStandardMaterial({color:0x7d5b40,roughness:.8}), metal=new T.MeshStandardMaterial({color:0x8f9890,metalness:.55,roughness:.37}),hair=new T.MeshStandardMaterial({color:0xc2ac83,roughness:.95});
function rod(parent,a,b,r1,r2,mat){let v=new T.Vector3(...a),w=new T.Vector3(...b),delta=w.clone().sub(v);const obj=new T.Mesh(new T.CylinderGeometry(r1,r2,delta.length(),12),mat);obj.position.copy(v).add(w).multiplyScalar(.5);obj.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),delta.normalize());obj.castShadow=true;parent.add(obj);return obj}
// Brush is a kinematic tool, with bundled 3D bristles whose lower tips approach
// the surface. It does not simulate a hand's grip or an actual technique.
const block=new T.Mesh(new T.BoxGeometry(.18,.07,.08),wood);block.position.y=.22;block.castShadow=true;tool.add(block);rod(tool,[0,.25,0],[0,.94,0],.045,.045,wood);rod(tool,[0,.25,0],[0,.31,0],.052,.052,metal);
for(let i=0;i<70;i++){let px=(rand()-.5)*.17,pz=(rand()-.5)*.07;rod(tool,[px,.18,pz],[px+.018,.035+rand()*.02,pz],.004,.0025,hair)}
const handData=await new GLTFLoader().loadAsync('/glove.glb');const hand=handData.scene;hand.scale.setScalar(.20);hand.rotation.x=-PI/2;hand.position.set(-.035,.77,.12);tool.add(hand);
for(const chain of [['Index_Finger','Lower001','Middle001','Top001'],['Middle_Finger','Lower002','Middle002','Top002'],['Ring_Finger','Lower003','Middle003','Top003'],['Pinky','Lower004','Middle004','Top004']]){[15,35,35,15].forEach((d,i)=>{const b=hand.getObjectByName(chain[i]);if(b)b.rotateX(T.MathUtils.degToRad(d))})}
const th=hand.getObjectByName('Thumb');if(th){th.rotateX(T.MathUtils.degToRad(20));th.rotateY(T.MathUtils.degToRad(20));th.rotateZ(T.MathUtils.degToRad(50))}for(const [n,d] of [['Middle',30],['Top',11.5]]){let b=hand.getObjectByName(n);if(b)b.rotateX(T.MathUtils.degToRad(d))}
hand.traverse(o=>{if(o.isMesh){o.frustumCulled=false;let mats=Array.isArray(o.material)?o.material:[o.material];o.material=mats.map(m=>{let c=m.clone();c.color.set(m.name==='Glove'?0x8b9d91:0x9b988a);c.roughness=.85;c.metalness=0;return c});if(o.material.length===1)o.material=o.material[0]}});
rod(tool,[.0,1.05,.03],[.34,2.05,.25],.13,.15,new T.MeshStandardMaterial({color:0x787c6f,roughness:1}));
// Small dislodged particles drift and settle behind the brush; hand animation,
// particle transport and contact are approximations, not validated physics.
const pcount=140,pg=new T.BufferGeometry(),pa=new Float32Array(pcount*3),pdata=[];for(let i=0;i<pcount;i++)pdata.push({x:rand()*.5-.25,z:rand()*.38-.19,phase:rand(),size:rand()});pg.setAttribute('position',new T.BufferAttribute(pa,3));const pm=new T.PointsMaterial({color:0x92836e,size:.018,transparent:true,opacity:.55,depthWrite:false});const dust=new T.Points(pg,pm);scene.add(dust);
const camera=new T.PerspectiveCamera(36,W/H,.04,30),target=new T.Vector3();
function draw(t){t=clamp(t,0,14);let u=sm((t-1.6)/8.4);progress.value=u;let lift=sm((t-9.8)/1.3),osc=.035*Math.sin(t*2.8)*sm((t-1.6)/.6)*(1-lift),bx=mix(-.72,.72,u)+osc+.24*lift;tool.position.set(bx,.025-.08*sm((t-1.5)/.8)+.30*lift,0);tool.rotation.z=-.13+.025*Math.sin(t*3)*((t>1.6&&t<10)?1:0);
 for(let i=0;i<pcount;i++){let d=pdata[i],f=(t*.7+d.phase)%1;pa[i*3]=bx-d.x-.13-f*.25;pa[i*3+1]=.04+f*.25*(1-f);pa[i*3+2]=d.z+f*.15}pg.attributes.position.needsUpdate=true;pm.opacity=(t>1.6&&t<10)? .30:0;
 let v=sm(t/14);camera.position.set(mix(.75,.45,v),mix(1.7,1.25,v),mix(2.05,1.55,v));target.set(mix(-.18,.0,v),-.05,0);camera.lookAt(target);r.render(scene,camera);ctx.clearRect(0,0,W,H);ctx.drawImage(r.domElement,0,0);ctx.fillStyle='rgba(248,244,231,.93)';ctx.shadowColor='rgba(15,18,18,.85)';ctx.shadowBlur=5;ctx.font='700 14px Manrope';ctx.textAlign='left';ctx.fillText('ILLUSTRATIVE EXCAVATION · REFERENCE FRAGMENT',28,690);ctx.shadowBlur=0;
 return {time:t,progress:u,brush_x:bx,lift,fragment:'adapted-reference-mesh',real_site:false};}
window.__seek=draw;window.__ready=true;draw(0);
