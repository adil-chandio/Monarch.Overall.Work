// Authored conceptual 3D explanations. Every arrangement is illustrative, never measured data.
import * as T from 'three';
import {animal} from './assets.mjs';
import {smooth as S} from './motion.mjs';
const V=(...v)=>new T.Vector3(...v), mix=(a,b,t)=>a+(b-a)*S(t);
const ink=new T.MeshStandardMaterial({color:'#223e45',roughness:.7});
const paper=new T.MeshStandardMaterial({color:'#d4d9ca',roughness:.8});
const gold=new T.MeshStandardMaterial({color:'#d8b576',roughness:.43});
const teal=new T.MeshStandardMaterial({color:'#72bcb1',roughness:.42});
const rust=new T.MeshStandardMaterial({color:'#d78161',roughness:.55});
const glass=new T.MeshPhysicalMaterial({color:'#c4e4dc',transparent:true,opacity:.16,roughness:.15,depthWrite:false,side:T.DoubleSide});
function mesh(p,g,m,pos=[0,0,0]){const o=new T.Mesh(g,m);o.position.set(...pos);o.castShadow=o.receiveShadow=true;p.add(o);return o;}
const box=(p,pos,size,m=paper)=>mesh(p,new T.BoxGeometry(...size),m,pos);
const ball=(p,pos,r=.07,m=teal)=>mesh(p,new T.SphereGeometry(r,16,12),m,pos);
function line(p,a,b,m=gold,r=.018){const u=V(...a),v=V(...b),o=mesh(p,new T.CylinderGeometry(r,r,u.distanceTo(v),10),m);o.position.copy(u).add(v).multiplyScalar(.5);o.quaternion.setFromUnitVectors(V(0,1,0),v.sub(u).normalize());return o;}
function fragment(p,pos,size=1){const g=new T.Group();p.add(g);g.position.set(...pos);g.scale.setScalar(size);for(let i=0;i<5;i++){const y=(i-2)*.09,a=i*.9;ball(g,[.13*Math.cos(a),y,.13*Math.sin(a)],.025,teal);ball(g,[-.13*Math.cos(a),y,-.13*Math.sin(a)],.025,gold);line(g,[.13*Math.cos(a),y,.13*Math.sin(a)],[-.13*Math.cos(a),y,-.13*Math.sin(a)],paper,.012);if(i){const q=(i-1)*.9;line(g,[.13*Math.cos(q),y-.09,.13*Math.sin(q)],[.13*Math.cos(a),y,.13*Math.sin(a)],teal,.018);line(g,[-.13*Math.cos(q),y-.09,-.13*Math.sin(q)],[-.13*Math.cos(a),y,-.13*Math.sin(a)],gold,.018);}}return g;}
function leaf(p,pos){const shape=new T.Shape();shape.moveTo(0,-.32);shape.quadraticCurveTo(.36,-.02,0,.38);shape.quadraticCurveTo(-.36,-.02,0,-.32);const g=new T.Group();g.position.set(...pos);p.add(g);mesh(g,new T.ShapeGeometry(shape,20),new T.MeshStandardMaterial({color:'#859958',roughness:.8,side:T.DoubleSide}));line(g,[0,-.3,.008],[0,.32,.008],paper,.009);return g;}
function vessel(p,x){const g=new T.Group();p.add(g);g.position.set(x,.95,0);mesh(g,new T.CylinderGeometry(.28,.28,.58,40,1,true),glass,[0,.3,0]);mesh(g,new T.CylinderGeometry(.29,.29,.06,40),ink,[0,.62,0]);mesh(g,new T.CylinderGeometry(.27,.27,.04,40),paper);return g;}
function foundation(s){const scene=new T.Scene();scene.background=new T.Color('#132c32');scene.fog=new T.FogExp2('#132c32',.016);scene.add(new T.HemisphereLight('#d9ebe0','#26312c',1.8));const key=new T.DirectionalLight('#ffe5b8',2.6);key.position.set(-3,6,4);key.castShadow=true;key.shadow.mapSize.set(1536,1536);Object.assign(key.shadow.camera,{left:-6,right:6,top:6,bottom:-6,near:.1,far:25});key.shadow.bias=-.0002;key.shadow.normalBias=.015;scene.add(key);const rim=new T.DirectionalLight('#80babd',1.6);rim.position.set(4,3,-2);scene.add(rim);box(scene,[0,.78,0],[6.2,.18,2.8],ink);box(scene,[0,-.1,0],[30,.15,30],ink);const w={scene,state:{},labels:()=>[],qualifier:'CONCEPTUAL EXPLANATION • not experimental data • symbols not to scale',directedScience:true,update:()=>{},camera:t=>({position:[.12*Math.sin(t*.08),2.35,3.65],target:[0,1.65,0]})};return w;}
export function buildScience(s){const w=foundation(s),p=w.scene,kind=s.world,labels=[];const L=(text,point)=>({text,point,opacity:1});
 if(kind==='extraction'){
  const a=vessel(p,-1.7),b=vessel(p,0),c=vessel(p,1.7);for(let i=0;i<8;i++)ball(a,[(i%3-1)*.1,.12+Math.floor(i/3)*.07,0],.065,gold);
  const bits=Array.from({length:6},(_,i)=>fragment(p,[-1.7,1.2+i*.06,0],.35));
  const tip=mesh(p,new T.CylinderGeometry(.025,.008,.45,16),paper);line(p,[-1.35,.96,.45],[-.4,.96,.45],gold);line(p,[.4,.96,.45],[1.35,.96,.45],teal);
  w.update=t=>{const u=S((t-1.5)/4),v=S((t-7)/3.5);tip.position.set(mix(-1.7,0,(t-1)/4),1.9-.14*Math.sin(Math.min(t,5)/5*Math.PI),0);bits.forEach((o,i)=>{o.position.set(mix(-1.7,0,u)+1.7*v,1.23+(i%3)*.085+.22*Math.sin(u*Math.PI),((i%2)-.5)*.13);});w.state={stage:kind,operation:t<5?'release':t<8?'separate':'prepare',specific_action:true};};
  w.labels=t=>[L('Sediment',[-2.05,1.65,0]),L(t<6?'Release fragments':'Separate material',[-.5,2.15,0]),L('For comparison',[1.15,1.65,0])];
 }else if(kind==='reference'){
  const rows=[];for(let r=0;r<3;r++){const row=[];for(let i=0;i<9;i++)row.push(box(p,[-1.3+i*.3,1.15+r*.36,0],[.23,.18,.12],(i+r)%3?teal:gold));rows.push(row);}
  const pieces=Array.from({length:4},(_,i)=>box(p,[-1.3+i*.3,2.45,.1],[.23,.18,.14],i%3?teal:gold));
  const bracket=line(p,[-1.45,1.36,.2],[1.35,1.36,.2],gold,.025);
  w.update=t=>{const u=S((t-3)/7);pieces.forEach((o,i)=>o.position.set(-1.3+i*.3+.6*u,2.45-.94*u,.25));rows.forEach((row,r)=>row.forEach(o=>o.scale.setScalar(r===1?1:1-.5*S((t-11)/3))));bracket.scale.y=.1+.9*S((t-10)/3);rows[2].forEach(o=>o.visible=t<17.67);w.state={stage:kind,comparison_alignment:u,illustrative_not_sequence_reads:true};};
  w.labels=t=>[L('Fragment',[-1.8,2.5,.1]),L(t<10.77?'Compare reference alternatives':t<12.07?'Look for matches':t<17.67?'Relatives can share similar stretches':t<20.87?'A needed reference may be missing':'A lineage, not necessarily an exact species',[-1.5,2.95,0]),L('Alternatives remain context',[-1.6,.93,.4])];
 }else if(kind==='controls'){
  const left=vessel(p,-1.2),right=vessel(p,1.2);const sample=Array.from({length:4},(_,i)=>fragment(p,[-1.3+(i%2)*.18,1.18+Math.floor(i/2)*.18,0],.35));
  const contamination=fragment(p,[1.2,2.3,0],.65);contamination.traverse(o=>{if(o.isMesh)o.material=rust;});
  const ancient=fragment(p,[-1.05,1.55,0],1.5),modern=fragment(p,[1.05,1.55,0],1.5);const ends=[];for(const side of [-1,1])ends.push(ball(p,[-1.05+side*.14,1.55+side*.29,.10],.055,rust));
  w.update=t=>{const damage=t>=12.5;left.visible=right.visible=!damage;sample.forEach(o=>o.visible=!damage);contamination.visible=!damage&&t>1;contamination.position.y=mix(2.3,1.28,(t-1)/4);ancient.visible=modern.visible=damage;ends.forEach(o=>o.visible=damage);w.state={stage:kind,control_phase:damage?'characteristic-damage-assessment':'alternative-source-contamination',hypothetical_example:true,damage_is_not_standalone_proof:true};};
  w.labels=t=>t<12.5?[L('Candidate trace',[-1.75,1.9,0]),L('Alternative source',[.65,1.9,0]),L(t<5.87?'Modern contamination can mimic a match':'Ask what else could explain the signal',[-1.95,2.7,0])]:[L('Characteristic damage',[-1.9,2.1,0]),L('Comparison',[.6,2.1,0]),L('One authenticity check, alongside filtering',[-1.9,2.8,0])];
 }else if(kind==='branch'){
  const root=[0,1,0],fork=[0,1.7,0];line(p,root,fork);line(p,fork,[-1.3,2.4,0],teal,.027);line(p,fork,[1.3,2.4,0],paper,.027);line(p,[-1.3,2.4,0],[-1.9,2.8,0],teal);line(p,[-1.3,2.4,0],[-.7,2.8,0],paper);const f=fragment(p,[0,1,0],.7);
  w.update=t=>{const u=S((t-1)/7);f.position.set(-1.0*u,1+1.15*u,.2);w.state={stage:kind,lineage_assignment:true,exact_species_not_claimed:true};};
  w.labels=t=>[L('Supported lineage',[-2.0,2.1,.1]),L('Not an exact recovered species',[.0,3.1,0])];
 }else if(kind==='proxies'||kind==='integration'){
  const positions=[-1.7,0,1.7];const f=fragment(p,[-1.7,1.5,0],1.1);const pollen=ball(p,[0,1.5,0],.28,gold);for(let i=0;i<7;i++){const a=i*Math.PI*2/7;mesh(p,new T.TorusGeometry(.20,.018,8,32),paper,[Math.sin(a)*.08,1.5+Math.cos(a)*.06,.12]).rotation.y=a;}
  const l=leaf(p,[1.7,1.5,0]);const panels=positions.map(x=>box(p,[x,1,.15],[1.15,.06,1.05],paper));
  if(kind==='integration'){for(let i=0;i<3;i++){line(p,[positions[i],1.25,-.1],[0,2.4,-.3],teal,.012);}ball(p,[0,2.4,-.3],.15,gold);}
  w.update=t=>{f.rotation.y=.18*Math.sin(t*.4);pollen.rotation.y=t*.12;l.rotation.y=.12*Math.sin(t*.3);panels.forEach((o,i)=>o.position.y=1+.045*S((t-i*3)/2));w.state={stage:kind,complementary_evidence:true,no_inventory_counts:true};};
  w.labels=t=>kind==='integration'?[L('Different clues, shared limits',[-1.8,2.9,0]),L('Not a complete inventory',[-1.2,.85,.8])]:[L('DNA',[-1.95,2.05,0]),L('Pollen',[-.3,2.05,0]),L('Remains',[1.4,2.05,0]),L('Complementary, incomplete evidence',[-1.7,2.7,0])];
  if(kind==='proxies')w.camera=t=>{const focus=t<9?-1.15:t<18?0:1.15;return {position:[focus*.32,2.3,3.7],target:[focus*.35,1.65,0]};};
 }else if(kind==='gaps'){
  const moving=Array.from({length:10},(_,i)=>fragment(p,[-2.0+(i%5)*.18,1.25+Math.floor(i/5)*.32,0],.35));const arrivals=Array.from({length:4},(_,i)=>fragment(p,[1.1+i*.18,1.2,0],.35));arrivals.forEach(o=>o.traverse(c=>{if(c.isMesh)c.material=gold;}));
  const missing=box(p,[1.5,1.9,0],[.8,.14,.08],ink);line(p,[-1.9,.94,.3],[1.9,.94,.3],paper,.012);
  w.update=t=>{moving.forEach((o,i)=>{o.visible=t<8.93?i<4:t<13.47?i<10-Math.floor(S((t-8.93)/4.54)*5):true;o.position.set(t<13.47?-1.9+(i%5)*.18:mix(-1.8,.3,(t-13.47)/2.66)+(i%5)*.18,1.25+Math.floor(i/5)*.32,0);});arrivals.forEach(o=>o.visible=t>13.47&&t<16.13);missing.visible=t>16.13;w.state={stage:kind,limitation:t<8.93?'missing-signal':t<13.47?'survival':t<16.13?'transport':'reference-gaps',not_measured_loss_rates:true};};
  w.labels=t=>[L(t<8.93?'Missing DNA does not mean a missing organism':t<13.47?'Some material does not survive':t<16.13?'Some material never reaches the sample':t<19.67?'Some surviving fragments are unrecognised':'No signal is not the same as no animal',[-2.15,2.35,0]),L('Schematic, not measured proportions',[-1.9,2.8,0])];
 }else if(kind==='boundary'){
  const model=animal('mastodon');model.scale.setScalar(.38);model.position.set(-.9,.9,0);model.rotation.y=.3;p.add(model);const evidence=fragment(p,[1.65,1.45,0],1.1);line(p,[.8,.95,-.5],[.8,2.6,-.5],paper,.012);
  w.update=t=>{model.userData.update(t,{walk:0,browse:.2*S((t-3)/3)});model.traverse(o=>{if(o.isMesh){o.material.transparent=true;o.material.opacity=1-.77*S((t-8)/5);}});evidence.rotation.y=t*.1;w.state={stage:kind,reconstruction_is_not_recovery:true};};
  w.labels=t=>[L(t<8?'An illustration':'Not a recovered portrait',[-1.9,2.75,0]),L('Fragmentary evidence',[.95,2.05,0])];
 }
 return w;
}

export function buildMicro(s){const w=foundation(s),p=w.scene,kind=s.world;w.directedScience=true;w.qualifier='CONCEPTUAL MAGNIFICATION • enlarged symbols • not a literal molecular image';
 if(kind==='section'){
  const layers=Array.from({length:4},(_,i)=>{const m=new T.MeshStandardMaterial({color:['#756a56','#95816a','#a99778','#c0b090'][i],roughness:1});return box(p,[0,.95+i*.22,0],[4.2,.2,1.8],m);});
  const bits=Array.from({length:5},(_,i)=>fragment(p,[-1.4+i*.65,2.3,.65],.5));
  w.update=t=>{layers.forEach((o,i)=>{o.visible=i===0||t>2+i*1.3;o.position.y=.95+i*.22;});bits.forEach((o,i)=>o.position.y=mix(2.3,1.08,(t-.3-i*.12)/2));w.state={stage:kind,conceptual_burial:true,individual_fragment_date_not_claimed:true};};
  w.labels=t=>[{text:t<5?'Material enters a deposit':'Later sediment buries earlier material',point:[-1.9,2.8,0]},{text:'Deposit age is context, not a direct date for each fragment',point:[-2.2,.8,.7]}];
 }else{
  const surface=mesh(p,new T.SphereGeometry(1,32,20),new T.MeshStandardMaterial({color:'#9c9175',roughness:.94}),[0,.9,0]);surface.scale.set(2.2,.19,1.1);
  const bits=Array.from({length:8},(_,i)=>fragment(p,[-1.65+(i%4)*.48,1.25+Math.floor(i/4)*.5,0],1.15));
  w.update=t=>{bits.forEach((o,i)=>{const protectedSide=i%4>=2;const loss=kind==='weather'?S((t-2)/6):kind==='mineral'?(protectedSide?0:S((t-3)/8)):0;o.scale.setScalar(1.15*(1-loss));o.position.y=1.25+Math.floor(i/4)*.5+(kind==='mineral'&&protectedSide?-.14*S(t/3)+.10*S((t-11.47)/3):0);o.rotation.y=.12*Math.sin(t*.3+i);});w.state={stage:kind,conceptual_preservation:true,not_measured_survival:true};};
  w.labels=t=>kind==='mineral'?[{text:'Unprotected traces',point:[-2.1,2.4,0]},{text:t<11.47?'Mineral association can help preservation':'Binding can also hinder recovery',point:[.0,2.8,0]}]:[{text:kind==='weather'?'Most traces do not survive':'A fragment, not a whole genome',point:[-1.8,2.7,0]}];
 }
 w.camera=t=>({position:[.18*Math.sin(t*.08),2.6,4.0],target:[0,1.6,0]});return w;
}
