---
name: design-grill
description: Stress-test broad product, architecture, workflow, or domain designs before requirements handoff or execution planning; use when the user asks to grill, critique, pressure-test, or resolve design tradeoffs.
---

# Design Grill

Use this skill when the user has a broad plan or design that should be challenged before it becomes requirements or an execution package.

Do not use this for narrow implementation clarifications. Use `deep-interview` when the user already knows the broad design and only needs implementation-ready requirements.

## Purpose

Resolve the decision tree behind a design and produce:

```text
agent-handoffs/<slug>-design-grill.md
```

This handoff should make later `deep-interview` or `plan-goal-runner` work sharper, but it is not itself an implementation plan.

Runtime handoffs must be written outside `.codex/` and `.agents/`.

## Interview Isolation

Design-grill owns design stress testing only. Do not call `create_goal`, do not start `/goal`, and do not route to `plan-goal-runner` while the grill is still active, even when the design implies serious implementation work.

Write the design handoff first. Move to requirements clarification or goal setup only after the handoff is written and the user explicitly chooses that next step.

## Workflow

1. Create or choose a short task slug.
2. If this is a brownfield repo, inspect existing code/docs for facts that can answer questions before asking.
3. Identify the main design branches: user outcome, system boundaries, data ownership, workflows, failure modes, compatibility, rollout, and rejected alternatives.
4. Ask one question at a time.
5. Provide your recommended answer for each question.
6. Use choice-assisted questions by default:
   - Use the Plan mode adapter when `request_user_input` is available.
   - Otherwise, use the Markdown fallback format below.
   - Give 2-3 decision-oriented options when useful.
   - Use open-ended questions when options would hide a real unknown.
7. Walk dependencies between decisions. Do not ask downstream questions until the upstream decision they depend on is settled.
8. Capture resolved decisions, rejected alternatives, assumptions, and scenarios as they emerge.
9. Stop when remaining uncertainty is small enough to hand off to `deep-interview` or `plan-goal-runner`.
10. Write the design handoff.

## Choice-Assisted Question Format

### Plan mode adapter

If `request_user_input` is available, use it instead of Markdown options for choice-assisted grill questions:

- Ask exactly one question per call.
- Provide 2-3 mutually exclusive options.
- Put the recommended option first and suffix its label with `(Recommended)`.
- Keep option labels to 1-5 words and descriptions to one short sentence about impact or tradeoff.
- Do not include an `Other` option manually; the Plan mode client adds a free-form Other path automatically.
- After the user answers, normalize the selected or free-form answer into the Decision Log.

### Markdown fallback

Use this format when `request_user_input` is unavailable:

```md
Question <n>: <one design decision question>

Recommended options:
A. <option> — <short tradeoff>
B. <option> — <short tradeoff>
C. <option> — <short tradeoff, optional>
D. Other / custom answer — describe what you want instead.

My default recommendation: <A/B/C> because <one-line reason>.
```

## Readiness Gate

Write the handoff when:

- the design objective is explicit
- major alternatives have been considered or intentionally skipped
- user-visible scenarios and edge cases have been probed
- system/domain boundaries are clear enough to become requirements
- risks and assumptions are listed
- remaining open questions are either low-risk or explicitly accepted

## Handoff Output

Write:

```text
agent-handoffs/<slug>-design-grill.md
```

Use `templates/design-grill-handoff.md` as the structure.
