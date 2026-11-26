# Fair Fare

*Fair fares for riders, a fair share for drivers.*

**Two drivers, in two countries, asked me what I paid. This is the product case study that question turned into, plus the tool I built along the way.**

Fair Fare tells a New York rider which app to open first for a specific trip (Uber or Lyft), using 51.5 million public trip records. The case study behind it asks a harder question from the driver's side: Uber already discloses its fee, so why do drivers still ask riders what they paid? And what would I build about it as Uber's PM?

**[Read the case study →](https://fair-fare-aashi.vercel.app/)** · [Try the tool](https://fair-fare-aashi.vercel.app/tool) · [Evals](https://fair-fare-aashi.vercel.app/evals) · [Case study (markdown)](docs/CASE_STUDY.md) · [Decision log](docs/DECISION_LOG.md)

---

## The short version

- **The problem.** Drivers in two countries weren't sure they were getting a fair share, and asked what I paid. Uber already shows its fee on trip receipts and in a weekly statement, so this isn't missing data. It's missing trust, about one trip, at the moment a rider names a number.
- **The evidence (NYC TLC data, my analysis).** On matched trips, Uber's premium over Lyft went from +14% (Mar 2025) to −2.3% (Sep 2026). Uber rides with a 10+ minute pickup went from 4.6% to 9.8% (Sep vs Sep); Lyft 4.2% to 5.3%. In NYC, which has a pay floor, drivers keep about three quarters of the base fare on both apps.
- **The proposal.** Uber already has an AI driver assistant. Teach it one new question: "The rider paid $X, I got $Y. Why?", answered only from that trip's breakdown, honest when the split is bad. Holdout test on pay-related support contacts, a driver trust survey and online hours.
- **The prototype** ([why.html](why.html)). 40 synthetic trips. The model writes the words; the app fills every amount from the trip and rejects any number the model typed itself.

## Driver assistant evals (why-v2, Claude Haiku, 40 synthetic trips)

| Design | All checks pass | Every number traceable to the trip |
|---|---:|---:|
| No-AI template | 58% | 100% |
| AI writes its own numbers | 85% | 95% |
| **Shipped: AI writes words, app fills numbers** | **95%** | **98%, and the one break was caught before display** |

The first prompt (why-v1) passed only 60%: it offered a "rider promo" as the reason for quotes nothing explained. Four rules later, v2 reached 95%. Run it yourself: `node evals/run-why.mjs https://your-deploy.vercel.app`.

## The rider tool

Pick a New York trip, or describe it in words, and see which app has usually been cheaper and which more often left riders waiting. The only AI is the trip parser:

| Set | Route accuracy | Refusals | No false precision | Invalid ids |
|---|---:|---:|---:|---:|
| Golden (40), Claude | 100% | 100% | 100% | 0 |
| Golden (40), keyword baseline | 29% | 100% | 100% | 0 |
| Held-out stress (30), Claude | 95% | 100% | 100% | 0 |
| Held-out stress (30), keyword baseline | 14% | 100% | 33% | 0 |

The stress set was written after the prompt was frozen: typos, texting shorthand, decoy times, multi-stop trips, places outside NYC, and questions that aren't trips. Known miss: "Yankee Stadium" maps to a neighboring zone. Next step is `parse-v2` with landmark anchors.

