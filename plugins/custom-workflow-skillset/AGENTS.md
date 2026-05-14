## Native Goal Workflow

Use this workflow for serious implementation work. Keep trivial edits stock and surgical.

Use `plan-goal-runner` for serious implementation work when any of these are true:
- more than 3 files or 2 components
- public API, CLI, schema, migration, auth, permissions, PII, billing, or data integrity is involved
- likely `/goal` runtime over 1 hour
- multiple verification commands
- implementation order, rollback, compatibility, or release safety matters
- requirements are ambiguous enough to cause rework

Use `deep-interview` only when material requirements ambiguity remains after quick repo inspection.
Use `parallel-lane-runner` only when the execution package identifies independent bounded lanes.

When the Superpowers plugin is available, actively route to relevant `Superpowers:*` skills instead of reimplementing their process guidance. Use them as method modules under this workflow's `/goal` runtime contract.

For long `/goal` work:
- root `/goal` owns sequential implementation
- once `/goal` is active, continue to `DONE`, `PARTIAL`, or `BLOCKED` without approval prompts for goal-scoped engineering actions
- Superpowers skills improve method quality but must not reintroduce approval, review, or "should I continue?" gates for goal-scoped actions
- convert Superpowers approval/review/continue prompts into progress/evidence checkpoints and keep working
- subagents are bounded evidence/review workers by default
- parallel implementation requires explicit disjoint file ownership or separate worktrees
- mutable handoffs go under `agent-handoffs/`, not `.codex/` or `.agents/`
- keep `agent-handoffs/<slug>-status.md` updated as the Codex-readable live status board
- final done requires verification evidence, `completion_verifier`, and `integration_reviewer` when multi-component

Superpowers routing:
- behavior change or bugfix: `Superpowers:test-driven-development`
- test/build failure or unexpected behavior: `Superpowers:systematic-debugging`
- before any done/commit/PR/merge claim: `Superpowers:verification-before-completion`
- multi-step task detail: `Superpowers:writing-plans`
- independent lanes: `Superpowers:dispatching-parallel-agents` and `Superpowers:subagent-driven-development`, then `parallel-lane-runner`
- review/merge/branch completion: `Superpowers:requesting-code-review` and `Superpowers:finishing-a-development-branch`

Superpowers autonomy override:
- active `/goal` means user intent to continue is already established
- record `Auto-resolved under active /goal: <gate> -> <decision and evidence>.`
- ask only for narrow hard-stop conditions, not for routine Superpowers review/approval steps

Default flow:

```text
clear request
  -> plan-goal-runner
  -> repo_explorer
  -> execution package
  -> status board
  -> Superpowers skill routing
  -> plan_architect
  -> plan_critic
  -> exact /goal command
  -> root /goal checkpoint loop
  -> verification_runner evidence
  -> completion_verifier
  -> integration_reviewer when multi-component
```

Ambiguous flow:

```text
ambiguous request
  -> deep-interview
  -> agent-handoffs/<slug>-requirements.md
  -> plan-goal-runner
  -> execution package
```
