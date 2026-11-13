# Golf Round Performance Review

Which parts of a round deserve focused practice?

## Why this project

Connects long-term golf interest with practical performance measurement. This is an independent demonstration, not an employer deliverable or a claim of production deployment.

## Run

Python 3.10+; no third-party dependencies. From this folder:

```sh
python3 app.py
python3 app.py --input sample.csv --output results.json
```

The command reads a CSV and writes deterministic, machine-readable JSON. Invalid or empty input returns a nonzero exit code. Run the portfolio tests from the repository root with `python3 -m unittest discover -s tests -v`.

## Input contract

All rows in `sample.csv` were generated for this portfolio. No employer, customer, or personal records are included.

| Column | Meaning |
| --- | --- |
| `round_id` | Synthetic round |
| `hole` | Hole number 1–18 |
| `par` | Hole par 3–5 |
| `strokes` | Positive total strokes including putts |
| `putts` | Nonnegative putt count |
| `gir` | Green in regulation 0/1 |

## Method and business interpretation

Reports score relative to par, putts per hole, GIR rate, three-putt rate, and par-or-better rate after a missed GIR. Keeps partial rounds explicitly marked; denominator is observed holes. The missed-GIR measure is null when no greens were missed.

## Limits and next iteration

No course rating, slope, shot location, or comparable baseline is provided, so this does not calculate an official handicap or strokes gained. Next: shot-level logs and course-adjusted comparisons.

See `results.json` for the reproducible sample output. Results describe only this synthetic sample; they are not evidence of impact at any employer. Review the assumptions before adapting the analysis to a business decision.
