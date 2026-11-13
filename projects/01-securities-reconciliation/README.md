# Securities Reconciliation Engine

Which transaction breaks should operations investigate before settlement?

## Why this project

Inspired by securities operations and SQL/Python reconciliation experience. This is an independent demonstration, not an employer deliverable or a claim of production deployment.

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
| `source` | bank, broker, or client |
| `trade_id` | Shared transaction reference |
| `amount` | Settlement amount in one common currency, decimal units |

## Method and business interpretation

Groups all three sources by trade reference. A match requires exactly one row per source and a maximum amount spread of at most 0.01. Missing sources, duplicate references, and mismatched amounts are all retained as exception reasons. Decimal arithmetic avoids binary currency rounding. Negative amounts are allowed for reversal records.

## Limits and next iteration

Assumes one currency and globally unique trade references. Never resolves exceptions or authorizes settlement automatically. Next: composite keys, currency calendars, and an auditable human approval queue.

See `results.json` for the reproducible sample output. Results describe only this synthetic sample; they are not evidence of impact at any employer. Review the assumptions before adapting the analysis to a business decision.
