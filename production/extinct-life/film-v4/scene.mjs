import * as T from 'three';
import {buildWorld,focus} from './worlds.mjs';
import {cameraPose,activeSequence,eventAt,smooth as flowEase} from './direction.mjs';
const canvas=document.querySelector('#final'),ctx=canvas.getContext('2d',{alpha:false});
const W=1920,H=1080,FPS=30;
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.18;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;
const camera=new T.PerspectiveCamera(39,W/H,.025,250);
const schedule=await fetch('/schedule.json').then(r=>r.json());const cache=new Map();
await Promise.all([document.fonts.load('22px AtlasSans'),document.fonts.load('64px AtlasSerif')]);await document.fonts.ready;
const clamp=x=>Math.max(0,Math.min(1,x)),smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
let prior=-1;
const names=['A TRACE OF A GIANT','HOW LIFE LEAVES A CLUE','WHAT THE MINERALS KEPT','TESTING THE IDENTITY','MORE THAN ONE ANIMAL','IMAGINING IS NOT OBSERVING','THE GAPS IN THE RECORD','WHAT THE DIRT GAVE BACK'];
function panel(text,x,y,size=21,color='#cfc9b3'){ctx.font=`${size}px AtlasSans`;ctx.fillStyle=color;ctx.shadowColor='rgba(5,15,20,.85)';ctx.shadowBlur=10;ctx.fillText(text,x,y);ctx.shadowBlur=0;}
function getWorld(sequence){
 if(cache.has(sequence.id)){const w=cache.get(sequence.id);cache.delete(sequence.id);cache.set(sequence.id,w);return w;}
 const w=buildWorld(sequence);w.defaults=(w.motionRoots||[]).map(o=>({o,scale:o.scale.clone(),visible:o.visible}));cache.set(sequence.id,w);
 while(cache.size>2){const id=cache.keys().next().value,old=cache.get(id),disposed=new Set();old.scene.traverse(o=>{if(o.geometry&&!disposed.has(o.geometry)){o.geometry.dispose();disposed.add(o.geometry);}if(o.shadow?.map)o.shadow.map.dispose();});cache.delete(id);renderer.renderLists.dispose();}
 return w;
}
function resetRoots(w){for(const d of w.defaults){d.o.scale.copy(d.scale);d.o.visible=d.visible;}}
function updateWorld(w,sequence,frame){
 const age=Math.max(0,(frame-sequence.start_frame)/FPS),time=age+sequence.seed*.001,{current,previous,weight}=eventAt(sequence,frame),mode=current.mode.split('-')[1];
 resetRoots(w);w.update(time,previous.mode.split('-')[1],age,sequence.chapter);
 const before=(w.motionRoots||[]).map(o=>({p:o.position.clone(),q:o.quaternion.clone(),s:o.scale.clone().multiplyScalar(o.visible?1:0)}));
 resetRoots(w);w.update(time,mode,age,sequence.chapter);
 (w.motionRoots||[]).forEach((o,i)=>{const end=o.scale.clone().multiplyScalar(o.visible?1:0);o.position.lerpVectors(before[i].p,o.position,weight);o.quaternion.slerpQuaternions(before[i].q,o.quaternion,weight);o.scale.lerpVectors(before[i].s,end,weight);o.visible=o.scale.lengthSq()>.000001;});
 return {mode,age};
}
function layer(sequence,frame,opacity,defocus=0){
 const w=getWorld(sequence),state=updateWorld(w,sequence,frame),pose=cameraPose(sequence,focus,frame);
 camera.position.set(...pose.position);camera.lookAt(new T.Vector3(...pose.target));camera.updateMatrixWorld();renderer.render(w.scene,camera);ctx.globalAlpha=opacity;ctx.filter=defocus>0?`blur(${defocus.toFixed(2)}px)`:'none';ctx.drawImage(renderer.domElement,0,0,W,H);ctx.globalAlpha=1;ctx.filter='none';return {...state,pose};
}
function draw(globalFrame){
 globalFrame=Math.max(0,Math.min(schedule.total_frames-1,Math.round(globalFrame)));
 const c=schedule.chapters.find(c=>globalFrame>=c.start_frame&&globalFrame<c.start_frame+c.frames),f=globalFrame-c.start_frame,t=f/FPS;
 const sequence=activeSequence(schedule,globalFrame),index=schedule.sequences.indexOf(sequence),worldKey=sequence.world;
 const elapsed=globalFrame-sequence.start_frame,blending=index>0&&elapsed<sequence.blend_frames,opacity=blending?flowEase(elapsed/sequence.blend_frames):1;
 const defocus=blending?26*Math.sin(Math.PI*elapsed/sequence.blend_frames)**2:0;
 if(blending)layer(schedule.sequences[index-1],globalFrame,1,defocus);
 const rendered=layer(sequence,globalFrame,opacity,defocus),mode=rendered.mode;
 // Restrained edge falloff and subtle deterministic grain; the underlying subjects are animated meshes.
 const vignette=ctx.createRadialGradient(W*.5,H*.45,H*.2,W*.5,H*.5,W*.68);vignette.addColorStop(0,'rgba(4,16,22,0)');vignette.addColorStop(1,'rgba(3,13,19,.3)');ctx.fillStyle=vignette;ctx.fillRect(0,0,W,H);
 panel('EXTINCT LIFE',76,68,22,'#e7dbbd');ctx.fillStyle='#b58f54';ctx.fillRect(76,81,38,2);
 const label=(worldKey==='habit')?'ILLUSTRATIVE RECONSTRUCTION · NOT AN OBSERVED ENCOUNTER':worldKey==='macro'?'CONCEPTUAL MOLECULAR ILLUSTRATION · NOT TO SCALE':worldKey==='compare'?'REFERENCE-MATCHING ILLUSTRATION · NOT ACTUAL SEQUENCE READS':worldKey==='lab'?'ILLUSTRATIVE LABORATORY · NOT STUDY FOOTAGE':worldKey==='evidence'?'ILLUSTRATIVE EVIDENCE · NO COMPLETE INVENTORY':worldKey==='river'?'REPRESENTATIVE TRANSPORT PATH · NOT A TRACKED MOLECULE':worldKey==='sediment'?'CONCEPTUAL SEDIMENT SECTION · NOT A MEASURED SAMPLE':'NORTH GREENLAND · LANDSCAPE RECONSTRUCTION';
 panel(label,76,1010,18,'#d2d4c8');
 if(t<3.2){ctx.globalAlpha=Math.min(1,t/.35)*Math.min(1,(3.2-t)/.4);panel(String(c.index+1).padStart(2,'0')+' / '+names[c.index],76,132,26,'#eadab9');ctx.globalAlpha=1;}
 if(c.index===4&&t<7){const entries=[['Hares',.1],['Reindeer',1.1],['Geese',2],['Rodents',2.9],['Mastodon lineage',3.8]];panel('DNA EVIDENCE: '+entries.filter(e=>t>=e[1]).map(e=>e[0]).join(' · '),76,953,25,'#eadab9');}
 if(worldKey==='evidence'){panel(mode==='gaps'?'No signal is not the same as no animal':'DNA · pollen · larger remains — complementary, incomplete records',76,953,25,'#eadab9');}
 // Persistent evidence keys, never fictional species accuracy percentages.
 if(worldKey==='compare'){
  const text=mode==='missing'?'A missing reference is not a missing animal':mode==='family'?'Shared sequences can limit identification':mode==='damage'?'Damage patterns are one part of the checks':'Compare. Check alternatives. Keep the uncertainty.';
  panel(text,76,953,27,'#eadab9');
 }
 if(c.index===7&&f>c.frames-90){const a=smooth((f-(c.frames-90))/55);ctx.fillStyle=`rgba(8,23,29,${a*.35})`;ctx.fillRect(0,0,W,H);ctx.globalAlpha=a;ctx.font='64px AtlasSerif';ctx.textAlign='center';ctx.fillStyle='#ebdfbf';ctx.fillText('EXTINCT LIFE',W/2,H*.47);ctx.font='23px AtlasSans';ctx.fillText('THE LOST WORLD INSIDE A HANDFUL OF DIRT',W/2,H*.53);ctx.textAlign='left';ctx.globalAlpha=1;}
 window.__state={frame:globalFrame,chapter:c.id,sequence:sequence.id,set_design:sequence.design,set_seed:sequence.seed,mode:worldKey+'-'+mode,local_time:t,sequence_age:rendered.age,camera_position:rendered.pose.position,camera_target:rendered.pose.target,transition:blending?'full-frame focus bridge between different physical scales':'continuous spatial move',transition_weight:opacity,forced_three_second_cuts:false,voice_time_stretched:false};prior=globalFrame;
}
window.__seek=draw;window.__schedule=schedule;draw(0);window.__ready=true;
let playing=false,startClock=0,startFrame=0,raf=null;const audio=document.querySelector('audio');
function tick(now){if(!playing)return;const frame=startFrame+(now-startClock)*FPS/1000;draw(frame);if(frame>=schedule.total_frames-1){playing=false;audio.pause();return;}const c=schedule.chapters.find(c=>frame>=c.start_frame&&frame<c.start_frame+c.frames);if(audio.dataset.chapter!==c.id){audio.src='/voice/'+c.id+'.flac';audio.dataset.chapter=c.id;audio.currentTime=Math.max(0,(frame-c.start_frame)/FPS);audio.play().catch(()=>{});}raf=requestAnimationFrame(tick);}
const btn=document.querySelector('#play');if(btn)btn.onclick=()=>{playing=!playing;btn.textContent=playing?'Pause work-in-progress preview':'Play work-in-progress preview';if(playing){startFrame=window.__state.frame;startClock=performance.now();const c=schedule.chapters.find(c=>startFrame>=c.start_frame&&startFrame<c.start_frame+c.frames);audio.src='/voice/'+c.id+'.flac';audio.dataset.chapter=c.id;audio.currentTime=(startFrame-c.start_frame)/FPS;audio.play().catch(()=>{});raf=requestAnimationFrame(tick);}else{audio.pause();cancelAnimationFrame(raf);}};
