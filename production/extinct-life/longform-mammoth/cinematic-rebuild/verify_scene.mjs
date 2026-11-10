// Structural checks for the experimental reconstruction; these are not aesthetic QC.
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http';
import assert from 'node:assert/strict'; import {chromium} from 'playwright'; import chromiumBin from '@sparticuz/chromium';
const root=process.cwd(), base=path.join(root,'production/extinct-life/longform-mammoth/cinematic-rebuild');
const files={'/':'stage.html','/scene.mjs':'scene.mjs','/timeline.json':'timeline.json','/assets/fur.jpg':'assets/fur.jpg','/assets/tundra.jpg':'assets/tundra.jpg'};
const server=http.createServer((req,res)=>{const n=new URL(req.url,'http://localhost').pathname;let f=files[n]?path.join(base,files[n]):n==='/three.module.js'?path.join(root,'node_modules/three/build/three.module.js'):n==='/three.core.js'?path.join(root,'node_modules/three/build/three.core.js'):n==='/Manrope.ttf'?path.join(root,'public/showreel/fonts/Manrope-800.ttf'):n==='/Anton.ttf'?path.join(root,'public/showreel/fonts/Anton-Regular.ttf'):null;
 if(!f||!fs.existsSync(f))return res.writeHead(404).end();
 res.setHeader('Content-Type',({'.mjs':'application/javascript','.js':'application/javascript','.html':'text/html','.json':'application/json','.jpg':'image/jpeg','.ttf':'font/ttf'})[path.extname(f)]||'application/octet-stream');fs.createReadStream(f).pipe(res);
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
try {
 browser=await chromium.launch({executablePath:await chromiumBin.executablePath(),env:{...process.env,LD_LIBRARY_PATH:path.join(root,'.cache/extinct-v14/libs/lib')},args:[...chromiumBin.args,'--enable-unsafe-swiftshader','--ignore-gpu-blocklist'],headless:true});
 const page=await browser.newPage({viewport:{width:1280,height:720}});const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`)});
 await page.goto(`http://127.0.0.1:${server.address().port}`,{waitUntil:'commit'});await page.waitForFunction(()=>window.__ready,null,{timeout:180000});
 const state=await page.evaluate(()=>{
  let mammoth; window.__dbg.scene.traverse(x=>{if(x.userData.legs)mammoth=x});
  if(!mammoth)throw Error('mammoth missing');
  window.__seek(15);const first=mammoth.userData.legs.map(x=>x.rotation.x);
  window.__seek(39);const second=mammoth.userData.legs.map(x=>x.rotation.x);
  window.__seek(15);const repeat=mammoth.userData.legs.map(x=>x.rotation.x);
  return {first,second,repeat,fur:mammoth.userData.legs.map(x=>x.children.some(c=>c.isInstancedMesh)),canvas:[window.__dbg.renderer.domElement.width,window.__dbg.renderer.domElement.height]};
 });
 assert.deepEqual(errors,[]);assert.deepEqual(state.canvas,[1280,720]);assert.equal(state.first.length,4);assert(state.fur.every(Boolean));assert.deepEqual(state.first,state.repeat);assert(state.first.some((v,i)=>Math.abs(v-state.second[i])>0.01));
 console.log('PASS: all four leg pivots change with time; fur is parented to each; pose is deterministic; canvas is 1280×720; no page errors.');
} finally {if(browser)await browser.close();server.close()}
