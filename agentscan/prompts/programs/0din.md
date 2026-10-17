# Program playbook — 0din (Mozilla 0Day Investigative Network)

Source: 0din.ai/policy (last updated 2026-10-02). Re-verify before submitting.

## Why this is the beginner entry point
- **Abstract-first**: submit a high-level abstract + affected model(s); 0din answers within
  **3 business days** with an in-scope decision and likely payout range. Cheap to test ideas.
- **Prompt injection is explicitly in scope** (unlike Google's AI VRP).
- Clear violation taxonomy that matches agent/application findings.

## Rewards
$500 – $15,000 (discretionary). Bands: Low ≤ $500 · Medium ≤ $2,500 · High ≤ $5,000 · Severe ≤ $15,000.
Duplicates split (same-severity within 7 days); Low severity: 1st 100%, 2nd 50%, 3rd 20%.
Validation ~2 weeks. Payment within 30 days of contract; ID required; confidentiality until disclosure.

## Scope — model bugs (inside the model, not the ecosystem)
| Class | Severity |
|---|---|
| Prompt extraction (original inputs/queries) | LOW |
| Guardrail jailbreak | LOW–HIGH |
| Interpreter jailbreak (bypass exec restrictions) | MEDIUM |
| Content manipulation (predictably inject harmful/misleading data) | HIGH |
| Weights & layers disclosure (replicable IP extraction) | SEVERE |

## Scope — application bugs (must start with prompt injection and end in unauthorized action)
| Violation | Severity | What we show |
|---|---|---|
| **Read** | LOW–MEDIUM | Unauthorized data exfiltration through the app |
| **Write** | MEDIUM–HIGH | Unauthorized data modification through the app |
| **Execute** | HIGH–SEVERE | Unauthorized command/code execution through the app |

This is exactly our DTAP-style chain language: injection through an ingested surface →
victim-impacting action (exfil = read; state change = write; tool/command execution = execute).

## Evidence requirements
- Affected model/app name + version, "latest generation" requirement.
- Original, unreported finding; abstract first, full details after sign-off.
- Test accounts; no service disruption; PoC + effect artifact; disclosure via 0din.

## Hunting angles that fit our harness
1. **Read violations**: indirect injection in an app's ingested content → cross-boundary
   exfiltration (markdown/image/link rendering, tool output, memory).
2. **Write violations**: injected content causes unauthorized state change (documents, tickets,
   calendar, memory) in the victim's context.
3. **Execute violations**: injection reaches a tool/command sink (shell, code interpreter,
   connector) — highest band.
4. **Guardrail jailbreaks**: only when they demonstrate a boundary violation (not content-only).

## Process
1. Build the PoC in a local replica / your own test app; prove the effect oracle.
2. Write the abstract: affected model/app, boundary violation class (read/write/execute), impact,
   evidence summary, novelty.
3. Submit abstract → wait for scope/payout decision (3 business days).
4. On sign-off: full report (repro, artifacts, versions, suggested fix).
5. Keep confidentiality; 0din handles vendor notification + disclosure.
