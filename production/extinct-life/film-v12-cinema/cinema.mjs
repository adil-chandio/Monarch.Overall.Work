import {grainPose} from './kinematics.mjs';
import {Sky} from 'three/addons/objects/Sky.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {SSAOPass} from 'three/addons/postprocessing/SSAOPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';
import {FXAAShader} from 'three/addons/shaders/FXAAShader.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
// Original absolute-time cinematic/action layer. No stochastic simulation state to accumulate on seek.
export function enhance(a){
 const {T,renderer,camera,worlds,M,bank,scoop,load,bag,journal,cards,fragments,microGrains,habitatVeg,pastVeg,ancient,living,groundLeaf,animal,leaf,text,V,S,height}=a,{field,micro,coast,lab,habitat}=worlds;
 const clamp=x=>Math.max(0,Math.min(1,x)),win=(t,x,y,z,q)=>S((t-x)/(y-x))*(1-S((t-z)/(q-z)));
 let seed=4921;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
 const make=(p,g,m,pos=V(),scale=V(1,1,1))=>{const o=new T.Mesh(g,m);o.position.copy(pos);o.scale.copy(scale);o.castShadow=o.receiveShadow=true;p.add(o);return o};
 const sphere=new T.SphereGeometry(1,16,12),rock=new T.IcosahedronGeometry(1,1);
 // Merge static bank layers to reduce draw calls while preserving their eroded edge and colour variation.
 bank.updateMatrixWorld(true);const slabs=bank.children.filter(o=>o.isMesh&&o.material.map&&o.geometry.type==='BoxGeometry');const gs=[];for(const o of slabs){o.updateMatrix();const g=o.geometry.clone().applyMatrix4(o.matrix);const colors=new Float32Array(g.attributes.position.count*3);for(let i=0;i<g.attributes.position.count;i++){const f=.9+.10*Math.sin(g.attributes.position.getX(i)*3+g.attributes.position.getY(i)*19);colors.set([o.material.color.r*f,o.material.color.g*f,o.material.color.b*f],i*3)}g.setAttribute('color',new T.BufferAttribute(colors,3));gs.push(g);bank.remove(o)}if(gs.length){const m=M.clay.clone();m.color.set('#ffffff');m.vertexColors=true;make(bank,mergeGeometries(gs),m)}
 // Procedural atmospheric sky and image-based room illumination, not generated picture plates.
 const pmrem=new T.PMREMGenerator(renderer),room=new RoomEnvironment(),env=pmrem.fromScene(room,.045).texture;room.dispose();
 const skies=[];for(const w of [field,coast,habitat]){const sky=new Sky();sky.scale.setScalar(230);const u=sky.material.uniforms;u.turbidity.value=w===habitat?5.0:7.5;u.rayleigh.value=w===habitat?1.6:1.05;u.mieCoefficient.value=.004;u.mieDirectionalG.value=.72;u.sunPosition.value.set(-.32,.24,.8);w.scene.add(sky);skies.push({w,sky});w.scene.environment=env;w.scene.environmentIntensity=.18;w.sun.shadow.mapSize.set(1536,1536);w.sun.shadow.radius=3;w.sun.intensity=w===habitat?3.0:2.8;}
 lab.scene.environment=env;lab.scene.environmentIntensity=.32;micro.scene.environment=env;micro.scene.environmentIntensity=.20;M.steel.envMapIntensity=.65;M.glass.envMapIntensity=.6;M.glass.opacity=.13;
 // Gentle contact AO: enough to ground hands/objects, without crushed outlines or bloom flashes.
 const composer=new EffectComposer(renderer),pass=new RenderPass(field.scene,camera),ao=new SSAOPass(field.scene,camera,960,540,8);ao.kernelRadius=.13;ao.minDistance=.00025;ao.maxDistance=.018;composer.addPass(pass);composer.addPass(ao);const aa=new ShaderPass(FXAAShader);aa.uniforms.resolution.value.set(1/1920,1/1080);composer.addPass(aa);composer.addPass(new OutputPass());composer.setSize(1920,1080);ao.setSize(960,540);
 // Wind bends individual instanced leaves/blades rather than rotating the entire forest as one object.
 const coastGround=coast.scene.children.find(o=>o.isMesh&&o.geometry.type==='PlaneGeometry');const pasture=coast.scene.children.find(o=>o.isMesh&&o.geometry.type==='PlaneGeometry'&&o!==coastGround);pasture.geometry.dispose();pasture.geometry=coastGround.geometry.clone();pasture.material=M.ground.clone();pasture.material.transparent=true;pasture.material.depthWrite=false;const waterSource=habitat.scene.children.find(o=>o.isMesh&&o.geometry.type==='PlaneGeometry'&&o.material.type==='MeshPhysicalMaterial');const coastWater=waterSource.clone();coastWater.geometry=waterSource.geometry.clone();coast.scene.add(coastWater);
 const wind={value:0};M.leaf.onBeforeCompile=shader=>{shader.uniforms.cinemaTime=wind;shader.vertexShader='uniform float cinemaTime;\n'+shader.vertexShader;shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
#ifdef USE_INSTANCING
float gust=sin(cinemaTime*1.2+instanceMatrix[3].x*.73+instanceMatrix[3].z*.41);
transformed.x+=gust*.07*max(position.y,0.0);
transformed.z+=sin(cinemaTime*.83+instanceMatrix[3].z)*.018*(position.z+.5);
#endif`)};M.leaf.customProgramCacheKey=()=> 'cinema-leaf-wind-v1';M.leaf.needsUpdate=true;
 // Keep grass out of the water channel; add a physically situated gravel margin and leaf litter.
 const dummy=new T.Object3D(),matrix=new T.Matrix4(),point=new T.Vector3();for(const veg of [habitatVeg,pastVeg]){for(let i=0;i<veg.grass.count;i++){veg.grass.getMatrixAt(i,matrix);point.setFromMatrixPosition(matrix);if(Math.abs(point.x-4-.3*Math.sin((point.z+12)*.12))<1.55){matrix.scale(V(0,0,0));veg.grass.setMatrixAt(i,matrix)}}veg.grass.instanceMatrix.needsUpdate=true}
 const gravel=new T.InstancedMesh(rock,M.rock,340);for(let i=0;i<340;i++){const z=-32+rand()*40,side=i%2?1:-1,x=4+.3*Math.sin((z+12)*.12)+side*(1.55+rand()*.38),r=.025+rand()*.075;dummy.position.set(x,height(x,z)+r*.22,z);dummy.scale.set(r*1.4,r*.55,r);dummy.rotation.set(rand(),rand()*6,rand());dummy.updateMatrix();gravel.setMatrixAt(i,dummy.matrix)}gravel.castShadow=gravel.receiveShadow=true;habitat.scene.add(gravel);
 const litterMat=M.leaf.clone();litterMat.color.set('#b19a6b');litterMat.roughness=.95;const litterShape=new T.Shape();litterShape.moveTo(0,-.075);litterShape.quadraticCurveTo(.06,-.015,0,.075);litterShape.quadraticCurveTo(-.05,.01,0,-.075);const litter=new T.InstancedMesh(new T.ShapeGeometry(litterShape,6),litterMat,260);for(let i=0;i<260;i++){const x=(rand()-.5)*22,z=-18+rand()*24;dummy.position.set(x,height(x,z)+.009,z);dummy.rotation.set(-Math.PI/2,0,rand()*6);dummy.scale.setScalar(.5+rand());dummy.updateMatrix();litter.setMatrixAt(i,dummy.matrix)}habitat.scene.add(litter);
 // The sample transfer is an actual sequence of grains with gravity, one bounce and rest in the pouch.
 const grains=[];for(let i=0;i<34;i++){const p=make(field.scene,rock,i%3?M.clay:M.rock,V(),V(.0035,.003,.004));grains.push({p,release:6.50+i*.008,side:(i%7-3)*.003,z:(Math.floor(i/7)-2)*.003})}
 const chips=[];for(let i=0;i<18;i++){const p=make(field.scene,rock,M.clay,V(),V(.003,.002,.004));chips.push({p,start:4.15+i*.021,x:(rand()-.5)*.10,v:.07+rand()*.08})}
 // A loose report sheet turns on its spine; the same two hands continue supporting the report.
 const page=new T.Group();journal.add(page);page.position.set(-.11,.024,0);const pg=new T.PlaneGeometry(.22,.29,16,20);pg.rotateX(-Math.PI/2);pg.translate(.11,0,0);const pageMesh=make(page,pg,M.paper.clone());pageMesh.material.side=T.DoubleSide;const bindPage=new Float32Array(pg.attributes.position.array);
 const heading=text(page,'MASTODON LINEAGE',V(.11,.002,-.07),.19,'#2d4140');heading.rotation.x=-Math.PI/2;const line=text(page,'Sediment evidence',V(.11,.002,.025),.17,'#4a5551');line.rotation.x=-Math.PI/2;
 // New evidence mechanism: a transparent cover and magnifying lens reveal a clue without changing its identity.
 const glassCover=make(lab.scene,new T.CylinderGeometry(.065,.065,.065,40,1,true),M.glass,V(.43,.86,-.12));const lensRoot=new T.Group();lab.scene.add(lensRoot);make(lensRoot,new T.TorusGeometry(.065,.006,10,48),M.steel);const lensGlass=make(lensRoot,new T.CircleGeometry(.061,40),M.glass);lensGlass.castShadow=false;const lensHandle=make(lensRoot,new T.CylinderGeometry(.005,.005,.13,12),M.dark,V(0,-.115,0));
 // A small field bird offers a restrained scale surprise on the return to the giant; wildlife is conceptual.
 const flyby=animal('goose');coast.scene.add(flyby);flyby.scale.setScalar(.68);
 const goose=animal('goose'),deer=animal('reindeer');habitat.scene.add(goose,deer);goose.scale.setScalar(.85);deer.position.set(7.5,height(7.5,-13.5),-13.5);deer.rotation.y=-Math.PI/2;
 // A tiny original beetle moves on the inspected leaf: living detail, not a claimed ancient taxon.
 const beetle=new T.Group();lab.scene.add(beetle);make(beetle,sphere,new T.MeshPhysicalMaterial({color:'#383f2b',roughness:.42,clearcoat:.25}),V(),V(.0032,.0023,.005));make(beetle,sphere,M.dark,V(0,0,-.0045),V(.002,.0018,.002));const legs=[];for(const side of [-1,1])for(let i=0;i<3;i++){const g=new T.Mesh(new T.CylinderGeometry(.00045,.00045,.005,5),M.dark);g.position.set(side*.003,0,(i-1)*.0024);g.rotation.z=side*.9;beetle.add(g);legs.push(g)}
 const ripples=[];for(let i=0;i<5;i++){const m=new T.MeshBasicMaterial({color:'#d0d9ce',transparent:true,opacity:0,depthWrite:false});const r=make(habitat.scene,new T.TorusGeometry(1,.003,5,64).rotateX(-Math.PI/2),m);r.castShadow=false;ripples.push(r)}
 // Fine airborne life/dust catches light without obscuring the action.
 const motes=[];for(let i=0;i<32;i++){const p=make(lab.scene,sphere,new T.MeshBasicMaterial({color:'#e4d5a9',transparent:true,opacity:.18}),V((rand()-.5)*2,.9+rand()*1.2,-rand()*2),V(.0015,.0015,.0015));p.castShadow=false;motes.push({p,base:p.position.clone(),phase:rand()*6})}
 let diagnostic={};
 function update(t,w,{left,right}){
  wind.value=t;const reconstruction=t>40?1:S((t-22.2)/3.3);pasture.position.y=.015;pasture.material.opacity=reconstruction;coastGround.visible=reconstruction<.999;coastWater.visible=reconstruction>.3;for(const {w:sw,sky}of skies){sky.material.uniforms.sunPosition.value.set(-.32,.24+(sw===coast?.03*S((t-22)/3):0),.8)}
  if(w===coast&&ancient.visible)ancient.position.y=height(ancient.position.x,ancient.position.z);if(w===habitat)living.position.y=height(living.position.x,living.position.z);
  const turn=win(t,28.3,29.6,30.6,31.8);page.visible=t>28.3&&t<31.8;page.rotation.z=-turn*2.35;const positions=pg.attributes.position;for(let i=0;i<positions.count;i++){const k=i*3,x=bindPage[k];positions.setXYZ(i,x,bindPage[k+1]+.022*Math.sin(x/.22*Math.PI)*Math.sin(turn*Math.PI),bindPage[k+2])}positions.needsUpdate=true;pg.computeVertexNormals();
  let falling=0,settled=0;const landing=V(-.118,-.25,-.45),start=V(-.118,-.077,-.45); // camera-relative transfer, same scale as held tool and pouch
  for(const g of grains){const age=t-g.release;g.p.visible=w===field&&age>=0&&age<.85;if(!g.p.visible)continue;const p=grainPose(age,g.side,g.z),local=V(...p.position);if(p.phase==='fall')falling++;else settled++;g.p.position.copy(local.applyQuaternion(camera.quaternion).add(camera.position));g.p.rotation.set(age*5,g.side*30,age*3)}
  for(const c of chips){const age=t-c.start;c.p.visible=w===field&&age>=0&&age<.65;if(c.p.visible){const local=V(.14+c.x,-.20+c.v*age-.5*1.2*age*age,-.58+.04*age);c.p.position.copy(local.applyQuaternion(camera.quaternion).add(camera.position));c.p.rotation.set(age*2,c.x*10,age*5)}}
  if(w===field)load.scale.y=.012*Math.max(.002,1-S((t-6.50)/.27));
  // Lens follows a real hand; a second action in the interpretation return, rather than a new orbit.
  lensRoot.visible=w===lab&&t>49.8&&t<53.15;if(lensRoot.visible){lensRoot.position.copy(right).add(camera.getWorldDirection(V()).multiplyScalar(.11)).add(V(0,.10,0));lensRoot.quaternion.copy(camera.quaternion)}glassCover.visible=t>=43.65;glassCover.position.y=.86;
  beetle.visible=w===lab&&t>=34.0&&t<36.8;if(beetle.visible){const u=S((t-34)/2.8);beetle.position.copy(right).add(camera.getWorldDirection(V()).multiplyScalar(.12));beetle.quaternion.copy(camera.quaternion);beetle.translateX(.012*Math.sin(u*3));beetle.translateY(-.024+.045*u);beetle.translateZ(.004);legs.forEach((g,i)=>g.rotation.x=.22*Math.sin(t*16+i*Math.PI))}
  flyby.visible=w===coast&&t>=41.05&&t<43.60;if(flyby.visible){const u=t-41.05;flyby.position.set(-2.8+u*3.1,1.10+.28*Math.sin(u*1.2),-2.4-u*.45);flyby.rotation.y=Math.PI/2;flyby.userData.update(u,{walk:0,flight:1})}
  if(w===habitat){const life=Math.max(0,t-53.333333);deer.userData.update(life,{walk:0,browse:win(life,.5,1.8,5.1,6.3)});deer.rotation.y=-Math.PI/2+.16*S((life-5.5)/1.2);goose.position.set(-2.8+life*.48,height(-2.8+life*.48,-6),-6);goose.rotation.y=Math.PI/2;goose.userData.update(life,{walk:1,flight:0});for(let i=0;i<ripples.length;i++){const age=life-(1.4+i*.38);const u=clamp(age/2.5);ripples[i].visible=age>=0&&age<2.5;ripples[i].position.set(4.6,-.012,-10.7);ripples[i].scale.setScalar(.08+u*.60);ripples[i].material.opacity=.23*Math.sin(Math.PI*u)}}
  for(const m of motes)m.p.position.copy(m.base).add(V(.02*Math.sin(t*.3+m.phase),.01*Math.sin(t*.4+m.phase),.015*Math.cos(t*.3+m.phase)));
  if(w===micro){const u=t<13.42?t-7.17:t-38.2;for(let i=0;i<fragments.length;i++){const g=fragments[i].g;g.rotation.x=.1*Math.sin(u*.4+i);g.position.z+=.05*S(u/3)*(i%2?1:-1)}for(let i=0;i<microGrains.length;i++)microGrains[i].position.x+=0;}
  diagnostic={cinema_layer:true,contact_ao:true,articulated_hand_detail:true,ballistic_grains_in_flight:falling,grains_settled:settled,page_turn:turn,bird_flyby_visible:flyby.visible,beetle_visible:beetle.visible,community_active:w===habitat,wind_time:t,rigid_body_simulation_claimed:false};
 }
 function render(w){pass.scene=w.scene;ao.scene=w.scene;ao.camera=camera;composer.render()}
 return {update,render,state:()=>diagnostic};
}
