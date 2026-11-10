// Per-frame renderer for the experimental genetic evidence scene; no frame interpolation.
import fs from 'node:fs';import path from 'node:path';import http from 'node:http';import {spawn,execFileSync} from 'node:child_process';import {once} from 'node:events';import {createHash} from 'node:crypto';import {chromium} from 'playwright';import chromiumBin from '@sparticuz/chromium';
const ROOT=process.cwd(),BASE=path.join(ROOT,'production/extinct-life/longform-mammoth/cinematic-rebuild/genetics-recut'),CACHE=path.join(ROOT,'.cache/mammoth-genetics-recut');fs.mkdirSync(CACHE,{recursive:true});
const files={'/':'stage.html','/scene.mjs':'scene.mjs','/three.module.js':path.join(ROOT,'node_modules/three/build/three.module.js'),'/three.core.js':path.join(ROOT,'node_modules/three/build/three.core.js'),'/Manrope.ttf':path.join(ROOT,'public/showreel/fonts/Manrope-800.ttf')};
const server=http.createServer((req,res)=>{let n=new URL(req.url,'http://x').pathname,f=files[n];if(!f)return res.writeHead(404).end();if(!path.isAbsolute(f))f=path.join(BASE,f);res.setHeader('Content-Type',({'.mjs':'application/javascript','.js':'application/javascript','.html':'text/html','.ttf':'font/ttf'})[path.extname(f)]||'application/octet-stream');fs.createReadStream(f).pipe(res);});await new Promise(r=>server.listen(0,'127.0.0.1',r));
let browser,encoder;const errors=[];
try{
 browser=await chromium.launch({executablePath:await chromiumBin.executablePath(),env:{...process.env,LD_LIBRARY_PATH:path.join(ROOT,'.cache/extinct-v14/libs/lib')},args:[...chromiumBin.args,'--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--disable-dev-shm-usage'],headless:true});
 const page=await browser.newPage({viewport:{width:1280,height:720}});page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`)});
 await page.goto(`http://127.0.0.1:${server.address().port}`,{waitUntil:'commit'});await page.waitForFunction(()=>window.__ready,null,{timeout:180000});if(errors.length)throw Error(errors.join('; '));
 const capture=async t=>page.evaluate(t=>{const state=window.__seek(t);return {state,jpeg:document.querySelector('#final').toDataURL('image/jpeg',.94).split(',')[1]};},t);
 if(process.argv.includes('--verify')){
  const x=await capture(2), y=await capture(12), z=await capture(2), d=await capture(22), e=await capture(24), f=await capture(26), g=await capture(28.5);
  if(x.jpeg!==z.jpeg)throw Error('Random-access frame is not deterministic');
  if(x.state.shot!=='lab-specimen'||d.state.shot!=='schematic-dna')throw Error('Wrong sequence at requested time');
  if(!(y.state.carriageX>x.state.carriageX))throw Error('Scan carriage did not move along the rail');
  if(d.state.shot!=='schematic-dna'||e.state.shot!=='deletion-wide'||f.state.shot!=='deletion-detail'||g.state.shot!=='translation-stop')throw Error('Molecular narrative cuts missing');
  if(!(f.state.deletedY<e.state.deletedY))throw Error('Deletion fragment did not move');
  if(d.jpeg===e.jpeg)throw Error('Molecular shot is visually static');
  console.log('PASS: deterministic random seek, connected scanner motion and moving schematic sequence; no page errors.');
 }else if(process.argv.includes('--stills')){
  for(let t of [0,3.5,6.5,9,11.5,14,16.5,19,21,23.5,25,26.5,28.5,29.5]){let x=await capture(t);fs.writeFileSync(path.join(CACHE,`still-${String(t).replace('.', '_')}.jpg`),Buffer.from(x.jpeg,'base64'));console.log('still',t,x.state.shot);}
 }else{
  const ff=execFileSync(path.join(ROOT,'.venv/bin/python'),['-c','import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'],{encoding:'utf8'}).trim();
  const fps=30,frames=893;
  encoder=spawn(ff,['-y','-v','warning','-f','image2pipe','-framerate',String(fps),'-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p',path.join(CACHE,'lab-plate.mp4')],{stdio:['pipe','inherit','inherit']});const done=once(encoder,'exit');const start=Date.now(),runs=[];
  for(let f=0;f<frames;f++){let x=await capture(f/fps);if(!runs.length||runs.at(-1).shot!==x.state.shot)runs.push({shot:x.state.shot,from:f,to:f+1});else runs.at(-1).to=f+1;if(!encoder.stdin.write(Buffer.from(x.jpeg,'base64')))await once(encoder.stdin,'drain');if((f+1)%90===0)console.log(`frame ${f+1}/${frames} ${x.state.shot} ${((Date.now()-start)/1000).toFixed(1)}s`);}
  encoder.stdin.end();const [code]=await done;if(code||errors.length)throw Error(`encoder=${code}; ${errors.join('; ')}`);
  const hash=createHash('sha256').update(fs.readFileSync(path.join(BASE,'scene.mjs'))).update(fs.readFileSync(path.join(BASE,'stage.html'))).digest('hex');
  fs.writeFileSync(path.join(CACHE,'render.json'),JSON.stringify({frames,fps,width:1280,height:720,scene_sha256:hash,errors,runs,render_seconds:(Date.now()-start)/1000},null,2));console.log('render completed');
 }
 if(errors.length)throw Error(errors.join('; '));
}finally{if(encoder&&encoder.exitCode===null)encoder.kill();if(browser)await browser.close();server.close();}
