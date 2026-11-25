// Shared trip parser: the live tool (app.html), the eval harness (eval.html) and the
// hosted endpoint (api/parse.js, via lib/prompt.js) all use this same prompt, so the
// eval measures exactly what users get. Bump VERSION in both files together.
window.WA = (() => {
  const VERSION = 'parse-v1';
  const BAND_HELP = 'Time bands: 0 = 4 to 7am, 1 = 7 to 10am, 2 = 10am to 4pm, 3 = 4 to 7pm, 4 = 7pm to midnight, 5 = midnight to 4am.';
  const prompt = (zones, q) => `Map a New York City ride description to NYC taxi zones. Zones (id|name|borough):
${zones.map(z => `${z[0]}|${z[1]}|${z[2]}`).join('\n')}

${BAND_HELP}
Description: ${JSON.stringify(q)}
Reply with only JSON: {"from": zone id or null, "to": zone id or null, "band": 0-5 or null, "weekend": true, false or null}. Pick the single best-matching zone for each place (for an airport, the airport zone; for a landmark, the zone it sits in). Use null when the description gives no clue.`;
  // Turn the model's reply into a checked result. Zone ids not in the list become 'invalid'
  // (counted as hallucinations by the eval); anything unparseable becomes null.
  const parseReply = (text, zById) => {
    const m = String(text || '').match(/\{[\s\S]*\}/);
    if (!m) return null;
    let j; try { j = JSON.parse(m[0]); } catch (e) { return null; }
    const id = v => (v === null || v === undefined || v === '') ? null : (zById.has(Number(v)) ? Number(v) : 'invalid');
    return {
      from: id(j.from), to: id(j.to),
      band: Number.isInteger(j.band) && j.band >= 0 && j.band <= 5 ? j.band : null,
      weekend: j.weekend === true ? true : j.weekend === false ? false : null
    };
  };
  // Returns a function (query, zones) => {text}, or null when no model is reachable.
  // On claude.ai it uses the artifact's Claude access; when hosted (Vercel) it calls
  // /api/parse, which builds the same prompt server-side so the key never reaches the browser.
  const sampler = async () => {
    if (window.claude && window.claude.use) {
      try { const s = await window.claude.use('sample'); if (s) return (q, zones) => s(prompt(zones, q), {modelTier: 'quick'}); } catch (e) {}
      return null;
    }
    try {
      const r = await fetch('/api/parse', {method: 'GET'});
      const j = r.ok ? await r.json() : null;
      if (!j || !j.ready) return null;
    } catch (e) { return null; }
    return async q => {
      const r = await fetch('/api/parse', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({q})});
      const j = await r.json().catch(() => ({}));
      if (!r.ok) { const e = new Error(j.error || 'failed'); e.code = j.error; throw e; }
      return {text: j.text};
    };
  };
  return {VERSION, prompt, parseReply, sampler};
})();
