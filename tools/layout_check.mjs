import { createCanvas, GlobalFonts } from '@napi-rs/canvas';
GlobalFonts.registerFromPath('showreel/v3/vendor/fonts/Anton-Regular.ttf','Anton');
GlobalFonts.registerFromPath('showreel/v3/vendor/fonts/Poppins-SemiBold.ttf','PSB');
const c = createCanvas(100,100), ctx = c.getContext('2d');
const W = (s,f,sz,sp=0)=>{ ctx.font = sz+'px '+f; if(sp) ctx.letterSpacing = sp+'px'; return Math.round(ctx.measureText(s).width); };
const PL=100, PR=1820, PT=130, PB=950, M=90, SAFE_R=PR-M;
console.log('plate safe x: 190 ..', SAFE_R);

console.log('\n== S1 hook: TWO lines, both must clear the bar column at 1180');
const lines = [
  { y: 'line1', words: [['EK','Anton',122,1],['VIDEO','Anton',196,-2]] },
  { y: 'line2', words: [['HAR','Anton',122,1],['VIEW','Anton',122,1],['KA','Anton',122,1]] },
];
for (const ln of lines) {
  let cursor = 190;
  for (const [s2,f,sz,sp] of ln.words) {
    const w = W(s2,f,sz,sp);
    console.log(`   ${ln.y}`, s2.padEnd(6), String(cursor).padStart(5), '→', String(cursor+w).padStart(5));
    cursor += w + 26;
  }
  console.log(`   ${ln.y} ends ${cursor-26} | bar starts 1180 →`, cursor-26 < 1160 ? 'CLEAR' : 'COLLIDES');
}

console.log('\n== S2 two-column');
console.log('   75% (Anton 240)', 170+W('75%','Anton',240,1), '| grid starts 830 →', 170+W('75%','Anton',240,1) < 820 ? 'CLEAR' : 'COLLIDES');
console.log('   BAANT (PSB 56)', 180+W('BAANT RAHE HAIN','PSB',56,4), '| grid starts 830 →', 180+W('BAANT RAHE HAIN','PSB',56,4) < 820 ? 'CLEAR' : 'COLLIDES');
console.log('   grid width', 8*74+7*13, '→ ends', 830+8*74+7*13, SAFE_R > 830+8*74+7*13 ? 'CLEAR' : 'OVERFLOW');

console.log('\n== S3 gap: left numeral vs right bars');
console.log('   36× (Anton 300)', 190+W('36×','Anton',300,1), '| base line starts 1140 →', 190+W('36×','Anton',300,1) < 1130 ? 'CLEAR':'COLLIDES');
console.log('   value labels width 260 at 1320 →', 1320+260, SAFE_R>1580?'CLEAR':'OVERFLOW');

console.log('\n== S4 topfive: rows 150..1570, verdict baseline');
const rowTop = 206, rowH = 108, rowGap = 124;
for (let i=0;i<5;i++) console.log(`   row ${i} top ${rowTop+i*rowGap} bottom ${rowTop+i*rowGap+rowH}`);
console.log('   verdict needs top', rowTop+5*rowGap-20, '| plate bottom', PB, rowTop+5*rowGap-20+70 < PB ? 'FITS':'OVERFLOWS');
console.log('   verdict text width', W('KOI NAHI BATATA: KAUN CHHOD GAYA','PSB',40,2), 'at 160 →', 160+W('KOI NAHI BATATA: KAUN CHHOD GAYA','PSB',40,2));

console.log('\n== S5 swap');
console.log('   SATURATED (Anton 170)', 190+W('SATURATED','Anton',170,2), '| hub 1540');
console.log('   CONCENTRATED (Anton 160)', 190+W('CONCENTRATED','Anton',160,1), '→', 190+W('CONCENTRATED','Anton',160,1) < 1430 ? 'CLEAR':'COLLIDES HUB');
console.log('   proof lines widest', Math.max(W('EK JEETNE WALA','PSB',39,3), W('UNTEES USKI COPY','PSB',39,3)), 'at 196');

console.log('\n== S6 comments: 20 cols × 60 = 1200 at 170 →', 170+20*60, SAFE_R>1370?'CLEAR':'OVERFLOW');
console.log('   label width', W('PAISE DENA CHAHTE HAIN','PSB',50,3), 'at 360 →', 360+W('PAISE DENA CHAHTE HAIN','PSB',50,3));

console.log('\n== S7 end: centred, widest', W('JO KOI FILM NAHI KARTA','Anton',80,2), 'centred at 960 → 560..1360, plate', PL,'-',PR);
