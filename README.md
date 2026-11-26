# Fair Fare

*Fair fares for riders, a fair share for drivers.*

**Multiple drivers, in more than one country, asked me what I paid. This is the product case study that question turned into, plus the tool I built along the way.**

Fair Fare tells a New York rider which app to open first for a specific trip (Uber or Lyft), using 51.5 million public trip records. The case study behind it asks a harder question from the driver's side: Uber already discloses its fee, so why do drivers still ask riders what they paid? And what would I build about it as Uber's PM?

**[Read the case study →](https://fair-fare-aashi.vercel.app/)** · [Try the tool](https://fair-fare-aashi.vercel.app/tool) · [Evals](https://fair-fare-aashi.vercel.app/evals) · [Case study (markdown)](docs/CASE_STUDY.md) · [Decision log](docs/DECISION_LOG.md)

---

## The short version

- **The problem.** Multiple drivers, in more than one country, weren't sure they were getting a fair share, and asked what I paid. Since upfront pricing (2022), rider prices and driver pay are set separately for every trip, and Uber's share varies trip to trip by design.
- **The gap.** Nationally, Uber charges more and keeps more per trip than Lyft (Gridwise Q3 2026: $24.30 vs $19.76 average fare; $5.45 vs $3.30 platform fee). In NYC (my analysis, Sep 2026), Uber kept over 40% on 18.6% of trips and nothing on 21.4%. Lyft caps its fee at 30% a month; Uber doesn't in the US.
- **Three ideas tested.** A weekly meter (dropped: Uber already ships weekly statements). An AI that explains each trip (built, kept as one arm). A monthly cap on Uber's cut (simulated, kept as one arm).
- **The proposal.** A four-group pilot: explanation, promise, both, neither. Primary metrics: driver dollars per hour and online hours. Decision rules for each outcome. See [docs/PRD.md](docs/PRD.md).
- **Prototypes.** [why.html](why.html) (explanation arm) and [promise.html](promise.html) (promise cost on 15.1M NYC trips).

**All trip-level data is one city's public records.** With Uber's data the conclusions could change, which is why the proposal is an experiment.

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

