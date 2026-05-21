#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
CLASSIFIER = ROOT / "scripts" / "user_prompt_submit_goal_classifier.py"
DEEP_INTERVIEW_SKILL = ROOT / "skills" / "deep-interview" / "SKILL.md"
DESIGN_GRILL_SKILL = ROOT / "skills" / "design-grill" / "SKILL.md"
DESIGN_GRILL_WITH_DOCS_SKILL = ROOT / "skills" / "design-grill-with-docs" / "SKILL.md"
SESSION_START = ROOT / "scripts" / "session_start_long_goal_context.py"
POST_TOOL_USE = ROOT / "scripts" / "post_tool_use_verification_capture.py"
PERMISSION_POLICY = ROOT / "scripts" / "permission_request_policy.py"
PRE_TOOL_USE = ROOT / "scripts" / "pre_tool_use_safety_guard.py"
SYNC_INSTALL = ROOT / "scripts" / "sync_user_install.py"
PLAN_GOAL_SKILL = ROOT / "skills" / "plan-goal-runner" / "SKILL.md"
EXECUTION_TEMPLATE = ROOT / "skills" / "plan-goal-runner" / "templates" / "execution-package.md"
STATUS_BOARD = ROOT / "skills" / "plan-goal-runner" / "scripts" / "status_board.py"
VALIDATOR = ROOT / "skills" / "plan-goal-runner" / "scripts" / "validate_execution_package.py"
SHARED_QUESTION = ROOT / "skills" / "_shared" / "references" / "choice-assisted-question.md"
TOKEN_CONFIG = ROOT / "docs" / "codex-config-token-efficient.toml"
CODEX_PLUGIN_JSON = ROOT / ".codex-plugin" / "plugin.json"
CLAUDE_PLUGIN_JSON = ROOT / ".claude-plugin" / "plugin.json"
HOOKS_JSON = ROOT / "hooks" / "hooks.json"
CLAUDE_MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "test.yml"


def run_classifier(prompt: str) -> str:
    env = os.environ.copy()
    with tempfile.TemporaryDirectory() as tmp:
        env["CWS_HOOK_STATE_DIR"] = tmp
        result = subprocess.run(
            [sys.executable, str(CLASSIFIER)],
            input=json.dumps({"prompt": prompt}),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=ROOT,
            env=env,
            check=True,
        )
    return result.stdout


def run_script(path: Path, event: dict, *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> str:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    result = subprocess.run(
        [sys.executable, str(path)],
        input=json.dumps(event),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        env=merged_env,
        check=True,
    )
    return result.stdout


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    if marker not in text:
        return ""
    after = text.split(marker, 1)[1]
    end = after.find("\n## ", 1)
    return after if end == -1 else after[:end]


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

    def test_explicit_long_goal_prompt_still_gets_goal_runner_hint(self) -> None:
        output = run_classifier(
            "Prepare a long /goal execution package for the auth refactor across multiple files with rollback and verification commands"
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


class TokenEfficiencyContractTest(unittest.TestCase):
    def test_classifier_ignores_generic_verbs_but_keeps_serious_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = {"CWS_HOOK_STATE_DIR": tmp}
            ordinary = run_script(CLASSIFIER, {"prompt": "Implement a small button style fix"}, env=env)
            serious = run_script(
                CLASSIFIER,
                {"prompt": "Implement the auth refactor across multiple files with rollback and verification commands"},
                env=env,
            )
            explicit = run_script(
                CLASSIFIER,
                {"prompt": "Prepare a long /goal execution package for the auth refactor with verification commands"},
                env=env,
            )

        self.assertEqual(ordinary, "")
        self.assertIn("$plan-goal-runner", serious)
        self.assertIn("$plan-goal-runner", explicit)

    def test_classifier_suppresses_repeated_prompt_hash(self) -> None:
        prompt = "Prepare a long /goal execution package for the auth refactor with rollback and verification commands"
        with tempfile.TemporaryDirectory() as tmp:
            env = {"CWS_HOOK_STATE_DIR": tmp}
            event = {"cwd": str(ROOT), "prompt": prompt}

            first = run_script(CLASSIFIER, event, env=env)
            second = run_script(CLASSIFIER, event, env=env)

        self.assertIn("$plan-goal-runner", first)
        self.assertEqual(second, "")

    def test_session_start_minimal_profile_emits_paths_without_tails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            handoffs = cwd / "agent-handoffs"
            handoffs.mkdir()
            (handoffs / "sample-status.md").write_text("SECRET_STATUS_TAIL\nNext checkpoint: continue\n", encoding="utf-8")
            (handoffs / "sample-progress.md").write_text("SECRET_PROGRESS_TAIL\nNext step: continue\n", encoding="utf-8")
            (handoffs / "sample-execution-package.md").write_text("# package\n", encoding="utf-8")

            output = run_script(SESSION_START, {"cwd": str(cwd)})

        self.assertIn("sample-status.md", output)
        self.assertIn("sample-progress.md", output)
        self.assertIn("sample-execution-package.md", output)
        self.assertNotIn("SECRET_STATUS_TAIL", output)
        self.assertNotIn("SECRET_PROGRESS_TAIL", output)

    def test_session_start_full_profile_can_include_tails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            handoffs = cwd / "agent-handoffs"
            handoffs.mkdir()
            (handoffs / "sample-status.md").write_text("FULL_STATUS_TAIL\n", encoding="utf-8")
            (handoffs / "sample-progress.md").write_text("FULL_PROGRESS_TAIL\n", encoding="utf-8")

            output = run_script(SESSION_START, {"cwd": str(cwd)}, env={"CWS_TOKEN_PROFILE": "full"})

        self.assertIn("FULL_STATUS_TAIL", output)
        self.assertIn("FULL_PROGRESS_TAIL", output)

    def test_post_tool_use_without_evidence_file_does_not_inline_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            handoffs = cwd / "agent-handoffs"
            handoffs.mkdir()
            (handoffs / "sample-status.md").write_text("State: RUNNING\n", encoding="utf-8")

            output = run_script(
                POST_TOOL_USE,
                {
                    "cwd": str(cwd),
                    "tool_input": {"command": "pytest tests"},
                    "tool_response": {"stdout": "VERY_LONG_OUTPUT_SENTINEL", "exit_code": 0},
                },
            )
            evidence = handoffs / "sample-verification.md"
            evidence_text = evidence.read_text(encoding="utf-8") if evidence.is_file() else ""

            self.assertIn("Verification captured", output)
            self.assertNotIn("VERY_LONG_OUTPUT_SENTINEL", output)
            self.assertTrue(evidence.is_file())
            self.assertIn("VERY_LONG_OUTPUT_SENTINEL", evidence_text)

    def test_post_tool_use_prefers_active_status_slug_over_latest_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            handoffs = cwd / "agent-handoffs"
            handoffs.mkdir()
            alpha_status = handoffs / "alpha-status.md"
            beta_evidence = handoffs / "beta-verification.md"
            alpha_status.write_text("State: RUNNING\n", encoding="utf-8")
            beta_evidence.write_text("old beta evidence\n", encoding="utf-8")
            os.utime(beta_evidence, (300, 300))
            os.utime(alpha_status, (200, 200))

            output = run_script(
                POST_TOOL_USE,
                {
                    "cwd": str(cwd),
                    "tool_input": {"command": "pytest tests"},
                    "tool_response": {"stdout": "alpha evidence", "exit_code": 0},
                },
            )
            alpha_evidence = handoffs / "alpha-verification.md"

            self.assertIn("alpha-verification.md", output)
            self.assertTrue(alpha_evidence.is_file())
            self.assertIn("alpha evidence", alpha_evidence.read_text(encoding="utf-8"))
            self.assertNotIn("alpha evidence", beta_evidence.read_text(encoding="utf-8"))

    def test_post_tool_use_rejects_symlink_evidence_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = root / "repo"
            handoffs = cwd / "agent-handoffs"
            handoffs.mkdir(parents=True)
            outside = root / "outside.txt"
            outside.write_text("before\n", encoding="utf-8")
            (handoffs / "escape-status.md").write_text("State: RUNNING\n", encoding="utf-8")
            os.symlink(outside, handoffs / "escape-verification.md")

            output = run_script(
                POST_TOOL_USE,
                {
                    "cwd": str(cwd),
                    "tool_input": {"command": "pytest tests"},
                    "tool_response": {"stdout": "escape payload", "exit_code": 0},
                },
            )

            self.assertIn("Unsafe evidence path", output)
            self.assertEqual(outside.read_text(encoding="utf-8"), "before\n")

    def test_permission_request_quiet_allow_outputs_no_system_message(self) -> None:
        output = run_script(
            PERMISSION_POLICY,
            {"tool_input": {"command": "printf ok"}},
            env={"CUSTOM_WORKFLOW_QUIET_ALLOW": "1"},
        )

        data = json.loads(output)
        self.assertEqual(data["hookSpecificOutput"]["decision"]["behavior"], "allow")
        self.assertNotIn("systemMessage", data)

    def test_boundary_warnings_are_once_per_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = {"CWS_HOOK_STATE_DIR": tmp, "CUSTOM_WORKFLOW_BOUNDARY_WARN_ONCE": "1"}
            event = {"tool_input": {"command": "npm install left-pad"}}

            first = run_script(PRE_TOOL_USE, event, env=env)
            second = run_script(PRE_TOOL_USE, event, env=env)

        self.assertIn("systemMessage", first)
        self.assertEqual(second, "")

    def test_boundary_warnings_remember_non_consecutive_fingerprints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = {"CWS_HOOK_STATE_DIR": tmp, "CUSTOM_WORKFLOW_BOUNDARY_WARN_ONCE": "1"}
            first = run_script(PRE_TOOL_USE, {"tool_input": {"command": "npm install left-pad"}}, env=env)
            second = run_script(PRE_TOOL_USE, {"tool_input": {"command": "npm install is-even"}}, env=env)
            third = run_script(PRE_TOOL_USE, {"tool_input": {"command": "npm install left-pad"}}, env=env)

        self.assertIn("systemMessage", first)
        self.assertIn("systemMessage", second)
        self.assertEqual(third, "")

    def test_pre_tool_use_denies_destructive_command_variants(self) -> None:
        commands = [
            "rm -rf *",
            "rm -fr .",
            "find . -delete",
            "python -c \"import shutil; shutil.rmtree('build')\"",
        ]

        for command in commands:
            with self.subTest(command=command):
                output = run_script(PRE_TOOL_USE, {"tool_input": {"command": command}})
                data = json.loads(output)
                hook = data["hookSpecificOutput"]
                self.assertEqual(hook["permissionDecision"], "deny")
                self.assertIn("destructive", hook["permissionDecisionReason"].lower())

    def test_session_start_compact_context_under_600_chars_and_once_per_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp) / "repo"
            state = Path(tmp) / "state"
            handoffs = cwd / "agent-handoffs"
            handoffs.mkdir(parents=True)
            (handoffs / "sample-status.md").write_text(
                "State: RUNNING\nCurrent checkpoint: CP02 - build\nNext checkpoint: CP03 - verify\nCurrent blocker: none\n",
                encoding="utf-8",
            )
            (handoffs / "sample-progress.md").write_text("Next step: continue\n", encoding="utf-8")
            (handoffs / "sample-execution-package.md").write_text("# package\n", encoding="utf-8")
            env = {
                "CWS_HOOK_STATE_DIR": str(state),
                "CUSTOM_WORKFLOW_CONTEXT_MAX_CHARS": "600",
                "CUSTOM_WORKFLOW_SESSIONSTART_ONCE_PER_FINGERPRINT": "1",
            }

            first = run_script(SESSION_START, {"cwd": str(cwd)}, env=env)
            second = run_script(SESSION_START, {"cwd": str(cwd)}, env=env)

        self.assertLessEqual(len(first), 900)
        self.assertIn("state=RUNNING", first)
        self.assertIn("current=CP02 - build", first)
        self.assertNotIn("Next step: continue", first)
        self.assertLess(len(second), len(first))

    def test_session_start_uses_one_active_slug_for_related_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            handoffs = cwd / "agent-handoffs"
            handoffs.mkdir()
            alpha_status = handoffs / "alpha-status.md"
            alpha_progress = handoffs / "alpha-progress.md"
            alpha_package = handoffs / "alpha-execution-package.md"
            beta_progress = handoffs / "beta-progress.md"
            alpha_status.write_text("State: RUNNING\nCurrent checkpoint: CP01\nNext checkpoint: CP02\n", encoding="utf-8")
            alpha_progress.write_text("alpha progress\n", encoding="utf-8")
            alpha_package.write_text("alpha package\n", encoding="utf-8")
            beta_progress.write_text("beta progress\n", encoding="utf-8")
            os.utime(beta_progress, (200, 200))
            os.utime(alpha_progress, (100, 100))
            os.utime(alpha_package, (100, 100))
            os.utime(alpha_status, (300, 300))

            output = run_script(SESSION_START, {"cwd": str(cwd)})

        self.assertIn("alpha-status.md", output)
        self.assertIn("alpha-progress.md", output)
        self.assertIn("alpha-execution-package.md", output)
        self.assertNotIn("beta-progress.md", output)

    def test_compact_execution_package_passes_validator_profile_compact(self) -> None:
        package = """# Execution Package: Compact
## Goal
Objective: Ship compact validator.
Done when: tests pass.
## Files
Expected: scripts
Must not edit: secrets
Preserve: user changes
## Checkpoints
| ID | Task | Verify |
| --- | --- | --- |
| CP01 | Patch | pytest |
## Runtime
Progress: `agent-handoffs/sample-progress.md`
Status: `agent-handoffs/sample-status.md`
Evidence: `agent-handoffs/sample-verification.md`
Policy: active `/goal`; continue goal-scoped actions; stop only for hard-stop conditions.
## Hard Stops
- destructive command
- payment/purchase
- credential/secret exfiltration
- repeated verification failure without new evidence
## Review Gates
completion_verifier: required
integration_reviewer if multi-component: conditional
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "compact.md"
            path.write_text(package, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), "--profile", "compact", str(path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

        self.assertIn("PASS", result.stdout)

    def test_status_board_update_verify_done_subcommands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            handoffs = Path(tmp) / "agent-handoffs"
            subprocess.run(
                [sys.executable, str(STATUS_BOARD), "sample", "--handoffs-dir", str(handoffs), "--checkpoint", "Build"],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            subprocess.run(
                [sys.executable, str(STATUS_BOARD), "update", "sample", "--handoffs-dir", str(handoffs), "--state", "RUNNING", "--current", "CP01", "--action", "running tests", "--next", "CP02", "--event", "started"],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            subprocess.run(
                [sys.executable, str(STATUS_BOARD), "verify", "sample", "--handoffs-dir", str(handoffs), "--command", "pytest", "--exit", "0", "--status", "PASS"],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            subprocess.run(
                [sys.executable, str(STATUS_BOARD), "done", "sample", "--handoffs-dir", str(handoffs), "--state", "DONE", "--summary", "All checks passed"],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            text = (handoffs / "sample-status.md").read_text(encoding="utf-8")

        self.assertIn("State: DONE", text)
        self.assertIn("Current checkpoint: CP01", text)
        self.assertIn("Current action: running tests", text)
        self.assertIn("| `pytest` |", text)
        self.assertIn("Outcome: All checks passed", text)

    def test_status_board_recent_events_do_not_copy_stop_condition_bullets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            handoffs = Path(tmp) / "agent-handoffs"
            subprocess.run(
                [sys.executable, str(STATUS_BOARD), "sample", "--handoffs-dir", str(handoffs), "--checkpoint", "Build"],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            subprocess.run(
                [sys.executable, str(STATUS_BOARD), "update", "sample", "--handoffs-dir", str(handoffs), "--event", "started"],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            text = (handoffs / "sample-status.md").read_text(encoding="utf-8")

        recent = section(text, "Recent Events")
        self.assertIn("started", recent)
        self.assertNotIn("Hard destructive shell command", recent)
        self.assertNotIn("Payment/purchase action", recent)

    def test_status_board_compact_create_accepts_verify_subcommand(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            handoffs = Path(tmp) / "agent-handoffs"
            subprocess.run(
                [sys.executable, str(STATUS_BOARD), "sample", "--handoffs-dir", str(handoffs), "--checkpoint", "Build", "--compact"],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            subprocess.run(
                [sys.executable, str(STATUS_BOARD), "verify", "sample", "--handoffs-dir", str(handoffs), "--command", "pytest", "--exit", "0", "--status", "PASS"],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            subprocess.run(
                [sys.executable, str(STATUS_BOARD), "verify", "sample", "--handoffs-dir", str(handoffs), "--command", "ruff check", "--exit", "0", "--status", "PASS"],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            text = (handoffs / "sample-status.md").read_text(encoding="utf-8")

        self.assertIn("## Files", text)
        self.assertIn("| `pytest` | 0 | PASS |", text)
        self.assertIn("| `ruff check` | 0 | PASS |", text)
        self.assertNotRegex(text, r"\| `ruff check` \| [0-9TZ:+-]+ \| 0 \| PASS \|")

    def test_agent_toml_contains_output_budget(self) -> None:
        for path in sorted((ROOT / "agents").glob("*.toml")):
            with self.subTest(path=path.name):
                self.assertIn("Output budget:", path.read_text(encoding="utf-8"))

    def test_shared_question_contract_and_token_config_exist(self) -> None:
        shared = SHARED_QUESTION.read_text(encoding="utf-8")
        config = TOKEN_CONFIG.read_text(encoding="utf-8")

        self.assertIn("request_user_input", shared)
        self.assertIn("Do not include an `Other` option manually", shared)
        self.assertIn("model_reasoning_effort = \"medium\"", config)
        self.assertIn("max_threads = 2", config)

    def test_plugin_versions_are_consistent_and_bumped(self) -> None:
        codex = json.loads(CODEX_PLUGIN_JSON.read_text(encoding="utf-8"))
        claude = json.loads(CLAUDE_PLUGIN_JSON.read_text(encoding="utf-8"))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertEqual(codex["version"], "0.3.15")
        self.assertEqual(claude["version"], codex["version"])
        self.assertIn("Current version: `0.3.15`", readme)
        if CLAUDE_MARKETPLACE_JSON.exists():
            marketplace = json.loads(CLAUDE_MARKETPLACE_JSON.read_text(encoding="utf-8"))["plugins"][0]
            self.assertEqual(marketplace["version"], codex["version"])
        elif (REPO_ROOT / ".git").exists():
            self.fail("Claude marketplace manifest is missing from the repository root")

    def test_hook_commands_use_portable_marketplace_paths(self) -> None:
        hooks = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]
        expected_prefix = 'python3 "$HOME/.codex/.tmp/marketplaces/custom-workflow-skillset/plugins/custom-workflow-skillset/scripts/'

        for event_entries in hooks.values():
            for entry in event_entries:
                for hook in entry["hooks"]:
                    command = hook["command"]
                    with self.subTest(command=command):
                        self.assertTrue(command.startswith(expected_prefix))
                        self.assertTrue(command.endswith('.py"'))
                        self.assertNotIn("./scripts/", command)
                        self.assertNotIn("/Users/", command)

    def test_ci_workflow_runs_plugin_contract_checks(self) -> None:
        if not CI_WORKFLOW.exists():
            if (REPO_ROOT / ".git").exists():
                self.fail("CI workflow is missing from the repository root")
            self.skipTest("CI workflow is only packaged at the marketplace repository root")
        workflow = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_deep_interview_contract.py", workflow)
        self.assertIn("package_clean_zip.py", workflow)
        self.assertIn("--profile compact", workflow)

    def test_sync_user_install_global_skill_copies_are_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            subprocess.run(
                [sys.executable, str(SYNC_INSTALL), "--skip-marketplace"],
                cwd=ROOT,
                env={**os.environ, "HOME": str(home)},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

            self.assertFalse((home / ".codex" / "skills" / "plan-goal-runner").exists())
            self.assertFalse((home / ".agents" / "skills" / "plan-goal-runner").exists())
            self.assertTrue((home / ".codex" / "agents" / "repo_explorer.toml").is_file())

    def test_sync_user_install_can_opt_into_codex_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            subprocess.run(
                [sys.executable, str(SYNC_INSTALL), "--skip-marketplace", "--install-codex-skills"],
                cwd=ROOT,
                env={**os.environ, "HOME": str(home)},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

            self.assertTrue((home / ".codex" / "skills" / "plan-goal-runner" / "SKILL.md").is_file())
            self.assertFalse((home / ".agents" / "skills" / "plan-goal-runner").exists())

    def test_sync_user_install_can_disable_legacy_global_skill_copies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            legacy = home / ".codex" / "skills" / "plan-goal-runner"
            legacy.parent.mkdir(parents=True)
            shutil.copytree(ROOT / "skills" / "plan-goal-runner", legacy)

            subprocess.run(
                [sys.executable, str(SYNC_INSTALL), "--skip-marketplace", "--disable-legacy-global-skills"],
                cwd=ROOT,
                env={**os.environ, "HOME": str(home)},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

            disabled = list((home / ".codex" / "skills-disabled").glob("custom-workflow-skillset-*/codex-skills/plan-goal-runner/SKILL.md"))
            self.assertFalse(legacy.exists())
            self.assertEqual(len(disabled), 1)

    def test_high_frequency_docs_are_compact(self) -> None:
        skill_words = PLAN_GOAL_SKILL.read_text(encoding="utf-8").split()
        template_words = EXECUTION_TEMPLATE.read_text(encoding="utf-8").split()

        self.assertLessEqual(len(skill_words), 1200)
        self.assertLessEqual(len(template_words), 650)

    def test_quality_gates_keep_balanced_review_policy(self) -> None:
        skill = PLAN_GOAL_SKILL.read_text(encoding="utf-8")
        compact = (ROOT / "skills" / "plan-goal-runner" / "templates" / "execution-package.compact.md").read_text(encoding="utf-8")
        parallel = (ROOT / "skills" / "parallel-lane-runner" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Run `plan_critic` for every serious plan", skill)
        self.assertIn("three or more components", skill)
        self.assertIn("unclear rollback/compatibility", skill)
        self.assertIn("`completion_verifier` before done", skill)
        self.assertIn("`integration_reviewer` for any multi-component", skill)
        self.assertIn("`verification-before-completion` is required", skill)
        self.assertIn("plan_architect if 3+ components", compact)
        self.assertIn("completion_verifier: required before done", compact)
        self.assertIn("keep it lazy", parallel)


if __name__ == "__main__":
    unittest.main()
