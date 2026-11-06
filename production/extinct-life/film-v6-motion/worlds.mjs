import * as T from 'three';
import {buildWorld as originalWorld} from '/v4/worlds.mjs';
import {smooth,clamp,mammalState,flightState} from './motion.mjs';
import {hermite} from '/v4/direction.mjs';
const V=(x,y,z)=>new T.Vector3(x,y,z);
const stone=new T.MeshStandardMaterial({color:'#a39c86',roughness:.96});
const vegetation=new T.MeshStandardMaterial({color:'#617354',roughness:.92,side:T.DoubleSide});
const copper=new T.MeshStandardMaterial({color:'#b99a65',roughness:.65});
const pale=new T.MeshStandardMaterial({color:'#d0c8a9',roughness:.86});
function mesh(p,g,m,x=0,y=0,z=0){const o=new T.Mesh(g,m);o.position.set(x,y,z);o.castShadow=o.receiveShadow=true;p.add(o);return o;}
function tube(p,points,r,mat){return mesh(p,new T.TubeGeometry(new T.CatmullRomCurve3(points.map(q=>V(...q))),32,r,7,false),mat);}
function scene(){const s=new T.Scene();s.background=new T.Color('#91afb5');s.fog=new T.FogExp2('#91afb5',.018);s.add(new T.HemisphereLight('#dbe5d5','#393b32',1.65));const sun=new T.DirectionalLight('#ffdb9e',3.5);sun.position.set(-8,13,-5);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-18,right:18,top:18,bottom:-18,near:.3,far:60});sun.shadow.bias=-.00025;sun.shadow.normalBias=.025;s.add(sun);const rim=new T.DirectionalLight('#83b9c4',1.25);rim.position.set(9,5,6);s.add(rim);return s;}
const tex=await new T.TextureLoader().loadAsync('/materials/clay-albedo.jpg');tex.colorSpace=T.SRGBColorSpace;tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.repeat.set(3,3);
const groundMat=new T.MeshStandardMaterial({color:'#9b9c82',map:tex,bumpMap:tex,bumpScale:.025,roughness:1});
function ground(s){const g=new T.PlaneGeometry(100,100,160,160);g.rotateX(-Math.PI/2);const p=g.attributes.position;for(let i=0;i<p.count;i++){const x=p.getX(i),z=p.getZ(i),bank=smooth((Math.abs(x)-1.1)/1.4);p.setY(i,-.32+bank*(.52+.1*Math.sin(z*.7)+.06*Math.sin(x*1.2+z)));}g.computeVertexNormals();mesh(s,g,groundMat);}
function water(s,width=3,length=32,x=0,z=0){
 const u={time:{value:0}};const mat=new T.ShaderMaterial({uniforms:u,vertexShader:`uniform float time;varying vec3 v;void main(){vec3 p=position;p.z+=.016*sin(p.x*3.+p.y*1.8+time*1.4)+.007*sin(p.y*4.7-time);v=p;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,fragmentShader:`uniform float time;varying vec3 v;void main(){float a=.5+.5*sin(v.y*1.7+v.x*.8+time*.6);float n=.13*cos(v.x*3.+v.y*1.8+time*1.4);float glint=pow(max(0.,1.-abs(n-.03)),80.);gl_FragColor=vec4(vec3(.17,.35,.36)+a*vec3(.04,.06,.05)+glint*vec3(.15,.16,.12),1.);}`});const o=mesh(s,new T.PlaneGeometry(width,length,24,100),mat,x,-.02,z);o.rotation.x=-Math.PI/2;const update=t=>u.time.value=t;update.mesh=o;return update;
}
function cam(keys,t){const p=hermite(keys.map(([time,...value])=>({time,value})),t);return {position:p.slice(0,3),target:p.slice(3)};}
export function createWorlds(){
 // The owner-accepted V4 moving world is the baseline, NOT the rejected V5 scene plates.
 const episode={world:'habit',design:'delta-contact-flight',seed:160619,chapter:5};const living=originalWorld(episode),originalUpdate=living.update;
 for(const key of ['reindeer','hare','rodent'])living.actors[key].visible=false;
 const treeTemplates=living.scene.children.filter(o=>o.isGroup&&o.children.some(c=>c.isInstancedMesh));
 function trees(s,n,spread=12){for(let i=0;i<n;i++){const a=treeTemplates[i%treeTemplates.length].clone();a.position.set((i%2?1:-1)*(3.5+(i*1.731%spread)), .1, -14+(i*3.973%30));a.scale.setScalar(.65+(i%4)*.08);s.add(a);}}
 const branch=new T.Group();branch.position.set(-1.15,-.045,.8);living.scene.add(branch);tube(branch,[[0,0,0],[0,1.1,0],[-.02,2.2,0],[.03,2.7,.08]],.025,vegetation);
 for(let i=0;i<12;i++){const q=i*2.4,p=tube(branch,[[0,1.1+i*.115,0],[Math.sin(q)*.22,1.3+i*.115,Math.cos(q)*.22]],.009,vegetation);const leaf=mesh(branch,new T.SphereGeometry(1,10,7),vegetation,Math.sin(q)*.26,1.35+i*.115,Math.cos(q)*.26);leaf.scale.set(.14,.025,.06);leaf.rotation.z=q;}
 const ripples=[];for(let i=0;i<7;i++){const mat=new T.MeshBasicMaterial({color:'#c9d8c5',transparent:true,opacity:0,depthWrite:false});const o=mesh(living.scene,new T.TorusGeometry(1,.012,5,60),mat);o.rotation.x=-Math.PI/2;ripples.push(o);}
 living.update=t=>{
  originalUpdate(t,'wide',t,5);const m=living.actors.mastodon,state=mammalState(t);m.visible=true;m.userData.update(t,true);m.position.set(state.position[0],-.045,state.position[2]);m.rotation.y=0;
  for(const key of ['reindeer','hare','rodent'])living.actors[key].visible=false;
  const f=flightState(t),bird=living.actors.goose;bird.visible=true;bird.userData.update(t,f.flight,f.blend);bird.position.set(...f.position);
  const relative=.8-m.position.z,contact=Math.max(0,.94*Math.sqrt(Math.max(0,1-(relative/1.6)**2))-.85);branch.rotation.z=-contact/1.85;branch.rotation.x=.012*Math.sin(t*1.4);
  for(let i=0;i<ripples.length;i++){const age=f.age-i*.21,active=f.flight&&age>0&&age<2.3;const o=ripples[i];o.visible=active;if(active){o.position.set(4.3+i*.015,-.004,.7-i*.02);o.scale.setScalar(.13+age*.5);o.material.opacity=.21*(1-age/2.3);}}
  living.state={mastodon_position:m.position.toArray(),feet:m.userData.rig.legs.map(l=>({stance:l.state.stance,local_z:l.foot.position.z,ground_contact_y:l.foot.position.y-.22+m.position.y})),goose_position:bird.position.toArray(),flight_age:f.age,goose_flying:f.flight,branch_contact_deflection:branch.rotation.z};
 };
 living.camera=t=>cam([[0,-7,3.0,-8.3,-.4,1.5,.0],[4,-6.5,2.9,-8.0,-.2,1.45,-.3],[8,-5.8,3.2,-8.8,.5,1.5,-1.0],[13,-5.1,3.7,-9.6,.6,1.6,-1.8],[23,-4.5,3.8,-11,.1,1.4,-2.7]],t);
 living.labels=t=>t<12.72?[]:[{text:'NOT A RECOVERED AFTERNOON',point:[-.5,4.8,-1],priority:1}];
 living.qualifier='IMAGINED RECONSTRUCTION · NOT AN OBSERVED ENCOUNTER';
 // A genuinely different active transport scene: material joins from banks and travels downstream.
 const rs=scene();ground(rs);trees(rs,18);const wu=water(rs,3.2,36);const gr=new T.IcosahedronGeometry(.05,1),particles=new T.InstancedMesh(gr,pale,96),dummy=new T.Object3D();rs.add(particles);
 for(let side of [-1,1])for(let j=0;j<35;j++){const x=side*(1.8+(j*1.73%3.6)),z=-16+(j*2.31%32),o=mesh(rs,new T.IcosahedronGeometry(.12+(j%5)*.04,1),stone,x,-.08,z);o.scale.set(1.2,.6,.8);}
 const tributary=water(rs,1.3,10,3.3,5.6);tributary.mesh.rotation.z=.7; // oblique joining branch, explicit conceptual catchment
 const sample=mesh(rs,new T.TorusGeometry(.48,.018,7,64),copper,0,.07,-8);sample.rotation.x=-Math.PI/2;
 const paths=[[[4.5,.1,8],[2.4,.05,6],[.5,.05,3],[0,.05,-8]],[[-4,.1,5],[-2,.06,4],[0,.05,1],[0,.05,-8]]].map(p=>new T.CatmullRomCurve3(p.map(q=>V(...q))));
 const river={scene:rs,qualifier:'REPRESENTATIVE TRANSPORT · NOT A RECOVERED CATCHMENT OR TRACKED MOLECULE'};
 river.update=t=>{wu(t);tributary(t);for(let i=0;i<96;i++){const arrival=i*.10,life=clamp((t-arrival)/17),curve=paths[i%2],p=curve.getPoint(life);p.y+=.018*Math.sin(t*2+i);dummy.position.copy(p);dummy.scale.setScalar(t<arrival?.001:.5+(i%4)*.16);dummy.rotation.set(i,.2*t,i*.4);dummy.updateMatrix();particles.setMatrixAt(i,dummy.matrix);}particles.instanceMatrix.needsUpdate=true;river.state={representative_traces:96,transport_age:t,source_sample_distinct:true};};
 river.camera=t=>cam([[0,-4.8,2.7,11,0,.1,5],[8,-5.3,2.9,5,0,.1,0],[16,-5.8,3.3,-1,0,.1,-4],[21,-7.5,5.2,-2,0,.2,-2],[26,-9,7,2,0,.2,0]],t);
 river.labels=t=>t<10.8?[]:t<19.5?[{text:'ENVIRONMENTAL DNA',point:[0,1.3,1]}]:[{text:'SOURCE',point:[-3,1.2,5]},{text:'SAMPLE LOCATION',point:[0,1.15,-8]}];
 // New depositional cross-section: layered sides, successive arrivals and a bracket attached to deposits.
 const ss=scene();ss.background.set('#809b9b');ss.fog.color.set('#809b9b');const fill=new T.DirectionalLight('#f2ead3',2.4);fill.position.set(6,7,9);ss.add(fill);mesh(ss,new T.CylinderGeometry(9,9,.3,64),groundMat,0,-1.6,0);const layers=[];const ring=theta=>[Math.sign(Math.cos(theta))*Math.abs(Math.cos(theta))**.46*3.4,Math.sign(Math.sin(theta))*Math.abs(Math.sin(theta))**.46*2.0];
 const n=64;for(let layer=0;layer<7;layer++){
  const y0=-1.4+layer*.34,y1=y0+.34,positions=[],uv=[];
  for(let j=0;j<n;j++){
   const a=j/n*2*Math.PI,b=(j+1)/n*2*Math.PI;
   const at=(theta,y)=>{const [x,z]=ring(theta);return [x,y+.055*Math.sin(x*2+z),z];};
   const v=[at(a,y0),at(a,y1),at(b,y0),at(a,y1),at(b,y1),at(b,y0)];for(let k=0;k<v.length;k++){positions.push(...v[k]);uv.push(j/n,k%2);}
  }
  const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(positions,3));g.setAttribute('uv',new T.Float32BufferAttribute(uv,2));g.computeVertexNormals();const mat=groundMat.clone();mat.color.set([0x6b6454,0x918775,0x797363,0xada18a,0x807662,0xb7ac93,0x9e957e][layer]);const o=mesh(ss,g,mat);layers.push(o);
 }
 const outline=new T.Shape();for(let i=0;i<=n;i++){const [x,z]=ring(i/n*2*Math.PI);if(i===0)outline.moveTo(x,-z);else outline.lineTo(x,-z);}const capGeo=new T.ShapeGeometry(outline,64);capGeo.rotateX(-Math.PI/2);const cp=capGeo.attributes.position;for(let i=0;i<cp.count;i++)cp.setY(i,.98+.055*Math.sin(cp.getX(i)*2+cp.getZ(i)));capGeo.computeVertexNormals();const cap=mesh(ss,capGeo,groundMat);const arrivals=[];
 for(let i=0;i<30;i++){const o=mesh(ss,new T.IcosahedronGeometry(.045,1),i%2?pale:copper);arrivals.push(o);}
 const deposits={scene:ss,qualifier:'CONCEPTUAL DEPOSITION · DEPOSIT AGE, NOT INDIVIDUAL MOLECULE DATES'};
 deposits.update=t=>{for(let i=0;i<arrivals.length;i++){const a=t-(i%3)*2.4-Math.floor(i/3)*.045,u=smooth(a/2.4),o=arrivals[i];o.visible=a>=0;o.position.set(Math.sin(i*2.4)*2,3.4-u*2.34,Math.cos(i*1.9)*1.4);o.rotation.set(i,t*.1,i*.3);}deposits.state={arrival_batches:Math.min(3,1+Math.floor(t/2.4)),age_applies_to:'deposits',individual_molecule_dates:false};};
 deposits.camera=t=>cam([[0,7,3.2,8,.0,.4,0],[5,6.3,3.6,8.1,0,.5,0],[13,5.6,3.1,8,0,.5,0]],t);
 deposits.labels=t=>t<4.8?[{text:'NOT ONE INSTANT',point:[0,2.2,0]}]:[{text:'~2 MILLION YEARS: DEPOSITS',point:[0,2.45,0]}];
 return {river,deposits,living};
}
