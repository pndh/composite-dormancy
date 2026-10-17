# Program playbook — Microsoft Copilot Bounty (MSRC)

Source: MSRC Copilot Bounty Program page (bounty-ai), revision history through 2026-04-07.
Re-verify scope/rules at submission time — programs change.

## Scope (personal account only)
- Copilot AI experiences on copilot.microsoft.com and copilot.ai (browser, all major vendors)
- Copilot integrated in Microsoft Edge (Windows), incl. Copilot Mode
- Microsoft Copilot app (iOS, Android)
- Copilot integrated in Windows OS via the Copilot app
- Copilot on WhatsApp and Telegram

## Awards and bar
- $250 – $30,000 USD. Severity per **MSRC AI severity classification** + online services bar.
- Must be reproducible on the **latest, fully patched** version.
- Paid vulnerability types include: deserialization of untrusted data, code injection,
  authentication issues, SQL/command injection, SSRF, improper access control, information
  disclosure, XSS, CSRF, web security misconfiguration, cross-origin issues, improper input
  validation, inference manipulation, inferential information disclosure.

## Out of scope (critical for hypothesis ranking)
- **Prompt injection attacks without a security impact on users other than the attacker.**
- Model hallucination where the model pretends to run code.
- Attacks that aim to leak (part of) the system/meta prompt.
- Content-related issues (report separately as "AI derived harm", not bounty).
- DoS; URL redirects alone; cookie replay; subdomain takeover; low-impact CSRF; server-side
  info disclosure (IPs, server names, most stack traces); debug pages / de-minified JS.
- Bugs requiring extensive/unlikely user actions; bugs in user-created content/apps;
  third-party software without demonstrable impact on the service.
- Training, documentation, samples, community forums.

## Submission requirements
- MSRC Researcher Portal; Product: **"Copilot, AI+ML, and LLMs"**.
- Include **conversation ID** (chat command `/id`) in Steps to reproduce.
- Describe the attack vector; provide minimal repro and evidence.
- Use a personal research account; add **MSOBB** to account name.
- Follow MSRC Rules of Engagement and CVD policy.

## What this means for hunting (impact-first)
The program pays for **victim-impact chains**, not for "the model obeyed me". So the unit of
proof is: attacker-controlled surface → model processes it in the *victim's* context → effect
on the victim (data leaves their context, action taken in their account, access boundary
crossed). Design every test with two accounts you own (attacker + victim) or with
attacker-content → your-own-victim-session, and record both sides.

Highest-fit hypothesis families for this program:
1. **Output-rendering exfil** — model emits links/images/markdown from attacker content;
   victim client renders → request to attacker canary (XSS/rendering + info disclosure).
2. **Ingested-content injection with cross-boundary effect** — documents/emails/web pages the
   victim asks Copilot about; effect must reach the victim (not just attacker).
3. **SSRF via browsing/fetching** — reach internal/link-local endpoints; prove with canary or
   response differential; impact required.
4. **Improper access control / cross-account data** — conversation or file access boundaries
   in the consumer app / Edge / mobile / WhatsApp surfaces.
5. **Auth/session issues** (account linking, token handling) — excluding cookie replay and
   low-impact CSRF.
6. **Inference/inferential disclosure** — only with a security impact.

## Mode
Consumer surfaces have no public automation API and the Rules of Engagement forbid abusive
automation → default mode is **assisted**: the agent prepares hypotheses, payloads, test steps
and evidence templates; the human executes in the browser/app and feeds artifacts back.
For OSS repos and local lab targets, the same harness runs fully automated.

## Pitfalls
- "Prompt injection" alone is explicitly unpaid — always design for victim impact.
- Do not touch other users' accounts or real data; two owned accounts is the ceiling.
- Keep evidence timestamps + version (Copilot UI build) + conversation IDs.
- Duplicate risk is high (public research exists, including EchoLeak-class work) — check before
  investing; aim at surfaces less covered (Edge Copilot Mode, Windows app, mobile, WhatsApp).
