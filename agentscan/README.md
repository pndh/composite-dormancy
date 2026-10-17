# agentscan — AI bug-hunting agent harness

A **semantic** vulnerability harness for AI systems (agents, MCP servers, copilots). Not a
network scanner: it maps capability graphs, forms security hypotheses, runs minimal tests in
sandbox/test accounts, and proves impact with **effect oracles**.

## What's here
```
prompts/hunter_system.md        the agent system prompt (identity, scope rules, method,
                                taxonomy, techniques, evidence standard, stop conditions)
prompts/task_template.md        per-session task prompt (runner fills the slots)
prompts/programs/<program>.md   program playbooks (scope, rules, evidence requirements)
config/programs.json            machine-readable program configs
hunter/runner.py                session builder + finding validator + advisory renderer
```

## Quickstart
```bash
# list programs
python3 agentscan/hunter/runner.py list

# build a session for the Microsoft Copilot bounty (assisted mode)
python3 agentscan/hunter/runner.py session \
  --program microsoft-copilot --target copilot.microsoft.com \
  --phase recon --out /tmp/opencode/copilot_session.json

# validate findings (must carry evidence/effect oracles)
python3 agentscan/hunter/runner.py validate --findings findings.json

# render an advisory draft from a finding
python3 agentscan/hunter/runner.py advisory --finding finding.json --out advisory.md
```

Feed `session.json` to your agent runtime: `system_prompt` + `program_context` +
`program_playbook` + `task_prompt`. The harness does not assume a specific model or vendor.

## Design rules (enforced in the prompt)
- **Real targets only** for findings. Benchmarks/labs measure the harness, they don't produce
  vulnerability claims.
- **Effect oracle or it didn't happen** — model text is not impact.
- **Victim impact** for bounty programs: attacker content → victim context → effect.
- **Scope discipline** — ambiguity means stop, not "probably fine".
- **Behavior-only observations** go to RESEARCH NOTES, never findings.
- **Stochastic results** are reported as rates, not single lucky runs.

## Program modes
- `assisted` — human executes in the product UI (consumer surfaces, mobile, WhatsApp); the agent
  prepares payloads, test steps, evidence templates, and triages results.
- `automated` — local repos/labs (OSS MCP servers, agent frameworks): the agent runs tests
  directly in a sandbox and captures effect artifacts.

## Sources encoded
- Operator arsenal: 21 IPI methods (arsenal/ipi), L1–L13 laws, FX1 in-band input rule,
  objective shaping / provenance frames / tool-framing, stochastic-retry discipline.
- Program rules: MSRC Copilot bounty terms (scope, out-of-scope, conversation ID evidence).
- Taxonomy: CWE + AI-native classes, MITRE ATLAS AML.T0051, OWASP LLM01.
