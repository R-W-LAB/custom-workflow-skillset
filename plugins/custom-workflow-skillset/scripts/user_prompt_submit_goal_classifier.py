#!/usr/bin/env python3
import re

from _hook_utils import emit_context, load_event


CRITERIA = [
    r"\b(goal|/goal|long[- ]?running|hours?|checkpoint|progress log|execution package)\b",
    r"\b(refactor|migration|schema|public api|cli|auth|permissions?|pii|billing|data integrity)\b",
    r"\b(multiple files|many files|components?|workflows?|acceptance criteria|verification commands?)\b",
    r"\b(plan|implementation order|rollback|compatibility|release safety|subagents?|parallel)\b",
    r"\b(build|implement|fix|add|rewrite|modernize|orchestrate)\b",
]

DEEP_INTERVIEW_PATTERNS = [
    r"\$deep[- ]?interview\b",
    r"\bdeep[- ]?interview\b",
    r"딥\s*인터뷰|딥인터뷰",
    r"\binterview me\b",
    r"\bclarif(?:y|ication)\b",
]


def main() -> None:
    event = load_event()
    prompt = event.get("prompt") or ""
    if not isinstance(prompt, str) or not prompt.strip():
        return

    if any(re.search(pattern, prompt, re.IGNORECASE) for pattern in DEEP_INTERVIEW_PATTERNS):
        return

    score = sum(1 for pattern in CRITERIA if re.search(pattern, prompt, re.IGNORECASE))
    if score < 2:
        return

    emit_context(
        "UserPromptSubmit",
        "This prompt appears to meet serious-plan criteria. Consider using `$plan-goal-runner` and native `/goal` if the task has a verifiable end state. If the Superpowers plugin is available, actively route to the relevant `Superpowers:*` skill: test-driven-development for behavior changes, systematic-debugging for failures, verification-before-completion before done, writing-plans for granular plans, and subagent-driven-development only for safe independent lanes. Under an active `/goal`, apply Superpowers Autonomy Override: convert Superpowers approval/review/continue prompts into progress/evidence checkpoints and keep working unless a narrow hard-stop condition is reached. Treat this as a suggestion, not a mandate; keep surgical edits stock and simple.",
    )


if __name__ == "__main__":
    main()
