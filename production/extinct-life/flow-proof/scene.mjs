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
function fragment(scale=1){const group=new T.Group(),gold=new T.MeshStandardMaterial({color:'#d7b478',roughness:.46,metalness:.13}),ivory=new T.MeshStandardMaterial({color:'#b8ccc0',roughness:.46,metalness:.08}),bond=new T.MeshStandardMaterial({color:'#8d9d89',roughness:.65});const strands=[[],[]];
for(let i=0;i<12;i++){const a=i*.64;for(let side=0;side<2;side++){const sign=side?1:-1,p=new T.Vector3((i-5.5)*.112,Math.sin(a)*.10*sign,Math.cos(a)*.10*sign);strands[side].push(p);const atom=new T.Mesh(new T.SphereGeometry(i===11&&side===0?.031:.024,14,10),side?ivory:gold);atom.position.copy(p);group.add(atom);}if(i!==6){const p1=strands[0][i],p2=strands[1][i],d=p2.clone().sub(p1),rung=new T.Mesh(new T.CylinderGeometry(.008,.008,d.length(),8),bond);rung.position.copy(p1).add(p2).multiplyScalar(.5);rung.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.normalize());group.add(rung);}}
for(let s=0;s<2;s++){const curve=new T.CatmullRomCurve3(strands[s]);const tube=new T.Mesh(new T.TubeGeometry(curve,65,.011,8,false),s?ivory:gold);group.add(tube);}group.scale.setScalar(scale);group.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});return group;}
const hero=fragment(1.12);scene.add(hero);
// Defocused foreground specks establish depth, not repeated title-card decoration.
const dustPos=[];for(let i=0;i<100;i++)dustPos.push((rnd()-.5)*17,-.3+rnd()*3,(rnd()-.5)*13);
const dg=new T.BufferGeometry();dg.setAttribute('position',new T.Float32BufferAttribute(dustPos,3));const dust=new T.Points(dg,new T.PointsMaterial({color:'#b9b7a2',size:.018,transparent:true,opacity:.24,depthWrite:false}));scene.add(dust);
const composer=new EffectComposer(renderer);composer.setSize(W,H);const renderPass=new RenderPass(scene,camera);composer.addPass(renderPass);
const dof=new ShaderPass({uniforms:{tDiffuse:{value:null},tDepth:{value:null},nearClip:{value:camera.near},farClip:{value:camera.far},focusDistance:{value:5},aperture:{value:.014},resolution:{value:new T.Vector2(W,H)}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:`varying vec2 vUv;uniform sampler2D tDiffuse,tDepth;uniform float nearClip,farClip,focusDistance,aperture;uniform vec2 resolution;void main(){float z=texture2D(tDepth,vUv).r;float d=nearClip*farClip/(farClip-z*(farClip-nearClip));float r=clamp(abs(d-focusDistance)/max(d,.01)*aperture,0.,.006);vec2 aspect=vec2(1.,resolution.x/resolution.y);vec4 c=texture2D(tDiffuse,vUv)*2.;for(int i=0;i<12;i++){float a=float(i)*2.399963;float rr=sqrt((float(i)+.5)/12.)*r;vec2 o=vec2(cos(a),sin(a))*rr*aspect;c+=texture2D(tDiffuse,vUv+o);}c/=14.;float vig=smoothstep(.78,.22,length((vUv-.5)*vec2(1.,.7)));c.rgb*=.84+.16*vig;gl_FragColor=c;}`});
// Depth attached to both ping-pong targets; no fake focus animation in a 2D plate.
for(const target of [composer.renderTarget1,composer.renderTarget2]){target.depthTexture=new T.DepthTexture(W,H);target.depthTexture.type=T.UnsignedIntType;}
composer.addPass(dof);composer.addPass(new OutputPass());
const shots=[
{p0:[4.8,4.5,9.5],p1:[4.0,3.25,8.0],target:[-.9,-.2,.3]},
{p0:[3.2,2.1,6.5],p1:[2.6,1.45,5.45],target:null},
{p0:[1.4,1.1,4.5],p1:[1.6,.8,3.85],target:null},
{p0:[-.4,.85,3.65],p1:[.25,.65,3.3],target:null},
{p0:[2.3,.9,3.15],p1:[2.7,.7,2.8],target:null},
{p0:[.2,.65,2.7],p1:[.3,.5,2.4],target:null},
{p0:[3.25,1.05,2.95],p1:[3.6,1.2,3.15],target:null},
{p0:[.5,1.6,3.7],p1:[.2,2.05,4.5],target:null}];
function heroPose(t){const drift=ease((t-2.4)/11.6),settle=ease((t-12.1)/2.4),brownian=1-ease((t-11.5)/3);return new T.Vector3(lerp(-2.05,1.48,drift)+Math.sin(t*1.3)*.025*brownian,lerp(.22,-.25,settle)+Math.sin(t*1.9)*.016*brownian,lerp(.85,-.43,drift)+Math.sin(t*.9)*.018*brownian);}
window.__seek=f=>{const t=f/FPS,index=Math.min(7,Math.floor(t/3)),u=(t-index*3)/3,s=shots[index],travel=u+.025*Math.sin(u*Math.PI*2);hero.position.copy(heroPose(t));const settle=ease((t-12.1)/2.4);hero.rotation.set(lerp(.18,0,settle),lerp(-.2,.10,ease(t/15)),lerp(-.08,0,settle));dust.rotation.y=t*.004;dust.position.x=Math.sin(t*.17)*.045;camera.position.fromArray(s.p0).lerp(new T.Vector3(...s.p1),travel);const target=s.target?new T.Vector3(...s.target):hero.position.clone().add(new T.Vector3(.03,-.01,0));camera.lookAt(target);camera.fov=index<2?38:35;camera.updateProjectionMatrix();dof.uniforms.focusDistance.value=camera.position.distanceTo(target);dof.uniforms.aperture.value=index<2?.005:.009;
// The render pass writes the first target, whose depth is sampled by the next pass.
dof.uniforms.tDepth.value=composer.readBuffer.depthTexture;renderer.shadowMap.autoUpdate=false;renderer.shadowMap.needsUpdate=!window.__continuous||f%3===0;composer.render();ctx.drawImage(renderer.domElement,0,0);ctx.save();ctx.font='17px Arial';ctx.fillStyle='rgba(221,226,211,.72)';ctx.shadowColor='#14242a';ctx.shadowBlur=6;ctx.fillText('Conceptual magnification · not actual sample imagery',84,1022);if(t<3){ctx.font='23px Arial';ctx.fillStyle='rgba(238,228,203,.90)';ctx.fillText('Inside ancient sediment',84,965);}if(t>20.6){ctx.font='23px Arial';ctx.fillStyle='rgba(238,228,203,.90)';ctx.fillText('A fragment. Not a complete genome.',84,965);}ctx.restore();window.__state={t,shot:index,hero:hero.position.toArray(),camera:camera.position.toArray(),focus:dof.uniforms.focusDistance.value};};
await document.fonts.ready;window.__seek(0);window.__ready=true;
