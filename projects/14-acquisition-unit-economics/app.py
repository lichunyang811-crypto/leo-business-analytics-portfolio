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

FIELDS = ['channel', 'revenue_cents', 'refund_cents', 'cogs_cents', 'fulfillment_cents', 'ad_spend_cents', 'new_customers']

def analyze(rows):
    output, seen = [], set()
    for r in rows:
        channel = identifier(r["channel"], "channel")
        unique(seen, channel)
        money = {k: whole(r[k], k) for k in FIELDS if k.endswith("_cents")}
        customers = whole(r["new_customers"], "new_customers")
        if money["refund_cents"] > money["revenue_cents"]:
            raise ValueError("Refunds exceed this cohort's gross revenue")
        net = money["revenue_cents"] - money["refund_cents"]
        before = net - money["cogs_cents"] - money["fulfillment_cents"]
        contribution = before - money["ad_spend_cents"]
        spend = money["ad_spend_cents"]
        output.append({"channel": channel, "net_revenue_cents": net,
            "contribution_before_acquisition_cents": before, "contribution_after_acquisition_cents": contribution,
            "contribution_margin": contribution / net if net else None,
            "gross_revenue_roas": money["revenue_cents"] / spend if spend else None,
            "cac_cents": spend / customers if customers else None,
            "break_even_ad_spend_cents": max(0, before),
            "review": "negative_contribution" if contribution < 0 else "nonnegative_contribution"})
    return {"channels": sorted(output, key=lambda r: (-r["contribution_after_acquisition_cents"], r["channel"])),
        "total_contribution_cents": sum(r["contribution_after_acquisition_cents"] for r in output)}


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
