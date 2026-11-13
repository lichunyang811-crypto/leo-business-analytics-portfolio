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

FIELDS = ['date', 'units']

def predict(history, model):
    if model == "last_value":
        return float(history[-1])
    if model == "seasonal_7":
        return float(history[-7])
    if model == "moving_mean_7":
        return sum(history[-7:]) / 7
    raise ValueError("Unknown forecast model")


def score(actuals, forecasts):
    errors = [abs(a - f) for a, f in zip(actuals, forecasts)]
    return {"mae": sum(errors) / len(errors),
            "wape": sum(errors) / sum(actuals) if sum(actuals) else None}


def analyze(rows):
    observations, seen = [], set()
    for r in rows:
        day = date.fromisoformat(r["date"])
        unique(seen, day)
        observations.append((day, whole(r["units"], "units")))
    observations.sort()
    if len(observations) < 28:
        raise ValueError("At least 28 consecutive days are required")
    if any((b[0] - a[0]).days != 1 for a, b in zip(observations, observations[1:])):
        raise ValueError("Daily series must be contiguous; missing days are not zeros")
    values = [n for _, n in observations]
    validation_start, holdout_start = len(values) - 14, len(values) - 7
    validation = []
    for model in ("last_value", "seasonal_7", "moving_mean_7"):
        estimates = [predict(values[:i], model) for i in range(validation_start, holdout_start)]
        validation.append({"model": model, **score(values[validation_start:holdout_start], estimates)})
    chosen = min(validation, key=lambda item: item["mae"])["model"]
    estimates = [predict(values[:i], chosen) for i in range(holdout_start, len(values))]
    return {"training_days": validation_start, "validation_days": 7, "holdout_days": 7,
        "validation_scores": validation, "selected_model": chosen,
        "holdout_score": score(values[holdout_start:], estimates),
        "holdout_predictions": [{"date": observations[i][0].isoformat(),
                                 "trained_through": observations[i-1][0].isoformat(),
                                 "actual": values[i], "forecast": estimates[i-holdout_start]}
                                for i in range(holdout_start, len(values))]}


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
