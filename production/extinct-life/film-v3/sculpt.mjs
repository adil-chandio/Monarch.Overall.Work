import * as T from 'three';
import {MarchingCubes} from 'three/addons/objects/MarchingCubes.js';
// Smooth-union implicit surfaces remove the intersecting-ball silhouettes of prototypes.
export function sculpt(parent,ellipsoids,material,center=[0,2,0],half=3.4,resolution=64){
 const mc=new MarchingCubes(resolution,material,false,false,180000);mc.isolation=0;const field=mc.field;
 const smin=(a,b,k)=>{const h=Math.max(k-Math.abs(a-b),0)/k;return Math.min(a,b)-h*h*k*.25;};
 for(let z=0;z<resolution;z++)for(let y=0;y<resolution;y++)for(let x=0;x<resolution;x++){
  const p=[(x/resolution*2-1)*half+center[0],(y/resolution*2-1)*half+center[1],(z/resolution*2-1)*half+center[2]];let d=100;
  for(const e of ellipsoids){const [cx,cy,cz,rx,ry,rz]=e;const v=(Math.sqrt(((p[0]-cx)/rx)**2+((p[1]-cy)/ry)**2+((p[2]-cz)/rz)**2)-1)*Math.min(rx,ry,rz);d=smin(d,v,.22);}
  field[x+resolution*(y+resolution*z)]=-d;
 }
 mc.update();const n=mc.geometry.drawRange.count,g=new T.BufferGeometry();for(const key of ['position','normal']){const old=mc.geometry.attributes[key];g.setAttribute(key,new T.BufferAttribute(old.array.slice(0,n*3),3));}
 const a=g.attributes.position;const uv=new Float32Array(n*2);for(let i=0;i<n;i++){const x=a.getX(i)*half+center[0],y=a.getY(i)*half+center[1],z=a.getZ(i)*half+center[2];a.setXYZ(i,x,y,z);uv[i*2]=Math.atan2(x,z)/(Math.PI*2)+.5;uv[i*2+1]=y*.4;}g.setAttribute('uv',new T.BufferAttribute(uv,2));const mesh=new T.Mesh(g,material);mesh.castShadow=mesh.receiveShadow=true;parent.add(mesh);mc.geometry.dispose();return mesh;
}
