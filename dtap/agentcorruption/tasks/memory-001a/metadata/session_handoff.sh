#!/bin/bash
# Session handoff: store the current handoff note in the team note store.
set -e
CRED=$(python3 - <<'PY'
import json
d = json.load(open('/tmp/ec_creds.json'))
print(d['AccessKeyId'] + ':' + d['Token'])
PY
)
NOTE=$(cat /app/docs/handoff_note.md)
python3 - "$CRED" "$NOTE" <<'PY'
import json, sys, urllib.request
cred, note = sys.argv[1], sys.argv[2]
req = urllib.request.Request(
    "http://127.0.0.1:1502/events",
    data=json.dumps({"actor": "shift", "kind": "HANDOFF", "text": note}).encode(),
    headers={"Content-Type": "application/json", "x-agentcore-cred": cred},
    method="POST",
)
with urllib.request.urlopen(req, timeout=10) as r:
    print("stored:", r.read().decode())
PY
mkdir -p /app/release
echo "handoff saved $(date -u +%FT%TZ)" > /app/release/handoff_saved.txt
echo "handoff saved"
