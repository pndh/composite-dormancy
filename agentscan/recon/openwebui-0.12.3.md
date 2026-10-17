# Recon report — Open WebUI 0.12.3 (local instance)

Date: 2026-10-17 · Mode: automated/local · Accounts: 2 synthetic (admin, user2) · Synthetic canary data only
Target: `ghcr.io/open-webui/open-webui:main` (version 0.12.3, digest 302987a7…) on 127.0.0.1:3000

## Scope and method
Real released image, local install. Black-box pass + targeted code review. Goal: find an
effect-proven vulnerability (CVE/advisory path). No live/third-party targets touched.

## Tests and results

| # | Test | Result |
|---|---|---|
| 1 | Unauth matrix on resource APIs (users/chats/files/knowledge/folders/channels/tools/functions/configs) | 401 on all |
| 2 | CORS preflight from `https://evil.example` and `null` | **ACAO echoes origin + `Allow-Credentials: true`** (default `CORS_ALLOW_ORIGIN=*` with Starlette reflection) |
| 3 | Session cookie flags | `HttpOnly; SameSite=lax; Path=/` (no `Secure` over HTTP); 28-day Max-Age |
| 4 | Security headers on `/` and `/api/config` | **None** (no X-Frame-Options / CSP frame-ancestors / HSTS / Referrer-Policy); `x-process-time` present |
| 5 | Path traversal probes (`/static/../…`, encoded variants, `/api/v1/files/../../etc/passwd`) | 404 / SPA fallback; no file read. Upload path uses `os.path.basename` |
| 6 | Share enumeration (`chats/share/{uuid,1,test}`) | 401 uniformly |
| 7 | Cross-user IDOR with 2 accounts: admin chat/note/KB/file vs user2 | 401/403/404 — **denied** (chat by id, note by id, KB by id, file by id/content) |
| 8 | Signin brute-force throttling (12 attempts, nonexistent user) | all 400, no 429 observed (default setup; rate limiting appears optional/redis-dependent) |
| 9 | SCIM/MFA/terminals "unauth 200" | **False positive** — SPA fallback (`text/html` index.html) for unmounted paths; SCIM route is bearer-token gated in code |
| 10 | SSRF on URL ingestion (`/process/url`, web loaders) | Guarded: `validate_url` + `get_ssrf_safe_session` (connect-time IP pin, defeats rebinding) + `allow_redirects=False` |
| 11 | `kb_exec` tool (pseudo-shell) | Whitelisted command map over KB files (ls/cat/grep/…); **no subprocess** |
| 12 | Terminals WS proxy | First-message auth, `session_id` URL-quoted, identity from server (`X-User-Id`), per-connection access check |

## Low-severity notes (not advisories yet; need impact/in-scope review)
- **CORS default reflects any origin with credentials.** Mitigated by `SameSite=lax` session cookie
  (cross-site fetch cannot send it). Becomes higher-impact with `WEBUI_AUTH_COOKIE_SAME_SITE=none`
  or token-in-header deployments. Candidate for a config-hardening report, not a standalone CVE.
- **No framing protection** (no X-Frame-Options / CSP frame-ancestors) → clickjacking surface.
  Low severity; check whether project treats UI framing as in scope.
- **`x-process-time`** on all responses — minor timing/info leak.
- **Signin spam not throttled in default in-memory setup** — deployment-dependent.

## Methodology lessons (kept for the harness)
- **SPA fallback poisons status-code-only matrices.** Unknown `/api/*` paths return `200 text/html`
  (index.html). Always assert `content-type: application/json` before calling a 200 a hit. This
  single check prevented 4 false positives in this pass.
- Code-reading hardcoded by 100+ advisories: terminal identity spoofing, XSS→ATO, Vega client
  SSRF, stored XSS via tool embeds were all recently fixed. Manual recon of these areas is low-yield.
- The project's SSRF/WS/authz code shows deliberate hardening (comments cite rebinding, redirect
  SSRF, integrity-unbound identity). Treat as "hard mode" target.

## Hypothesis backlog (next round, ranked)
1. **Channels webhooks** — token scoping/replay: can a webhook token target other channels or
   act after revocation? (new feature, relatively less advisory coverage)
2. **Notes/folders ACL staleness** — past advisory class (shared folder/KB stale membership);
   test current revocation paths for similar gaps.
3. **MFA recovery token flows** — challenge/redeem semantics, token reuse, cross-account binding.
4. **OAuth token exchange (when explicitly enabled)** — trusted-client introspection is fail-closed
   when endpoint missing; verify claim-shape coverage (roles/groups) against role policy.
5. **Apps/custom URL surfaces** — `utils/apps.py` private-origin rules; check redirect/rebinding edges.
6. **Share modes** (`share_mode=continue`) and admin chat access — boundary between read/write.

## Recommendation
Do not sink more time into Open WebUI as a first CVE target. Pivot to a less-hardened OSS agent
platform (n8n, Flowise, Langflow, Dify) with the same harness and the same matrix, and keep Open
WebUI as the "hard mode" calibration. For 0din, app-layer chains (read/write/execute violations)
remain the right angle — but pick a target where the renderer/tool boundary is still loose.
