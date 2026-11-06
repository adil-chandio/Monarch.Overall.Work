import React, { useEffect, useRef, useState } from 'react';

function CursorIcon() {
  return (
    <svg width="26" height="26" viewBox="0 0 28 28" fill="none" aria-hidden="true">
      <path d="M4.2 3.4 12.8 24.2l2.5-8.4 8.5-1.6L4.2 3.4Z" fill="#fff" stroke="#111" strokeWidth="1.4" strokeLinejoin="round" />
    </svg>
  );
}

function Handles({ className }) {
  return (
    <span className={`m-fig-handles ${className || ''}`} aria-hidden="true">
      <i /><i /><i /><i /><i /><i /><i /><i />
    </span>
  );
}

/**
 * Load sequence from the Renando reference:
 * particles → Figma bounding boxes + cursor placing layers →
 * Hello I'm ADIL / PORTFOLIO / portrait → wipe into the real site.
 */
export function CinematicOpen({ onDone }) {
  const canvasRef = useRef(null);
  const doneRef = useRef(onDone);
  doneRef.current = onDone;
  const [phase, setPhase] = useState('particles');
  const [placed, setPlaced] = useState({ type: false, photo: false, name: false });
  const [cursor, setCursor] = useState({ x: 18, y: 42, click: false });
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches) {
      doneRef.current?.();
      return;
    }
    document.documentElement.classList.add('m-intro-lock');
    return () => document.documentElement.classList.remove('m-intro-lock');
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let raf = 0;
    const particles = [];

    const resize = () => {
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      canvas.width = Math.floor(window.innerWidth * dpr);
      canvas.height = Math.floor(window.innerHeight * dpr);
      canvas.style.width = `${window.innerWidth}px`;
      canvas.style.height = `${window.innerHeight}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener('resize', resize);

    const off = document.createElement('canvas');
    off.width = 420;
    off.height = 280;
    const octx = off.getContext('2d');
    octx.fillStyle = '#fff';
    octx.font = '800 210px Syne, Manrope, sans-serif';
    octx.textAlign = 'center';
    octx.textBaseline = 'middle';
    octx.fillText('M', 210, 150);
    const { data } = octx.getImageData(0, 0, off.width, off.height);
    const targets = [];
    for (let y = 0; y < off.height; y += 5) {
      for (let x = 0; x < off.width; x += 5) {
        if (data[(y * off.width + x) * 4 + 3] > 40) targets.push({ x, y });
      }
    }

    const W = () => window.innerWidth;
    const H = () => window.innerHeight;
    const scale = Math.min(W() / 520, H() / 420, 1.2);
    const colors = ['#ece9e2', '#7ad0ff', '#d21f2b', '#f4d35e', '#9b8cff'];
    targets.forEach((t) => {
      particles.push({
        x: Math.random() * W(),
        y: Math.random() * H(),
        tx: W() / 2 + (t.x - 210) * scale,
        ty: H() / 2 + (t.y - 140) * scale,
        r: 1.1 + Math.random() * 2.2,
        hue: colors[(Math.random() * colors.length) | 0],
      });
    });

    let start = performance.now();
    const tick = (now) => {
      const t = (now - start) / 1000;
      const w = W();
      const h = H();
      ctx.fillStyle = t < 2.1 ? 'rgba(5,5,8,0.42)' : 'rgba(5,5,8,0.12)';
      ctx.fillRect(0, 0, w, h);
      const settle = Math.min(1, t / 1.7);
      const ease = 1 - (1 - settle) ** 3;
      const scatter = t > 1.85 ? Math.min(1, (t - 1.85) / 0.45) : 0;
      for (const p of particles) {
        const dx = (Math.random() - 0.5) * scatter * 18;
        const dy = (Math.random() - 0.5) * scatter * 18;
        p.x += (p.tx + dx - p.x) * (0.05 + ease * 0.07);
        p.y += (p.ty + dy - p.y) * (0.05 + ease * 0.07);
        ctx.beginPath();
        ctx.fillStyle = p.hue;
        ctx.globalAlpha = 0.4 + ease * 0.6 - scatter * 0.35;
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
      if (t < 3.2) raf = requestAnimationFrame(tick);
    };
    ctx.fillStyle = '#050508';
    ctx.fillRect(0, 0, W(), H());
    raf = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', resize);
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    const wait = (ms) => new Promise((r) => setTimeout(r, ms));
    const clickAt = async (x, y, key) => {
      setCursor({ x, y, click: false });
      await wait(380);
      if (cancelled) return;
      setCursor({ x, y, click: true });
      if (key) setPlaced((p) => ({ ...p, [key]: true }));
      await wait(140);
      setCursor({ x, y, click: false });
    };

    (async () => {
      await wait(2000);
      if (cancelled) return;
      setPhase('compose');
      const w = window.innerWidth;
      const h = window.innerHeight;
      await clickAt(w * 0.28, h * 0.42, 'type');
      await wait(220);
      await clickAt(w * 0.52, h * 0.48, 'photo');
      await wait(220);
      await clickAt(w * 0.22, h * 0.28, 'name');
      await wait(700);
      if (cancelled) return;
      setPhase('settle');
      await wait(1600);
      if (cancelled) return;
      setPhase('out');
      await wait(720);
      if (cancelled) return;
      document.documentElement.classList.remove('m-intro-lock');
      setVisible(false);
      doneRef.current?.();
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  const skip = () => {
    document.documentElement.classList.remove('m-intro-lock');
    setVisible(false);
    doneRef.current?.();
  };

  if (!visible) return null;

  return (
    <div className={`m-cinematic ${phase}`}>
      <canvas ref={canvasRef} className="m-cinematic-canvas" />

      <div className="m-cin-stage">
        <div className={`m-cin-layer m-cin-giant ${placed.type ? 'is-on' : ''}`}>
          <Handles />
          <span>PORTFOLIO</span>
        </div>

        <div className={`m-cin-layer m-cin-photo ${placed.photo ? 'is-on' : ''}`}>
          <Handles />
          <img src="/proof/portrait-masked.png" alt="" />
        </div>

        <div className={`m-cin-layer m-cin-hello ${placed.name ? 'is-on' : ''}`}>
          <Handles />
          <em>Hello, I&apos;m</em>
          <b>ADIL.</b>
          <small>EDITOR &amp; VFX · WEB SYSTEMS</small>
        </div>
      </div>

      {phase !== 'particles' && (
        <div
          className={`m-builder-cursor${cursor.click ? ' is-click' : ''}`}
          style={{ transform: `translate(${cursor.x}px, ${cursor.y}px)` }}
        >
          <CursorIcon />
          <span className="m-builder-ripple" />
        </div>
      )}

      <button type="button" className="m-cinematic-skip" onClick={skip}>
        Skip
      </button>
    </div>
  );
}
