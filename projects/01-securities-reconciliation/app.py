"""Independent portfolio case study. All bundled input data is synthetic."""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from decimal import Decimal

def analyze(rows, tolerance=Decimal("0.01")):
    if tolerance < 0:
        raise ValueError("Tolerance must be nonnegative")
    expected = {"bank", "broker", "client"}
    trades = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["source"] not in expected or not r["trade_id"].strip():
            raise ValueError("Unknown source or blank trade_id")
        amount = Decimal(r["amount"])
        if not amount.is_finite():
            raise ValueError("Amount must be finite")
        trades[r["trade_id"]][r["source"]].append(amount)
    exceptions, matched = [], 0
    for key, sources in sorted(trades.items()):
        reasons = []
        missing = sorted(expected - sources.keys())
        duplicate = sorted(s for s, values in sources.items() if len(values) > 1)
        if missing:
            reasons.append("missing_source")
        if duplicate:
            reasons.append("duplicate_reference")
        amounts = [v for values in sources.values() for v in values]
        if max(amounts) - min(amounts) > tolerance:
            reasons.append("amount_mismatch")
        if reasons:
            exceptions.append({"trade_id": key, "reasons": reasons, "missing": missing, "duplicates": duplicate})
        else:
            matched += 1
    return {"trade_count": len(trades), "matched": matched, "exceptions": exceptions,
            "match_rate": matched / len(trades) if trades else None}


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
