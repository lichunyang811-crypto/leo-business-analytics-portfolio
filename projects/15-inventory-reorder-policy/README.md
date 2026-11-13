# Inventory Reorder Policy Simulator

When does inventory position justify a replenishment review, and how does case packing change the quantity?

## Business context

Extends retail operations into inventory and service-level assumptions. This independent portfolio case uses invented records. It is not a former employer's system or a claim of production impact.

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
| `sku` | Unique synthetic SKU |
| `daily_mean` | Nonnegative estimated daily unit demand |
| `daily_std` | Nonnegative daily demand standard deviation |
| `lead_days` | Fixed supplier lead time, nonnegative days |
| `review_days` | Positive days of additional coverage in the order-up-to target |
| `safety_z` | Nonnegative safety multiplier, not a guaranteed service level |
| `on_hand` | Nonnegative stock units |
| `on_order` | Nonnegative incoming units |
| `backorders` | Nonnegative committed but unfilled units |
| `pack_size` | Positive integer supplier case size |

## Method

Inventory position = on hand + on order − backorders. Reorder point = ceil(mean × lead + z × std × sqrt(lead)). Trigger at or below the threshold. The target uses lead + review days, and order quantity rounds up to a whole supplier case. No order is placed by this program.

## Acceptance criteria

- Backorders reduce available inventory position.
- Recommended quantity is a nonnegative multiple of pack size.
- Above-threshold items receive no order; zero-demand items never invent demand.

## Limitations and next iteration

Assumes independent daily demand and deterministic lead time; normal-approximation safety stock can be unsuitable for intermittent demand. On-order arrival timing, shelf life, minimum order values, and capacity are omitted. Next: historical stockout backtests and lead-time uncertainty.

Use this case to explain the business question, metric definitions, exception handling, and assumptions in an interview. Any result is about the synthetic fixture only.
