#!/usr/bin/env python3
"""
Fix Clay benchmark CSVs: align result column with reasoning.
Rule: "No company list" / cannot execute → qualified
"""

import csv
import re
import sys
from pathlib import Path

# Patterns indicating task could NOT be executed (no company list, etc.)
NO_EXEC_PATTERNS = [
    r"absence of (?:the |a )?company list",
    r"company list (?:was |is )?(?:missing|not provided|not included)",
    r"no (?:company list|companies|domains?) (?:were |was )?(?:listed|provided|included)",
    r"without (?:the )?(?:specific )?(?:company |domain )?list",
    r"without (?:these |specific )?domains?",
    r"list (?:of companies|of domains) (?:was |is )?(?:missing|not provided)",
    r"cannot (?:be )?(?:initiated|executed|performed|determine)",
    r"execution (?:is |cannot be )?(?:blocked|paused|stalled)",
    r"search cannot be (?:initiated|executed)",
    r"impossible to (?:perform|determine)",
    r"awaiting (?:the )?(?:target |company )?list",
    r"ready-to-execute.*pending (?:the )?input",
    r"pending input",
    r"cannot determine whether any company",
    r"did not (?:provide|supply) the list",
    r"'provided list'.*not (?:included|present)",
    r"input list.*not provided",
]

# Patterns indicating explicit unqualified (pages FOUND on target company)
FOUND_PAGES_PATTERNS = [
    r"(?:found|identified|located) (?:comparison |\d+ )?pages? (?:on |for )",
    r"(?:company|domain) (?:has|hosts?) (?:comparison |dedicated )",
    r"marked (?:as )?['\"]?unqualified['\"]? because",
    r"(?:is |was )?['\"]?unqualified['\"]? (?:because|since|as)",
    r"comparison (?:pages?|content) (?:were |was )?(?:found|detected)",
]

# Patterns indicating explicit qualified (no pages)
NO_PAGES_PATTERNS = [
    r"no (?:comparison )?pages? (?:were |was )?(?:found|detected)",
    r"(?:does not|do not) (?:have|host) (?:comparison |such )?pages?",
    r"marked (?:as )?['\"]?qualified['\"]? because",
]


def infer_result_from_reasoning(reasoning: str, formula: str) -> str | None:
    """Infer qualified/unqualified from reasoning text. Returns None if unclear."""
    text = f" {reasoning or ''} {formula or ''} ".lower()
    
    # Check: explicit pages found for this company
    for p in FOUND_PAGES_PATTERNS:
        if re.search(p, text, re.I):
            return "unqualified"
    
    # Check: explicit no pages
    for p in NO_PAGES_PATTERNS:
        if re.search(p, text, re.I):
            return "qualified"
    
    # Check: could not execute (no list, etc.) → qualified
    for p in NO_EXEC_PATTERNS:
        if re.search(p, text, re.I):
            return "qualified"
    
    return None  # unclear, don't change


def fix_clay_csv(filepath: Path, dry_run: bool = False) -> int:
    """Fix a single Clay CSV. Returns number of changes made."""
    with open(filepath, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if len(rows) < 2:
        return 0
    
    headers = rows[0]
    
    # Find column indices
    reason_idx = next((i for i, h in enumerate(headers) if h.strip() == "Reasoning"), None)
    formula_idx = next((i for i, h in enumerate(headers) if h.strip() == "Formula"), None)
    
    # Result column: "Qualification Status formula" or "Qualification Status qualification"
    # EXCLUDE "explanation" (contains long text, not the result)
    result_idx = None
    for i in range(len(headers) - 1, -1, -1):
        h = headers[i].strip().lower()
        if "explanation" in h:
            continue  # skip explanation column
        if ("formula" in h or "qualification" in h) and "qualification" in h:
            result_idx = i
            break
        if "reasoning" in h and "formula" in h:
            result_idx = i
            break

    if result_idx is None:
        # fallback: second-to-last if last is explanation
        if headers and "explanation" in headers[-1].lower():
            result_idx = len(headers) - 2
        else:
            result_idx = len(headers) - 1
    
    if reason_idx is None and formula_idx is None:
        print(f"  No Reasoning/Formula columns in {filepath.name}", file=sys.stderr)
        return 0
    
    changes = 0
    for i in range(1, len(rows)):
        row = rows[i]
        if len(row) <= max(result_idx, reason_idx or 0, formula_idx or 0):
            continue
        
        current = (row[result_idx] or "").strip().lower()
        reasoning = row[reason_idx] if reason_idx is not None and reason_idx < len(row) else ""
        formula = row[formula_idx] if formula_idx is not None and formula_idx < len(row) else ""
        
        # Skip non-standard values (high, blank, Running...) - set to qualified
        if current not in ("qualified", "unqualified"):
            if not dry_run:
                row[result_idx] = "qualified"
            changes += 1
            continue
        
        inferred = infer_result_from_reasoning(reasoning, formula)
        if inferred is not None and inferred != current:
            if not dry_run:
                row[result_idx] = inferred
            changes += 1
    
    if not dry_run and changes > 0:
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
    
    return changes


def main():
    clay_dir = Path(__file__).parent / "clay"
    dry_run = "--dry-run" in sys.argv
    
    total = 0
    for f in sorted(clay_dir.glob("benchmark-clay-*.csv")):
        n = fix_clay_csv(f, dry_run=dry_run)
        total += n
        status = "(dry run)" if dry_run else "(written)"
        print(f"{f.name}: {n} changes {status}")
    
    print(f"\nTotal: {total} changes")


if __name__ == "__main__":
    main()
