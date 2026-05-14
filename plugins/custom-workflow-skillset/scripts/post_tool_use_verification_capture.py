#!/usr/bin/env python3
from pathlib import Path

from _hook_utils import command_text, cwd_path, emit_context, exit_code, is_verification_command, latest_file, load_event, now_iso, rel, response_text, snippet


def main() -> None:
    event = load_event()
    command = command_text(event)
    if not command or not is_verification_command(command):
        return

    cwd = cwd_path(event)
    code = exit_code(event)
    output = snippet(response_text(event), 1800)
    evidence = latest_file(cwd, "-verification.md")
    block = (
        f"\n## Hook Evidence - {now_iso()}\n\n"
        f"Command: `{command}`\n\n"
        f"Exit code: `{code if code is not None else 'unknown'}`\n\n"
        "Relevant output:\n\n"
        "```text\n"
        f"{output}\n"
        "```\n"
    )

    if evidence and evidence.exists():
        try:
            with evidence.open("a", encoding="utf-8") as fh:
                fh.write(block)
            emit_context("PostToolUse", f"Verification-like command detected. Evidence was appended to `{rel(evidence, cwd)}`. The root agent should interpret it and update the progress log and live status board if relevant.")
            return
        except OSError:
            pass

    emit_context(
        "PostToolUse",
        "Verification-like command detected. Append this evidence to `agent-handoffs/<slug>-verification.md` and update `agent-handoffs/<slug>-status.md` if this is part of a long-goal checkpoint:\n" + block,
    )


if __name__ == "__main__":
    main()
