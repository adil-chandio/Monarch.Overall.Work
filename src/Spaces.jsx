import React, { useMemo, useState } from 'react';
import { ArrowRight, ArrowUpRight, ChevronRight, CircleDot, Search } from 'lucide-react';
import { spaceList, sectionsFor, spaceCounts, spaceSources } from './lib/spaces.js';
import channelsFile from '../config/channels.json';
import reposFile from '../config/repos.json';
import servicesFile from '../config/services.json';
import railsFile from '../config/payment-rails.json';
import socialFile from '../config/social.json';
import { serviceRows, railRows, railSummary, socialRows, channelRows, repoRows } from './lib/normalise.js';

const CHANNELS = channelRows(channelsFile);
const SERVICES = serviceRows(servicesFile.services);
const RAILS = railRows(railsFile);
const SOCIAL = socialRows(socialFile);
const REPOS = repoRows(reposFile);

/**
 * SpaceBar — the five intentional mini-spaces, rendered as a real switcher rather
 * than a decorative menu. Selecting a space changes the section list, the breadcrumb
 * and the route (?space=…&page=…), so a link can point at one space's one section.
 */
export function SpaceBar({ active, onSelect }) {
  return (
    <nav className="space-bar" aria-label="Workspace spaces">
      {spaceList.map((s) => (
        <button
          key={s.id}
          className={`space-tab ${active === s.id ? 'active' : ''}`}
          style={{ '--space-color': s.color }}
          onClick={() => onSelect(s.id)}
          title={s.tagline}
        >
          <span className="space-dot" />
          <span className="space-tab-copy">
            <b>{s.short}</b>
            <small>{s.label}</small>
          </span>
        </button>
      ))}
      <div className="space-bar-rule" />
      <span className="space-bar-note mono">5 SPACES · ONE OS · NOTHING SHARED BY ACCIDENT</span>
    </nav>
  );
}

/** Honest KPI tile: a value, a label, and the source it came from. */
function Kpi({ value, label, source, tone = 'sage' }) {
  return (
    <div className={`space-kpi tone-${tone}`}>
      <b>{value}</b>
      <span>{label}</span>
      <small className="mono">{source}</small>
    </div>
  );
}

const HEALTH_COPY = {
  setup: ['Setup', 'declared, not producing yet'],
  producing: ['Producing', 'work is in the pipeline'],
  selling: ['Selling', 'at least one rail is live'],
  'pre-revenue': ['Pre-revenue', 'no live payment rail yet'],
  drafting: ['Drafting', 'identity stage'],
  public: ['Public', 'shipped and linked'],
  tracked: ['Tracked', 'notes and decisions exist'],
  cold: ['Cold', 'nothing recorded yet'],
};

/**
 * SpaceHome — one screen per space. Every figure is labelled with where it came from,
 * and anything unconnected says so. This is the "no fabricated numbers" rule in UI form.
 */
export function SpaceHome({ spaceId, data, counts, onNavigate, onOpenPage }) {
  const meta = spaceList.find((s) => s.id === spaceId);
  const c = (counts || spaceCounts(data))[spaceId] || {};
  const [healthLabel, healthNote] = HEALTH_COPY[c.health] || ['—', ''];
  const sources = spaceSources(spaceId);
  const sections = sectionsFor(spaceId);

  const railState = railSummary(railsFile);

  return (
    <div className="space-home">
      <header className="space-head" style={{ '--space-color': meta?.color }}>
        <div className="space-head-main">
          <div className="mono space-eyebrow">SPACE · {meta?.short}</div>
          <h1>{meta?.label}</h1>
          <p>{meta?.tagline}</p>
        </div>
        <div className="space-head-side">
          <div className={`space-health health-${c.health || 'cold'}`}>
            <span className="space-health-dot" />
            <div>
              <b>{healthLabel}</b>
              <small>{healthNote}</small>
            </div>
          </div>
          <div className="mono space-route">{meta?.route}</div>
        </div>
      </header>

      <div className="space-kpis">
        <Kpi value={c.primary ?? 0} label={c.primaryLabel || 'items'} source={sources[0] || 'workspace'} tone="sage" />
        <Kpi value={c.secondary ?? 0} label={c.secondaryLabel || 'records'} source={sources[1] || 'workspace'} tone="blue" />
        <Kpi value={sections.length} label="sections in this space" source="src/lib/spaces.js" tone="lavender" />
        <Kpi value={meta?.public ? 'PUBLIC' : 'PRIVATE'} label="visibility" source="config/spaces.json" tone="peach" />
      </div>

      {spaceId === 'yt-automation' && (
        <section className="space-panel">
          <div className="section-head"><div><h2>Channel roster</h2><p>Three slots. Names and targets are declared in config, not assumed.</p></div></div>
          <div className="space-table">
            <div className="space-table-head mono"><span>CHANNEL</span><span>NICHE</span><span>CADENCE</span><span>KPI TARGET</span><span>STATE</span></div>
            {CHANNELS.map((row) => (
              <div className="space-table-row" key={row.handle}>
                <span><b>{row.name}</b><small className="mono">{row.handle}</small></span>
                <span>{row.niche}</span>
                <span>{row.cadence}</span>
                <span className="mono">{row.kpi || 'no KPI set'}</span>
                <span className={`state-chip state-${row.status}`}>{row.status}</span>
                {row.conflict && <span className="space-conflict">{row.conflict}</span>}
              </div>
            ))}
          </div>
        </section>
      )}

      {spaceId === 'monarch-studio' && (
        <section className="space-panel">
          <div className="section-head"><div><h2>Service menu &amp; settlement reality</h2><p>What is for sale, and which rails can actually receive money from Pakistan.</p></div>
            <button className="subtle-link" onClick={() => onNavigate('b2b-rails')}>Payment rails <ArrowRight size={14} /></button>
          </div>
          <div className="space-two-col">
            <div className="space-list">
              <div className="space-list-head mono">SERVICES · price range · turnaround</div>
              {SERVICES.map((s) => (
                <div className="space-list-row" key={s.id}>
                  <b>{s.title}</b>
                  <span className="mono">{s.price.usd} · {s.turnaround}</span>
                </div>
              ))}
              {!SERVICES.length && <div className="space-empty">No services declared in config/services.json yet.</div>}
            </div>
            <div className="space-list">
              <div className="space-list-head mono">RAILS · {railState.live} usable from PK · {railState.blocked} cannot onboard</div>
              {RAILS.map((r) => (
                <div className="space-list-row" key={r.id}>
                  <b>{r.label}</b>
                  <span>{r.methods.length ? r.methods.join(' · ') : r.note}</span>
                  <span className={`state-chip state-${r.status}`}>{r.status}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {spaceId === 'personal-brand' && (
        <section className="space-panel">
          <div className="section-head"><div><h2>Identity surface</h2><p>Accounts and the voice they share. One pillar set, no contradicting posts.</p></div></div>
          <div className="space-list">
            {SOCIAL.map((a) => (
              <div className="space-list-row" key={a.id}>
                <b>{a.label}</b><span>{a.platforms.join(' · ')} · {a.handle}</span>
                <span className={`state-chip state-${a.status}`}>{a.status}</span>
              </div>
            ))}
            {!SOCIAL.length && <div className="space-empty">No accounts declared yet.</div>}
          </div>
        </section>
      )}

      {spaceId === 'portfolio' && (
        <section className="space-panel">
          <div className="section-head"><div><h2>Proof surface</h2><p>Public pages may only show figures that exist in this repo or the studio's own captures.</p></div>
            <button className="subtle-link" onClick={onOpenPage}>Open the live surface <ArrowUpRight size={14} /></button>
          </div>
          <div className="space-list">
            {REPOS.filter((r) => r.role === 'core' || r.role === 'satellite').map((r) => (
              <div className="space-list-row" key={r.name}>
                <b>{r.name}</b><span>{r.note}</span><span className="mono">{r.sizeMb} MB</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {spaceId === 'ops' && (
        <section className="space-panel">
          <div className="section-head"><div><h2>Repo health</h2><p>Archive candidates are counted, never deleted. The core repo stays under 1 GB.</p></div></div>
          <div className="space-two-col">
            <div className="space-list">
              <div className="space-list-row"><b>Total repos</b><span className="mono">{REPOS.length}</span></div>
              <div className="space-list-row"><b>Archive candidates</b><span className="mono">{REPOS.filter((r) => r.status === 'archived-candidate').length}</span></div>
              <div className="space-list-row"><b>Merge candidates</b><span className="mono">{REPOS.filter((r) => r.status === 'merge-candidate').length}</span></div>
              <div className="space-list-row"><b>Payment rails live</b><span className="mono">{railState.live} / {railState.total}</span></div>
              <div className="space-list-row"><b>Core repo size</b><span className="mono">{REPOS.filter((r) => r.role === 'core').reduce((n, r) => n + r.sizeMb, 0)} MB</span></div>
            </div>
            <div className="space-list">
              <div className="space-list-row"><b>Open tasks</b><span className="mono">{(data.tasks || []).filter((t) => !t.done).length}</span></div>
              <div className="space-list-row"><b>Notes</b><span className="mono">{(data.notes || []).length}</span></div>
              <div className="space-list-row"><b>Vault files</b><span className="mono">{(data.files || []).length}</span></div>
            </div>
          </div>
        </section>
      )}

      <section className="space-panel">
        <div className="section-head"><div><h2>Inside this space</h2><p>Each section is its own surface. Nothing borrows another space's numbers.</p></div></div>
        <div className="space-nav-grid">
          {sections.map((s) => (
            <button key={s.id} className="space-nav-card" onClick={() => onNavigate(s.id)}>
              <div className="space-nav-top"><b>{s.label}</b><ArrowUpRight size={14} /></div>
              <span>{s.hint}</span>
            </button>
          ))}
        </div>
      </section>

      <footer className="space-sources mono">
        <span>SOURCES</span>
        {sources.map((s) => <span key={s} className="space-source-chip">{s}</span>)}
      </footer>
    </div>
  );
}

/**
 * CommandPalette — ⌘K. Searches pages, spaces, config records and seeded workspace
 * records in one list, keyboard-first. It exists because five spaces without a fast
 * way to jump between them is just five places to get lost.
 */
export function CommandPalette({ open, onClose, data, onGo }) {
  const [q, setQ] = useState('');
  const [idx, setIdx] = useState(0);

  const items = useMemo(() => {
    const out = [];
    spaceList.forEach((s) => {
      out.push({ kind: 'space', label: `${s.label} — home`, hint: s.tagline, go: { space: s.id, page: 'overview' } });
      sectionsFor(s.id).forEach((sec) => out.push({
        kind: 'section', label: `${s.short} · ${sec.label}`, hint: sec.hint, go: { space: s.id, page: sec.id },
      }));
    });
    CHANNELS.forEach((c) => out.push({ kind: 'channel', label: c.name, hint: `${c.handle} · ${c.niche}`, go: { space: 'yt-automation', page: 'youtube' } }));
    REPOS.forEach((r) => out.push({ kind: 'repo', label: r.name, hint: `${r.role} · ${r.status}`, go: { space: 'ops', page: 'overview' } }));
    RAILS.forEach((r) => out.push({ kind: 'rail', label: r.label, hint: `${r.status} · ${r.methods.slice(0, 2).join('/') || r.note}`, go: { space: 'monarch-studio', page: 'b2b-rails' } }));
    SERVICES.forEach((sv) => out.push({ kind: 'service', label: sv.title, hint: `${sv.price.usd} · ${sv.turnaround}`, go: { space: 'monarch-studio', page: 'overview' } }));
    (data?.tasks || []).forEach((t) => out.push({ kind: 'task', label: t.title, hint: `${t.area} · ${t.due}`, go: { space: 'ops', page: 'inbox' } }));
    (data?.content || []).forEach((c) => out.push({ kind: 'content', label: c.title, hint: `${c.stage} · ${c.channel}`, go: { space: c.kind === 'social' ? 'personal-brand' : 'yt-automation', page: c.kind === 'social' ? 'social' : 'youtube' } }));
    return out;
  }, [data]);

  const filtered = useMemo(() => {
    if (!q.trim()) return items.slice(0, 12);
    const needle = q.toLowerCase();
    return items.filter((i) => `${i.label} ${i.hint} ${i.kind}`.toLowerCase().includes(needle)).slice(0, 14);
  }, [q, items]);

  if (!open) return null;

  const run = (item) => { if (item) onGo(item.go); };
  const onKey = (e) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); setIdx((i) => Math.min(i + 1, filtered.length - 1)); }
    if (e.key === 'ArrowUp') { e.preventDefault(); setIdx((i) => Math.max(i - 1, 0)); }
    if (e.key === 'Enter') { e.preventDefault(); run(filtered[idx]); }
    if (e.key === 'Escape') onClose();
  };

  return (
    <div className="cmdk-overlay" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="cmdk" role="dialog" aria-label="Command palette">
        <div className="cmdk-input">
          <Search size={17} />
          <input
            autoFocus
            value={q}
            onChange={(e) => { setQ(e.target.value); setIdx(0); }}
            onKeyDown={onKey}
            placeholder="Jump to a space, section, channel, repo, task…"
          />
          <kbd>ESC</kbd>
        </div>
        <div className="cmdk-list">
          {filtered.map((item, i) => (
            <button
              key={`${item.kind}-${item.label}-${i}`}
              className={`cmdk-row ${i === idx ? 'active' : ''}`}
              onMouseEnter={() => setIdx(i)}
              onClick={() => run(item)}
            >
              <span className={`cmdk-kind kind-${item.kind}`}>{item.kind}</span>
              <span className="cmdk-label">{item.label}</span>
              <small>{item.hint}</small>
              <ChevronRight size={13} />
            </button>
          ))}
          {!filtered.length && <div className="cmdk-empty">Nothing matches “{q}”. Try a channel name, a repo, or “rails”.</div>}
        </div>
        <div className="cmdk-foot mono">
          <span>↑ ↓ MOVE · ↵ OPEN · ESC CLOSE</span>
          <span>{items.length} targets across 5 spaces</span>
        </div>
      </div>
    </div>
  );
}
