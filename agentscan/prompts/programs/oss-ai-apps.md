# Program playbook — self-hosted AI/agent apps (OSS CVE track)

Beginner-friendly because: real code, no scope ambiguity, local install, GitHub advisories →
CVE via GitHub's CNA, low competition per target compared to big-tech programs.

## Target shortlist (self-hostable, agent/tool surfaces, active advisories)
- **Open WebUI** — chat UI + tools/RAG; auth, file upload, SSRF, path handling.
- **n8n** — workflow automation with AI agents; expression injection, SSRF, authz.
- **Flowise** — agent/flow builder; custom tools, auth bypass, RCE classes.
- **Langflow** — flow builder; path traversal, code execution via components.
- **Dify** — LLM app platform; SSRF, authz, file handling.
- **LibreChat / AnythingLLM** — chat + connectors; auth, SSRF, file handling.
- **Ollama / vLLM / LiteLLM** — model servers/gateways; path traversal, SSRF, authz, deserialization.
- **MCP servers** (filesystem/git/fetch/browser/db) — tool-arg sinks (traversal, SSRF, injection).

## What to hunt (architecture-driven)
- Tool/param → sink: filesystem path, shell, SQL, URL fetch, archive extraction, template.
- Auth on API/webhook endpoints; multi-user boundaries; share/public links.
- File upload → storage path, type confusion, zip-slip, symlink.
- Connector/OAuth token handling; SSRF to internal/metadata endpoints.
- Agent flows: untrusted content → tool action (read/write/execute violations).

## Process
1. Clone + run the released version locally (docker compose if provided).
2. Map entry points and tool handlers; check advisories/dupes first.
3. PoC with a canary (file outside root / callback to your listener / command output).
4. Report via the repo's SECURITY.md / GitHub Security Advisory; request CVE via maintainer or
   GitHub CNA. 90-day disclosure norm; publish writeup after fix.

## Quality bar
- Affected version + minimal repro + effect artifact + fix suggestion.
- No duplicates of public advisories; check release notes and GitHub advisories.
- Behavior-only findings are not bugs here — need an effect (file read, request, execution).
