# Settlement SLA and Bottleneck Analysis

Where does a settlement workflow lose time?

## Why this project

Inspired by KPI definition and operations process improvement. This is an independent demonstration, not an employer deliverable or a claim of production deployment.

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
| `case_id` | Unique workflow case |
| `stage` | Process stage |
| `minutes` | Observed stage duration |
| `sla_minutes` | Allowed duration for this stage |

## Method and business interpretation

Computes stage mean, nearest-rank p90, strict SLA breach rate, and total excess minutes. Ranks the bottleneck by excess minutes, not by raw average duration. Case totals sum observed stages.

## Limits and next iteration

The data has no timestamps, parallel tasks, or staffing levels. Case totals assume sequential stages and cannot reveal missing stages. Next: event-log completeness checks and business-hour clocks.

See `results.json` for the reproducible sample output. Results describe only this synthetic sample; they are not evidence of impact at any employer. Review the assumptions before adapting the analysis to a business decision.
