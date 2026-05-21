#!/usr/bin/env python3
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import shlex
import sys
import tempfile
from pathlib import Path


def load_event() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def emit(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False))


def emit_context(event_name: str, text: str) -> None:
    if text.strip():
        emit({"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": text}})


def no_stop_output() -> None:
    emit({"continue": True})


def cwd_path(event: dict) -> Path:
    return Path(event.get("cwd") or os.getcwd()).expanduser().resolve()


def tool_input(event: dict) -> dict:
    value = event.get("tool_input") or {}
    return value if isinstance(value, dict) else {}


def command_text(event: dict) -> str:
    parts = []
    ti = tool_input(event)
    for key in ("command", "cmd", "script", "input", "description", "reason"):
        value = event.get(key)
        if isinstance(value, str) and value:
            parts.append(value)
    for key in ("command", "cmd", "script", "input"):
        value = ti.get(key)
        if isinstance(value, str):
            parts.append(value)
    for key in ("request", "permission_request", "approval_request"):
        value = event.get(key)
        if isinstance(value, dict):
            for nested_key in ("command", "cmd", "description", "reason", "message"):
                nested_value = value.get(nested_key)
                if isinstance(nested_value, str) and nested_value:
                    parts.append(nested_value)
        elif isinstance(value, str) and value:
            parts.append(value)
    if parts:
        return "\n".join(parts)
    if ti:
        return json.dumps(ti, ensure_ascii=False, sort_keys=True)
    return json.dumps(event, ensure_ascii=False, sort_keys=True)


def response_text(event: dict) -> str:
    value = event.get("tool_response")
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        parts = []
        for key in ("stdout", "stderr", "output", "message", "error"):
            item = value.get(key)
            if isinstance(item, str) and item:
                parts.append(f"{key}: {item}")
        if parts:
            return "\n".join(parts)
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if value is None:
        return ""
    return str(value)


def exit_code(event: dict):
    value = event.get("tool_response")
    if isinstance(value, dict):
        for key in ("exit_code", "exitCode", "status", "returncode"):
            if key in value:
                return value[key]
    return None


def find_handoff_dir(cwd: Path) -> Path | None:
    for base in [cwd, *cwd.parents]:
        for name in ("agent-handoffs", "docs/agent-handoffs"):
            candidate = base / name
            if candidate.is_dir():
                return candidate
        if base == base.parent:
            break
    return None


def latest_file(cwd: Path, suffix: str) -> Path | None:
    handoffs = find_handoff_dir(cwd)
    if not handoffs:
        return None
    files = list(handoffs.glob(f"*{suffix}"))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def slug_from_handoff(path: Path, suffix: str) -> str | None:
    return path.name[: -len(suffix)] if path.name.endswith(suffix) else None


def handoff_path_for_slug(cwd: Path, slug: str, suffix: str) -> Path | None:
    handoffs = find_handoff_dir(cwd)
    if not handoffs:
        return None
    return handoffs / f"{slug}{suffix}"


def active_handoff_paths(cwd: Path) -> dict[str, Path | str | None]:
    source = latest_file(cwd, "-status.md")
    source_suffix = "-status.md"
    if not source:
        for suffix in ("-execution-package.md", "-progress.md", "-verification.md"):
            source = latest_file(cwd, suffix)
            source_suffix = suffix
            if source:
                break
    if not source:
        return {}

    slug = slug_from_handoff(source, source_suffix)
    if not slug:
        return {}

    paths: dict[str, Path | str | None] = {"slug": slug}
    for label, suffix in (
        ("status", "-status.md"),
        ("package", "-execution-package.md"),
        ("progress", "-progress.md"),
        ("verification", "-verification.md"),
    ):
        path = handoff_path_for_slug(cwd, slug, suffix)
        paths[label] = path if path and path.exists() else None
        paths[f"{label}_path"] = path
    return paths


def read_tail(path: Path, max_chars: int = 4000) -> str:
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return ""
    return text[-max_chars:]


def rel(path: Path, cwd: Path) -> str:
    try:
        return str(path.relative_to(cwd))
    except ValueError:
        return str(path)


def snippet(text: str, limit: int = 1800) -> str:
    clean = re.sub(r"\n{3,}", "\n\n", text.strip())
    if len(clean) <= limit:
        return clean
    return clean[:limit] + "\n...[truncated]"


def env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, "").strip())
    except ValueError:
        return default


def token_profile() -> str:
    value = os.environ.get("CWS_TOKEN_PROFILE") or os.environ.get("CUSTOM_WORKFLOW_TOKEN_PROFILE") or "minimal"
    value = value.strip().lower()
    return value if value in {"minimal", "standard", "full"} else "minimal"


def include_context_tails() -> bool:
    return token_profile() in {"standard", "full"}


def include_tool_output_context() -> bool:
    return token_profile() == "full"


def hook_state_dir() -> Path:
    root = os.environ.get("CWS_HOOK_STATE_DIR")
    path = Path(root) if root else Path(tempfile.gettempdir()) / "custom-workflow-skillset-hooks"
    path.mkdir(parents=True, exist_ok=True)
    return path


def state_file(name: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", name).strip("-") or "state"
    return hook_state_dir() / f"{safe}.json"


def load_state(name: str) -> dict:
    try:
        data = json.loads(state_file(name).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(name: str, data: dict) -> None:
    try:
        state_file(name).write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    except OSError:
        pass


def fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def first_fingerprint(name: str, key: str, value: str) -> bool:
    state = load_state(name)
    digest = fingerprint(value)
    existing = state.get(key)
    if isinstance(existing, list):
        seen = [item for item in existing if isinstance(item, str)]
    elif isinstance(existing, str):
        seen = [existing]
    else:
        seen = []
    if digest in seen:
        return False
    seen.append(digest)
    state[key] = seen[-env_int("CUSTOM_WORKFLOW_FINGERPRINT_SET_MAX", 100) :]
    save_state(name, state)
    return True


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


SEVERE_COMMAND_PATTERNS = [
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard is destructive."),
    (r"\bgit\s+clean\s+-[^\n;]*[fdx][^\n;]*\b", "git clean with force/delete flags is destructive."),
    (r"\brm\s+-[^\n;]*r[^\n;]*f[^\n;]*(/|\$HOME|~|\.)\b", "broad recursive force delete is destructive."),
    (r"\bshutil\.rmtree\s*\(", "programmatic recursive delete is destructive."),
    (r"\bfs\.rm(?:Sync)?\s*\([^;\n]*recursive\s*:\s*true", "programmatic recursive delete is destructive."),
    (r"\bchmod\s+-R\s+777\b", "recursive chmod 777 is unsafe."),
    (r"\bchown\s+-R\b", "recursive chown is high-impact."),
    (r"\bdd\s+.*\bof=/dev/", "writing directly to block devices is destructive."),
    (r"\bdiskutil\s+(erase|partition|apfs\s+delete)\b", "disk erase/partition commands are destructive."),
    (r"\b(drop\s+database|drop\s+schema|truncate\s+table)\b", "destructive database operation."),
]

BOUNDARY_COMMAND_PATTERNS = [
    (r"\b(npm|pnpm|yarn|bun)\s+(install|add|remove|update|upgrade)\b", "dependency change"),
    (r"\b(pip|pip3|uv|poetry|pipenv)\s+(install|add|remove|sync|lock)\b", "Python dependency change"),
    (r"\b(brew|apt|apt-get|dnf|yum)\s+install\b", "system dependency installation"),
    (r"\b(prisma|sequelize|typeorm|rails|alembic|django-admin|manage\.py)\s+.*\b(migrate|migration)\b", "schema migration"),
    (r"\b(curl|wget)\s+.*\|\s*(sh|bash|python|python3)\b", "network-fetched script execution"),
]

VERIFICATION_COMMAND_PATTERNS = [
    r"\b(test|pytest|vitest|jest|mocha|rspec|go\s+test|cargo\s+test|mvn\s+test|gradle\s+test)\b",
    r"\b(lint|eslint|ruff|flake8|clippy|rubocop)\b",
    r"\b(typecheck|tsc|mypy|pyright|sorbet)\b",
    r"\b(build|cargo\s+build|go\s+build|npm\s+run\s+build|pnpm\s+build|yarn\s+build)\b",
]


def first_match(patterns, command: str):
    for pattern, reason in patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return reason
    return None


def _shell_tokens(command: str) -> list[str]:
    normalized = re.sub(r"(;|&&|\|\|)", " ", command)
    try:
        return shlex.split(normalized)
    except ValueError:
        return []


def _command_name(token: str) -> str:
    return Path(token).name


def _broad_delete_target(target: str) -> bool:
    return target in {
        "*",
        ".",
        "./",
        "./*",
        "..",
        "../",
        "../*",
        "/",
        "/*",
        "~",
        "~/",
        "~/*",
        "$HOME",
        "$HOME/",
        "$HOME/*",
        "${HOME}",
        "${HOME}/",
        "${HOME}/*",
    }


def _rm_recursive_force_reason(tokens: list[str]) -> str | None:
    for index, token in enumerate(tokens):
        if _command_name(token) != "rm":
            continue
        flags = set()
        targets = []
        after_options = False
        for arg in tokens[index + 1 :]:
            if arg == "--":
                after_options = True
                continue
            if not after_options and arg.startswith("-") and arg != "-":
                if arg == "--recursive":
                    flags.add("r")
                elif arg == "--force":
                    flags.add("f")
                elif not arg.startswith("--"):
                    flags.update(arg.lstrip("-"))
                continue
            targets.append(arg)
        if {"r", "f"}.issubset(flags) and any(_broad_delete_target(target) for target in targets):
            return "broad recursive force delete is destructive."
    return None


def _find_delete_reason(tokens: list[str]) -> str | None:
    for index, token in enumerate(tokens):
        if _command_name(token) != "find":
            continue
        args = tokens[index + 1 :]
        if "-delete" not in args:
            continue
        roots = []
        for arg in args:
            if arg.startswith("-"):
                break
            roots.append(arg)
        if not roots:
            roots = ["."]
        if any(_broad_delete_target(root) for root in roots):
            return "broad find -delete is destructive."
    return None


def severe_command_reason(command: str) -> str | None:
    reason = first_match(SEVERE_COMMAND_PATTERNS, command)
    if reason:
        return reason
    tokens = _shell_tokens(command)
    return _rm_recursive_force_reason(tokens) or _find_delete_reason(tokens)


def boundary_command_reason(command: str) -> str | None:
    return first_match(BOUNDARY_COMMAND_PATTERNS, command)


def is_verification_command(command: str) -> bool:
    return any(re.search(pattern, command, re.IGNORECASE) for pattern in VERIFICATION_COMMAND_PATTERNS)


def strict_mode() -> bool:
    return os.environ.get("CUSTOM_WORKFLOW_HOOKS_STRICT", "").lower() in {"1", "true", "yes", "on"}
