import * as T from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {BokehPass} from 'three/addons/postprocessing/BokehPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {buildWorld} from './worlds.mjs';
const schedule=await(await fetch('./schedule.json')).json(),W=1920,H=1080;
const canvas=document.querySelector('#stage'),ctx=document.querySelector('#overlay').getContext('2d');
const renderer=new T.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});renderer.setSize(W,H,false);renderer.setPixelRatio(1);renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
const camera=new T.PerspectiveCamera(39,W/H,.03,150),composer=new EffectComposer(renderer),pass=new RenderPass(new T.Scene(),camera),bokeh=new BokehPass(pass.scene,camera,{focus:7,aperture:.000025,maxblur:.0012});composer.addPass(pass);composer.addPass(bokeh);composer.addPass(new OutputPass());composer.setSize(W,H);
const cache=new Map(),clamp=x=>Math.max(0,Math.min(1,x)),smooth=x=>{x=clamp(x);return x*x*(3-2*x);};let active;
function world(s){if(!cache.has(s.id))cache.set(s.id,buildWorld(s));return cache.get(s.id);}
function setCamera(p){camera.position.set(...p.position);camera.lookAt(...p.target);camera.updateMatrixWorld(true);return camera.position.distanceTo(new T.Vector3(...p.target));}
function text(w,t){ctx.clearRect(0,0,W,H);ctx.textBaseline='middle';const age=t%8.5,visibility=smooth(age/.6)*(1-smooth((age-5.5)/.8));for(const l of w.labels(t)){const v=new T.Vector3(...l.point).project(camera);if(v.z>1||v.z< -1)continue;const x=(v.x*.5+.5)*W,y=(-v.y*.5+.5)*H;if(x<110||x>W-380||y<90||y>H-150)continue;const a=visibility*l.opacity;if(a<.01)continue;const dx=25*(1-smooth(age/.7));ctx.save();ctx.globalAlpha=a;ctx.strokeStyle='#e4cf9a';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+23,y-26);ctx.lineTo(x+65,y-26);ctx.stroke();ctx.beginPath();ctx.arc(x,y,3,0,Math.PI*2);ctx.fillStyle='#ebd8b0';ctx.fill();ctx.font='500 31px Arial';ctx.fillStyle='#f4f2e7';ctx.shadowColor='rgba(7,20,25,.95)';ctx.shadowBlur=7;ctx.shadowOffsetY=2;ctx.fillText(l.text,x+31+dx,y-50);ctx.restore();}
 if(t<5.5&&w.qualifier){ctx.save();ctx.globalAlpha=.85*smooth(t/.7)*(1-smooth((t-4.6)/.7));ctx.font='22px Arial';ctx.fillStyle='#e3e7df';ctx.shadowColor='#10232b';ctx.shadowBlur=5;ctx.shadowOffsetY=2;ctx.fillText(w.qualifier,68,H-49);ctx.restore();}}
async function render(frame,{lockCamera=false}={}){const s=schedule.sequences.find(s=>frame>=s.start_frame&&frame<s.end_frame)||schedule.sequences.at(-1),w=world(s),t=(frame-s.start_frame)/30;active={s,w,t};w.update(t);const dist=setCamera(w.camera(lockCamera?0:t));pass.scene=w.scene;bokeh.scene=w.scene;bokeh.uniforms.focus.value=dist;composer.render();text(w,t);const edge=s.blend_frames||0;if(edge&&frame-s.start_frame<edge){const previous=schedule.sequences[schedule.sequences.indexOf(s)-1];if(previous){const pw=world(previous),pt=(previous.end_frame-previous.start_frame-1)/30;pw.update(pt);const alpha=1-smooth((frame-s.start_frame)/edge);const fresh=document.createElement('canvas');fresh.width=W;fresh.height=H;fresh.getContext('2d').drawImage(canvas,0,0);setCamera(pw.camera(pt));pass.scene=pw.scene;bokeh.scene=pw.scene;bokeh.uniforms.focus.value=camera.position.distanceTo(new T.Vector3(...pw.camera(pt).target));composer.render();ctx.save();ctx.globalAlpha=1-alpha;ctx.drawImage(fresh,0,0);ctx.restore();}}
 window.__frameState={frame,sequence:s.id,world:s.world,time:t,...w.state,camera:camera.position.toArray(),caption_panels:0,organic_native_assets:true};return window.__frameState;}
window.renderFrame=render;window.__film={schedule,render,readState:()=>window.__frameState,ready:true};window.__ready=true;
const final=document.querySelector('#final'),fc=final.getContext('2d');
window.__seek=frame=>{render(frame,{lockCamera:!!window.__freezeCamera});fc.clearRect(0,0,W,H);fc.drawImage(canvas,0,0);fc.drawImage(document.querySelector('#overlay'),0,0);window.__state=window.__frameState;};
window.__seek(0);
const audio=document.querySelector('audio');audio.src='/proof.wav';let playing=false;
document.querySelector('#play').onclick=async()=>{playing=!playing;if(playing){await audio.play();requestAnimationFrame(tick);}else audio.pause();};
function tick(){if(!playing)return;window.__seek(Math.min(schedule.total_frames-1,Math.floor(audio.currentTime*30)));requestAnimationFrame(tick);}

