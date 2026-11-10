// A geographically anchored present-day map, not a 10,000-year-old coastline.
import * as T from 'three';
const W=1280,H=720;await document.fonts.load('700 16px Manrope');const data=await(await fetch('/map.geojson')).json();
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(1);renderer.setSize(W,H);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.1;
const canvas=document.createElement('canvas');canvas.id='final';canvas.width=W;canvas.height=H;document.body.appendChild(canvas);const ctx=canvas.getContext('2d');
const scene=new T.Scene();scene.background=new T.Color(0x101d24);scene.fog=new T.Fog(0x101d24,45,95);scene.add(new T.HemisphereLight(0xa3d3e3,0x152322,1.7));let light=new T.DirectionalLight(0xffdfa4,2.7);light.position.set(-6,18,-12);scene.add(light);
// Local equirectangular display at about 70°N; vertical extrusion is artistic.
const sx=4*Math.cos(70*Math.PI/180),sy=4;const xy=([x,y])=>[(x-180)*sx,(y-70)*sy];
function shapeFor(poly){const [outer,...holes]=poly;const shape=new T.Shape();outer.forEach((p,i)=>{let [x,y]=xy(p);i?shape.lineTo(x,y):shape.moveTo(x,y)});for(const hole of holes){const h=new T.Path();hole.forEach((p,i)=>{let [x,y]=xy(p);i?h.lineTo(x,y):h.moveTo(x,y)});shape.holes.push(h)}return shape}
function meshes(feature,color,depth){let geom=feature.geometry;let polygons=geom.type==='Polygon'?[geom.coordinates]:geom.coordinates;const mat=new T.MeshStandardMaterial({color,roughness:.86,metalness:.05});let n=0;for(const p of polygons){if(!p[0]||p[0].length<4)continue;let mesh=new T.Mesh(new T.ExtrudeGeometry(shapeFor(p),{depth,bevelEnabled:false,steps:1,curveSegments:2}),mat);mesh.rotation.x=-Math.PI/2;scene.add(mesh);n++}return n}
const count=meshes(data.features[0],0x8d9986,.13);meshes(data.features[1],0xdac491,.155);
const oceanUniforms={time:{value:0}};const sea=new T.Mesh(new T.PlaneGeometry(500,500,1,1),new T.ShaderMaterial({uniforms:oceanUniforms,vertexShader:`varying vec2 uv0;void main(){uv0=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,fragmentShader:`varying vec2 uv0;uniform float time;void main(){float n=sin(uv0.x*150.+time*.18)*sin(uv0.y*150.-time*.13);vec3 a=vec3(.025,.13,.18),b=vec3(.05,.22,.26);gl_FragColor=vec4(mix(a,b,.45+.16*n),1.);}`}));sea.rotation.x=-Math.PI/2;sea.position.set(0,-.025,0);scene.add(sea);
const camera=new T.PerspectiveCamera(31,W/H,.1,350);const marker=new T.Vector3(...[(180.4-180)*sx,.16,-(71.25-70)*sy]);const smooth=u=>{u=Math.max(0,Math.min(1,u));return u*u*(3-2*u)};
function draw(t){t=Math.max(0,Math.min(20,t));const u=smooth(t/20);camera.position.set(17-4*u,20-3*u,24-5*u);camera.lookAt(0,0,-1.3);oceanUniforms.time.value=t;renderer.render(scene,camera);ctx.clearRect(0,0,W,H);ctx.drawImage(renderer.domElement,0,0);
 const p=marker.clone().project(camera),x=(p.x*.5+.5)*W,y=(-p.y*.5+.5)*H;ctx.strokeStyle='rgba(255,220,162,.9)';ctx.lineWidth=2;ctx.beginPath();ctx.arc(x,y,5,0,Math.PI*2);ctx.moveTo(x+8,y-8);ctx.lineTo(x+53,y-42);ctx.lineTo(x+215,y-42);ctx.stroke();ctx.fillStyle='#f2e5c9';ctx.textAlign='left';ctx.font='700 19px Manrope';ctx.fillText('WRANGEL ISLAND',x+58,y-52);
 ctx.textAlign='left';ctx.font='700 14px Manrope';ctx.fillStyle='rgba(221,229,226,.85)';ctx.fillText('PRESENT-DAY COASTLINES · ANCIENT SHORELINE UNCERTAIN',30,H-31);
 return {time:t,land_polygons:count,source:'Natural Earth 1:10m present-day land',historical_shoreline_claim:false};}
window.__seek=draw;window.__ready=true;draw(0);
