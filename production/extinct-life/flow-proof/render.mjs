// Own deterministic harness adapted from the repo's showreel capture pattern.
import fs from 'node:fs';import path from 'node:path';import http from 'node:http';import zlib from 'node:zlib';import {spawn,execFileSync} from 'node:child_process';import {once} from 'node:events';import {chromium} from 'playwright';import serverChromium from '@sparticuz/chromium';
const START=Number(process.argv.find(x=>x.startsWith('--from='))?.split('=')[1]||0);if(!Number.isInteger(START)||START<0||START>=720)throw Error('Invalid first frame');
const root=process.cwd(),cache=path.join(root,'.cache/extinct-flow');fs.mkdirSync(cache,{recursive:true});
const FF=execFileSync(path.join(root,'.venv/bin/python'),['-c','import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'],{encoding:'utf8'}).trim();
const base=path.join(root,'production/extinct-life/flow-proof');
const files={'/':path.join(base,'stage.html'),'/scene.mjs':path.join(base,'scene.mjs'),'/atlas-serif.ttf':'/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf','/three.module.js':path.join(root,'node_modules/three/build/three.module.js'),'/three.core.js':path.join(root,'node_modules/three/build/three.core.js')};
const server=http.createServer((req,res)=>{let file=files[req.url];if(req.url.startsWith('/addons/')&&!req.url.includes('..'))file=path.join(root,'node_modules/three/examples/jsm',req.url.slice(8));if(req.url.startsWith('/materials/')&&!req.url.includes('..'))file=path.join(base,req.url);if(!file||!fs.existsSync(file)){res.writeHead(404).end();return;}res.setHeader('Content-Type',req.url.endsWith('.jpg')?'image/jpeg':req.url==='/'?'text/html':'application/javascript');res.end(fs.readFileSync(file));});
await new Promise(r=>server.listen(0,'0.0.0.0',r));
let browser,enc;
// Lambda Chromium bundles NSS/NSPR; unpack locally when the Linux image lacks them.
const libs=path.join(cache,'libs');fs.mkdirSync(libs,{recursive:true});
if(!fs.existsSync(path.join(libs,'lib/libnspr4.so'))){const tar=path.join(cache,'chrome-libs.tar');fs.writeFileSync(tar,zlib.brotliDecompressSync(fs.readFileSync(path.join(root,'node_modules/@sparticuz/chromium/bin/al2023.tar.br'))));execFileSync('tar',['-xf',tar,'-C',libs]);fs.unlinkSync(tar);}
try{
 browser=await chromium.launch({env:{...process.env,LD_LIBRARY_PATH:path.join(libs,'lib')+':'+(process.env.LD_LIBRARY_PATH||'')},executablePath:await serverChromium.executablePath(),args:[...serverChromium.args,'--enable-unsafe-swiftshader','--ignore-gpu-blocklist'],headless:true});
 const context=await browser.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1});const page=await context.newPage();page.on('pageerror',e=>console.error(e));
 await page.goto(`http://127.0.0.1:${server.address().port}/`);await page.waitForFunction(()=>window.__ready,null,{timeout:90000});
 for(const t of [1.2,4.5,7.5,10.5,13.5,16.5,19.5,22.5]){const jpg=await page.evaluate(f=>{window.__seek(f);return document.querySelector('#final').toDataURL('image/jpeg',.95).split(',')[1];},Math.round(t*30));fs.writeFileSync(path.join(cache,`still_${t}.jpg`),Buffer.from(jpg,'base64'));}
 const checks=[];for(const f of [0,89,90,179,180,269,270,359,360,449,450,539,540,629,630,719]){checks.push(await page.evaluate(f=>{window.__seek(f);return window.__state;},f));}fs.writeFileSync(path.join(cache,'states.json'),JSON.stringify(checks,null,2));
 const capture=async f=>page.evaluate(f=>{window.__seek(f);return document.querySelector('#final').toDataURL('image/jpeg',.95);},f);
 const repeatA=await capture(390);await capture(719);const repeatB=await capture(390);if(repeatA!==repeatB)throw Error('Non-deterministic repeated seek: inspect depth-buffer state');console.log('Deterministic A/B/A frame check passed');
 if(!process.argv.includes('--stills')){
  enc=spawn(FF,['-y','-hide_banner','-loglevel','warning','-f','image2pipe','-framerate','30','-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',path.join(cache,START?'tail.mp4':'picture.mp4')],{stdio:['pipe','inherit','inherit']});const finished=once(enc,'exit');
  await page.evaluate(()=>{window.__continuous=true;});const started=Date.now();
  for(let f=START;f<720;f++){const jpg=await page.evaluate(f=>{window.__seek(f);return document.querySelector('#final').toDataURL('image/jpeg',.95).split(',')[1];},f);if(!enc.stdin.write(Buffer.from(jpg,'base64')))await once(enc.stdin,'drain');if(f%60===0)console.log(`Continuity proof ${f}/720 frames; elapsed ${((Date.now()-started)/1000).toFixed(1)}s`);}
  enc.stdin.end();const [code]=await finished;if(code)throw Error(`Encoder failed ${code}`);console.log(`PICTURE COMPLETE: ${720-START} native frames`);
 }
}finally{if(browser)await browser.close();server.close();}
