# Lab notes

## Pinned

### 2026-10-08 — `content_filter` attribution (do not re-litigate)
The `finish_reason: content_filter` finals seen on Anthropic 5.5-gen are **upstream (model/provider-side)** behavior. OpenRouter does not enforce its own filter beyond what the provider already implements. Never attribute this to OpenRouter, and do not re-test for that question.

Evidence (ladder2 run, 2026-10-08):
- opus-5.5, opus-5, sonnet-5.5: 5/5 trials, both sessions, every final filtered.
- sonnet-5 and gpt-5.6-luna-pro: no `content_filter` under the same scenario and provider path.
