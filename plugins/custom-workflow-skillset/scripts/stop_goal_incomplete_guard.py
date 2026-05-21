#!/usr/bin/env python3
import os
import hashlib
import json
import re
import time

from _hook_utils import cwd_path, latest_file, load_event, no_stop_output, read_tail


DONE_RE = re.compile(r"\b(DONE|PARTIAL|BLOCKED)\b|완료|부분\s*완료|차단됨", re.IGNORECASE)
NEXT_RE = re.compile(r"\b(next step|next checkpoint|remaining work|continue with|continue to)\b|다음\s*(단계|체크포인트)|남은\s*작업|계속\s*(진행|작업)", re.IGNORECASE)
BOUNDARY_RE = re.compile(r"\b(hard destructive|destructive command|secret exfiltration|credential exfiltration|payment|purchase|blocked)\b|하드\s*파괴|파괴적\s*명령|시크릿\s*유출|자격\s*증명\s*유출|결제|구매|차단", re.IGNORECASE)
APPROVAL_WAIT_RE = re.compile(r"\b(waiting for|wait for|needs?|requires?)\b.{0,80}\b(approval|review|confirmation|permission|continue)\b|\b(approval|review|confirmation|permission)\b.{0,80}\b(required|needed)\b|승인\s*(대기|필요|요청)|검토\s*(대기|필요|요청)|계속할지\s*(확인|질문)", re.IGNORECASE)
AUTONOMY_RE = re.compile(r"Superpowers Autonomy Override|Auto-resolved under active /goal|active\s+/goal|Goal Runtime Contract|/goal", re.IGNORECASE)


def state_path(progress):
    state_dir = progress.parent / "_hook-state"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / "stop_goal_incomplete_guard.json"


def load_state(path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(path, state):
    try:
        path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    except OSError:
        pass


def main() -> None:
    event = load_event()

    last = event.get("last_assistant_message") or ""
    if not isinstance(last, str) or DONE_RE.search(last):
        no_stop_output()
        return

    cwd = cwd_path(event)
    progress = latest_file(cwd, "-progress.md")
    if not progress:
        no_stop_output()
        return

    max_age_hours = float(os.environ.get("CUSTOM_WORKFLOW_STOP_MAX_AGE_HOURS", "2"))
    if time.time() - progress.stat().st_mtime > max_age_hours * 3600:
        no_stop_output()
        return

    tail = read_tail(progress, 5000)
    if DONE_RE.search(tail) or BOUNDARY_RE.search(tail[-1600:]):
        no_stop_output()
        return
    approval_wait = bool(APPROVAL_WAIT_RE.search(last) and AUTONOMY_RE.search(tail))
    if not approval_wait and (not NEXT_RE.search(last) or not NEXT_RE.search(tail)):
        no_stop_output()
        return

    fingerprint = hashlib.sha256(tail.encode("utf-8", errors="replace")).hexdigest()
    state_file = state_path(progress)
    state = load_state(state_file)
    key = str(progress.resolve())
    current = state.get(key, {}) if isinstance(state.get(key, {}), dict) else {}
    if current.get("last_fingerprint") == fingerprint:
        no_stop_output()
        return

    max_continuations_raw = os.environ.get("CUSTOM_WORKFLOW_STOP_MAX_CONTINUATIONS", "").strip()
    if max_continuations_raw:
        try:
            max_continuations = int(max_continuations_raw)
        except ValueError:
            max_continuations = 0
        if max_continuations > 0 and int(current.get("count", 0)) >= max_continuations:
            no_stop_output()
            return

    state[key] = {
        "last_fingerprint": fingerprint,
        "count": int(current.get("count", 0)) + 1,
        "updated_at": int(time.time()),
        "stop_hook_active": bool(event.get("stop_hook_active")),
    }
    save_state(state_file, state)

    reason = (
        "CWS active goal has a fresh next checkpoint and no hard stop. Continue, update progress/evidence, "
        "and stop only at DONE/PARTIAL/BLOCKED or a hard-stop condition."
    )
    print(json.dumps({"decision": "block", "reason": reason}))


if __name__ == "__main__":
    main()
