# CRM Identity Quality Audit

Which member records can be linked exactly and which need manual review?

## Why this project

Inspired by member matching and CRM data synchronization. This is an independent demonstration, not an employer deliverable or a claim of production deployment.

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
| `record_id` | Unique source record |
| `email` | Synthetic email, may be blank |
| `phone` | Synthetic phone, may be blank |

## Method and business interpretation

Trims and lowercases email, strips phone punctuation, flags missing or malformed identifiers, and groups exact matches. Shared identifiers with conflicting secondary identifiers are explicitly marked for review. Never merges records, even when exact identifiers agree.

## Limits and next iteration

No fuzzy matching, international dialing normalization, ownership verification, or consent resolution. Lowercasing the email local part is a documented simplifying assumption. Next: source priority and reviewer decisions with an audit trail.

See `results.json` for the reproducible sample output. Results describe only this synthetic sample; they are not evidence of impact at any employer. Review the assumptions before adapting the analysis to a business decision.
