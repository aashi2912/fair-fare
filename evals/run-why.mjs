// Runs the "Why did I earn this?" eval against the deployed endpoint and writes report-why.json.
// Usage: node evals/run-why.mjs https://fair-fare-aashi.vercel.app
// Paces requests to stay under the endpoint's per-IP rate limit (40 per 10 minutes).
import fs from 'node:fs';
import trips from '../why/trips.js';
import { VERSION, grade, templateAnswer } from '../why/core.js';
const BASE = process.argv[2] || 'https://fair-fare-aashi.vercel.app';
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function ask(t, variant) {
  for (let attempt = 0; attempt < 4; attempt++) {
    const r = await fetch(BASE + '/api/why', { method: 'POST', headers: { 'Content-Type': 'application/json', Origin: BASE }, body: JSON.stringify({ id: t.id, question: t.question, variant }) });
    const j = await r.json().catch(() => ({}));
    if (r.status === 429) { console.log('rate limited, waiting 10.5 min'); await sleep(630000); continue; }
    if (!r.ok) throw new Error(t.id + ' ' + r.status + ' ' + JSON.stringify(j));
    return j.text;
  }
  throw new Error('gave up ' + t.id);
}
const KEYS = ['faithful', 'states_split', 'quote', 'promo', 'honest_high', 'missing', 'concise', 'all'];
const summarize = rows => Object.fromEntries(KEYS.map(k => { const xs = rows.map(r => r.grade[k]).filter(v => v !== null && v !== undefined); return [k, xs.length ? Math.round(100 * xs.filter(Boolean).length / xs.length) : null]; }).concat([['n', rows.length]]));
const out = { version: VERSION, ts: new Date().toISOString(), base: BASE, variants: {} };
out.variants.template = trips.map(t => ({ id: t.id, kind: t.kind, ...grade(t, 'template', templateAnswer(t)) }));
for (const v of (process.argv[3] || 'placeholders,free').split(',')) {
  const rows = [];
  for (const t of trips) { const raw = await ask(t, v); rows.push({ id: t.id, kind: t.kind, raw, ...grade(t, v, raw) }); process.stdout.write('.'); }
  out.variants[v] = rows; console.log(' ' + v + ' done');
}
out.summary = Object.fromEntries(Object.entries(out.variants).map(([k, rows]) => [k, summarize(rows)]));
out.byKind = Object.fromEntries(Object.entries(out.variants).map(([k, rows]) => [k, Object.fromEntries([...new Set(rows.map(r => r.kind))].map(kind => { const rs = rows.filter(r => r.kind === kind); return [kind, rs.filter(r => r.grade.all).length + '/' + rs.length]; }))]));
fs.writeFileSync(new URL('../report-why.json', import.meta.url), JSON.stringify(out, null, 1));
console.log(JSON.stringify(out.summary, null, 1)); console.log(JSON.stringify(out.byKind, null, 1));
