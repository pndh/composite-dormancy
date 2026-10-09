#!/usr/bin/env python3
"""Replay a DTAP per-task trajectory as a readable agent-action stream."""
import argparse
import json
import sys
import time
from pathlib import Path


def compact(value, width):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    text = " ".join(str(text).split())
    if width and len(text) > width:
        return text[: width - 1] + "\u2026"
    return text


def resolve(path):
    p = Path(path)
    if p.is_dir():
        candidates = sorted(list(p.glob("2026*.json")) + list(p.glob("trajectory*.json")))
        if not candidates:
            sys.exit(f"no trajectory json found in {p}")
        return candidates[-1]
    return p


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="trajectory json file or a task result directory")
    parser.add_argument("--delay", type=float, default=0.0, help="seconds between steps (for live demos)")
    parser.add_argument("--result-width", type=int, default=200)
    args = parser.parse_args()

    path = resolve(args.path)
    data = json.loads(path.read_text(encoding="utf-8"))
    info = data.get("task_info", {})
    traj_info = data.get("traj_info", {})

    print(f"task        : {info.get('task_id')}")
    print(f"domain      : {info.get('domain')}  |  risk: {info.get('risk_category')}  |  threat: {info.get('threat_model')}")
    print(f"instruction : {compact(info.get('original_instruction') or '', 300)}")
    if info.get("malicious_instruction"):
        print(f"goal        : {compact(info.get('malicious_instruction'), 300)}")
    print("-" * 78)

    for step in data.get("trajectory", []):
        role = step.get("role")
        metadata = step.get("metadata") or {}
        if role == "user":
            print(f"USER  \u25b6 {compact(step.get('state'), 300)}")
        elif role == "agent":
            action = step.get("action") or ""
            if action in ("final_response", "send_message_to_user"):
                message = metadata.get("message") or step.get("state") or ""
                print(f"\nAGENT \u270e {compact(message, 1200)}\n")
            else:
                reasoning = step.get("reasoning") or metadata.get("reasoning")
                if reasoning:
                    print(f"AGENT \u2026 {compact(reasoning, 300)}")
                print(f"AGENT \u279c {compact(action, 260)}")
        elif role == "tool":
            print(f"  TOOL \u2190 {compact(step.get('state'), args.result_width)}")
        if args.delay:
            time.sleep(args.delay)

    if traj_info.get("duration"):
        print(f"\n[duration {traj_info['duration']}s over {traj_info.get('step_count', 0)} steps]")


if __name__ == "__main__":
    main()
