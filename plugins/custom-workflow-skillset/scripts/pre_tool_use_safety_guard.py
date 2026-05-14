#!/usr/bin/env python3
from _hook_utils import boundary_command_reason, command_text, emit, load_event, severe_command_reason, strict_mode


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
        warn(f"Custom Workflow Skillset YOLO mode: {boundary} detected and allowed. Record the command and result in the execution package/progress log if this is part of a long goal.")


if __name__ == "__main__":
    main()
