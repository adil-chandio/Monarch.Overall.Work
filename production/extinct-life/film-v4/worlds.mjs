import * as T from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {mastodon,reindeer,hare,rodent,goose} from '/shared/animals.mjs';
const V=(x,y,z)=>new T.Vector3(x,y,z),clamp=x=>Math.max(0,Math.min(1,x)),smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
let seed=20261106;function rnd(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}
let landShift=0,activeDesign="";
const noise=(x,z)=>baseNoise(x+landShift,z-landShift*.37);
const baseNoise=(x,z)=>Math.sin(x*.29+z*.18)*.7+Math.sin(x*.71-z*.41)*.22+Math.sin(x*1.82+z*1.13)*.1;
function texture(kind){const cv=document.createElement('canvas');cv.width=cv.height=512;const c=cv.getContext('2d');c.fillStyle=kind==='bark'?'#77736c':kind==='ground'?'#898978':'#aaa49a';c.fillRect(0,0,512,512);for(let i=0;i<28000;i++){const b=45+Math.floor(rnd()*150);c.fillStyle=`rgba(${b},${b},${b},${.06+rnd()*.23})`;const x=rnd()*512,y=rnd()*512;c.fillRect(x,y,kind==='bark'?1+rnd()*3:1+rnd()*4,kind==='bark'?8+rnd()*44:1+rnd()*3);}const tx=new T.CanvasTexture(cv);tx.wrapS=tx.wrapT=T.RepeatWrapping;tx.repeat.set(kind==='ground'?12:2,kind==='ground'?12:3);tx.colorSpace=T.SRGBColorSpace;return tx;}
const soilMap=texture('ground'),barkMap=texture('bark'),rockMap=texture('rock');
const mats={soil:new T.MeshStandardMaterial({color:0xb5a991,map:soilMap,bumpMap:soilMap,bumpScale:.08,roughness:1}),green:new T.MeshStandardMaterial({color:0x71816a,map:soilMap,bumpMap:soilMap,bumpScale:.065,roughness:1}),rock:new T.MeshStandardMaterial({color:0x9a9588,map:rockMap,bumpMap:rockMap,bumpScale:.06,roughness:.94}),clay:new T.MeshStandardMaterial({color:0xb9b3a3,map:rockMap,bumpMap:rockMap,bumpScale:.035,roughness:.84}),bark:new T.MeshStandardMaterial({color:0x776852,map:barkMap,bumpMap:barkMap,bumpScale:.05,roughness:1}),birch:new T.MeshStandardMaterial({color:0xc9c7b6,map:barkMap,bumpMap:barkMap,bumpScale:.018,roughness:.94}),leaf:new T.MeshStandardMaterial({color:0x566747,roughness:.89,side:T.DoubleSide}),needle:new T.MeshStandardMaterial({color:0x374f44,roughness:.94}),amber:new T.MeshStandardMaterial({color:0xe5b46c,roughness:.35,metalness:.16}),cyan:new T.MeshStandardMaterial({color:0x73b7b0,roughness:.32,metalness:.12}),steel:new T.MeshStandardMaterial({color:0x98a9a6,roughness:.31,metalness:.8}),ivory:new T.MeshStandardMaterial({color:0xe4dfcd,roughness:.45}),glass:new T.MeshPhysicalMaterial({color:0xc5e2df,roughness:.1,metalness:0,transparent:true,opacity:.25,depthWrite:false,side:T.DoubleSide}),liquid:new T.MeshStandardMaterial({color:0x78a9a3,roughness:.18,transparent:true,opacity:.67})};
const loader=new T.TextureLoader();
const [photoClay,photoHeight]=await Promise.all([loader.loadAsync('/materials/clay-albedo.jpg'),loader.loadAsync('/materials/clay-height.jpg')]);
photoClay.colorSpace=T.SRGBColorSpace;
for(const tex of [photoClay,photoHeight]){tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.repeat.set(2.5,2.5);tex.anisotropy=2;}
for(const key of ['rock','clay']){mats[key].map=photoClay;mats[key].bumpMap=photoHeight;mats[key].bumpScale=key==='rock'?.055:.035;mats[key].color.set(key==='clay'?'#e5dbc3':'#d2c9b4');}
function mesh(parent,g,m,x=0,y=0,z=0){const a=new T.Mesh(g,m);a.position.set(x,y,z);a.castShadow=a.receiveShadow=true;parent.add(a);return a;}
const ball=new T.SphereGeometry(1,24,18);function ell(p,m,x,y,z,sx,sy,sz){const a=mesh(p,ball,m,x,y,z);a.scale.set(sx,sy,sz);return a;}
function cylinder(p,r1,r2,h,m,x=0,y=0,z=0){return mesh(p,new T.CylinderGeometry(r1,r2,h,20),m,x,y,z);}
function box(p,w,h,d,m,x=0,y=0,z=0){return mesh(p,new T.BoxGeometry(w,h,d,2,2,2),m,x,y,z);}
function curve(p,pts,r,mat){return mesh(p,new T.TubeGeometry(new T.CatmullRomCurve3(pts.map(q=>V(...q))),30,r,10,false),mat);}
function setup(type){const scene=new T.Scene();scene.background=new T.Color(type==='lab'?'#182b31':'#91afb5');scene.fog=new T.FogExp2(type==='lab'?'#182b31':'#91afb5',type==='lab'?.033:.017);scene.add(new T.HemisphereLight(type==='lab'?'#a6c9cb':'#dbe5d5','#393b32',type==='lab'?2.1:1.65));const sun=new T.DirectionalLight(type==='lab'?'#f4e3be':'#ffdb9e',type==='lab'?3.1:3.5);sun.position.set(-8,13,-5);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-14,right:14,top:14,bottom:-14,near:.3,far:45});sun.shadow.bias=-.00025;sun.shadow.normalBias=.03;scene.add(sun);const rim=new T.DirectionalLight('#83b9c4',1.25);rim.position.set(9,5,6);scene.add(rim);return {scene,update:()=>{},type};}
function terrain(p,green=false){const geo=new T.PlaneGeometry(180,180,140,140);geo.rotateX(-Math.PI/2);const a=geo.attributes.position;for(let i=0;i<a.count;i++){const x=a.getX(i),z=a.getZ(i),d=Math.min(1,Math.max(0,(Math.hypot(x,z)-12)/18));a.setY(i,noise(x,z)*d*2.2-.045);}geo.computeVertexNormals();mesh(p,geo,green?mats.green:mats.soil);}
function rocks(p,n=100){const g=new T.IcosahedronGeometry(1,2),a=new T.InstancedMesh(g,mats.rock,n),o=new T.Object3D();a.castShadow=a.receiveShadow=true;for(let i=0;i<n;i++){let x=(rnd()-.5)*65,z=(rnd()-.5)*65;if(Math.hypot(x,z)<4)x+=8;let s=.08+rnd()*.65;o.position.set(x,noise(x,z)*Math.min(1,Math.max(0,(Math.hypot(x,z)-12)/18))*2.2-.045+s*.17,z);o.scale.set(s,s*(.4+rnd()*.3),s*(.7+rnd()));o.rotation.set(rnd(),rnd()*6,rnd());o.updateMatrix();a.setMatrixAt(i,o.matrix);}p.add(a);}
function tree(p,x,z,h,type){
 const g=new T.Group();g.position.set(x,noise(x,z)*Math.min(1,Math.max(0,(Math.hypot(x,z)-12)/18))*2.2-.045,z);p.add(g);const bark=type==='birch'?mats.birch:mats.bark;cylinder(g,.025,.12,h,bark,0,h/2,0);
 const tips=[],branchParts=[];const pine=type==='conifer';const n=pine?42:20;
 for(let j=0;j<n;j++){const y=pine?h*(.2+.75*Math.floor(j/6)/7):h*(.45+.48*j/n),theta=j*2.399,rad=(pine?(1-y/h)*.43:.22+Math.sin(j*1.9)*.035)*h;const a=V(0,y,0),b=V(Math.sin(theta)*rad,y+(pine?-.05:.12)*h,Math.cos(theta)*rad),mid=a.clone().lerp(b,.65);mid.y-=h*.04;const tubeGeo=new T.TubeGeometry(new T.CatmullRomCurve3([a,mid,b]),10,.012+(1-y/h)*.025,5,false);branchParts.push(tubeGeo);tips.push(b);}
 const merged=mergeGeometries(branchParts);mesh(g,merged,bark);branchParts.forEach(a=>a.dispose());
 const shape=new T.Shape();shape.moveTo(0,-.1);shape.quadraticCurveTo(.065,-.025,0,.1);shape.quadraticCurveTo(-.065,-.025,0,-.1);
 const geo=pine?new T.PlaneGeometry(.023,.19):new T.ShapeGeometry(shape,3),count=pine?1000:800,leaves=new T.InstancedMesh(geo,pine?mats.needle:mats.leaf,count),o=new T.Object3D();leaves.material.side=T.DoubleSide;leaves.castShadow=true;
 for(let j=0;j<count;j++){const b=tips[j%tips.length],a=rnd()*Math.PI*2,r=Math.cbrt(rnd())*h*(pine?.065:.12);o.position.set(b.x+Math.sin(a)*r,b.y+(rnd()-.5)*r*1.6,b.z+Math.cos(a)*r);o.rotation.set(rnd()*Math.PI,rnd()*6,rnd()*6);o.scale.setScalar(.7+rnd()*.65);o.updateMatrix();leaves.setMatrixAt(j,o.matrix);}g.add(leaves);return g;
}
function grass(p){const n=1800,g=new T.ConeGeometry(.025,.35,3),a=new T.InstancedMesh(g,mats.leaf,n),o=new T.Object3D();for(let i=0;i<n;i++){let x=(rnd()-.5)*35,z=(rnd()-.5)*30;if(Math.abs(x-(5+Math.sin(z*.12)*.9))<2.1)x-=4;if(Math.abs(x)<1.8&&Math.abs(z)<5)x-=3;o.position.set(x,.08,z);o.rotation.set(rnd()*.25,rnd()*6,rnd()*.18);o.scale.setScalar(.5+rnd());o.updateMatrix();a.setMatrixAt(i,o.matrix);}p.add(a);}
function water(p,x,z,w=5,l=35){const uniforms={time:{value:0},base:{value:new T.Color('#477f82')}};const mat=new T.ShaderMaterial({uniforms,vertexShader:`varying vec3 v;uniform float time;void main(){vec3 p=position;p.x=p.x*(1.+.12*sin(p.y*.15))+sin(p.y*.12)*.9;p.z+=.012*sin(p.x*3.+p.y*2.+time*1.4)+.008*sin(p.y*5.-time);v=p;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,fragmentShader:`varying vec3 v;uniform float time;uniform vec3 base;void main(){float dx=.12*cos(v.x*3.+v.y*2.+time*1.4)+.06*cos(v.x*7.7-v.y*3.1-time*.8);float dz=.08*cos(v.x*3.+v.y*2.+time*1.4)+.09*cos(v.y*5.-time);vec3 n=normalize(vec3(-dx,1.,-dz));float shine=pow(max(0.,dot(n,normalize(vec3(.3,1.,.15)))),65.);float tone=.5+.5*sin(v.x*1.1+v.y*.7+time*.3);gl_FragColor=vec4(base*.8+vec3(.12,.15,.13)*tone+vec3(.3,.29,.23)*shine,1.);}`});const m=mesh(p,new T.PlaneGeometry(w,l,30,100),mat,x,-.008,z);m.rotation.x=-Math.PI/2;return t=>uniforms.time.value=t;}
export function landscape(warm=true){const w=setup('outside'),p=w.scene;terrain(p,warm);rocks(p,warm?95:200);const dry=activeDesign.includes('opening')||activeDesign.includes('last-green'),delta=activeDesign.includes('delta'),terrace=activeDesign.includes('terrace');const waterUpdate=dry?()=>{}:water(p,delta?4.5:5,0,delta?5.4:3,65);const trees=[];if(warm){for(let i=0;i<(terrace?40:75);i++){let x=(rnd()-.5)*65,z=(rnd()-.5)*58;if(Math.hypot(x,z)<7||Math.abs(x-5)<2.4){x+=x>5?7:-7;}trees.push(tree(p,x,z,3+rnd()*4,i%3===0?'conifer':i%3===1?'birch':'poplar'));}grass(p);}
 const mammal=mastodon();p.add(mammal);const deer=reindeer();deer.position.set(-4,0,-4);p.add(deer);const rabbit=hare();rabbit.position.set(-1.7,0,1);p.add(rabbit);const mouse=rodent();mouse.position.set(1.4,0,.7);p.add(mouse);const bird=goose();bird.position.set(4.3,.1,.7);p.add(bird);
 const actors={mastodon:mammal,reindeer:deer,hare:rabbit,rodent:mouse,goose:bird};if(!warm)Object.values(actors).forEach(a=>a.visible=false);
 w.actors=actors;w.update=(t,mode,act=0,chapter=0)=>{waterUpdate(t);if(warm){Object.entries(actors).forEach(([key,a])=>{a.visible=mode==='wide'?(chapter>=4||key==='mastodon'):key===(mode==='takeoff'?'goose':mode);});mammal.position.set(Math.sin(t*.075)*1.1,0,-Math.sin(t*.055)*.65);mammal.rotation.y=-.2+Math.sin(t*.04)*.12;mammal.userData.update(t);deer.position.x=-4+Math.sin(t*.08)*.55;deer.userData.update(t);rabbit.userData.update(t);mouse.userData.update(t);const fly=mode==='takeoff';bird.userData.update(t,fly);bird.position.set(4.3,.1+(fly?smooth(act/2.6)*2.3:0),.7-(fly?smooth(act/3)*2:0));trees.forEach((q,i)=>{q.rotation.z=.012*Math.sin(t*.5+i*.8);});}};return w;}
export function riverWorld(){const w=setup('outside'),p=w.scene;terrain(p,true);rocks(p,85);const wu=water(p,0,0,3.4,70);for(let i=0;i<25;i++)tree(p,(i%2?-1:1)*(3+rnd()*8),-15+rnd()*30,3+rnd()*3,i%3?'birch':'conifer');const animal=mastodon();animal.scale.setScalar(.75);animal.position.set(-3,0,-2);p.add(animal);const grainGeo=new T.SphereGeometry(.035,7,5),grains=new T.InstancedMesh(grainGeo,mats.amber,90),o=new T.Object3D();p.add(grains);
 w.update=(t,mode,age=0)=>{wu(t);animal.userData.update(t);for(let i=0;i<90;i++){const life=clamp((age-i*.07)/20);let x=Math.sin(i*5.7)*.8,y=.05+(1-life)*.1,z=9-life*18;if(mode==='shed'||mode==='decay'){x=-3+life*3;y=.1+Math.sin(life*Math.PI)*.35;z=-2+life*5;}o.position.set(x,y,z);o.scale.setScalar(.5+(i%4)*.12);o.updateMatrix();grains.setMatrixAt(i,o.matrix);}grains.instanceMatrix.needsUpdate=true;};return w;}
export function fragment(parent,count=10){const g=new T.Group(),units=[];parent.add(g);for(let i=0;i<count;i++){const a=i*.75,x=Math.cos(a)*.14,z=Math.sin(a)*.14,y=i*.11;units.push(ell(g,mats.amber,x,y,z,.045,.045,.045));units.push(ell(g,mats.cyan,-x,y,-z,.045,.045,.045));const rung=cylinder(g,.016,.016,.28,mats.ivory,0,y,0);rung.rotation.z=Math.PI/2;rung.rotation.y=-a;units.push(rung);}for(const side of [-1,1]){const pts=Array.from({length:count},(_,i)=>[side*Math.cos(i*.75)*.14,i*.11,side*Math.sin(i*.75)*.14]);curve(g,pts,.019,side>0?mats.amber:mats.cyan);}return {group:g,units};}
export function sedimentWorld(macro=false){const w=setup('outside'),p=w.scene;const macroFill=new T.DirectionalLight('#f5e6c7',2.6);macroFill.position.set(2,5,5);p.add(macroFill);w.scene.background.set('#192a2d');w.scene.fog.color.set('#192a2d');w.scene.fog.density=.07;terrain(p);rocks(p,160);const bank=new T.Group();p.add(bank);bank.visible=!macro;for(let i=0;i<7;i++){const ma=mats.clay.clone();ma.color.setHSL(.105,.12,.40+i*.035);const geo=new T.BoxGeometry(9,.3,3,50,3,12),a=geo.attributes.position;for(let j=0;j<a.count;j++){const x=a.getX(j),z=a.getZ(j);a.setY(j,a.getY(j)+noise(x*4,z*3)*.045);}geo.computeVertexNormals();mesh(bank,geo,ma,0,.16+i*.3,-2.2);}const host=mesh(p,new T.IcosahedronGeometry(1,5),mats.clay,0,.3,0);host.scale.set(1.9,.45,1.3);const fr=fragment(p,8);fr.group.scale.setScalar(.48);const extra=fragment(p,5);extra.group.scale.setScalar(.3);
 w.motionRoots=[fr.group,extra.group,host];w.primaryFragment=fr.group;w.extraFragment=extra.group;w.update=(t,mode,act=0)=>{let bind=['bind','hold','clay'].includes(mode);const k=bind?smooth(act/2):0;fr.group.position.set(-.65+k*.65,.98-k*.25,0);fr.group.rotation.set(.25,.5+Math.sin(t*.28)*.15,.7-k*.6);fr.units.forEach((a,i)=>{a.visible=true;a.position.x+=0;});extra.group.position.set(.8,1.2,-.1);extra.group.rotation.y=t*.24;extra.group.visible=mode==='fragments'||mode==='mix'||mode==='loss'||mode==='break';extra.group.scale.setScalar((mode==='loss'?Math.max(.02,.3*(1-smooth(act/2.5))):.3));host.rotation.y=.025*Math.sin(t*.2);if(mode==='break'){extra.group.position.x=.35+smooth(act/2)*.7;extra.group.position.y=1.2-smooth(act/2)*.25;}if(mode==='cold'){fr.group.rotation.y=.4+Math.sin(t*.45)*.04;}if(mode==='damage'){fr.units.forEach((a,i)=>a.visible=(i%5!==0||act<2));}};return w;}
function vial(p,x,z){const g=new T.Group();g.position.set(x,1.29,z);p.add(g);cylinder(g,.13,.13,.57,mats.glass,0,.3,0);cylinder(g,.105,.105,.22,mats.liquid,0,.13,0);const cap=cylinder(g,.155,.155,.065,mats.steel,0,.61,0);if(Math.abs(x+1.27)<.03&&z<0)cap.visible=false;return g;}
export function labWorld(compare=false){const w=setup('lab'),p=w.scene;box(p,22,.25,16,mats.steel,0,-.2,0);box(p,9,.16,4,mats.ivory,0,1.1,0);const rack=box(p,2,.1,.95,mats.steel,-1,1.24,0);for(let i=0;i<8;i++)vial(p,-1.7+(i%4)*.43,Math.floor(i/4)*.45-.22);const sample=new T.Group();p.add(sample);cylinder(sample,.38,.34,.18,mats.glass,1.2,1.3,0);cylinder(sample,.32,.32,.075,mats.soil,1.2,1.28,0);const pipette=new T.Group();pipette.position.set(1.2,2.5,0);p.add(pipette);cylinder(pipette,.09,.07,.8,mats.ivory,0,.4,0);cylinder(pipette,.04,.012,.52,mats.glass,0,-.22,0);cylinder(pipette,.11,.11,.1,mats.cyan,0,.83,0);const drop=ell(p,mats.liquid,1.2,1.8,0,.025,.06,.025);
 // Persistent physical lab: illuminated racks, extraction vessel, and reference trays.
 for(let i=0;i<3;i++){box(p,1.1,1.8,.7,mats.steel,-3+i*2.8,1.7,-2.5);box(p,.86,.48,.03,mats.cyan,-3+i*2.8,2.05,-2.12);}const traces=[];for(let j=0;j<4;j++){const tray=new T.Group();tray.position.set(-.8+j*.65,1.24,1.05);p.add(tray);box(tray,.48,.035,.72,mats.steel);const f=fragment(tray,5+j%2);f.group.scale.setScalar(.3);f.group.rotation.z=Math.PI/2;f.group.position.set(.06,.09,-.1);traces.push(f);}
 w.motionRoots=[pipette,drop,...traces.flatMap(f=>[f.group,...f.units])];w.traces=traces;w.update=(t,mode,act=0)=>{const phase=act%6.2,travel=smooth((phase-2)/1.5);pipette.position.x=1.2-2.47*travel;pipette.position.z=-.22*travel;pipette.position.y=phase<1?2.7-.85*smooth(phase):phase<2?1.85+.85*smooth(phase-1):phase<3.5?2.7:phase<4.5?2.7-.35*smooth(phase-3.5):2.35+.35*smooth((phase-5.2)/1);drop.position.set(pipette.position.x,1.88-Math.max(0,phase-4.5)*.3,pipette.position.z);drop.visible=mode==='extract'&&phase>=4.5&&phase<5.2;traces.forEach((f,j)=>{f.group.rotation.y=.08*Math.sin(t*.3+j);f.units.forEach((a,i)=>a.visible=!(mode==='damage'&&i%4===j));});if(mode==='control')drop.visible=false;};return w;}
export function evidenceWorld(){const w=labWorld(),p=w.scene;const pollen=new T.Group();pollen.position.set(.4,1.65,.3);p.add(pollen);for(let i=0;i<4;i++){const q=ell(pollen,mats.amber,(i%2)*.31,Math.floor(i/2)*.3,0,.11,.1,.11);for(let j=0;j<12;j++){const a=j*2.4;ell(q,mats.amber,Math.sin(a)*.85,Math.cos(a)*.85,Math.sin(j)*.45,.13,.13,.13);}}const leaf=new T.Group();leaf.position.set(-.7,1.35,.65);p.add(leaf);ell(leaf,mats.leaf,0,0,0,.2,.018,.43);curve(leaf,[[0,.02,.4],[0,.04,0],[0,.02,-.4]],.008,mats.ivory);
 w.motionRoots=[pollen,leaf];w.pollen=pollen;w.leaf=leaf;w.update=(t,mode,act)=>{pollen.rotation.y=t*.12;pollen.visible=mode==='pollen'||mode==='combine';leaf.rotation.y=.18*Math.sin(t*.3);leaf.visible=mode!=='gaps';};return w;}
export const focus={
 'habit-mastodon':{at:[0,2,-.6],r:7.5},'habit-wide':{at:[0,1.4,-1],r:13},'habit-hare':{at:[-1.7,.42,1],r:1.8},'habit-reindeer':{at:[-4,1.5,-4],r:5.5},'habit-goose':{at:[4.3,.65,.7],r:2.8},'habit-takeoff':{at:[4.3,1.9,-.3],r:5.8},'habit-rodent':{at:[1.4,.16,.7],r:.9},'habit-plants':{at:[-6,2,-5],r:7},
 'coast-wide':{at:[0,.7,-5],r:17},'coast-ground':{at:[0,.12,0],r:2.6},
 'river-shed':{at:[-2,1,-1],r:6},'river-decay':{at:[-1,.25,0],r:3.5},'river-flow':{at:[0,.15,1],r:5},'river-source':{at:[0,.8,-6],r:12},
 'sediment-layers':{at:[0,1,-2],r:6},'sediment-age':{at:[0,1,-2],r:5},'sediment-clay':{at:[0,.65,0],r:2.5},
 'macro-trace':{at:[-.3,1,0],r:2.2},'macro-fragments':{at:[0,1,0],r:2.4},'macro-break':{at:[.1,1,0],r:2},'macro-damage':{at:[-.4,1,0],r:1.7},'macro-loss':{at:[.1,1,0],r:2.7},'macro-cold':{at:[-.4,1,0],r:2.2},'macro-bind':{at:[0,.8,0],r:1.9},'macro-hold':{at:[0,.8,0],r:1.8},'macro-mix':{at:[0,1,0],r:2.8},'macro-archive':{at:[0,.75,-.8],r:4},
 'lab-sample':{at:[1.2,1.4,0],r:2.5},'lab-extract':{at:[1,1.7,0],r:2.5},'lab-control':{at:[-1,1.5,0],r:2.5},
 'compare-match':{at:[.1,1.4,1],r:2.2},'compare-family':{at:[.1,1.4,1],r:3},'compare-missing':{at:[.1,1.4,1],r:2.5},'compare-damage':{at:[.1,1.4,1],r:1.9},
 'evidence-plant':{at:[-.7,1.4,.65],r:1.6},'evidence-pollen':{at:[.5,1.7,.3],r:1.7},'evidence-gaps':{at:[.1,1.4,1],r:3},'evidence-combine':{at:[0,1.4,.6],r:3.2}
};

function environmentDetails(w,episode){
 const p=w.scene,kind=episode.world,variant=episode.seed%11;
 // New physical foreground landmarks per visit, not a recolour or replay of the previous set.
 if(['habit','river','coast'].includes(kind)){
  for(let i=0;i<7;i++){
   const x=-3-rnd()*5,z=-1-rnd()*7;
   if(kind==='coast'){
    const g=new T.DodecahedronGeometry(.45+rnd()*.65,2),a=mesh(p,g,mats.rock,x,.08,z);a.scale.set(1.3,.35+rnd()*.3,.8);a.rotation.y=rnd()*6;
   }else{
    const length=1.2+rnd()*2.4;curve(p,[[x,.12,z],[x+length*.4,.17,z+.2],[x+length,.09,z+.45]],.07+rnd()*.045,mats.bark);
    for(let j=0;j<5;j++){const a=j*2.4,r=.25+rnd()*.35;curve(p,[[x,0,z],[x+Math.sin(a)*r*.5,.25,z+Math.cos(a)*r*.5],[x+Math.sin(a)*r,.38,z+Math.cos(a)*r]],.014,mats.leaf);}
   }
  }
  // Distinct delta reed margins and shoreline stones for the imagined encounter.
  if(episode.design.includes('delta'))for(let j=0;j<40;j++){const z=-7+rnd()*15,x=3.1+rnd()*.6;curve(p,[[x,0,z],[x+.04,.5+rnd()*.3,z],[x+.14,.9+rnd()*.2,z+.04]],.008,mats.leaf);}
 }else if(['lab','compare','evidence'].includes(kind)){
  // Different physical sample layouts: circular collection rack, angled slide holder, extraction rail.
  const equipment=new T.Group();equipment.position.set(-2.2,1.25,.9);p.add(equipment);
  const count=5+variant%4;
  for(let i=0;i<count;i++){
   const angle=i/count*Math.PI*2,x=Math.cos(angle)*.55,z=Math.sin(angle)*.32;
   cylinder(equipment,.055,.05,.22,mats.glass,x,.13,z);cylinder(equipment,.065,.065,.025,mats.cyan,x,.25,z);
  }
  cylinder(equipment,.73,.73,.07,mats.steel,0,0,0);
  const rail=new T.Group();rail.position.set(1.9,1.27,.8);rail.rotation.y=.25+variant*.06;p.add(rail);
  for(let j=0;j<3;j++){box(rail,.37,.025,.58,mats.ivory,j*.4,0,0);curve(rail,[[j*.4-.08,.05,-.13],[j*.4+.03,.07,0],[j*.4+.08,.05,.15]],.014,j%2?mats.amber:mats.cyan);}
 }else{
  // A new exposed mineral ledge and a genuinely different particle/fragment arrangement per visit.
  for(let i=0;i<5;i++){
   const a=mesh(p,new T.IcosahedronGeometry(.2+rnd()*.4,3),mats.clay,-1.2+rnd()*2.4,.05,-.8-rnd()*.9);a.scale.set(1,.3+rnd()*.2,.6);a.rotation.y=rnd()*6;
  }
  if(w.primaryFragment){w.primaryFragment.rotation.z+=variant*.06;}
 }
 w.scene.userData.design=episode.design;w.scene.userData.seed=episode.seed;
}
export function buildWorld(episode){
 seed=episode.seed>>>0;activeDesign=episode.design;landShift=(episode.seed%997)*.029;
 const factory={habit:()=>landscape(true),coast:()=>landscape(false),river:riverWorld,macro:()=>sedimentWorld(true),sediment:()=>sedimentWorld(false),lab:labWorld,compare:()=>labWorld(true),evidence:evidenceWorld};
 const w=factory[episode.world]();environmentDetails(w,episode);const original=w.update;let candidate=null;if(episode.world==='compare'&&w.traces){candidate=w.traces[0].group.clone();w.scene.add(candidate);w.motionRoots.push(candidate);}
 w.update=(time,mode,age,chapter)=>{
  original(time,mode,age,chapter);
  if(w.actors&&episode.world==='habit'){
   const actors=w.actors,community=episode.chapter===4||episode.chapter===5;
   Object.entries(actors).forEach(([name,a])=>a.visible=community||name==='mastodon'&&episode.chapter!==7);
   const m=actors.mastodon,u=clamp((age-19)/4),walk=age<19?age:19+4*(u-u**3+.5*u**4);if(age>19){const nodes=[];m.traverse(o=>{if(o!==m)nodes.push(o);});m.userData.update(time,false);const neutral=nodes.map(o=>({p:o.position.clone(),q:o.quaternion.clone(),s:o.scale.clone()}));m.userData.update(time,true);const blend=smooth(u);nodes.forEach((o,i)=>{o.position.lerp(neutral[i].p,blend);o.quaternion.slerp(neutral[i].q,blend);o.scale.lerp(neutral[i].s,blend);});}
   // A one-way traverse/browse, rather than the old sinusoidal back-and-forth root loop.
   m.position.set(-.4+walk*.04,0,-walk*.065);m.rotation.y=-.18+smooth((age-12)/9)*.2;
   actors.reindeer.position.x=-4+age*.075;
   const hopPhase=Math.max(0,Math.min(age-2,4));actors.hare.position.z=1-hopPhase*.11;
   if(age>6)actors.hare.position.y=.01*Math.sin(age*1.3);
   actors.rodent.position.x=1.4+smooth((age-4)/2)*.65;
   // Exactly one takeoff in the imagined-delta sequence; no return-to-start on each spoken phrase.
   const fly=episode.design.includes('delta')&&age>=5.4,flightAge=Math.max(0,age-5.4);
   actors.goose.userData.update(time,fly);if(fly&&flightAge<.9){const nodes=[];actors.goose.traverse(o=>nodes.push(o));actors.goose.userData.update(time,false);const rest=nodes.map(o=>o.quaternion.clone());actors.goose.userData.update(time,true);nodes.forEach((o,i)=>o.quaternion.slerpQuaternions(rest[i],o.quaternion,smooth(flightAge/.9)));}actors.goose.position.set(4.3+smooth(flightAge/7)*2.1,.1+(fly?smooth(flightAge/5)*3.3:0),.7-(fly?smooth(flightAge/8)*7:0));
  }
  if(w.pollen){w.pollen.rotation.y=.2+1.2*smooth(age/24);w.leaf.rotation.y=-.15+.4*smooth((age-8)/18);}
  if(w.traces){w.traces.forEach((f,i)=>f.group.rotation.y=.14*smooth((age-8-i)/16));}if(candidate){candidate.position.set(-.55+1.1*smooth(age/5)-.55*smooth((age-11)/7),1.63+.13*smooth((age-19)/5),1.05);candidate.rotation.y=.06*smooth((age-30)/6);}
  if(w.primaryFragment){w.primaryFragment.rotation.y=.3+.22*smooth(age/40);w.motionRoots[2].rotation.y=0;}
  if(w.extraFragment){w.extraFragment.rotation.y=.2+.6*smooth(age/18);}
  if(w.primaryFragment&&episode.design.includes('release')&&age>32){const release=smooth((age-32)/4);w.primaryFragment.position.y+=release*.55;w.primaryFragment.rotation.z+=release*.3;}
 };
 return w;
}
