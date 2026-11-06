import * as T from 'three';
// Approximate sky reflection + geometric wave normals, not screen-space reflections or field footage.
export const WATER_FRAGMENT=`
uniform float time;varying vec3 v;varying vec3 wp;
void main(){
 vec3 n=normalize(cross(dFdx(wp),dFdy(wp)));if(n.y<0.)n=-n;
 float wx=v.x*2.7+v.y*2.1+time*.8,wz=v.y*3.4-v.x*1.4-time*.6;
 n=normalize(n+vec3(.09*cos(wx)+.04*cos(wz),0.,.07*cos(wz)));
 vec3 eye=normalize(cameraPosition-wp),sun=normalize(vec3(-.45,.85,-.25));
 float fresnel=pow(1.-clamp(dot(n,eye),0.,1.),3.);
 float glint=pow(max(0.,dot(reflect(-sun,n),eye)),32.);
 float drift=.5+.5*sin(v.x*2.1+sin(v.y*.71-time*.27)*1.2+time*.4);
 vec3 deep=vec3(.10,.27,.28),sky=vec3(.38,.51,.52);
 vec3 color=mix(deep,sky,.16+.48*fresnel)+vec3(.012,.018,.015)*drift;
 color+=vec3(.02,.035,.03)*sin(wx)*sin(wz)+vec3(.17,.16,.13)*glint;
 gl_FragColor=vec4(color,1.);
}`;
export function refineWater(material){
 if(!material?.isShaderMaterial||(!material.vertexShader.includes('varying vec3 v;')||!material.vertexShader.includes('v=p;gl_Position=')))return;
 material.vertexShader=material.vertexShader.replace('varying vec3 v;','varying vec3 v;varying vec3 wp;').replace('v=p;gl_Position=','v=p;wp=(modelMatrix*vec4(p,1.)).xyz;gl_Position=');
 material.fragmentShader=WATER_FRAGMENT;material.needsUpdate=true;
}
export function shoreReeds(scene,centre,height,{halfWidth=1.6,range=13,count=240}={}){
 const positions=[],colors=[];
 const point=(u,side)=>[u*u*.055+side*.017*Math.pow(1-u,.6),u*.45,Math.sin(u*Math.PI)*.026];
 for(let j=0;j<7;j++){
  const a=j/7,b=(j+1)/7,tri=[point(a,-1),point(a,1),point(b,-1),point(a,1),point(b,1),point(b,-1)];
  for(const p of tri){positions.push(...p);const u=p[1]/.45;colors.push(.10+u*.05,.16+u*.08,.07+u*.035);}
 }
 const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(positions,3));g.setAttribute('color',new T.Float32BufferAttribute(colors,3));g.computeVertexNormals();
 const mat=new T.MeshStandardMaterial({vertexColors:true,roughness:.96,side:T.DoubleSide});
 const time={value:0};const wind=shader=>{shader.uniforms.windTime=time;shader.vertexShader='uniform float windTime;\n'+shader.vertexShader;shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
 transformed.x+=.035*pow(position.y/.45,2.)*sin(windTime*.8+instanceMatrix[3].x*.31+instanceMatrix[3].z*.13);`);};
 mat.onBeforeCompile=wind;
 const reeds=new T.InstancedMesh(g,mat,count),o=new T.Object3D();const fract=x=>x-Math.floor(x);
 for(let i=0;i<count;i++){
  const z=(fract(Math.sin(i*127.1+3)*43758.5453)*2-1)*range,side=i%2?1:-1;
  const x=centre(z)+side*(halfWidth+.15+fract(Math.sin(i*78.23+8)*12345.67)*.6);
  o.position.set(x,height(x,z)-.025,z);o.rotation.y=i*2.399;o.scale.set(.7+fract(i*.731)*.5,.55+fract(i*.917)*.9,1);o.updateMatrix();reeds.setMatrixAt(i,o.matrix);
 }
 const depth=new T.MeshDepthMaterial({depthPacking:T.RGBADepthPacking,side:T.DoubleSide});depth.onBeforeCompile=wind;reeds.customDepthMaterial=depth;reeds.castShadow=reeds.receiveShadow=true;scene.add(reeds);
 return t=>{time.value=t;};
}
export function sectionGrains(cap,material){
 const grains=new T.InstancedMesh(new T.IcosahedronGeometry(1,0),material,180),o=new T.Object3D();
 const fract=x=>x-Math.floor(x);
 for(let i=0;i<180;i++){
  const x=(fract(Math.sin(i*127.1+2)*43758.5453)*2-1)*2.7,z=(fract(Math.sin(i*311.7+8)*18732.3)*2-1)*1.55,r=.009+fract(i*.731)*.018;
  o.position.set(x,.988+.055*Math.sin(x*2+z),z);o.scale.set(r,r*.48,r*.8);o.rotation.set(i,.3*i,.2*i);o.updateMatrix();grains.setMatrixAt(i,o.matrix);
 }
 grains.castShadow=false;grains.receiveShadow=true;cap.add(grains);return grains;
}
