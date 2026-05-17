# Custom Workflow Skillset

Codex long-goal workflow plugin for serious implementation work that should run
approval-free to a verifiable goal while preserving explicit requirements,
native `/goal` runtime discipline, checkpointed progress, command evidence, and
bounded subagent review.

Current version: `0.3.10`

## Included

- `skills/deep-interview/`
- `skills/plan-goal-runner/`
- `skills/parallel-lane-runner/`
- `agents/*.toml` (15 custom agents)
- `hooks/hooks.json` Codex lifecycle hooks for autonomous long-goal runs
- `.claude-plugin/plugin.json` Claude Code manifest exposing the skills only
- `scripts/*.py` deterministic hook, validation, sync, and packaging helpers
- `AGENTS.md` optional compact project instruction for the native goal workflow
- `docs/codex-config-features-excerpt.toml` recommended Codex config excerpt
- `skills/plan-goal-runner/references/superpowers-routing.md` optional routing map for the Superpowers plugin
- `skills/plan-goal-runner/templates/status-board.md` Codex-readable live status board template
- `scripts/watch_status.py` and the installed `cws-watch` command for tmux/Codex terminal checkpoint TUI viewing
- `MANIFEST.sha256` checksums for all files in the archive
- `TREE.txt` file listing

## Install

### Git marketplace install

Register the GitHub marketplace:

```bash
codex plugin marketplace add R-W-LAB/custom-workflow-skillset
```

Update it later with:

```bash
codex plugin marketplace upgrade custom-workflow-skillset
```

The GitHub repository is laid out as a Codex marketplace at its root, with this
plugin copied under `plugins/custom-workflow-skillset/`.

### Claude Code marketplace install

Codex is the primary plugin target. Claude Code can install the same repository
as a marketplace and use the skill instructions:

```bash
claude plugin marketplace add R-W-LAB/custom-workflow-skillset
claude plugin install custom-workflow-skillset@custom-workflow-skillset
```

Claude Code loads the `skills/` directory. Codex lifecycle hooks and TOML
subagents stay Codex-only because their runtime contracts and output schemas are
not Claude Code components.

### User-wide plugin package

Place this folder under your home-local plugin directory:

```bash
mkdir -p ~/plugins
cp -R . ~/plugins/custom-workflow-skillset
```

Then add a marketplace entry in `~/.agents/plugins/marketplace.json`:

```json
{
  "name": "custom-workflow-skillset",
  "source": {
    "source": "local",
    "path": "./plugins/custom-workflow-skillset"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Coding"
}
```

The plugin manifest exposes the skills through `skills = "./skills/"`.
Custom agent TOMLs are packaged in `agents/` and should also be installed into
Codex's custom-agent directory:

```bash
mkdir -p ~/.codex/agents
cp agents/*.toml ~/.codex/agents/
```

### User-wide direct skills/agents install

If you do not want to use a plugin marketplace entry, install the skills and
agents directly:

```bash
mkdir -p ~/.agents/skills ~/.codex/agents
cp -R skills/* ~/.agents/skills/
cp agents/*.toml ~/.codex/agents/
```

### Sync this plugin after edits

From the plugin root:

```bash
python3 scripts/sync_user_install.py
```

This syncs:

- `~/plugins/custom-workflow-skillset`
- `~/.codex/plugins/cache/local/custom-workflow-skillset/<version>`
- `~/.codex/agents`
- `~/.agents/skills`
- `~/.codex/skills`
- `~/.agents/plugins/marketplace.json`
- `~/.local/bin/cws-watch`

### Repo-scoped install

For a single repository:

```bash
mkdir -p .agents/skills .codex/agents
cp -R skills/* .agents/skills/
cp agents/*.toml .codex/agents/
```

If you want the compact workflow guidance active in that repository, merge the
relevant section from `AGENTS.md` into the repo's own `AGENTS.md`.

## Recommended Config

```toml
model = "gpt-5.5"
model_reasoning_effort = "high"
sandbox_mode = "danger-full-access"
approval_policy = "never"
web_search = "cached"

[features]
goals = true
multi_agent = true
codex_hooks = true
shell_snapshot = true

[agents]
max_threads = 4
max_depth = 1
job_max_runtime_seconds = 1800
```

Use `web_search = "live"` temporarily only when version-specific external docs
must be checked live. For a more conservative session, use
`sandbox_mode = "workspace-write"` and `approval_policy = "on-request"`, but
that can interrupt long `/goal` runs.

## Operating Model

This workflow is intentionally opt-in and heavyweight:

- `deep-interview` for ambiguous requirements and requirement handoff generation.
- `plan-goal-runner` for serious implementation planning, review gate, and native `/goal` command generation.
- `parallel-lane-runner` only for independent bounded lanes with low conflict risk.
- When Superpowers is installed, this plugin actively routes to relevant `Superpowers:*` skills for TDD, debugging, plan writing, review, verification, worktree isolation, and subagent-driven execution.
- Custom agents are intended mostly for review, repo exploration, verification, and bounded specialist checks rather than replacing Codex's native implementation loop.
- Lifecycle hooks provide context hints, evidence capture, and hard destructive-command guards. They do not replace `/goal`, progress logs, or reviewer gates.

## Codex Live Status Board

For long `/goal` work, keep this file open in Codex:

```text
agent-handoffs/<slug>-status.md
```

It is a Markdown dashboard meant for the Codex file viewer/editor, not a
terminal watch pane. The root `/goal` runner updates it whenever checkpoint
state, current action, verification evidence, blockers, subagent lanes, or final
state changes.

The execution package still owns the plan, and the progress/verification files
still own durable evidence:

```text
agent-handoffs/<slug>-execution-package.md
agent-handoffs/<slug>-status.md
agent-handoffs/<slug>-progress.md
agent-handoffs/<slug>-verification.md
```

Create an initial board manually from the template or with:

```bash
python3 scripts/status_board.py <slug> \
  --title "<title>" \
  --objective "<objective>" \
  --checkpoint "<checkpoint 1>" \
  --checkpoint "<checkpoint 2>"
```

In a tmux right pane or Codex app terminal, run:

```bash
cws-watch
```

`cws-watch` renders a Korean checkpoint dashboard by default. In tmux-style
right panes, it automatically switches to a narrow vertical layout below 72
columns so checkpoint names do not fight the pane width. It does not dump the
whole Markdown file unless `--raw` is used.

Useful options:

```bash
cws-watch --slug <slug>
cws-watch --interval 1
cws-watch --details
cws-watch --all
cws-watch --layout narrow
cws-watch --lang en
cws-watch --raw
cws-watch --plain
cws-watch --once
cws-watch --handoffs-dir docs/agent-handoffs
```

Interactive keys:

```text
d  검증/서브에이전트/최근 이벤트 상세 보기
a  전체 체크포인트 보기
r  원본 Markdown 보기
q  종료
```

Run it from the repository workspace. It searches `agent-handoffs/` and
`docs/agent-handoffs/`, waits when no status board exists yet, and automatically
switches to the newest `*-status.md`.

## Superpowers Integration

Custom Workflow is the outer long-goal runtime. Superpowers is a method library.
When both are available, serious execution packages include a
`## Superpowers Skill Routing` section so the root agent can actively load the
right Superpowers skill instead of improvising the process.

Default routing:

- `Superpowers:test-driven-development` for behavior changes, bugfixes, and refactors.
- `Superpowers:systematic-debugging` for test failures, build failures, flakes, and unexpected behavior.
- `Superpowers:verification-before-completion` before claiming done, committing, creating PRs, or merging.
- `Superpowers:writing-plans` when requirements need granular task planning.
- `Superpowers:dispatching-parallel-agents` and `Superpowers:subagent-driven-development` when independent bounded lanes are actually safe.
- `Superpowers:receiving-code-review`, `Superpowers:requesting-code-review`, and `Superpowers:finishing-a-development-branch` around review, PR, merge, and cleanup.
- `Superpowers:using-git-worktrees` when isolation is worth the setup cost.
- `Superpowers:writing-skills` when editing this plugin's skills or adding new ones.

During an active `/goal`, Superpowers user-review checkpoints are adapted into
progress/evidence checkpoints unless a real ambiguity or hard-stop condition
blocks safe progress. The integration should improve discipline without
reintroducing approval prompts for goal-scoped engineering actions.

### Superpowers Autonomy Override

Active `/goal` means the user's intent to continue is already established. If a
Superpowers skill asks for user approval, user review, execution choice, or
"should I continue?", the root agent must convert that into a progress/evidence
checkpoint and continue.

Required progress entry:

```text
Auto-resolved under active /goal: <Superpowers gate> -> <decision and evidence>.
```

This override applies to design/spec review prompts, plan execution choices,
pre-PR review prompts, branch finishing options, and continuation questions.
It does not override narrow hard stops: hard destructive commands,
payment/purchase, credential or secret exfiltration, explicit user-forbidden
actions, impossible file-safety conflicts, or repeated verification failure
without new evidence.

## Autonomous Goal Policy

The default mode is YOLO for goal-scoped engineering actions. If an action is
part of the user's objective or the execution package, Codex should proceed
without asking for approval and record the action in progress/evidence logs.

Allowed without approval when goal-scoped:

- pushing branches and tags
- opening or updating PRs
- posting GitHub comments
- closing or marking duplicate issues
- merging PRs after acceptance criteria and verification pass
- dependency installs/updates
- network-backed documentation or API calls
- schema migrations or release steps included in the objective/package

Hard-stop exceptions remain narrow:

- broad destructive shell commands such as `git reset --hard`, force-cleaning the worktree, or recursive force deletes
- payment/purchase actions
- credential or secret exfiltration
- actions explicitly forbidden by the current user message or execution package

Default long-goal flow:

```text
clear request
  -> plan-goal-runner
  -> repo_explorer
  -> inline requirements or requirements handoff
  -> execution package
  -> parallelization verdict
  -> plan_architect
  -> plan_critic
  -> exact /goal command
  -> root /goal checkpoint loop
  -> verification_runner evidence
  -> completion_verifier
  -> integration_reviewer
  -> DONE / PARTIAL / BLOCKED
```

## Hook Policy

The bundled hooks are YOLO by default for goal-scoped engineering work, with a narrow hard destructive-command guard:

- `SessionStart` injects recent long-goal handoff context when `agent-handoffs/` exists.
- `UserPromptSubmit` only suggests `$plan-goal-runner` when a prompt appears to meet serious-plan criteria.
- `PreToolUse` denies clearly destructive commands. It only warns on dependency/migration/network boundaries unless `CUSTOM_WORKFLOW_HOOKS_STRICT=1`.
- `PermissionRequest` denies clearly destructive permission requests and auto-allows non-destructive requests so long `/goal` work does not stop for routine prompts. Set `CUSTOM_WORKFLOW_HOOKS_STRICT=1` to deny dependency/migration/network boundaries instead of YOLO-allowing them.
- `PostToolUse` captures test/build/lint/typecheck evidence. It appends only to an existing `agent-handoffs/<slug>-verification.md`; otherwise it returns additional context for the root agent.
- `Stop` can request continuation when a recent progress log and the latest assistant message both identify a clear next checkpoint. It keeps continuing while progress evidence changes, and stops when `DONE`, `PARTIAL`, `BLOCKED`, a hard destructive boundary, payment, or secret-exfiltration risk appears.

Useful environment toggles:

```bash
CUSTOM_WORKFLOW_HOOKS_STRICT=1
CUSTOM_WORKFLOW_STOP_MAX_AGE_HOURS=2
CUSTOM_WORKFLOW_STOP_MAX_CONTINUATIONS=25
```

## Validation Helpers

Validate an execution package:

```bash
python3 skills/plan-goal-runner/scripts/validate_execution_package.py \
  agent-handoffs/<slug>-execution-package.md
```

Create a clean zip:

```bash
python3 scripts/package_clean_zip.py
```
