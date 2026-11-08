import React, { useEffect, useMemo, useState } from 'react';
import { ArrowRight, ArrowUpRight, ChevronRight, CircleDot, Play, RotateCw, Search } from 'lucide-react';
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

      {spaceId === 'yt-automation' && <ResearchPanel onNavigate={onNavigate} />}

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

const fmtCount = (n) => (n >= 1e6 ? `${(n / 1e6).toFixed(1)}M` : n >= 1e3 ? `${(n / 1e3).toFixed(n >= 1e4 ? 0 : 1)}k` : `${n}`);

/**
 * ResearchPanel — the yt_intel bridge, on screen.
 *
 * It reads `public/yt-intel/index.json` (written by `scripts/yt-index.mjs`, which is only a
 * bridge to the Python tool). Three states, all honest:
 *   no index      -> explain the two commands that produce one
 *   verdict RETRY -> say the sample never arrived, and name the fix (API key / network)
 *   verdict GO/…  -> score, parts, objections, next probe
 *
 * The panel never computes a score itself. Two implementations of the same number is how
 * a dashboard starts lying quietly.
 */
function ResearchPanel({ onNavigate }) {
  const [state, setState] = useState({ status: 'loading', reports: [], lanes: null });
  useEffect(() => {
    let live = true;
    // Two files, deliberately: the reports and the lane the last CI run actually used. The
    // lane file is written by the workflow itself, so this panel can never claim the API is
    // in use when the run that produced these numbers was keyless.
    Promise.all([
      fetch('/yt-intel/index.json', { cache: 'no-cache' })
        .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
        .then((d) => d)
        .catch(() => null),
      fetch('/yt-intel/lanes.json', { cache: 'no-cache' })
        .then((r) => (r.ok ? r.json() : null))
        .catch(() => null),
    ]).then(([payload, lanes]) => {
      if (!live) return;
      setState(payload
        ? { status: 'ok', reports: payload.reports || [], comments: payload.comments || [],
            thumbnails: payload.thumbnails || null, lanes }
        : { status: 'none', reports: [], comments: [], thumbnails: null, lanes });
    });
    return () => { live = false; };
  }, []);

  const recent = [...state.reports].sort((a, b) => (b.at || '').localeCompare(a.at || '')).slice(0, 6);

  return (
    <section className="space-panel">
      <div className="section-head">
        <div>
          <h2>Research desk</h2>
          <p>Demand → saturation → mechanism → verdict, computed by <code>yt_intel</code> and cached in the repo.</p>
        </div>
        <span className="mono research-lane">{state.status === 'ok' ? `${state.reports.length} reports` : 'no reports yet'}</span>
      </div>

      {state.status === 'loading' && <div className="space-empty">Reading the research index…</div>}

      {state.status === 'none' && (
        <div className="research-empty">
          <b>No research has been run yet.</b>
          <span>Two commands produce a report. Nothing is generated in the browser, so what you see here is always a real measurement.</span>
          <div className="research-cmd mono">
            <code>npm run yt:topic -- "your topic"</code>
            <code>python -m yt_intel topic "your topic" --limit 30 --order thisMonth --json public/yt-intel/your-topic.json</code>
          </div>
        </div>
      )}

      {recent.length > 0 && (
        <div className="research-list">
          {recent.map((r) => {
            // two shapes reach this panel: the full report (decision.verdict) and the slim
            // index entry (verdict at top level). Support both rather than rendering "—".
            const d = r.decision || r;
            const retry = d.verdict === 'RETRY';
            return (
              <article className={`research-card ${retry ? 'research-retry' : ''}`} key={`${r.topic}-${r.at}`}>
                <header>
                  <div>
                    <b>{r.topic}</b>
                    <small className="mono">
                      {r.lane} lane · {r.count ?? 0} videos · {r.status}
                      {d.confidence != null && ` · conf ${Math.round(d.confidence * 100)}%`}
                    </small>
                  </div>
                  <span className={`research-verdict v-${(d.verdict || 'none').toLowerCase()}`}>
                    {retry ? <RotateCw size={11} /> : <Play size={11} />}
                    {d.verdict || '—'}{d.score != null ? ` ${d.score}` : ''}
                  </span>
                </header>
                <p className="research-reason">{d.reason}</p>
                {(() => {
                  // The numbers that decide whether an angle is worth a day. Joined as one
                  // string so the line still reads correctly when copied or spoken.
                  const stats = [
                    // the ask itself, first: a median without its search order is unreadable
                    r.order ? `asked as ${r.order}` : null,
                    r.saturation?.median_views != null ? `median ${fmtCount(r.saturation.median_views)} views` : null,
                    r.vph_median != null ? `${fmtCount(r.vph_median)} views/hour` : null,
                    r.saturation?.reading || null,
                  ].filter(Boolean);
                  return stats.length ? <p className="research-stats mono">{stats.join(' · ')}</p> : null;
                })()}
                {retry ? (
                  <p className="research-probe"><b>Next probe:</b> {d.next_probe}</p>
                ) : (
                  <>
                    <div className="research-parts">
                      {Object.entries(d.parts || {}).map(([k, v]) => (
                        <div key={k} className="research-part">
                          <span>{k}</span>
                          <div className="research-meter"><i style={{ width: `${Math.max(0, Math.min(100, v ?? 0))}%` }} /></div>
                          <b className="mono">{v == null ? '—' : Math.round(v)}</b>
                        </div>
                      ))}
                    </div>
                    {d.strongest_against?.length > 0 && (
                      <ul className="research-against">{d.strongest_against.slice(0, 2).map((a) => <li key={a}>{a}</li>)}</ul>
                    )}
                    {d.next_probe && <p className="research-probe"><b>Next probe:</b> {d.next_probe}</p>}
                  </>
                )}
              </article>
            );
          })}
        </div>
      )}

      {state.lanes && (
        <div className={`research-lane-state ${state.lanes.key_present ? 'lane-api' : 'lane-web'}`}>
          {state.lanes.key_present ? (
            <>
              <b>Data API lane</b>
              <span>
                last CI run used <code>{state.lanes.key_secret_name}</code> · quota {state.lanes.quota_remaining} units left
              </span>
            </>
          ) : (
            <>
              <b>Keyless lane</b>
              <span>
                the last CI run measured these reports without an API key
                {state.lanes.secrets_seen && Object.values(state.lanes.secrets_seen).every((v) => !v)
                  ? ' — no key secret reached the run at all'
                  : ' — a key exists but did not resolve; check the secret name'}
                . View counts and ages are parsed from public pages, so exact likes, comment
                counts and comment mining are unavailable until a key lands.
              </span>
            </>
          )}
        </div>
      )}

      {(state.comments || []).length > 0 && (
        <div className="research-comments">
          <div className="research-comments-head">
            <b>Comment mining</b>
            <span>what the audience of a winning video actually asked for · API lane only</span>
          </div>
          {state.comments.slice(0, 2).map((c) => (
            <article className="research-comment-card" key={c.video}>
              <header>
                <a href={`https://www.youtube.com/watch?v=${c.video}`} target="_blank" rel="noreferrer">
                  {c.video}
                </a>
                <span className="mono">{c.n} comments</span>
              </header>
              <p>{c.reading}</p>
              <div className="research-comment-lists">
                {[['asked', c.asks], ['objected', c.objections], ['wanted', c.wants]].map(([label, rows]) =>
                  (rows || []).length ? (
                    <div key={label}>
                      <span className="mono">{label}</span>
                      <ul>
                        {rows.map((h) => (
                          <li key={h.label}>
                            <b className="mono">{Math.round(h.share * 100)}%</b> {h.label}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : null,
                )}
              </div>
              {(c.top_liked || []).length > 0 && (
                <ul className="research-top-liked">
                  {c.top_liked.map((t) => (
                    <li key={t.text}>
                      <b className="mono">{fmtCount(t.likes)}♥</b> {t.text}
                    </li>
                  ))}
                </ul>
              )}
            </article>
          ))}
        </div>
      )}

      {state.thumbnails && (
        <div className="research-thumbs">
          <div className="research-comments-head">
            <b>Thumbnail forensics</b>
            <span>
              {state.thumbnails.n} thumbnails from “{state.thumbnails.topic}” · fetched by the CI
              runner, not the browser
            </span>
          </div>
          <p className="research-thumb-reading">{state.thumbnails.reading}</p>
          <div className="research-thumb-strip">
            {state.thumbnails.samples.map((s) => (
              <a
                key={s.id}
                className="research-thumb"
                href={`https://www.youtube.com/watch?v=${s.id}`}
                target="_blank"
                rel="noreferrer"
              >
                <img src={`https://i.ytimg.com/vi/${s.id}/mqdefault.jpg`} alt="" loading="lazy" />
                <span className="mono">
                  <i style={{ background: s.hex || 'transparent' }} />
                  {s.hex || '—'} · face {Math.round((s.face || 0) * 100)}%
                </span>
              </a>
            ))}
          </div>
          <div className="research-thumb-families mono">
            {(state.thumbnails.hue_families || []).map(([name, n]) => (
              <span key={name}>
                {name} {n}/{state.thumbnails.n}
              </span>
            ))}
            <span>contrast {state.thumbnails.avg_contrast}</span>
            <span>busy {state.thumbnails.avg_busy}</span>
          </div>
        </div>
      )}

      <div className="research-foot mono">
        <span>keyless by default · API key optional</span>
        <span>1 request/second, cached to disk</span>
      </div>
    </section>
  );
}
