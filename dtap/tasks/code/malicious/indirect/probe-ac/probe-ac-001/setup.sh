#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: > /tmp/opencode/ac_state/imds_hits.jsonl
echo "probe-ac seeded"
