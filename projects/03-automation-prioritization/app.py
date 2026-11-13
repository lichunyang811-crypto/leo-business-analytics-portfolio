"""Independent portfolio case study. All bundled input data is synthetic."""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

def analyze(rows):
    results, seen = [], set()
    for r in rows:
        name = r["workflow"]
        if not name or name in seen:
            raise ValueError("Workflow names must be nonempty and unique")
        seen.add(name)
        cases, saved, hours = [float(r[k]) for k in ("daily_cases", "minutes_saved", "build_hours")]
        risk = int(r["risk"])
        if not all(math.isfinite(v) and v >= 0 for v in [cases, saved, hours]) or risk not in range(1,6) or r["approval_control"] not in ("0", "1"):
            raise ValueError("Invalid estimates or control inputs")
        daily_hours = cases * saved / 60
        gate = r["approval_control"] == "1" and risk <= 3
        payback = hours / daily_hours if daily_hours else None
        results.append({"workflow": name, "daily_hours_saved": daily_hours,
            "payback_workdays": payback, "control_gate_passed": gate,
            "recommendation": "pilot" if gate and daily_hours > 0 else "hold",
            "priority_score": daily_hours / (hours or 1) / risk if gate else 0})
    return {"ranked_workflows": sorted(results, key=lambda x: (-x["priority_score"], x["workflow"])),
            "assumption": "Estimates only; one-time build effort divided by daily gross time saved."}


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
