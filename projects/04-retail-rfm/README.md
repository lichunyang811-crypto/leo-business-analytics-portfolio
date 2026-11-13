# Retail Customer Lifecycle Segmentation

Which customers should a CRM team retain, reactivate, or develop?

## Why this project

Inspired by retail CRM lifecycle segmentation and member analytics. This is an independent demonstration, not an employer deliverable or a claim of production deployment.

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
| `customer_id` | Unique synthetic member |
| `last_purchase` | ISO date, on/before 2026-10-31 |
| `orders` | Lifetime nonnegative integer purchase count |
| `spend` | Lifetime nonnegative spend |

## Method and business interpretation

Uses a frozen 2026-10-31 analysis date and explicit business thresholds. Recency: ≤30/≤90/>90 days. Frequency: ≥10/≥3/<3 orders. Monetary: ≥1000/≥300/<300. Assigns four explainable lifecycle segments; it does not infer campaign lift.

## Limits and next iteration

Thresholds are illustrative and need validation against actual buying cycles, margin, and consent. No campaign is sent. Next: holdout testing and channel-level eligibility.

See `results.json` for the reproducible sample output. Results describe only this synthetic sample; they are not evidence of impact at any employer. Review the assumptions before adapting the analysis to a business decision.
