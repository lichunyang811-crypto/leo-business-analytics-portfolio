# Ordered Checkout Funnel

At which step do sessions stop progressing through checkout?

## Business context

Extends marketing conversion analysis into product event analytics. This independent portfolio case uses invented records. It is not a former employer's system or a claim of production impact.

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
| `event_id` | Unique event id |
| `session_id` | Precomputed session identifier |
| `event` | visit, cart, checkout, or purchase |
| `timestamp` | ISO timestamp with explicit timezone |

## Method

Counts one ordered path per session, starting at the first visit. Events must have strictly increasing timestamps and complete within an inclusive 30-minute window from that visit. Repeated events do not inflate counts. An earlier cart before the visit is ignored, but a later valid cart can advance the session. Timestamp offsets normalize to UTC.

## Acceptance criteria

- Counts never increase at later stages.
- Out-of-order, duplicate, late, and missing-entry events cannot create false conversions.
- Equivalent timezone representations produce the same result.

## Limitations and next iteration

Existing session identifiers are assumed correct. Equal-time steps do not establish order; the first visit is not restarted after expiry. Ignores cross-device identity and checkout variants. Next: instrumentation QA and device/channel segmentation.

Use this case to explain the business question, metric definitions, exception handling, and assumptions in an interview. Any result is about the synthetic fixture only.
