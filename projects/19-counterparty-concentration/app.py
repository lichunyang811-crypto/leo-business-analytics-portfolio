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

FIELDS = ['position_id', 'counterparty', 'parent_group', 'currency', 'exposure_cents']

def analyze(rows, review_threshold=.35):
    threshold = number(review_threshold, "review_threshold")
    if threshold > 1:
        raise ValueError("Review threshold must be <= 1")
    groups, parents, seen = defaultdict(Counter), {}, set()
    for r in rows:
        unique(seen, identifier(r["position_id"], "position_id"))
        counterparty = identifier(r["counterparty"], "counterparty")
        parent = identifier(r["parent_group"], "parent_group")
        if counterparty in parents and parents[counterparty] != parent:
            raise ValueError("Counterparty has conflicting parent groups")
        parents[counterparty] = parent
        currency = r["currency"]
        if len(currency) != 3 or not currency.isascii() or not currency.isalpha() or not currency.isupper():
            raise ValueError("Currency must be three uppercase ASCII letters")
        groups[currency][parent] += whole(r["exposure_cents"], "exposure_cents")
    output = []
    for currency, exposures in sorted(groups.items()):
        total = sum(exposures.values())
        shares = [(name, amount, amount / total if total else None) for name, amount in exposures.items()]
        hhi = sum(share**2 for _, _, share in shares) if total else None
        output.append({"currency": currency, "total_exposure_cents": total,
            "hhi_fraction": hhi, "effective_group_count": 1 / hhi if hhi else None,
            "groups": [{"parent_group": name, "exposure_cents": amount, "share": share,
                        "review_flag": share > threshold if share is not None else False}
                       for name, amount, share in sorted(shares, key=lambda x: (-x[1], x[0]))]})
    return {"illustrative_review_threshold": threshold, "currency_profiles": output}


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
