# Retail Basket Affinity

Which product pairs occur together more often than their individual frequencies imply?

The unit is a basket, not a receipt line. Deduplicate repeated products, keep singleton baskets in the denominator, and emit each unordered pair once. A minimum of two co-occurring baskets is a demonstration threshold. Cap and tee appear together in two of six baskets: cap → tee confidence is 100%, tee → cap is 66.7%, and lift is 2.0. This suggests a merchandising hypothesis, not a causal effect; validate on a larger sample before testing a bundle.

## Reproduce

Run `python3 app.py` in this folder. Use `--input sample.csv --output results.json` to select files. The Python standard library loads the CSV into a fresh SQLite database, validates it against the schema in `app.py`, and runs [the query](analysis.sql). See [the input](sample.csv) and [the full output](results.json). All records and findings are synthetic.
