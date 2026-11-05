import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawn,execFileSync} from 'node:child_process';
import {once} from 'node:events';
import {createCanvas,Path2D,GlobalFonts} from '@napi-rs/canvas';

const dir=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(dir,'../../..');
const cache=path.join(root,'.cache/extinct-opening-25d-v2');
fs.mkdirSync(cache,{recursive:true});
// Execute the very same deterministic Canvas scene source without browser IPC.
// Skia rasterizes every 1920x1080 frame natively; no still-image pans or fps interpolation.
for(const [file,family] of [['DejaVuSerif.ttf','AtlasSerif'],['DejaVuSans.ttf','Arial']]){
  if(!GlobalFonts.registerFromPath('/usr/share/fonts/truetype/dejavu/'+file,family))throw Error('Font registration failed: '+family);
}
const canvas=createCanvas(1920,1080),window={};
const document={querySelector:()=>canvas,createElement:()=>createCanvas(300,150),fonts:{load:async()=>[]}};
const source=fs.readFileSync(path.join(dir,'stage.html'),'utf8').match(/<script>([\s\S]*)<\/script>/)[1];
vm.runInNewContext(source,{window,document,Path2D,console,fetch:async url=>({json:async()=>JSON.parse(fs.readFileSync(path.join(dir,path.basename(url)),'utf8'))})},{filename:'stage.html'});
// Assets are local, but the scene intentionally exposes an asynchronous readiness contract.
await new Promise(resolve=>setImmediate(resolve));
if(!window.__ready)throw Error('Scene did not initialize');
const seamTimes=JSON.parse(fs.readFileSync(path.join(dir,'edit.json'),'utf8')).seams.map(x=>x.t);
const diagnostics={source_sha256:createHash('sha256').update(source).digest('hex'),edit_sha256:createHash('sha256').update(fs.readFileSync(path.join(dir,'edit.json'))).digest('hex'),rasterizer:'@napi-rs/canvas / Skia',width:1920,height:1080,fps:30,frames:1350,camera:seamTimes.map(t=>({t,before:window.__motionStats(t-.001),at:window.__motionStats(t),after:window.__motionStats(t+.001)}))};
const checkFile=path.join(cache,'render.json');
if(fs.existsSync(checkFile)){const previous=JSON.parse(fs.readFileSync(checkFile,'utf8'));if(previous.source_sha256===diagnostics.source_sha256&&previous.edit_sha256===diagnostics.edit_sha256&&previous.non_monotonic_seek_probes)diagnostics.non_monotonic_seek_probes=previous.non_monotonic_seek_probes;}
fs.writeFileSync(checkFile,JSON.stringify(diagnostics,null,2));
if(process.argv.includes('--verify')){
  const checksum=f=>{window.__seek(f);return createHash('sha256').update(canvas.encodeSync('jpeg',94)).digest('hex')};
  const probes=[];
  for(const f of [19,234,428,628,778,965,1270]){const first=checksum(f);checksum((f+311)%1350);const second=checksum(f);if(first!==second)throw Error('Non-deterministic random seek at frame '+f);probes.push({frame:f,sha256:first});}
  diagnostics.non_monotonic_seek_probes=probes;
  fs.writeFileSync(path.join(cache,'render.json'),JSON.stringify(diagnostics,null,2));
  console.log('Seven out-of-order frame seeks are pixel-encoding identical.');
}else if(process.argv.includes('--stills')){
  for(const [i,t] of [0.6,2.4,4.6,7.9,10,12.3,15.5,20.7,25.8,28.8,32.9,38.4,42.3].entries()){
    window.__seek(Math.round(t*30));fs.writeFileSync(path.join(cache,`still-${String(i).padStart(2,'0')}.jpg`),canvas.encodeSync('jpeg',94));
  }
  console.log('13 native-resolution keyframes rendered.');
}else{
  const ffmpeg=execFileSync(path.join(root,'.venv/bin/python'),['-c','import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())'],{encoding:'utf8'}).trim();
  const p=spawn(ffmpeg,['-y','-hide_banner','-loglevel','error','-f','image2pipe','-vcodec','mjpeg','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',path.join(cache,'picture.mp4')]);
  let errors='';p.stderr.on('data',b=>{errors=(errors+b).slice(-5000)});
  const done=once(p,'close');
  for(let f=0;f<1350;f++){
    window.__seek(f);const frame=canvas.encodeSync('jpeg',94);
    if(!p.stdin.write(frame))await once(p.stdin,'drain');
    if(f%90===0)console.log(`Frame ${f}/1350 (${(f/30).toFixed(1)}s)`);
  }
  p.stdin.end();const [code]=await done;if(code!==0)throw Error('Encoder failed: '+errors);
  console.log('Picture complete: native 1080p, 1350 frames, 30 fps.');
}
