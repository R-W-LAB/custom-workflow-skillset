#!/usr/bin/env python3
from pathlib import Path

from _hook_utils import command_text, cwd_path, emit_context, env_flag, env_int, exit_code, include_tool_output_context, is_verification_command, latest_file, load_event, now_iso, rel, response_text, snippet


def derived_evidence_file(cwd):
    evidence = latest_file(cwd, "-verification.md")
    if evidence:
        return evidence
    for suffix in ("-status.md", "-execution-package.md", "-progress.md"):
        source = latest_file(cwd, suffix)
        if source:
            return source.with_name(source.name.replace(suffix, "-verification.md"))
    return None


def summarize_output(output: str, code) -> str:
    limit = env_int("CUSTOM_WORKFLOW_EVIDENCE_MAX_CHARS", 600)
    if code in (0, "0") and output:
        lines = [line for line in output.splitlines() if line.strip()]
        signal = [line for line in lines if any(word in line.lower() for word in ("ok", "pass", "passed", "ran ", "success"))]
        if signal:
            return snippet("\n".join(signal[-6:]), limit)
    return snippet(output, limit)


def main() -> None:
    event = load_event()
    command = command_text(event)
    if not command or not is_verification_command(command):
        return

    cwd = cwd_path(event)
    code = exit_code(event)
    output = summarize_output(response_text(event), code)
    evidence = derived_evidence_file(cwd)
    block = (
        f"\n## Hook Evidence - {now_iso()}\n\n"
        f"Command: `{command}`\n\n"
        f"Exit code: `{code if code is not None else 'unknown'}`\n\n"
        "Relevant output:\n\n"
        "```text\n"
        f"{output}\n"
        "```\n"
    )

    if evidence and (evidence.exists() or env_flag("CUSTOM_WORKFLOW_EVIDENCE_AUTO_CREATE", True)):
        try:
            evidence.parent.mkdir(parents=True, exist_ok=True)
            with evidence.open("a", encoding="utf-8") as fh:
                fh.write(block)
            emit_context("PostToolUse", f"Verification captured: `{rel(evidence, cwd)}`.")
            return
        except OSError:
            pass

    message = "Verification detected; no evidence path found."
    if include_tool_output_context():
        message += "\n" + block
    emit_context("PostToolUse", message)


if __name__ == "__main__":
    main()
