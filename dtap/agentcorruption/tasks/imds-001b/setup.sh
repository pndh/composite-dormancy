#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

for f in imds_hits collector control_calls memory_events; do
  : > /tmp/opencode/ac_state/${f}.jsonl 2>/dev/null || true
done

C=$(docker ps --format '{{.Names}}' | grep -E 'terminal-env-1$' | head -1)
if [ -n "$C" ]; then
  docker exec "$C" mkdir -p /app/docs /app/tools /app/release
  docker cp metadata/platform_notes.md "$C:/app/docs/platform_notes.md"
  docker cp metadata/preflight.sh "$C:/app/tools/preflight.sh"
  docker exec "$C" chmod +x /app/tools/preflight.sh
  echo "imds-001b seeded into $C"
else
  echo "imds-001b: no terminal container found at setup time" >&2
fi
