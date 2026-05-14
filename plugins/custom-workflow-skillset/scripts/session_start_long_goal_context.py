#!/usr/bin/env python3
from _hook_utils import cwd_path, emit_context, latest_file, load_event, read_tail, rel, snippet


def main() -> None:
    event = load_event()
    cwd = cwd_path(event)
    status = latest_file(cwd, "-status.md")
    progress = latest_file(cwd, "-progress.md")
    package = latest_file(cwd, "-execution-package.md")
    if not progress and not package and not status:
        return

    lines = ["Custom Workflow Skillset: long-goal handoff context detected."]
    if package:
        lines.append(f"- Execution package: `{rel(package, cwd)}`")
    if status:
        lines.append(f"- Live status board: `{rel(status, cwd)}`")
        status_tail = snippet(read_tail(status, 2500), 1800)
        if status_tail:
            lines.append("\nCurrent status board tail:\n```text\n" + status_tail + "\n```")
    if progress:
        lines.append(f"- Progress log: `{rel(progress, cwd)}`")
        tail = snippet(read_tail(progress, 2500), 2000)
        if tail:
            lines.append("\nRecent progress tail:\n```text\n" + tail + "\n```")
    lines.append("Before continuing a long goal, read the execution package and preserve any user/pre-existing changes recorded there.")
    emit_context("SessionStart", "\n".join(lines))


if __name__ == "__main__":
    main()
