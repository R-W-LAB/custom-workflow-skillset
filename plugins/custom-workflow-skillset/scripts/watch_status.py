#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import select
import shutil
import subprocess
import sys
import termios
import time
import tty
import unicodedata
from dataclasses import dataclass
from pathlib import Path


STATUS_COLORS = {
    "DONE": "32",
    "PASS": "32",
    "READY": "32",
    "RUNNING": "36",
    "VERIFYING": "33",
    "WATCH": "33",
    "PARTIAL": "35",
    "BLOCKED": "31",
    "FAIL": "31",
    "TODO": "90",
    "PLANNING": "34",
}

STATUS_ICONS = {
    "TODO": ("○", "o"),
    "RUNNING": ("▶", ">"),
    "VERIFYING": ("◐", "~"),
    "DONE": ("●", "*"),
    "PASS": ("●", "*"),
    "READY": ("●", "*"),
    "PARTIAL": ("◒", "%"),
    "BLOCKED": ("✕", "x"),
    "FAIL": ("✕", "x"),
    "WATCH": ("!", "!"),
    "PLANNING": ("●", "*"),
}

STATUS_LABELS = {
    "ko": {
        "DONE": "완료",
        "PASS": "통과",
        "READY": "준비",
        "RUNNING": "진행",
        "VERIFYING": "검증",
        "WATCH": "관찰",
        "PARTIAL": "부분",
        "BLOCKED": "차단",
        "FAIL": "실패",
        "TODO": "대기",
        "PLANNING": "계획",
        "UNKNOWN": "불명",
    },
    "en": {
        "DONE": "DONE",
        "PASS": "PASS",
        "READY": "READY",
        "RUNNING": "RUNNING",
        "VERIFYING": "VERIFYING",
        "WATCH": "WATCH",
        "PARTIAL": "PARTIAL",
        "BLOCKED": "BLOCKED",
        "FAIL": "FAIL",
        "TODO": "TODO",
        "PLANNING": "PLANNING",
        "UNKNOWN": "UNKNOWN",
    },
}

TEXT = {
    "ko": {
        "app": "목표 현황",
        "refresh": "갱신",
        "path": "파일",
        "now": "현재",
        "checkpoint": "체크",
        "action": "작업",
        "next": "다음",
        "blocker": "차단",
        "none": "없음",
        "checkpoints": "체크포인트",
        "verification": "검증",
        "subagents": "Superpowers / 서브에이전트",
        "recent": "최근",
        "details_help": "d 상세 · a 전체 · r 원문 · q 종료",
        "more": "{count}개 더 있음",
        "before_more": "위에 {count}개 있음",
        "after_more": "아래에 {count}개 있음",
        "no_checkpoints": "체크포인트가 없습니다.",
        "progress_unknown": "진척 불명",
        "waiting": "상태 파일 대기 중",
        "search_dirs": "검색 경로",
        "target": "대상",
        "git_unavailable": "git: 없음",
        "git_changed": "변경",
        "stop": "^C 종료",
        "evidence": "증거",
    },
    "en": {
        "app": "Custom Workflow",
        "refresh": "refresh",
        "path": "path",
        "now": "NOW",
        "checkpoint": "checkpoint",
        "action": "action",
        "next": "next",
        "blocker": "blocker",
        "none": "none",
        "checkpoints": "CHECKPOINTS",
        "verification": "VERIFICATION",
        "subagents": "SUPERPOWERS / SUBAGENTS",
        "recent": "RECENT",
        "details_help": "d details · a all · r raw · q quit",
        "more": "{count} more",
        "before_more": "{count} above",
        "after_more": "{count} below",
        "no_checkpoints": "No checkpoints found.",
        "progress_unknown": "progress unknown",
        "waiting": "waiting for status file",
        "search_dirs": "search dirs",
        "target": "target",
        "git_unavailable": "git: unavailable",
        "git_changed": "changed",
        "stop": "^C to stop",
        "evidence": "ev",
    },
}

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


@dataclass
class StatusBoard:
    path: Path
    title: str
    state: str
    objective: str
    progress: str
    bar: str
    current_checkpoint: str
    current_action: str
    next_checkpoint: str
    current_blocker: str
    checkpoints: list[dict[str, str]]
    verification: list[dict[str, str]]
    superpowers: list[dict[str, str]]
    recent_events: list[str]
    final_state: list[str]
    raw_text: str


def text(key: str, lang: str) -> str:
    return TEXT.get(lang, TEXT["ko"]).get(key, key)


def normalize_status(status: str) -> str:
    return status.strip().upper() or "UNKNOWN"


def color(enabled: bool, code: str, value: str) -> str:
    return f"\033[{code}m{value}\033[0m" if enabled else value


def strip_ansi(value: str) -> str:
    return ANSI_RE.sub("", value)


def clear_screen(enabled: bool) -> None:
    if enabled:
        sys.stdout.write("\033[2J\033[H")


def char_width(char: str) -> int:
    if unicodedata.combining(char):
        return 0
    return 2 if unicodedata.east_asian_width(char) in {"F", "W"} else 1


def display_width(value: str) -> int:
    return sum(char_width(char) for char in strip_ansi(value))


def fit(value: str, width: int) -> str:
    if width <= 0:
        return ""
    if display_width(value) <= width:
        return value + " " * (width - display_width(value))
    if width <= 1:
        return "…"
    out = ""
    used = 0
    for char in value:
        size = char_width(char)
        if used + size > width - 1:
            break
        out += char
        used += size
    return out + "…"


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def repo_root(start: Path) -> Path:
    for path in [start, *start.parents]:
        if (path / ".git").exists():
            return path
    return start


def handoff_dirs(root: Path, explicit: list[str]) -> list[Path]:
    if explicit:
        return [Path(item).expanduser().resolve() for item in explicit]
    return [root / "agent-handoffs", root / "docs" / "agent-handoffs"]


def status_files(root: Path, explicit_dirs: list[str], slug: str | None) -> list[Path]:
    files: list[Path] = []
    pattern = f"{slug}-status.md" if slug else "*-status.md"
    for directory in handoff_dirs(root, explicit_dirs):
        if directory.is_dir():
            files.extend(path for path in directory.glob(pattern) if path.is_file())
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)


def git_summary(root: Path, lang: str) -> str:
    if not (root / ".git").exists() or not shutil.which("git"):
        return text("git_unavailable", lang)
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=2,
            check=False,
        ).stdout.splitlines()
    except (OSError, subprocess.SubprocessError):
        return text("git_unavailable", lang)
    label = branch or "detached"
    if lang == "ko":
        return f"git: {text('git_changed', lang)} {len(status)} · {label}"
    return f"git: {len(status)} {text('git_changed', lang)} · {label}"


def extract_value(markdown: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(.+)$", markdown, re.MULTILINE)
    return match.group(1).strip() if match else ""


def section_text(markdown: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)"
    match = re.search(pattern, markdown, re.MULTILINE)
    return match.group(1).strip("\n") if match else ""


def parse_markdown_table(markdown: str, heading: str) -> list[dict[str, str]]:
    body = section_text(markdown, heading)
    rows = []
    for line in body.splitlines():
        if line.strip().startswith("|") and line.strip().endswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
                continue
            rows.append(cells)
    if len(rows) < 2:
        return []
    headers = rows[0]
    parsed = []
    for row in rows[1:]:
        if len(row) < len(headers):
            row += [""] * (len(headers) - len(row))
        parsed.append({headers[index]: row[index] for index in range(len(headers))})
    return parsed


def parse_bullets(markdown: str, heading: str) -> list[str]:
    body = section_text(markdown, heading)
    return [line.strip()[2:] for line in body.splitlines() if line.strip().startswith("- ")]


def parse_final_state(markdown: str) -> list[str]:
    body = section_text(markdown, "Final State")
    return [line.strip() for line in body.splitlines() if line.strip()]


def parse_board(path: Path) -> StatusBoard:
    markdown = path.read_text(encoding="utf-8", errors="replace")
    title_match = re.search(r"^# Goal Status:\s*(.+)$", markdown, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem
    return StatusBoard(
        path=path,
        title=title,
        state=extract_value(markdown, "State") or "UNKNOWN",
        objective=extract_value(markdown, "Objective") or "",
        progress=extract_value(markdown, "Progress") or "",
        bar=extract_value(markdown, "Bar") or "",
        current_checkpoint=extract_value(markdown, "Current checkpoint") or "",
        current_action=extract_value(markdown, "Current action") or "",
        next_checkpoint=extract_value(markdown, "Next checkpoint") or "",
        current_blocker=extract_value(markdown, "Current blocker") or "none",
        checkpoints=parse_markdown_table(markdown, "Checkpoints"),
        verification=parse_markdown_table(markdown, "Verification"),
        superpowers=parse_markdown_table(markdown, "Superpowers / Subagents"),
        recent_events=parse_bullets(markdown, "Recent Events"),
        final_state=parse_final_state(markdown),
        raw_text=markdown,
    )


def status_label(status: str, lang: str) -> str:
    normalized = normalize_status(status)
    return STATUS_LABELS.get(lang, STATUS_LABELS["ko"]).get(normalized, normalized)


def status_icon(status: str, ascii_mode: bool, color_enabled: bool) -> str:
    normalized = normalize_status(status)
    icon = STATUS_ICONS.get(normalized, ("?", "?"))[1 if ascii_mode else 0]
    return color(color_enabled, STATUS_COLORS.get(normalized, "37"), icon)


def status_text(status: str, color_enabled: bool, lang: str) -> str:
    normalized = normalize_status(status)
    return color(color_enabled, STATUS_COLORS.get(normalized, "37"), status_label(normalized, lang))


def render_progress_bar(progress: str, width: int, color_enabled: bool) -> str:
    match = re.search(r"(\d+)\s*/\s*(\d+)", progress)
    if not match:
        return "[" + "." * width + "]"
    done = max(0, int(match.group(1)))
    total = max(int(match.group(2)), 1)
    filled = max(0, min(width, round(width * min(done, total) / total)))
    if color_enabled:
        return "[" + color(True, "42;32", " " * filled) + color(True, "90", "." * (width - filled)) + "]"
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def current_checkpoint_id(board: StatusBoard) -> str:
    match = re.search(r"\b([A-Z]{1,4}\d{1,3}(?:-\d{1,3})?)\b", board.current_checkpoint)
    return match.group(1) if match else ""


def checkpoint_anchor(rows: list[dict[str, str]], current_id: str) -> int:
    if current_id:
        for index, row in enumerate(rows):
            if row.get("ID", "") == current_id:
                return index
    for index, row in enumerate(rows):
        if normalize_status(row.get("Status", "")) not in {"DONE", "PASS"}:
            return index
    return 0


def checkpoint_window(
    rows: list[dict[str, str]], limit: int, current_id: str, show_all: bool
) -> tuple[list[dict[str, str]], int, int]:
    if show_all or len(rows) <= limit:
        return rows, 0, 0
    anchor = checkpoint_anchor(rows, current_id)
    before = max(1, min(3, limit // 3))
    start = max(0, min(anchor - before, len(rows) - limit))
    end = start + limit
    return rows[start:end], start, len(rows) - end


def checkpoint_summary(board: StatusBoard, color_enabled: bool, lang: str) -> str:
    counts: dict[str, int] = {}
    for row in board.checkpoints:
        status = normalize_status(row.get("Status", ""))
        counts[status] = counts.get(status, 0) + 1
    parts = []
    for key in ("DONE", "RUNNING", "VERIFYING", "BLOCKED", "PARTIAL", "TODO"):
        if counts.get(key):
            parts.append(f"{status_text(key, color_enabled, lang)} {counts[key]}")
    return " · ".join(parts) if parts else text("no_checkpoints", lang)


def hidden_line(kind: str, count: int, color_enabled: bool, lang: str) -> str:
    return color(color_enabled, "90", "… " + text(kind, lang).format(count=count))


def render_wide_checkpoint_rows(
    board: StatusBoard,
    width: int,
    height_budget: int,
    ascii_mode: bool,
    color_enabled: bool,
    lang: str,
    show_all: bool,
) -> list[str]:
    rows = board.checkpoints
    if not rows:
        return ["  " + color(color_enabled, "90", text("no_checkpoints", lang))]
    current_id = current_checkpoint_id(board)
    limit = len(rows) if show_all else max(1, height_budget)
    visible, before, after = checkpoint_window(rows, limit, current_id, show_all)
    rendered = []
    if before:
        rendered.append(hidden_line("before_more", before, color_enabled, lang))
    for row in visible:
        cp_id = row.get("ID", "")
        status = row.get("Status", "")
        name = compact(row.get("Checkpoint", ""))
        owner = row.get("Owner", "")
        evidence = row.get("Evidence", "")
        current = bool(current_id and cp_id == current_id)
        right = " ".join(part for part in [status_text(status, color_enabled, lang), owner] if part).strip()
        marker = ">" if current else " "
        left_prefix = f"{marker}{status_icon(status, ascii_mode, color_enabled)} {cp_id:<5} "
        right_part = f" {right}" if right else ""
        evidence_part = f" · {text('evidence', lang)}" if evidence else ""
        name_width = max(12, width - display_width(left_prefix) - display_width(right_part) - display_width(evidence_part) - 2)
        checkpoint_name = fit(name, name_width)
        if current:
            checkpoint_name = color(color_enabled, "1;37", checkpoint_name)
        rendered.append(left_prefix + checkpoint_name + right_part + evidence_part)
    if after:
        rendered.append(hidden_line("after_more", after, color_enabled, lang))
    return rendered


def render_narrow_checkpoint_rows(
    board: StatusBoard,
    width: int,
    line_budget: int,
    ascii_mode: bool,
    color_enabled: bool,
    lang: str,
    show_all: bool,
) -> list[str]:
    rows = board.checkpoints
    if not rows:
        return ["  " + color(color_enabled, "90", text("no_checkpoints", lang))]
    current_id = current_checkpoint_id(board)
    row_limit = len(rows) if show_all else max(1, (line_budget - 2) // 2)
    visible, before, after = checkpoint_window(rows, row_limit, current_id, show_all)
    rendered = []
    if before:
        rendered.append(hidden_line("before_more", before, color_enabled, lang))
    for index, row in enumerate(visible):
        suffix_room = 1 if after and index == len(visible) - 1 else 0
        if not show_all and len(rendered) + 2 + suffix_room > line_budget:
            break
        cp_id = row.get("ID", "")
        status = row.get("Status", "")
        name = compact(row.get("Checkpoint", ""))
        evidence = row.get("Evidence", "")
        current = bool(current_id and cp_id == current_id)
        marker = ">" if current else " "
        first = f"{marker}{status_icon(status, ascii_mode, color_enabled)} {cp_id} {status_text(status, color_enabled, lang)}"
        if current:
            first = color(color_enabled, "1;37", first)
        rendered.append(fit(first, width))
        evidence_suffix = f" · {text('evidence', lang)}" if evidence else ""
        rendered.append("  " + fit(name + evidence_suffix, max(1, width - 2)))
    if after:
        rendered.append(hidden_line("after_more", after, color_enabled, lang))
    return rendered


def render_detail_table(
    title: str,
    rows: list[dict[str, str]],
    width: int,
    max_rows: int,
    color_enabled: bool,
    lang: str,
) -> list[str]:
    if not rows or max_rows <= 0:
        return []
    output = [color(color_enabled, "1;36", title)]
    for row in rows[:max_rows]:
        values = [compact(value) for value in row.values()]
        status = row.get("Status") or row.get("Verdict") or ""
        label = values[0] if values else ""
        prefix = f"  {status_icon(status, False, color_enabled)} {status_label(status, lang)} " if status else "  - "
        output.append(prefix + fit(label, width - display_width(prefix)))
    if len(rows) > max_rows:
        output.append(hidden_line("more", len(rows) - max_rows, color_enabled, lang))
    return output


def raw_render(board: StatusBoard, root: Path, args: argparse.Namespace, color_enabled: bool) -> str:
    width = min(shutil.get_terminal_size((80, 30)).columns, 120)
    lines = board.raw_text.splitlines()
    if args.lines > 0:
        lines = lines[: args.lines]
    path = display_path(board.path, root)
    return "\n".join(
        [
            f"{text('app', args.lang)} 원문 · {board.path.name} · {status_label(board.state, args.lang)} · {board.progress}",
            f"{text('refresh', args.lang)}: {time.strftime('%Y-%m-%d %H:%M:%S')} · {args.interval:g}s",
            f"{text('path', args.lang)}: {path}",
            "-" * width,
            *lines,
            "-" * width,
            git_summary(root, args.lang) + " · " + text("stop", args.lang),
        ]
    ) + "\n"


def render_wide_dashboard(
    board: StatusBoard,
    root: Path,
    args: argparse.Namespace,
    color_enabled: bool,
    width: int,
    height: int,
    show_all: bool,
    show_details: bool,
) -> str:
    path = display_path(board.path, root)
    state = status_text(board.state, color_enabled, args.lang)
    bar_width = max(10, min(28, width - 34))
    bar = render_progress_bar(board.progress, bar_width, color_enabled)
    sep = "─" * width if not args.ascii else "-" * width
    title = fit(board.title, max(20, width - 28))

    output = [
        color(color_enabled, "1;37", f"{text('app', args.lang)} · {title}") + f" {state}",
        f"{bar} {board.progress or text('progress_unknown', args.lang)} · {text('refresh', args.lang)} {args.interval:g}s",
        color(color_enabled, "90", f"{path} · {time.strftime('%H:%M:%S')}"),
        sep,
        color(color_enabled, "1;36", text("now", args.lang)),
        f"  {text('checkpoint', args.lang)}: " + fit(board.current_checkpoint or "-", width - 10),
        f"  {text('action', args.lang)}: " + fit(board.current_action or "-", width - 10),
        f"  {text('next', args.lang)}: " + fit(board.next_checkpoint or "-", width - 10),
        f"  {text('blocker', args.lang)}: "
        + (
            color(color_enabled, "31", board.current_blocker)
            if board.current_blocker and board.current_blocker.lower() not in {"none", "없음"}
            else text("none", args.lang)
        ),
        sep,
        color(color_enabled, "1;36", text("checkpoints", args.lang)) + "  " + color(color_enabled, "90", checkpoint_summary(board, color_enabled, args.lang)),
    ]

    reserved = 16 + (9 if show_details else 0)
    checkpoint_budget = max(4, height - reserved)
    output.extend(render_wide_checkpoint_rows(board, width, checkpoint_budget, args.ascii, color_enabled, args.lang, show_all))

    if show_details:
        output.append(sep)
        output.extend(render_detail_table(text("verification", args.lang), board.verification, width, 4, color_enabled, args.lang))
        output.extend(render_detail_table(text("subagents", args.lang), board.superpowers, width, 4, color_enabled, args.lang))
        if board.recent_events:
            output.append(color(color_enabled, "1;36", text("recent", args.lang)))
            for event in board.recent_events[-3:]:
                output.append("  - " + fit(compact(event), width - 4))
    else:
        output.append(color(color_enabled, "90", text("details_help", args.lang)))

    output.append(sep)
    output.append(git_summary(root, args.lang) + " · " + text("stop", args.lang))
    return "\n".join(output) + "\n"


def render_narrow_dashboard(
    board: StatusBoard,
    root: Path,
    args: argparse.Namespace,
    color_enabled: bool,
    width: int,
    height: int,
    show_all: bool,
    show_details: bool,
) -> str:
    path = display_path(board.path, root)
    sep = "─" * width if not args.ascii else "-" * width
    bar_width = max(10, width - 2)
    blocker = board.current_blocker if board.current_blocker and board.current_blocker.lower() not in {"none", "없음"} else text("none", args.lang)

    output = [
        color(color_enabled, "1;37", text("app", args.lang)),
        fit(board.title, width),
        f"{status_text(board.state, color_enabled, args.lang)} · {board.progress or text('progress_unknown', args.lang)}",
        render_progress_bar(board.progress, bar_width, color_enabled),
        color(color_enabled, "90", fit(f"{time.strftime('%H:%M:%S')} · {path}", width)),
        sep,
        color(color_enabled, "1;36", text("now", args.lang)),
        fit(f"{text('checkpoint', args.lang)} {board.current_checkpoint or '-'}", width),
        fit(f"{text('action', args.lang)} {board.current_action or '-'}", width),
        fit(f"{text('next', args.lang)} {board.next_checkpoint or '-'}", width),
        fit(f"{text('blocker', args.lang)} {blocker}", width),
        sep,
        color(color_enabled, "1;36", text("checkpoints", args.lang)),
        fit(checkpoint_summary(board, False, args.lang), width),
    ]

    reserved = len(output) + 3 + (8 if show_details else 1)
    line_budget = max(4, height - reserved)
    output.extend(render_narrow_checkpoint_rows(board, width, line_budget, args.ascii, color_enabled, args.lang, show_all))

    if show_details:
        output.append(sep)
        output.extend(render_detail_table(text("verification", args.lang), board.verification, width, 3, color_enabled, args.lang))
        output.extend(render_detail_table(text("subagents", args.lang), board.superpowers, width, 3, color_enabled, args.lang))
        if board.recent_events:
            output.append(color(color_enabled, "1;36", text("recent", args.lang)))
            for event in board.recent_events[-2:]:
                output.append("  - " + fit(compact(event), width - 4))
    else:
        output.append(color(color_enabled, "90", fit(text("details_help", args.lang), width)))

    output.append(sep)
    output.append(fit(git_summary(root, args.lang) + " · " + text("stop", args.lang), width))
    return "\n".join(output) + "\n"


def dashboard_render(
    board: StatusBoard,
    root: Path,
    args: argparse.Namespace,
    color_enabled: bool,
    show_all: bool,
    show_details: bool,
) -> str:
    size = shutil.get_terminal_size((54, 36))
    width = min(max(size.columns, 32), 140)
    height = max(size.lines, 14)
    layout = args.layout
    narrow = layout == "narrow" or (layout == "auto" and width < 72)
    if narrow:
        return render_narrow_dashboard(board, root, args, color_enabled, width, height, show_all, show_details)
    return render_wide_dashboard(board, root, args, color_enabled, width, height, show_all, show_details)


def waiting(root: Path, explicit_dirs: list[str], slug: str | None, args: argparse.Namespace, color_enabled: bool) -> str:
    target = f"{slug}-status.md" if slug else "*-status.md"
    dirs = ", ".join(str(path) for path in handoff_dirs(root, explicit_dirs))
    title = color(color_enabled, "1;37", text("app", args.lang))
    return (
        f"{title}\n"
        f"{text('waiting', args.lang)}\n"
        f"{text('target', args.lang)}: {target}\n"
        f"{text('search_dirs', args.lang)}: {dirs}\n"
        f"{text('refresh', args.lang)}: {time.strftime('%H:%M:%S')} · {args.interval:g}s\n"
        f"{git_summary(root, args.lang)} · {text('stop', args.lang)}\n"
    )


class KeyReader:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self.old_settings = None

    def __enter__(self):
        if self.enabled:
            self.old_settings = termios.tcgetattr(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.enabled and self.old_settings is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.old_settings)

    def read(self, timeout: float) -> str | None:
        if not self.enabled:
            time.sleep(timeout)
            return None
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.read(1)
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Watch the latest custom-workflow-skillset goal status board.")
    parser.add_argument("--slug", help="Watch agent-handoffs/<slug>-status.md")
    parser.add_argument("--handoffs-dir", action="append", default=[], help="Directory to search. Can be repeated.")
    parser.add_argument("--interval", type=float, default=2.0, help="Refresh interval in seconds")
    parser.add_argument("--lines", type=int, default=180, help="Maximum raw status file lines to render; 0 means all")
    parser.add_argument("--once", action="store_true", help="Render once and exit")
    parser.add_argument("--plain", action="store_true", help="Disable color")
    parser.add_argument("--no-clear", action="store_true", help="Do not clear the terminal between refreshes")
    parser.add_argument("--raw", action="store_true", help="Show the raw Markdown status file")
    parser.add_argument("--details", action="store_true", help="Show verification, subagent, and recent-event sections")
    parser.add_argument("--all", action="store_true", help="Show all checkpoints instead of fitting to pane height")
    parser.add_argument("--ascii", action="store_true", help="Use ASCII status markers")
    parser.add_argument("--layout", choices=["auto", "narrow", "wide"], default="auto", help="Dashboard layout. auto uses narrow below 72 columns.")
    parser.add_argument("--lang", choices=["ko", "en"], default="ko", help="Display language")
    args = parser.parse_args()

    start = Path.cwd().resolve()
    root = repo_root(start)
    color_enabled = not args.plain and sys.stdout.isatty() and not os.environ.get("NO_COLOR")
    interactive = sys.stdin.isatty() and not args.once
    raw_mode = args.raw
    show_details = args.details
    show_all = args.all

    with KeyReader(interactive) as keys:
        while True:
            files = status_files(root, args.handoffs_dir, args.slug)
            clear_screen(not args.no_clear and not args.once)
            if files:
                board = parse_board(files[0])
                if raw_mode:
                    sys.stdout.write(raw_render(board, root, args, color_enabled))
                else:
                    sys.stdout.write(dashboard_render(board, root, args, color_enabled, show_all, show_details))
            else:
                sys.stdout.write(waiting(root, args.handoffs_dir, args.slug, args, color_enabled))
            sys.stdout.flush()
            if args.once:
                return 0

            key = keys.read(max(args.interval, 0.2))
            if key in {"q", "Q", "\x03"}:
                return 0
            if key in {"r", "R"}:
                raw_mode = not raw_mode
            elif key in {"d", "D"}:
                show_details = not show_details
            elif key in {"a", "A"}:
                show_all = not show_all


if __name__ == "__main__":
    raise SystemExit(main())
