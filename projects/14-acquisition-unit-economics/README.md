# Acquisition Channel Contribution

Does a high-revenue acquisition channel still contribute after refunds and variable costs?

## Business context

Combines retail campaign analytics with commercial decision support. This independent portfolio case uses invented records. It is not a former employer's system or a claim of production impact.

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
| `channel` | Unique acquisition channel for a single comparable period |
| `revenue_cents` | Gross order revenue before refunds |
| `refund_cents` | Refunded revenue, no greater than gross revenue |
| `cogs_cents` | Net cost of goods sold, already adjusted for returned inventory |
| `fulfillment_cents` | Net fulfillment and payment costs |
| `ad_spend_cents` | Attributed acquisition spend |
| `new_customers` | Distinct attributed first-time customers |

## Method

Net revenue = gross revenue − refunds. Contribution before acquisition subtracts net COGS and variable fulfillment costs; contribution after acquisition also subtracts ad spend. Gross-revenue ROAS and CAC remain separate measures. Zero denominators return null, not infinity. Break-even ad spend is the nonnegative portion of pre-acquisition contribution.

## Acceptance criteria

- Refunds and costs cannot be dropped from contribution.
- Zero-spend and zero-customer channels must remain interpretable.
- Negative contribution is visible even when gross ROAS exceeds one.

## Limitations and next iteration

All rows must cover the same period, currency, and attribution rules. No fixed overhead, multi-touch attribution, repeat-customer lifetime value, or incrementality is included. Next: gross-margin cohorts and attribution sensitivity.

Use this case to explain the business question, metric definitions, exception handling, and assumptions in an interview. Any result is about the synthetic fixture only.
