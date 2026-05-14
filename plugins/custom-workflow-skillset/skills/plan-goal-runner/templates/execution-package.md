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
<!-- Required when no separate requirements handoff exists. -->

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

### Lane A — <name>
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
