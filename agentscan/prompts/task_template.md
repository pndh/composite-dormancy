# SESSION TASK

program: {{program}}
target: {{target}}
phase: {{phase}}          # recon | hypothesis | test-design | execute | verify | report
objective: {{objective}}
budget: {{budget}}        # e.g. "30 tool calls / 1 hour / 5 hypotheses"
accounts: {{accounts}}
allowed_actions: {{allowed_actions}}
deliverable: {{deliverable}}
mode: {{mode}}            # assisted (human in the loop) | automated (sandbox/lab only)

## Required output
1. `session_report.md` — what was tested, what was learned, dead ends, next actions.
2. `findings.json` — array of finding records per §8 of the system prompt (may be empty).
3. `journal_update.json` — updated hypothesis table: id, hypothesis, status, result, next step.

## Reminders
- Restate scope before acting. When in doubt, stop and ask.
- Every claimed effect needs an oracle artifact (file, request, state diff, screenshot).
- Behavior-only observations go to RESEARCH NOTES, never findings.
