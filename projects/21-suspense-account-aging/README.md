# Suspense Account Aging

Which unmatched cash postings still need investigation at month end?

The review date is **2026-10-31**. Within one currency and one investigation case, debits increase the signed balance and credits decrease it. Zero-net cases leave the queue. Case A remains open at +2,000 cents for 30 days; its November clearing entry cannot change the October report. Case B is a credit balance and remains visible. Age measures the life of the case, not individual unpaid lots. If a case can close and reopen, allocate a fresh case ID.

## Reproduce

Run `python3 app.py` in this folder. Use `--input sample.csv --output results.json` to select files. The Python standard library loads the CSV into a fresh SQLite database, validates it against the schema in `app.py`, and runs [the query](analysis.sql). See [the input](sample.csv) and [the full output](results.json). All records and findings are synthetic.
