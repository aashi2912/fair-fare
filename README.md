# Fair Fare

*Fair fares for riders, a fair share for drivers.*

**Two drivers, in two countries, asked me what I paid. This is the product case study that question turned into, plus the tool I built along the way.**

Fair Fare tells a New York rider which app to open first for a specific trip (Uber or Lyft), using 51.5 million public trip records. The case study behind it asks a harder question from the driver's side: Uber already discloses its fee, so why do drivers still ask riders what they paid? And what would I build about it as Uber's PM?

**[Read the case study →](https://fair-fare-aashi.vercel.app/)** · [Try the tool](https://fair-fare-aashi.vercel.app/tool) · [Evals](https://fair-fare-aashi.vercel.app/evals) · [Case study (markdown)](docs/CASE_STUDY.md) · [Decision log](docs/DECISION_LOG.md)

---

## The short version

- **The problem.** Drivers told me Uber takes too much, then asked what I paid. Uber's own pages show the fee on receipts and weekly statements, so this isn't missing data. It's missing trust, at the moment drivers decide whether to drive.
- **The evidence (NYC TLC data, my analysis).** On matched trips, Uber's premium over Lyft went from +14% (Mar 2025) to −2.3% (Sep 2026). Uber rides with a 10+ minute pickup went from 4.6% to 9.8% (Sep vs Sep); Lyft 4.2% to 5.3%. In NYC, which has a pay floor, drivers keep about three quarters of the base fare on both apps (77.9% vs 75.9%).
- **The proposal.** An Earnings Promise meter: make the weekly promise Uber already makes in some markets checkable on the go-online and earnings screens. Test it with an 8-week geo holdout on driver hours, long pickups, a driver trust survey, and guardrails.
- **The tool.** Pick a trip, or describe it in words. An LLM parses the text into taxi zones and a time band; everything after that is plain lookups over real past rides.

## The AI, scoped honestly

The only model call is the trip parser (`parse.js`, prompt version `parse-v1`). It returns JSON that the browser validates: any zone id that doesn't exist is counted as a hallucination, anything unparseable is dropped.

| Set | Route accuracy | Refusals | No false precision | Invalid ids |
|---|---:|---:|---:|---:|
| Golden (40), Claude | 100% | 100% | 100% | 0 |
| Golden (40), keyword baseline | 29% | 100% | 100% | 0 |
| Held-out stress (30), Claude | 95% | 100% | 100% | 0 |
| Held-out stress (30), keyword baseline | 14% | 100% | 33% | 0 |

The stress set was written after the prompt was frozen: typos, texting shorthand, decoy times, multi-stop trips, places outside NYC, and questions that aren't trips. Known miss: "Yankee Stadium" maps to a neighboring zone. Next step is `parse-v2` with landmark anchors.

## Run it

Static site plus one serverless function. No build step.

```
vercel dev            # or any static server for the pages
```

Environment (Vercel → Settings → Environment Variables):

| Variable | Required | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | for the "Describe your trip" box | Without it, the box hides and the tool still works with pickers |
| `LLM_MODEL` | no | Defaults to `claude-haiku-4-5-20251001` |
| `ALLOWED_ORIGIN` | no | Extra allowed origins for a custom domain |

`api/parse.js` builds the prompt server-side from the user's text, so the endpoint can't be used as a general LLM. It has an origin lock, a per-IP rate limit and a small cache (`lib/llmGuard.js`).

## Repo map

```
index.html      case study
app.html        the tool
eval.html       eval harness (live on claude.ai, saved report when hosted)
parse.js        shared prompt + reply validator (browser)
lib/prompt.js   same prompt for the server; keep in sync with parse.js
api/parse.js    serverless trip parser
data.json       route-level aggregates, Jul to Sep 2026
cases.json      golden set   ·  stress.json  held-out stress set  ·  report.json  saved runs
analysis/       DuckDB scripts over the raw TLC parquet files
docs/           case study, decision log, PRD
```

## Data and limits

Source: [NYC TLC high-volume for-hire trip records](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) (HV0003 = Uber, HV0005 = Lyft), non-shared trips. Fares are base passenger fare before tolls, taxes, fees, tips and promos. One city, with a driver pay floor. Promotions and the ride product chosen aren't visible.

Independent project. Not affiliated with or endorsed by Uber or Lyft.

Built by [Aashi Thakkar](https://www.linkedin.com/in/aashithakkar29) · [aashithakkar.com](https://aashithakkar.com)
