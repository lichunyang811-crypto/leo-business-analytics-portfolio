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

FIELDS = ['requirement_id', 'priority', 'test_id', 'status']

def analyze(rows):
    requirements, seen, global_tests = {}, set(), {}
    for r in rows:
        req = identifier(r["requirement_id"], "requirement_id")
        priority, test, status = r["priority"], r["test_id"].strip(), r["status"]
        if priority not in ("critical", "normal") or status not in ("pass", "fail", "blocked", "not_run"):
            raise ValueError("Invalid priority or test status")
        if not test and status != "not_run":
            raise ValueError("Unmapped requirement must be not_run")
        unique(seen, (req, test))
        if req in requirements and requirements[req]["priority"] != priority:
            raise ValueError("Conflicting requirement priority")
        record = requirements.setdefault(req, {"priority": priority, "tests": {}})
        record["tests"][test] = status
        if test:
            if test in global_tests and global_tests[test] != status:
                raise ValueError("Shared test has conflicting execution status")
            global_tests[test] = status
    output = []
    for req, record in sorted(requirements.items()):
        tests = record["tests"]
        if "" in tests and len(tests) > 1:
            raise ValueError("Do not mix unmapped placeholder with mapped tests")
        mapped = "" not in tests
        ready = mapped and all(status == "pass" for status in tests.values())
        output.append({"requirement_id": req, "priority": record["priority"],
            "mapped": mapped, "ready": ready,
            "open_tests": [test for test, status in sorted(tests.items()) if test and status != "pass"],
            "reason": "passed" if ready else "unmapped" if not mapped else "tests_not_all_passed"})
    count = len(output)
    return {"requirements": output,
        "mapped_requirement_rate": sum(r["mapped"] for r in output) / count if count else None,
        "passed_requirement_rate": sum(r["ready"] for r in output) / count if count else None,
        "critical_blockers": [r["requirement_id"] for r in output if r["priority"] == "critical" and not r["ready"]],
        "unique_test_status_counts": dict(Counter(global_tests.values())),
        "release_recommendation": "ready_for_human_signoff" if count and all(r["ready"] for r in output) else "hold"}


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
