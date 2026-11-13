"""Independent portfolio case study. All bundled input data is synthetic."""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

def analyze(rows, as_of=date(2026,10,31)):
    members, seen = [], set()
    for r in rows:
        key = r["customer_id"]
        if not key or key in seen:
            raise ValueError("Customer ids must be nonempty and unique")
        seen.add(key)
        recency = (as_of - date.fromisoformat(r["last_purchase"])).days
        frequency, monetary = int(r["orders"]), float(r["spend"])
        if recency < 0 or frequency < 0 or not math.isfinite(monetary) or monetary < 0:
            raise ValueError("Future date or negative/nonfinite customer measure")
        r_score = 3 if recency <= 30 else 2 if recency <= 90 else 1
        f_score = 3 if frequency >= 10 else 2 if frequency >= 3 else 1
        m_score = 3 if monetary >= 1000 else 2 if monetary >= 300 else 1
        segment = ("champions" if r_score == 3 and f_score == 3 and m_score == 3 else
                   "at_risk_high_value" if r_score == 1 and m_score == 3 else
                   "recent" if r_score == 3 else "nurture")
        members.append({"customer_id": key, "recency_days": recency, "rfm": [r_score,f_score,m_score], "segment": segment})
    return {"as_of": as_of.isoformat(), "segment_counts": dict(Counter(m["segment"] for m in members)), "customers": members}


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
