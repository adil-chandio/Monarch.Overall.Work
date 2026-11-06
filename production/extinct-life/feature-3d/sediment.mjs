// Extends the owner-approved procedural material/lighting engine, not its encoded footage.
import * as T from 'three';
import {mergeVertices} from 'three/addons/utils/BufferGeometryUtils.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
const W=1920,H=1080,FPS=30,canvas=document.querySelector('#final'),ctx=canvas.getContext('2d',{alpha:false});
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.16;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;
const scene=new T.Scene();scene.background=new T.Color('#192a2d');scene.fog=new T.FogExp2('#192a2d',.038);
const camera=new T.PerspectiveCamera(38,W/H,.035,70);
scene.add(new T.HemisphereLight('#c1d1cd','#3a3228',1.45));
const key=new T.DirectionalLight('#ffdfb4',3.5);key.position.set(-3,7,5);key.castShadow=true;key.shadow.mapSize.set(1536,1536);Object.assign(key.shadow.camera,{left:-10,right:10,top:8,bottom:-8,near:.5,far:25});key.shadow.normalBias=.025;key.shadow.bias=-.00015;scene.add(key);
const fill=new T.DirectionalLight('#8eb7c2',1.0);fill.position.set(7,3,0);scene.add(fill);
const rim=new T.DirectionalLight('#a5cfca',1.7);rim.position.set(1,4,-7);scene.add(rim);
let seed=77421;function rnd(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}
const clamp=x=>Math.max(0,Math.min(1,x)),ease=x=>{x=clamp(x);return x*x*(3-2*x)},lerp=T.MathUtils.lerp;
function noise(x,y,z){return Math.sin(x*2.3+y*.8+z*.7)*.45+Math.sin(x*5.1-y*3.3+z*2.8)*.23+Math.sin(x*11.7+y*8.4-z*6.7)*.12+Math.sin(x*24.1-y*19.1+z*17.3)*.055;}
const texLoader=new T.TextureLoader();const [albedo,height]=await Promise.all([texLoader.loadAsync('/materials/clay-albedo.jpg'),texLoader.loadAsync('/materials/clay-height.jpg')]);
albedo.colorSpace=T.SRGBColorSpace;for(const t of [albedo,height]){t.wrapS=t.wrapT=T.RepeatWrapping;t.repeat.set(2.5,2.5);t.anisotropy=4;}
const sediment=new T.MeshStandardMaterial({map:albedo,bumpMap:height,bumpScale:.065,color:'#d2c9b4',roughness:.94,metalness:0});
const clayMat=new T.MeshStandardMaterial({map:albedo,bumpMap:height,bumpScale:.038,color:'#b6b9a8',roughness:.78,metalness:0});
// Continuous irregular material surface, not floating diagram slabs.
function floorY(x,z){return -.85+.13*noise(x*.7,0,z*.7)-.65*Math.exp(-Math.pow((x-.8)/3.6,2)-Math.pow(z/3.0,2));}
const geo=new T.PlaneGeometry(120,110,160,140);geo.rotateX(-Math.PI/2);const gp=geo.attributes.position;
for(let i=0;i<gp.count;i++){const x=gp.getX(i),z=gp.getZ(i);const trench=Math.exp(-Math.pow((x-.8)/3.6,2)-Math.pow(z/3.0,2));gp.setY(i,-.85+.13*noise(x*.7,0,z*.7)-trench*.65);}
geo.computeVertexNormals();const floor=new T.Mesh(geo,sediment);floor.receiveShadow=true;scene.add(floor);
// Rounded, individually coloured granular geometry; all original 3D parts.
const rockGeos=[];
for(let j=0;j<5;j++){let g=mergeVertices(new T.IcosahedronGeometry(1,3));const p=g.attributes.position;for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i),z=p.getZ(i),d=1+noise(x+j*4,y+j,z)*.11;p.setXYZ(i,x*d,y*d,z*d);}g.computeVertexNormals();rockGeos.push(g);}
const dummy=new T.Object3D(),color=new T.Color();
for(let j=0;j<5;j++){const n=105,m=new T.InstancedMesh(rockGeos[j],sediment,n);m.castShadow=true;m.receiveShadow=true;for(let i=0;i<n;i++){let x=(rnd()-.5)*24,z=(rnd()-.5)*18;const nearHero=Math.abs(x-1.4)<2.6&&Math.abs(z+.4)<2.1;if(nearHero){x+=x<1.4?-3.8:3.8;z-=1.3;}const s=.055+Math.pow(rnd(),3)*.9;dummy.position.set(x,floorY(x,z)+s*.22,z);dummy.rotation.set(rnd()*3,rnd()*6,rnd()*2);dummy.scale.set(s*(.8+rnd()*.8),s*(.45+rnd()*.4),s*(.7+rnd()*.9));dummy.updateMatrix();m.setMatrixAt(i,dummy.matrix);color.setHSL(.09+rnd()*.035,.08+rnd()*.16,.66+rnd()*.27);m.setColorAt(i,color);}scene.add(m);}
// Distant continuation prevents an isolated tabletop/void silhouette.
const distant=new T.InstancedMesh(mergeVertices(new T.IcosahedronGeometry(1,1)),sediment,300);distant.receiveShadow=true;
for(let i=0;i<300;i++){const x=(rnd()-.5)*74,z=-10-rnd()*35,r=.18+rnd()*1.15;dummy.position.set(x,floorY(x,z)+r*.2,z);dummy.rotation.set(rnd()*2,rnd()*6,rnd());dummy.scale.set(r,r*(.5+rnd()*.3),r*(.7+rnd()*.5));dummy.updateMatrix();distant.setMatrixAt(i,dummy.matrix);color.setHSL(.1,.12,.7+rnd()*.23);distant.setColorAt(i,color);}scene.add(distant);
// One embedded rounded clay aggregate; no floating stacked polygon podium.
let hostGeo=mergeVertices(new T.IcosahedronGeometry(1,16));const hp=hostGeo.attributes.position;
for(let i=0;i<hp.count;i++){const x=hp.getX(i),y=hp.getY(i),z=hp.getZ(i),r=1+.045*noise(x*3,2,z*3);const top=.45+.010*noise(x*5,1,z*5);const yy=y>.32?top:lerp(y,top,ease((y+.02)/.34));hp.setXYZ(i,x*r,yy,z*r);}
hostGeo.computeVertexNormals();const host=new T.Mesh(hostGeo,clayMat);host.position.set(1.65,-.84,-.65);host.scale.set(2.42,1,1.85);host.castShadow=true;host.receiveShadow=true;scene.add(host);
// A single short, broken-ended illustrative fragment, identifiable across every cut.
function fragment(scale=1,first=0,last=12){const group=new T.Group(),gold=new T.MeshStandardMaterial({color:'#d7b478',roughness:.46,metalness:.13}),ivory=new T.MeshStandardMaterial({color:'#b8ccc0',roughness:.46,metalness:.08}),bond=new T.MeshStandardMaterial({color:'#8d9d89',roughness:.65});const strands=[[],[]];
for(let i=first;i<last;i++){const a=i*.64;for(let side=0;side<2;side++){const sign=side?1:-1,p=new T.Vector3((i-5.5)*.112,Math.sin(a)*.10*sign,Math.cos(a)*.10*sign);strands[side].push(p);const atom=new T.Mesh(new T.SphereGeometry(i===11&&side===0?.031:.024,14,10),side?ivory:gold);atom.position.copy(p);group.add(atom);}if(i!==6){const p1=strands[0].at(-1),p2=strands[1].at(-1),d=p2.clone().sub(p1),rung=new T.Mesh(new T.CylinderGeometry(.008,.008,d.length(),8),bond);rung.position.copy(p1).add(p2).multiplyScalar(.5);rung.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.normalize());group.add(rung);}}
for(let s=0;s<2;s++){const curve=new T.CatmullRomCurve3(strands[s]);const tube=new T.Mesh(new T.TubeGeometry(curve,65,.011,8,false),s?ivory:gold);group.add(tube);}group.scale.setScalar(scale);group.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});return group;}
const hero=fragment(1.12,0,6),whole=fragment(1.12),broken=fragment(1.12,6,12),exposed=fragment(.43);
scene.add(hero,whole,broken,exposed);exposed.position.set(3.03,-.32,-.53);exposed.rotation.y=.4;
function opacity(group,value){group.visible=value>.005;group.traverse(o=>{if(o.isMesh){o.material.transparent=value<.999;o.material.opacity=value;o.castShadow=value>.8;}});}
// A continuous sediment bank, rather than an isolated display plinth.
const bankGeo=new T.PlaneGeometry(80,20,150,70),bp=bankGeo.attributes.position,bc=[];
for(let i=0;i<bp.count;i++){const x=bp.getX(i),y=bp.getY(i);bp.setZ(i,.35*noise(x*.4,y*.6,2)+.08*Math.sin(x*2.3+y*1.1));const shade=.72+.065*Math.sin(y*9+.18*Math.sin(x*2));const c=new T.Color().setRGB(shade,shade*.92,shade*.80);bc.push(c.r,c.g,c.b);}
bankGeo.setAttribute('color',new T.Float32BufferAttribute(bc,3));bankGeo.computeVertexNormals();const bankMat=sediment.clone();bankMat.vertexColors=true;const bank=new T.Mesh(bankGeo,bankMat);bank.position.set(1,-.1,-4.15);bank.receiveShadow=true;scene.add(bank);
const embedded=[];for(let i=0;i<3;i++){const f=fragment(.18+i*.035);f.position.set(-1.4+i*2.1,-.4+i*.55,-3.92);f.position.z=-4.15+.35*noise(f.position.x*.4,(f.position.y+.1)*.6,2)+.08*Math.sin(f.position.x*2.3+(f.position.y+.1)*1.1)+.01;f.rotation.set(.1,.25*i,i*.08);scene.add(f);embedded.push(f);}
// Defocused foreground specks establish depth, not repeated title-card decoration.
const dustPos=[];for(let i=0;i<100;i++)dustPos.push((rnd()-.5)*17,-.3+rnd()*3,(rnd()-.5)*13);
const dg=new T.BufferGeometry();dg.setAttribute('position',new T.Float32BufferAttribute(dustPos,3));const dust=new T.Points(dg,new T.PointsMaterial({color:'#b9b7a2',size:.018,transparent:true,opacity:.24,depthWrite:false}));scene.add(dust);
const composer=new EffectComposer(renderer);composer.setSize(W,H);const renderPass=new RenderPass(scene,camera);composer.addPass(renderPass);
const dof=new ShaderPass({uniforms:{tDiffuse:{value:null},tDepth:{value:null},nearClip:{value:camera.near},farClip:{value:camera.far},focusDistance:{value:5},aperture:{value:.014},resolution:{value:new T.Vector2(W,H)}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:`varying vec2 vUv;uniform sampler2D tDiffuse,tDepth;uniform float nearClip,farClip,focusDistance,aperture;uniform vec2 resolution;void main(){float z=texture2D(tDepth,vUv).r;float d=nearClip*farClip/(farClip-z*(farClip-nearClip));float r=clamp(abs(d-focusDistance)/max(d,.01)*aperture,0.,.006);vec2 aspect=vec2(1.,resolution.x/resolution.y);vec4 c=texture2D(tDiffuse,vUv)*2.;for(int i=0;i<12;i++){float a=float(i)*2.399963;float rr=sqrt((float(i)+.5)/12.)*r;vec2 o=vec2(cos(a),sin(a))*rr*aspect;c+=texture2D(tDiffuse,vUv+o);}c/=14.;float vig=smoothstep(.78,.22,length((vUv-.5)*vec2(1.,.7)));c.rgb*=.84+.16*vig;gl_FragColor=c;}`});
// Depth attached to both ping-pong targets; no fake focus animation in a 2D plate.
for(const target of [composer.renderTarget1,composer.renderTarget2]){target.depthTexture=new T.DepthTexture(W,H);target.depthTexture.type=T.UnsignedIntType;}
composer.addPass(dof);composer.addPass(new OutputPass());
const sequence=await (await fetch('/sequence.json')).json();const shots=sequence.chapter_02_shots;
const coverage=[
 {a:[5.6,3.4,8.2],b:[5.1,2.9,7.4],fov:38},
 {a:[2.2,1.1,4.3],b:[1.9,.9,3.9],fov:36},
 {a:[-1.4,.75,3.4],b:[-1.2,.6,3.05],fov:35},
 {a:[1.45,.8,3.0],b:[1.25,.65,2.75],fov:35},
 {a:[-.9,.45,2.2],b:[-.8,.4,2.0],fov:34},
 {a:[2.1,2.4,3.9],b:[1.9,2.1,3.5],fov:36},
 {a:[4.5,4.1,7.8],b:[4.2,4.5,9.0],fov:38}
];
function pose(t){const travel=ease((t-9.8)/12.16),settle=ease((t-19.37)/2.59),thermal=(1-.7*ease((t-10.09)/7))*(1-settle);return new T.Vector3(lerp(-1.8,1.8,travel)+Math.sin(t*1.3)*.025*thermal,lerp(.30,-.25,settle)+Math.sin(t*1.9)*.016*thermal,lerp(.85,-.43,travel)+Math.sin(t*.9)*.018*thermal);}
window.__seek=f=>{
 const t=f/30,index=shots.findIndex(s=>f>=s.start_frame&&f<s.end_frame);if(index<0)throw Error('Frame outside authored chapter');const shot=shots[index],v=coverage[shot.coverage],u=(f-shot.start_frame)/(shot.end_frame-shot.start_frame),travel=u+.025*Math.sin(u*6.2831853),p=pose(t),split=ease((t-6.07)/1.11);
 hero.position.copy(p);whole.position.copy(p);broken.position.copy(p).add(new T.Vector3(split*1.8,split*.32,-split*.65));
 const settle=ease((t-19.37)/2.59);hero.rotation.set(lerp(.18,0,settle),lerp(-.2,.1,ease(t/22)),lerp(-.08,0,settle));whole.rotation.copy(hero.rotation);broken.rotation.copy(hero.rotation);broken.rotation.z+=split*.4;
 whole.visible=t<6.07;hero.visible=t>=6.07;opacity(broken,t<6.07?0:1-ease((t-7.18)/2.91));opacity(exposed,1-ease((t-28.77)/2.31));
 dust.rotation.y=t*.004;dust.position.x=Math.sin(t*.17)*.045;fill.intensity=lerp(1.0,1.22,ease((t-10.09)/7));
 const focus=p.clone().add(new T.Vector3(t>=6.07?-.34:0,-.01,0));if(t>46.69)focus.lerp(new T.Vector3(1.0,.05,-2.1),ease((t-46.69)/5.07)*.6);
 const relative=new T.Vector3(...v.a).lerp(new T.Vector3(...v.b),travel);camera.position.copy(focus).add(relative);camera.lookAt(focus);camera.fov=v.fov;camera.updateProjectionMatrix();
 dof.uniforms.focusDistance.value=camera.position.distanceTo(focus);dof.uniforms.aperture.value=shot.coverage===0||shot.coverage===6?.005:.009;dof.uniforms.tDepth.value=composer.readBuffer.depthTexture;renderer.shadowMap.autoUpdate=false;renderer.shadowMap.needsUpdate=!window.__continuous||f%3===0;composer.render();ctx.drawImage(renderer.domElement,0,0);
 ctx.save();ctx.font='17px Arial';ctx.fillStyle='rgba(221,226,211,.76)';ctx.shadowColor='#14242a';ctx.shadowBlur=6;ctx.fillText('Conceptual reconstruction · not actual sample imagery',84,1022);
 let caption='';if(t<4.4)caption='What allowed a fragment to survive?';else if(t>=6.07&&t<10.09)caption='Fragments break. Many traces are lost.';else if(t>=10.09&&t<19.37)caption='Cold conditions and mineral surfaces';else if(t>=19.37&&t<28.77)caption='Mineral binding can offer some protection';else if(t>=28.77&&t<31.08)caption='Protection is not permanent preservation';else if(t>=31.08&&t<39.37)caption='A mechanism illustrated — not a molecular recording';else if(t>=41.02&&t<46.69)caption='Surface chemistry can influence preservation';else if(t>=46.69)caption='An incomplete archive, held in sediment';if(caption){ctx.font='25px Arial';ctx.fillStyle='rgba(238,228,203,.92)';ctx.fillText(caption,84,965);}ctx.restore();
 window.__state={t,shot:index,hero:hero.position.toArray(),camera:camera.position.toArray(),focus:dof.uniforms.focusDistance.value,split,exposedOpacity:exposed.visible?1-ease((t-28.77)/2.31):0};
};
await document.fonts.ready;window.__seek(0);window.__ready=true;
