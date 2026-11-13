# Campaign A/B Test Readout

Does a campaign change conversion enough to justify a follow-up experiment?

## Why this project

Inspired by marketing conversion analysis and experiment participation. This is an independent demonstration, not an employer deliverable or a claim of production deployment.

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
| `variant` | control or treatment |
| `visitors` | Number of independently randomized users |
| `conversions` | Users with at least one conversion |

## Method and business interpretation

Reports absolute and relative conversion lift, an unpooled normal 95% difference interval, and pooled two-sided z-test p-value. Suppresses inference when any success/failure count is below 10. Checks allocation against a preplanned 50/50 split. A positive signal requires the interval lower bound above zero and no allocation warning.

## Limits and next iteration

Assumes independent users, fixed-horizon testing, a single outcome, and 50/50 randomization. Does not support sequential peeking, multiple comparisons, or clustered assignment. Next: power planning and exact inference for sparse events.

See `results.json` for the reproducible sample output. Results describe only this synthetic sample; they are not evidence of impact at any employer. Review the assumptions before adapting the analysis to a business decision.
