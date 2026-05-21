#!/usr/bin/env python3
import re

from _hook_utils import active_handoff_paths, cwd_path, emit_context, env_flag, env_int, fingerprint, first_fingerprint, include_context_tails, load_event, read_tail, rel, snippet, token_profile


def field(text: str, label: str, default: str = "unknown") -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else default


def main() -> None:
    event = load_event()
    cwd = cwd_path(event)
    paths = active_handoff_paths(cwd)
    status = paths.get("status")
    progress = paths.get("progress")
    package = paths.get("package")
    if not progress and not package and not status:
        return

    status_text = read_tail(status, 2500) if status else ""
    progress_text = read_tail(progress, 1200) if progress else ""
    fp = fingerprint(status_text + "\n" + progress_text)
    once = env_flag("CUSTOM_WORKFLOW_SESSIONSTART_ONCE_PER_FINGERPRINT", True)
    repeated = once and not first_fingerprint("session-start", str(cwd), fp)

    lines = []
    if status_text and not repeated:
        state = field(status_text, "State")
        current = field(status_text, "Current checkpoint")
        next_step = field(status_text, "Next checkpoint")
        blocker = field(status_text, "Current blocker", "none")
        lines.append(f"CWS active: state={state}, current={current}, next={next_step}, blocker={blocker}.")
    else:
        lines.append("CWS active handoff detected; paths only.")
    if package:
        lines.append(f"pkg={rel(package, cwd)}")
    if status:
        lines.append(f"status={rel(status, cwd)}")
        status_tail = snippet(status_text, env_int("CUSTOM_WORKFLOW_CONTEXT_MAX_CHARS", 600)) if include_context_tails() and not repeated else ""
        if status_tail:
            lines.append("Status tail:\n```text\n" + status_tail + "\n```")
    if progress:
        lines.append(f"progress={rel(progress, cwd)}")
        tail = snippet(progress_text, env_int("CUSTOM_WORKFLOW_CONTEXT_MAX_CHARS", 600)) if include_context_tails() and not repeated and (token_profile() == "full" or not status_text) else ""
        if tail:
            lines.append("Progress tail:\n```text\n" + tail + "\n```")
    lines.append("Read package only if continuing this goal.")
    emit_context("SessionStart", snippet("\n".join(lines), env_int("CUSTOM_WORKFLOW_CONTEXT_MAX_CHARS", 600)))


if __name__ == "__main__":
    main()
