# CRM Contact Eligibility Audit

Which members meet a campaign’s consent and seven-day contact rules?

Evaluate a single hypothetical channel at the end of **2026-10-31**. Latest consent wins; an opt-out wins a same-day tie because event times are unavailable. Missing consent is ineligible. At least seven calendar days must have elapsed since a send. Member B qualifies exactly at the boundary; A is still cooling down. C’s future opt-in is ignored. This is an illustrative business rule and does not send messages or establish legal compliance.

## Reproduce

Run `python3 app.py` in this folder. Use `--input sample.csv --output results.json` to select files. The Python standard library loads the CSV into a fresh SQLite database, validates it against the schema in `app.py`, and runs [the query](analysis.sql). See [the input](sample.csv) and [the full output](results.json). All records and findings are synthetic.
