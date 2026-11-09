#!/usr/bin/env python3
"""Minimal pre-tool-use guard for AI coding-agent sessions (generic example).

Reads the tool-call event as JSON on stdin and prints a permission decision.
Deny = hard block. Every decision is logged. Unreadable input fails open so a
broken guard never freezes every session.
"""
import datetime
import json
import os
import re
import sys

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guard_log.jsonl")

BASH_DENY = [
    (r"(^|[\s;&|(`])(rm|rmdir|unlink|shred)\s", "Do not delete: move the file to the holding folder instead."),
    (r"--(go|rollback-go)\b", "Production deploy/rollback is run by the human: write a one-line command."),
    (r"(^|[\s;&|(`])(ssh|scp|sftp)\s", "Server access is human-only: write a read-only command for the human."),
    (r"\bgit\s+push\b", "git push needs the human."),
]
RAW_DATA = re.compile(r"/raw_data/|contacts?_.*\.xlsx", re.I)


def decide(decision, reason, event):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": datetime.datetime.now().isoformat(timespec="seconds"),
                                "tool": event.get("tool_name"), "decision": decision,
                                "reason": reason}) + "\n")
    except OSError:
        pass
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": decision,
                                             "permissionDecisionReason": reason}}))
    sys.exit(0)


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail open
    tool, args = event.get("tool_name", ""), event.get("tool_input", {}) or {}
    if tool == "Bash":
        cmd = args.get("command", "")
        for pattern, reason in BASH_DENY:
            if re.search(pattern, cmd):
                decide("deny", reason, event)
        if RAW_DATA.search(cmd):
            decide("deny", "Raw sales/contact data is processed by local scripts only.", event)
    if tool in ("Read", "Edit", "Write") and RAW_DATA.search(args.get("file_path", "")):
        decide("deny", "Raw sales/contact data is processed by local scripts only.", event)
    decide("allow", "no rule matched", event)


if __name__ == "__main__":
    main()
