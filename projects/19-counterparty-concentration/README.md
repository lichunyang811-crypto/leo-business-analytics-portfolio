# Counterparty Exposure Concentration

How concentrated are gross exposures after related entities are grouped?

## Business context

Extends securities operations into descriptive exposure monitoring. This independent portfolio case uses invented records. It is not a former employer's system or a claim of production impact.

## Run and inspect

Python 3.10+; no third-party libraries, accounts, or network calls.

```sh
python3 app.py
python3 app.py --input sample.csv --output results.json
```

Run from this folder, or pass the full path to `app.py` from elsewhere. The default input and output resolve beside the script. `results.json` is the reproducible sample output. The portfolio root test command is `python3 -m unittest discover -s tests -v`.

## Data contract

CSV headers must match the following names and order. Empty inputs, missing columns, malformed row widths, invalid values, and duplicate logical keys fail with exit code 2. Money, where present, is stored in integer minor units to avoid currency rounding errors. No live or private data is included.

| Column | Definition |
| --- | --- |
| `position_id` | Unique synthetic position |
| `counterparty` | Legal entity label |
| `parent_group` | Related-entity group; consistent for each counterparty |
| `currency` | Three uppercase ASCII letters |
| `exposure_cents` | Nonnegative gross exposure in integer minor units |

## Method

Consolidates legal entities by parent group and calculates within-currency shares, sum of squared shares (HHI on a 0–1 scale), and 1/HHI as an effective group count. Groups above the illustrative 35% review threshold are flagged. All-zero currency books return null concentration metrics.

## Acceptance criteria

- Related counterparties must be consolidated before measuring concentration.
- Different currencies cannot contaminate each other.
- Zero-exposure books must not create a false concentration signal.

## Limitations and next iteration

Gross exposure is not expected loss, risk-adjusted capital, or net exposure after collateral. Currencies are intentionally not added without FX conversion. The threshold is a demonstration, not a regulatory limit or investment recommendation. Next: dated FX conversion, collateral and stress scenarios.

Use this case to explain the business question, metric definitions, exception handling, and assumptions in an interview. Any result is about the synthetic fixture only.
