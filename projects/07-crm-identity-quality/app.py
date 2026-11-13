"""Independent portfolio case study. All bundled input data is synthetic."""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

def analyze(rows):
    email_groups, phone_groups = defaultdict(list), defaultdict(list)
    clean, seen = [], set()
    for r in rows:
        key = r["record_id"]
        if not key or key in seen:
            raise ValueError("Record ids must be nonempty and unique")
        seen.add(key)
        email = r["email"].strip().lower()
        phone = "".join(c for c in r["phone"] if c.isdigit())
        valid = email.count("@") == 1 and bool(email.split("@")[0]) and "." in email.split("@")[-1] and not any(c.isspace() for c in email)
        issues = []
        if email and not valid:
            issues.append("invalid_email")
        if phone and not 7 <= len(phone) <= 15:
            issues.append("invalid_phone_length")
        if not email and not phone:
            issues.append("missing_identifiers")
        if email and valid:
            email_groups[email].append(key)
        if phone and 7 <= len(phone) <= 15:
            phone_groups[phone].append(key)
        clean.append({"record_id": key, "email": email, "phone": phone, "issues": issues})
    by_id = {r["record_id"]: r for r in clean}
    conflicts = []
    for kind, groups, other in [("email",email_groups,"phone"),("phone",phone_groups,"email")]:
        for identifier, keys in sorted(groups.items()):
            if len(keys) > 1:
                distinct = {by_id[k][other] for k in keys if by_id[k][other]}
                conflicts.append({"matched_on": kind, "identifier": identifier, "records": keys,
                    "status": "conflicting_identifiers" if len(distinct)>1 else "duplicate_candidate"})
    return {"records": clean, "review_groups": conflicts, "automatic_merges": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("sample.csv"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("results.json"))
    args = parser.parse_args()
    try:
        with args.input.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        if not rows:
            raise ValueError("Input must contain at least one data row")
        result = analyze(rows)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, OSError, ArithmeticError) as error:
        parser.exit(2, f"Invalid input: {error}\n")

if __name__ == "__main__":
    main()
