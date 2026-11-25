# Evals: the trip parser

The only AI in the tool turns a typed trip into `{from, to, band, weekend}`. `eval.html` scores the exact prompt the tool uses (`parse.js`, `parse-v1`) against a no-AI keyword baseline.

- **Golden set** (`../cases.json`, 40): written with the prompt. Catches regressions.
- **Held-out stress set** (`../stress.json`, 30): written after the prompt was frozen; never used for tuning.

Metrics: route accuracy, slang/landmark/typo accuracy, refusal accuracy (no route invented when there's no trip), no false precision (empty side for a borough-only or out-of-NYC place), time band, day type, all fields, invalid zone ids.

Saved results: `../report.json`. Live runs work on the claude.ai version of `eval.html`.
