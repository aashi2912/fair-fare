# Two drivers asked me what I paid. Here's what I'd build as Uber's PM.

*Aashi Thakkar · Product, AI & Strategy Leader · November 2026 · Independent project, not affiliated with Uber or Lyft*

## Summary
The information exists. It just isn't trusted where it matters. Uber already shows drivers its fee per trip and weekly, and already has an AI driver assistant. Drivers in two countries still asked me what I paid. My proposal: teach Uber Assistant one new question, "the rider paid $X, I got $Y, why?", answered only from that trip's breakdown. I built it and evaluated it.

## The moment
I open Lyft first. For my trips, it usually feels cheaper. One night I took an Uber anyway. Near the end, my driver asked: "Can I ask how much you paid?" He wasn't sure he was getting a fair share of what riders pay. Months later, in another country, a different driver had the same doubt and asked me the same question. Cities are left out on purpose.

## The data (NYC TLC public trip records, my analysis)
Matched trips only: same pickup zone, dropoff zone, hour and day type; prices from quick pickups (driver on scene within 5 minutes).

| Finding | Number | Caveat |
|---|---|---|
| Uber's premium over Lyft on identical trips | +14.0% (Mar 2025) → −2.3% (Sep 2026); Uber pricier in 11 of the 12 months to Sep 2026 | Base fare before tolls, taxes, fees, tips, promos. One month below zero isn't a trend. |
| Trips with a 10+ minute pickup | Uber 4.6% → 9.8%; Lyft 4.2% → 5.3% (Sep 2025 vs Sep 2026) | Completed trips only. Cause unknown. |
| Driver pay ÷ base fare, Sep 2026 | Uber 77.9%, Lyft 75.9% | NYC has a per-trip pay floor; doesn't generalize. |
| Platform share of rider payments, elsewhere | Uber: about 21%. Estimates: 29% median in London (Oxford); over 50% in some US cities (Columbia, 3 drivers) | Contested. Uber attributes the gap to insurance and third-party fees. |

## The insight
Uber defines its service fee as what the rider paid minus what the driver earned, excluding tips, tolls and certain fees and taxes. Its weekly statements (since 2022) show what customers paid and the week's service fee, and Uber UK says this is in the driver app. The gap is timing: the doubt is about one trip, in the moment, after a rider names a number that may include a tip or reflect a platform-paid discount. Uber's UK general manager has named that comparison as the trap.

## The proposal
See [PRD.md](PRD.md). A new intent in Uber Assistant, grounded only in the trip ledger. The model writes the words, never the numbers: it uses placeholders, the app fills every amount and rejects anything the model typed. It explains a quote only with a listed tip or discount, states high fees plainly, and admits missing lines. Holdout in two markets; primary metric pay-related support contacts per 1,000 trips.

## The prototype and evals
40 synthetic trips (everyday, airport, rider discount, tip in quote, high fee, missing line, unexplained quote). Shipped design: 95% of trips pass every check; the one rule break (an unknown placeholder) was caught and replaced by the template, so no unchecked number reached a driver. An AI writing its own numbers: 85%, with 2 figures not traceable to the trip. No-AI template: 58%. Prompt v1 scored 60% before four rules were added.

The rider tool (which app has been cheaper on a New York route) stays as a data explorer.

## Limits
One city with a pay floor. Promotions and chosen ride product aren't visible. The wait-time rise has no established cause and I don't tie it to driver sentiment. The Lyft study is preliminary. Two drivers are why I looked, not evidence.

## Sources
- [NYC TLC trip record data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) · [TLC driver pay rates](https://www.nyc.gov/site/tlc/about/driver-pay-rates.page)
- [Uber Under the Hood: Uber's share of driver earnings](https://medium.com/uber-under-the-hood/understanding-ubers-share-of-driver-earnings-899d5eb733bd)
- [Uber: service fee, explained](https://uber.com/us/en/drive/driver-app/service-fee) · [Uber Colombia service fee page](https://www.uber.com/co/en/drive/driver-app/service-fee/)
- [Binns et al., Oxford, FAccT 2025](https://arxiv.org/html/2506.15278v1)
- [Len Sherman, Columbia](https://len-sherman.medium.com/ubers-long-and-winding-road-to-50-take-rates-1aaf4a574ae0)
- [Lyft driver earnings commitment](https://www.lyft.com/blog/posts/lyft-expands-driver-earnings-commitment-nationwide)
- [Li, Liu, Sundararajan, NYU Stern (2026)](https://arxiv.org/pdf/2602.08955v2)
