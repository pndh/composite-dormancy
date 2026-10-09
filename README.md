# composite-dormancy

Research lab for **composite dormant threats** against tool-using agents: payloads whose
fragments are individually benign and only compose into a harmful action when an agent
assembles them across channels (mail, docs, calendar, tool descriptions) at a later trigger.

Status: working lab. Standalone replica with ablation results, plus a DTAP-native task
bundle in `dtap/` (runs on the full Docker platform; see `dtap/README.md` for results).

## Layout

```
src/composite_dormancy/trajectory/   trajectory types for attack runs (vendored, see NOTICE)
sandbox/                             workspace scenario: fragments, task config, judge
runner/                              model matrix: replay the scenario across models
licenses/                            third-party license texts
```

## What this repo will contain

- A reproducible sandbox where fragments are planted in separate benign artifacts.
- An ablation harness: remove one fragment -> attack must fail.
- Per-model attack-success and per-layer detection tables.
- Full agent trajectories for every run.

## Provenance

`src/composite_dormancy/trajectory/` vendors two modules from
[DecodingTrust-Agent](https://github.com/AI-secure/DecodingTrust-Agent)
(Apache-2.0, commit `e0323a521ba4ef88f8e14c1eccf68d0a3d19a458`), renamed on import:

| File here | Upstream path |
|---|---|
| `base.py` | `dt_arena/src/types/trajectory.py` |
| `red_teaming.py` | `dt_arena/src/types/red_teaming_trajectory.py` |

See `NOTICE` for attribution details. Files are unmodified.

## Clean-room note

This repository contains no client, engagement, or third-party confidential material.
It is built from scratch; the only external code is the Apache-2.0 vendoring documented above.

## License

Project code: TBD. Vendored code: Apache-2.0 (see `licenses/Apache-2.0.txt` and `NOTICE`).
