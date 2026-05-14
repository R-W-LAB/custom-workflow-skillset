#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CHECKS = [
    ("native goal command", r"## Native Goal Command[\s\S]*?/goal\s+Complete"),
    ("progress file path", r"agent-handoffs/[^`\s]+-progress\.md"),
    ("status board file path", r"agent-handoffs/[^`\s]+-status\.md"),
    ("verification evidence file path", r"agent-handoffs/[^`\s]+-verification\.md"),
    ("dirty working tree guard", r"User\s*/\s*pre-existing changes"),
    ("pre-existing modified files", r"Pre-existing modified files"),
    ("acceptance criteria", r"## Acceptance Criteria"),
    ("autonomous action policy", r"## Autonomous Action Policy"),
    ("live status board", r"## Live Status Board"),
    ("superpowers skill routing", r"## Superpowers Skill Routing"),
    ("superpowers autonomy override", r"## Superpowers Autonomy Override"),
    ("active goal auto-resolution log", r"Auto-resolved under active /goal"),
    ("final verification commands or plan", r"(final verification|## Verification Plan|Done only when all acceptance criteria)"),
    ("checkpoint loop", r"Checkpoint loop"),
    ("narrow hard-stop conditions", r"Narrow hard-stop conditions|Rollback\s*/\s*Stop Conditions"),
    ("parallelization verdict", r"Verdict:\s*(PARALLEL_SAFE|PARALLEL_SAFE_WITH_LIMITS|SEQUENTIAL_RECOMMENDED|SEQUENTIAL_REQUIRED)"),
    ("file ownership boundary", r"(## File / Ownership Boundaries|Allowed files:|Must not edit:)"),
    ("reviewer gates", r"(completion_verifier|integration_reviewer)"),
    ("rollback/recovery note", r"## Rollback\s*/\s*Stop Conditions"),
]


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    failures = []
    for label, pattern in CHECKS:
        if not re.search(pattern, text, re.IGNORECASE):
            failures.append(label)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a plan-goal-runner execution package contract.")
    parser.add_argument("path", help="Path to agent-handoffs/<slug>-execution-package.md")
    args = parser.parse_args()
    path = Path(args.path)
    if not path.exists():
        print(f"FAIL: file not found: {path}", file=sys.stderr)
        return 2

    failures = validate(path)
    if failures:
        print("FAIL: execution package is missing required contract items:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("PASS: execution package contract is complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
