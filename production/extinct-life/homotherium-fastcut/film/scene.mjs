// Pure 2D editorial compositor. No Three.js, WebGL, models or 3D globe.
await document.fonts.load('800 48px Manrope');await document.fonts.load('80px Anton');
const S=await(await fetch('/timeline.json')).json(),land=await(await fetch('/land.geojson')).json(),W=1080,H=1920,ctx=document.querySelector('#final').getContext('2d',{alpha:false});
const imgs={};await Promise.all(['cub','lion','skull','dorsal','paw','lion-paw'].map(async n=>{const i=new Image();i.src='/assets/'+n+'.png';await i.decode();imgs[n]=i}));
const clamp=x=>Math.max(0,Math.min(1,x)),ease=x=>1-(1-clamp(x))**3;
function text(s,x,y,size=52,color='#f4eddc',font='Manrope',align='center'){ctx.font=`${font==='Anton'?400:800} ${size}px ${font}`;ctx.fillStyle=color;ctx.textAlign=align;ctx.fillText(s,x,y)}
function line(x,y,X,Y,c='#dab886',w=3){ctx.strokeStyle=c;ctx.lineWidth=w;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(X,Y);ctx.stroke()}
function bg(){const g=ctx.createLinearGradient(0,0,W,H);g.addColorStop(0,'#14272f');g.addColorStop(.5,'#081922');g.addColorStop(1,'#030c14');ctx.fillStyle=g;ctx.fillRect(0,0,W,H)}
function photo(n,x,y,w,angle=0){const i=imgs[n];ctx.save();ctx.translate(x,y);ctx.rotate(angle);ctx.drawImage(i,-w/2,-w/i.width*i.height/2,w,w/i.width*i.height);ctx.restore()}
function crop(n,sx,sy,sw,sh,x,y,w,h){const i=imgs[n];ctx.drawImage(i,sx,sy,sw,sh,x,y,w,h)}
function small(s,y=1225){text(s,540,y,26,'#aac3c8')}
function ring(x,y,r){ctx.strokeStyle='#e8c38d';ctx.lineWidth=4;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.stroke()}
function map(pin,u){const lon0=pin?118:65,lon1=pin?174:180,lat0=pin?48:5,lat1=pin?79:85;const project=([lon,lat])=>[75+(lon-lon0)/(lon1-lon0)*930,1125-(lat-lat0)/(lat1-lat0)*780];ctx.save();ctx.beginPath();ctx.rect(75,345,930,820);ctx.clip();ctx.fillStyle='#163844';ctx.fillRect(75,345,930,820);for(let lat=0;lat<=90;lat+=10){const p=project([lon0,lat]);line(75,p[1],1005,p[1],'#33545d',1)}for(let lon=50;lon<190;lon+=10){const p=project([lon,lat0]);line(p[0],345,p[0],1165,'#33545d',1)}ctx.fillStyle='#7e8e79';for(const f of land.features){const ps=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates;for(const p of ps){ctx.beginPath();for(const r of p){r.forEach((v,i)=>{const [x,y]=project(v);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.closePath()}ctx.fill('evenodd')}}const [x,y]=project([146.7703,67.6872]);ctx.fillStyle='#ffe0a3';ctx.beginPath();ctx.arc(x,y,10,0,7);ctx.fill();ring(x,y,19+6*u);ctx.restore();text('SIBERIA',540,260,78,'#ead0a3','Anton');small(pin?'BADYARIKHA RIVER':'NORTHEAST YAKUTIA',1230)}
function feature(n,sx,sy,sw,sh,u){crop(n,sx,sy,sw,sh,60-7*u,320-7*u,960+14*u,890+14*u)}
function seek(frame){const st=performance.now(),t=Math.max(0,Math.min(S.duration-.0001,frame/30)),shot=S.scenes.find(s=>t>=s.start&&t<s.end),u=(t-shot.start)/(shot.end-shot.start),z=1+.025*ease(u),k=shot.kind;bg();
 if(k==='fur'){feature('cub',170,95,600,560,u);small('REAL PRESERVED FUR',1255)}
 if(k==='head'){photo('cub',540,800,1010*z);}
 if(k==='head-tight'){photo('cub',550,800,1210*z);}
 if(k==='age-old'){photo('cub',540,700,940*z);text('35,000+',540,1170,152,'#efd09e','Anton');small('YEARS OLD',1230)}
 if(k==='map-wide'||k==='map-pin')map(k==='map-pin',u);
 if(k==='not-alive'){photo('cub',540,760,1010*z);text('PRESERVED. NOT ALIVE.',540,1220,66,'#ead0a3','Anton')}
 if(k==='skull'){photo('skull',540,800,985*z);small('Published CT-based model',1240)}
 if(k==='teeth'){feature('skull',0,180,490,330,u);small('SKULL + TOOTH DEVELOPMENT',1250)}
 if(k==='skull-top'){photo('dorsal',540,780,890*z);small('Published CT-based model',1250)}
 if(k==='identity'){photo('cub',540,720,920*z);text('HOMOTHERIUM',540,1190,99,'#ecd0a6','Anton');}
 if(k==='age-young'){text('~3',540,775,360,'#e8c491','Anton');text('WEEKS OLD',540,930,96,'#ede9de','Anton');small('Estimated from tooth development',1140)}
 if(k==='compare'||k==='compare-ear'){photo('cub',540,565,650*z);photo('lion',540,1090,650*z);text('HOMOTHERIUM',540,320,36,'#efd0a1');text('LION',540,1405,36,'#bdd3d4');small('Comparison images · different display scales',1460);if(k==='compare-ear'){ring(524,505,43);ring(440,1063,50)}}
 if(k==='ear'){feature('cub',190,120,460,470,u);small('SMALLER EARS',1250)}
 if(k==='neck'){feature('cub',20,220,560,540,u);small('ROBUST NECK',1250)}
 if(k==='paw'){photo('paw',550,780,860*z);small('HOMOTHERIUM FRONT PAW',1250)}
 if(k==='paw-pair'){photo('paw',540,610,535*z);photo('lion-paw',540,1110,570*z);text('HOMOTHERIUM',540,315,33,'#e7c490');text('LION',540,1390,33,'#b9d0d2');small('Comparison images · different display scales',1450)}
 if(k==='partial'){photo('cub',700,800,1120*z);const g=ctx.createLinearGradient(0,0,450,0);g.addColorStop(0,'#081922');g.addColorStop(1,'#08192200');ctx.fillStyle=g;ctx.fillRect(0,300,450,1000);text('INCOMPLETE',540,1230,96,'#e9c48e','Anton')}
 if(k==='uncertain'){photo('dorsal',540,730,780*z);text('RECONSTRUCTION',540,1190,79,'#e4c08e','Anton');small('Full living appearance remains uncertain',1250)}
 // Local scientific qualifiers, no persistent branding/counters/lecture-like headings.
 if(['skull','teeth','skull-top'].includes(k))small('Original published model partly mirrored',1300);
 const grad=ctx.createLinearGradient(0,1390,0,H);grad.addColorStop(0,'#030d1500');grad.addColorStop(.45,'#030d15e8');grad.addColorStop(1,'#030d15');ctx.fillStyle=grad;ctx.fillRect(0,1390,W,H-1390);
 const c=S.captions.find(c=>t>=c.start&&t<c.end);let captionBounds=null;if(c){let size=62;do{ctx.font=`800 ${size}px Manrope`;if(ctx.measureText(c.text).width<=900)break;size--}while(size>40);ctx.textAlign='center';ctx.lineJoin='round';ctx.lineWidth=9;ctx.strokeStyle='#020a13';ctx.strokeText(c.text,540,1570);ctx.fillStyle='#fff2dc';ctx.fillText(c.text,540,1570);captionBounds={left:540-ctx.measureText(c.text).width/2,right:540+ctx.measureText(c.text).width/2,size}}
 if(t>=43.8){text('Images: Lopatin et al. · Scientific Reports (2024)',540,1690,21,'#a7bcc2');text('Figs 2, 4, 7 · CC BY 4.0 · cropped / composited',540,1725,20,'#8ca7b0')}
 window.__state={frame,time:t,scene:shot.id,kind:k,no_3d:true,caption_bounds:captionBounds,timings:{composite:performance.now()-st}};
}
window.__seek=seek;window.__ready=true;seek(0);const audio=document.querySelector('#audio');let playing=false;document.querySelector('#play').onclick=async()=>{playing=!playing;if(playing){if(audio.ended)audio.currentTime=0;await audio.play();tick()}else audio.pause()};function tick(){if(!playing)return;seek(audio.currentTime*30);if(audio.ended){playing=false;return}requestAnimationFrame(tick)}
