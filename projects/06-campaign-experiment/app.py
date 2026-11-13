"""Independent portfolio case study. All bundled input data is synthetic."""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

def analyze(rows):
    counts = {}
    for r in rows:
        key = r["variant"]
        if key not in ("control", "treatment") or key in counts:
            raise ValueError("Exactly one row per variant is required")
        n, x = int(r["visitors"]), int(r["conversions"])
        if n <= 0 or x < 0 or x > n:
            raise ValueError("Require 0 <= conversions <= positive visitors")
        counts[key] = (n, x)
    if set(counts) != {"control", "treatment"}:
        raise ValueError("Both variants are required")
    n0,x0 = counts["control"]; n1,x1 = counts["treatment"]
    p0,p1 = x0/n0,x1/n1
    delta = p1-p0
    adequate = min(x0,n0-x0,x1,n1-x1) >= 10
    se = math.sqrt(p0*(1-p0)/n0 + p1*(1-p1)/n1)
    pooled = (x0+x1)/(n0+n1)
    pooled_se = math.sqrt(pooled*(1-pooled)*(1/n0+1/n1))
    p_value = math.erfc(abs(delta/pooled_se)/math.sqrt(2)) if adequate and pooled_se else None
    allocation_z = (n1-(n0+n1)/2)/math.sqrt((n0+n1)*.25)
    srm_p = math.erfc(abs(allocation_z)/math.sqrt(2))
    return {"control_rate": p0, "treatment_rate": p1, "absolute_lift": delta,
        "relative_lift": delta/p0 if p0 else None,
        "difference_ci95": [delta-1.96*se, delta+1.96*se] if adequate else None,
        "two_sided_p_value": p_value, "normal_approximation_adequate": adequate,
        "allocation_p_value": srm_p, "sample_ratio_warning": srm_p < .01,
        "decision": "investigate_allocation" if srm_p < .01 else "positive_signal" if adequate and delta-1.96*se > 0 else "inconclusive"}


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
