/* MONARCH rebuild: independently implemented visual tour.
   One timeline owns the cursor, selection and reveal of each real page element. */
(() => {
  'use strict';
  const SEEN = 'monarch_rebuild_seen_v1';
  const palette = ['#6cbce6','#df7585','#b18ce7','#78c8aa','#e0a96c','#899fe8','#e887b8','#8ccdd2'];
  const names = ['NOVA','ECHO','ATLAS','PIXEL','ORBIT','FLUX','EMBER','NORTH','SORA','VEX','LUMA','NIM','MICA','DUNE','INK','KITE','BOLT','LYRA','VALE','RIO','FINN','REMI','SAGE','SOL'];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const TRAVEL = 500, DRAW = 650, REVEAL = 700, HOLD = 180;
  let run = null, autoScheduled = false;
  const seen = () => { try { return sessionStorage.getItem(SEEN) === '1'; } catch (_) { return true; } };
  const markSeen = () => { try { sessionStorage.setItem(SEEN, '1'); } catch (_) {} };
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const ease = v => v*v*(3-2*v);
  const $ = s => document.querySelector(s);
  const make = (tag, cls) => { const el = document.createElement(tag); if (cls) el.className = cls; return el; };
  const visibleX = rect => rect.right > 0 && rect.left < innerWidth;
  function clearTarget(t) {
    t.el.classList.remove('build-wait', 'build-drawing');
    t.el.style.removeProperty('--build-reveal');
    delete t.el.dataset.buildPhase;
    delete t.el.dataset.buildActor;
    if (t.box) { t.box.remove(); t.box = null; }
  }
  function markRevealed(el) {
    if (el.matches('[data-rv]')) el.classList.add('in');
    el.querySelectorAll('[data-rv]').forEach(child => child.classList.add('in'));
    window.dispatchEvent(new CustomEvent('monarch:rebuild-reveal', { detail: { element: el } }));
  }
  function cleanup(completed, returnToTop = false) {
    if (!run) return;
    const r = run; run = null;
    cancelAnimationFrame(r.raf);
    r.controller.abort();
    r.targets.forEach(clearTarget);
    document.body.classList.remove('monarch-build-active');
    // An observer may have fired while the tour controlled this viewport. Only settle
    // currently visible elements; leave unvisited ones to the site's normal reveals.
    document.querySelectorAll('main [data-rv]').forEach(el => {
      const b = el.getBoundingClientRect();
      if (b.bottom > 0 && b.top < innerHeight && visibleX(b)) el.classList.add('in');
    });
    r.overlay.remove(); r.hud.remove();
    if (returnToTop) window.scrollTo({ top:0, behavior:'instant' });
    document.documentElement.style.scrollBehavior = r.scrollBehavior;
    if (completed) markSeen();
    window.dispatchEvent(new CustomEvent('monarch:rebuild-end', { detail: { completed } }));
  }
  function collectTargets() {
    // Include every native reveal and the important non-reveal page components.
    // A selected ancestor owns its children, so nested elements never flash ahead.
    const selector = 'main [data-rv], main .hero-wm, main .hero-car, main .stage-tags, main .marquee, main .work-swipe, main .work-plank, main .sol-flag, main blockquote, main .timeline li, footer';
    const all = Array.from(document.querySelectorAll(selector));
    const chosen = new Set(all);
    return all.filter(el => {
      if (el.closest('.curtain, #player, #letterModal, #rcModal')) return false;
      let p = el.parentElement;
      while (p && p !== document.body) { if (chosen.has(p)) return false; p = p.parentElement; }
      const rect = el.getBoundingClientRect();
      // Mobile film cards in the horizontal carousel outside its viewport are not
      // part of this vertical tour. They remain normally accessible when swiped.
      return rect.width > 2 && rect.height > 2 && visibleX(rect) && getComputedStyle(el).display !== 'none';
    }).map(el => ({ el, state:'waiting', box:null }));
  }
  function start(manual = false) {
    if (run || document.body.classList.contains('locked')) return;
    if (reduced.matches) return;
    if (!manual && (seen() || location.hash)) return;
    markSeen();
    const controller = new AbortController(), signal = controller.signal;
    const scrollBehavior = document.documentElement.style.scrollBehavior;
    document.documentElement.style.scrollBehavior = 'auto';
    window.scrollTo(0, 0);
    // Suspend the site's own reveal styling before measuring, in the same paint as
    // hiding our targets. This avoids a frame of already-visible text at the start.
    document.body.classList.add('monarch-build-active');
    const targets = collectTargets();
    if (!targets.length) {
      document.body.classList.remove('monarch-build-active');
      document.documentElement.style.scrollBehavior = scrollBehavior;
      return;
    }
    targets.forEach(t => { t.el.classList.add('build-wait'); t.el.dataset.buildPhase = 'waiting'; });
    const overlay = make('div','build-overlay'); overlay.setAttribute('aria-hidden','true');
    const guide = make('div','build-guide'); overlay.append(guide);
    const hud = make('div','build-hud');
    hud.setAttribute('role','region'); hud.setAttribute('aria-label','Visual rebuild controls');
    hud.innerHTML = '<span class="build-dots" aria-hidden="true"></span><span class="build-label">VISUAL REBUILD</span><span class="build-progress" aria-hidden="true"><i></i></span><button type="button" class="build-pause" aria-label="Pause visual rebuild">PAUSE</button><button type="button" class="build-speed" aria-label="Change rebuild speed">1×</button><button type="button" class="build-skip">SKIP</button>';
    palette.slice(0,6).forEach(c => { const d=make('i'); d.style.setProperty('--dot',c); hud.querySelector('.build-dots').append(d); });
    const actors = names.slice(0, innerWidth < 650 ? 12 : 24).map((name, i) => {
      const node = make('div','build-cursor'), color = palette[i % palette.length]; node.style.setProperty('--agent',color); node.dataset.actor=name;
      node.innerHTML = '<svg viewBox="0 0 20 24" aria-hidden="true"><path d="M2 1.5 17 14l-6 .4-2.8 6.7z" fill="'+color+'" stroke="white" stroke-width="1.3" stroke-linejoin="round"/></svg><span>'+name+'</span>';
      overlay.append(node);
      return { node, name, color, x:innerWidth/2, y:innerHeight/2, target:null, seed:i*2.4 };
    });
    document.body.append(overlay, hud);
    const maxScroll = Math.max(0, document.documentElement.scrollHeight-innerHeight);
    const duration = clamp(48000 + maxScroll * 0.0011, 52000, 76000);
    run = { controller, scrollBehavior, overlay, hud, guide, actors, targets, maxScroll, duration, elapsed:0, last:0, paused:false, speed:1, phase:'tour', raf:0, scroll:0 };
    const r = run;
    hud.querySelector('.build-skip').addEventListener('click', () => cleanup(true, r.phase === 'complete'), { signal });
    hud.querySelector('.build-pause').addEventListener('click', e => {
      if (r.phase === 'complete') { cleanup(true); start(true); return; }
      r.paused = !r.paused; r.last=0; e.currentTarget.textContent = r.paused ? 'RESUME' : 'PAUSE';
      e.currentTarget.setAttribute('aria-label', r.paused ? 'Resume visual rebuild' : 'Pause visual rebuild');
    }, { signal });
    hud.querySelector('.build-speed').addEventListener('click', e => { r.speed = r.speed === 1 ? 2 : r.speed === 2 ? 3 : 1; e.currentTarget.textContent=r.speed+'×'; }, { signal });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); cleanup(true); } else if (['PageDown','PageUp','ArrowDown','ArrowUp','Home','End',' '].includes(e.key) && !hud.contains(e.target)) cleanup(true); }, { signal });
    window.addEventListener('wheel', () => cleanup(true), { passive:true, signal });
    window.addEventListener('pointerdown', e => { if (!hud.contains(e.target)) cleanup(true); }, { passive:true, signal });
    window.addEventListener('touchstart', e => { if (!hud.contains(e.target)) cleanup(true); }, { passive:true, signal });
    window.addEventListener('resize', () => cleanup(true), { passive:true, signal });
    window.dispatchEvent(new Event('monarch:rebuild-start'));
    function assign(t, actor) {
      const box=make('div','build-box'); box.style.setProperty('--agent',actor.color); box.dataset.actor=actor.name;
      const label=make('i'); label.textContent=t.el.matches('img,.hero-car,.work-card,.phone') ? 'MEDIA' : t.el.matches('h1,h2,h3,p,li') ? 'TEXT' : 'FRAME';
      box.append(label); r.overlay.append(box);
      t.state='active'; t.box=box; t.start=r.elapsed; t.actor=actor; t.originX=actor.x; t.originY=actor.y;
      t.el.dataset.buildPhase='approach'; t.el.dataset.buildActor=actor.name; actor.target=t;
    }
    function frame(now) {
      if (run !== r) return;
      if (!r.last) r.last=now;
      const realDelta = Math.min(50, now-r.last); r.last=now;
      const delta = r.paused ? 0 : realDelta*r.speed;
      r.elapsed += delta;
      // Images and fonts can change page height after the tour starts.
      r.maxScroll = Math.max(0, document.documentElement.scrollHeight-innerHeight);
      r.scroll = Math.min(r.scroll, r.maxScroll);
      r.guide.style.transform='translateX('+Math.round(innerWidth*0.045)+'px)';
      if (r.phase === 'tour' && !r.paused && r.elapsed > 3000) {
        // Move first, then measure every box/cursor from the resulting viewport.
        // Slow down only when unfinished work is approaching the top edge.
        const needsTime = r.targets.some(t => {
          if (t.state==='done') return false;
          const b=t.el.getBoundingClientRect();
          return visibleX(b) && b.bottom > 0 && b.top < innerHeight*(t.state==='waiting' ? .35 : .20);
        });
        if (!needsTime) {
          r.scroll=Math.min(r.maxScroll,r.scroll+(r.maxScroll/r.duration)*delta);
          window.scrollTo(0,r.scroll);
        }
      }
      if (r.phase === 'tour' && !r.paused && r.elapsed >= 450) {
        // Work on elements as they enter the viewport; auto-scroll never outruns
        // pending or active work, even with slow devices and the 3x setting.
        for (const t of r.targets) {
          if (t.state !== 'waiting') continue;
          const rect=t.el.getBoundingClientRect();
          if (rect.bottom <= 0 || rect.top >= innerHeight*.72 || !visibleX(rect)) continue;
          const actor=r.actors.find(a => !a.target);
          if (!actor) break;
          assign(t,actor);
        }
      }
      for (const a of r.actors) {
        const t=a.target;
        a.node.classList.toggle('is-busy', !!t);
        if (t) {
          const rect=t.el.getBoundingClientRect(), dt=r.elapsed-t.start;
          // The selection is a viewport overlay; the real element supplies the
          // same geometry on every frame, including during any page layout changes.
          const x=rect.left, y=rect.top, w=rect.width, h=rect.height;
          const travel=ease(clamp(dt/TRAVEL,0,1));
          const draw=ease(clamp((dt-TRAVEL)/DRAW,0,1));
          const reveal=ease(clamp((dt-TRAVEL-DRAW)/REVEAL,0,1));
          t.box.style.transform='translate3d('+x+'px,'+y+'px,0)';
          t.box.style.width=Math.max(1,w*draw)+'px'; t.box.style.height=Math.max(1,h*draw)+'px';
          t.box.style.opacity=dt<TRAVEL ? '0' : '1';
          if (dt<TRAVEL) {
            a.x=t.originX+(x-t.originX)*travel; a.y=t.originY+(y-t.originY)*travel;
          } else if (dt<TRAVEL+DRAW) {
            t.el.dataset.buildPhase='draw';
            a.x=x+w*draw; a.y=y+h*draw;
          } else {
            if (t.state==='active') {
              t.state='revealing'; t.el.classList.remove('build-wait'); t.el.classList.add('build-drawing');
              t.el.dataset.buildPhase='reveal';
            }
            t.el.style.setProperty('--build-reveal', (100*reveal).toFixed(2)+'%');
            a.x=x+w*reveal; a.y=y+Math.min(h*.55, 22);
            if (dt>=TRAVEL+DRAW+REVEAL+HOLD) {
              markRevealed(t.el); clearTarget(t); t.state='done'; t.actor=null; a.target=null;
            }
          }
        } else if (!r.paused) {
          const theta = r.elapsed*.00042+a.seed;
          let tx,ty;
          if (r.elapsed < 1000) { tx=innerWidth*.5+Math.cos(theta)*34;ty=innerHeight*.45+Math.sin(theta)*24; }
          else if (r.phase==='complete') { tx=innerWidth*.77+Math.cos(theta*1.7)*Math.min(innerWidth*.13,125);ty=innerHeight*.26+Math.sin(theta*1.6)*85; }
          else { tx=innerWidth*(.12+(.76*((Math.sin(a.seed*9.1)+1)/2)))+Math.cos(theta)*35;ty=innerHeight*(.16+(.62*((Math.sin(a.seed*4.3)+1)/2)))+Math.sin(theta*1.3)*32; }
          const k=1-Math.pow(.001,delta/1000); a.x+=(tx-a.x)*k; a.y+=(ty-a.y)*k;
        }
        a.node.style.transform='translate3d('+a.x.toFixed(1)+'px,'+a.y.toFixed(1)+'px,0)';
      }
      if (r.phase === 'tour' && !r.paused) {
        const blocking=r.targets.some(t => {
          if (t.state==='done') return false;
          const b=t.el.getBoundingClientRect();
          return visibleX(b) && b.top < innerHeight*.72 && b.bottom > 0;
        });
        r.hud.querySelector('.build-progress i').style.transform='scaleX('+(r.maxScroll ? r.scroll/r.maxScroll : 1)+')';
        if (r.scroll>=r.maxScroll-1 && !blocking && !r.actors.some(a=>a.target)) {
          r.phase='complete'; r.completedAt=now;
          r.hud.querySelector('.build-label').textContent='REBUILD COMPLETE';
          r.hud.querySelector('.build-pause').textContent='REPLAY';
          r.hud.querySelector('.build-pause').setAttribute('aria-label','Replay visual rebuild');
          r.hud.querySelector('.build-skip').textContent='GO LIVE';
          r.hud.querySelector('.build-speed').hidden=true;
        }
      }
      if (r.phase==='complete' && now-r.completedAt>4500) { cleanup(true,true); return; }
      r.raf=requestAnimationFrame(guardedFrame);
    }
    function guardedFrame(now) { try { frame(now); } catch (error) { console.error('Visual rebuild stopped:',error); cleanup(true); } }
    r.raf=requestAnimationFrame(guardedFrame);
  }
  function init() {
    $('#rebuildReplay').addEventListener('click', () => {
      if (reduced.matches) { const el=$('#toast');el.textContent='Visual rebuild is disabled by your reduced motion preference.';el.classList.add('show');setTimeout(()=>el.classList.remove('show'),3200);return; }
      start(true);
    });
    window.addEventListener('monarch:intro-done', () => { if (!autoScheduled) { autoScheduled=true; setTimeout(() => start(false),600); } });
  }
  init();
})();
