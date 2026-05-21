#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import sys
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


def render_compact(slug: str, title: str, objective: str, checkpoints: list[str]) -> str:
    total = max(len(checkpoints), 1)
    first = checkpoints[0] if checkpoints else "Initial checkpoint"
    stamp = now()
    return f"""# Goal Status: {title}

Last updated: {stamp}
State: PLANNING
Objective: {objective}
Progress: 0 / {total} (0%)

## Now

Current checkpoint: CP01 - {first}
Current action: preparing execution package
Next checkpoint: CP01 - {first}
Current blocker: none

## Files

- Package: `agent-handoffs/{slug}-execution-package.md`
- Progress: `agent-handoffs/{slug}-progress.md`
- Evidence: `agent-handoffs/{slug}-verification.md`

## Verification

| Command | Exit | Status | Evidence |
| --- | --- | --- | --- |
| `<command>` |  | TODO |  |

## Recent Events

- {stamp} - Status board initialized.

## Final State

Outcome: pending
"""


def status_path(slug: str, handoffs_dir: str) -> Path:
    return Path(handoffs_dir) / f"{slug}-status.md"


def replace_line(text: str, prefix: str, value: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = f"{prefix}{value}"
            return "\n".join(lines) + "\n"
    return text.rstrip() + f"\n{prefix}{value}\n"


def append_recent_event(text: str, event: str, keep: int = 5) -> str:
    stamp = now()
    entry = f"- {stamp} - {event}"
    marker = "## Recent Events"
    if marker not in text:
        return text.rstrip() + f"\n\n{marker}\n\n{entry}\n"
    before, after = text.split(marker, 1)
    lines = after.splitlines()
    kept = [line for line in lines if line.startswith("- ")][: keep - 1]
    rest_start = next((i for i, line in enumerate(lines) if line.startswith("## ") and i > 0), None)
    rest = "\n".join(lines[rest_start:]) if rest_start is not None else ""
    body = "\n".join([entry, *kept])
    return before.rstrip() + f"\n\n{marker}\n\n{body}\n\n" + rest.rstrip() + "\n"


def load_board(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"status board not found: {path}")
    return path.read_text(encoding="utf-8")


def verification_section(text: str) -> str:
    marker = "## Verification"
    if marker not in text:
        return ""
    after = text.split(marker, 1)[1]
    next_section = after.find("\n## ", 1)
    return after if next_section == -1 else after[:next_section]


def compact_verification_table(text: str) -> bool:
    section = verification_section(text)
    return "| Command | Exit | Status | Evidence |" in section


def update_board(args) -> int:
    path = status_path(args.slug, args.handoffs_dir)
    text = load_board(path)
    text = replace_line(text, "Last updated: ", now())
    if args.state:
        text = replace_line(text, "State: ", args.state)
    if args.current:
        text = replace_line(text, "Current checkpoint: ", args.current)
        text = replace_line(text, "Current action: ", args.current)
    if args.next:
        text = replace_line(text, "Next checkpoint: ", args.next)
    if args.blocker:
        text = replace_line(text, "Current blocker: ", args.blocker)
    if args.event:
        text = append_recent_event(text, args.event)
    path.write_text(text, encoding="utf-8")
    print(path)
    return 0


def verify_board(args) -> int:
    path = status_path(args.slug, args.handoffs_dir)
    text = load_board(path)
    marker = "## Verification"
    is_compact = compact_verification_table(text)
    row = (
        f"| `{args.command}` | {args.exit} | {args.status} | {args.evidence or ''} |"
        if is_compact
        else f"| `{args.command}` | {now()} | {args.exit} | {args.status} | {args.evidence or ''} |"
    )
    if marker in text and "| `<command>` | never |" in text:
        text = text.replace("| `<command>` | never |  | TODO |  |", row)
    elif marker in text and "| `<command>` |  | TODO |  |" in text:
        text = text.replace("| `<command>` |  | TODO |  |", row)
    elif marker in text:
        before, after = text.split(marker, 1)
        next_section = after.find("\n## ", 1)
        if next_section == -1:
            text = before + marker + after.rstrip() + "\n" + row + "\n"
        else:
            text = before + marker + after[:next_section].rstrip() + "\n" + row + "\n" + after[next_section:]
    else:
        text += f"\n\n{marker}\n\n| Command / Check | Last run | Exit | Status | Evidence |\n| --- | --- | --- | --- | --- |\n{row}\n"
    text = append_recent_event(text, f"verification {args.status}: {args.command}")
    path.write_text(text, encoding="utf-8")
    print(path)
    return 0


def done_board(args) -> int:
    path = status_path(args.slug, args.handoffs_dir)
    text = load_board(path)
    text = replace_line(text, "Last updated: ", now())
    text = replace_line(text, "State: ", args.state)
    text = replace_line(text, "Outcome: ", args.summary)
    text = append_recent_event(text, f"final state {args.state}: {args.summary}")
    path.write_text(text, encoding="utf-8")
    print(path)
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in {"update", "verify", "done"}:
        command = sys.argv[1]
        parser = argparse.ArgumentParser(description=f"{command} a Codex-readable long-goal status board.")
        parser.add_argument("slug")
        parser.add_argument("--handoffs-dir", default="agent-handoffs")
        if command == "update":
            parser.add_argument("--state")
            parser.add_argument("--current")
            parser.add_argument("--next")
            parser.add_argument("--blocker")
            parser.add_argument("--event")
            return update_board(parser.parse_args(sys.argv[2:]))
        if command == "verify":
            parser.add_argument("--command", required=True)
            parser.add_argument("--exit", required=True)
            parser.add_argument("--status", required=True)
            parser.add_argument("--evidence", default="")
            return verify_board(parser.parse_args(sys.argv[2:]))
        parser.add_argument("--state", default="DONE")
        parser.add_argument("--summary", required=True)
        return done_board(parser.parse_args(sys.argv[2:]))

    parser = argparse.ArgumentParser(description="Create a Codex-readable long-goal status board.")
    parser.add_argument("slug", help="Task slug used in agent-handoffs/<slug>-status.md")
    parser.add_argument("--title", default=None, help="Status board title")
    parser.add_argument("--objective", default=None, help="One-line objective")
    parser.add_argument("--checkpoint", action="append", default=[], help="Checkpoint name. Repeat for multiple checkpoints.")
    parser.add_argument("--handoffs-dir", default="agent-handoffs", help="Directory for handoff files")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing status board")
    parser.add_argument("--compact", action="store_true", help="Create the compact status board layout")
    args = parser.parse_args()

    handoffs = Path(args.handoffs_dir)
    handoffs.mkdir(parents=True, exist_ok=True)
    path = handoffs / f"{args.slug}-status.md"
    if path.exists() and not args.force:
        print(path)
        return 0

    title = args.title or args.slug.replace("-", " ").title()
    objective = args.objective or "<one-line objective>"
    renderer = render_compact if args.compact else render
    path.write_text(renderer(args.slug, title, objective, args.checkpoint), encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
