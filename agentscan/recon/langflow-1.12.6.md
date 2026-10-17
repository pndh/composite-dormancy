# Recon report — Langflow 1.12.6 (local instance)

Date: 2026-10-17 · Mode: automated/local · Accounts: superuser + 1 member · Synthetic data only
Target: `pip`/`uv` install of `langflow` 1.12.6, 127.0.0.1:7860

## Context noticed
37 advisories, including criticals: unauthenticated RCE via public flow build (fixed 2026-03),
authenticated RCE via MCP stdio transport (2026-09-10), IDOR in `/api/v1/responses` (2026-06),
cross-project file disclosure via MCP resources (2026-09-22), SSRF in URL-taking components
(2026-09-28, "protection disabled by default / warn-only"), path traversal in Knowledge Bases
(2026-06-11), weak Fernet key (2026-08-12). The project ships fixes fast; current 1.12.6 is
post-fix for these classes.

## Deployment notes (cost-relevant)
- `pip install langflow` resolver ran **8m36s** without finishing → killed.
- `uv pip install langflow` finished in **~90s**; venv **1.7 GB**. Lesson: use uv for Python target installs.
- Default run requires auth even with `type: public` config (`403 No authentication credentials provided`).
  Restarted with `LANGFLOW_AUTO_LOGIN=false`, explicit superuser, secret key. Login is form-encoded
  OAuth2 (`application/x-www-form-urlencoded`), returns access/refresh JWT.

## Tests and results

| # | Test | Result |
|---|---|---|
| 1 | Unauth API matrix (flows, validate/code, files, build_public_tmp) | **403 / 404** — auth required |
| 2 | `POST /api/v1/validate/code` unauth (historic RCE class) | **403**; canary file not written |
| 3 | Superuser login + flow creation | OK |
| 4 | Second user creation + login | OK (superuser-only user admin) |
| 5 | IDOR: member → superuser flow by id / files list | **404 "Flow not found"**; users list **403 privileges** |
| 6 | File endpoints: traversal on `download/{flow_id}/{file_name}`, `list/{flow_id}` (raw + encoded) | **404**, no file read |
| 7 | Public flow/build endpoints (historic unauth RCE) | 404 for unknown ids; no public flows exposed |
| 8 | SSRF guards (code + defaults) | **enabled by default** (`ssrf_protection_enabled=True`, connector validation True, loopback disallowed); A2A util rejects private/metadata IPs **even when the global toggle is off** ("hard floor") |
| 9 | A2A routes | `/api/v1/a2a/agents` 404 (disabled/empty) |

## Verdict
No exploitable finding on this pass. Authz/IDOR/file handling held; the SSRF advisory class is
mitigated with a hard floor; public-build RCE class is closed. Same pattern as Open WebUI and n8n:
the project just went through security hardening, and the easy classes are gone.

## Next step that actually fits hardened targets
**Patch-diff / n-day variant analysis.** Pick one of the recent advisories (e.g., the MCP stdio RCE
2026-09-10 or the SSRF "warn-only" 2026-09-28), diff the fix commit, and test whether the fix is
complete (alternate transports, alternate endpoints, bypass of the guard). That is the standard way
to find a *new* issue in a hardened project. Also worth a look: the "deprecated" `/api/v1/build/{flow_id}`
cross-user advisory (2026-09-28) — verify deprecated paths still enforce ownership on this version.
