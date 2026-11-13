"""Independent portfolio case study. All bundled input data is synthetic."""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

def analyze(rows):
    rounds, seen = defaultdict(list), set()
    for r in rows:
        hole, par, strokes, putts = [int(r[k]) for k in ("hole","par","strokes","putts")]
        key = (r["round_id"],hole)
        if not r["round_id"] or key in seen or not 1<=hole<=18 or par not in (3,4,5) or strokes<1 or not 0<=putts<=strokes or r["gir"] not in ("0","1"):
            raise ValueError("Invalid or duplicate round/hole")
        seen.add(key)
        rounds[r["round_id"]].append((par,strokes,putts,int(r["gir"])))
    output = []
    for key, holes in sorted(rounds.items()):
        n = len(holes)
        missed = [h for h in holes if h[3]==0]
        output.append({"round_id":key,"holes":n,"complete_round":n==18,
            "score":sum(h[1] for h in holes),"relative_to_par":sum(h[1]-h[0] for h in holes),
            "putts_per_hole":sum(h[2] for h in holes)/n,"gir_rate":sum(h[3] for h in holes)/n,
            "three_putt_rate":sum(h[2]>=3 for h in holes)/n,
            "par_or_better_after_missed_gir":sum(h[1]<=h[0] for h in missed)/len(missed) if missed else None,
            "double_bogey_or_worse":sum(h[1]>=h[0]+2 for h in holes)})
    return {"rounds":output,"note":"Descriptive round measures, not official handicap or strokes-gained calculations."}


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
