/**
 * Normalisers — config/*.json files deliberately use different shapes (rails have
 * `label` and no status, services sell a price *range*, social accounts list several
 * platforms). The UI must not guess at those shapes, so every shape is flattened here,
 * in one pure module with no imports, that can be unit-tested without a build step.
 */

export const priceRange = (usd, pkr) => {
  if (Array.isArray(usd) && usd.length === 2) {
    return { usd: `$${usd[0]}–${usd[1]}`, usdMin: usd[0], usdMax: usd[1], pkr: Array.isArray(pkr) ? `Rs ${pkr[0].toLocaleString()}–${pkr[1].toLocaleString()}` : '' };
  }
  if (typeof usd === 'number') return { usd: `$${usd}`, usdMin: usd, usdMax: usd, pkr: typeof pkr === 'number' ? `Rs ${pkr.toLocaleString()}` : '' };
  return { usd: 'quote', usdMin: null, usdMax: null, pkr: '' };
};

export const serviceRows = (services = []) => services.map((s) => ({
  id: s.slug || s.id || s.title,
  title: s.title || s.name || s.slug,
  badge: s.badge || '',
  price: priceRange(s.price_usd, s.price_pkr),
  turnaround: s.turnaround || '',
  revisions: s.revisions ?? null,
  stages: (s.pipeline || []).length,
}));

/**
 * A rail is only "live" if it can actually receive money from Pakistan *and* the
 * config does not list it as unavailable. Anything else is honestly "unavailable".
 */
export const railRows = (file = {}) => {
  const unavailable = new Set((file.unavailable_from_pakistan || []).map((s) => s.toLowerCase()));
  const rails = (file.rails || []).map((r) => {
    const label = r.label || r.name || r.id;
    const blocked = unavailable.has(String(label).toLowerCase());
    return {
      id: r.id || label,
      label,
      methods: r.methods || [],
      settlement: r.settlement || '',
      fee: typeof r.fee_pct === 'number' ? `${r.fee_pct}%` : '',
      status: blocked ? 'unavailable' : 'live',
      note: blocked ? 'listed as unavailable from Pakistan' : `${r.settlement || 'settlement n/a'} · fee ${r.fee_pct ?? '?'}%`,
    };
  });
  const blocked = (file.unavailable_from_pakistan || []).map((label) => ({
    id: `blocked-${label}`,
    label,
    methods: [],
    settlement: '',
    fee: '',
    status: 'unavailable',
    note: 'cannot be onboarded from Pakistan',
  }));
  return [...rails, ...blocked];
};

export const railSummary = (file = {}) => {
  const rows = railRows(file);
  return { total: rows.length, live: rows.filter((r) => r.status === 'live').length, blocked: rows.filter((r) => r.status !== 'live').length };
};

export const socialRows = (file = {}) => (file.accounts || []).map((a) => ({
  id: a.id,
  label: a.label || a.role || a.handle,
  platforms: Array.isArray(a.platforms) ? a.platforms : [a.platform].filter(Boolean),
  handle: a.handle || '',
  status: a.status || 'active',
  cadence: a.cadence || '',
}));

export const channelRows = (file = {}) => (file.channels || []).map((ch) => ({
  id: ch.id,
  slot: ch.slot || ch.id,
  name: ch.name,
  handle: ch.handle,
  niche: ch.niche || '',
  cadence: ch.cadence || '',
  format: ch.format || '',
  status: ch.status || 'setup',
  kpi: ch.kpi ? `${String(ch.kpi.primary || '').replace(/_/g, ' ')} ${ch.kpi.direction === 'below' ? '≤' : '≥'} ${ch.kpi.target}${String(ch.kpi.primary || '').includes('pct') ? '%' : ''}` : '',
  conflict: ch.conflict_flag || '',
}));

export const repoRows = (file = {}) => (file.repos || []).map((r) => ({
  name: r.name, role: r.role, space: r.space, sizeMb: r.size_mb ?? 0,
  language: r.language, status: r.status, note: r.note || '',
}));
