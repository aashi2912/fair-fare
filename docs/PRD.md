# PRD: Earnings Promise meter (concept)

**Status:** proposal from an independent case study. Not affiliated with Uber.

## Problem
Drivers distrust what the platform keeps, enough to ask riders what they paid. Uber already discloses its fee (receipts, weekly statement) and, in some markets, promises it never makes more than the driver in a week. The information exists but shows up after the decision it should inform.

## Users
- **Primary:** drivers deciding whether to go online or keep driving.
- **Secondary:** riders, through pickup times, if supply responds.

## Goals
1. Drivers can check the weekly promise at decision time.
2. Trust in pay calculation goes up.
3. Online hours per active driver go up without raising rider prices.

## Non-goals
Changing the take rate or the promise itself. New fee types. Markets without the promise (later phase only).

## What ships (v1)
- Weekly meter on the earnings and go-online screens: riders paid, you earned, platform share, promise line.
- Per-trip split on tap.
- Third-party fees (insurance, tolls, local surcharges) on their own line.

## Experiment
8-week geo holdout in two markets that already carry the promise.

| Metric | Role |
|---|---|
| Online hours per active driver | Primary |
| Share of trips with a 10+ minute pickup | Secondary |
| "I understand how my pay is calculated" (survey) | Trust signal |
| Take rate, rider price, pay-related support contacts | Guardrails |

**Prior:** an NYU Stern study of ~47M Lyft rides found driver hours rose 8.6% to 33.3% after Lyft's 70% weekly floor, and waits in busy areas fell about 3% (preliminary, not peer-reviewed).

## Risks
- **A bad week shows the platform near the line.** Intended. Where the promise holds, the meter shows it holding; where it doesn't, the top-up must be real or the meter doesn't ship there.
- **Fee attribution disputes.** Show third-party fees separately with plain-language explainers.
- **Market variance.** Launch only where the promise already exists.

## Roadmap
- **Now (8 weeks):** meter + holdout in two markets.
- **Next:** per-trip split and fee explainers, if trust moves without guardrail damage.
- **Later:** new markets only where the economics hold.
