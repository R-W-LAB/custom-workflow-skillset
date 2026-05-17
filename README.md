# Custom Workflow Skillset Marketplace

Git-backed Codex plugin marketplace for `custom-workflow-skillset`.
Codex remains the primary plugin format; the repository also includes Claude
Code marketplace metadata for users who want the same skills there.

## Install

```bash
codex plugin marketplace add R-W-LAB/custom-workflow-skillset
```

Then install or enable `custom-workflow-skillset` from the `Custom Workflow Skillset` marketplace in Codex.

## Update

```bash
codex plugin marketplace upgrade custom-workflow-skillset
```

## Claude Code

Claude Code users can add the same GitHub repository as a Claude marketplace:

```bash
claude plugin marketplace add R-W-LAB/custom-workflow-skillset
claude plugin install custom-workflow-skillset@custom-workflow-skillset
```

The Claude manifest exposes the workflow skills under `skills/`. Codex-specific
hooks and TOML subagents remain packaged for Codex and are not enabled as Claude
components.

## Layout

```text
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
plugins/custom-workflow-skillset/
```

The plugin manifest lives at:

```text
plugins/custom-workflow-skillset/.codex-plugin/plugin.json
plugins/custom-workflow-skillset/.claude-plugin/plugin.json
```
