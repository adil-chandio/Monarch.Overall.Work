// Own deterministic harness adapted from the repo's showreel capture pattern.
import fs from 'node:fs';import path from 'node:path';import http from 'node:http';import zlib from 'node:zlib';import {spawn,execFileSync} from 'node:child_process';import {once} from 'node:events';import {chromium} from 'playwright';import serverChromium from '@sparticuz/chromium';
const root=process.cwd(),cache=path.join(root,'.cache/extinct-motion-lab');fs.mkdirSync(cache,{recursive:true});
const FF=execFileSync(path.join(root,'.venv/bin/python'),['-c','import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'],{encoding:'utf8'}).trim();
const files={'/':path.join(root,'production/extinct-life/motion-lab/stage.html'),'/three.module.js':path.join(root,'node_modules/three/build/three.module.js'),'/three.core.js':path.join(root,'node_modules/three/build/three.core.js')};
const server=http.createServer((req,res)=>{const file=files[req.url];if(!file){res.writeHead(404).end();return;}res.setHeader('Content-Type',req.url==='/'?'text/html':'application/javascript');res.end(fs.readFileSync(file));});
await new Promise(r=>server.listen(0,'0.0.0.0',r));
let browser,enc;
// Lambda Chromium bundles NSS/NSPR; unpack locally when the Linux image lacks them.
const libs=path.join(cache,'libs');fs.mkdirSync(libs,{recursive:true});
if(!fs.existsSync(path.join(libs,'lib/libnspr4.so'))){const tar=path.join(cache,'chrome-libs.tar');fs.writeFileSync(tar,zlib.brotliDecompressSync(fs.readFileSync(path.join(root,'node_modules/@sparticuz/chromium/bin/al2023.tar.br'))));execFileSync('tar',['-xf',tar,'-C',libs]);fs.unlinkSync(tar);}
try{
 browser=await chromium.launch({env:{...process.env,LD_LIBRARY_PATH:path.join(libs,'lib')+':'+(process.env.LD_LIBRARY_PATH||'')},executablePath:await serverChromium.executablePath(),args:[...serverChromium.args,'--enable-unsafe-swiftshader','--ignore-gpu-blocklist'],headless:true});
 const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});page.on('pageerror',e=>console.error(e));
 await page.goto(`http://127.0.0.1:${server.address().port}/`);await page.waitForFunction(()=>window.__ready,{timeout:30000});
 for(const t of [0,3,5.5,8.5,11,14,17]){await page.evaluate(f=>window.__seek(f),Math.round(t*60));await page.screenshot({path:path.join(cache,`still_${t}.jpg`),type:'jpeg',quality:94});}
 if(!process.argv.includes('--stills')){
 enc=spawn(FF,['-y','-v','warning','-f','image2pipe','-framerate','60','-vcodec','mjpeg','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-threads','4','-pix_fmt','yuv420p','-movflags','+faststart',path.join(cache,'picture.mp4')],{stdio:['pipe','inherit','inherit']});
 const finished=once(enc,'exit');
 for(let f=0;f<1080;f++){await page.evaluate(f=>window.__seek(f),f);const b=await page.screenshot({type:'jpeg',quality:94});if(!enc.stdin.write(b))await once(enc.stdin,'drain');if(f%120===0)console.log(`Motion test ${f}/1080 frames`);}
 enc.stdin.end();const [code]=await finished;if(code)throw Error(`Encoder failed ${code}`);console.log('PICTURE COMPLETE');
 }
}finally{if(browser)await browser.close();server.close();}
