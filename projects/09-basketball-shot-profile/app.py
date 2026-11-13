"""Independent portfolio case study. All bundled input data is synthetic."""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

def analyze(rows):
    groups, seen = defaultdict(list), set()
    for r in rows:
        if not r["shot_id"] or r["shot_id"] in seen or not r["player"] or r["zone"] not in ("rim","midrange","three") or r["made"] not in ("0","1"):
            raise ValueError("Duplicate shot or invalid shot field")
        seen.add(r["shot_id"])
        groups[(r["player"],r["zone"])].append(int(r["made"]))
    result = []
    for (player,zone), shots in sorted(groups.items()):
        n, made = len(shots), sum(shots)
        p, z = made/n, 1.96
        center = (p+z*z/(2*n))/(1+z*z/n)
        radius = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
        value = 3 if zone == "three" else 2
        result.append({"player": player, "zone": zone, "attempts": n, "fg_pct": p,
            "effective_fg_pct": made*value/(2*n), "points_per_attempt": made*value/n,
            "fg_wilson_ci95": [center-radius,center+radius], "small_sample": n<30})
    return {"shot_profiles": result}


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
