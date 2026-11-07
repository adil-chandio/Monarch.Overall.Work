// Ordinary public browser playback; no authentication, stealth, cookies or access-wall bypass.
import {chromium} from 'playwright';
import fs from 'node:fs';import path from 'node:path';
const out='docs/research/stickman-study/browser-playback';fs.mkdirSync(out,{recursive:true});
const ids=['viv47VJHF-w','YoLqQ8yCXSc','OGEL9n3GWc4','8uTxLjeFcEE','TkMULj3bUuw','9JVF4egvr7I','1t8_eOuKd0Q','tzt_MzfFmEg','TPLXdDn9Kdg','o5koCe2SR6U','L2cHAQ5CVbQ','I8bSN1TX8Sc'];
const browser=await chromium.launch({headless:true});const results=[];
try{for(const id of ids){const page=await browser.newPage({viewport:{width:1280,height:900}});const row={id,url:'https://www.youtube.com/watch?v='+id,public_browser_access:false,actual_frame_quotes:[],human_review_completed:false};
try{await page.goto(row.url,{waitUntil:'domcontentloaded',timeout:35000});
 const reject=page.getByRole('button',{name:/Reject all/i});if(await reject.count())await reject.first().click({timeout:5000}).catch(()=>{});
 await page.waitForFunction(()=>{const v=document.querySelector('video'),p=document.getElementById('movie_player');return v&&v.readyState>=2&&v.videoWidth>0&&p?.getVideoData?.()?.video_id;},null,{timeout:22000});
 const state=await page.evaluate(()=>{const p=document.getElementById('movie_player'),v=document.querySelector('video');return {id:p.getVideoData().video_id,title:p.getVideoData().title,duration:v.duration,width:v.videoWidth,height:v.videoHeight,ad:!!document.querySelector('.ad-showing')};});
 if(state.id!==id||state.ad||!Number.isFinite(state.duration))throw Error('Cannot establish requested actual video, not an ad');row.public_browser_access=true;row.player=state;const folder=path.join(out,id);fs.mkdirSync(folder,{recursive:true});
 for(let k=0;k<12;k++){const t=Math.min(state.duration-.2,(k+.5)*Math.min(state.duration,180)/12);await page.evaluate(t=>{const v=document.querySelector('video');v.pause();v.currentTime=t;},t);await page.waitForFunction(t=>{const v=document.querySelector('video');return !v.seeking&&v.readyState>=2&&Math.abs(v.currentTime-t)<.5;},t,{timeout:15000});
 const f=path.join(folder,String(k).padStart(2,'0')+'.jpg');await page.locator('video').first().screenshot({path:f,type:'jpeg',quality:67});row.actual_frame_quotes.push({requested_seconds:t,path:f,exact_frame_timestamp_not_claimed:true});}
}catch(e){row.error=String(e);row.visible_public_page_message=await page.locator('body').innerText({timeout:3000}).catch(()=>'');row.visible_public_page_message=row.visible_public_page_message.slice(0,2200);}
finally{results.push(row);fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({results,study_complete:false},null,2));console.log(id,row.public_browser_access,row.error??'');await page.close();}}
}finally{await browser.close();}
