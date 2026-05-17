---
name: deep-interview
description: Clarify ambiguous feature/change requests before implementation; interview one question at a time and write an implementation-ready handoff.
---

# Deep Interview

Use this skill when the user request is ambiguous, broad, high-risk, or likely to cause rework if implemented immediately.

Do not use this skill for clear surgical edits. Long `/goal` work may use this first, but only when requirements ambiguity is material.

If the Superpowers plugin is available and the request involves creative/product design, use `Superpowers:brainstorming` as a companion method for exploring alternatives. Keep this skill responsible for the final implementation-ready handoff under `agent-handoffs/`.

## Purpose

Produce `agent-handoffs/<slug>-requirements.md` that is ready for planning. Do not implement code.

Runtime handoffs must be written outside `.codex/` and `.agents/` so Codex can update related execution/progress files under normal workspace-write sandboxing.

## Interview Isolation

Deep-interview owns requirements clarification only. Do not call `create_goal`, do not start `/goal`, and do not route to `plan-goal-runner` while the interview is still active, even when the request would otherwise meet serious-plan criteria.

Write the requirements handoff first. Move to planning or goal setup only after the requirements handoff is written and the user explicitly chooses that next step.

## Workflow

1. Create or choose a short task slug.
2. If this is a brownfield repo, spawn `repo_explorer` first to gather facts that can be discovered locally.
3. Ask only questions that cannot be answered from the repo or provided context.
4. Ask one question at a time.
5. Use choice-assisted questions by default:
   - Use the Plan mode adapter when `request_user_input` is available.
   - Otherwise, use the Markdown fallback format below.
   - Give 2-3 recommended answer options when useful.
   - Mark the safest/default recommendation when there is a clear best option.
   - Keep each option short and decision-oriented, not a long essay.
   - Explain the tradeoff in one line when the options materially affect scope, risk, or implementation cost.
   - If the user gives a free-form answer, accept it and continue; do not force them into the listed options.
   - Do not offer fake choices for purely factual questions that should be answered from the repo.
6. Resolve, at minimum:
   - desired outcome
   - user-visible behavior
   - scope and non-goals
   - decision boundaries: default to agent autonomy for goal-scoped engineering actions; identify only explicit user-forbidden actions, payment/purchase boundaries, credential/secret risks, or hard destructive operations
   - acceptance criteria
   - constraints: compatibility, data migration, UX, security, performance, deadline
   - likely verification commands or manual checks
7. If the handoff is still weak, spawn `requirements_analyst` for a read-only gap review.
8. Record any Superpowers skill used or intentionally skipped.
9. Write the handoff document.

## Choice-Assisted Question Format

### Plan mode adapter

If `request_user_input` is available, use it instead of Markdown options for choice-assisted interview questions:

- Ask exactly one question per call.
- Provide 2-3 mutually exclusive options.
- Put the recommended option first and suffix its label with `(Recommended)`.
- Keep option labels to 1-5 words and descriptions to one short sentence about impact or tradeoff.
- Do not include an `Other` option manually; the Plan mode client adds a free-form Other path automatically.
- After the user answers, normalize the selected or free-form answer into the Decision Log.

### Markdown fallback

Use this format when `request_user_input` is unavailable:

```md
Question <n>: <one clear decision question>

Recommended options:
A. <option> — <short tradeoff>
B. <option> — <short tradeoff>
C. <option> — <short tradeoff, optional>
D. Other / custom answer — describe what you want instead.

My default recommendation: <A/B/C> because <one-line reason>.
```

Rules:
- Prefer 2 options when the decision is simple; use 3 only when there are genuinely distinct paths.
- Keep the question answerable in one message.
- If the user answers with a letter, record the selected meaning, not just the letter.
- If the user mixes options, normalize it into a concrete requirement and confirm only if the mix creates ambiguity.
- Avoid turning every interview into a quiz: use open-ended questions when options would bias the user or hide an important unknown.

## Readiness Gate

Proceed to planning only when:

- the outcome is clear enough to test
- non-goals are explicit
- at least one acceptance criterion is verifiable
- material assumptions are listed
- open questions are either answered or marked as accepted assumptions

## Handoff Output

Write:

```text
agent-handoffs/<slug>-requirements.md
```

Use this structure:

```md
# Requirements Handoff: <title>

## Source Request

## Desired Outcome

## In Scope

## Non-Goals

## Decision Boundaries

## Acceptance Criteria

## Constraints

## Repo Facts

## Assumptions

## Decision Log
<!-- Record important interview choices, e.g. Q1: selected B = MVP-first scope. -->

## Superpowers Routing
<!-- Record `Superpowers:brainstorming` or other Superpowers skills used/skipped during requirements clarification. -->

## Open Questions

## Likely Touchpoints

## Verification Ideas
```
