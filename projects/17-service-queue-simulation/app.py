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

FIELDS = ['ticket_id', 'arrival_minute', 'service_minutes', 'wait_sla_minutes']

import heapq


def simulate(jobs, workers):
    workers = whole(workers, "workers", 1)
    available = [(0.0, worker) for worker in range(workers)]
    heapq.heapify(available)
    schedule = []
    for arrival, ticket, duration, sla in sorted(jobs):
        free_at, worker = heapq.heappop(available)
        start = max(arrival, free_at)
        finish = start + duration
        wait = start - arrival
        heapq.heappush(available, (finish, worker))
        schedule.append({"ticket_id": ticket, "worker": worker + 1, "arrival": arrival,
            "start": start, "finish": finish, "wait": wait, "sla_breached": wait > sla})
    end = max(s["finish"] for s in schedule)
    waits = sorted(s["wait"] for s in schedule)
    return {"workers": workers, "mean_wait_minutes": sum(waits) / len(waits),
        "p90_wait_minutes": waits[math.ceil(.9 * len(waits)) - 1],
        "wait_sla_breach_rate": sum(s["sla_breached"] for s in schedule) / len(schedule),
        "busy_fraction_from_time_zero": sum(j[2] for j in jobs) / (workers * end),
        "last_completion_minute": end, "schedule": schedule}


def analyze(rows, worker_counts=(1, 2, 3)):
    jobs, seen = [], set()
    for r in rows:
        ticket = identifier(r["ticket_id"], "ticket_id")
        unique(seen, ticket)
        arrival, service, sla = [number(r[k], k) for k in ("arrival_minute", "service_minutes", "wait_sla_minutes")]
        if service == 0:
            raise ValueError("Service duration must be positive")
        jobs.append((arrival, ticket, service, sla))
    if not jobs or not worker_counts:
        raise ValueError("Jobs and staffing scenarios are required")
    counts = [whole(w, "workers", 1) for w in worker_counts]
    if len(set(counts)) != len(counts):
        raise ValueError("Staffing scenarios must be unique")
    return {"discipline": "FCFS; simultaneous arrivals sorted by ticket id; no preemption",
            "scenarios": [simulate(jobs, count) for count in counts]}


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
