# Financial Education Savings Simulator

How do contributions, compounding, fees, and inflation change a hypothetical savings path?

## Why this project

Inspired by the financial education field project. This is an independent demonstration, not an employer deliverable or a claim of production deployment.

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
| `scenario` | Unique scenario label |
| `initial` | Initial balance |
| `monthly_contribution` | End-of-month contribution |
| `annual_return` | Effective annual gross return as decimal |
| `annual_fee` | Annual proportional fee as decimal |
| `inflation` | Effective annual inflation as decimal |
| `years` | Integer horizon, 1–100 |

## Method and business interpretation

Converts effective annual return and fee into a monthly growth factor: ((1+return)×(1−fee))^(1/12). Adds contributions at each month-end, then discounts nominal balances by cumulative inflation. Keeps internal full precision and rounds annual displayed balances.

## Limits and next iteration

All rates are hypothetical inputs, not current market data. Ignores taxes, volatility, liquidity constraints, and changing contributions. Next: stochastic scenarios and accessible learning checks; do not interpret fixed returns as guaranteed outcomes.

See `results.json` for the reproducible sample output. Results describe only this synthetic sample; they are not evidence of impact at any employer. Review the assumptions before adapting the analysis to a business decision.
