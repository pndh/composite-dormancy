#!/usr/bin/env python3
"""agentscan runner — session builder + finding validator + advisory renderer.

No third-party dependencies. Commands:
  list                              list configured programs
  session  --program P --target T   build a ready-to-run agent session (JSON)
           [--phase recon] [--objective "..."] [--budget "..."] [--mode assisted]
           [--accounts "..."] [--allowed "..."] [--deliverable "..."]
           [--out session.json]
  validate --findings findings.json  structural + evidence checks; exit 1 on failure
  advisory --finding finding.json    render a markdown advisory draft
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"
CONFIG = ROOT / "config" / "programs.json"

REQUIRED_FINDING_KEYS = [
    "id", "title", "program", "target", "version", "date", "class_cwe", "atlas",
    "severity", "impact", "preconditions", "attack_chain", "evidence", "repro",
    "disclosure_status", "confidence",
]
BEHAVIOR_MARKERS = ("model said", "model refused", "model complied", "no security impact",
                    "behavior only", "behaviour only")


def load_programs() -> dict:
    return json.loads(CONFIG.read_text())


def render_task(template: str, values: dict) -> str:
    def sub(match):
        key = match.group(1).strip()
        return str(values.get(key, match.group(0)))
    return re.sub(r"\{\{([^}]+)\}\}", sub, template)


def cmd_list(_args) -> int:
    for pid, p in load_programs().items():
        print(f"{pid:24s} {p['type']:7s} {p['mode']:10s} {p['name']}")
    return 0


def cmd_session(args) -> int:
    programs = load_programs()
    if args.program not in programs:
        print(f"unknown program: {args.program}", file=sys.stderr)
        return 2
    program = programs[args.program]
    system = (PROMPTS / "hunter_system.md").read_text()
    playbook_path = PROMPTS / "programs" / f"{args.program.split('--')[0]}.md"
    if not playbook_path.exists():
        playbook_path = PROMPTS / "programs" / f"{args.program}.md"
    playbook = playbook_path.read_text() if playbook_path.exists() else "(no program playbook)"
    task = render_task((PROMPTS / "task_template.md").read_text(), {
        "program": args.program,
        "target": args.target,
        "phase": args.phase,
        "objective": args.objective or "Recon the target surface and produce a ranked hypothesis list.",
        "budget": args.budget or "30 tool calls / 2 hours",
        "accounts": args.accounts or program.get("accounts", ""),
        "allowed_actions": args.allowed or "Read-only recon; program-scoped tests only.",
        "deliverable": args.deliverable or "Capability map + ranked hypotheses with test designs.",
        "mode": args.mode or program.get("mode", "assisted"),
    })
    context = {
        "program_id": args.program,
        "program": program,
        "scope_check": "Restate scope before acting; anything not in scope is forbidden.",
    }
    session = {
        "system_prompt": system,
        "program_context": context,
        "program_playbook": playbook,
        "task_prompt": task,
        "mode": args.mode or program.get("mode", "assisted"),
        "harness": {"version": "0.1", "root": str(ROOT)},
    }
    out = Path(args.out or "session.json")
    out.write_text(json.dumps(session, indent=2) + "\n")
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    print(f"program={args.program} phase={args.phase} mode={session['mode']}")
    return 0


def _validate_one(f: dict, idx: int, errors: list, warnings: list) -> None:
    missing = [k for k in REQUIRED_FINDING_KEYS if k not in f]
    if missing:
        errors.append(f"[{idx}] {f.get('id', '?')}: missing keys {missing}")
    if not f.get("evidence"):
        errors.append(f"[{idx}] {f.get('id', '?')}: evidence is empty (no effect oracle)")
    if not f.get("attack_chain"):
        warnings.append(f"[{idx}] {f.get('id', '?')}: attack_chain is empty")
    blob = json.dumps(f).lower()
    for marker in BEHAVIOR_MARKERS:
        if marker in blob and not f.get("effect_oracle"):
            warnings.append(
                f"[{idx}] {f.get('id', '?')}: contains behavior-only language ('{marker}') "
                "without an effect_oracle field — consider RESEARCH NOTES instead of a finding"
            )
    if f.get("severity") not in ("critical", "important", "moderate", "low", "none", None):
        warnings.append(f"[{idx}] {f.get('id', '?')}: unusual severity '{f.get('severity')}'")


def cmd_validate(args) -> int:
    data = json.loads(Path(args.findings).read_text())
    findings = data if isinstance(data, list) else [data]
    errors, warnings = [], []
    for i, f in enumerate(findings):
        _validate_one(f, i, errors, warnings)
    for w in warnings:
        print("WARN:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"validated {len(findings)} finding(s): {len(errors)} error(s), {len(warnings)} warning(s)")
    return 0 if not errors else 1


def cmd_advisory(args) -> int:
    f = json.loads(Path(args.finding).read_text())
    lines = [
        f"# {f.get('title', 'Untitled finding')}",
        "",
        f"- Program: {f.get('program', '')}",
        f"- Target: {f.get('target', '')} ({f.get('version', 'unknown version')})",
        f"- Date: {f.get('date', '')}",
        f"- Class: {f.get('class_cwe', '')} | ATLAS: {f.get('atlas', '')}",
        f"- Severity: {f.get('severity', '')}",
        "",
        "## Impact",
        str(f.get("impact", "")),
        "",
        "## Preconditions",
        str(f.get("preconditions", "")),
        "",
        "## Attack chain",
    ]
    chain = f.get("attack_chain") or []
    lines += [f"{i+1}. {step}" for i, step in enumerate(chain)]
    lines += ["", "## Reproduction"]
    repro = f.get("repro") or []
    lines += [f"{i+1}. {step}" for i, step in enumerate(repro)]
    lines += ["", "## Evidence"]
    for ev in f.get("evidence") or []:
        if isinstance(ev, dict):
            lines.append(f"- {ev.get('type', 'artifact')}: {ev.get('path', '')} {ev.get('note', '')}".rstrip())
        else:
            lines.append(f"- {ev}")
    lines += [
        "",
        "## Remediation",
        str(f.get("fix_suggestion", "")),
        "",
        f"_Disclosure status: {f.get('disclosure_status', '')} · Confidence: {f.get('confidence', '')}_",
    ]
    out = Path(args.out or "advisory.md")
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="agentscan")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")

    s = sub.add_parser("session")
    s.add_argument("--program", required=True)
    s.add_argument("--target", required=True)
    s.add_argument("--phase", default="recon")
    s.add_argument("--objective")
    s.add_argument("--budget")
    s.add_argument("--mode", choices=["assisted", "automated"])
    s.add_argument("--accounts")
    s.add_argument("--allowed")
    s.add_argument("--deliverable")
    s.add_argument("--out")

    v = sub.add_parser("validate")
    v.add_argument("--findings", required=True)

    a = sub.add_parser("advisory")
    a.add_argument("--finding", required=True)
    a.add_argument("--out")

    args = ap.parse_args()
    return {"list": cmd_list, "session": cmd_session,
            "validate": cmd_validate, "advisory": cmd_advisory}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
