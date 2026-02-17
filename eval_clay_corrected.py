#!/usr/bin/env python3
"""
Re-evaluate Clay (reasoning-corrected) per README methodology.
Ground truth: from README (agreement baseline + disputed verification + audit).
Implemented using benchmark data with IMTC=qualified, Rad Security excluded.
"""

import csv
import sys
from pathlib import Path

BENCH_DIR = Path(__file__).parent
PLYNE = BENCH_DIR / "plyne" / "benchmark-plyne-1.csv"
CLAY_FILES = [
    BENCH_DIR / "clay" / "benchmark-clay-1.csv",
    BENCH_DIR / "clay" / "benchmark-clay-2.csv",
    BENCH_DIR / "clay" / "benchmark-clay-3.csv",
]

# Per README methodology: IMTC was incorrectly classified by both platforms → ground truth = qualified
# Rad Security = unclear, excluded from scoring
GT_OVERRIDES = {"IMTC": "qualified"}
EXCLUDE = {"Rad Security"}


def load_ground_truth():
    """Load ground truth per README methodology. Returns dict company -> qualified|unqualified."""
    gt = {}
    with open(PLYNE, encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            name = row.get("name", "").strip()
            if not name:
                continue
            res = (row.get("no_comparison_pages_result") or "").strip().lower()
            if name in GT_OVERRIDES:
                res = GT_OVERRIDES[name]
            gt[name] = res
    return gt


def load_clay_run(filepath):
    """Load Clay result per company. Returns dict company -> qualified|unqualified|other."""
    # Find result column
    with open(filepath, encoding="utf-8") as f:
        r = csv.reader(f)
        headers = next(r)
    result_idx = None
    for i in range(len(headers) - 1, -1, -1):
        h = headers[i].strip().lower()
        if "explanation" in h:
            continue
        if ("formula" in h or "qualification" in h) and "qualification" in h:
            result_idx = i
            break
        if "reasoning" in h and "formula" in h:
            result_idx = i
            break
    if result_idx is None:
        result_idx = len(headers) - 2 if headers and "explanation" in headers[-1].lower() else len(headers) - 1

    name_idx = 0  # Organization Name
    out = {}
    with open(filepath, encoding="utf-8") as f:
        r = csv.reader(f)
        next(r)  # header
        for row in r:
            if len(row) <= max(name_idx, result_idx):
                continue
            name = row[name_idx].strip().strip('"')
            res = (row[result_idx] or "").strip().lower()
            if res not in ("qualified", "unqualified"):
                res = "other"
            out[name] = res
    return out


def main():
    gt = load_ground_truth()
    companies = [c for c in gt if c not in EXCLUDE]
    n_total = len(companies)

    # On-domain rule: Clay has no on-domain refs, so unqualified = always incorrect.
    # Correct only when Clay says qualified AND ground truth says qualified.
    runs = []
    for fp in CLAY_FILES:
        clay = load_clay_run(fp)
        correct = 0
        q_count = u_count = o_count = 0
        for c in companies:
            cgt = gt.get(c)
            cres = clay.get(c, "other")
            if cres == "qualified":
                q_count += 1
            elif cres == "unqualified":
                u_count += 1
            else:
                o_count += 1
            # With on-domain rule: only Clay qualified + GT qualified counts as correct
            if cgt and cres == "qualified" and cgt == "qualified":
                correct += 1
        runs.append({
            "correct": correct,
            "qualified": q_count,
            "unqualified": u_count,
            "other": o_count,
        })

    # Consistency: same result across all 3 runs
    clay1 = load_clay_run(CLAY_FILES[0])
    clay2 = load_clay_run(CLAY_FILES[1])
    clay3 = load_clay_run(CLAY_FILES[2])
    consistent = 0
    for c in companies:
        r1 = clay1.get(c, "other")
        r2 = clay2.get(c, "other")
        r3 = clay3.get(c, "other")
        if r1 == r2 == r3 and r1 in ("qualified", "unqualified"):
            consistent += 1

    avg_pct = sum(r["correct"] for r in runs) / 3 / n_total * 100 if n_total else 0

    # Inconsistent companies
    incon = []
    for c in sorted(gt.keys()):
        r1, r2, r3 = clay1.get(c, "?"), clay2.get(c, "?"), clay3.get(c, "?")
        if not (r1 == r2 == r3 and r1 in ("qualified", "unqualified")):
            incon.append((c, r1, r2, r3))

    print("=== Clay (reasoning-corrected) Re-evaluation ===\n")
    print("Accuracy (on-domain rule: unqualified without on-domain ref = incorrect):")
    print(f"  Run 1: {runs[0]['correct']}/{n_total} ({runs[0]['correct']/n_total*100:.1f}%)")
    print(f"  Run 2: {runs[1]['correct']}/{n_total} ({runs[1]['correct']/n_total*100:.1f}%)")
    print(f"  Run 3: {runs[2]['correct']}/{n_total} ({runs[2]['correct']/n_total*100:.1f}%)")
    print(f"  Average: {avg_pct:.1f}%")
    print()
    print("Consistency:")
    print(f"  Consistent: {consistent}/{len(gt)} ({consistent/len(gt)*100:.0f}%)")
    print()
    print("Distribution per run:")
    for i, r in enumerate(runs, 1):
        print(f"  Run {i}: Qualified={r['qualified']}, Unqualified={r['unqualified']}, Other={r['other']}")

    if "--list-inconsistent" in sys.argv:
        print("\nInconsistent companies (name, r1, r2, r3):")
        for name, r1, r2, r3 in incon:
            print(f"  {name}: {r1} | {r2} | {r3}")


if __name__ == "__main__":
    main()
