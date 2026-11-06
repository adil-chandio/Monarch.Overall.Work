import * as T from 'three';
import {createWorlds} from './worlds.mjs';
import {smooth} from './motion.mjs';
const W=1920,H=1080,canvas=document.querySelector('#final'),ctx=canvas.getContext('2d',{alpha:false});
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.18;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;
const camera=new T.PerspectiveCamera(39,W/H,.025,180),schedule=await fetch('/schedule.json').then(r=>r.json()),worlds=createWorlds();
await Promise.all([document.fonts.load('24px AtlasSans'),document.fonts.load('42px AtlasSerif')]);await document.fonts.ready;
function line(text,x,y,size=24,color='#e9dfc6'){ctx.font=`${size}px AtlasSans`;ctx.fillStyle=color;ctx.shadowBlur=10;ctx.shadowColor='rgba(8,20,22,.8)';ctx.fillText(text,x,y);ctx.shadowBlur=0;}
function layer(segment,f,opacity,blur){const age=(f-segment.start_frame)/30,w=worlds[segment.world];w.update(age);const pose=w.camera(window.__freezeCamera?0:age);camera.position.set(...pose.position);camera.lookAt(new T.Vector3(...pose.target));camera.updateMatrixWorld();renderer.render(w.scene,camera);ctx.globalAlpha=opacity;ctx.filter=blur?`blur(${blur}px)`:'none';ctx.drawImage(renderer.domElement,0,0,W,H);ctx.filter='none';ctx.globalAlpha=1;return {w,pose,age};}
function tag(label){const v=new T.Vector3(...label.point).project(camera),x=(v.x*.5+.5)*W,y=(-v.y*.5+.5)*H;if(v.z>1||v.z<-1)return;const xx=Math.max(105,Math.min(W-570,x+30)),yy=Math.max(215,Math.min(H-170,y-45));ctx.strokeStyle='#c9aa70';ctx.lineWidth=1.3;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(xx-12,yy+8);ctx.stroke();ctx.fillStyle='#dec397';ctx.beginPath();ctx.arc(x,y,3,0,Math.PI*2);ctx.fill();line(label.text,xx,yy,25);}
function draw(frame){
 frame=Math.max(0,Math.min(schedule.total_frames-1,Math.round(frame)));const index=schedule.segments.findIndex(s=>frame>=s.start_frame&&frame<s.end_frame),s=schedule.segments[index],elapsed=frame-s.start_frame,blend=index>0&&elapsed<45,alpha=blend?smooth(elapsed/45):1,blur=blend?12*Math.sin(Math.PI*elapsed/45)**2:0;
 if(blend)layer(schedule.segments[index-1],frame,1,blur);
 const state=layer(s,frame,alpha,blur),v=ctx.createRadialGradient(W*.5,H*.45,H*.15,W*.5,H*.5,W*.7);v.addColorStop(0,'rgba(5,17,23,0)');v.addColorStop(1,'rgba(4,15,18,.22)');ctx.fillStyle=v;ctx.fillRect(0,0,W,H);
 line('EXTINCT LIFE',78,70,22);ctx.fillStyle='#b79a64';ctx.fillRect(78,84,44,2);line('MOVING 3D · DEVELOPMENT',W-448,70,19,'#d2d8cc');
 if(!blend||alpha>.75)state.w.labels(state.age).forEach(tag);
 line(state.w.qualifier,78,1017,23,'#d3d8cd');if(frame>schedule.total_frames-150)line('MUSIC: HIRAETH — SCOTT BUCKLEY · CC-BY 4.0 · scottbuckley.com.au',78,974,21,'#ded5bd');
 window.__state={frame,world:s.world,sequence:s.id,age:state.age,camera:state.pose,actual_mesh_scene:true,generated_scene_images_used:false,old_movie_used:false,...state.w.state};
}
window.__seek=draw;window.__schedule=schedule;draw(0);window.__ready=true;
const audio=document.querySelector('audio');audio.src='/proof.wav';let playing=false,start=0,from=0;const button=document.querySelector('#play');
function tick(now){if(!playing)return;const f=from+(now-start)*.03;draw(f);if(f>=schedule.total_frames-1){playing=false;audio.pause();button.textContent='Play moving 3D preview';return;}requestAnimationFrame(tick);}
button.textContent='Play moving 3D preview';button.onclick=()=>{playing=!playing;button.textContent=playing?'Pause':'Play moving 3D preview';if(playing){from=window.__state.frame;audio.currentTime=from/30;start=performance.now();audio.play().catch(()=>{});requestAnimationFrame(tick);}else audio.pause();};
