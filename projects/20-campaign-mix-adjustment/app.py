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

FIELDS = ['segment', 'variant', 'users', 'conversions']

def analyze(rows):
    segments, seen = defaultdict(dict), set()
    for r in rows:
        segment = identifier(r["segment"], "segment")
        variant = r["variant"]
        if variant not in ("control", "treatment"):
            raise ValueError("Variant must be control or treatment")
        unique(seen, (segment, variant))
        users = whole(r["users"], "users", 1)
        conversions = whole(r["conversions"], "conversions")
        if conversions > users:
            raise ValueError("Conversions exceed users")
        segments[segment][variant] = (users, conversions)
    if not segments or any(set(cells) != {"control", "treatment"} for cells in segments.values()):
        raise ValueError("Each segment requires both variants")
    total_users = sum(n for cells in segments.values() for n, _ in cells.values())
    pooled, standardized = {}, {"control": 0.0, "treatment": 0.0}
    detail = []
    for segment, cells in sorted(segments.items()):
        weight = sum(n for n, _ in cells.values()) / total_users
        rates = {v: x / n for v, (n, x) in cells.items()}
        for variant in standardized:
            standardized[variant] += weight * rates[variant]
        detail.append({"segment": segment, "common_weight": weight,
            "control_rate": rates["control"], "treatment_rate": rates["treatment"],
            "difference": rates["treatment"] - rates["control"]})
    for variant in standardized:
        n = sum(cells[variant][0] for cells in segments.values())
        x = sum(cells[variant][1] for cells in segments.values())
        pooled[variant] = x / n
    raw_diff = pooled["treatment"] - pooled["control"]
    adjusted_diff = standardized["treatment"] - standardized["control"]
    return {"segments": detail, "pooled_rates": pooled, "standardized_rates": standardized,
        "pooled_difference": raw_diff, "standardized_difference": adjusted_diff,
        "direction_reversal": raw_diff * adjusted_diff < 0,
        "interpretation": "Descriptive common-mix comparison, not an estimate of causal treatment effect."}


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
