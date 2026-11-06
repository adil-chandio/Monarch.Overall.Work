// Original articulated 3D lineage stand-ins, not recovered portraits or simulation.
import * as T from 'three';
import {sculpt} from './sculpt.mjs';
import {footState} from '/motion.mjs';
const sphere=new T.SphereGeometry(1,28,20), eyeMat=new T.MeshPhysicalMaterial({color:0x10110e,roughness:.08,clearcoat:1});
const bone=new T.MeshStandardMaterial({color:0xe4d2ac,roughness:.38}),dark=new T.MeshStandardMaterial({color:0x292823,roughness:.8});
function skin(color){const cv=document.createElement('canvas');cv.width=cv.height=256;const c=cv.getContext('2d');c.fillStyle='#888';c.fillRect(0,0,256,256);for(let i=0;i<8500;i++){let x=(i*97.17)%256,y=(i*71.93)%256;c.fillStyle=`rgba(${i%2?220:20},${i%2?220:20},${i%2?220:20},.12)`;c.fillRect(x,y,1+(i%3),1);}const tx=new T.CanvasTexture(cv);tx.wrapS=tx.wrapT=T.RepeatWrapping;tx.repeat.set(3,2);return new T.MeshStandardMaterial({color,roughness:.88,bumpMap:tx,bumpScale:.045});}
function ell(parent,mat,x,y,z,sx,sy,sz){const m=new T.Mesh(sphere,mat);m.position.set(x,y,z);m.scale.set(sx,sy,sz);m.castShadow=m.receiveShadow=true;parent.add(m);return m;}
function tube(parent,points,r,mat,end=.1){const curve=new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p)));const g=new T.TubeGeometry(curve,40,r,12,false);const p=g.attributes.position;for(let i=0;i<p.count;i++){const u=Math.floor(i/13)/40,center=curve.getPointAt(Math.min(1,u)),v=new T.Vector3(p.getX(i),p.getY(i),p.getZ(i));v.sub(center).multiplyScalar(1-u*(1-end)).add(center);p.setXYZ(i,v.x,v.y,v.z);}g.computeVertexNormals();const m=new T.Mesh(g,mat);m.castShadow=true;parent.add(m);return m;}
function segment(parent,a,b,width,mat){const len=a.distanceTo(b),m=ell(parent,mat,0,0,0,width,len*.55,width*.91);m.position.copy(a).add(b).multiplyScalar(.5);m.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),b.clone().sub(a).normalize());return m;}
function link(mesh,a,b,width){mesh.position.copy(a).add(b).multiplyScalar(.5);mesh.scale.set(width,a.distanceTo(b)*.57,width*.91);mesh.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),b.clone().sub(a).normalize());}
export function mastodon(){
 const root=new T.Group(),torso=new T.Group();root.add(torso);const mat=skin('#716657'),earMat=skin('#807060');
 sculpt(torso,[[0,2.4,0,1,1.05,1.57],[0,2.55,-.87,.88,1.02,.82],[0,2.16,1.04,.84,.86,.82]],mat,[0,2.25,0],2.8,72);
 const head=new T.Group();head.position.set(0,2.9,-1.5);torso.add(head);sculpt(head,[[0,0,0,.64,.65,.7],[0,-.33,-.4,.45,.52,.43]],mat,[0,-.1,-.1],1.5,60);
 // Small fan-shaped ears, broad low head and less-curled tusks distinguish the stand-in from a woolly mammoth.
 const ears=[];for(const side of [-1,1]){const e=new T.Group();e.position.set(side*.57,-.04,.12);head.add(e);e.scale.set(.65,.8,.65);const sh=new T.Shape();sh.moveTo(0,.4);sh.bezierCurveTo(side*.66,.58,side*.83,-.1,side*.48,-.68);sh.bezierCurveTo(side*.16,-.82,0,-.5,0,.4);const eg=new T.ExtrudeGeometry(sh,{depth:.065,bevelEnabled:true,bevelThickness:.035,bevelSize:.035,bevelSegments:3,steps:1,curveSegments:20});const em=new T.Mesh(eg,earMat);em.castShadow=true;e.add(em);ears.push(e);
  ell(head,dark,side*.53,.02,-.47,.07,.045,.04);ell(head,eyeMat,side*.59,.025,-.48,.029,.025,.028);ell(head,bone,side*.615,.048,-.5,.012,.009,.01);
  tube(head,[[side*.32,-.42,-.47],[side*.48,-.68,-.9],[side*.57,-.69,-1.4],[side*.56,-.47,-1.83]],.12,bone,.025);
 }
 const trunk=new T.Group();head.add(trunk);
 const trunkCurve=new T.CatmullRomCurve3(Array.from({length:17},(_,i)=>new T.Vector3(0,-.4-i*.13,-.65-.08*Math.sin(i*.13))));
 const trunkGeo=new T.TubeGeometry(trunkCurve,48,.2,16,false),trunkMesh=new T.Mesh(trunkGeo,mat);trunk.add(trunkMesh);trunkMesh.castShadow=true;
 function updateTrunk(t){const centers=Array.from({length:49},(_,i)=>{const u=i/48;return new T.Vector3(.09*Math.sin(t*.8-u*1.4)*u,-.42-u*2.05,-.65-.11*Math.sin(u*2)+.12*Math.sin(t*.65+u)*u);});const a=trunkGeo.attributes.position;for(let i=0;i<49;i++){const c=centers[i],r=.205-i/48*.145;for(let j=0;j<=16;j++){const angle=j/16*Math.PI*2;a.setXYZ(i*17+j,c.x+Math.cos(angle)*r,c.y,c.z+Math.sin(angle)*r);}}a.needsUpdate=true;trunkGeo.computeVertexNormals();}
 const tail=new T.Group();tail.position.set(0,2.3,1.65);torso.add(tail);tube(tail,[[0,0,0],[.1,-.65,.15],[.12,-1.25,.18]],.055,mat,.5);ell(tail,dark,.12,-1.25,.18,.09,.17,.09);
 const legs=[];for(const side of [-1,1])for(const z of [-.93,1.02]){const x=side*.62,a=new T.Vector3(x,2.1,z),b=new T.Vector3(x,1.14,z+.05),d=new T.Vector3(x,.25,z),upper=segment(root,a,b,.28,mat),lower=segment(root,b,d,.22,mat),foot=ell(root,mat,x,.18,z,.29,.22,.33);for(let k=-1;k<=1;k++)ell(foot,bone,k*.36,-.15,-.8,.15,.12,.12);const knee=ell(root,mat,x,1.14,z,.24,.26,.25);legs.push({x,z,upper,lower,foot,knee,phase:(side>0?Math.PI:0)+(z>0?Math.PI/2:0)});}
 root.userData.rig={head,torso,legs};
 root.userData.update=(t,walk=true)=>{
  torso.position.y=.018*Math.sin(t*3.4);torso.rotation.z=.005*Math.sin(t*1.7);
  head.rotation.y=.025*Math.sin(t*.65);head.rotation.x=.015*Math.sin(t*.8);tail.rotation.z=.12*Math.sin(t*1.5);ears.forEach((e,i)=>e.rotation.y=(i?-.22:.22)+.04*Math.sin(t*1.1+i));updateTrunk(t);
  for(const l of legs){
   const state=walk?footState(t,l.phase/(2*Math.PI)):{z:0,lift:0,pitch:0,stance:true};
   const a=new T.Vector3(l.x,2.15,l.z),d=new T.Vector3(l.x,.22+state.lift,l.z+state.z),axis=d.clone().sub(a),length=axis.length(),dir=axis.clone().normalize();
   const L1=1.08,L2=1.02,k=(L1*L1-L2*L2+length*length)/(2*length),h=Math.sqrt(Math.max(0,L1*L1-k*k));
   const bend=new T.Vector3(0,-dir.z,dir.y).normalize(),b=a.clone().addScaledVector(dir,k).addScaledVector(bend,h*.65);
   link(l.upper,a,b,.285);link(l.lower,b,d,.225);l.knee.position.copy(b);l.foot.position.copy(d);l.foot.rotation.x=state.pitch;
   l.state=state;
  }
 };

 return root;
}
export function reindeer(){
 const root=new T.Group(),body=new T.Group();root.add(body);const mat=skin('#796e5a'),pale=skin('#b2ad98');sculpt(body,[[0,1.13,0,.33,.42,.75],[0,1.4,-.56,.23,.5,.28]],mat,[0,1.2,0],1.6,60);ell(body,pale,0,1.42,-.73,.16,.32,.12).rotation.x=-.25;const head=new T.Group();head.position.set(0,1.85,-.83);body.add(head);sculpt(head,[[0,0,-.04,.145,.24,.29],[0,-.1,-.26,.115,.115,.2]],mat,[0,0,-.15],.6,44);ell(head,dark,0,-.09,-.37,.115,.09,.12);for(const side of [-1,1]){ell(head,eyeMat,side*.15,.02,-.16,.033,.04,.035);ell(head,mat,side*.24,.21,.02,.13,.065,.2).rotation.z=side*.4;tube(head,[[side*.1,.18,.08],[side*.22,.55,.17],[side*.35,.96,.03],[side*.49,1.2,-.22]],.035,bone,.08);for(let j=0;j<3;j++)tube(head,[[side*(.21+j*.11),.51+j*.2,.1],[side*(.38+j*.1),.76+j*.22,-.15]],.018,bone,.1);}
 const legs=[];for(const side of [-1,1])for(const z of [-.5,.5]){const x=side*.22,a=new T.Vector3(x,1.03,z),b=new T.Vector3(x,.55,z),d=new T.Vector3(x,.05,z);legs.push({x,z,phase:(side>0?Math.PI:0)+(z>0?Math.PI/2:0),u:segment(root,a,b,.062,mat),l:segment(root,b,d,.041,pale),foot:ell(root,dark,x,.07,z,.07,.08,.11)});}ell(body,pale,0,1.24,.78,.1,.08,.17);
 root.userData.head=head;root.userData.update=(t,walking=1)=>{body.position.y=.012*Math.sin(t*3.4);head.rotation.y=.08*Math.sin(t*.4);legs.forEach(q=>{const state=footState(t,q.phase/(2*Math.PI)),a=new T.Vector3(q.x,1.03,q.z),d=new T.Vector3(q.x,.07+state.lift*.45*walking,q.z+state.z*.45*walking),dir=d.clone().sub(a).normalize(),distance=a.distanceTo(d),k=(.55*.55-.50*.50+distance*distance)/(2*distance),h=Math.sqrt(Math.max(0,.55*.55-k*k)),bend=new T.Vector3(0,-dir.z,dir.y).normalize(),b=a.clone().addScaledVector(dir,k).addScaledVector(bend,h*.65);link(q.u,a,b,.062);link(q.l,b,d,.041);q.foot.position.copy(d);});};return root;
}
export function hare(){const root=new T.Group(),mat=skin('#bdb9a8');sculpt(root,[[0,.28,0,.18,.23,.32],[0,.44,-.2,.14,.15,.18],[0,.46,-.31,.09,.09,.11]],mat,[0,.35,0],.7,50);ell(root,paleMat(),0,.3,.31,.1,.1,.1);for(const side of [-1,1]){ell(root,mat,side*.08,.76,-.23,.044,.27,.065).rotation.z=side*.15;ell(root,eyeMat,side*.13,.52,-.33,.023,.03,.02);ell(root,mat,side*.14,.13,.16,.115,.12,.2);ell(root,mat,side*.09,.06,-.19,.055,.06,.14);}root.userData.update=t=>{const p=t*2.2,hop=Math.max(0,Math.sin(p));root.position.y=.13*hop;root.rotation.x=.12*Math.sin(p);};return root;}
function paleMat(){return new T.MeshStandardMaterial({color:0xc6c0aa,roughness:.9});}
export function rodent(){const root=new T.Group(),mat=skin('#6e6252');ell(root,mat,0,.13,0,.11,.12,.23);ell(root,mat,0,.17,-.2,.1,.1,.12);for(const s of [-1,1]){ell(root,paleMat(),s*.075,.26,-.16,.065,.07,.022);ell(root,eyeMat,s*.075,.2,-.255,.018,.019,.018);for(const z of [-.1,.13])ell(root,dark,s*.09,.035,z,.03,.025,.07);}tube(root,[[0,.13,.2],[.07,.05,.4],[.27,.04,.5],[.37,.035,.4]],.014,mat,.2);root.userData.update=t=>{root.rotation.y=.09*Math.sin(t*2);root.position.y=.006*Math.sin(t*7);};return root;}
export function goose(){
 const root=new T.Group(),mat=skin('#a9a797'),neckMat=skin('#8a8877');
 sculpt(root,[[0,.34,0,.22,.25,.43],[0,.43,-.23,.14,.18,.22]],mat,[0,.36,0],.68,56);
 const neck=new T.Group();neck.position.set(0,.48,-.25);root.add(neck);
 tube(neck,[[0,0,0],[0,.15,.015],[0,.32,-.03],[0,.48,-.14]],.062,neckMat,.9);
 const head=new T.Group();head.position.set(0,.48,-.14);neck.add(head);ell(head,mat,0,0,0,.095,.105,.135);
 ell(head,new T.MeshStandardMaterial({color:0xbda47c,roughness:.65}),0,-.025,-.18,.054,.029,.105);
 for(const side of [-1,1])ell(head,eyeMat,side*.085,.018,-.06,.014,.017,.016);
 const wings=[],feet=[];
 for(const side of [-1,1]){
  const wing=new T.Group();wing.position.set(side*.16,.43,.01);root.add(wing);ell(wing,mat,side*.24,0,.04,.33,.06,.27);
  for(let j=0;j<9;j++){const feather=ell(wing,j<4?mat:dark,side*(.38+j*.035),-.025,.04+j*.052,.065,.025,.27-j*.006);feather.rotation.y=side*(-.5+j*.075);}wings.push({wing,side});
  const leg=new T.Group();leg.position.set(side*.09,.24,.13);root.add(leg);ell(leg,dark,0,-.1,0,.02,.12,.02);
  const sh=new T.Shape();sh.moveTo(0,-.10);sh.lineTo(.065,.045);sh.lineTo(-.065,.045);sh.closePath();const web=new T.Mesh(new T.ShapeGeometry(sh),dark);web.rotation.x=-Math.PI/2;web.position.set(0,-.21,-.05);leg.add(web);feet.push(leg);
 }
 ell(root,mat,0,.36,.45,.16,.055,.22);
 root.userData.update=(t,flying=false,amount=1)=>{
  const blend=flying?amount:0,phase=t*10;
  for(const {wing,side} of wings){wing.scale.x=.32+.68*blend;wing.rotation.z=side*(-.15*(1-blend)+Math.sin(phase)*.88*blend);wing.rotation.y=-side*.6*(1-blend);}
  neck.rotation.x=-1.05*blend;head.rotation.x=1.05*blend;feet.forEach(f=>f.rotation.x=-1.3*blend);
  root.rotation.x=-.055*blend+(1-blend)*Math.sin(t*.9)*.018;
 };
 return root;
}
