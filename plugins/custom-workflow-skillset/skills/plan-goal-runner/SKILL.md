---
name: plan-goal-runner
description: Turn a requirements handoff or clear request into a reviewed execution package, native /goal runtime contract, progress log, bounded parallelization decision, and final verification plan.
---

# Plan Goal Runner

Use this skill for non-trivial implementation work that should be planned, reviewed, tracked through native `/goal`, and verified after completion.

This is a long-goal harness, not a prompt ritual. Keep model reasoning flexible, but make the runtime contract strict: objective, checkpoints, progress log, verification commands, narrow hard-stop conditions, and final verification.

## Purpose

Produce an autonomous execution package and exact native `/goal` command for Codex long-running work. Do not treat a Markdown checklist as a replacement for Codex native goal tracking.

Once a native `/goal` is active, YOLO execution is the default: continue until `DONE`, `PARTIAL`, or `BLOCKED`. Do not stop for user approval on goal-scoped engineering actions, including externally visible engineering actions, when they are part of the objective or execution package.

When the Superpowers plugin is installed, actively route to relevant `Superpowers:*` skills as method modules. Do not duplicate their content; read the matching skill when its trigger applies, then record the routing decision in the execution package or progress log.

Superpowers approval/review checkpoints do not override an active `/goal`. Convert them into local progress/evidence checkpoints, record the decision, and continue unless a narrow hard-stop condition is reached.

For short/surgical work, do not use this skill. Use stock Codex behavior with narrow verification.

## Handoff Paths

Runtime handoff files must be writable by the normal Codex workspace sandbox. Do **not** write mutable handoffs under `.codex/` or `.agents/`.

Use:

```text
agent-handoffs/<slug>-requirements.md
agent-handoffs/<slug>-execution-package.md
agent-handoffs/<slug>-status.md
agent-handoffs/<slug>-progress.md
agent-handoffs/<slug>-verification.md
```

`docs/agent-handoffs/` is acceptable for teams that prefer docs, but `agent-handoffs/` is the default because it is obvious, writable, and easy to diff.

## Inputs

This skill can start from either:

1. A direct user request in the current conversation.
2. An existing requirements handoff:

```text
agent-handoffs/<slug>-requirements.md
```

A handoff is preferred for ambiguous or high-risk work, but it is not required. If no handoff exists, first create a short "Inline Requirements" section inside the execution package from the user's request and repo facts.

Use `deep-interview` only when ambiguity remains material after quick repo inspection. Do not force deep-interview for clear requests.

## Serious Plan Criteria

Treat a task as a serious plan when any of the following is true:

- expected work spans more than 3 files or 2 components
- public API, CLI, schema, migration, auth, permissions, PII, billing, or data integrity is involved
- the task is likely to run under `/goal` for more than one hour
- acceptance criteria require multiple verification commands
- implementation order matters
- rollback, compatibility, or release safety matters
- requirements are ambiguous enough to cause rework

For serious plans:

- use `repo_explorer` before planning in brownfield repos
- use `plan_architect` and `plan_critic` before long implementation
- use `completion_verifier` before done
- use `integration_reviewer` for multi-component or multi-lane work
- if Superpowers is available, use the Superpowers routing table below to load relevant process skills

## Workflow

1. Read the direct request and/or requirements handoff plus current repo guidance.
2. If no handoff exists, derive inline requirements: outcome, in-scope, non-goals if obvious, assumptions, acceptance criteria, and verification ideas.
3. Spawn `repo_explorer` for brownfield facts unless the change is trivial.
4. If repo facts reveal material ambiguity, either ask the minimum necessary question or use `deep-interview` for broader clarification.
5. Identify Superpowers routing for the task. Read `references/superpowers-routing.md` when needed.
6. Draft an execution plan with file touchpoints, tests, risks, rollback, autonomous external-action policy, Superpowers skill routing, Superpowers autonomy override, and narrow hard-stop conditions.
   - Default to YOLO for goal-scoped engineering actions. Add only explicit user-forbidden boundaries from the current user message.
7. Spawn `parallel_planner` to classify whether native subagent parallel lanes are safe.
8. Spawn `plan_architect` to review architecture fit and tradeoffs.
9. Revise the plan if needed.
10. Spawn `plan_critic` to validate executability.
11. If rejected, revise and repeat the critic gate once; ask the user only if a blocker cannot be resolved from repo/context.
12. Write `agent-handoffs/<slug>-execution-package.md` and include the Goal Runtime Contract.
13. Run the execution package validator when available:
    `python3 <this-skill>/scripts/validate_execution_package.py agent-handoffs/<slug>-execution-package.md`
14. Fix missing contract sections before presenting the plan.
15. Initialize `agent-handoffs/<slug>-status.md` from `templates/status-board.md` or:
    `python3 <this-skill>/scripts/status_board.py <slug> --title "<title>" --objective "<objective>" --checkpoint "<checkpoint>"`
16. Present the exact `/goal ...` command and the status-board file path for the user to keep open in Codex. If the current interface cannot set native `/goal`, stop for the user to enter it in Codex TUI/App.
17. If already inside Codex with an active `/goal`, or explicitly asked to proceed, continue under the Goal Runtime Contract until `DONE`, `PARTIAL`, or `BLOCKED`.

## Superpowers Integration

Superpowers is a method library. Custom Workflow is the outer `/goal` runtime. If both are available:

- Use `Superpowers:using-superpowers` as a discovery rule when unsure which process skill applies.
- Use `Superpowers:test-driven-development` before behavior-changing implementation; prefer red-green-refactor per checkpoint.
- Use `Superpowers:systematic-debugging` before fixing test failures, build failures, flaky behavior, or unexpected output.
- Use `Superpowers:verification-before-completion` before claiming done, committing, opening PRs, or merging.
- Use `Superpowers:writing-plans` when a multi-step requirement needs task-level plan detail; fold the useful output into `## Execution Plan`.
- Use `Superpowers:dispatching-parallel-agents` and `Superpowers:subagent-driven-development` only when the parallelization verdict allows independent lanes; root `/goal` still owns orchestration and integration.
- Use `Superpowers:receiving-code-review`, `Superpowers:requesting-code-review`, and `Superpowers:finishing-a-development-branch` around review, PR, merge, and cleanup work.

During an active `/goal`, adapt Superpowers user-review checkpoints into progress/evidence checkpoints unless a real ambiguity or hard-stop condition blocks safe progress. Superpowers should raise method quality, not reintroduce approval prompts for goal-scoped actions.

## Superpowers Autonomy Override

When a native `/goal` is active or the user explicitly requested autonomous execution:

- Treat Superpowers skills as method guidance, not human-in-the-loop gates.
- If a Superpowers skill says to ask for approval, wait for review, ask whether to continue, commit a design doc for review, or offer execution choices, convert that step into an internal checkpoint.
- Record the auto-resolution in the progress log:
  `Auto-resolved under active /goal: <Superpowers gate> -> <decision and evidence>.`
- Continue with the next checkpoint when the objective, execution package, repo facts, and acceptance criteria provide enough information to proceed.
- Ask the user only when a narrow hard-stop condition is reached: hard destructive command, payment/purchase, credential or secret exfiltration, explicit user-forbidden action, impossible file-safety conflict, or repeated verification failure without new evidence.
- Do not mark `BLOCKED` merely because a Superpowers skill requested user review or approval.

## Execution Package Structure

````md
# Execution Package: <title>

## Native Goal Command

```text
/goal Complete <objective> according to agent-handoffs/<slug>-execution-package.md.

First read the execution package. Maintain agent-handoffs/<slug>-progress.md.

Keep agent-handoffs/<slug>-status.md updated as the live Codex status board. Update it whenever checkpoint status, verification status, blockers, or current/next action changes.

Do not treat this as a general backlog. Work only toward this single objective and its acceptance criteria.

Because this `/goal` is active, continue without asking for approval on goal-scoped engineering actions.

Superpowers Autonomy Override is active: convert any Superpowers approval/review/continue prompt into a recorded progress checkpoint and keep working unless a narrow hard-stop condition is reached.

Work checkpoint-by-checkpoint. After each checkpoint:
1. summarize what changed,
2. run the relevant verification command(s),
3. append progress, evidence, and remaining work to the progress log,
4. continue unless a narrow hard-stop condition is triggered.

Do not broaden scope beyond the execution package. Do not stop merely because an action is externally visible if it is goal-scoped, including branch pushes, PR creation/updates, GitHub comments, issue duplicate/close actions, or PR merges after final verification. Continue through goal-scoped dependency, network, schema migration, and release steps when they are part of the objective or execution package. Stop only for hard destructive shell commands, payment/purchase actions, credential or secret exfiltration, edits outside the execution package, explicit user-forbidden actions, or if the same verification failure repeats twice without new evidence.

Done only when all acceptance criteria are satisfied and final verification passes: <commands>.
```

## Source Request / Handoff

## Inline Requirements
<!-- Required when no separate requirements handoff exists. Summarize outcome, scope, non-goals if obvious, assumptions, acceptance criteria, and verification ideas. -->

## Acceptance Criteria

## File / Ownership Boundaries
- Expected touchpoints:
- Must not edit:
- User-owned or pre-existing changes to preserve:

## Execution Plan

## Autonomous Action Policy
- Goal-scoped external engineering actions may proceed without user approval.
- This includes branch push, PR open/update, GitHub comments, issue duplicate/close actions, and PR merge when final verification passes.
- Record externally visible actions in the progress log.
- Stop only for hard destructive shell commands, payment/purchase actions, credential or secret exfiltration, explicit user-forbidden actions, or repeated verification failure.

## Live Status Board
- File: `agent-handoffs/<slug>-status.md`
- Intended use: keep this Markdown file open in Codex while `/goal` runs.
- Update cadence:
  - after creating the execution package
  - before starting a checkpoint
  - after completing a checkpoint
  - after each verification command
  - when a blocker, subagent lane, Superpowers auto-resolution, or final state changes
- Required visible fields:
  - State: PLANNING | RUNNING | VERIFYING | DONE | PARTIAL | BLOCKED
  - Objective
  - Progress count and percentage
  - Current checkpoint/action
  - Next checkpoint
  - Checkpoint table
  - Verification table
  - Recent events

## Superpowers Skill Routing
- Available: yes | no | unknown
- Required before implementation:
  - `Superpowers:test-driven-development` for behavior changes, or reason skipped:
  - `Superpowers:systematic-debugging` for failures, or reason not applicable:
- Required before done:
  - `Superpowers:verification-before-completion`
- Conditional:
  - `Superpowers:writing-plans` for detailed task decomposition:
  - `Superpowers:using-git-worktrees` if isolation is needed:
  - `Superpowers:dispatching-parallel-agents` / `Superpowers:subagent-driven-development` if lanes are independent:
  - `Superpowers:requesting-code-review` / `Superpowers:finishing-a-development-branch` for review, PR, merge, or cleanup:

## Superpowers Autonomy Override
- Active when native `/goal` is active or the user requested autonomous execution.
- Superpowers approval/review/continue prompts are not user gates during active `/goal`.
- Convert them into progress/evidence checkpoints and continue.
- Record each conversion as:
  `Auto-resolved under active /goal: <gate> -> <decision and evidence>.`
- User input is required only for narrow hard-stop conditions.

## Goal Runtime Contract

Progress log:
- `agent-handoffs/<slug>-progress.md`

Live status board:
- `agent-handoffs/<slug>-status.md`

Verification evidence:
- `agent-handoffs/<slug>-verification.md`

Baseline:
- Current git status:
- Initial failing/passing verification:
- Known broken tests unrelated to this task:

User / pre-existing changes:
- Pre-existing modified files:
- Pre-existing untracked files:
- Must not overwrite user changes:
- If a target file has user changes unrelated to this task, preserve them and continue when possible; stop only if safe editing is impossible.

Checkpoint loop:
1. Choose the next smallest checkpoint from the execution package.
2. Update the status board: mark the checkpoint RUNNING, set Current action, and refresh Last updated.
3. Make one focused change set.
4. Run targeted verification for that checkpoint.
5. Update the status board: mark verification state and checkpoint state.
6. Append progress log:
   - checkpoint name
   - files changed
   - commands run
   - result
   - evidence file updates, if any
   - status board update
   - next step
   - blockers / risks
7. Continue until `DONE`, `PARTIAL`, or `BLOCKED` unless a narrow hard-stop condition is triggered.

Checkpoint cadence:
- At the end of each execution package step.
- Before changing component boundaries.
- Before public API/schema/migration changes.
- After any failed verification retry.

Narrow hard-stop conditions:
- Acceptance criteria cannot be verified.
- Same failure repeats twice without new evidence.
- Required change touches files outside the execution package and cannot be kept in scope.
- Hard destructive shell command is needed.
- Payment/purchase action is needed.
- Credential or secret exfiltration risk is discovered.
- Explicit user-forbidden action is needed.
- Existing behavior risk is discovered that is not covered by the plan and cannot be mitigated within scope.
- Tests fail in a way that cannot be attributed to the current change.

Finalization:
1. Run full verification commands.
2. Use `verification_runner` for command evidence when needed.
3. Run `completion_verifier`.
4. Run `integration_reviewer` for multi-component or multi-lane work.
5. Update `agent-handoffs/<slug>-status.md` to DONE, PARTIAL, or BLOCKED.
6. Produce final summary with diff, tests, risks, and remaining issues.

## Parallelization Decision
Verdict: PARALLEL_SAFE | PARALLEL_SAFE_WITH_LIMITS | SEQUENTIAL_RECOMMENDED | SEQUENTIAL_REQUIRED
Reason:

Default for long `/goal` work: root `/goal` owns sequential implementation. Use parallel subagents primarily for bounded read-only evidence/review. Parallel implementation requires explicit disjoint file ownership or separate worktrees.

## Lane Handoffs

### Lane <A> — <name>
Agent:
Mode: read_only_evidence | implementation_disjoint | review_verification | sequential_required
Timebox: 5-30 minutes unless the execution package says otherwise
Allowed files:
Must not edit:
Task:
Completion evidence:
Dependencies:

## Sequential Gates

## Verification Plan

## Rollback / Stop Conditions

## Reviewer Notes
- Architect:
- Critic:
````

## `/goal` Rules

The `/goal` command should include runtime discipline, not lane detail.

Include:

- final objective
- reference to `agent-handoffs/<slug>-execution-package.md`
- requirement to read the execution package first
- requirement to keep `agent-handoffs/<slug>-status.md` updated as a live Codex status board
- requirement to maintain `agent-handoffs/<slug>-progress.md`
- checkpoint loop
- verification commands/checks
- narrow hard-stop conditions
- explicit instruction to continue without approval prompts for goal-scoped engineering actions while `/goal` is active
- Superpowers skill routing when the Superpowers plugin is available
- Superpowers Autonomy Override that converts approval/review/continue prompts into progress checkpoints
- final done criteria

Do not put all lane details inside `/goal`; keep those in the execution package.

## Specialist Routing

Core specialists:

- `repo_explorer` before planning in brownfield repos.
- `plan_architect` before `plan_critic`.
- `plan_critic` before execution package finalization.
- `completion_verifier` after implementation claims.
- `integration_reviewer` after multiple lanes or multi-component changes.

Use when relevant:

- `requirements_analyst` for weak requirements.
- `parallel_planner` for lane classification.
- `verification_runner` to run package-listed or checkpoint-required verification commands and record exact evidence without editing files.
- `test_engineer`, `security_reviewer`, `api_reviewer`, `performance_reviewer`, `external_researcher` as conditional evidence/review lanes.
- `parallel_implementer` only for declared disjoint implementation lanes.
- `parallel_verifier` to check individual lane evidence.

## Reasoning Effort Policy

- Root `/goal` runner: `high` by default; `xhigh` for large migrations/refactors or ambiguous multi-component work.
- Planner / critic / integration: `high` or `xhigh` when the plan is risky.
- Explorer / test map / external docs: `medium` by default.
- Implementation worker: `medium` or `high`; avoid long-running implementation subagents unless using disjoint files or worktrees.

## Start Rule

If the user is outside Codex or the current interface cannot set `/goal` directly:

- produce the execution package,
- provide the exact `/goal` command,
- stop for the user to enter it.

If the user is inside Codex and explicitly asks to proceed:

- set or instruct the user to set the `/goal`,
- then continue with the Goal Runtime Contract,
- maintain the progress log until `DONE`, `PARTIAL`, or `BLOCKED`.
