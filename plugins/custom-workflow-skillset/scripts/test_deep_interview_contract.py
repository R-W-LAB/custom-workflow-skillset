#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLASSIFIER = ROOT / "scripts" / "user_prompt_submit_goal_classifier.py"
DEEP_INTERVIEW_SKILL = ROOT / "skills" / "deep-interview" / "SKILL.md"
HOOKS = ROOT / "hooks" / "hooks.json"


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

    def test_hook_commands_resolve_from_plugin_root_not_project_cwd(self) -> None:
        hooks = json.loads(HOOKS.read_text(encoding="utf-8"))["hooks"]
        payloads = {
            "SessionStart": {"cwd": ""},
            "UserPromptSubmit": {"prompt": "small prompt"},
            "PreToolUse": {"tool_input": {"command": "echo ok"}},
            "PermissionRequest": {"tool_input": {"command": "echo ok"}},
            "PostToolUse": {"tool_input": {"command": "python3 -m unittest"}, "tool_response": {"stdout": "OK", "exit_code": 0}},
            "Stop": {"last_assistant_message": "complete"},
        }

        with tempfile.TemporaryDirectory() as tmp:
            foreign_cwd = Path(tmp)
            env = os.environ.copy()
            env["CLAUDE_PLUGIN_ROOT"] = str(ROOT)

            for event_name, entries in hooks.items():
                with self.subTest(event=event_name):
                    command = entries[0]["hooks"][0]["command"]
                    self.assertIn("${CLAUDE_PLUGIN_ROOT}/scripts/", command)
                    self.assertNotIn("./scripts/", command)
                    result = subprocess.run(
                        command,
                        input=json.dumps({**payloads[event_name], "cwd": str(foreign_cwd)}),
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=foreign_cwd,
                        env=env,
                        shell=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
