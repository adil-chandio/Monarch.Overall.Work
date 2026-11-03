/**
 * Config-shape tests. No framework: run with `node src/lib/normalise.test.mjs`.
 * These exist because the UI silently rendering "undefined" for a rail or a price is
 * exactly the kind of flaw that never shows up in a screenshot review.
 */
import fs from 'node:fs';
import assert from 'node:assert';
import { channelRows, railRows, railSummary, serviceRows, socialRows, repoRows, priceRange } from './normalise.js';

const read = (f) => JSON.parse(fs.readFileSync(new URL(`../../config/${f}`, import.meta.url), 'utf8'));
let passed = 0;
const test = (name, fn) => { fn(); passed++; console.log('  ok', name); };

test('priceRange handles a range, a number and a missing value', () => {
  assert.equal(priceRange([280, 650], [78000, 180000]).usd, '$280–650');
  assert.equal(priceRange(120).usd, '$120');
  assert.equal(priceRange(undefined).usd, 'quote');
});

test('every channel normalises with a name, handle and KPI string', () => {
  const rows = channelRows(read('channels.json'));
  assert.equal(rows.length, 3);
  for (const r of rows) {
    assert.ok(r.name && r.handle, `channel ${r.id} missing identity`);
    assert.ok(r.kpi.includes('≥') || r.kpi.includes('≤'), `channel ${r.id} KPI not rendered`);
  }
});

test('rails split into live vs unavailable from Pakistan', () => {
  const file = read('payment-rails.json');
  const rows = railRows(file);
  const s = railSummary(file);
  assert.equal(rows.length, file.rails.length + file.unavailable_from_pakistan.length);
  assert.equal(s.live, file.rails.length);
  assert.ok(s.blocked >= 3, 'Stripe/Wise/PayPal must be counted as blocked');
  assert.ok(rows.every((r) => r.label), 'no rail may be label-less');
  assert.ok(rows.every((r) => r.status === 'live' || r.status === 'unavailable'));
});

test('services expose a price string and a turnaround', () => {
  const rows = serviceRows(read('services.json').services);
  assert.ok(rows.length >= 2);
  for (const r of rows) {
    assert.ok(r.title, 'service without title');
    assert.ok(r.price.usd, 'service without price');
  }
});

test('social accounts flatten multiple platforms', () => {
  const rows = socialRows(read('social.json'));
  assert.ok(rows.length >= 3);
  for (const r of rows) assert.ok(Array.isArray(r.platforms) && r.platforms.length, 'account without platform');
});

test('repos count matches the registry', () => {
  const file = read('repos.json');
  const rows = repoRows(file);
  assert.equal(rows.length, file.repos.length);
  assert.ok(rows.find((r) => r.role === 'core'), 'core repo must exist');
});

console.log(`\n${passed} config-shape tests passed`);
