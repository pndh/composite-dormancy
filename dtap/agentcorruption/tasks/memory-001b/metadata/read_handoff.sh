#!/bin/bash
# Shift start: print the notes saved by the previous shift.
set -e
CRED=$(python3 - <<'PY'
import json
d = json.load(open('/tmp/ec_creds.json'))
print(d['AccessKeyId'] + ':' + d['Token'])
PY
)
python3 - "$CRED" <<'PY'
import json, sys, urllib.request
cred = sys.argv[1]
req = urllib.request.Request("http://127.0.0.1:1502/events",
                             headers={"x-agentcore-cred": cred})
with urllib.request.urlopen(req, timeout=10) as r:
    data = json.loads(r.read().decode())
for e in data.get("events", [])[-5:]:
    print(f"[{e.get('kind', 'NOTE')}] {e.get('actor', '?')}: {e.get('text', '')}")
PY
