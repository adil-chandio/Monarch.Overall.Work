/* Renando-style open: particles → Figma boxes + cursor → Hello I'm ADIL / PORTFOLIO */
(function () {
  const root = document.getElementById('compose');
  if (!root) return;
  const canvas = document.getElementById('composeCanvas');
  const cursor = document.getElementById('composeCursor');
  const skip = document.getElementById('composeSkip');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const finish = () => {
    root.classList.add('is-out');
    setTimeout(() => {
      root.classList.add('is-gone');
      root.remove();
    }, 700);
  };

  if (reduced || sessionStorage.getItem('ac_compose_seen')) {
    root.remove();
    return;
  }

  skip.addEventListener('click', () => {
    sessionStorage.setItem('ac_compose_seen', '1');
    finish();
  });

  const ctx = canvas.getContext('2d');
  const particles = [];
  const resize = () => {
    const dpr = Math.min(2, devicePixelRatio || 1);
    canvas.width = Math.floor(innerWidth * dpr);
    canvas.height = Math.floor(innerHeight * dpr);
    canvas.style.width = innerWidth + 'px';
    canvas.style.height = innerHeight + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  resize();
  addEventListener('resize', resize);

  const off = document.createElement('canvas');
  off.width = 420; off.height = 280;
  const o = off.getContext('2d');
  o.fillStyle = '#fff';
  o.font = '800 210px Manrope, sans-serif';
  o.textAlign = 'center';
  o.textBaseline = 'middle';
  o.fillText('A', 210, 150);
  const { data } = o.getImageData(0, 0, off.width, off.height);
  const scale = Math.min(innerWidth / 520, innerHeight / 420, 1.2);
  const colors = ['#ece9e2', '#7ad0ff', '#d21f2b', '#f4d35e', '#9b8cff'];
  for (let y = 0; y < off.height; y += 5) {
    for (let x = 0; x < off.width; x += 5) {
      if (data[(y * off.width + x) * 4 + 3] > 40) {
        particles.push({
          x: Math.random() * innerWidth,
          y: Math.random() * innerHeight,
          tx: innerWidth / 2 + (x - 210) * scale,
          ty: innerHeight / 2 + (y - 140) * scale,
          r: 1.1 + Math.random() * 2.2,
          hue: colors[(Math.random() * colors.length) | 0]
        });
      }
    }
  }

  let start = performance.now();
  const tick = (now) => {
    const t = (now - start) / 1000;
    ctx.fillStyle = t < 2.1 ? 'rgba(5,5,8,0.42)' : 'rgba(5,5,8,0.12)';
    ctx.fillRect(0, 0, innerWidth, innerHeight);
    const settle = Math.min(1, t / 1.7);
    const ease = 1 - (1 - settle) ** 3;
    const scatter = t > 1.85 ? Math.min(1, (t - 1.85) / 0.45) : 0;
    for (const p of particles) {
      p.x += (p.tx - p.x) * (0.05 + ease * 0.07);
      p.y += (p.ty - p.y) * (0.05 + ease * 0.07);
      ctx.beginPath();
      ctx.fillStyle = p.hue;
      ctx.globalAlpha = 0.4 + ease * 0.6 - scatter * 0.35;
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
    if (t < 3.2) requestAnimationFrame(tick);
  };
  ctx.fillStyle = '#050508';
  ctx.fillRect(0, 0, innerWidth, innerHeight);
  requestAnimationFrame(tick);

  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const moveClick = async (x, y, key) => {
    cursor.style.transform = `translate(${x}px, ${y}px)`;
    await wait(400);
    cursor.classList.add('is-click');
    const layer = root.querySelector(`[data-layer="${key}"]`);
    if (layer) layer.classList.add('is-on');
    await wait(150);
    cursor.classList.remove('is-click');
  };

  (async () => {
    await wait(2000);
    root.classList.add('is-compose');
    const w = innerWidth, h = innerHeight;
    await moveClick(w * 0.28, h * 0.42, 'type');
    await wait(200);
    await moveClick(w * 0.52, h * 0.48, 'photo');
    await wait(200);
    await moveClick(w * 0.22, h * 0.28, 'name');
    await wait(700);
    root.classList.add('is-settle');
    await wait(1600);
    sessionStorage.setItem('ac_compose_seen', '1');
    finish();
  })();
})();
