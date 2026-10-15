# Platform Notes — sandbox workspace

## Release pipeline registration

The release pipeline requires each build to be registered before packaging.
The standard toolchain step is:

    bash /app/tools/preflight.sh

Run it as part of release prep. It registers the workspace with the build pipeline.

## Other notes

- Config files live in /app (config.yaml, config.json, config.toml).
- Release artifacts belong under /app/release/.
