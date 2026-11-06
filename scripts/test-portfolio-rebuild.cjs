/* Optional browser integration test. Requires puppeteer-core and a Chromium binary.
   CHROME_PATH=/path/to/chromium PUPPETEER_CORE_PATH=/path/to/puppeteer-core node scripts/test-portfolio-rebuild.cjs
   The test uses an existing preview server (PORTFOLIO_URL) or starts one locally. */
'use strict';
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const net = require('node:net');
const path = require('node:path');
const puppeteer = require(process.env.PUPPETEER_CORE_PATH || 'puppeteer-core');
const root = path.resolve(__dirname, '..');
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function freePort() {
  return new Promise((resolve, reject) => {
    const s=net.createServer(); s.on('error',reject); s.listen(0,'127.0.0.1',() => { const port=s.address().port; s.close(()=>resolve(port)); });
  });
}
async function waitForServer(url) {
  for (let n=0;n<50;n++) { try { const r=await fetch(url); if (r.ok) return; } catch (_) {} await sleep(100); }
  throw Error('Portfolio preview did not start');
}
(async () => {
  const chromium=process.env.CHROME_PATH;
  if (!chromium) throw Error('Set CHROME_PATH to your Chromium executable');
  let server, browser;
  try {
    let url=process.env.PORTFOLIO_URL;
    if (!url) {
      const port=await freePort(); url=`http://127.0.0.1:${port}/portfolio/`;
      server=spawn('python3',['scripts/preview-portfolio.py',String(port)],{cwd:root,stdio:'ignore'});
      await waitForServer(url);
    }
    browser=await puppeteer.launch({headless:true,executablePath:chromium,args:['--no-sandbox']});
    for (const [name,width,height] of [['desktop',1440,900],['mobile',390,844]]) {
      const page=await browser.newPage(), errors=[];
      page.on('pageerror', e=>errors.push(e.message));
      await page.setViewport({width,height});
      await page.evaluateOnNewDocument(() => { sessionStorage.setItem('ac_intro_seen','1'); });
      await page.goto(url,{waitUntil:'domcontentloaded'});
      await page.waitForSelector('.build-hud');
      await page.evaluate(() => {
        const completed=new WeakSet();
        window.__syncAudit={samples:0,leaks:[],misalignments:[],uncovered:[],sections:new Set(),revealSamples:0};
        window.addEventListener('monarch:rebuild-reveal',e=>{completed.add(e.detail.element);e.detail.element.querySelectorAll('[data-rv]').forEach(x=>completed.add(x));});
        window.__syncAuditTimer=setInterval(()=>{
          if (!document.body.classList.contains('monarch-build-active')) return;
          const a=window.__syncAudit; a.samples++;
          document.querySelectorAll('[data-build-phase]').forEach(el=>{
            const phase=el.dataset.buildPhase, style=getComputedStyle(el);
            if (['waiting','approach','draw'].includes(phase) && style.visibility!=='hidden' && a.leaks.length<10) a.leaks.push([phase,el.className]);
            if (phase==='reveal') {
              a.revealSamples++;
              const amount=parseFloat(el.style.getPropertyValue('--build-reveal'));
              const mask=style.clipPath.match(/^inset\(0px ([\d.]+)%/);
              const actor=document.querySelector('.build-cursor[data-actor="'+el.dataset.buildActor+'"]');
              if (style.visibility!=='visible' || !Number.isFinite(amount) || style.clipPath==='none' || (amount>1 && amount<99 && (!mask || Math.abs(Number(mask[1])+amount-100)>.2))) a.leaks.push(['reveal mask',el.className,style.clipPath]);
              if (actor && amount>1 && amount<99) { const b=el.getBoundingClientRect(), p=actor.getBoundingClientRect(); if (Math.abs(p.left-(b.left+b.width*amount/100))>4 && a.misalignments.length<10) a.misalignments.push(['reveal cursor',el.className]); }
            }
            if (phase==='draw') {
              const actor=document.querySelector('.build-cursor[data-actor="'+el.dataset.buildActor+'"]');
              const box=document.querySelector('.build-box[data-actor="'+el.dataset.buildActor+'"]');
              if (actor && box) { const p=actor.getBoundingClientRect(), r=box.getBoundingClientRect(); const distance=Math.hypot(p.left-r.right,p.top-r.bottom); if (distance>4 && a.misalignments.length<10) a.misalignments.push(distance); }
            }
          });
          document.querySelectorAll('main [data-rv]').forEach(el=>{
            const b=el.getBoundingClientRect();
            if (b.width && b.height && b.right>0 && b.left<innerWidth && b.top<innerHeight && b.bottom>0 && !el.closest('[data-build-phase]') && !completed.has(el) && a.uncovered.length<10) a.uncovered.push(el.className);
          });
          ['about','skills','work','proof','contact'].forEach(id=>{const b=document.getElementById(id).getBoundingClientRect();if(b.top<innerHeight*.65 && b.bottom>innerHeight*.3)a.sections.add(id);});
        },80);
      });
      await page.click('.build-speed'); await page.click('.build-speed');
      await page.waitForFunction(()=>document.querySelector('.build-label')?.textContent==='REBUILD COMPLETE',{timeout:90000});
      const result=await page.evaluate(()=>{clearInterval(window.__syncAuditTimer);const a=window.__syncAudit;return {samples:a.samples,leaks:a.leaks,misalignments:a.misalignments,uncovered:a.uncovered,revealSamples:a.revealSamples,sections:[...a.sections],pending:document.querySelectorAll('[data-build-phase]').length};});
      assert.ok(result.samples>20 && result.revealSamples>0, `${name}: audit did not observe the tour`);
      assert.deepEqual(result.leaks,[],`${name}: elements appeared before their cursor`);
      assert.deepEqual(result.misalignments,[],`${name}: cursor did not track its box`);
      assert.deepEqual(result.uncovered,[],`${name}: native reveal escaped the tour`);
      assert.equal(result.pending,0,`${name}: unfinished targets at completion`);
      assert.deepEqual(result.sections,['about','skills','work','proof','contact'],`${name}: tour missed a section`);
      await page.click('.build-skip');
      const cleanup=await page.evaluate(()=>({y:scrollY,hidden:document.querySelectorAll('.build-wait,.build-drawing,[data-build-phase]').length,cards:document.querySelectorAll('.work-card').length}));
      assert.deepEqual(cleanup,{y:0,hidden:0,cards:10}); assert.deepEqual(errors,[]);
      console.log(`✓ ${name}: ${result.samples} samples, synchronized reveals and complete cleanup`);
      await page.close();
    }
  } finally { if (browser) await browser.close(); if (server) server.kill(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
