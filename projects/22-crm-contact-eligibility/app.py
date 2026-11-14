"""Run the SQLite case against a synthetic or user-supplied CSV."""
import argparse, csv, json, sqlite3
from contextlib import closing
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = ['event_id', 'member_id', 'event_day', 'kind']
SCHEMA = "CREATE TABLE records (event_id TEXT PRIMARY KEY CHECK(length(trim(event_id))>0), member_id TEXT CHECK(length(trim(member_id))>0), event_day TEXT CHECK(date(event_day,'+0 days') IS event_day), kind TEXT CHECK(kind IN ('opt_in','opt_out','send')))"

def run(source):
    with closing(sqlite3.connect(":memory:")) as db, source.open(newline="", encoding="utf-8") as stream:
        db.row_factory = sqlite3.Row
        db.execute(SCHEMA)
        reader = csv.reader(stream)
        if next(reader, None) != FIELDS:
            raise ValueError("Unexpected CSV header")
        count = 0
        for count, row in enumerate(reader, 1):
            if len(row) != len(FIELDS):
                raise ValueError(f"Wrong field count at row {count + 1}")
            db.execute("INSERT INTO records VALUES (" + ",".join("?" for _ in row) + ")", row)
        if not count:
            raise ValueError("Input must contain at least one data row")
        return [dict(row) for row in db.execute((HERE / "analysis.sql").read_text())]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=HERE / "sample.csv")
    parser.add_argument("--output", type=Path, default=HERE / "results.json")
    args = parser.parse_args()
    try:
        result = run(args.input)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    except (ValueError, sqlite3.Error, OSError) as exc:
        parser.exit(2, f"Invalid input: {exc}\n")
