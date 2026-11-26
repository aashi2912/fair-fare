// Re-grades saved answers with the current grader (no new model calls).
import fs from 'node:fs';
import trips from '../why/trips.js';
import { grade, templateAnswer } from '../why/core.js';
const file = process.argv[2];
const rep = JSON.parse(fs.readFileSync(file, 'utf8'));
const KEYS = ['faithful', 'states_split', 'quote', 'promo', 'honest_high', 'missing', 'concise', 'all'];
for (const [v, rows] of Object.entries(rep.variants)) for (const row of rows) {
  const t = trips.find(x => x.id === row.id);
  Object.assign(row, grade(t, v, v === 'template' ? templateAnswer(t) : row.raw));
}
rep.summary = Object.fromEntries(Object.entries(rep.variants).map(([k, rows]) => [k, Object.fromEntries(KEYS.map(c => { const xs = rows.map(r => r.grade[c]).filter(x => x !== null); return [c, xs.length ? Math.round(100 * xs.filter(Boolean).length / xs.length) : null]; }).concat([['n', rows.length]]))]));
rep.byKind = Object.fromEntries(Object.entries(rep.variants).map(([k, rows]) => [k, Object.fromEntries([...new Set(rows.map(r => r.kind))].map(kind => { const rs = rows.filter(r => r.kind === kind); return [kind, rs.filter(r => r.grade.all).length + '/' + rs.length]; }))]));
rep.regraded = new Date().toISOString();
fs.writeFileSync(file, JSON.stringify(rep, null, 1));
console.log(file, JSON.stringify(Object.fromEntries(Object.entries(rep.summary).map(([k, v]) => [k, v.all + '% all, ' + v.faithful + '% faithful']))));
