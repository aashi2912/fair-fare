// Server copy of the prompt in /parse.js. Keep the two identical and bump VERSION together:
// the eval harness scores /parse.js, and this is what the hosted tool sends.
export const VERSION = "parse-v1";
const BAND_HELP = "Time bands: 0 = 4 to 7am, 1 = 7 to 10am, 2 = 10am to 4pm, 3 = 4 to 7pm, 4 = 7pm to midnight, 5 = midnight to 4am.";
export const prompt = (zones, q) => `Map a New York City ride description to NYC taxi zones. Zones (id|name|borough):
${zones.map((z) => `${z[0]}|${z[1]}|${z[2]}`).join("\n")}

${BAND_HELP}
Description: ${JSON.stringify(q)}
Reply with only JSON: {"from": zone id or null, "to": zone id or null, "band": 0-5 or null, "weekend": true, false or null}. Pick the single best-matching zone for each place (for an airport, the airport zone; for a landmark, the zone it sits in). Use null when the description gives no clue.`;
