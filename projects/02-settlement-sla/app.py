"""Independent portfolio case study. All bundled input data is synthetic."""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

def percentile(values, q):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(q * len(ordered)) - 1)]

def analyze(rows):
    groups, totals, seen = defaultdict(list), defaultdict(float), set()
    for r in rows:
        key = (r["case_id"], r["stage"])
        if not all(key) or key in seen:
            raise ValueError("Blank or duplicate case/stage")
        seen.add(key)
        duration, sla = float(r["minutes"]), float(r["sla_minutes"])
        if not all(math.isfinite(v) and v >= 0 for v in [duration, sla]):
            raise ValueError("Durations must be finite and nonnegative")
        groups[r["stage"]].append((duration, sla))
        totals[r["case_id"]] += duration
    stages = []
    for name, items in sorted(groups.items()):
        durations = [v for v, _ in items]
        stages.append({"stage": name, "observations": len(items),
            "mean_minutes": sum(durations) / len(items), "p90_minutes": percentile(durations, .9),
            "breach_rate": sum(v > sla for v, sla in items) / len(items),
            "excess_minutes": sum(max(0, v - sla) for v, sla in items)})
    return {"stages": stages, "case_count": len(totals),
            "largest_excess_stage": max(stages, key=lambda s: s["excess_minutes"])["stage"] if stages else None,
            "mean_observed_case_minutes": sum(totals.values()) / len(totals) if totals else None}


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
