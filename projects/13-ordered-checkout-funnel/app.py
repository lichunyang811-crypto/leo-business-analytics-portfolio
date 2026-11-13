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

FIELDS = ['event_id', 'session_id', 'event', 'timestamp']

STAGES = ("visit", "cart", "checkout", "purchase")


def analyze(rows, window_minutes=30):
    window = number(window_minutes, "window_minutes")
    sessions, seen = defaultdict(list), set()
    for r in rows:
        key = identifier(r["event_id"], "event_id")
        unique(seen, key)
        session = identifier(r["session_id"], "session_id")
        if r["event"] not in STAGES:
            raise ValueError("Unknown funnel event")
        stamp = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError("Timestamp must include timezone")
        sessions[session].append((stamp.astimezone(timezone.utc), key, r["event"]))
    counts, detail = [0] * len(STAGES), []
    for session, events in sorted(sessions.items()):
        level, entered, previous = 0, None, None
        for stamp, _, event in sorted(events):
            if level == len(STAGES):
                break
            if event != STAGES[level]:
                continue
            if entered is not None and (stamp - entered).total_seconds() > window * 60:
                continue
            if previous is not None and stamp <= previous:
                continue
            entered = entered or stamp
            previous = stamp
            counts[level] += 1
            level += 1
        detail.append({"session_id": session, "steps_completed": level,
            "last_completed_step": STAGES[level - 1] if level else None})
    return {"window_minutes": window, "sessions_observed": len(sessions),
        "excluded_without_entry": sum(s["steps_completed"] == 0 for s in detail),
        "funnel": [{"step": stage, "sessions": counts[i],
                    "conversion_from_entry": counts[i] / counts[0] if counts[0] else None,
                    "conversion_from_previous": counts[i] / counts[i-1] if i and counts[i-1] else None}
                   for i, stage in enumerate(STAGES)], "session_progress": detail}


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
