// Distinct authored 3D sets. Shared materials/helpers are not reused scene layouts.
export function fragments(K,design){
 const {T,V,setup,mesh,ball,box,tube,shortTrace,stone,soil,ivory,amber,cyan,pose,smooth,label}=K,w=setup(true),p=w.scene;
 const returned=design==='incomplete-fragments-return',question=design==='survival-question';
 if(returned){const grains=new T.InstancedMesh(new T.IcosahedronGeometry(.18,2),stone,170),o=new T.Object3D();for(let i=0;i<170;i++){const r=.13+((i*17)%19)/80;o.position.set(Math.sin(i*127.1)*1.5,Math.cos(i*43.6)*.20-.25,Math.cos(i*47.7)*1.2);o.scale.set(r*4,r*2,r*3);o.rotation.set(i,.3*i,.1*i);o.updateMatrix();grains.setMatrixAt(i,o.matrix);}grains.castShadow=grains.receiveShadow=true;p.add(grains);}
 if(question){for(let i=0;i<4;i++){const q=mesh(p,new T.IcosahedronGeometry(1,2),stone,(i%2-.5)*2,-.4,Math.floor(i/2)*1.5-.7);q.scale.set(1.1,.35,.7);}}
 const fs=[];
 for(let i=0;i<(returned?4:6);i++){
  const g=new T.Group();p.add(g);const n=3+i%4;
  for(let j=0;j<n;j++){
   const x=(j-(n-1)/2)*.16;
   box(g,j%3?amber:cyan,[x,0,0],[.055,.045,.23]);
   ball(g,ivory,[x,.0,-.14],[.035,.032,.035]);ball(g,ivory,[x,.0,.14],[.035,.032,.035]);
   if(j){tube(g,[[x-.16,0,-.14],[x,0,-.14]],.018,ivory);tube(g,[[x-.16,0,.14],[x,0,.14]],.018,ivory);}
  }
  const x=Math.sin(i*2.1)*1.0,z=Math.cos(i*2.3)*.8;g.position.set(x,.15+(i%2)*.3,z);g.rotation.set(.15*i,i*.7,.07*i);fs.push({g,x,z});
 }
 w.qualifier='ENLARGED CONCEPTUAL FRAGMENTS · NO ACTUAL READS, WHOLE GENOME OR MOLECULAR FOOTAGE';
 w.update=t=>{fs.forEach(({g,x,z},i)=>{g.position.set(x+.04*Math.sin(t*.25+i),.15+(i%2)*.3+(returned?.16*smooth(t/3):.03*Math.sin(t*.4+i)),z+.03*Math.sin(t*.3));g.rotation.y=i*.7+t*.025;});w.state={stage:'separate-short-fragments',returned_to_sediment:returned,fragments_never_join_into_genome:true};};
 w.camera=t=>pose([[0,2.8,2.1,3.6,0,.2,0],[12,2.4,2.2,3.3,0,.2,0]],t);
 w.labels=t=>[label(question?'WHY DID ANY MATERIAL SURVIVE?':returned?'BROKEN FRAGMENTS · INCOMPLETE RECORD':'SHORT FRAGMENTS · NOT A COMPLETE GENOME',[.3,.6,0],smooth(t/.6))];return w;
}
export function mineral(K){
 const {T,setup,mesh,shortTrace,stone,amber,cyan,pose,smooth,label}=K,w=setup(true),p=w.scene;
 const layers=[];
 for(let i=0;i<4;i++){
  const shape=new T.Shape();shape.moveTo(-2,-1);shape.lineTo(-.3,-1.25);shape.lineTo(1.8,-.7);shape.lineTo(2.1,.3);shape.lineTo(.8,1.2);shape.lineTo(-1.5,.9);shape.closePath();
  const geo=new T.ExtrudeGeometry(shape,{depth:.075,bevelEnabled:true,bevelSegments:2,steps:1,bevelSize:.035,bevelThickness:.03});geo.rotateX(-Math.PI/2);const q=mesh(p,geo,stone,(i-1.5)*.12,i*.14-.45,0);q.rotation.y=(i-1.5)*.075;layers.push(q);
 }
 const fs=Array.from({length:7},(_,i)=>{const f=shortTrace(p,3+i%3);f.group.scale.setScalar(.7);return f;});
 w.qualifier='MINERAL SURFACE / BINDING · CONCEPTUAL, ENLARGED · NOT CALIBRATED MOLECULAR DYNAMICS';
 w.update=t=>{const bind=smooth((t-.5)/4);fs.forEach((f,i)=>{const x=-1.3+i*.43,z=Math.sin(i*1.9)*.5;f.group.position.set(x,-.45+3*.14+.075+.032+(1-bind)*.8,z);f.group.rotation.y=i*.3;});w.state={stage:'mineral-lamellae',binding_progress:bind,protection_possible_not_guaranteed:true};};
 w.camera=t=>pose([[0,3.2,2.6,4,0,.3,0],[5,2.9,2.0,3.7,0,.1,0],[20,3.6,2.6,4.5,.2,.0,0]],t);
 w.labels=t=>[label(t<10?'BINDING MAY AID SURVIVAL':'RETENTION ALSO COMPLICATES RELEASE',[0,.2,0],smooth(t/.6))];return w;
}
export function controls(K){
 const {T,setup,mesh,box,ball,shortTrace,steel,ivory,cyan,glass,pose,smooth,label}=K,w=setup(true),p=w.scene;
 box(p,steel,[0,1.25,-.4],[5,.12,2.5]);box(p,steel,[0,2.6,-1.6],[5,2.7,.12]);for(const x of [-2.45,2.45])box(p,glass,[x,2.45,-.4],[.06,2.3,2.5]);box(p,ivory,[0,3.85,-.4],[5,.1,2.5]);
 const traces=[];
 for(let i=0;i<3;i++){const x=-1.5+i*1.5;box(p,ivory,[x,1.34,0],[1.15,.06,.85]);mesh(p,new T.CylinderGeometry(.14,.14,.45,24),glass,x,1.6,-.7);mesh(p,new T.CylinderGeometry(.16,.16,.05,24),cyan,x,1.83,-.7);const f=shortTrace(p,i===1?7:4);f.group.position.set(x,1.5,0);f.group.scale.setScalar(.7);traces.push(f);}
 w.qualifier='CONCEPTUAL AUTHENTICITY CHECKS · NOT STUDY FOOTAGE, ACTUAL CONTROLS OR SEQUENCE READS';
 w.update=t=>{const check=smooth((t-12.5)/4);traces[0].units.forEach((u,j)=>u.scale.setScalar(j===0||j===3?1-check*.8:1));traces[1].group.position.z=.0-.22*smooth((t-2)/5);traces[2].group.position.y=1.5+.08*smooth((t-7)/4);w.state={stage:'separate-clean-hood-controls',damage_check_progress:check,damage_not_proof_alone:true};};
 w.camera=t=>pose([[0,4,3.2,6,0,2.1,-.4],[11,3.8,3.0,5.5,-.3,1.8,-.1],[26,4.2,3.2,6.2,0,2,-.3]],t);
 w.labels=t=>[label(t<12.5?'CONTAMINATION / ALTERNATIVE EXPLANATIONS':'DAMAGE IS ONE CHECK · NOT PROOF ALONE',[t<12.5?0:-1.5,1.65,0],smooth(t/.7))];return w;
}
export function branch(K){
 const {T,setup,mesh,box,ball,tube,shortTrace,stone,amber,cyan,ivory,pose,smooth,label}=K,w=setup(true),p=w.scene;
 mesh(p,new T.CylinderGeometry(1.7,1.85,.22,60),stone,0,-.15,0);
 tube(p,[[0,0,0],[0,1.1,0],[-1.1,2.3,0]],.035,ivory);tube(p,[[0,1.1,0],[1.1,2.3,0]],.035,ivory);tube(p,[[-.6,1.75,0],[-1.35,2.3,-.55]],.025,ivory);
 const supported=ball(p,amber,[0,1.1,0],[.07,.07,.07]),f=shortTrace(p,4);f.group.scale.setScalar(.6);
 w.qualifier='SCHEMATIC SUPPORTED BRANCH · NOT THE STUDY TREE, EXACT SPECIES OR A COMPLETE GENOME';
 w.update=t=>{const u=smooth(t/6);f.group.position.set(-1.9*(1-u),.25+.85*u,.6*(1-u));f.group.rotation.z=.1*u;supported.scale.setScalar(.07*(1+.1*Math.sin(t*.5)));w.state={stage:'branch-level-support',candidate_approach:u,complete_genome:false};};
 w.camera=t=>pose([[0,3.5,2.4,4.8,-.1,1.2,0],[15,4.2,2.7,5.5,0,1.2,0]],t);
 w.labels=t=>[label('A SUPPORTED BRANCH ≠ AN EXACT SPECIES',[0,1.1,0],smooth(t/.7))];return w;
}
export function boundary(K){
 const {T,setup,mesh,box,tube,shortTrace,stone,ivory,green,pose,smooth,label,mat}=K,w=setup(true),p=w.scene;
 const base=mesh(p,new T.IcosahedronGeometry(1,3),stone,0,-.1,0);base.scale.set(2.8,.3,1.8);
 const wire=mat('#a7bcad',{wireframe:true,transparent:true,opacity:.4}),trees=[];
 for(let i=0;i<5;i++){const g=new T.Group();g.position.set(-1.8+i*.85,.12,Math.sin(i*2.4)*.6);p.add(g);mesh(g,new T.CylinderGeometry(.02,.05,1.2,6),wire,0,.6,0);mesh(g,new T.ConeGeometry(.48,1.5,7,3,true),wire,0,1.2,0);trees.push(g);}
 const traces=Array.from({length:4},(_,i)=>{const f=shortTrace(p,3+i%2);f.group.position.set(-1.5+i,.25,1.1);f.group.scale.setScalar(.55);return f;});
 w.qualifier='CONCEPTUAL RECONSTRUCTION BOUNDARY · WIREFRAME IS ILLUSTRATION, NOT RECOVERED APPEARANCE';
 w.update=t=>{wire.opacity=.5*(1-.7*smooth((t-10)/5));trees.forEach((g,i)=>{g.scale.y=.75+.25*smooth((t-i*.35)/3);});w.state={stage:'evidence-versus-illustration-diorama',illustration_certainty_not_measured:true,wireframe_opacity:wire.opacity};};
 w.camera=t=>pose([[0,4.3,2.8,5.6,0,.8,0],[19,4.7,3.1,6.2,0,.7,0]],t);
 w.labels=t=>[label(t<12?'ILLUSTRATION ADDS APPEARANCE':'EVIDENCE DOES NOT RECOVER ONE AFTERNOON',t<12?[.3,1.5,0]:[0,.25,1.1],smooth(t/.7))];return w;
}
export function gaps(K){
 const {T,setup,mesh,box,ball,shortTrace,stone,soil,steel,ivory,cyan,pose,smooth,label,WATER_FRAGMENT}=K,w=setup(true),p=w.scene;
 // A physical process model, not three repeated specimen trays or an implied actual laboratory filter.
 box(p,soil,[0,.0,0],[6.2,.18,1.9]);for(const z of [-.48,.48])box(p,stone,[0,.17,z],[6.3,.25,.18]);
 const wm=new T.ShaderMaterial({uniforms:{time:{value:0}},vertexShader:'uniform float time;varying vec3 v;varying vec3 wp;void main(){vec3 p=position;p.z+=.01*sin(p.x*3.+time);v=p;wp=(modelMatrix*vec4(p,1.)).xyz;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}',fragmentShader:WATER_FRAGMENT});const water=mesh(p,new T.PlaneGeometry(6,.8,70,12),wm,0,.17,0);water.rotation.x=-Math.PI/2;
 box(p,steel,[1.1,.28,.9],[.7,.2,.55]);for(let i=0;i<3;i++){box(p,steel,[2.5,.32+i*.3,-.1],[.45,.06,.7]);}
 const fs=Array.from({length:3},(_,i)=>{const f=shortTrace(p,4);f.group.scale.setScalar(.5);return f;});
 w.qualifier='CONCEPTUAL SURVIVAL / DELIVERY / RECOGNITION · NOT A LAB PROTOCOL OR MEASURED TRAJECTORIES';
 w.update=t=>{wm.uniforms.time.value=t;
  const a=smooth((t-7)/4),b=smooth((t-11)/4),c=smooth((t-15)/4);
  fs[0].group.position.set(-2.3+a*.7,.36,0);fs[0].units.forEach((u,j)=>u.scale.setScalar(1-a*(j%2?.95:.7)));
  fs[1].group.position.set(-.7+b*1.8,.36,-b*.35); // misses the collection recess at positive z
  fs[2].group.position.set(1.5+c*.65,.36,0); // remains outside an incomplete reference rack
  w.state={stage:'process-model-signal-gaps',survival_loss:a,delivery_bypass:b,reference_gap:c,absence_not_established:true};};
 w.camera=t=>pose([[0,4.1,2.9,5.5,-.2,.4,0],[12,4.0,2.8,5.2,.1,.4,0],[23,4.4,3.2,5.8,.3,.4,0]],t);
 w.labels=t=>[label(t<9?'SURVIVAL CAN FAIL':t<14?'MATERIAL MAY MISS THE SAMPLE':t<19?'REFERENCES MAY BE INCOMPLETE':'NO SIGNAL ≠ NO ANIMAL',[t<9?-2:t<14?.4:2.2,.45,0],smooth(t/.7))];return w;
}
export function integration(K){
 const {T,setup,box,ball,shortTrace,paperLeaf,steel,ivory,amber,cyan,pose,smooth,label}=K,w=setup(true),p=w.scene;
 // Three independently opening archive drawers: complementary, visibly incomplete record types.
 box(p,steel,[0,1.75,-.6],[3.9,3.5,.12]);for(const x of [-1.95,1.95])box(p,steel,[x,1.75,.15],[.12,3.5,1.6]);const drawers=[];
 for(let i=0;i<3;i++){
  const g=new T.Group();g.position.set(0,.45+i*1.1,0);p.add(g);box(g,ivory,[0,0,0],[3.7,.1,1.5]);box(g,steel,[0,.16,.78],[3.7,.36,.07]);box(g,amber,[0,.16,.85],[.65,.05,.08]);drawers.push(g);
  if(i===0)for(let j=0;j<3;j++){const f=shortTrace(g,3+j%2);f.group.scale.setScalar(.5);f.group.position.set(-1.05+j,.12,0);}
  if(i===1)for(let j=0;j<3;j++)ball(g,amber,[-1+j*.9,.18,-.1],[.11,.10,.11]);
  if(i===2){paperLeaf(g,[-.9,.11,0],1.1);paperLeaf(g,[.75,.11,0],.7);}
 }
 w.qualifier='SCHEMATIC COMPLEMENTARY ARCHIVE · EMPTY SPACE IS NOT SPECIES ABSENCE OR A MEASURED COUNT';
 w.update=t=>{drawers.forEach((g,i)=>g.position.z=.1+.65*smooth((t-i*4)/6));w.state={stage:'independent-incomplete-archive-drawers',records_complementary:true,complete_inventory:false};};
 w.camera=t=>pose([[0,4.3,3.8,6.8,0,1.7,.2],[17,4.8,4.1,7.5,0,1.7,.4]],t);
 w.labels=t=>[label('DIFFERENT RECORDS · DIFFERENT GAPS',[0,2.1,.8],smooth(t/.7))];return w;
}
export function sampleArrival(K){
 const {T,setup,mesh,box,ball,stone,soil,ivory,steel,glass,pose,smooth,label}=K,w=setup(true),p=w.scene;
 box(p,steel,[0,.9,0],[6,.13,3.5]);box(p,ivory,[0,1,0],[5.8,.06,3.3]);const sled=new T.Group();p.add(sled);box(sled,steel,[0,0,0],[1.8,.07,.9]);
 const sleeve=mesh(sled,new T.CylinderGeometry(.25,.25,1.25,36),glass,0,.3,0);sleeve.rotation.z=Math.PI/2;const core=mesh(sled,new T.CylinderGeometry(.21,.21,1.12,36),soil,0,.3,0);core.rotation.z=Math.PI/2;for(const x of [-.66,.66]){const cap=mesh(sled,new T.CylinderGeometry(.27,.27,.08,36),ivory,x,.3,0);cap.rotation.z=Math.PI/2;}
 w.qualifier='ILLUSTRATIVE SAMPLE ARRIVAL · NOT ACTUAL COLLECTION EQUIPMENT OR STUDY FOOTAGE';
 w.update=t=>{sled.position.set(-1.6+2*smooth(t/5),1.10,0);w.state={stage:'closed-sediment-sample-arrival',sample_closed:true};};
 w.camera=t=>pose([[0,3.6,2.5,4.6,-.5,1.35,0],[7,3.5,2.5,4.7,.3,1.35,0]],t);
 w.labels=t=>[label('FROM SEDIMENT TO A GENETIC QUESTION',[sled.position.x,1.5,0],smooth(t/.6))];return w;
}
