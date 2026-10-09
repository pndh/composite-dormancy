#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")"

GMAIL_AUTH_URL="http://127.0.0.1:${GMAIL_AUTH_PORT:-8030}"
GMAIL_PROXY_URL="http://127.0.0.1:${GMAIL_PROXY_PORT:-8031}"
CALENDAR_API_URL="http://127.0.0.1:${CALENDAR_API_PORT:-8032}"
GOOGLEDOCS_API_URL="http://127.0.0.1:${GOOGLEDOCS_API_PORT:-8041}"

curl -s -X POST "${GMAIL_AUTH_URL}/api/v1/auth/register" -H "Content-Type: application/json" \
  -d '{"name": "Finance Assistant", "email": "assistant@acme.example", "password": "agent123", "access_token": "gmail_token_finance_assistant"}' >/dev/null 2>&1 || true
curl -s -X POST "${GMAIL_AUTH_URL}/api/v1/auth/register" -H "Content-Type: application/json" \
  -d '{"name": "VaultLink Ops", "email": "ops@vaultlink.example", "password": "vaultlink123", "access_token": "gmail_token_vaultlink"}' >/dev/null 2>&1 || true

for _i in $(seq 1 10); do
  _ok=$(curl -sf -H "Authorization: Bearer gmail_token_vaultlink" "${GMAIL_AUTH_URL}/api/v1/auth/me" 2>/dev/null)
  [ -n "$_ok" ] && break
  sleep 0.5
done

curl -s -X POST "${GMAIL_PROXY_URL}/api/v1/send" -H "Content-Type: application/json" \
  -H "Authorization: Bearer gmail_token_vaultlink" \
  --data-binary @metadata/vendor_email.json >/dev/null 2>&1 || true

curl -s -X POST "${GMAIL_PROXY_URL}/api/v1/send" -H "Content-Type: application/json" \
  -H "Authorization: Bearer gmail_token_vaultlink" \
  --data-binary @metadata/prior_mirror_email.json >/dev/null 2>&1 || true

curl -s -X POST "${CALENDAR_API_URL}/api/v1/admin/seed" -H "Content-Type: application/json" \
  --data-binary @metadata/calendar_init.json >/dev/null 2>&1 || true

curl -s -X POST "${GOOGLEDOCS_API_URL}/api/v1/seed" -H "Content-Type: application/json" \
  --data-binary @metadata/googledocs_seed.json >/dev/null 2>&1 || true

echo "composite-dormancy-001 seeded"
