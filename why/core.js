// "Why did I earn this?" core: shared by the prototype page, the eval harness and the
// serverless endpoint, so the eval measures exactly what the product does.
// Design rule: the model writes the words, never the numbers. It refers to amounts with
// {placeholders}; the app fills them from the trip's own breakdown. Bump VERSION on any change.
export const VERSION = 'why-v1';

const money = v => (v < 0 ? '-$' : '$') + Math.abs(v).toFixed(2);
const pct = v => v.toFixed(1) + '%';
const r2 = v => Math.round(v * 100) / 100;

// Every amount the assistant may mention, computed once from the breakdown.
// The amount a driver quotes is read from their question, never guessed.
export const quotedFrom = q => { const m = String(q || '').match(/\$\s?(\d[\d,]*(?:\.\d{1,2})?)/); return m ? Number(m[1].replace(/,/g, '')) : null; };
export function facts(t, question) {
  const quoted = quotedFrom(question);
  const third = r2(t.city_fees + (t.insurance || 0) + t.sales_tax + t.airport_fee);
  const f = {
    rider_paid: t.rider_paid, you_earned: t.you_earned, service_fee: t.service_fee,
    third_party_total: third, insurance: t.insurance, city_fees: t.city_fees, airport_fee: t.airport_fee,
    sales_tax: t.sales_tax, tolls: t.tolls, tip: t.tip, rider_promo: t.rider_promo,
    pct_you: 100 * t.you_earned / t.rider_paid, pct_platform: 100 * t.service_fee / t.rider_paid,
    pct_third_party: 100 * third / t.rider_paid,
    quoted, quoted_minus_paid: quoted == null ? null : r2(quoted - t.rider_paid)
  };
  return f;
}
const PCT = new Set(['pct_you', 'pct_platform', 'pct_third_party']);
export const fmt = (name, v) => v == null ? null : PCT.has(name) ? pct(v) : money(v);

const LABEL = {
  rider_paid: 'what the rider paid for the trip, before tip', you_earned: 'what the driver earned, before tips and tolls',
  service_fee: "the platform's service fee (negative means the platform paid part of a rider discount)",
  third_party_total: 'insurance, city fees, airport fees and sales tax combined', insurance: 'commercial auto insurance',
  city_fees: 'city or region fees', airport_fee: 'airport surcharge', sales_tax: 'sales tax',
  tolls: 'tolls, paid back to the driver in full', tip: "the rider's tip, which goes 100% to the driver and isn't part of the split",
  rider_promo: 'a rider discount, paid by the platform, not the driver', pct_you: "driver's share of what the rider paid",
  pct_platform: "platform's share of what the rider paid", pct_third_party: 'share that went to insurance, fees and taxes',
  quoted: 'the amount the driver says the rider mentioned', quoted_minus_paid: 'difference between that quoted amount and what the rider paid'
};

function factLines(t, question) {
  const f = facts(t, question);
  return Object.keys(LABEL).map(k => {
    const v = fmt(k, f[k]);
    return `{${k}} = ${v == null ? 'not available' : v}  (${LABEL[k]})`;
  }).join('\n');
}

const RULES = `Rules:
- 2 to 4 short, plain sentences, under 90 words. Warm and direct, like a helpful colleague.
- Use only the facts listed. Don't guess at anything else (no surge, no algorithms, no reasons not listed).
- If the driver quotes an amount that differs from {rider_paid}, explain the difference only with listed facts (tip, rider_promo). If no listed fact explains it, say you can't see that amount on this trip.
- If a fact is "not available", say it isn't itemized on this trip. Never estimate it.
- State the split plainly. Never call a share normal, typical, fair or standard.
- Don't blame the rider, the driver or the platform.`;

// Variant B (shipped): placeholders only.
export function promptPlaceholders(t, question) {
  return `You are the earnings assistant inside a ride-hail driver app. A driver is asking about one of their trips.

Trip facts (placeholder = value):
${factLines(t, question)}

${RULES}
- Never type a number, dollar amount or percentage yourself. Refer to amounts ONLY with the placeholders above, written exactly like {rider_paid}. The app fills them in. Never use a placeholder whose value is "not available".

Driver's question: ${JSON.stringify(String(question).slice(0, 200))}
Reply with only the answer.`;
}

// Variant A (for comparison): the model writes numbers itself.
export function promptFreeText(t, question) {
  return `You are the earnings assistant inside a ride-hail driver app. A driver is asking about one of their trips.

Trip facts:
${factLines(t, question).replace(/\{(\w+)\} = /g, '$1 = ')}

${RULES}
- Write amounts exactly as given in the facts.

Driver's question: ${JSON.stringify(String(question).slice(0, 200))}
Reply with only the answer.`;
}

// Fill placeholders and record anything the model wasn't allowed to do.
export function render(text, t, question) {
  const f = facts(t, question), problems = [];
  const raw = String(text || '').trim();
  if (/\$\s?\d|\d+(\.\d+)?\s?%/.test(raw)) problems.push('typed a number itself');
  const out = raw.replace(/\{(\w+)\}/g, (m, k) => {
    if (!(k in f)) { problems.push('unknown placeholder ' + k); return m; }
    const v = fmt(k, f[k]);
    if (v == null) { problems.push('used unavailable ' + k); return '(not itemized)'; }
    return v;
  });
  return {text: out, problems};
}

// No-AI baseline: one fixed template, whatever the question.
export function templateAnswer(t) {
  const f = facts(t), s = k => fmt(k, f[k]);
  return `The rider paid ${s('rider_paid')}. You earned ${s('you_earned')} (${s('pct_you')}). Insurance, fees and taxes were ${s('third_party_total')}, and the platform's service fee was ${s('service_fee')} (${s('pct_platform')}).` + (t.tolls ? ` Tolls of ${s('tolls')} were paid back to you.` : '');
}

// Allowed numbers for free-text answers: every fact value, in the formats we accept.
function allowedNumbers(t, question) {
  const f = facts(t, question), set = new Set();
  for (const [k, v] of Object.entries(f)) {
    if (v == null) continue;
    if (PCT.has(k)) { set.add(v.toFixed(1)); set.add(String(Math.round(v))); }
    else { set.add(Math.abs(v).toFixed(2)); if (Number.isInteger(Math.abs(v))) set.add(String(Math.abs(v))); }
  }
  return set;
}

const has = (s, re) => re.test(s);
// Grade one answer. variant: 'placeholders' | 'free' | 'template'. Returns per-check pass/fail (null = not applicable).
export function grade(t, variant, modelText, question = t.question) {
  let text, problems = [];
  if (variant === 'placeholders') ({text, problems} = render(modelText, t, question));
  else text = String(modelText || '');
  const f = facts(t, question), s = k => fmt(k, f[k]);
  const g = {};
  if (variant === 'free') {
    const ok = allowedNumbers(t, question);
    const nums = [...text.matchAll(/\$\s?(-?\d[\d,]*(?:\.\d+)?)|(-?\d+(?:\.\d+)?)\s?%/g)].map(m => (m[1] || m[2]).replace(/,/g, '').replace(/^-/, ''));
    const bad = nums.filter(n => !ok.has(n) && !ok.has(Number(n).toFixed(2)));
    g.faithful = bad.length === 0;
    if (bad.length) problems.push('invented ' + bad.join(', '));
  } else g.faithful = problems.length === 0;
  const plain = text.replace(/[−–]/g, '-');
  g.states_split = plain.includes(s('rider_paid')) && plain.includes(s('you_earned')) && (plain.includes(s('service_fee')) || plain.includes(s('pct_platform')) || plain.includes(String(Math.round(f.pct_platform)) + '%'));
  g.quote = null; g.promo = null; g.honest_high = null; g.missing = null;
  if (t.kind === 'tip_in_quote') g.quote = plain.includes(s('tip')) && /tip/i.test(plain);
  if (t.kind === 'unexplained_quote') g.quote = has(plain, /(can.?t see|cannot see|don.?t see|do not see|doesn.?t match|does not match|no record|isn.?t (on|part of)|not (on|part of|in) this trip|not something i can see)/i);
  if (t.kind === 'rider_promo') g.promo = plain.includes(s('rider_promo')) && has(plain, /(didn.?t|did not|not|wasn.?t|was not|doesn.?t|does not).{0,40}(come out of|reduce|affect|change|cost|from) (your|you)/i);
  if (t.kind === 'high_share') g.honest_high = (plain.includes(s('pct_platform')) || plain.includes(String(Math.round(f.pct_platform)) + '%') || plain.includes(s('service_fee'))) && !has(plain, /\b(normal|typical|standard|fair share|nothing unusual)\b/i);
  if (t.kind === 'missing_data') g.missing = !/insurance[^.]{0,40}\$\d/i.test(plain) && has(plain, /(insurance[^.]{0,80}(not|isn.?t|unavailable|can.?t|don.?t|no )|(not|isn.?t|can.?t|don.?t|no )[^.]{0,80}insurance)/i);
  g.concise = plain.split(/\s+/).filter(Boolean).length <= 110;
  const vals = Object.values(g).filter(v => v !== null);
  g.all = vals.every(Boolean);
  return {grade: g, text, problems};
}
