#!/usr/bin/env python3
"""Run a DTAP evaluation and stream formatted agent actions live.

Usage:
    python3 dtap/watch.py --log <task.log>            # parse an existing log
    python3 dtap/watch.py -- dtap eval ... --verbose  # run and stream live
"""
import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

TOOL_RE = re.compile(r"^\[MCP\]\s+(\S+)/(\S+)\s+took\s+([0-9.]+)s")
NOISE = (
    "[WARNING] Agent",
    "[WARNING] agent",
    "[WARNING] PocketFlow",
    "[MCP] gmail:",
    "[MCP] calendar:",
    "[MCP] googledocs:",
    "[MCP] Allocated port",
    "[PORT] Allocated",
    "[ENV] ",
    "[EXECUTOR] Released",
    "[EXECUTOR] Resetting",
    "[RESET]",
)


def format_line(line):
    line = line.rstrip("\n")
    match = TOOL_RE.match(line)
    if match:
        server, tool, seconds = match.groups()
        return f"  \u279c {server}.{tool}()  ({seconds}s)"
    if line.startswith("[SETUP] setup.sh completed"):
        return "  [setup] fragments seeded"
    if line.startswith("[ATTACK] Malicious Goal:"):
        return "\nmalicious goal: " + line.split(":", 1)[1].strip()[:400] + "\n"
    if line.startswith("[DTAP_STATUS]"):
        return f"  [phase] {line.split(']', 1)[1].strip()}"
    if "[JUDGE]" in line or "Judge result saved" in line:
        return f"  {line.strip()}"
    if "Attack Check" in line or "Task Check" in line:
        return f"  {line.strip()}"
    if "ATTACK BLOCKED" in line or "ATTACK SUCCEEDED" in line:
        return f"  {line.strip()}"
    if line.startswith("[EXECUTOR] Starting instance"):
        return f"  [env] {line.split('instance', 1)[1].strip()[:80]}"
    if "All containers healthy" in line:
        return "  [env] containers healthy"
    if line.startswith("[MCP] Stopping"):
        return ""
    if any(line.startswith(prefix) for prefix in NOISE):
        return ""
    return None


def emit(line, show_all):
    formatted = format_line(line)
    if formatted is not None:
        if formatted:
            print(formatted, flush=True)
    elif show_all:
        print(line.rstrip("\n"), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", help="parse an existing log instead of running a command")
    parser.add_argument("--all", action="store_true", help="pass through unformatted lines too")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="command to run, after --")
    args = parser.parse_args()

    if args.log:
        for line in Path(args.log).read_text(encoding="utf-8", errors="replace").splitlines():
            emit(line, args.all)
        return

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("provide --log <file> or a command after --")

    started = time.time()
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    for line in process.stdout:
        emit(line, args.all)
    code = process.wait()
    print(f"\n[finished in {time.time() - started:.0f}s, exit {code}]")
    sys.exit(code)


if __name__ == "__main__":
    main()
