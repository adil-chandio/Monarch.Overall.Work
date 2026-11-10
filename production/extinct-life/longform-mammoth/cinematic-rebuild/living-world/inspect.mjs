// Screenshot and deterministic seek checks for experimental rig; no film render.
import fs from 'node:fs';import path from 'node:path';import http from 'node:http';import assert from 'node:assert/strict';import {chromium} from 'playwright';import chromiumBin from '@sparticuz/chromium';
const root=process.cwd(),base=path.join(root,'production/extinct-life/longform-mammoth/cinematic-rebuild/living-world'),cache=path.join(root,'.cache/living-world-review');fs.mkdirSync(cache,{recursive:true});
const files={'/':'stage.html','/scene.mjs':'scene.mjs','/tundra.jpg':path.join(root,'production/extinct-life/longform-mammoth/cinematic-rebuild/assets/tundra.jpg'),'/mammoth.glb':path.join(root,'production/extinct-life/longform-mammoth/cinematic-rebuild/mammoth-rig/assets/SDPM-Mammoth-Experimental-Rig.glb'),'/three.module.js':path.join(root,'node_modules/three/build/three.module.js'),'/three.core.js':path.join(root,'node_modules/three/build/three.core.js'),'/GLTFLoader.js':path.join(root,'node_modules/three/examples/jsm/loaders/GLTFLoader.js'),'/utils/BufferGeometryUtils.js':path.join(root,'node_modules/three/examples/jsm/utils/BufferGeometryUtils.js'),'/utils/SkeletonUtils.js':path.join(root,'node_modules/three/examples/jsm/utils/SkeletonUtils.js'),'/Manrope.ttf':path.join(root,'public/showreel/fonts/Manrope-800.ttf')};
const server=http.createServer((req,res)=>{const n=new URL(req.url,'http://localhost').pathname;let f=files[n];if(!f)return res.writeHead(404).end();if(!path.isAbsolute(f))f=path.join(base,f);res.setHeader('Content-Type',({'.mjs':'application/javascript','.js':'application/javascript','.html':'text/html','.ttf':'font/ttf','.obj':'text/plain'})[path.extname(f)]||'application/octet-stream');fs.createReadStream(f).pipe(res)});await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
try{
 browser=await chromium.launch({executablePath:await chromiumBin.executablePath(),env:{...process.env,LD_LIBRARY_PATH:path.join(root,'.cache/extinct-v14/libs/lib')},args:[...chromiumBin.args,'--enable-unsafe-swiftshader','--ignore-gpu-blocklist'],headless:true});const page=await browser.newPage({viewport:{width:1280,height:720}});const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`)});await page.goto(`http://127.0.0.1:${server.address().port}`,{waitUntil:'commit'});await page.waitForFunction(()=>window.__ready,null,{timeout:30000});
 const capture=async(t)=>page.evaluate(t=>{let state=window.__seek(t);return {state,jpeg:document.querySelector('#final').toDataURL('image/jpeg',.94).split(',')[1]}},t);
 const samples=[];for(let t of [0,2,4.9,5.35,8,14,19,19.35,23,29]){let v=await capture(t);fs.writeFileSync(path.join(cache,`still-${String(t).replace('.','_')}.jpg`),Buffer.from(v.jpeg,'base64'));samples.push(v.state);}
 let a=await capture(3),b=await capture(9),c=await capture(3);assert.equal(a.jpeg,c.jpeg);assert.notEqual(a.jpeg,b.jpeg);assert.equal(a.state.animals,3);assert.equal(a.state.triangles,56994);assert.deepEqual(errors,[]);
 const probes=await page.evaluate(()=>[0,.3,.6,.9,1.2,1.5,1.8,2.1,2.4].map(t=>({t,feet:window.__gaitProbe(t)})));
 assert.ok(probes.every(p=>p.feet.every(f=>f.count>20)));assert.ok(Math.abs(a.state.clip_duration-2.4)<1e-4);
 // On flat ground compare deformed soles in stance, not just bone targets.
 const phase=[.25,.75,0,.5],period=2.4,stance=.75;
 for(let n=0;n<probes.length;n++)for(let i=0;i<4;i++){
   const p=probes[n],q=(p.t/period+phase[i])%1;
   if(q<stance-1e-5){assert.ok(Math.abs(p.feet[i].minY-(-.055))<.006,`foot ${i} height at ${p.t}`);
    if(n){const prev=probes[n-1],q0=(prev.t/period+phase[i])%1;if(q0<stance-1e-5&&Math.floor(prev.t/period+phase[i])===Math.floor(p.t/period+phase[i]))assert.ok(Math.abs(p.feet[i].xyz[0]-prev.feet[i].xyz[0])<.004,`foot ${i} slipped`)}
   }
 }
 console.log(JSON.stringify({samples,probes,page_errors:errors,note:'Structural only; not scientific/anatomical validation or a finished film'},null,2));
}finally{if(browser)await browser.close();server.close();}
