# Payment Settlement Ledger

Do processor payouts reconcile to captured sales, refunds, and fees?

## Business context

Extends operations reconciliation into payment processing and merchant analytics. This independent portfolio case uses invented records. It is not a former employer's system or a claim of production impact.

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
| `event_id` | Unique ledger event |
| `batch_id` | Processor settlement batch |
| `currency` | Three uppercase ASCII letters; batches are separated by currency |
| `event_type` | capture, refund, fee, or payout |
| `amount_cents` | Nonnegative integer minor units |

## Method

Within each batch/currency, expected payout = captures − refunds − fees. Actual payout can consist of multiple unique payout events. A zero net amount without a payout record is still flagged as missing. Negative net batches require review. Differences retain their sign: actual minus expected.

## Acceptance criteria

- Every currency is reconciled independently.
- Duplicated events fail before totals are produced.
- Every unexplained difference enters the review list, including refund-only batches.

## Limitations and next iteration

Assumes supplied batch assignments are correct and all input currencies use the same documented minor-unit convention. Does not model reserves, FX, chargebacks, or timing differences. Never initiates payments. Next: settlement calendars and explained adjustment types.

Use this case to explain the business question, metric definitions, exception handling, and assumptions in an interview. Any result is about the synthetic fixture only.
