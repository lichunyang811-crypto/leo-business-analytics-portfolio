# UAT Requirements Traceability

Which unmet requirements block a release recommendation?

## Business context

Connects requirements gathering, test execution, defect retesting, and release discussions. This independent portfolio case uses invented records. It is not a former employer's system or a claim of production impact.

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
| `requirement_id` | Requirement identifier; can repeat for multiple mapped tests |
| `priority` | critical or normal, consistent within a requirement |
| `test_id` | Mapped test id; blank only for an unmapped requirement |
| `status` | pass, fail, blocked, or not_run; blank test requires not_run |

## Method

A requirement passes only if at least one test is mapped and every mapped test passes. Coverage measures mapped requirements separately from passed requirements. Shared tests count once in execution totals, and conflicting statuses are rejected. Any unresolved requirement causes a hold; critical blockers are listed explicitly. The program never releases software.

## Acceptance criteria

- Unmapped and unexecuted requirements cannot appear ready.
- Shared tests cannot inflate execution totals.
- Even one failing critical requirement must block the recommendation.

## Limitations and next iteration

This is one release snapshot, not a history of test runs. Business signoff, severity, environment, and evidence attachments are not modeled. Next: latest-run selection and immutable links to test evidence.

Use this case to explain the business question, metric definitions, exception handling, and assumptions in an interview. Any result is about the synthetic fixture only.
