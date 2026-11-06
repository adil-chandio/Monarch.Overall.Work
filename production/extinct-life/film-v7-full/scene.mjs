import * as T from 'three';
import {buildWorld} from './worlds.mjs';
import {smooth} from '/enhanced/motion.mjs';
const W=1920,H=1080,canvas=document.querySelector('#final'),ctx=canvas.getContext('2d',{alpha:false});
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.18;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;
const camera=new T.PerspectiveCamera(39,W/H,.025,250),schedule=await fetch('/schedule.json').then(r=>r.json()),cache=new Map();
await Promise.all([document.fonts.load('25px AtlasSans'),document.fonts.load('58px AtlasSerif')]);await document.fonts.ready;
function text(s,x,y,size=24,color='#e6dec7'){ctx.font=`${size}px AtlasSans`;ctx.fillStyle=color;ctx.shadowBlur=9;ctx.shadowColor='rgba(6,17,20,.8)';ctx.fillText(s,x,y);ctx.shadowBlur=0;}
function get(s){if(cache.has(s.id))return cache.get(s.id);const w=buildWorld(s);cache.set(s.id,w);while(cache.size>3){const first=cache.keys().next().value,old=cache.get(first);if(!old.persistent){const seen=new Set();old.scene.traverse(o=>{if(o.geometry&&!seen.has(o.geometry)){o.geometry.dispose();seen.add(o.geometry);}if(o.shadow?.map)o.shadow.map.dispose();});}cache.delete(first);renderer.renderLists.dispose();}return w;}
function layer(s,f,alpha){const age=Math.max(0,(f-s.start_frame)/30),key=[...s.keys].reverse().find(k=>k.frame<=f)||s.keys[0],mode=key.mode.split('-')[1],w=get(s);w.update(age,mode);const pose=w.camera(window.__freezeCamera?0:age);camera.position.set(...pose.position);camera.lookAt(new T.Vector3(...pose.target));camera.updateMatrixWorld();renderer.render(w.scene,camera);ctx.globalAlpha=alpha;ctx.drawImage(renderer.domElement,0,0,W,H);ctx.globalAlpha=1;return {w,pose,age,mode};}
function tag(l){const p=new T.Vector3(...l.point).project(camera),x=(p.x*.5+.5)*W,y=(-p.y*.5+.5)*H;if(p.z>1||p.z<-1||x<65||x>W-65||y<150||y>H-130)return;ctx.save();ctx.globalAlpha=l.opacity??1;ctx.font='23px AtlasSans';const width=ctx.measureText(l.text).width,right=x+width+50<W-70;const xx=Math.max(76,Math.min(W-width-76,right?x+30:x-width-30)),yy=Math.max(170,Math.min(H-175,y-42));ctx.strokeStyle='#c7aa72';ctx.lineWidth=1.2;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(right?xx-10:xx+width+10,yy+6);ctx.stroke();text(l.text,xx,yy,23);ctx.restore();}
function draw(frame){
 frame=Math.max(0,Math.min(schedule.total_frames-1,Math.round(frame)));const i=schedule.sequences.findIndex(s=>frame>=s.start_frame&&frame<s.end_frame),s=schedule.sequences[i],elapsed=frame-s.start_frame,blend=i>0&&elapsed<s.blend_frames,a=blend?smooth(elapsed/s.blend_frames):1;
 if(blend)layer(schedule.sequences[i-1],frame,1);
 const state=layer(s,frame,a);const vignette=ctx.createRadialGradient(W*.5,H*.43,H*.2,W*.5,H*.5,W*.72);vignette.addColorStop(0,'rgba(4,15,20,0)');vignette.addColorStop(1,'rgba(4,15,20,.20)');ctx.fillStyle=vignette;ctx.fillRect(0,0,W,H);
 text('EXTINCT LIFE',76,68,22);ctx.fillStyle='#b99c67';ctx.fillRect(76,82,42,2);
 if(!blend||a>.8)state.w.labels(state.age,state.mode).forEach(tag);
 text(state.w.qualifier,76,1016,18,'#d1d7cc');
 if(frame>schedule.total_frames-210){text('MUSIC: HIRAETH / UNDERTOW — SCOTT BUCKLEY · CC-BY 4.0 · scottbuckley.com.au',76,976,18,'#d6cdb5');}
 if(frame>schedule.total_frames-85){ctx.save();ctx.globalAlpha=smooth((frame-(schedule.total_frames-85))/50);ctx.textAlign='center';ctx.font='55px AtlasSerif';ctx.fillStyle='#eadfbe';ctx.fillText('EXTINCT LIFE',W/2,H*.40);ctx.font='22px AtlasSans';ctx.fillText('THE LOST WORLD INSIDE A HANDFUL OF DIRT',W/2,H*.46);ctx.restore();}
 window.__state={frame,sequence:s.id,world:s.world,design:s.design,age:state.age,camera:state.pose,actual_mesh_scene:true,generated_scene_images_used:false,old_movie_used:false,...state.w.state};
}
window.__seek=draw;window.__schedule=schedule;draw(0);window.__ready=true;
const audio=document.querySelector('audio');audio.src='/proof.wav';let playing=false,start=0,from=0;const button=document.querySelector('#play');button.textContent='Play full moving-3D work preview';
function tick(now){if(!playing)return;const frame=from+(now-start)*.03;draw(frame);if(frame>=schedule.total_frames-1){playing=false;audio.pause();button.textContent='Replay full work preview';from=0;return;}requestAnimationFrame(tick);}
button.onclick=()=>{playing=!playing;button.textContent=playing?'Pause':'Play full moving-3D work preview';if(playing){from=window.__state.frame>=schedule.total_frames-1?0:window.__state.frame;audio.currentTime=from/30;start=performance.now();audio.play().catch(()=>{});requestAnimationFrame(tick);}else audio.pause();};
