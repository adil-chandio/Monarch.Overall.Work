import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {spawn,execFileSync} from 'node:child_process';
import {once} from 'node:events';
import {createHash} from 'node:crypto';
import {createCanvas,Path2D,GlobalFonts} from '@napi-rs/canvas';
const P=path.dirname(fileURLToPath(import.meta.url)),R=path.resolve(P,'../../..'),C=path.join(R,'.cache/extinct-feature');
const plan=JSON.parse(fs.readFileSync(path.join(P,'timeline.json'),'utf8'));
fs.mkdirSync(C,{recursive:true});
if(process.argv.includes('--all')){
  // Independent exact frame ranges, two workers; rerender explicitly after source changes.
  let next=0;
  async function worker(){while(next<plan.chapters.length){const i=next++;const file=path.join(C,`chapter-${i}.mp4`);const p=spawn(process.execPath,[fileURLToPath(import.meta.url),'--chapter',String(i)],{stdio:'inherit'});const [code]=await once(p,'close');if(code!==0)throw Error('Chapter failed: '+i);}}
  await Promise.all([worker(),worker()]);console.log('All eight chapters rendered.');process.exit(0);
}
for(const [f,n]of [['DejaVuSerif.ttf','AtlasSerif'],['DejaVuSans.ttf','Arial']])if(!GlobalFonts.registerFromPath('/usr/share/fonts/truetype/dejavu/'+f,n))throw Error('Missing font '+n);
const canvas=createCanvas(1920,1080),window={};const document={querySelector:()=>canvas,createElement:()=>createCanvas(300,150),fonts:{load:async()=>[]}};
const helper=fs.readFileSync(path.join(P,'stage.html'),'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const source=helper+'\n'+fs.readFileSync(path.join(P,'scenes.js'),'utf8');
vm.runInNewContext(source,{window,document,Path2D,console,fetch:async u=>({json:async()=>JSON.parse(fs.readFileSync(path.join(P,path.basename(u)),'utf8'))})},{filename:'feature-scenes.js'});
await new Promise(r=>setImmediate(r));if(!window.__ready)throw Error('Scene readiness failed');
if(process.argv.includes('--stills')){
 for(const s of plan.shots){const f=Math.round((s.start_frame+s.end_frame)/2);window.__seek(f);fs.writeFileSync(path.join(C,`still-${String(s.index).padStart(2,'0')}.jpg`),canvas.encodeSync('jpeg',94));}
 console.log('40 independent shot previews rendered.');
}else if(process.argv.includes('--verify')){
 const hash=f=>{window.__seek(f);return createHash('sha256').update(canvas.encodeSync('jpeg',94)).digest('hex')};
 const samples=[];for(const s of plan.shots){const f=Math.round((s.start_frame+s.end_frame)/2),a=hash(f);hash((f+891)%plan.body_frames);if(a!==hash(f))throw Error('State leak at shot '+s.index);samples.push({shot:s.index,frame:f,sha256:a});}
 const provenance=createHash('sha256').update(source).update(fs.readFileSync(path.join(P,'timeline.json'))).digest('hex');
 fs.writeFileSync(path.join(P,'render-checks.json'),JSON.stringify({provenance_sha256:provenance,renderer:'@napi-rs/canvas 1.1.0 / Skia',width:1920,height:1080,fps:30,body_frames:plan.body_frames,non_monotonic_seek_checks:samples},null,2));console.log('40/40 shot seeks are deterministic.');
}else{
 const arg=process.argv.indexOf('--chapter'),index=arg>=0?Number(process.argv[arg+1]):0,ch=plan.chapters[index];if(!ch)throw Error('Invalid chapter');
 const ff=execFileSync(path.join(R,'.venv/bin/python'),['-c','import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())'],{encoding:'utf8'}).trim();
 const out=path.join(C,`chapter-${index}.mp4`),tmp=out+'.partial.mp4';
 const p=spawn(ff,['-y','-hide_banner','-loglevel','error','-f','image2pipe','-vcodec','mjpeg','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',tmp]);let errors='';p.stderr.on('data',b=>{errors=(errors+b).slice(-5000)});const done=once(p,'close');
 for(let k=0;k<ch.frames;k++){window.__seek(ch.start_frame+k);if(!p.stdin.write(canvas.encodeSync('jpeg',94)))await once(p.stdin,'drain');if(k%300===0)console.log(`Chapter ${index+1}/8: ${k}/${ch.frames}`);}
 p.stdin.end();const [code]=await done;if(code!==0)throw Error(errors);fs.renameSync(tmp,out);console.log(`Chapter ${index+1} complete: ${ch.frames} frames.`);
}
