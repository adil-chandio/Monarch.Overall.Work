import * as T from 'three';
import * as science from './science-worlds.mjs';
import {buildWorld as legacy} from '/v4/worlds.mjs';
import {createWorlds as selectedWorlds} from '/enhanced/worlds.mjs';
import {refineWater,shoreReeds,WATER_FRAGMENT} from '/enhanced/surface.mjs';
import {smooth,clamp,footState,mammalState} from '/enhanced/motion.mjs';
import {hermite} from '/v4/direction.mjs';
const V=(...p)=>new T.Vector3(...p),sphere=new T.SphereGeometry(1,20,14);
const clay=await new T.TextureLoader().loadAsync('/materials/clay-albedo.jpg');clay.colorSpace=T.SRGBColorSpace;clay.wrapS=clay.wrapT=T.RepeatWrapping;clay.repeat.set(2.5,2.5);
const mat=(color,extra={})=>new T.MeshStandardMaterial({color,roughness:.9,...extra});
const stone=mat('#b0aa98',{map:clay,bumpMap:clay,bumpScale:.018}),soil=mat('#9a9985',{map:clay,bumpMap:clay,bumpScale:.035}),green=mat('#687450'),ivory=mat('#d5cdb2'),amber=mat('#bc9a5d'),cyan=mat('#81aaa1'),steel=mat('#6b8588',{metalness:.45,roughness:.5});
const glass=new T.MeshPhysicalMaterial({color:'#abc8c3',transparent:true,opacity:.22,roughness:.2,depthWrite:false,side:T.DoubleSide});
function mesh(p,g,m,x=0,y=0,z=0){const o=new T.Mesh(g,m);o.position.set(x,y,z);o.castShadow=o.receiveShadow=true;p.add(o);return o;}
function ball(p,m,pos,scale){const o=mesh(p,sphere,m,...pos);o.scale.set(...scale);return o;}
function box(p,m,pos,size){return mesh(p,new T.BoxGeometry(...size),m,...pos);}
function tube(p,pts,r,m){return mesh(p,new T.TubeGeometry(new T.CatmullRomCurve3(pts.map(a=>V(...a))),24,r,6,false),m);}
function pose(keys,t){const a=hermite(keys.map(([time,...value])=>({time,value})),t);return {position:a.slice(0,3),target:a.slice(3)};}
function setup(lab=false){const scene=new T.Scene();scene.background=new T.Color(lab?'#20383c':'#91aeb1');scene.fog=new T.FogExp2(scene.background,lab?.025:.014);scene.add(new T.HemisphereLight('#dce4d7','#343a32',1.7));const sun=new T.DirectionalLight('#f4d9aa',3.0);sun.position.set(-6,12,-4);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-12,right:12,top:12,bottom:-12,near:.1,far:50});sun.shadow.bias=-.0002;sun.shadow.normalBias=.025;scene.add(sun);const fill=new T.DirectionalLight('#b5d4cf',1.2);fill.position.set(6,5,7);scene.add(fill);return {scene,state:{},update:()=>{},labels:()=>[]};}
function bench(w){box(w.scene,steel,[0,.9,0],[7,.16,4]);box(w.scene,ivory,[0,1.0,0],[6.7,.06,3.7]);for(const x of [-2.7,2.7])box(w.scene,steel,[x,.38,0],[.12,1,3]);}
function shortTrace(parent,count=5){const g=new T.Group();parent.add(g);const units=[];for(let i=0;i<count;i++){const x=i*.20-(count-1)*.10;const a=box(g,i%3?amber:cyan,[x,.02,Math.sin(i*1.7)*.035],[.125,.055,.065]);a.rotation.y=i*.37;units.push(a);}return {group:g,units};}
function label(text,point,opacity=1){return {text,point,opacity};}
function paperLeaf(parent,pos=[0,0,0],scale=1){const g=new T.Group();g.position.set(...pos);parent.add(g);const sh=new T.Shape();sh.moveTo(0,-.35);sh.quadraticCurveTo(.26,0,0,.42);sh.quadraticCurveTo(-.23,0,0,-.35);const geo=new T.ShapeGeometry(sh,14);geo.rotateX(-Math.PI/2);mesh(g,geo,mat('#7c8460',{side:T.DoubleSide}));tube(g,[[0,.006,-.31],[0,.025,0],[0,.006,.36]],.008,ivory);g.scale.setScalar(scale);return g;}
let chosen;
function enhanced(){return chosen??=selectedWorlds();}
function fieldSection(){
 const w=setup(),p=w.scene;mesh(p,new T.PlaneGeometry(80,80).rotateX(-Math.PI/2),soil,0,-.04,0);
 for(let i=0;i<7;i++){const g=new T.BoxGeometry(8,.27,2.6,48,2,12),a=g.attributes.position;for(let j=0;j<a.count;j++)a.setY(j,a.getY(j)+.045*Math.sin(a.getX(j)*1.4+a.getZ(j)*.7));g.computeVertexNormals();const m=stone.clone();m.color.setHSL(.11,.13,.42+i*.026);mesh(p,g,m,0,.15+i*.27,-.7);}
 const tray=new T.Group();p.add(tray);box(tray,steel,[0,0,0],[.85,.06,.6]);const sample=mesh(tray,new T.IcosahedronGeometry(.24,2),soil,0,.1,0);sample.scale.y=.3;
 const remains=paperLeaf(p,[-1.4,1.42,.62],.85);remains.rotation.x=.85;
 w.qualifier='KAP KØBENHAVN · ILLUSTRATIVE EXPOSURE / PLANT REMAINS · NOT A MEASURED SECTION';
 w.update=t=>{const u=smooth((t-10)/6);tray.position.set(1.9+u*.5,.12+u*.7,1.5);remains.rotation.y=.06*Math.sin(t*.25);w.state={stage:'field-exposure',sample_separation:u,formation_age_not_molecule_date:true};};
 w.camera=t=>pose([[0,6.5,3.6,7,0,1,-.4],[8,5.8,3.4,6.4,-.5,1.05,-.25],[21,5.9,3.9,7.6,-.1,1,-.1]],t);
 w.labels=t=>[label(t<7.4?'REPORTED 2022 · KAP KØBENHAVN FORMATION':t<13?'VISIBLE PLANT REMAINS · ANOTHER LINE OF EVIDENCE':'SEDIMENT CONNECTS MULTIPLE CLUES',t<7.4?[1,1.5,.5]:[-1.4,1.42,.62],smooth(t/.8))];return w;
}
function molecular(kind){
 const w=setup(true),p=w.scene;box(p,steel,[0,-.24,0],[12,.2,9]);
 const host=mesh(p,new T.IcosahedronGeometry(1,4),stone,0,.1,0);host.scale.set(2.1,.37,1.3);
 const fragments=Array.from({length:7},(_,i)=>{const f=shortTrace(p,3+i%3);f.group.scale.setScalar(.65);return f;});
 const warm=mesh(p,new T.TorusGeometry(.95,.012,5,64),amber,0,.54,0);warm.rotation.x=-Math.PI/2;
 w.qualifier='CONCEPTUAL FRAGMENTS / MINERAL SURFACE · ENLARGED · NOT ACTUAL MOLECULAR FOOTAGE';
 w.update=(t,mode)=>{
  const clock=Math.min(t,10.3)+Math.max(0,t-10.3)*.12,damage=kind==='weather'?smooth((clock-2.5)/4):0,bind=kind==='mineral'?smooth((t-.4)/4):kind==='trace'?0:.2;
  for(let i=0;i<fragments.length;i++){
   const f=fragments[i],x=-1.5+i*.46,z=Math.sin(i*2.3)*.55;
   const contact=.1+.37*Math.sqrt(Math.max(0,1-(x/2.1)**2-(z/1.3)**2))+.035;f.group.position.set(x+(1-bind)*.07*Math.sin(clock*.3+i),contact+(1-bind)*(.45+.05*Math.sin(clock*.5+i)),z);f.group.rotation.set(.05,Math.sin(i)*.2+.10*Math.sin(t*.17+i),.03*Math.sin(t*.4));
   f.units.forEach((u,j)=>{const loss=damage*smooth((t-4-j*.6-i*.15)/2);u.scale.setScalar(j%3===1?1-loss*.35:1-loss*.95);u.position.z=Math.sin(j*1.7)*.035+loss*(j%2?.18:-.18);});
  }
  if(kind==='weather')for(let i=4;i<7;i++)fragments[i].group.scale.setScalar(.65*(1-.93*smooth((t-5-i*.12)/3)));
  warm.visible=kind==='mineral';warm.scale.setScalar(1+.025*Math.sin(t*.5));warm.material=amber;
  w.state={stage:kind,bind,damage,fragment_count_schematic:true,individual_molecule_dates:false};
 };
 w.camera=t=>pose([[0,3.7,2.1,4.0,0,.6,0],[5,3.2,1.8,3.8,0,.62,0],[16,2.7,1.9,3.6,0,.55,0],[26,3.1,2.4,4.2,0,.5,0]],t);
 w.labels=t=>kind==='mineral'?[label(t<9?'MINERAL BINDING · MAY AID SURVIVAL':'RETENTION ALSO COMPLICATES EXTRACTION',[0,.6,0],smooth(t/.7))]:kind==='weather'?[label(t<5?'BREAKAGE AND DAMAGE':t<10.3?'SURVIVAL IS SELECTIVE':'COLD MAY SLOW LOSS · NOT STOP IT',[-.8,1.0,.2],smooth(t/.7))]:[label('SURVIVING FRAGMENTS · NOT A COMPLETE GENOME',[0,.9,.2],smooth(t/.7))];return w;
}
function extraction(){
 const w=setup(true);bench(w);const p=w.scene;
 const vessel=mesh(p,new T.CylinderGeometry(.44,.44,.38,40),glass,-1.5,1.23,0);ball(p,soil,[-1.5,1.10,0],[.36,.055,.34]);
 const receiver=mesh(p,new T.CylinderGeometry(.22,.22,.52,30),glass,1.1,1.3,0);mesh(p,new T.CylinderGeometry(.18,.18,.13,30),cyan,1.1,1.12,0);
 const pip=new T.Group();p.add(pip);mesh(pip,new T.CylinderGeometry(.07,.07,.6,20),ivory,0,.3,0);mesh(pip,new T.CylinderGeometry(.035,.006,.35,20),glass,0,-.17,0);
 const drop=ball(p,cyan,[0,0,0],[.025,.055,.025]);const f=shortTrace(p,4);f.group.scale.setScalar(.45);
 w.qualifier='ILLUSTRATIVE EXTRACTION WORKFLOW · NOT STUDY FOOTAGE OR A CALIBRATED PROTOCOL';
 w.update=t=>{const lift=smooth((t-1)/2),travel=smooth((t-3.0)/3.2),dispense=smooth((t-6.2)/1.2);pip.position.set(-1.5+2.6*travel,1.75+.55*lift-.18*dispense,0);drop.visible=t>6.3&&t<7.5;drop.position.set(1.1,1.95-.55*smooth((t-6.3)/1.2),0);f.group.position.set(-1.5+2.6*travel,1.48+.5*Math.sin(Math.PI*travel),.03);f.group.rotation.y=.05*Math.sin(t*.3);w.state={stage:'extraction',transfer:travel,dispense};};
 w.camera=t=>pose([[0,3.6,2.7,4.3,-.7,1.5,0],[5,3.2,2.4,4,-.1,1.5,0],[16,3.8,2.8,4.4,.4,1.45,0]],t);
 w.labels=t=>[label(t<5?'RELEASE FROM SEDIMENT':'EXTRACTED MATERIAL · STILL MIXED',t<5?[-1.5,1.3,0]:[1.1,1.45,0],smooth(t/.7))];return w;
}
function references(kind){
 const w=setup(true);bench(w);const p=w.scene,refs=[];
 for(let i=0;i<3;i++){const z=-.85+i*.8;box(p,steel,[.5,1.09,z],[2.7,.05,.58]);const f=shortTrace(p,8);f.group.position.set(.5,1.16,z);refs.push(f);}
 // Empty third slot is a hypothetical missing reference, not an assertion about a particular species.
 refs[2].units.forEach(u=>u.visible=false);
 const candidate=shortTrace(p,4);const alternative=shortTrace(p,6);alternative.group.position.set(-1.8,1.25,-1.1);alternative.group.scale.setScalar(.65);
 const branch=new T.Group();branch.position.set(1.85,1.18,.6);p.add(branch);tube(branch,[[0,0,0],[0,.7,0],[-.6,1.15,0]],.025,amber);tube(branch,[[0,.7,0],[.6,1.15,0]],.025,cyan);
 w.qualifier='SCHEMATIC REFERENCE COMPARISON · NO RECOVERED SEQUENCE READS OR SPECIES SCORES';
 w.update=(t,mode)=>{
  const align=smooth((t-1)/5);candidate.group.position.set(-1.8+2.3*align,1.32,-.85+.8*smooth((t-12)/6));candidate.group.rotation.y=.03*Math.sin(t*.2);
  if(kind==='branch'){candidate.group.position.set(.5+1.35*smooth(t/6),1.3+.5*smooth(t/6),.25);branch.scale.setScalar(.8+.2*smooth(t/5));}
  else branch.scale.setScalar(.75);
  const damage=kind==='controls'?smooth((t-11)/4):0;alternative.units.forEach((u,j)=>{u.scale.setScalar(j===0||j===5?1-.8*damage:1);});
  alternative.group.position.y=1.25+.2*smooth((t-2)/4);w.state={stage:kind,alignment:align,damage_check:damage,reference_missing:true,identification_is_not_complete_genome:true};
 };
 w.camera=t=>kind==='branch'?pose([[0,4,3.2,4.6,.4,1.3,.2],[15,4.3,3.6,5.3,.8,1.55,.2]],t):pose([[0,3.7,3.2,4.2,0,1.2,0],[10,3.1,3.2,3.8,.3,1.2,-.3],[27,3.8,3.5,4.7,.3,1.3,.2]],t);
 w.labels=(t,mode)=>[label(kind==='branch'?'SUPPORTED BRANCH ≠ EXACT SPECIES':kind==='controls'?(t<11?'CHECK ALTERNATIVE EXPLANATIONS':'DAMAGE IS ONE CHECK, NOT PROOF ALONE'):mode==='family'?'RELATED REFERENCES CAN SHARE STRETCHES':t>17?'MISSING REFERENCE ≠ MISSING ANIMAL':'COMPARE SURVIVING FRAGMENTS',[.5,1.3,t>12?-.05:-.85],smooth(t/.8))];return w;
}
function records(kind){
 const w=setup(true);bench(w);const p=w.scene,groups=[],leaves=[],grains=[];
 for(let i=0;i<3;i++){
  const g=new T.Group();g.position.set(-2+i*2,1.10,0);p.add(g);box(g,steel,[0,0,0],[1.45,.05,1.9]);groups.push(g);
  if(i===0){for(let j=0;j<3;j++){const f=shortTrace(g,3+j%2);f.group.position.set(0,.14,-.55+j*.48);f.group.scale.setScalar(.65);}}
  if(i===1){for(let j=0;j<4;j++){const a=ball(g,amber,[(j%2-.5)*.42,.17,Math.floor(j/2)*.45-.3],[.11,.10,.11]);for(let k=0;k<9;k++){const q=k*2.4;ball(a,amber,[Math.sin(q)*.85,Math.cos(q)*.85,Math.sin(q*1.3)*.5],[.14,.14,.14]);}grains.push(a);}}
  if(i===2){leaves.push(paperLeaf(g,[0,.09,0],1.6));}
 }
 const failures=[];
 if(kind==='gaps')for(let i=0;i<3;i++){const f=shortTrace(p,4);f.group.scale.setScalar(.65);failures.push(f);}
 w.qualifier='SCHEMATIC COMPLEMENTARY RECORDS · NOT COUNTS, AN INVENTORY OR ACTUAL SPECIMENS';
 w.update=t=>{
  const offsets=kind==='proxies'?[smooth((t-7)/3),smooth((t-1)/3),smooth(t/3)]:kind==='integration'?[smooth(t/4),smooth((t-3)/4),smooth((t-5)/4)]:[.2,.2,.2];
  groups.forEach((g,i)=>{g.position.y=1.10+offsets[i]*.17;});grains.forEach((g,i)=>g.rotation.y=t*.12+i);leaves.forEach(l=>l.rotation.y=.04*Math.sin(t*.3));
  failures.forEach((f,i)=>{const u=smooth((t-(7+i*3.8))/3);f.group.position.set(-2+i*2,1.8-u*.3,-.8+u*1.1);f.units.forEach((a,j)=>a.scale.setScalar(i===0?1-u*.95:i===2&&j%2?1-u*.85:1));if(i===1)f.group.position.z=-.8+u*.45;});
  w.state={stage:kind,records_complementary:true,inventory_complete:false,missing_signal_not_absence:true};
 };
 w.camera=t=>pose([[0,4.4,3.4,5.7,0,1.25,0],[8,3.9,3.4,5.1,0,1.35,0],[24,4.6,3.9,6.0,0,1.3,0],[40,5,4,6.5,0,1.25,0]],t);
 w.labels=t=>kind==='gaps'?[label(t<9?'DID MATERIAL SURVIVE?':t<14?'DID IT REACH THE SAMPLE?':t<19?'COULD IT BE RECOGNISED?':'NO SIGNAL ≠ NO ANIMAL',[t<9?-2:t<14?0:2,1.8,0],smooth(t/.7))]:[label(kind==='boundary'?'EVIDENCE SUPPORTS A WORLD · NOT A RECOVERED AFTERNOON':kind==='integration'?'DIFFERENT METHODS · DIFFERENT GAPS':'DNA · POLLEN · VISIBLE REMAINS',[0,1.8,.1],smooth(t/.7))];return w;
}
function coast(kind){
 const w=setup(),p=w.scene,g=new T.PlaneGeometry(140,140,100,100);g.rotateX(-Math.PI/2);const a=g.attributes.position;for(let i=0;i<a.count;i++){const x=a.getX(i),z=a.getZ(i);a.setY(i,-.08+Math.max(0,(Math.hypot(x,z)-8)/25)*(.25*Math.sin(x*.35+z*.2)+.17*Math.sin(z*.6)));}g.computeVertexNormals();mesh(p,g,soil);
 const rocks=new T.InstancedMesh(new T.IcosahedronGeometry(1,2),stone,220),o=new T.Object3D();for(let i=0;i<220;i++){const x=Math.sin(i*127.1)*22,z=Math.cos(i*47.7)*23,r=.03+(i%9)*.035;o.position.set(x,-.055+r*.12,z);o.scale.set(r,r*.4,r*.8);o.rotation.set(i,.37*i,0);o.updateMatrix();rocks.setMatrixAt(i,o.matrix);}p.add(rocks);
 const waterMat=new T.ShaderMaterial({uniforms:{time:{value:0}},vertexShader:'uniform float time;varying vec3 v;varying vec3 wp;void main(){vec3 p=position;p.z+=.018*sin(p.x*2.+p.y+time*.8);v=p;wp=(modelMatrix*vec4(p,1.)).xyz;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}',fragmentShader:WATER_FRAGMENT});const tide=mesh(p,new T.PlaneGeometry(16,70,30,90),waterMat,15,-.04,0);tide.rotation.x=-Math.PI/2;
 const host=mesh(p,new T.IcosahedronGeometry(.44,3),stone,0,.07,0);host.scale.set(1,.26,.72);const trace=shortTrace(p,3);trace.group.scale.setScalar(.11);trace.group.position.set(0,.20,0);const returning=kind==='return-to-handful-scale';
 w.qualifier='NORTH GREENLAND · ILLUSTRATIVE LANDSCAPE / ENLARGED TRACE · NOT SITE FOOTAGE';
 w.update=t=>{if(returning)host.position.y=.07+.18*smooth((t-8)/5);waterMat.uniforms.time.value=t;tide.position.y=-.04+.008*Math.sin(t*.26);trace.group.rotation.y=.03*Math.sin(t*.3);w.state={stage:kind,tide_time:t,trace_is_enlarged:true};};
 w.camera=t=>kind==='closing'?pose([[0,2.8,1.8,3.5,0,.18,0],[10,3.6,2.2,4.5,0,.15,0],[20,7,4.7,10,0,.25,-1],[28,10,6.5,14,0,.35,-2]],t):kind==='present-polar-shore'?pose([[0,9,5,13,0,.4,-2],[12,8,4.4,11,0,.2,-1]],t):pose([[0,6.7,3.3,8.3,0,.18,-1],[10,3.2,1.7,4.0,0,.13,0],[17,2.3,1.3,2.8,0,.13,0]],t);
 w.labels=t=>kind==='closing'&&t>17?[label('AN INCOMPLETE RECORD',[0,.2,0],smooth((t-17)/1))]:[];return w;
}
function habitat(sequence){
 const kind=sequence.world,w=legacy({...sequence,world:'habit',design:kind==='canopy'?'last-green-canopy':kind==='community'?'open-river-terrace':'opening-tracks-clearing'}),original=w.update;
 // Clear a real camera/subject corridor, instead of letting random foreground trunks obscure the action.
 for(const g of w.scene.children){if(g.isGroup&&g.children.some(c=>c.isInstancedMesh&&[800,1000].includes(c.count))){if(kind!=='canopy'&&g.position.x>-13&&g.position.x<2&&g.position.z>-16&&g.position.z<8)g.visible=false;}}
 const sapling=new T.Group();sapling.position.set(-5,0,-1.3);w.scene.add(sapling);sapling.visible=kind==='community';tube(sapling,[[0,0,0],[.02,.8,0],[.12,1.45,0]],.014,green);for(let i=0;i<7;i++){const y=.55+i*.12,l=paperLeaf(sapling,[Math.sin(i*2.4)*.18,y,Math.cos(i*2.4)*.15],.7);l.rotation.y=i*2.4;l.rotation.x=.5;}
 w.scene.traverse(o=>{if(o.material)refineWater(o.material);});
 const reeds=kind==='community'?shoreReeds(w.scene,z=>5-.9*Math.sin(z*.12),()=>-.045,{halfWidth:1.6,range:6,count:240}):()=>{};
 w.qualifier='ILLUSTRATIVE COMMUNITY / APPEARANCE · NOT AN OBSERVED ENCOUNTER OR COMPLETE INVENTORY';
 w.update=(t,mode)=>{
  original(t,'wide',t,sequence.chapter);reeds(t);const m=w.actors.mastodon,s=mammalState(t);m.userData.update(t,true);m.position.set(...s.position);m.position.y=-.045;m.rotation.y=0;
  Object.entries(w.actors).forEach(([name,a])=>a.visible=kind==='community'||name==='mastodon'&&kind==='opening');
  if(kind==='community'){
   const d=w.actors.reindeer;const stop=clamp((t-10)/4),walk=t<10?t:10+4*(stop-stop**3+.5*stop**4);d.position.set(-5,-.035,1-walk*.108);d.rotation.y=0;d.userData.update(walk,1-smooth(stop));const browse=smooth((t-12)/3)*(1-.15*smooth((t-26)/3));d.userData.head.rotation.x=.22*browse+.02*browse*Math.sin(t*1.2);d.userData.head.position.y=1.53-.12*browse; // overridden enhanced reindeer uses the same compensated stance scheme.
   w.actors.hare.userData.update(Math.min(t,6));w.actors.hare.position.set(-.7,.05+((t>1&&t<5)?.12*Math.sin((t-1)*Math.PI)**2:0),1.5-.12*Math.min(4,Math.max(0,t-1)));
   w.actors.rodent.position.set(1.3+.5*smooth((t-3)/2),.0,.6);w.actors.goose.userData.update(t,false,0);w.actors.goose.position.set(4.3,-.08,.7);
  }
  w.state={stage:kind,mastodon_position:m.position.toArray(),subject_motion_not_just_camera:true};
 };
 w.camera=t=>kind==='opening'?pose([[0,-6.4,2.8,-5.8,-1.7,1.8,.4],[4,-6.2,2.8,-6.2,-1.7,1.8,.2]],t):kind==='canopy'?pose([[0,-8,4.8,-9,-4,2.7,-4],[13,-9,5.7,-12,-3.3,2.4,-5]],t):pose([[0,-9,2.1,-5,-4,1.1,0],[7,-8,2.6,-5,-4.5,1.4,-.7],[16,-9,3.4,-7,-3,1.3,-1.7],[31,-11,4.8,-11,-2.4,1.4,-4]],t);
 w.labels=t=>kind==='community'?[label(t<6?'DNA EVIDENCE · MULTIPLE ANIMAL LINEAGES':t<15?'PLANTS AND ANIMALS · A DIFFERENT COMMUNITY':'NOT A COPY OF ONE MODERN FOREST',[-2,4.0,-2],smooth(t/.8))]:[];return w;
}
const KIT={T,V,setup,bench,mesh,ball,box,tube,shortTrace,paperLeaf,stone,soil,green,ivory,amber,cyan,steel,glass,pose,smooth,label,mat,WATER_FRAGMENT};
export function buildWorld(sequence){
 const k=sequence.world;
 if(k==='trace')return science.fragments(KIT,sequence.design);
 if(['mineral','controls','branch','boundary','gaps','integration'].includes(k))return science[k](KIT);
 if(k==='river'||k==='section'||k==='encounter'){
  const original=enhanced()[k==='section'?'deposits':k==='encounter'?'living':'river'];
  if(k==='section'&&sequence.design==='formation-and-plant-evidence')return fieldSection();
  original.persistent=true;
  if(k!=='encounter')return original;
  const wrapper={...original,camera:t=>pose([[0,-7,3,-8.3,-.4,1.5,0],[4,-6.5,2.9,-8,-.2,1.45,-.3],[8,-5.8,3.2,-8.8,.5,1.5,-1],[13,-5.1,3.7,-9.6,.6,1.6,-1.8],[23,-4.5,3.8,-11,.1,1.4,-2.7],[31,-5,3.9,-13,-1,1.4,-4.5],[40,-6,4,-15,-1.3,1.4,-6.7]],t),update:t=>{original.update(t);wrapper.state=original.state;}};return wrapper;
 }
 if(['opening','community','canopy'].includes(k))return habitat(sequence);
 if(['trace','weather','mineral'].includes(k))return molecular(k);
 if(k==='extraction'||k==='shedding'){
  if(k==='extraction')return sequence.design==='sample-to-question'?science.sampleArrival(KIT):extraction();
  const w=habitat({...sequence,world:'opening'});const initial=w.update;const f=shortTrace(w.scene,4);f.group.scale.setScalar(.2);w.update=t=>{initial(t);f.group.position.set(-1.1+1.3*smooth((t-2)/5),.4+.6*(1-smooth((t-2)/5)),1.2);w.state.stage='shedding';};w.labels=t=>[label('BIOLOGICAL MATERIAL · ENLARGED TRACE MARKERS',[-.4,.8,1.2],smooth((t-1)/.8))];return w;
 }
 if(['reference','controls','branch'].includes(k))return references(k);
 if(['proxies','boundary','gaps','integration'].includes(k))return records(k);
 if(k==='coast')return coast(sequence.design);
 if(k==='closing')return coast('closing');
 throw Error('Unimplemented full-film stage '+k);
}
