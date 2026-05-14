#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def progress_bar(done: int, total: int, width: int = 20) -> str:
    if total <= 0:
        return "[" + "-" * width + "]"
    done = max(0, min(done, total))
    filled = max(0, min(width, round(width * done / total)))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def checkpoint_rows(checkpoints: list[str]) -> str:
    if not checkpoints:
        checkpoints = ["Initial checkpoint"]
    rows = []
    for index, name in enumerate(checkpoints, start=1):
        rows.append(f"| CP{index:02d} | TODO | {name} | root |  |")
    return "\n".join(rows)


def render(slug: str, title: str, objective: str, checkpoints: list[str]) -> str:
    total = max(len(checkpoints), 1)
    first = checkpoints[0] if checkpoints else "Initial checkpoint"
    stamp = now()
    return f"""# Goal Status: {title}

Last updated: {stamp}
State: PLANNING
Objective: {objective}
Progress: 0 / {total} (0%)
Bar: {progress_bar(0, total)}

Open companion files:
- Execution package: `agent-handoffs/{slug}-execution-package.md`
- Progress log: `agent-handoffs/{slug}-progress.md`
- Verification evidence: `agent-handoffs/{slug}-verification.md`

## Now

Current checkpoint: CP01 - {first}
Current action: preparing execution package
Next checkpoint: CP01 - {first}
Current blocker: none

## Checkpoints

| ID | Status | Checkpoint | Owner | Evidence |
| --- | --- | --- | --- | --- |
{checkpoint_rows(checkpoints)}

Status values: TODO, RUNNING, VERIFYING, DONE, PARTIAL, BLOCKED.

## Verification

| Command / Check | Last run | Exit | Status | Evidence |
| --- | --- | --- | --- | --- |
| `<command>` | never |  | TODO |  |

## Superpowers / Subagents

| Item | Status | Notes |
| --- | --- | --- |
| Superpowers routing | TODO |  |
| Subagent lanes | TODO |  |
| Completion verifier | TODO |  |
| Integration reviewer | TODO |  |

## Recent Events

- {stamp} - Status board initialized.

## Stop Conditions

- Hard destructive shell command needed:
- Payment/purchase action needed:
- Credential or secret exfiltration risk:
- Explicit user-forbidden action needed:
- Same verification failure repeated twice without new evidence:

## Final State

Outcome: pending
Final verification:
Remaining issues:
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Codex-readable long-goal status board.")
    parser.add_argument("slug", help="Task slug used in agent-handoffs/<slug>-status.md")
    parser.add_argument("--title", default=None, help="Status board title")
    parser.add_argument("--objective", default=None, help="One-line objective")
    parser.add_argument("--checkpoint", action="append", default=[], help="Checkpoint name. Repeat for multiple checkpoints.")
    parser.add_argument("--handoffs-dir", default="agent-handoffs", help="Directory for handoff files")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing status board")
    args = parser.parse_args()

    handoffs = Path(args.handoffs_dir)
    handoffs.mkdir(parents=True, exist_ok=True)
    path = handoffs / f"{args.slug}-status.md"
    if path.exists() and not args.force:
        print(path)
        return 0

    title = args.title or args.slug.replace("-", " ").title()
    objective = args.objective or "<one-line objective>"
    path.write_text(render(args.slug, title, objective, args.checkpoint), encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
