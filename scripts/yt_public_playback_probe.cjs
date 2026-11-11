// Public unauthenticated browser playback feasibility probe. No screenshots, media
// downloads, cookies, account access or bot-check bypass are used or retained.
const {chromium}=require('playwright');const fs=require('fs');const http=require('http');
(async()=>{
 const server=http.createServer((req,res)=>{res.writeHead(200,{'Content-Type':'text/html','Referrer-Policy':'strict-origin-when-cross-origin'});res.end('<iframe width="640" height="360" src="https://www.youtube.com/embed/aWHX5Awe_TI" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>');});
 await new Promise(resolve=>server.listen(4173,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const ctx=await browser.newContext({viewport:{width:1280,height:800}});const rows=[];
 for(const [name,url] of [
 ['DusanFC Neymar watch','https://www.youtube.com/watch?v=aWHX5Awe_TI'],
 ['LV Animation watch','https://www.youtube.com/watch?v=8wtQAI_ZZlQ'],
 ['Stickman Snooze watch','https://www.youtube.com/watch?v=GHT3RyE9wGI'],
 ['DusanFC Neymar iframe in local page','http://127.0.0.1:4173/']]){
  const page=await ctx.newPage();page.setDefaultTimeout(10000);const row={name,url};
  try{
   const resp=await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});row.http=resp?.status()??null;
   // Basic optional public consent interface, if present; no authentication.
   for(const label of ['Accept all','Reject all']){const b=page.getByRole('button',{name:label,exact:true}).first();if(await b.isVisible().catch(()=>false)){await b.click().catch(()=>{});break;}}
   await page.waitForTimeout(4000);
   row.title=(await page.title()).slice(0,180);
   const target=url.startsWith('http://127.0.0.1:4173') ? await (await page.locator('iframe').elementHandle()).contentFrame() : page;
   await page.waitForTimeout(url.startsWith('http://127.0.0.1:4173')?3000:0);
   row.videoElements=await target.locator('video').count();
   const body=(await target.locator('body').innerText({timeout:8000}).catch(()=>''));
   row.visibleText=body.slice(0,500);
   if(row.videoElements){
    row.initial=await target.locator('video').first().evaluate(v=>({time:v.currentTime,readyState:v.readyState,paused:v.paused,width:v.videoWidth,height:v.videoHeight,error:v.error?.code||null}));
    row.playResult=await target.locator('video').first().evaluate(v=>{v.muted=true;v.play().catch(()=>{});return 'requested'});
    await page.waitForTimeout(3500);
    row.after=await target.locator('video').first().evaluate(v=>({time:v.currentTime,readyState:v.readyState,paused:v.paused,width:v.videoWidth,height:v.videoHeight,error:v.error?.code||null}));
    row.playbackVerified=row.after.time>row.initial.time+.3 && row.after.width>0 && row.after.height>0;
   }else row.playbackVerified=false;
  }catch(e){row.error=String(e.message).slice(0,220);row.playbackVerified=false;}
  console.log(name,JSON.stringify({http:row.http,videoElements:row.videoElements,playbackVerified:row.playbackVerified,error:row.error}));rows.push(row);await page.close();
 }
 await browser.close();server.close();fs.mkdirSync('audit-output',{recursive:true});fs.writeFileSync('audit-output/yt-browser-probe.json',JSON.stringify({method:'Fresh GitHub runner, headless Playwright Chromium, public watch/embed links, unauthenticated, no stored media. Playback confirmed only if video time advances with nonzero decoded dimensions; this is not a guarantee for user browser.',rows},null,2));
})().catch(e=>{console.error(e.message);process.exitCode=1});
