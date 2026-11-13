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

FIELDS = ['event_id', 'batch_id', 'currency', 'event_type', 'amount_cents']

def analyze(rows):
    groups, seen = defaultdict(Counter), set()
    for r in rows:
        unique(seen, identifier(r["event_id"], "event_id"))
        batch = identifier(r["batch_id"], "batch_id")
        currency = r["currency"]
        if len(currency) != 3 or not currency.isascii() or not currency.isalpha() or not currency.isupper():
            raise ValueError("Currency must be three uppercase ASCII letters")
        kind = r["event_type"]
        if kind not in ("capture", "refund", "fee", "payout"):
            raise ValueError("Unknown ledger event")
        amount = whole(r["amount_cents"], "amount_cents")
        groups[(batch, currency)][kind] += amount
        groups[(batch, currency)][kind + "_events"] += 1
    output = []
    for (batch, currency), totals in sorted(groups.items()):
        expected = totals["capture"] - totals["refund"] - totals["fee"]
        actual = totals["payout"]
        reasons = []
        if totals["payout_events"] == 0:
            reasons.append("missing_payout")
        if expected < 0:
            reasons.append("net_debit_requires_review")
        if actual != expected:
            reasons.append("amount_difference")
        output.append({"batch_id": batch, "currency": currency,
            "captured_cents": totals["capture"], "refund_cents": totals["refund"],
            "fee_cents": totals["fee"], "expected_payout_cents": expected,
            "actual_payout_cents": actual, "difference_cents": actual - expected,
            "status": "review" if reasons else "matched", "reasons": reasons})
    return {"batches": output, "review_count": sum(b["status"] == "review" for b in output)}


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
