# AGENTS.md

## Mission

This repository is in the `v1.1.0` development cycle. The latest shipped release is `v1.0.1`. Priorities are:

1. Fix bugs and regressions in extraction, rendering, packaging, and CLI behavior.
2. Preserve the binary-first install/use experience on WSL, Ubuntu, macOS, and Windows PowerShell 7.
3. Expand the product deliberately in `v1.1.0`, especially around batch workflows, unsupported-input diagnostics, and downstream validation/interop hooks.
4. Keep local, Docker, and release-binary workflows aligned with the latest stable release.

## Working Standards

- Prefer cross-platform instructions and code paths. If a workflow is shell-specific, document both POSIX and PowerShell 7 variants or provide a Python-based alternative.
- Do not assume `bash`, GNU utilities, or Unix path behavior on Windows.
- Prefer `python -m pip ...` and `python -m specforge_distill.cli ...` in docs when that improves portability.
- Preserve deterministic output. Changes must not introduce unstable ordering, IDs, or manifest content.
- Keep docs copy-pasteable. Every command shown in README/docs should be valid for the platform section it appears in.

## Version Discipline

When touching release/version work, keep these version markers synchronized:

- `pyproject.toml`
- `src/specforge_distill/__init__.py`
- CLI help/version text
- `README.md`
- release notes and sample manifests/docs when they expose a version string

If version markers disagree, treat that as release debt and call it out explicitly.
On `main`, the development version should remain `1.1.0.dev0` until the next release cut. User-facing docs should clearly distinguish the latest stable release (`1.0.1`) from in-progress development work.

## Platform Focus

User-facing setup and usage should be validated for:

- WSL
- Ubuntu
- macOS
- Windows PowerShell 7

Avoid documenting Linux-only shell wrappers as the primary path for Windows users. If a helper script is bash-only, pair it with a PowerShell-friendly command path.

## Build and Packaging Context

- Python package metadata lives in `pyproject.toml`.
- The release workflow in `.github/workflows/release.yml` builds PyInstaller executables for Ubuntu, macOS, and Windows.
- Docker support is defined by `Dockerfile`.
- The root `distill` script is a convenience runner, but it is not the portable entrypoint for every environment.

Any packaging change should consider all three paths:

1. Source install via `pip`
2. Docker image usage
3. GitHub release binaries

## Documentation Expectations

README and docs should make it easy for a new user to:

1. Install from source
2. Run a release binary
3. Use Docker
4. Verify the install with a minimal command
5. Build executables or packages locally
6. Understand platform-specific caveats, especially WSL and PowerShell 7

If a workflow is materially different on one platform, document it in a dedicated section instead of hiding it in prose.
Maintain the in-progress release-note draft at `docs/RELEASE_NOTES_v1.1.0.md` whenever a user-visible feature, fix, docs change, packaging change, known issue, or upgrade-path note changes during the `v1.1.0` cycle.

## Verification

Use the smallest relevant verification set for the change:

- `python -m pip install -e .`
- `pytest`
- `python -m specforge_distill.cli --help`
- `python -m specforge_distill.cli <pdf> --dry-run`
- `docker build -t distill .`

For doc-only changes, verify commands for correctness against the current code and packaging behavior.
