# Basketball Shot Profile Analytics

Which shot zones combine efficiency and enough attempts to merit attention?

## Why this project

Connects basketball interest with explainable sports analytics. This is an independent demonstration, not an employer deliverable or a claim of production deployment.

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
| `shot_id` | Unique shot |
| `player` | Synthetic player |
| `zone` | rim, midrange, or three |
| `made` | Binary result 0/1 |

## Method and business interpretation

Computes field-goal rate, effective field-goal rate, and points per attempt by player and zone. Uses Wilson intervals for shooting accuracy so 0-for-N and N-for-N samples do not misleadingly have zero uncertainty. Flags groups under 30 attempts.

## Limits and next iteration

Excludes free throws, turnovers, defense, shot difficulty, and possessions. Points per attempt is not points per possession or causal coaching advice. Next: opponent and game-context stratification.

See `results.json` for the reproducible sample output. Results describe only this synthetic sample; they are not evidence of impact at any employer. Review the assumptions before adapting the analysis to a business decision.
