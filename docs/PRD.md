# PRD: "Why did I earn this?" in Uber Assistant (concept)

**Status:** proposal and working prototype from an independent case study. Not affiliated with Uber.

## Problem
Drivers distrust the split enough to ask riders what they paid. Uber already shows its service fee per trip and in a weekly statement, and Uber Assistant already answers earnings questions. The doubt shows up about one trip, in the moment, often after a rider names a number that includes a tip or reflects a platform-paid discount.

## Users
- **Primary:** drivers who just finished a trip and want to understand its split.
- **Secondary:** Uber support, which absorbs pay questions today.

## Goals
1. A driver can ask "the rider paid $X, I got $Y, why?" and get a correct, plain answer from that trip's ledger.
2. Fewer pay-related support contacts.
3. Higher trust in pay calculation, without changing pricing.

## Non-goals
Changing the take rate. New fee types. Arguing that a split is fair.

## Design
- New intent in Uber Assistant, reachable from trip details and by voice.
- Grounded only in the trip ledger: rider paid, driver earnings, insurance, city and airport fees, taxes, tolls, rider discounts, service fee, tip.
- **The model writes words, never numbers.** It uses placeholders; the app fills amounts and rejects any typed number or unknown placeholder, falling back to a fixed template.
- Explains a quoted amount only with a listed tip or discount; otherwise says it can't see that amount.
- States high fees plainly; never calls a split "normal." Says when a line isn't itemized.

## Launch gate
100% of shown numbers traceable to the ledger, and at least 95% of eval cases passing every check, on a real-ledger eval set.

## Experiment
Holdout in two markets that already itemize trips.

| Metric | Role |
|---|---|
| Pay-related support contacts per 1,000 trips | Primary |
| "I understand how my pay is calculated" (survey) | Trust signal |
| Online hours per active driver | Secondary |
| Answer accuracy, follow-up rate, take rate | Guardrails |

## Risks
- **The honest answer is a high fee.** Intended: it says so. Accurate bad news keeps more trust than rumor, and the questioned trips show where pricing feels unfair.
- **Ledger edge cases** (adjustments, multi-stop, split fares). Extend the eval set before launch.
- **Over-reliance on the model.** Numbers never come from it, by design.

## Roadmap
- **Now (one quarter):** the intent, two markets, eval gate, holdout.
- **Next:** proactive explanation on trips where a tip or discount makes the rider's number differ.
- **Later:** a plain-language weekly story on top of the weekly statement.
