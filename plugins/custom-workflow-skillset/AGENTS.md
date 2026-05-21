## Native Goal Workflow

Keep trivial edits stock and surgical. Use `plan-goal-runner` only for serious work: more than 3 files or 2 components, public API/CLI/schema/auth/PII/billing/data-integrity risk, long runtime, multiple verification commands, ordered rollout, rollback, compatibility, or material ambiguity.

Use `deep-interview` only when quick repo inspection leaves material requirements ambiguity. Use `parallel-lane-runner` only when the execution package declares bounded independent lanes.

For long `/goal` work:
- root owns orchestration and usually implementation
- mutable handoffs live under `agent-handoffs/`
- keep `<slug>-status.md`, `<slug>-progress.md`, and `<slug>-verification.md` current
- prefer compact execution packages and `validate_execution_package.py --profile compact`; use full packages only for high-risk work
- update status boards with `status_board.py update|verify|done` when possible instead of reopening the whole Markdown board
- use policy IDs instead of repeating long prose: `CWS-GOAL-CONTRACT-v1`, `CWS-AUTONOMY-v1`, `CWS-HARD-STOPS-v1`, `CWS-SUBAGENTS-v1`
- route to `Superpowers:*` lazily as method modules only when needed; convert routine approval/review/continue prompts into progress evidence during active `/goal`
- final done requires verification evidence plus `completion_verifier`; add `integration_reviewer` only for multi-component, multi-lane, or cross-contract work

Default flow: clear request -> `plan-goal-runner` -> repo facts -> compact execution package/status board -> `plan_critic` -> `plan_architect` only for architecture/API/schema/auth/migration/coupling risk or critic revision -> `/goal` checkpoint loop -> verification -> reviewer gates -> DONE / PARTIAL / BLOCKED.

Ambiguous flow: `deep-interview` -> `agent-handoffs/<slug>-requirements.md` -> `plan-goal-runner`.
