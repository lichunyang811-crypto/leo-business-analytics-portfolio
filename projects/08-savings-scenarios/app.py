"""Independent portfolio case study. All bundled input data is synthetic."""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

def analyze(rows):
    output, seen = [], set()
    for r in rows:
        name = r["scenario"]
        if not name or name in seen:
            raise ValueError("Scenario names must be nonempty and unique")
        seen.add(name)
        initial, contribution, rate, fee, inflation = [float(r[k]) for k in ("initial","monthly_contribution","annual_return","annual_fee","inflation")]
        years = int(r["years"])
        if not all(math.isfinite(v) for v in [initial,contribution,rate,fee,inflation]) or min(initial,contribution)<0 or rate<=-1 or inflation<=-1 or not 0<=fee<1 or not 1<=years<=100:
            raise ValueError("Invalid scenario range")
        monthly_factor = ((1+rate)*(1-fee))**(1/12)
        balance, schedule = initial, []
        for month in range(1,years*12+1):
            balance = balance*monthly_factor + contribution
            if month%12 == 0:
                schedule.append({"year": month//12, "nominal_balance": round(balance,2),
                    "real_balance": round(balance/(1+inflation)**(month/12),2),
                    "contributions_to_date": initial+contribution*month})
        output.append({"scenario": name, "annual_schedule": schedule})
    return {"scenarios": output, "notice": "Hypothetical constant-return education model; not a forecast or investment advice."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("sample.csv"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("results.json"))
    args = parser.parse_args()
    try:
        with args.input.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        if not rows:
            raise ValueError("Input must contain at least one data row")
        result = analyze(rows)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, OSError, ArithmeticError) as error:
        parser.exit(2, f"Invalid input: {error}\n")

if __name__ == "__main__":
    main()
