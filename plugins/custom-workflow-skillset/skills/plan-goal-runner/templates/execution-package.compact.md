# Execution Package: <title>

## Goal
Objective:
Done when:

## Files
Expected:
Must not edit:
Preserve:

## Checkpoints
| ID | Task | Verify |
| --- | --- | --- |
| CP01 |  |  |

## Runtime
Progress: `agent-handoffs/<slug>-progress.md`
Status: `agent-handoffs/<slug>-status.md`
Evidence: `agent-handoffs/<slug>-verification.md`
Policy: active `/goal`; continue goal-scoped actions; stop only for hard-stop conditions.
Superpowers: lazy; `verification-before-completion` before done when available.

## Hard Stops
- destructive command
- payment/purchase
- credential/secret exfiltration
- explicit user-forbidden action
- repeated verification failure without new evidence

## Review Gates
plan_critic: required for serious plan
plan_architect if 3+ components, unclear rollback/compatibility, API/schema/auth/migration, or coupling risk:
completion_verifier: required before done
integration_reviewer if multi-component:
