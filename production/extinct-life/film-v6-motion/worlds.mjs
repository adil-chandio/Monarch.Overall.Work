import * as T from 'three';
import {buildWorld as originalWorld} from '/v4/worlds.mjs';
import {smooth,clamp,mammalState,flightState} from './motion.mjs';
import {hermite} from '/v4/direction.mjs';
import {refineWater,shoreReeds,sectionGrains} from './surface.mjs';
import {CUES,channelX,bankHeight,riverLeaf,traceState,layerGrowth,depositSurface,depositionTrace,branchLeaf} from './action.mjs';
const V=(x,y,z)=>new T.Vector3(x,y,z);
const stone=new T.MeshStandardMaterial({color:'#a39c86',roughness:.96});
const vegetation=new T.MeshStandardMaterial({color:'#617354',roughness:.92,side:T.DoubleSide});
const copper=new T.MeshStandardMaterial({color:'#b99a65',roughness:.65});
const pale=new T.MeshStandardMaterial({color:'#d0c8a9',roughness:.86});
function mesh(p,g,m,x=0,y=0,z=0){const o=new T.Mesh(g,m);o.position.set(x,y,z);o.castShadow=o.receiveShadow=true;p.add(o);return o;}
function tube(p,points,r,mat){return mesh(p,new T.TubeGeometry(new T.CatmullRomCurve3(points.map(q=>V(...q))),32,r,7,false),mat);}
function scene(){const s=new T.Scene();s.background=new T.Color('#91afb5');s.fog=new T.FogExp2('#91afb5',.018);s.add(new T.HemisphereLight('#dbe5d5','#393b32',1.65));const sun=new T.DirectionalLight('#ffdb9e',3.5);sun.position.set(-8,13,-5);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-18,right:18,top:18,bottom:-18,near:.3,far:60});sun.shadow.bias=-.00025;sun.shadow.normalBias=.025;s.add(sun);const rim=new T.DirectionalLight('#83b9c4',1.25);rim.position.set(9,5,6);s.add(rim);return s;}
const tex=await new T.TextureLoader().loadAsync('/materials/clay-albedo.jpg');tex.colorSpace=T.SRGBColorSpace;tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.repeat.set(3,3);
stone.map=tex;stone.bumpMap=tex;stone.bumpScale=.04;stone.color.set('#8d907f');
const groundMat=new T.MeshStandardMaterial({color:'#9b9c82',map:tex,bumpMap:tex,bumpScale:.025,roughness:1});
function ground(s){const g=new T.PlaneGeometry(100,100,160,160);g.rotateX(-Math.PI/2);const p=g.attributes.position;for(let i=0;i<p.count;i++){const x=p.getX(i),z=p.getZ(i),bank=bankHeight(x,z);p.setY(i,bank);}g.computeVertexNormals();mesh(s,g,groundMat);}
function water(s,width=3,length=32,x=0,z=0){
 const u={time:{value:0}};const mat=new T.ShaderMaterial({uniforms:u,vertexShader:`uniform float time;varying vec3 v;void main(){vec3 p=position;p.x+=.25*sin(p.y*.28);p.z+=.016*sin(p.x*3.+p.y*1.8+time*1.4)+.007*sin(p.y*4.7-time);v=p;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,fragmentShader:`uniform float time;varying vec3 v;void main(){float a=.5+.5*sin(v.y*1.7+v.x*.8+time*.6);float n=.13*cos(v.x*3.+v.y*1.8+time*1.4);float glint=pow(max(0.,1.-abs(n-.03)),80.);gl_FragColor=vec4(vec3(.17,.35,.36)+a*vec3(.04,.06,.05)+glint*vec3(.15,.16,.12),1.);}`});refineWater(mat);const o=mesh(s,new T.PlaneGeometry(width,length,24,100),mat,x,-.02,z);o.rotation.x=-Math.PI/2;const update=t=>u.time.value=t;update.mesh=o;return update;
}
function cam(keys,t){const p=hermite(keys.map(([time,...value])=>({time,value})),t);return {position:p.slice(0,3),target:p.slice(3)};}
export function createWorlds(){
 // The owner-accepted V4 moving world is the baseline, NOT the rejected V5 scene plates.
 const episode={world:'habit',design:'delta-contact-flight',seed:160619,chapter:5};const living=originalWorld(episode),originalUpdate=living.update;
 living.scene.traverse(o=>{if(o.material)refineWater(o.material);});
 const livingReeds=shoreReeds(living.scene,z=>4.5-.9*Math.sin(z*.12),()=>-.045,{halfWidth:2.7,range:7,count:180});
 for(const key of ['reindeer','hare','rodent'])living.actors[key].visible=false;
 const treeTemplates=living.scene.children.filter(o=>o.isGroup&&o.children.some(c=>c.isInstancedMesh));
 function trees(s,n,spread=12){for(let i=0;i<n;i++){const a=treeTemplates[i%treeTemplates.length].clone();a.position.set((i%2?1:-1)*(3.5+(i*1.731%spread)), bankHeight((i%2?1:-1)*(3.5+(i*1.731%spread)),-14+(i*3.973%30)), -14+(i*3.973%30));a.scale.setScalar(.65+(i%4)*.08);s.add(a);}}
 const attachedLeaves=[];
 const branch=new T.Group();branch.position.set(-1.15,-.045,.8);living.scene.add(branch);tube(branch,[[0,0,0],[0,1.1,0],[-.02,2.2,0],[.03,2.7,.08]],.025,vegetation);
 for(let i=0;i<12;i++){const q=i*2.4,p=tube(branch,[[0,1.1+i*.115,0],[Math.sin(q)*.22,1.3+i*.115,Math.cos(q)*.22]],.009,vegetation);const leaf=mesh(branch,new T.SphereGeometry(1,10,7),vegetation,Math.sin(q)*.26,1.35+i*.115,Math.cos(q)*.26);leaf.scale.set(.14,.025,.06);leaf.rotation.z=q;attachedLeaves.push(leaf);}
 const fallenLeaves=[];for(let i=0;i<2;i++){const leaf=mesh(living.scene,new T.SphereGeometry(1,12,8),vegetation);leaf.scale.set(.14,.025,.06);fallenLeaves.push(leaf);}
 const ripples=[];for(let i=0;i<7;i++){const mat=new T.MeshBasicMaterial({color:'#c9d8c5',transparent:true,opacity:0,depthWrite:false});const o=mesh(living.scene,new T.TorusGeometry(1,.012,5,60),mat);o.rotation.x=-Math.PI/2;ripples.push(o);}
 living.update=t=>{
  originalUpdate(t,'wide',t,5);livingReeds(t);const m=living.actors.mastodon,state=mammalState(t);m.visible=true;m.userData.update(t,true);m.position.set(state.position[0],-.045,state.position[2]);m.rotation.y=0;
  for(const key of ['reindeer','hare','rodent'])living.actors[key].visible=false;
  const f=flightState(t),bird=living.actors.goose;bird.visible=true;bird.userData.update(t,f.flight,f.blend);bird.position.set(...f.position);
  const attention=smooth((t-5.8)/1.1)*(1-smooth((t-8.7)/1.8));m.userData.rig.head.rotation.y-=.16*attention;
  fallenLeaves.forEach((leaf,i)=>{attachedLeaves[8+i].visible=t<CUES.branch_leaf_release+i*.12;const a=branchLeaf(t,i);leaf.visible=a.visible;leaf.position.set(...a.position);leaf.rotation.set(a.landed?0:(t-CUES.branch_leaf_release)*2.3,0,a.landed?.3:(8+i)*2.4+(t-CUES.branch_leaf_release)*1.8);});
  const relative=.8-m.position.z,contact=Math.max(0,.94*Math.sqrt(Math.max(0,1-(relative/1.6)**2))-.85);branch.rotation.z=-contact/1.85;branch.rotation.x=.012*Math.sin(t*1.4);if(t>10)branch.rotation.z+=.022*Math.exp(-(t-10)*1.4)*Math.sin((t-10)*9);
  for(let i=0;i<ripples.length;i++){const age=f.age-i*.21,active=f.flight&&age>0&&age<2.3;const o=ripples[i];o.visible=active;if(active){o.position.set(4.3+i*.015,-.004,.7-i*.02);o.scale.setScalar(.13+age*.5);o.material.opacity=.21*(1-age/2.3);}}
  if(Math.abs(t-CUES.branch_leaf_release)<1e-5){branch.updateMatrixWorld(true);const error=attachedLeaves[8].getWorldPosition(V(0,0,0)).distanceTo(V(...branchLeaf(t).position));if(error>.001)throw Error('Detached leaf discontinuity: '+error);}
  living.state={mastodon_position:m.position.toArray(),feet:m.userData.rig.legs.map(l=>({stance:l.state.stance,local_z:l.foot.position.z,ground_contact_y:l.foot.position.y-.22+m.position.y})),goose_position:bird.position.toArray(),flight_age:f.age,goose_flying:f.flight,branch_contact_deflection:branch.rotation.z,head_attention:attention,detached_leaf:branchLeaf(t)};
 };
 living.camera=t=>cam([[0,-7,3.0,-8.3,-.4,1.5,.0],[4,-6.5,2.9,-8.0,-.2,1.45,-.3],[8,-5.8,3.2,-8.8,.5,1.5,-1.0],[13,-5.1,3.7,-9.6,.6,1.6,-1.8],[23,-4.5,3.8,-11,.1,1.4,-2.7]],t);
 living.labels=t=>t<12.72?[]:[{text:'NOT A RECOVERED AFTERNOON',point:[-.5,4.8,-1],priority:1}];
 living.qualifier='IMAGINED RECONSTRUCTION · NOT AN OBSERVED ENCOUNTER';
 // A genuinely different active transport scene: material joins from banks and travels downstream.
 const rs=scene();ground(rs);trees(rs,26);const riverReeds=shoreReeds(rs,channelX,bankHeight);const wu=water(rs,3.2,36);const gr=new T.IcosahedronGeometry(.045,1),particles=new T.InstancedMesh(gr,pale,36),dummy=new T.Object3D();rs.add(particles);particles.frustumCulled=false; // Instance transforms move beyond the initial cached bounds.
 for(let side of [-1,1])for(let j=0;j<35;j++){const x=side*(1.8+(j*1.73%3.6)),z=-16+(j*2.31%32),o=mesh(rs,new T.IcosahedronGeometry(.12+(j%5)*.04,1),stone,x,bankHeight(x,z)+.035,z);o.scale.set(1.2,.6,.8);o.rotation.y=j*2.399;}
 // A visible leaf is an illustrative current tracer, NOT a visible DNA molecule.
 const leafShape=new T.Shape();leafShape.moveTo(0,-.27);leafShape.quadraticCurveTo(.24,-.02,0,.32);leafShape.quadraticCurveTo(-.20,.04,0,-.27);
 const leafGeo=new T.ShapeGeometry(leafShape,12);leafGeo.rotateX(-Math.PI/2);const heroLeaf=mesh(rs,leafGeo,new T.MeshStandardMaterial({color:'#c9af61',roughness:.8,side:T.DoubleSide}));
 heroLeaf.scale.setScalar(.7);const vein=tube(heroLeaf,[[0,.008,-.23],[0,.025,0],[0,.008,.27]],.009,vegetation);
 const sample=mesh(rs,new T.TorusGeometry(.48,.009,6,64,Math.PI*1.65),copper,channelX(-8),.07,-8);sample.rotation.x=-Math.PI/2;
 const shoal=mesh(rs,new T.SphereGeometry(1,24,12),groundMat,channelX(-8),-.035,-8);shoal.scale.set(.48,.055,.57);
 const splash=[];for(let i=0;i<3;i++){const o=mesh(rs,new T.TorusGeometry(1,.009,5,48),new T.MeshBasicMaterial({color:'#e3dfbf',transparent:true,opacity:0,depthWrite:false}));o.rotation.x=-Math.PI/2;splash.push(o);}
 const river={scene:rs,qualifier:'CONCEPTUAL TRANSPORT · TRACE MARKERS ENLARGED · NOT A RECOVERED CATCHMENT'};
 river.update=t=>{wu(t);riverReeds(t);const leaf=riverLeaf(t);heroLeaf.position.set(...leaf.position);heroLeaf.rotation.set(leaf.landed?.05*Math.sin(t*1.8):.7*Math.sin(t*2),Math.min(t,CUES.river_leaf_arrive)*.23,leaf.landed?0:.6*Math.cos(t));
  let arrived=0;for(let i=0;i<36;i++){const a=traceState(t,i);dummy.position.set(...a.position);if(a.arrived){dummy.position.x+=(i%6-2.5)*.075;dummy.position.z+=Math.floor(i/6)*.055;arrived++;}dummy.scale.setScalar(a.visible?a.scale:.001);dummy.rotation.set(i,.2*Math.min(t,a.stopTime),i*.4);dummy.updateMatrix();particles.setMatrixAt(i,dummy.matrix);}particles.instanceMatrix.needsUpdate=true;
  const landed=riverLeaf(CUES.river_leaf_land).position;for(let i=0;i<splash.length;i++){const age=t-CUES.river_leaf_land-i*.17,o=splash[i];o.visible=age>0&&age<1.5;if(o.visible){o.position.set(landed[0],.001,landed[2]);o.scale.setScalar(.12+age*.38);o.material.opacity=.32*(1-age/1.5);}}
  sample.scale.setScalar(1+.045*Math.sin(t*2)*smooth((t-17)/2));river.state={representative_traces:36,transport_age:t,source_sample_distinct:true,visible_leaf:leaf,settled_trace_markers:arrived};};
 river.camera=t=>cam([[0,-3.2,2.5,11,0,.6,7],[4,-3.4,2.6,9,0,.1,6],[10,-4,2.9,3,0,.1,0],[17,-4.8,3.1,-3.5,0,.1,-6],[22,-7,5.4,-.5,0,.1,-3],[26,-8,6,1,0,.1,-2]],t);
 river.labels=t=>t<10.8?[]:t<19.5?[{text:'ENVIRONMENTAL DNA · ENLARGED MARKERS',point:traceState(t,5).position,opacity:smooth((t-10.8)/.6)*(1-smooth((t-18.9)/.6))}]:[{text:'UPSTREAM MATERIAL',point:[channelX(5),.05,5],opacity:smooth((t-19.5)/.6)},{text:'SAMPLE LOCATION',point:[channelX(-8),.08,-8],opacity:smooth((t-19.5)/.6)}];
 // New depositional cross-section: layered sides, successive arrivals and a bracket attached to deposits.
 const ss=scene();ss.background.set('#809b9b');ss.fog.color.set('#809b9b');const fill=new T.DirectionalLight('#f2ead3',2.4);fill.position.set(6,7,9);ss.add(fill);mesh(ss,new T.CylinderGeometry(9,9,.3,64),groundMat,0,-1.6,0);const layers=[];const ring=theta=>[Math.sign(Math.cos(theta))*Math.abs(Math.cos(theta))**.46*3.4,Math.sign(Math.sin(theta))*Math.abs(Math.sin(theta))**.46*2.0];
 const n=64;for(let layer=0;layer<7;layer++){
  const y0=-1.4+layer*.34,y1=y0+.34,positions=[],uv=[];
  for(let j=0;j<n;j++){
   const a=j/n*2*Math.PI,b=(j+1)/n*2*Math.PI;
   const at=(theta,y)=>{const [x,z]=ring(theta);return [x,y+.055*Math.sin(x*2+z),z];};
   const v=[at(a,y0),at(a,y1),at(b,y0),at(a,y1),at(b,y1),at(b,y0)];for(let k=0;k<v.length;k++){positions.push(...v[k]);uv.push(j/n,k%2);}
  }
  const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(positions,3));g.setAttribute('uv',new T.Float32BufferAttribute(uv,2));g.userData.rest=Float32Array.from(positions);g.computeVertexNormals();const mat=groundMat.clone();mat.color.set([0x6b6454,0x918775,0x797363,0xada18a,0x807662,0xb7ac93,0x9e957e][layer]);const o=mesh(ss,g,mat);layers.push(o);
 }
 const outline=new T.Shape();for(let i=0;i<=n;i++){const [x,z]=ring(i/n*2*Math.PI);if(i===0)outline.moveTo(x,-z);else outline.lineTo(x,-z);}const capGeo=new T.ShapeGeometry(outline,64);capGeo.rotateX(-Math.PI/2);const cp=capGeo.attributes.position;for(let i=0;i<cp.count;i++)cp.setY(i,.98+.055*Math.sin(cp.getX(i)*2+cp.getZ(i)));capGeo.computeVertexNormals();const cap=mesh(ss,capGeo,groundMat);const grainMat=groundMat.clone();grainMat.color.set('#a5977c');grainMat.bumpScale=.0005;sectionGrains(cap,grainMat);const arrivals=[];
 for(let i=0;i<30;i++){const o=mesh(ss,new T.IcosahedronGeometry(.045,1),i%2?pale:copper);arrivals.push(o);}
 const deposits={scene:ss,qualifier:'SCHEMATIC TIME ACCUMULATION · ENLARGED MARKERS · AGE APPLIES TO DEPOSITS'};
 // Surface rises as new bands accumulate. Three marker cohorts become exposed at different depths.
 const ageBracket=new T.Group();ss.add(ageBracket);const bracketMat=copper.clone();bracketMat.transparent=true;
 tube(ageBracket,[[3.8,-1.35,1.4],[3.8,.98,1.4]],.018,bracketMat);for(const y of [-1.35,.98])tube(ageBracket,[[3.53,y,1.4],[3.8,y,1.4]],.018,bracketMat);
 deposits.update=t=>{for(let i=0;i<layers.length;i++){const grow=layerGrowth(t,i),bottom=-1.4+i*.34;layers[i].visible=grow>0;const p=layers[i].geometry.attributes.position,rest=layers[i].geometry.userData.rest;for(let j=0;j<p.count;j++){const wave=.055*Math.sin(rest[j*3]*2+rest[j*3+2]);p.setY(j,bottom+(rest[j*3+1]-bottom-wave)*grow+wave);}p.needsUpdate=true;}cap.position.y=depositSurface(t)-.98;
  for(let i=0;i<arrivals.length;i++){const a=depositionTrace(t,i),o=arrivals[i];o.visible=a.visible;o.position.set(...a.position);o.rotation.set(i,a.landed?0:t*.3,i*.3);o.scale.setScalar(1.35);}
  ageBracket.visible=t>5.05;bracketMat.opacity=smooth((t-5.05)/.8);deposits.state={arrival_batches:Math.min(3,1+Math.floor(t/1.64)),surface_height:depositSurface(t),layer_growth:layers.map((_,i)=>layerGrowth(t,i)),age_applies_to:'deposits',individual_molecule_dates:false};};
 deposits.camera=t=>cam([[0,7.5,3.8,9,0,-.35,0],[2.5,7.3,3.9,9.2,0,-.1,0],[5,7.2,4,9.5,0,0,0],[13,6.8,3.9,9.8,0,0,0]],t);
 deposits.labels=t=>t<5.05?[{text:'ACCUMULATED OVER TIME · NOT ONE INSTANT',point:[0,depositSurface(t)+.08,1.85],opacity:smooth(t/.7)}]:[{text:'~2 MILLION YEARS: DEPOSITS',point:[3.8,-.1,1.4],opacity:smooth((t-5.05)/.8)}];
 return {river,deposits,living};
}
