import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {footState,smooth,SPEED} from '/enhanced/motion.mjs';
const loader=new GLTFLoader();
const library=new Map(await Promise.all(['mastodon','reindeer','goose','hare'].map(async k=>[k,(await loader.loadAsync('/native/'+k+'.glb')).scene])));
const clamp=x=>Math.max(0,Math.min(1,x));
export function animal(kind){
 const root=new T.Group(),parts=[];const source=library.get(kind);source.updateMatrixWorld(true);
 source.traverse(o=>{if(!o.isMesh)return;const g=o.geometry.clone().applyMatrix4(o.matrixWorld),m=o.material.clone();m.roughness=Math.max(.42,m.roughness??.8);if(/eye/i.test(o.name)){m.roughness=.16;m.color.set('#171b17');}m.envMapIntensity=.35;const p=g.attributes.position,bind=new Float32Array(p.array),colors=new Float32Array(p.count*3);for(let i=0;i<p.count;i++){const f=.93+.07*Math.sin(p.getX(i)*23+p.getY(i)*17)*Math.sin(p.getZ(i)*31);colors.set([f,f,f],i*3);}g.setAttribute('color',new T.BufferAttribute(colors,3));m.vertexColors=true;const mesh=new T.Mesh(g,m);mesh.name=o.name;mesh.castShadow=mesh.receiveShadow=true;root.add(mesh);parts.push({mesh,bind,name:o.name});});
 const dims={mastodon:{hip:1.9,x:.68,z:[1.03,-1.17],r:.44},reindeer:{hip:1.08,x:.24,z:[.5,-.65],r:.20},hare:{hip:.26,x:.12,z:[.18,-.2],r:.16}}[kind];
 root.rotation.y=Math.PI;root.userData.originalOrganicAsset=true;
 root.userData.update=(t,{walk=1,browse=0,flight=0}={})=>{
  const feet=[-1,1].flatMap(side=>[0,1].map(j=>footState(t,(side>0?.5:0)+(j?.25:0))));for(const {mesh,bind,name} of parts){const p=mesh.geometry.attributes.position;const wing=/wing|primary/i.test(name),trunk=/Unified.sculpt|nostril/i.test(name);
   for(let i=0;i<p.count;i++){const n=i*3,x=bind[n],y=bind[n+1],z=bind[n+2];let xx=x,yy=y,zz=z;
    if(dims){for(const side of [-1,1])for(let j=0;j<2;j++){const phase=(side>0?.5:0)+(j?.25:0),f=feet[(side>0?2:0)+j],w=(1-smooth((Math.abs(x-side*dims.x)-dims.r*.95)/(dims.r*.5)))*(1-smooth((Math.abs(z-dims.z[j])-dims.r*1.4)/(dims.r*.4)))*clamp((dims.hip-y)/(dims.hip*.75));zz-=f.z*w*walk*(kind==='mastodon'?1:.5);yy+=f.lift*w*walk*(kind==='mastodon'?1:.5);}
     xx+=.035*Math.sin(t*1.7)*clamp((y-dims.hip*.6)/dims.hip);yy+=.012*Math.sin(t*1.7)*clamp((y-dims.hip*.7)/dims.hip);}
    if(kind==='mastodon'){
     if(/ear/i.test(name)){const side=x<0?-1:1,angle=side*.045*Math.sin(t*.9),dx=xx-side*.56,dz=zz-1.59;xx=side*.56+dx*Math.cos(angle)+dz*Math.sin(angle);zz=1.59+dz*Math.cos(angle)-dx*Math.sin(angle);}
     if(/tail/i.test(name))xx+=.045*Math.sin(t*.8)*clamp((-z-1.8)/.3);
     if(trunk){const w=clamp((z-2.32)/.3)*clamp((2.65-y)/1.6);xx+=.12*Math.sin(t*.65)*w;zz+=.06*Math.sin(t*.8)*w;yy+=browse*.24*w;}
     const h=clamp((z-1.3)/.8)*clamp((y-1.5)/.65),angle=(.035*Math.sin(t*.45)+.06*browse)*h,dx=xx,dz=zz-1.4;xx=dx*Math.cos(angle)+dz*Math.sin(angle);zz=1.4+dz*Math.cos(angle)-dx*Math.sin(angle);
    }
    if(kind==='reindeer'){const h=clamp((z-.6)/.4)*clamp((y-1.05)/.3);yy-=.36*browse*h;zz+=.12*browse*h;}
    if(kind==='goose'&&wing){yy+=Math.abs(x)*Math.sin(t*10)*.8*flight;xx*=.36+.64*flight;}
    p.setXYZ(i,xx,yy,zz);
   }p.needsUpdate=true;
  }
  if(kind==='hare'){root.position.y=.12*Math.max(0,Math.sin(t*2.5))*walk;}
  root.userData.pose={clock:t,walk,browse,flight};
  if(dims)root.userData.feet=[-1,1].flatMap(side=>[0,1].map(j=>{const f=footState(t,(side>0?.5:0)+(j?.25:0));return {side,pair:j,stance:f.stance||walk===0,x:root.position.x-side*dims.x,y:root.position.y+f.lift*walk,z:root.position.z-dims.z[j]+f.z*walk};}));
 };
 return root;
}
export {SPEED,smooth};
