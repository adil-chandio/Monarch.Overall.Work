import * as T from 'three';
import {buildWorlds,focus} from './worlds.mjs';
const canvas=document.querySelector('#final'),ctx=canvas.getContext('2d',{alpha:false});
const W=1920,H=1080,FPS=30;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.18;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;
const camera=new T.PerspectiveCamera(39,W/H,.025,250);
const schedule=await fetch('/schedule.json').then(r=>r.json());const worlds=buildWorlds();
await Promise.all([document.fonts.load('22px AtlasSans'),document.fonts.load('64px AtlasSerif')]);await document.fonts.ready;
const clamp=x=>Math.max(0,Math.min(1,x)),smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
let prior=-1;
const names=['A TRACE OF A GIANT','HOW LIFE LEAVES A CLUE','WHAT THE MINERALS KEPT','TESTING THE IDENTITY','MORE THAN ONE ANIMAL','IMAGINING IS NOT OBSERVING','THE GAPS IN THE RECORD','WHAT THE DIRT GAVE BACK'];
function panel(text,x,y,size=21,color='#cfc9b3'){ctx.font=`${size}px AtlasSans`;ctx.fillStyle=color;ctx.shadowColor='rgba(5,15,20,.85)';ctx.shadowBlur=10;ctx.fillText(text,x,y);ctx.shadowBlur=0;}
function draw(globalFrame){
 globalFrame=Math.max(0,Math.min(schedule.total_frames-1,Math.round(globalFrame)));
 const c=schedule.chapters.find(c=>globalFrame>=c.start_frame&&globalFrame<c.start_frame+c.frames);
 const f=globalFrame-c.start_frame,t=f/FPS,shot=c.shots.find(s=>f>=s.start_frame&&f<s.end_frame),i=c.shots.indexOf(shot),q=(f-shot.start_frame)/(shot.end_frame-shot.start_frame);
 const [worldKey,mode]=shot.mode.split('-'),world=worlds[worldKey];if(!world)throw Error('Missing authored world '+shot.mode);
 const act=t-shot.sentence_start;world.update(t+c.index*13.7,mode,Math.max(0,act),c.index);
 const spec=focus[shot.mode];if(!spec)throw Error('Missing focus '+shot.mode);
 const target=new T.Vector3(...spec.at);
 // Maintain a consistent side of the action; cut coverage changes size/angle, never resets actor time.
 if(worldKey==='habit'&&['mastodon','hare','rodent','reindeer','goose','takeoff'].includes(mode)){
  const a=world.actors[mode==='takeoff'?'goose':mode];if(a){target.x+=a.position.x-(mode==='mastodon'?0:mode==='hare'?-1.7:mode==='rodent'?1.4:mode==='reindeer'?-4:4.3);if(mode==='takeoff')target.y=a.position.y+.4;}
 }
 const side=[.68,.82,.48,.95,.6][i%5],angle=side+(q-.5)*.075,dist=spec.r*([1,.87,1.08,.93][shot.coverage%4]);
 const elevation=worldKey==='habit'?(mode==='wide'?.29:.16):worldKey==='coast'?(mode==='wide'?.43:.27):worldKey==='river'?.35:worldKey==='sediment'?.22:worldKey==='macro'?.17:.24;
 camera.position.set(target.x+Math.sin(angle)*dist,target.y+dist*elevation,target.z+(['habit','coast','river'].includes(worldKey)?-1:1)*Math.cos(angle)*dist);target.x+=(q-.5)*.025*dist;camera.lookAt(target);camera.updateMatrixWorld();
 renderer.render(world.scene,camera);ctx.drawImage(renderer.domElement,0,0,W,H);
 // Restrained edge falloff and subtle deterministic grain; the underlying subjects are animated meshes.
 const vignette=ctx.createRadialGradient(W*.5,H*.45,H*.2,W*.5,H*.5,W*.68);vignette.addColorStop(0,'rgba(4,16,22,0)');vignette.addColorStop(1,'rgba(3,13,19,.3)');ctx.fillStyle=vignette;ctx.fillRect(0,0,W,H);
 panel('EXTINCT LIFE',76,68,22,'#e7dbbd');ctx.fillStyle='#b58f54';ctx.fillRect(76,81,38,2);
 const label=(worldKey==='habit')?'ILLUSTRATIVE RECONSTRUCTION · NOT AN OBSERVED ENCOUNTER':worldKey==='macro'?'CONCEPTUAL MOLECULAR ILLUSTRATION · NOT TO SCALE':worldKey==='compare'?'REFERENCE-MATCHING ILLUSTRATION · NOT ACTUAL SEQUENCE READS':worldKey==='lab'?'ILLUSTRATIVE LABORATORY · NOT STUDY FOOTAGE':worldKey==='evidence'?'ILLUSTRATIVE EVIDENCE · NO COMPLETE INVENTORY':worldKey==='river'?'REPRESENTATIVE TRANSPORT PATH · NOT A TRACKED MOLECULE':worldKey==='sediment'?'CONCEPTUAL SEDIMENT SECTION · NOT A MEASURED SAMPLE':'NORTH GREENLAND · LANDSCAPE RECONSTRUCTION';
 panel(label,76,1010,18,'#d2d4c8');
 if(t<3.2){ctx.globalAlpha=Math.min(1,t/.35)*Math.min(1,(3.2-t)/.4);panel(String(c.index+1).padStart(2,'0')+' / '+names[c.index],76,132,26,'#eadab9');ctx.globalAlpha=1;}
 // Persistent evidence keys, never fictional species accuracy percentages.
 if(worldKey==='compare'){
  const text=mode==='missing'?'A missing reference is not a missing animal':mode==='family'?'Shared sequences can limit identification':mode==='damage'?'Damage patterns are one part of the checks':'Compare. Check alternatives. Keep the uncertainty.';
  panel(text,76,953,27,'#eadab9');
 }
 if(c.index===7&&f>c.frames-90){const a=smooth((f-(c.frames-90))/55);ctx.fillStyle=`rgba(8,23,29,${a*.35})`;ctx.fillRect(0,0,W,H);ctx.globalAlpha=a;ctx.font='64px AtlasSerif';ctx.textAlign='center';ctx.fillStyle='#ebdfbf';ctx.fillText('EXTINCT LIFE',W/2,H*.47);ctx.font='23px AtlasSans';ctx.fillText('THE LOST WORLD INSIDE A HANDFUL OF DIRT',W/2,H*.53);ctx.textAlign='left';ctx.globalAlpha=1;}
 window.__state={frame:globalFrame,chapter:c.id,shot:shot.id,mode:shot.mode,local_time:t,actor_time:t+c.index*13.7,subject_motion:'original articulated meshes and deterministic continuous-world actions',voice_time_stretched:false};prior=globalFrame;
}
window.__seek=draw;window.__schedule=schedule;draw(0);window.__ready=true;
let playing=false,startClock=0,startFrame=0,raf=null;const audio=document.querySelector('audio');
function tick(now){if(!playing)return;const frame=startFrame+(now-startClock)*FPS/1000;draw(frame);if(frame>=schedule.total_frames-1){playing=false;audio.pause();return;}const c=schedule.chapters.find(c=>frame>=c.start_frame&&frame<c.start_frame+c.frames);if(audio.dataset.chapter!==c.id){audio.src='/voice/'+c.id+'.flac';audio.dataset.chapter=c.id;audio.currentTime=Math.max(0,(frame-c.start_frame)/FPS);audio.play().catch(()=>{});}raf=requestAnimationFrame(tick);}
const btn=document.querySelector('#play');if(btn)btn.onclick=()=>{playing=!playing;btn.textContent=playing?'Pause work-in-progress preview':'Play work-in-progress preview';if(playing){startFrame=window.__state.frame;startClock=performance.now();const c=schedule.chapters.find(c=>startFrame>=c.start_frame&&startFrame<c.start_frame+c.frames);audio.src='/voice/'+c.id+'.flac';audio.dataset.chapter=c.id;audio.currentTime=(startFrame-c.start_frame)/FPS;audio.play().catch(()=>{});raf=requestAnimationFrame(tick);}else{audio.pause();cancelAnimationFrame(raf);}};
