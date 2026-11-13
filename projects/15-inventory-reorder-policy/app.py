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

FIELDS = ['sku', 'daily_mean', 'daily_std', 'lead_days', 'review_days', 'safety_z', 'on_hand', 'on_order', 'backorders', 'pack_size']

def analyze(rows):
    output, seen = [], set()
    for r in rows:
        sku = identifier(r["sku"], "sku")
        unique(seen, sku)
        mean, std, lead, review, z = [number(r[k], k) for k in ("daily_mean", "daily_std", "lead_days", "review_days", "safety_z")]
        if review == 0:
            raise ValueError("review_days must be positive")
        hand, ordered, backlog = [whole(r[k], k) for k in ("on_hand", "on_order", "backorders")]
        pack = whole(r["pack_size"], "pack_size", 1)
        position = hand + ordered - backlog
        reorder = math.ceil(mean * lead + z * std * math.sqrt(lead))
        target = math.ceil(mean * (lead + review) + z * std * math.sqrt(lead + review))
        trigger = position <= reorder
        quantity = math.ceil(max(0, target - position) / pack) * pack if trigger else 0
        output.append({"sku": sku, "inventory_position": position,
            "reorder_point": reorder, "order_up_to_target": target,
            "reorder_trigger": trigger, "suggested_units": quantity,
            "case_count": quantity // pack, "position_after_order": position + quantity})
    return {"policy": "Continuous threshold review with a lead-plus-review coverage target", "items": output}


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
