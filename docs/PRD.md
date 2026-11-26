# Pilot plan: explanation vs promise (concept)

**Status:** proposal from an independent case study, with prototypes. Not affiliated with Uber.

## Problem
Drivers aren't sure they get a fair share. Since upfront pricing, rider price and driver pay are set separately per trip; Uber's share swings trip to trip (NYC Sep 2026: over 40% on 18.6% of trips, nothing on 21.4%). Uber shows weekly totals, but US drivers have no ceiling on its cut. Lyft caps its fee at 30% a month.

## Hypotheses
- **H1 (explanation):** explaining a trip against the month reduces perceived unfairness and pay-related support contacts.
- **H2 (promise):** a monthly ceiling on Uber's share raises online hours and lowers churn, especially for lower earners.
- **H3:** the two effects are separable and may add up (as an NYU study of Lyft's promise found).

## Design
Four groups, randomized at driver level, two or three pilot markets (at least one without a pay floor), 12 weeks (three monthly cycles).

| | No promise | Promise |
|---|---|---|
| **No explanation** | Control | Monthly cap, top-up after month end |
| **Explanation** | Assistant explains trip vs month | Both |

Cap level set per market from local data (NYC simulation: 35% costs at most ~0.7% of fees).

## Metrics
| Metric | Role |
|---|---|
| Driver dollars per hour, net of top-ups | Primary |
| Online hours per driver; 90-day churn | Primary |
| "I'm paid fairly" survey; pay-related support contacts | Trust |
| Top-up cost; Uber fee rate; rider price; rider wait times (vs holdout markets) | Cost and guardrails |

## Decision rules
- Explanation works, promise adds little: ship the assistant.
- Promise works, explanation adds little: ship the promise where cost < value of extra hours.
- Both beat either: ship together.
- Nothing moves: it's pay level, not fairness; next test pay for long pickups and traffic.

## Risks
Fees raised elsewhere to fund the promise; changed trip acceptance; spillover within markets; NYC-only evidence.
