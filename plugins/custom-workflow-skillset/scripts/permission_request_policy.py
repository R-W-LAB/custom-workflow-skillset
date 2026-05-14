#!/usr/bin/env python3
from __future__ import annotations

from _hook_utils import boundary_command_reason, command_text, emit, load_event, severe_command_reason, strict_mode, tool_input


def allow(message: str | None = None) -> None:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {
                "behavior": "allow",
            },
        }
    }
    if message:
        output["systemMessage"] = message
    emit(output)


def deny(message: str) -> None:
    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {
                    "behavior": "deny",
                    "message": message,
                },
            }
        }
    )


def main() -> None:
    event = load_event()
    command = command_text(event)
    description = tool_input(event).get("description") or ""
    combined = f"{command}\n{description}"

    severe = severe_command_reason(combined)
    if severe:
        deny(f"{severe} Permission denied by the hard destructive-command guard. Use a narrower reversible command or change the plan explicitly.")
        return

    boundary = boundary_command_reason(combined)
    if boundary and strict_mode():
        deny(f"{boundary} is denied because CUSTOM_WORKFLOW_HOOKS_STRICT is enabled.")
        return

    if boundary:
        allow(f"Custom Workflow Skillset YOLO mode auto-approved this {boundary} request so the active long-goal run can continue. Record the command and result in the progress/evidence log.")
        return

    allow("Custom Workflow Skillset YOLO mode auto-approved this non-destructive permission request for uninterrupted long-goal execution.")


if __name__ == "__main__":
    main()
