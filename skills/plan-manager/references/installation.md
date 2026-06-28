# Installation

## Claude Code

Default target:

```bash
bash install.sh --target claude --mode symlink
```

Installs to:

```text
~/.claude/skills/plan-manager
```

## Codex CLI

```bash
bash install.sh --target codex --mode symlink
```

Installs to:

```text
~/.codex/skills/plan-manager
```

## Copilot CLI

```bash
bash install.sh --target copilot --mode symlink
```

Installs to:

```text
~/.agents/skills/plan-manager
```

## Verify

```bash
skills/plan-manager/scripts/verify-installation.sh --target ~/.claude/skills/plan-manager
```

Use `--mode copy` when symlinked skills are unsupported. Use `--force` to replace an existing target.
