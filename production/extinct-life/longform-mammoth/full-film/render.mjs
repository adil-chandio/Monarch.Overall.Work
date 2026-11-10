// Headless 3D renderer. A 4 fps moving 3D plate is interpolated to 30 fps
// during finishing; opening-3d is the independently rendered 30 fps sequence.
import fs from 'node:fs';import path from 'node:path';import http from 'node:http';
import {spawn,execFileSync} from 'node:child_process';import {once} from 'node:events';
import {chromium} from 'playwright';import chromiumBin from '@sparticuz/chromium';
const ROOT=process.cwd(),BASE=path.join(ROOT,'production/extinct-life/longform-mammoth/full-film'),C=path.join(ROOT,'.cache/longform-mammoth-full');
fs.mkdirSync(C,{recursive:true});fs.mkdirSync(path.join(C,'stills'),{recursive:true});
const plan=JSON.parse(fs.readFileSync(path.join(BASE,'timeline.json'))), fps=4;
const arg=(key,def)=>{let hit=process.argv.find(a=>a.startsWith('--'+key+'='));return hit?hit.slice(hit.indexOf('=')+1):def};
const files={'/':'stage.html','/scene.mjs':'scene.mjs','/timeline.json':'timeline.json'};
const server=http.createServer((req,res)=>{const u=new URL(req.url,'http://local'),n=decodeURIComponent(u.pathname);if(n.includes('..'))return res.writeHead(403).end();let f;
 if(files[n])f=path.join(BASE,files[n]);else if(n==='/three.module.js')f=path.join(ROOT,'node_modules/three/build/three.module.js');else if(n==='/three.core.js')f=path.join(ROOT,'node_modules/three/build/three.core.js');else if(n==='/Manrope.ttf')f=path.join(ROOT,'public/showreel/fonts/Manrope-800.ttf');else if(n==='/Anton.ttf')f=path.join(ROOT,'public/showreel/fonts/Anton-Regular.ttf');else f=path.join(BASE,n);
 if(!fs.existsSync(f)||fs.statSync(f).isDirectory())return res.writeHead(404).end();
 res.setHeader('Content-Type',({'.mjs':'application/javascript','.js':'application/javascript','.html':'text/html','.json':'application/json','.ttf':'font/ttf','.jpg':'image/jpeg'})[path.extname(f)]||'application/octet-stream');fs.createReadStream(f).pipe(res);
});await new Promise(r=>server.listen(0,'127.0.0.1',r));
let browser,enc;
try{
 browser=await chromium.launch({executablePath:await chromiumBin.executablePath(),env:{...process.env,LD_LIBRARY_PATH:path.join(ROOT,'.cache/extinct-v14/libs/lib')},args:[...chromiumBin.args,'--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--disable-dev-shm-usage'],headless:true});
 const page=await browser.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`)});
 await page.goto('http://127.0.0.1:'+server.address().port,{waitUntil:'commit',timeout:120000});await page.waitForFunction(()=>window.__ready,null,{timeout:180000});if(errors.length)throw Error(errors.join('; '));
 async function capture(t){return page.evaluate(t=>{const shot=window.__seek(t);return {shot,jpg:document.querySelector('#final').toDataURL('image/jpeg',.92).split(',')[1]}},t)}
 if(process.argv.includes('--stills')){
  for(const time of arg('times','65,140,210,260,330,390,470,530,600,680').split(',').map(Number)){const data=await capture(time);fs.writeFileSync(path.join(C,'stills',String(time).padStart(4,'0')+'.jpg'),Buffer.from(data.jpg,'base64'));console.log('still',time,data.shot)}
 }else{
  const FF=execFileSync(path.join(ROOT,'.venv/bin/python'),['-c','import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'],{encoding:'utf8'}).trim();
  enc=spawn(FF,['-y','-v','warning','-f','image2pipe','-framerate',String(fps),'-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','17','-threads','2','-pix_fmt','yuv420p',path.join(C,'visual-4fps.mp4')],{stdio:['pipe','inherit','inherit']});const done=once(enc,'exit');
  const count=Math.ceil((plan.duration-plan.opening_seconds)*fps),start=Date.now();
  for(let i=0;i<count;i++){const t=plan.opening_seconds+i/fps,a=await capture(t);if(!enc.stdin.write(Buffer.from(a.jpg,'base64')))await once(enc.stdin,'drain');if((i+1)%120===0)console.log(`frame ${i+1}/${count} t=${t.toFixed(2)} ${a.shot} elapsed=${((Date.now()-start)/1000).toFixed(1)}s`)}
  enc.stdin.end();const [code]=await done;if(code)throw Error('encoder exited '+code);if(errors.length)throw Error(errors.join('; '));
  fs.writeFileSync(path.join(C,'render.json'),JSON.stringify({count,fps,width:1280,height:720,start:plan.opening_seconds,end:plan.duration,errors,render_seconds:(Date.now()-start)/1000},null,2));console.log('render complete',count,'frames');
 }
}finally{if(enc&&enc.exitCode===null)enc.kill();if(browser)await browser.close();server.close()}
