"""Run the SQLite case against a synthetic or user-supplied CSV."""
import argparse, csv, json, sqlite3
from contextlib import closing
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = ['posting_id', 'case_id', 'posted_on', 'direction', 'amount_cents']
SCHEMA = "CREATE TABLE records (posting_id TEXT PRIMARY KEY CHECK(length(trim(posting_id))>0), case_id TEXT NOT NULL CHECK(length(trim(case_id))>0), posted_on TEXT NOT NULL CHECK(date(posted_on,'+0 days') IS posted_on), direction TEXT CHECK(direction IN ('debit','credit')), amount_cents INTEGER NOT NULL CHECK(typeof(amount_cents)='integer' AND amount_cents>0))"

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
