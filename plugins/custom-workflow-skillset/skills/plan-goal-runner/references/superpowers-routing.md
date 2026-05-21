# Superpowers Routing Reference

Use this when the Superpowers plugin is installed. Do not copy Superpowers skill
content into the execution package; route to the relevant Superpowers skill and
record the routing decision.

Custom Workflow remains the outer runtime contract. During an active `/goal`,
Superpowers skills are sub-skills that improve method quality. They must not add
human approval gates for goal-scoped engineering actions when the user already
authorized autonomous goal execution.

## Autonomy Override

When native `/goal` is active, any Superpowers instruction to wait for user
approval, request review, ask whether to continue, present execution options, or
pause for a design/spec review becomes an internal checkpoint.

Required behavior:

1. Record the gate in the progress log.
2. Make the best decision from the objective, execution package, repo facts, and
   acceptance criteria.
3. Append:
   `Auto-resolved under active /goal: <gate> -> <decision and evidence>.`
4. Continue to the next checkpoint.

Only stop for narrow hard-stop conditions: hard destructive command,
payment/purchase, credential or secret exfiltration, explicit user-forbidden
action, impossible file-safety conflict, or repeated verification failure
without new evidence.

## Routing Table

| Trigger | Superpowers skill to use | Custom Workflow adaptation |
| --- | --- | --- |
| Starting a conversation or unsure what skill applies | `Superpowers:using-superpowers` | Use it as a discovery rule, then continue with the custom execution package. |
| Ambiguous creative/product behavior before implementation | `Superpowers:brainstorming` | Use only until requirements are clear enough. In active `/goal`, auto-resolve design approval prompts into recorded assumptions unless ambiguity blocks safe implementation. |
| Multi-step requirements need a concrete plan | `Superpowers:writing-plans` | Convert useful task granularity into `## Execution Plan`; keep handoffs under `agent-handoffs/`; auto-resolve plan execution choices in favor of continuing under the active `/goal`. |
| Feature, bugfix, refactor, or behavior change | `Superpowers:test-driven-development` | Prefer red-green-refactor per checkpoint. If tests are infeasible, record why and use equivalent verification evidence. |
| Bug, failing test, flaky build, unexpected behavior | `Superpowers:systematic-debugging` | Investigate root cause before fixes. Log evidence and hypothesis in progress/evidence files. |
| Work needs isolation from a dirty workspace | `Superpowers:using-git-worktrees` | Use when isolation is worth the setup; otherwise preserve user changes in place. |
| Two or more independent tasks | `Superpowers:dispatching-parallel-agents` | Combine with `parallel-lane-runner`; root `/goal` owns lane registry and integration. |
| Executing independent implementation tasks in-session | `Superpowers:subagent-driven-development` | Use fresh bounded Codex subagents only when file ownership is explicit. Keep root as orchestrator. |
| Executing an existing written plan inline | `Superpowers:executing-plans` | Map checklist tasks to checkpoints; do not pause between checkpoints unless a hard stop is reached. |
| Receiving review feedback | `Superpowers:receiving-code-review` | Validate technical merit before implementing comments. |
| Major completion or pre-merge review | `Superpowers:requesting-code-review` | Prefer bounded reviewer subagents, then `completion_verifier` and `integration_reviewer`; do not wait for human approval before goal-scoped PR/merge actions after verification. |
| Before any completion claim, commit, PR, or merge | `Superpowers:verification-before-completion` | Required. Fresh verification evidence must exist in progress/evidence logs. |
| Branch completion, PR, merge, cleanup | `Superpowers:finishing-a-development-branch` | Use the checklist, but preserve YOLO: proceed with goal-scoped publish/merge actions after verification. |
| Creating or editing skills/plugins | `Superpowers:writing-skills` | Use for skill wording, trigger clarity, and validation. |

## Execution Package Requirement

Compact packages should include only the lazy-load summary:

```md
## Superpowers
Available: yes | no | unknown
Use lazily:
- TDD if behavior changes
- systematic-debugging if failures
- verification-before-completion before done
- parallel/worktree skills only if lanes or isolation are clear

## Superpowers Autonomy Override
- Active when native `/goal` is active or autonomous execution was requested.
- Approval/review/continue prompts from Superpowers are converted into progress checkpoints.
- Record: `Auto-resolved under active /goal: <gate> -> <decision and evidence>.`
- Ask the user only for narrow hard-stop conditions.
```

Full packages may expand this into a routing table when the method choice itself
is a material risk.
