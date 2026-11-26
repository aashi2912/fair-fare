/**
 * Vercel Serverless Function: "Why did I earn this?" assistant (prototype).
 *
 * GET  -> {ready, version}
 * POST {id, question, variant} -> {text}: the model's raw answer. The browser fills the
 * {placeholders} from the trip's own breakdown and rejects anything the model typed itself.
 *
 * Trips are the synthetic set in /why/trips.js, looked up by id: the browser can't send
 * its own numbers, and the prompt is fixed, so this can't be used as a general LLM.
 */
import { originAllowed, rateLimited, cacheGet, cacheSet, hash, resolveKey, resolveModel } from "../lib/llmGuard.js";
import { VERSION, promptPlaceholders, promptFreeText } from "../why/core.js";
import trips from "../why/trips.js";

export default async function handler(req, res) {
  if (req.method === "GET") return res.status(200).json({ ready: Boolean(resolveKey()), version: VERSION });
  if (req.method !== "POST") return res.status(405).json({ error: "method_not_allowed" });
  if (!originAllowed(req)) return res.status(403).json({ error: "forbidden_origin" });

  const { id, question, variant } = req.body || {};
  const trip = trips.find((t) => t.id === id);
  if (!trip) return res.status(400).json({ error: "unknown_trip" });
  const q = String(question || "").trim().slice(0, 200);
  if (!q) return res.status(400).json({ error: "empty" });
  const v = variant === "free" ? "free" : "placeholders";

  const key = "w:" + VERSION + ":" + v + ":" + id + ":" + hash(q.toLowerCase());
  const hit = cacheGet(key);
  if (hit !== undefined) return res.status(200).json({ text: hit, cached: true });
  if (rateLimited(req)) return res.status(429).json({ error: "rate_limited" });

  const apiKey = resolveKey();
  if (!apiKey) return res.status(503).json({ error: "no_key" });
  const prompt = v === "free" ? promptFreeText(trip, q) : promptPlaceholders(trip, q);
  try {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-api-key": apiKey, "anthropic-version": "2023-06-01" },
      body: JSON.stringify({ model: resolveModel(), max_tokens: 300, temperature: 0, messages: [{ role: "user", content: prompt }] }),
    });
    if (!r.ok) return res.status(502).json({ error: "upstream_" + r.status });
    const data = await r.json();
    const text = (data.content || []).map((c) => c.text || "").join("").trim();
    cacheSet(key, text);
    return res.status(200).json({ text });
  } catch (e) {
    return res.status(502).json({ error: "upstream_error" });
  }
}
