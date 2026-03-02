# Release Notes: v1.2.1

This release addresses the initial push issues, stabilizes the SSH configuration for developers, and fixes versioning inconsistencies in the documentation.

## Release Snapshot

- Latest stable release: `v1.2.1`
- Status: Released

## Highlights

- **Permanent SSH Configuration:** Fixed a recurring issue where GitHub SSH keys were not consistently being presented.
- **Documentation Alignment:** Synchronized `README.md`, `pyproject.toml`, and internal version strings to `v1.2.1`.

## Fixed

- Corrected mismatched version strings in `README.md` that incorrectly pointed to `v1.1.0`.
- Resolved a "Permission Denied (publickey)" error for Git operations by establishing a persistent `~/.ssh/config` for GitHub.

## Documentation

- Updated `README.md` to reflect the current installation paths and asset naming conventions for the `v1.2.x` series.

## Packaging And Release

- Bumped project version to `1.2.1` in `pyproject.toml`.
- Corrected release asset download examples to use the `v1.2.0` stable base.

## Upgrade Path

- No breaking changes. Users on `v1.2.0` are encouraged to update to `v1.2.1` for accurate documentation and smoother developer workflows.
