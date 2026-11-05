// Own deterministic harness adapted from the repo's showreel capture pattern.
import fs from 'node:fs';import path from 'node:path';import http from 'node:http';import zlib from 'node:zlib';import {spawn,execFileSync} from 'node:child_process';import {once} from 'node:events';import {chromium} from 'playwright';import serverChromium from '@sparticuz/chromium';
const root=process.cwd(),cache=path.join(root,'.cache/extinct-opening-25d');fs.mkdirSync(cache,{recursive:true});
const FF=execFileSync(path.join(root,'.venv/bin/python'),['-c','import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'],{encoding:'utf8'}).trim();
const files={'/':path.join(root,'production/extinct-life/opening-25d/stage.html'),'/atlas-serif.ttf':'/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf','/three.module.js':path.join(root,'node_modules/three/build/three.module.js'),'/three.core.js':path.join(root,'node_modules/three/build/three.core.js'),'/greenland.json':path.join(root,'production/extinct-life/opening-25d/greenland.json')};
const server=http.createServer((req,res)=>{const file=files[req.url];if(!file){res.writeHead(404).end();return;}res.setHeader('Content-Type',req.url==='/'?'text/html':req.url.endsWith('.ttf')?'font/ttf':'application/javascript');res.end(fs.readFileSync(file));});
await new Promise(r=>server.listen(0,'0.0.0.0',r));
let browser,enc;
// Lambda Chromium bundles NSS/NSPR; unpack locally when the Linux image lacks them.
const libs=path.join(cache,'libs');fs.mkdirSync(libs,{recursive:true});
if(!fs.existsSync(path.join(libs,'lib/libnspr4.so'))){const tar=path.join(cache,'chrome-libs.tar');fs.writeFileSync(tar,zlib.brotliDecompressSync(fs.readFileSync(path.join(root,'node_modules/@sparticuz/chromium/bin/al2023.tar.br'))));execFileSync('tar',['-xf',tar,'-C',libs]);fs.unlinkSync(tar);}
try{
 browser=await chromium.launch({env:{...process.env,LD_LIBRARY_PATH:path.join(libs,'lib')+':'+(process.env.LD_LIBRARY_PATH||'')},executablePath:await serverChromium.executablePath(),args:[...serverChromium.args,'--enable-unsafe-swiftshader','--ignore-gpu-blocklist'],headless:true});
 const context=await browser.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1});const page=await context.newPage();page.on('pageerror',e=>console.error(e));
 await page.goto(`http://127.0.0.1:${server.address().port}/`);await page.waitForFunction(()=>window.__ready,{timeout:30000});
 for(const t of [1,4.5,8.5,14.5,21,25,29,33,38,42]){const jpg=await page.evaluate(f=>{window.__seek(f);return document.querySelector('canvas').toDataURL('image/jpeg',.94).split(',')[1];},Math.round(t*30));fs.writeFileSync(path.join(cache,`still_${t}.jpg`),Buffer.from(jpg,'base64'));}
 if(!process.argv.includes('--stills')){
 async function renderPart(worker,start,end){
  const p=await context.newPage();
  await p.goto(`http://127.0.0.1:${server.address().port}/`);await p.waitForFunction(()=>window.__ready);
  const proc=spawn(FF,['-y','-v','warning','-f','image2pipe','-framerate','30','-vcodec','mjpeg','-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p',path.join(cache,`part_${worker}.mp4`)],{stdio:['pipe','inherit','inherit']});
  const finished=once(proc,'exit');
  for(let f=start;f<end;f++){const jpg=await p.evaluate(f=>{window.__seek(f);return document.querySelector('canvas').toDataURL('image/jpeg',.94).split(',')[1];},f);const b=Buffer.from(jpg,'base64');if(!proc.stdin.write(b))await once(proc.stdin,'drain');if((f-start)%90===0)console.log(`Worker ${worker}: ${f-start}/${end-start} frames`);}
  proc.stdin.end();const [code]=await finished;if(code)throw Error(`Encoder failed ${code}`);await p.close();
 }
 await Promise.all([renderPart(0,0,675),renderPart(1,675,1350)]);
 fs.writeFileSync(path.join(cache,'concat.txt'),"file 'part_0.mp4'\nfile 'part_1.mp4'\n");
 execFileSync(FF,['-y','-v','warning','-f','concat','-safe','0','-i',path.join(cache,'concat.txt'),'-c','copy',path.join(cache,'picture.mp4')]);
 console.log('PICTURE COMPLETE: 1350 frames / 45 seconds');
 }

}finally{if(browser)await browser.close();server.close();}
