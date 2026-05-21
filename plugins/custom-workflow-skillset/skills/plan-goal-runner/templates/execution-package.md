# Execution Package: <title>

## Native Goal Command

```text
/goal Complete <objective> according to agent-handoffs/<slug>-execution-package.md.

First read the execution package. Maintain agent-handoffs/<slug>-progress.md, keep agent-handoffs/<slug>-status.md current, and record evidence in agent-handoffs/<slug>-verification.md.

Use the policy summary in this package: CWS-GOAL-CONTRACT-v1, CWS-AUTONOMY-v1, CWS-HARD-STOPS-v1, and CWS-SUBAGENTS-v1. Work checkpoint-by-checkpoint and continue until DONE, PARTIAL, or BLOCKED.

Done only when all acceptance criteria are satisfied and final verification passes: <commands>.
```

## Source Request / Handoff

## Inline Requirements
<!-- Required when no separate requirements handoff exists. Summarize outcome, scope, non-goals, assumptions, acceptance criteria, and verification ideas. -->

## Acceptance Criteria

## File / Ownership Boundaries
- Expected touchpoints:
- Must not edit:
- User-owned or pre-existing changes to preserve:

## Execution Plan

## Autonomous Action Policy
- Goal-scoped engineering actions may proceed under CWS-AUTONOMY-v1.
- Record externally visible actions in the progress log.
- Stop only for CWS-HARD-STOPS-v1 conditions.

## Live Status Board
- File: `agent-handoffs/<slug>-status.md`
- Update when checkpoint state, verification state, blockers, subagent lanes, or final state changes.
- Fields: State, Objective, Progress, Current action, Next checkpoint, Checkpoints, Verification, Recent events.

## Superpowers Skill Routing
- Available: yes | no | unknown
- Required before implementation:
  - `Superpowers:test-driven-development` for behavior changes, or reason skipped:
  - `Superpowers:systematic-debugging` for failures, or reason not applicable:
- Required before done:
  - `Superpowers:verification-before-completion`
- Conditional:
  - `Superpowers:writing-plans`:
  - `Superpowers:using-git-worktrees`:
  - `Superpowers:dispatching-parallel-agents` / `Superpowers:subagent-driven-development`:
  - `Superpowers:requesting-code-review` / `Superpowers:finishing-a-development-branch`:

## Superpowers Autonomy Override
- Active when native `/goal` is active or autonomous execution was requested.
- Convert Superpowers approval/review/continue prompts into progress checkpoints.
- Record: `Auto-resolved under active /goal: <gate> -> <decision and evidence>.`
- Ask only for CWS-HARD-STOPS-v1 conditions.

## Goal Runtime Contract
- Policy IDs: CWS-GOAL-CONTRACT-v1, CWS-AUTONOMY-v1, CWS-HARD-STOPS-v1, CWS-SUBAGENTS-v1.
- Progress log: `agent-handoffs/<slug>-progress.md`
- Live status board: `agent-handoffs/<slug>-status.md`
- Verification evidence: `agent-handoffs/<slug>-verification.md`

Policy summary:
- CWS-GOAL-CONTRACT-v1: work only toward this package's objective and acceptance criteria; keep progress, status, and verification files current.
- CWS-AUTONOMY-v1: proceed on goal-scoped engineering actions without routine approval prompts.
- CWS-HARD-STOPS-v1: stop for unverifiable criteria, repeated failures without new evidence, out-of-scope edits, destructive commands, payment, credential/secret exposure, explicit user-forbidden actions, or unsafe pre-existing-change conflicts.
- CWS-SUBAGENTS-v1: root owns orchestration; lanes need mode, files, timebox, dependencies, and evidence.

Baseline:
- Current git status:
- Initial failing/passing verification:
- Known broken tests unrelated to this task:

User / pre-existing changes:
- Pre-existing modified files:
- Pre-existing untracked files:
- Must not overwrite user changes:

Checkpoint loop:
1. Mark the next checkpoint RUNNING in the status board.
2. Make one focused change set.
3. Run targeted verification.
4. Append files changed, commands, result, evidence, next step, blockers, and risks to the progress log.
5. Continue unless a CWS-HARD-STOPS-v1 condition appears.

Narrow hard-stop conditions:
- See CWS-HARD-STOPS-v1; list task-specific additions here:

Finalization:
1. Run full verification commands.
2. Use `verification_runner` for command evidence when useful.
3. Run `completion_verifier`.
4. Run `integration_reviewer` for multi-component, multi-lane, or cross-contract work.
5. Set status to DONE, PARTIAL, or BLOCKED.

## Parallelization Decision
Verdict: PARALLEL_SAFE | PARALLEL_SAFE_WITH_LIMITS | SEQUENTIAL_RECOMMENDED | SEQUENTIAL_REQUIRED
Reason:

## Lane Handoffs

### Lane A - <name>
Agent:
Mode: read_only_evidence | implementation_disjoint | review_verification | sequential_required
Timebox:
Allowed files:
Must not edit:
Task:
Completion evidence:
Dependencies:

## Sequential Gates

## Verification Plan

## Rollback / Stop Conditions

## Reviewer Notes
- plan_critic: required for serious plan
- plan_architect: required for architecture/API/schema/auth/migration, 3+ components, unclear rollback/compatibility, or coupling risk
- completion_verifier: required before done
- integration_reviewer: required for multi-component, multi-lane, or cross-contract work
