/**
 * Vercel Serverless Function: trip parser (the only AI in Which App Wins).
 *
 * GET  -> {ready}: lets the page show the "Describe your trip" box only when a key is set.
 * POST {q} -> {text}: the model's raw JSON reply; the browser validates it with WA.parseReply.
 *
 * The prompt is built here from the user's text, never sent from the browser, so this
 * endpoint can't be used as a general-purpose LLM. Same guards as blind-spot and vibe-route:
 * origin lock, per-IP rate limit, small cache.
 */
import { originAllowed, rateLimited, cacheGet, cacheSet, hash, resolveKey, resolveModel } from "../lib/llmGuard.js";
import { prompt, VERSION } from "../lib/prompt.js";
import zones from "../lib/zones.js";

export default async function handler(req, res) {
  if (req.method === "GET") return res.status(200).json({ ready: Boolean(resolveKey()), version: VERSION });
  if (req.method !== "POST") return res.status(405).json({ error: "method_not_allowed" });
  if (!originAllowed(req)) return res.status(403).json({ error: "forbidden_origin" });
  if (rateLimited(req)) return res.status(429).json({ error: "rate_limited" });

  const q = String((req.body && req.body.q) || "").trim().slice(0, 200);
  if (!q) return res.status(400).json({ error: "empty" });

  const key = "p:" + VERSION + ":" + hash(q.toLowerCase());
  const hit = cacheGet(key);
  if (hit !== undefined) return res.status(200).json({ text: hit, cached: true });

  const apiKey = resolveKey();
  if (!apiKey) return res.status(503).json({ error: "no_key" });

  try {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-api-key": apiKey, "anthropic-version": "2023-06-01" },
      body: JSON.stringify({
        model: resolveModel(),
        max_tokens: 120,
        temperature: 0,
        messages: [{ role: "user", content: prompt(zones, q) }],
      }),
    });
    if (!r.ok) return res.status(502).json({ error: "upstream_" + r.status });
    const data = await r.json();
    const text = (data.content || []).map((c) => c.text || "").join("");
    cacheSet(key, text);
    return res.status(200).json({ text });
  } catch (e) {
    return res.status(502).json({ error: "upstream_error" });
  }
}
