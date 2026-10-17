# Cost ledger — OSS recon passes (agentscan)

All costs are operator-side (this machine). **Model API cost: $0** — these recon passes are
tool-driven (shell/HTTP/docker) and make no LLM API calls. If a future pass uses model-driven
agents via OpenRouter, cost will be itemized per-token here.

| Date | Target | Method | Disk (image/clone) | Wall time | API $ |
|---|---|---|---|---|---|
| 2026-10-17 | Open WebUI 0.12.3 | docker `ghcr.io/open-webui/open-webui:main` | 6.38 GB / 79 MB | ~35 min | 0 |
| 2026-10-17 | n8n 2.43.7 | docker `docker.n8n.io/n8nio/n8n:latest` | 1.8 GB / 354 MB | ~25 min | 0 |
| 2026-10-17 | Flowise 3.1.4 (latest) | docker `flowiseai/flowise:latest` — **broken image**, removed | 9.29 GB (freed) / 71 MB | ~20 min | 0 |
| 2026-10-17 | Langflow 1.12.6 | pip (killed after 8m36s) → **uv** (~90s) | venv 1.7 GB (no clone) | ~30 min | 0 |

Notes:
- Peak disk from images ~17.5 GB; Flowise image removed after the broken-image diagnosis
  (freed 9.29 GB; disk went 92% → 87%).
- Containers are stopped after each pass; images kept only for repeating tests.
- Network: ~17.5 GB pull bandwidth (Open WebUI 6.4 + n8n 1.8 + Flowise 9.3).
- No cloud sandboxes, no paid APIs, no bounty submissions (account-bound actions left to operator).

## Lessons that save cost next time
1. **Check the image health before deep pull**: Flowise `latest` ships broken deps
   (`@smithy/eventstream-codec` missing, LangChain export mismatch) and exits at init.
2. **Pinned tags > latest** for reproducibility; verify tag age (Flowise latest = 2026-07-29).
3. **Boot timing**: n8n mounts REST routes only after migrations; healthz ≠ ready. Wait for
   `/rest/settings` 200 before running the matrix.
4. Prefer Python/pip targets (Langflow) when docker images are multi-GB and brittle.

## Final tally (2026-10-17 session)
- Targets attempted: Open WebUI 0.12.3, n8n 2.43.7, Flowise 3.1.4 (broken image), Langflow 1.12.6.
- **Findings: 0 exploitable; 2 low notes (Open WebUI CORS/clickjacking) + 1 informational (n8n member directory).**
- Downloads: ~17.5 GB images + ~1.7 GB venv + ~0.5 GB clones; Flowise image (9.29 GB) removed after diagnosis.
- Wall time: ~1h50m of agent/tool time across four targets (~25–35 min each).
- **Model API cost: $0** (no OpenRouter calls; recon is tool-driven).
- Account-bound actions intentionally not performed: 0din submission, Gray Swan, MSRC portal.
