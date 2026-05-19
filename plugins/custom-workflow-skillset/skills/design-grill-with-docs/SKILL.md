---
name: design-grill-with-docs
description: Stress-test a design against repo domain language, CONTEXT.md, ADRs, and code facts before planning; use when the user asks to grill with docs, align terminology, or update domain docs.
---

# Design Grill With Docs

Use this skill when a design needs to be challenged against the repository's documented domain model, glossary, ADRs, and code facts.

Do not use this for ordinary implementation planning. Use `design-grill` when no documentation updates are expected. Use `deep-interview` when the design is already settled and only implementation requirements remain.

## Purpose

Resolve design terminology and durable decisions while keeping domain documentation accurate. Produce:

```text
agent-handoffs/<slug>-design-grill-with-docs.md
```

Runtime handoffs must be written outside `.codex/` and `.agents/`.

## Interview Isolation

Design-grill-with-docs owns design/documentation clarification only. Do not call `create_goal`, do not start `/goal`, and do not route to `plan-goal-runner` while the grill is still active, even when the design implies serious implementation work.

Write the design/docs handoff first. Move to requirements clarification or goal setup only after the handoff is written and the user explicitly chooses that next step.

## Documentation Safety

- Do not edit implementation files.
- Read existing `CONTEXT-MAP.md`, `CONTEXT.md`, and `docs/adr/` before proposing documentation changes.
- Create docs lazily: only create `CONTEXT.md` or `docs/adr/` after a term or decision is actually resolved.
- Update `CONTEXT.md` only for domain concepts meaningful to domain experts, not implementation details.
- Preserve existing documentation style unless it conflicts with the bundled formats.
- If the repo has multiple contexts and the relevant context is unclear, ask before editing.
- Offer ADRs sparingly. Create or offer an ADR only when the decision is hard to reverse, surprising without context, and the result of a real tradeoff.

Reference formats:

- `references/CONTEXT-FORMAT.md`
- `references/ADR-FORMAT.md`

## Workflow

1. Create or choose a short task slug.
2. Inspect repo docs first:
   - root `CONTEXT-MAP.md`
   - root or context-local `CONTEXT.md`
   - root or context-local `docs/adr/`
3. Inspect code when the user's claim can be checked locally.
4. Challenge terminology conflicts immediately.
5. Ask one question at a time.
6. Provide your recommended answer for each question.
7. Use choice-assisted questions by default:
   - Use the Plan mode adapter when `request_user_input` is available.
   - Otherwise, use the Markdown fallback format below.
8. Stress-test concrete scenarios that clarify boundaries between concepts.
9. When a term is resolved, update the relevant `CONTEXT.md` inline using `CONTEXT-FORMAT.md`.
10. When an ADR-worthy decision is resolved, offer the ADR and write it only when the user accepts or the current instruction explicitly authorizes docs updates.
11. Record docs changes and remaining ambiguities in the handoff.

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
Question <n>: <one domain/design decision question>

Recommended options:
A. <option> — <short tradeoff>
B. <option> — <short tradeoff>
C. <option> — <short tradeoff, optional>
D. Other / custom answer — describe what you want instead.

My default recommendation: <A/B/C> because <one-line reason>.
```

## Readiness Gate

Write the handoff when:

- resolved terms have canonical names or accepted ambiguity
- code/doc contradictions are listed
- domain boundaries are clear enough to become requirements
- docs changes are recorded or intentionally deferred
- ADR-worthy decisions are recorded, skipped with reason, or offered
- remaining open questions are low-risk or explicitly accepted

## Handoff Output

Write:

```text
agent-handoffs/<slug>-design-grill-with-docs.md
```

Use `templates/design-grill-with-docs-handoff.md` as the structure.
