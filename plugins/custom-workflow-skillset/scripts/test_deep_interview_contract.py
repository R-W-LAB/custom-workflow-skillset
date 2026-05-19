#!/usr/bin/env python3
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLASSIFIER = ROOT / "scripts" / "user_prompt_submit_goal_classifier.py"
DEEP_INTERVIEW_SKILL = ROOT / "skills" / "deep-interview" / "SKILL.md"
DESIGN_GRILL_SKILL = ROOT / "skills" / "design-grill" / "SKILL.md"
DESIGN_GRILL_WITH_DOCS_SKILL = ROOT / "skills" / "design-grill-with-docs" / "SKILL.md"


def run_classifier(prompt: str) -> str:
    result = subprocess.run(
        [sys.executable, str(CLASSIFIER)],
        input=json.dumps({"prompt": prompt}),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
        check=True,
    )
    return result.stdout


class DeepInterviewContractTest(unittest.TestCase):
    def test_deep_interview_prompts_do_not_emit_goal_runner_hint(self) -> None:
        prompts = [
            "$deep-interview clarify a multi-component auth refactor with rollback and verification commands",
            "Deep Interview this migration plan before implementation",
            "딥인터뷰로 이 auth workflow 변경 범위를 먼저 정리해줘",
            "interview me before building this feature",
            "clarify this public API compatibility change before planning",
        ]

        for prompt in prompts:
            with self.subTest(prompt=prompt):
                self.assertEqual(run_classifier(prompt), "")

    def test_serious_non_interview_prompt_still_gets_goal_runner_hint(self) -> None:
        output = run_classifier(
            "Implement the auth refactor across multiple files with rollback and verification commands"
        )

        self.assertIn("$plan-goal-runner", output)
        self.assertIn("native `/goal`", output)

    def test_deep_interview_skill_documents_plan_mode_adapter(self) -> None:
        text = DEEP_INTERVIEW_SKILL.read_text(encoding="utf-8")

        self.assertIn("request_user_input", text)
        self.assertIn("Plan mode adapter", text)
        self.assertIn("Do not include an `Other` option manually", text)
        self.assertIn("Markdown fallback", text)

    def test_deep_interview_skill_blocks_goal_handoff_during_interview(self) -> None:
        text = DEEP_INTERVIEW_SKILL.read_text(encoding="utf-8")

        self.assertIn("Do not call `create_goal`", text)
        self.assertIn("do not start `/goal`", text)
        self.assertIn("do not route to `plan-goal-runner`", text)
        self.assertIn("only after the requirements handoff is written", text)


class DesignGrillContractTest(unittest.TestCase):
    def test_design_grill_prompts_do_not_emit_goal_runner_hint(self) -> None:
        prompts = [
            "$design-grill stress-test this multi-component auth design before implementation",
            "grill me on this release architecture and rollback strategy",
            "설계 검토로 이 도메인 모델 결정을 압박 면접해줘",
            "stress-test this design before writing an execution plan",
            "design critique this public API migration before planning",
        ]

        for prompt in prompts:
            with self.subTest(prompt=prompt):
                self.assertEqual(run_classifier(prompt), "")

    def test_design_grill_skill_documents_plan_mode_and_isolation(self) -> None:
        text = DESIGN_GRILL_SKILL.read_text(encoding="utf-8")

        self.assertIn("request_user_input", text)
        self.assertIn("Plan mode adapter", text)
        self.assertIn("Markdown fallback", text)
        self.assertIn("Do not call `create_goal`", text)
        self.assertIn("do not start `/goal`", text)
        self.assertIn("do not route to `plan-goal-runner`", text)
        self.assertIn("agent-handoffs/<slug>-design-grill.md", text)

    def test_design_grill_with_docs_includes_conservative_docs_policy(self) -> None:
        text = DESIGN_GRILL_WITH_DOCS_SKILL.read_text(encoding="utf-8")

        self.assertIn("request_user_input", text)
        self.assertIn("Plan mode adapter", text)
        self.assertIn("Markdown fallback", text)
        self.assertIn("Do not call `create_goal`", text)
        self.assertIn("agent-handoffs/<slug>-design-grill-with-docs.md", text)
        self.assertIn("CONTEXT-FORMAT.md", text)
        self.assertIn("ADR-FORMAT.md", text)
        self.assertIn("Do not edit implementation files", text)
        self.assertIn("Offer ADRs sparingly", text)

    def test_design_grill_with_docs_bundles_reference_formats(self) -> None:
        skill_dir = DESIGN_GRILL_WITH_DOCS_SKILL.parent

        self.assertTrue((skill_dir / "references" / "CONTEXT-FORMAT.md").is_file())
        self.assertTrue((skill_dir / "references" / "ADR-FORMAT.md").is_file())


if __name__ == "__main__":
    unittest.main()
