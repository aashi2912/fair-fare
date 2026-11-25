# Two drivers asked me what I paid. Here's what I'd build as Uber's PM.

*Aashi Thakkar · AI Product Manager · November 2026 · Independent project, not affiliated with Uber or Lyft*

## Summary
The information exists. It just isn't trusted where it matters. Uber already discloses its fee and, in some markets, promises it never makes more than the driver in a week. Drivers in two countries still asked me what I paid. My proposal: make that existing promise checkable at the moment drivers decide, and test whether trust moves driver hours and pickup waits.

## The moment
I open Lyft first. For my trips, it usually feels cheaper. One night I took an Uber anyway. Near the end, my driver told me he wasn't happy with what he was earning: Uber takes too much of the fare, and drivers aren't getting what they deserve. Then he asked: "Can I ask how much you paid?" Months later, in another country, a different driver told me the same thing and asked me the same question. Cities are left out on purpose.

## The data (NYC TLC public trip records, my analysis)
Matched trips only: same pickup zone, dropoff zone, hour and day type; prices from quick pickups (driver on scene within 5 minutes).

| Finding | Number | Caveat |
|---|---|---|
| Uber's premium over Lyft on identical trips | +14.0% (Mar 2025) → −2.3% (Sep 2026); Uber pricier in 11 of the 12 months to Sep 2026 | Base fare before tolls, taxes, fees, tips, promos. One month below zero isn't a trend. |
| Trips with a 10+ minute pickup | Uber 4.6% → 9.8%; Lyft 4.2% → 5.3% (Sep 2025 vs Sep 2026) | Completed trips only. Cause unknown. |
| Driver pay ÷ base fare, Sep 2026 | Uber 77.9%, Lyft 75.9% | NYC has a per-trip pay floor; doesn't generalize. |
| Platform share of rider payments, elsewhere | Uber: about 21%. Estimates: 29% median in London (Oxford); over 50% in some US cities (Columbia, 3 drivers) | Contested. Uber attributes the gap to insurance and third-party fees. |

## The insight
Uber's driver pages say its fee is what the rider paid minus what the driver earned, visible on trip receipts and a weekly statement. "Drivers can't see the numbers" would be wrong. The gap is timing and trust: the weekly statement answers after the week; the driver in my car was deciding in the moment.

Lyft promises drivers at least 70% of rider fares each week, after external fees, and tops up any shortfall. An NYU Stern study of about 47M Lyft rides found drivers logged 8.6% to 33.3% more hours afterward and waits in busy areas fell about 3%. Preliminary, so it's my hypothesis, not my proof.

## The proposal: Earnings Promise meter
See [PRD.md](PRD.md). Weekly meter on the earnings and go-online screens, per-trip split on tap, third-party fees on their own line. 8-week geo holdout in markets that already carry the promise. Primary metric: online hours per active driver. Secondary: share of 10+ minute pickups. Trust signal: driver survey. Guardrails: take rate, rider price, pay-related support contacts.

## The tool
Fair Fare tells riders which app to open first on a given trip. One LLM call parses free text into zones and time; everything else is lookups over 51.5M real rides. On a held-out stress set: 95% route accuracy vs 14% for a keyword baseline, 100% refusal accuracy, zero invented zone ids across 70 cases. See [../evals](../evals/README.md).

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
