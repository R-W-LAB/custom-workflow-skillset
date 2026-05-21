#!/usr/bin/env python3
import re

from _hook_utils import cwd_path, emit_context, first_fingerprint, load_event


CRITERIA = [
    r"\b(goal|/goal|long[- ]?running|hours?|checkpoint|progress log|execution package)\b",
    r"\b(refactor|migration|schema|public api|cli|auth|permissions?|pii|billing|data integrity)\b",
    r"\b(multiple files|many files|components?|workflows?|acceptance criteria|verification commands?)\b",
    r"\b(plan|implementation order|rollback|compatibility|release safety|subagents?|parallel)\b",
]

STRONG_GOAL_SIGNALS = [
    r"\$plan[- ]?goal[- ]?runner\b",
    r"\b/goal\b",
    r"\blong[- ]?(goal|running)\b",
    r"\bexecution package\b",
    r"\bprogress log\b",
    r"\bcheckpoint[- ]?by[- ]?checkpoint\b",
]

DEEP_INTERVIEW_PATTERNS = [
    r"\$deep[- ]?interview\b",
    r"\bdeep[- ]?interview\b",
    r"딥\s*인터뷰|딥인터뷰",
    r"\binterview me\b",
    r"\bclarif(?:y|ication)\b",
]

DESIGN_GRILL_PATTERNS = [
    r"\$design[- ]?grill\b",
    r"\$grill[- ]?with[- ]?docs\b",
    r"\bgrill me\b",
    r"\bdesign[- ]?grill\b",
    r"\bgrill[- ]?with[- ]?docs\b",
    r"\bstress[- ]?test\b",
    r"\bdesign critique\b",
    r"\bdesign interview\b",
    r"\bpressure[- ]?test\b",
    r"설계\s*검토",
    r"압박\s*면접",
    r"도메인\s*모델",
    r"\b(?:CONTEXT\.md|ADR)\b.*\b(?:grill|critique|review|stress[- ]?test|clarif(?:y|ication)|design)\b",
    r"\b(?:grill|critique|review|stress[- ]?test|clarif(?:y|ication)|design)\b.*\b(?:CONTEXT\.md|ADR)\b",
]


def main() -> None:
    event = load_event()
    prompt = event.get("prompt") or ""
    if not isinstance(prompt, str) or not prompt.strip():
        return

    if any(re.search(pattern, prompt, re.IGNORECASE) for pattern in DEEP_INTERVIEW_PATTERNS):
        return

    if any(re.search(pattern, prompt, re.IGNORECASE) for pattern in DESIGN_GRILL_PATTERNS):
        return

    has_strong_signal = any(re.search(pattern, prompt, re.IGNORECASE) for pattern in STRONG_GOAL_SIGNALS)
    score = sum(1 for pattern in CRITERIA if re.search(pattern, prompt, re.IGNORECASE))
    if score < 3 and not (has_strong_signal and score >= 2):
        return
    if not first_fingerprint("prompt-classifier", str(cwd_path(event)), prompt):
        return

    emit_context(
        "UserPromptSubmit",
        "Serious-plan signal detected. Consider `$plan-goal-runner` and native `/goal`; keep routine surgical edits outside the long-goal harness.",
    )


if __name__ == "__main__":
    main()
