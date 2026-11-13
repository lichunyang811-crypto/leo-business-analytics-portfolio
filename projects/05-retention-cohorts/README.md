# Monthly Purchase Retention Cohorts

Do newly acquired customers return in later months?

## Why this project

Inspired by repeat-purchase and retention measurement. This is an independent demonstration, not an employer deliverable or a claim of production deployment.

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
| `order_id` | Unique order identifier |
| `customer_id` | Synthetic customer |
| `order_date` | ISO purchase date |

## Method and business interpretation

Cohort membership uses the first observed purchase month. Each customer counts once per month, regardless of order frequency. Denominator stays at original cohort size. Only months up to the explicit observation cutoff are emitted, so future periods are never filled with zero.

## Limits and next iteration

First observed purchase may not equal first-ever purchase. Monthly purchase retention is not subscription retention. A mid-month cutoff produces a partial final month. Next: acquisition-source cohorts and gross-margin retention.

See `results.json` for the reproducible sample output. Results describe only this synthetic sample; they are not evidence of impact at any employer. Review the assumptions before adapting the analysis to a business decision.
