"""Independent business analytics case study; bundled data is entirely synthetic."""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


def whole(value, label, minimum=0):
    text = str(value).strip()
    if not text or not text.isascii() or not text.isdigit():
        raise ValueError(f"{label} must be an integer >= {minimum}")
    result = int(text)
    if result < minimum:
        raise ValueError(f"{label} must be >= {minimum}")
    return result


def number(value, label, minimum=0):
    result = float(value)
    if not math.isfinite(result) or result < minimum:
        raise ValueError(f"{label} must be finite and >= {minimum}")
    return result


def identifier(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} cannot be blank")
    return value.strip()


def unique(seen, key):
    if key in seen:
        raise ValueError(f"Duplicate key: {key}")
    seen.add(key)

FIELDS = ['customer_id', 'month', 'mrr_cents']

def month_key(text):
    parsed = date.fromisoformat(text + "-01")
    if parsed.strftime("%Y-%m") != text:
        raise ValueError("Month must use YYYY-MM")
    return parsed.year * 12 + parsed.month - 1


def analyze(rows):
    snapshots, seen = defaultdict(dict), set()
    for r in rows:
        customer = identifier(r["customer_id"], "customer_id")
        month_key(r["month"])
        unique(seen, (customer, r["month"]))
        snapshots[r["month"]][customer] = whole(r["mrr_cents"], "mrr_cents")
    months = sorted(snapshots)
    if len(months) < 2:
        raise ValueError("At least two monthly snapshots are required")
    customers = set().union(*(set(s) for s in snapshots.values()))
    if any(set(snapshots[m]) != customers for m in months):
        raise ValueError("Missing customer/month snapshot; use explicit zeros for inactive accounts")
    if any(month_key(b) - month_key(a) != 1 for a, b in zip(months, months[1:])):
        raise ValueError("Snapshots must cover consecutive months")
    ever_paid = {c for c, v in snapshots[months[0]].items() if v > 0}
    bridges = []
    for previous, current in zip(months, months[1:]):
        before, after = snapshots[previous], snapshots[current]
        moves = Counter({k: 0 for k in ("new", "reactivation", "expansion", "contraction", "churn")})
        for customer in sorted(customers):
            old, new = before[customer], after[customer]
            if old == 0 and new > 0:
                moves["reactivation" if customer in ever_paid else "new"] += new
            elif old > 0 and new == 0:
                moves["churn"] += old
            elif new > old:
                moves["expansion"] += new - old
            elif new < old:
                moves["contraction"] += old - new
            if new > 0:
                ever_paid.add(customer)
        start, end = sum(before.values()), sum(after.values())
        retained = start + moves["expansion"] - moves["contraction"] - moves["churn"]
        bridges.append({"month": current, "opening_mrr_cents": start, "closing_mrr_cents": end,
            "movements_cents": dict(moves), "net_revenue_retention": retained / start if start else None,
            "bridge_difference_cents": end - (retained + moves["new"] + moves["reactivation"])})
    return {"baseline_month": months[0], "customer_count": len(customers), "bridges": bridges}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("sample.csv"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("results.json"))
    args = parser.parse_args()
    try:
        with args.input.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != FIELDS:
                raise ValueError("CSV headers must match: " + ",".join(FIELDS))
            rows = list(reader)
        if not rows:
            raise ValueError("Input must contain at least one data row")
        if any(None in r or any(v is None for v in r.values()) for r in rows):
            raise ValueError("CSV row width does not match the header")
        result = analyze(rows)
        payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(payload, end="")
    except (ValueError, KeyError, TypeError, OSError, ArithmeticError) as error:
        parser.exit(2, f"Invalid input: {error}\n")

if __name__ == "__main__":
    main()
