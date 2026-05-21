#!/usr/bin/env python3
from _hook_utils import boundary_command_reason, command_text, emit, env_flag, first_fingerprint, load_event, severe_command_reason, strict_mode


def deny(reason: str) -> None:
    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
    )


def warn(reason: str) -> None:
    emit({"systemMessage": reason})


def main() -> None:
    event = load_event()
    command = command_text(event)
    if not command:
        return

    severe = severe_command_reason(command)
    if severe:
        deny(f"{severe} Hard destructive-command guard blocked it. Use a narrower reversible command or change the plan explicitly.")
        return

    boundary = boundary_command_reason(command)
    if boundary and strict_mode():
        deny(f"{boundary} is denied because CUSTOM_WORKFLOW_HOOKS_STRICT is enabled.")
        return
    if boundary:
        if not env_flag("CUSTOM_WORKFLOW_BOUNDARY_WARN_ONCE", True) or first_fingerprint("pre-tool-boundary", boundary, command):
            warn(f"Allowed boundary: {boundary}. Log if goal-scoped.")


if __name__ == "__main__":
    main()
