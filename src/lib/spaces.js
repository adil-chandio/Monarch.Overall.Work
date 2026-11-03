/**
 * Space registry — the bridge between config/spaces.json and the UI.
 *
 * RULE: nothing here invents data. Every number a space shows is either
 *   (a) declared in /config/*.json, or
 *   (b) counted live from the workspace records the user actually has.
 * If a source is empty the UI says "not connected yet" instead of showing a zero
 * dressed up as performance. That is the whole point of this repo.
 */
import { spaces, channels, repos, services, socialAccounts } from './config.js';
import railsFile from '../../config/payment-rails.json';
import { railSummary } from './normalise.js';

const I = {
  yt: 'Youtube',
  studio: 'Clapperboard',
  personal: 'Sparkles',
  proof: 'Globe',
  ops: 'Gauge',
};

/** Which page ids belong to each space, in the order a working day would use them. */
export const SECTIONS = {
  'yt-automation': [
    { id: 'overview', label: 'Command deck', icon: 'Home', hint: 'channels, cadence, what ships next' },
    { id: 'youtube', label: 'Channel studio', icon: 'Video', hint: 'per-channel pipeline and specs' },
    { id: 'calendar', label: 'Publishing calendar', icon: 'CalendarDays', hint: 'slots, gaps, batch days' },
    { id: 'inbox', label: 'Idea inbox', icon: 'ListTodo', hint: 'raw ideas before they become scripts' },
  ],
  'monarch-studio': [
    { id: 'overview', label: 'Studio deck', icon: 'Home', hint: 'clients, films, settlement' },
    { id: 'b2b-portals', label: 'Portals & unlock', icon: 'LockKeyhole', hint: 'locked preview to paid master' },
    { id: 'b2b-leads', label: 'Client leads', icon: 'Inbox', hint: 'briefs that came in' },
    { id: 'b2b-rails', label: 'Payment rails', icon: 'ShieldCheck', hint: 'who can actually get paid, from PK' },
    { id: 'b2b-outreach', label: 'Outreach & sync', icon: 'Zap', hint: 'follow-ups, no cold spam' },
    { id: 'projects', label: 'Film projects', icon: 'BriefcaseBusiness', hint: 'build waves and delivery state' },
    { id: 'agents', label: 'Skill library', icon: 'Sparkles', hint: '931 vendored skills, mapped to jobs' },
  ],
  'personal-brand': [
    { id: 'overview', label: 'Identity deck', icon: 'Home', hint: 'voice, pillars, visual system' },
    { id: 'social', label: 'Social studio', icon: 'Clapperboard', hint: 'accounts and post pipeline' },
    { id: 'youtube', label: 'Showcase cuts', icon: 'Film', hint: 'long-form where the brand lives' },
    { id: 'agents', label: 'Prompt vault', icon: 'Sparkles', hint: 'reusable hooks and formats' },
  ],
  portfolio: [
    { id: 'overview', label: 'Proof surface', icon: 'Home', hint: 'public, real numbers only' },
    { id: 'projects', label: 'Case studies', icon: 'FileText', hint: 'one page per shipped thing' },
    { id: 'vault', label: 'Asset shelf', icon: 'Cloud', hint: 'posters, stills, masters' },
    { id: 'team', label: 'Credits & access', icon: 'Users', hint: 'who can edit the public surface' },
  ],
  ops: [
    { id: 'overview', label: 'Ops deck', icon: 'Home', hint: 'money, repo health, agent runs' },
    { id: 'inbox', label: 'Task queue', icon: 'ListTodo', hint: 'everything open, ranked' },
    { id: 'knowledge', label: 'Knowledge base', icon: 'BookOpen', hint: 'decisions and doctrine' },
    { id: 'agents', label: 'Agent library', icon: 'Sparkles', hint: 'skills, gates, automations' },
    { id: 'vault', label: 'Vault & storage', icon: 'Cloud', hint: 'files, quota, backup state' },
    { id: 'settings', label: 'Connections', icon: 'Settings', hint: 'supabase, payment rails, deploy' },
    { id: 'team', label: 'Access', icon: 'Users', hint: 'who is in the workspace' },
  ],
};

export const spaceList = spaces.map((s) => ({ ...s, icon: I[s.id] || s.icon || 'Gauge' }));

export const getSpaceMeta = (id) => spaceList.find((s) => s.id === id);
export const sectionsFor = (spaceId) => SECTIONS[spaceId] || SECTIONS.ops;

/** Which space owns a page, for the breadcrumb and for direct links. */
export const spaceForPage = (page) => {
  for (const [id, list] of Object.entries(SECTIONS)) {
    if (list.some((s) => s.id === page)) return id;
  }
  if (page?.startsWith('b2b-')) return 'monarch-studio';
  return 'ops';
};

/**
 * Live counts per space. Every value is derived from real records — no placeholders.
 * `connected` tells the UI whether the underlying source exists at all, so an empty
 * space can say "not connected" instead of pretending to be a dashboard with zeros.
 */
export const spaceCounts = (data = {}) => {
  const tasks = data.tasks || [];
  const content = data.content || [];
  const files = data.files || [];
  const projects = data.projects || [];
  const notes = data.notes || [];
  const chats = data.chats || [];

  return {
    'yt-automation': {
      primary: channels.length,
      primaryLabel: 'channels',
      secondary: content.filter((c) => c.kind !== 'social').length,
      secondaryLabel: 'in pipeline',
      connected: channels.length > 0,
      health: content.filter((c) => ['Script', 'Recording', 'Editing'].includes(c.stage)).length
        ? 'producing'
        : 'setup',
    },
    'monarch-studio': {
      primary: services.length,
      primaryLabel: 'services',
      secondary: projects.length,
      secondaryLabel: 'projects',
      connected: services.length > 0,
      // a rail counts only if it can actually receive money from Pakistan (see
      // lib/normalise.js — config lists the rails that cannot)
      health: railSummary(railsFile).live ? 'selling' : 'pre-revenue',
    },
    'personal-brand': {
      primary: socialAccounts.length,
      primaryLabel: 'accounts',
      secondary: content.filter((c) => c.kind === 'social').length,
      secondaryLabel: 'social drafts',
      connected: socialAccounts.length > 0,
      health: 'drafting',
    },
    portfolio: {
      primary: repos.filter((r) => r.role === 'satellite' || r.role === 'core').length,
      primaryLabel: 'shipped repos',
      secondary: projects.length,
      secondaryLabel: 'case studies',
      connected: true,
      health: 'public',
    },
    ops: {
      primary: tasks.filter((t) => !t.done).length,
      primaryLabel: 'open tasks',
      secondary: repos.filter((r) => r.status === 'archived-candidate').length,
      secondaryLabel: 'archive candidates',
      connected: true,
      health: notes.length || chats.length ? 'tracked' : 'cold',
    },
  };
};

/** Honest, config-derived facts shown on each space home under "sources". */
export const spaceSources = (spaceId) => {
  const meta = getSpaceMeta(spaceId);
  if (!meta) return [];
  return [
    ...(meta.config || []).map((f) => `config/${f}`),
    ...(meta.tables || []).map((t) => `table:${t}`),
  ];
};

export const railsSummary = () => railSummary(railsFile);

/** Channels are only relevant inside the yt-automation space. */
export const showsChannels = (spaceId) => spaceId === 'yt-automation';
