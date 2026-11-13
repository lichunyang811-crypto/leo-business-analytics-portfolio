# Automation Opportunity Scorecard

Which workflow changes deserve a pilot, and which fail control gates?

## Why this project

Inspired by workflow migration evaluation, operational risk, and UAT. This is an independent demonstration, not an employer deliverable or a claim of production deployment.

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
| `workflow` | Unique workflow name |
| `daily_cases` | Daily case volume |
| `minutes_saved` | Estimated minutes saved per case |
| `build_hours` | Implementation effort |
| `risk` | Residual risk 1–5 |
| `approval_control` | 1 if human approval is preserved, else 0 |

## Method and business interpretation

Explicitly gates out workflows without preserved approval or with residual risk above 3. Ranks eligible ideas by daily hours saved / build hours / risk; zero build hours uses a one-hour floor. Payback uses workdays and reports null for zero benefit.

## Limits and next iteration

The score is a transparent heuristic, not a validated risk model or realized ROI. Excludes maintenance, adoption, and recurring control costs. Next: scenario ranges and pilot acceptance criteria.

See `results.json` for the reproducible sample output. Results describe only this synthetic sample; they are not evidence of impact at any employer. Review the assumptions before adapting the analysis to a business decision.
