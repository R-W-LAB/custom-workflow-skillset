---
name: parallel-lane-runner
description: Execute bounded independent lanes from a Codex execution package using native subagents without tmux/team/mailbox orchestration.
---

# Parallel Lane Runner

Use this skill only after `plan-goal-runner` produced an execution package with a parallelization verdict of `PARALLEL_SAFE` or `PARALLEL_SAFE_WITH_LIMITS`.

For long `/goal` work, parallelism is a support tool, not the default implementation strategy. The root `/goal` runner owns overall execution and integration.

If the Superpowers plugin is available, keep it lazy: use `Superpowers:dispatching-parallel-agents` or `Superpowers:subagent-driven-development` only when lane suitability is unclear, a lane is failing or drifting, or method discipline affects correctness. Keep Custom Workflow's lane registry, file ownership, and root integration rules as the controlling contract.

## Purpose

Run bounded in-session parallel work with Codex native subagents while avoiding edit conflicts and runaway fan-out.

## Hard Rules

- Do not invent new lanes not present in the execution package unless the current objective or package requires them.
- Keep subagent tasks bounded, typically 5-30 minutes.
- Prefer read-only evidence/review lanes over long-running implementation lanes.
- Do not parallelize edits to the same file, schema, migration, lockfile, generated output, or shared config.
- Use multiple implementation lanes only with explicit non-overlapping file ownership or separate worktrees.
- If a lane touches disallowed files, stop that lane and let the root continue or re-plan from the execution package.
- Do not let subagents broaden scope or run their own multi-hour goals.
- Final integration review is sequential.

## Good Parallel Lanes

- repository exploration
- test gap mapping
- official docs / dependency behavior research
- API compatibility review
- security review
- performance review
- independent small fixes in disjoint files
- implementation in separate worktrees

## Risky / Usually Sequential

- multiple agents editing the same file
- schema/migration/lockfile/generated-output changes without a single owner
- broad refactors with unclear ownership
- tasks blocked by unresolved design decisions
- tightly coupled changes that require constant cross-agent coordination
- long implementation lanes expected to run for hours

## Workflow

1. Read `agent-handoffs/<slug>-execution-package.md`.
2. Confirm the verdict is `PARALLEL_SAFE` or `PARALLEL_SAFE_WITH_LIMITS`.
3. If suitability is unclear or a lane is already drifting/failing, route through `Superpowers:dispatching-parallel-agents` or `Superpowers:subagent-driven-development` without changing file ownership.
4. Group lanes by dependency:
   - preflight sequential gates
   - parallel read-only evidence lanes
   - parallel disjoint implementation lanes
   - post-lane verification
   - final integration review
5. Spawn independent lanes simultaneously with full lane handoff text and explicit timebox.
6. Collect outputs and evidence.
7. Run `parallel_verifier` for lane-specific PASS/FAIL/PARTIAL when needed.
8. Apply required fixes sequentially if conflicts or review findings appear.
9. Use `verification_runner` for package-listed or checkpoint-required verification commands when command evidence is needed.
10. Spawn `completion_verifier` and `integration_reviewer` before declaring done.

## Orchestrator Protocol

The root agent owns:

- task decomposition
- lane registry
- file ownership
- wait / continue decisions
- integration decisions
- final `DONE` / `PARTIAL` / `BLOCKED` state

Maintain a lightweight lane registry in the progress log or in:

```text
agent-handoffs/<slug>-agents.md
```

Subagents must return:

```md
STATUS:
- CLEAR | WATCH | BLOCKED | DONE | PARTIAL

LANE:
- lane id
- assigned scope
- files inspected
- files touched, if any

EVIDENCE:
- commands run
- relevant output
- file references
- assumptions confirmed / rejected

BLOCKERS:
- missing requirement
- unsafe scope expansion
- hard destructive/payment/secret boundary
- needs parent decision

NEEDS_PARENT_DECISION:
- yes/no
- exact question
- recommended next action
```

Output budget:
- Default lane report: 300-500 tokens.
- Evidence is command + exit/status + file path or short finding, not pasted logs.
- Read-only evidence lanes return top 5 findings only.

Use follow-up messages to subagents sparingly. Send input only for:

- blocker clarification
- evidence gaps
- lane drift back into assigned scope

Do not use subagent follow-up messages as a general chat loop. If repeated clarification is needed, let the root continue or re-plan from the execution package.
Do not send more than one follow-up to a lane unless it is `BLOCKED`.

## Lane Output Contract

Each lane must report:

```md
## Lane Result: <name>
Status: PASS | FAIL | PARTIAL | BLOCKED
Files changed:
Files inspected:
Commands run:
Evidence:
Issues / risks:
Follow-up needed:
```

## Final Output Contract

Report:

- lanes run
- changes made
- verification evidence
- unresolved issues
- final verdict: DONE | PARTIAL | BLOCKED
