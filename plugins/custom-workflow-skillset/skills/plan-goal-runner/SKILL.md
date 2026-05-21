---
name: plan-goal-runner
description: Turn a requirements handoff or clear request into a reviewed execution package, native /goal runtime contract, progress log, bounded parallelization decision, and final verification plan.
---

# Plan Goal Runner

Use for serious implementation work that needs durable `/goal` tracking, checkpoints, evidence, reviewer gates, or rollback discipline. Do not use for surgical edits.

## Trigger

Use when any apply:
- more than 3 files or 2 components
- public API, CLI, schema, migration, auth, permissions, PII, billing, or data integrity
- likely runtime over 1 hour
- multiple verification commands
- implementation order, rollback, compatibility, or release safety matters
- ambiguity could cause rework after quick repo inspection

## Output Files

Write mutable handoffs under `agent-handoffs/` by default:

```text
agent-handoffs/<slug>-execution-package.md
agent-handoffs/<slug>-status.md
agent-handoffs/<slug>-progress.md
agent-handoffs/<slug>-verification.md
```

If requirements are still materially unclear, use `deep-interview` first and write `agent-handoffs/<slug>-requirements.md`.

## Core Flow

1. Read the request, repo guidance, and any requirements handoff.
2. Derive inline requirements when no handoff exists: outcome, scope, non-goals, assumptions, acceptance criteria, and verification ideas.
3. Use `repo_explorer` for brownfield facts unless the change is clearly small.
4. Decide Superpowers routing lazily. Record availability and needed skill names; read `references/superpowers-routing.md` only when method details affect the work. If Superpowers is available, `verification-before-completion` is required at the final done/commit/PR gate.
5. Draft a scoped execution package from `templates/execution-package.compact.md` by default. Use `templates/execution-package.md` only for high-risk full plans.
6. Classify parallelism: default to `SEQUENTIAL_RECOMMENDED` unless independent lanes are already clear. Call `parallel_planner` only for likely parallel lanes or explicit user parallelism.
7. Prefer root-owned sequential implementation. Use subagents primarily for bounded evidence/review; use implementation lanes only with explicit disjoint files or separate worktrees.
8. Run `plan_critic` for every serious plan. Run `plan_architect` first for architecture boundary changes, public API/schema/auth/migration risk, three or more components, multi-component coupling, unclear rollback/compatibility, or if `plan_critic` returns `NEEDS_REVISION`.
9. Validate the package:
   `python3 <this-skill>/scripts/validate_execution_package.py --profile compact agent-handoffs/<slug>-execution-package.md`
10. Initialize `agent-handoffs/<slug>-status.md` with `templates/status-board.md` or:
    `python3 <this-skill>/scripts/status_board.py <slug> --title "<title>" --objective "<objective>" --checkpoint "<checkpoint>"`
11. Provide the exact `/goal` command. If already explicitly asked to proceed in Codex, continue checkpoint-by-checkpoint until `DONE`, `PARTIAL`, or `BLOCKED`.

## Runtime Policy

Use policy IDs in the execution package instead of repeating long prose:
- `CWS-GOAL-CONTRACT-v1`: objective-bound checkpoint loop with progress, status, and verification evidence files.
- `CWS-AUTONOMY-v1`: active `/goal` means goal-scoped engineering actions can proceed without approval prompts.
- `CWS-HARD-STOPS-v1`: stop only for unverifiable acceptance criteria, repeated failures without new evidence, out-of-scope edits, hard destructive commands, payment/purchase, credential or secret exposure, explicit user-forbidden actions, or unsafe pre-existing-change conflicts.
- `CWS-SUBAGENTS-v1`: root owns orchestration; subagents need bounded task, mode, files, timebox, dependencies, and completion evidence.

The execution package template includes a self-contained policy summary for generated handoffs.

## Package Profiles

Compact package:
- `Goal`, `Files`, `Checkpoints`, `Runtime`, `Hard Stops`, and `Review Gates`.
- `Runtime` names progress/status/evidence paths and the active `/goal` policy.
- `Superpowers` may be a short lazy-load list, with `verification-before-completion` marked required before done when available.

Full package:
- Use only when high-risk details need explicit long-form policy text.
- Validate with the default full profile:
  `python3 <this-skill>/scripts/validate_execution_package.py agent-handoffs/<slug>-execution-package.md`

Adaptive reasoning:
- Root `/goal`, planner, and reviewer work starts at medium effort.
- Raise effort only for public API, schema, auth, billing, PII, migration, multi-component coupling, or failed evidence.

## Full Execution Package Must Include

- Native Goal Command with `/goal Complete ...`
- Source Request / Handoff
- Inline Requirements when no requirements handoff exists
- Acceptance Criteria
- File / Ownership Boundaries, including pre-existing user changes
- Execution Plan
- Autonomous Action Policy
- Live Status Board
- Superpowers Skill Routing and Superpowers Autonomy Override when Superpowers is available
- Goal Runtime Contract with progress, status, and verification paths
- Parallelization Decision
- Lane Handoffs when lanes exist
- Sequential Gates
- Verification Plan
- Rollback / Stop Conditions
- Reviewer Notes for `plan_architect`, `plan_critic`, `completion_verifier`, and `integration_reviewer` when applicable

## Specialist Routing

Core:
- `repo_explorer` before planning brownfield work unless the change is clearly small.
- `plan_critic` before finalizing every serious package.
- `completion_verifier` before done.
- `integration_reviewer` for any multi-component, multi-lane, or cross-contract change.

Conditional:
- `requirements_analyst` for weak requirements.
- `plan_architect` for architecture/API/schema/auth/migration, three or more components, unclear rollback/compatibility, or coupling risk.
- `parallel_planner` only when independent lanes are likely or explicitly requested.
- `verification_runner` for command evidence without source edits.
- `test_engineer`, `security_reviewer`, `api_reviewer`, `performance_reviewer`, `external_researcher` when their domain affects correctness.
- `parallel_implementer` only for declared disjoint implementation lanes.
- `parallel_verifier` for lane evidence.

## Start Rule

If native `/goal` cannot be set from the current interface, write the execution package, give the exact `/goal` command, and stop for the user to enter it. If the user already asked Codex to proceed, continue under the package contract and maintain progress/status/evidence files.
