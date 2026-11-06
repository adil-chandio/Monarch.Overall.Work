/* MONARCH rebuild: original implementation inspired by the reference's visual idea.
   No source code or assets from the referenced Swarm engine are used. */
(() => {
  'use strict';
  const SEEN = 'monarch_rebuild_seen_v1';
  const palette = ['#6cbce6','#df7585','#b18ce7','#78c8aa','#e0a96c','#899fe8','#e887b8','#8ccdd2'];
  const names = ['NOVA','ECHO','ATLAS','PIXEL','ORBIT','FLUX','EMBER','NORTH','SORA','VEX','LUMA','NIM','MICA','DUNE','INK','KITE','BOLT','LYRA','VALE','RIO','FINN','REMI','SAGE','SOL'];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let run = null, autoScheduled = false;
  const seen = () => { try { return sessionStorage.getItem(SEEN) === '1'; } catch (_) { return true; } };
  const markSeen = () => { try { sessionStorage.setItem(SEEN, '1'); } catch (_) {} };
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const ease = v => v*v*(3-2*v);
  const $ = s => document.querySelector(s);
  const make = (tag, cls) => { const el = document.createElement(tag); if (cls) el.className = cls; return el; };
  function cleanup(completed, returnToTop = false) {
    if (!run) return;
    const r = run; run = null;
    cancelAnimationFrame(r.raf);
    r.controller.abort();
    r.targets.forEach(t => t.el.classList.remove('build-wait'));
    document.body.classList.remove('monarch-build-active');
    document.querySelectorAll('[data-rv]').forEach(el => el.classList.add('in'));
    r.overlay.remove(); r.hud.remove();
    if (returnToTop) window.scrollTo({ top:0, behavior:'instant' });
    document.documentElement.style.scrollBehavior = r.scrollBehavior;
    if (completed) markSeen();
    window.dispatchEvent(new CustomEvent('monarch:rebuild-end', { detail: { completed } }));
  }
  function collectTargets() {
    const selector = 'main .hero-wm, main .hero-car, main .hero-eye, main .hero-lede-fly, main .stage-tags, main h2, main h3, main p, main .work-card, main .sk, main .timeline li, main blockquote, main .letter-card, main .proof-card, main .soc-tile, main .contact-grid, footer';
    const all = Array.from(document.querySelectorAll(selector));
    const chosen = new Set(all);
    return all.filter(el => {
      if (el.closest('.curtain, #player, #letterModal, #rcModal')) return false;
      let p = el.parentElement;
      while (p && p !== document.body) { if (chosen.has(p)) return false; p = p.parentElement; }
      const rect = el.getBoundingClientRect();
      return rect.width > 2 && rect.height > 2 && getComputedStyle(el).display !== 'none';
    }).map(el => ({ el, state:'waiting' }));
  }
  function start(manual = false) {
    if (run || document.body.classList.contains('locked')) return;
    if (reduced.matches) { if (manual) $('#toast')?.classList.add('show'); return; }
    if (!manual && (seen() || location.hash)) return;
    markSeen();
    const controller = new AbortController();
    const signal = controller.signal;
    const scrollBehavior = document.documentElement.style.scrollBehavior;
    document.documentElement.style.scrollBehavior = 'auto';
    window.scrollTo(0, 0);
    const targets = collectTargets();
    if (!targets.length) { document.documentElement.style.scrollBehavior = scrollBehavior; return; }
    const overlay = make('div','build-overlay'); overlay.setAttribute('aria-hidden','true');
    const guide = make('div','build-guide'); overlay.append(guide);
    const hud = make('div','build-hud');
    hud.setAttribute('role','region'); hud.setAttribute('aria-label','Visual rebuild controls');
    hud.innerHTML = '<span class="build-dots" aria-hidden="true"></span><span class="build-label">VISUAL REBUILD</span><span class="build-progress" aria-hidden="true"><i></i></span><button type="button" class="build-pause" aria-label="Pause visual rebuild">PAUSE</button><button type="button" class="build-speed" aria-label="Change rebuild speed">1×</button><button type="button" class="build-skip">SKIP</button>';
    palette.slice(0,6).forEach(c => { const d=make('i'); d.style.setProperty('--dot',c); hud.querySelector('.build-dots').append(d); });
    const actors = names.slice(0, innerWidth < 650 ? 12 : 24).map((name, i) => {
      const node = make('div','build-cursor'); const color = palette[i % palette.length]; node.style.setProperty('--agent',color);
      node.innerHTML = '<svg viewBox="0 0 20 24" aria-hidden="true"><path d="M2 1.5 17 14l-6 .4-2.8 6.7z" fill="'+color+'" stroke="white" stroke-width="1.3" stroke-linejoin="round"/></svg><span>'+name+'</span>';
      overlay.append(node);
      return { node, name, color, x:innerWidth/2, y:innerHeight/2, target:null, seed:i*2.4 };
    });
    document.body.append(overlay, hud);
    document.body.classList.add('monarch-build-active');
    targets.forEach(t => t.el.classList.add('build-wait'));
    const maxScroll = Math.max(0, document.documentElement.scrollHeight-innerHeight);
    // A long page gets a little more time, while the reference's ~one-minute rhythm is retained.
    const duration = clamp(48000 + maxScroll * 0.0011, 52000, 76000);
    run = { controller, scrollBehavior, overlay, hud, guide, actors, targets, maxScroll, duration, elapsed:0, last:0, paused:false, speed:1, phase:'intro', raf:0 };
    const r = run;
    hud.querySelector('.build-skip').addEventListener('click', () => cleanup(true, r.phase === 'complete'), { signal });
    hud.querySelector('.build-pause').addEventListener('click', e => {
      if (r.phase === 'complete') { cleanup(true); start(true); return; }
      r.paused = !r.paused; r.last=0; e.currentTarget.textContent = r.paused ? 'RESUME' : 'PAUSE';
      e.currentTarget.setAttribute('aria-label', r.paused ? 'Resume visual rebuild' : 'Pause visual rebuild');
    }, { signal });
    hud.querySelector('.build-speed').addEventListener('click', e => { r.speed = r.speed === 1 ? 2 : r.speed === 2 ? 3 : 1; e.currentTarget.textContent=r.speed+'×'; }, { signal });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); cleanup(true); } else if (['PageDown','PageUp','ArrowDown','ArrowUp','Home','End',' '].includes(e.key) && !hud.contains(e.target)) { cleanup(true); } }, { signal });
    // Taking over scroll immediately returns control to the visitor.
    window.addEventListener('wheel', () => cleanup(true), { passive:true, signal });
    window.addEventListener('pointerdown', e => { if (!hud.contains(e.target)) cleanup(true); }, { passive:true, signal });
    window.addEventListener('touchstart', e => { if (!hud.contains(e.target)) cleanup(true); }, { passive:true, signal });
    window.addEventListener('resize', () => cleanup(true), { passive:true, signal });
    window.dispatchEvent(new Event('monarch:rebuild-start'));
    function frame(now) {
      if (run !== r) return;
      if (!r.last) r.last=now;
      const delta = Math.min(50, now-r.last); r.last=now;
      if (!r.paused) r.elapsed += delta*r.speed;
      const progress = clamp((r.elapsed-4000)/r.duration,0,1);
      const finish = r.elapsed > r.duration+4000;
      if (!r.paused && !finish) window.scrollTo(0, r.maxScroll*progress);
      r.hud.querySelector('.build-progress i').style.transform='scaleX('+progress+')';
      r.guide.style.transform='translateX('+Math.round(innerWidth*0.045)+'px)';
      // The viewport determines which real elements the cursors can "build".
      if (!r.paused && r.elapsed > 500 && !finish) {
        const waiting = r.targets.filter(t => t.state==='waiting');
        for (const t of waiting) {
          const rect = t.el.getBoundingClientRect();
          if (rect.bottom < -25) { t.el.classList.remove('build-wait'); t.state='done'; continue; }
          if (rect.top > innerHeight*.9 || rect.bottom < 0 || rect.left > innerWidth || rect.right < 0) continue;
          const actor = r.actors.find(a => !a.target);
          if (!actor) break;
          const box=make('div','build-box'); box.style.setProperty('--agent',actor.color);
          const label=make('i'); label.textContent = t.el.matches('img,.hero-car,.work-card') ? 'MEDIA' : t.el.matches('h1,h2,h3,p') ? 'TEXT' : 'FRAME'; box.append(label); r.overlay.append(box);
          t.state='active'; t.box=box; t.start=r.elapsed; t.actor=actor; actor.target=t;
        }
      }
      // Once a block has landed, brief follow-up selections keep the swarm working
      // around the visible page, rather than turning into floating decoration.
      if (!r.paused && !finish && r.elapsed > 1600 && (!r.lastDetail || r.elapsed-r.lastDetail > 420)) {
        r.lastDetail = r.elapsed;
        const inspected = r.targets.filter(t => t.state === 'done' && !t.actor);
        const free = r.actors.filter(a => !a.target);
        if (free.length && r.actors.filter(a => a.target).length < 5) {
          const visible = inspected.filter(t => { const b=t.el.getBoundingClientRect(); return b.top > 60 && b.bottom < innerHeight-40 && b.left >= 0 && b.right <= innerWidth && b.width > 16 && b.height > 12; });
          const t = visible[Math.floor(Math.random()*visible.length)];
          if (t) {
            const a=free[Math.floor(Math.random()*free.length)], box=make('div','build-box');
            box.style.setProperty('--agent',a.color);
            const label=make('i'); label.textContent=t.el.matches('h1,h2,h3,p')?'TEXT':'FRAME'; box.append(label);r.overlay.append(box);
            t.state='active';t.box=box;t.start=r.elapsed;t.actor=a;a.target=t;
          }
        }
      }
      for (const a of r.actors) {
        const t=a.target;
        a.node.classList.toggle('is-busy', !!t);
        let tx,ty;
        if (t) {
          const rect=t.el.getBoundingClientRect(), dt=r.elapsed-t.start;
          const w=clamp(rect.width,4,innerWidth*1.1), h=clamp(rect.height,4,innerHeight*.8);
          const x=clamp(rect.left,-innerWidth*.2,innerWidth), y=clamp(rect.top,-innerHeight*.2,innerHeight);
          const draw=ease(clamp(dt/650,0,1));
          t.box.style.transform='translate3d('+x+'px,'+y+'px,0)'; t.box.style.width=Math.max(3,w*draw)+'px'; t.box.style.height=Math.max(3,h*draw)+'px';
          tx=clamp(x+w*draw,8,innerWidth-24); ty=clamp(y+h*draw,8,innerHeight-28);
          if (dt>720 && t.state==='active') {t.el.classList.remove('build-wait');t.state='revealed';}
          if (dt>1050 || rect.bottom < -100) {t.el.classList.remove('build-wait');t.box.remove();t.state='done';t.actor=null;a.target=null;}
        } else {
          const theta = r.elapsed*.00042+a.seed;
          if (r.elapsed < 1000) { tx=innerWidth*.5+Math.cos(theta)*34;ty=innerHeight*.45+Math.sin(theta)*24; }
          else if (finish) { tx=innerWidth*.77+Math.cos(theta*1.7)*Math.min(innerWidth*.13,125);ty=innerHeight*.26+Math.sin(theta*1.6)*85; }
          else { tx=innerWidth*(.12+(.76*((Math.sin(a.seed*9.1)+1)/2)))+Math.cos(theta)*35;ty=innerHeight*(.16+(.62*((Math.sin(a.seed*4.3)+1)/2)))+Math.sin(theta*1.3)*32; }
        }
        if (!r.paused) { const k=1-Math.pow(.001,delta/1000);a.x+=(tx-a.x)*k;a.y+=(ty-a.y)*k; }
        a.node.style.transform='translate3d('+a.x.toFixed(1)+'px,'+a.y.toFixed(1)+'px,0)';
      }
      if (finish) {
        if (r.phase !== 'complete') {
          r.phase='complete'; r.completedAt=now;
          r.targets.forEach(t=>{ t.el.classList.remove('build-wait');if(t.box)t.box.remove();t.state='done'; });
          r.actors.forEach(a=>a.target=null);
          r.hud.querySelector('.build-label').textContent='REBUILD COMPLETE';
          r.hud.querySelector('.build-pause').textContent='REPLAY';
          r.hud.querySelector('.build-pause').setAttribute('aria-label','Replay visual rebuild');
          r.hud.querySelector('.build-skip').textContent='GO LIVE';
          r.hud.querySelector('.build-speed').hidden=true;
        }
        if (now-r.completedAt>4500) { cleanup(true, true); return; }
      }
      r.raf=requestAnimationFrame(guardedFrame);
    }
    function guardedFrame(now) {
      try { frame(now); } catch (error) { console.error('Visual rebuild stopped:', error); cleanup(true); }
    }
    r.raf=requestAnimationFrame(guardedFrame);
  }
  function init() {
    const trigger=$('#rebuildReplay');
    trigger.addEventListener('click', () => {
      if (reduced.matches) { const el=$('#toast');el.textContent='Visual rebuild is disabled by your reduced motion preference.';el.classList.add('show');setTimeout(()=>el.classList.remove('show'),3200);return; }
      start(true);
    });
    window.addEventListener('monarch:intro-done', () => {
      if (!autoScheduled) { autoScheduled=true; setTimeout(() => start(false), 600); }
    });
  }
  init();
})();
