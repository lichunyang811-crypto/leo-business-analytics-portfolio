"""Independent portfolio case study. All bundled input data is synthetic."""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

def month_index(value):
    d = date.fromisoformat(value)
    return d.year * 12 + d.month - 1

def analyze(rows, cutoff="2026-10-31"):
    end = date.fromisoformat(cutoff)
    members, seen = defaultdict(set), set()
    for r in rows:
        if not r["order_id"] or r["order_id"] in seen or not r["customer_id"]:
            raise ValueError("Duplicate/blank order or blank customer")
        seen.add(r["order_id"])
        if date.fromisoformat(r["order_date"]) > end:
            raise ValueError("Order after observation cutoff")
        members[r["customer_id"]].add(month_index(r["order_date"]))
    cohorts = defaultdict(list)
    for months in members.values():
        cohorts[min(months)].append(months)
    result = []
    for start, customers in sorted(cohorts.items()):
        periods = []
        for offset in range(month_index(cutoff) - start + 1):
            active = sum(start + offset in months for months in customers)
            periods.append({"month_offset": offset, "active_customers": active, "retention": active / len(customers)})
        result.append({"cohort": f"{start//12:04}-{start%12+1:02}", "size": len(customers), "periods": periods})
    return {"cutoff": cutoff, "cohorts": result}


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
