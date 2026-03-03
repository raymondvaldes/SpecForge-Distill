# SpecForge Distill

`main` is preparing `v1.2.3-dev`. The latest stable release is `v1.2.2`.

Transform digital-text specification PDFs into structured, provenance-linked Markdown and JSON.

SpecForge Distill is designed to be usable without a Python setup. For most users, the fastest path is to download a single CLI binary for your platform and run it locally.

## Trusted Download And Run

Official downloads are GitHub Releases assets only. If a binary, checksum file, or copied mirror did not come from that page, discard it and start again from the official release.

The examples below use the current `v1.2.2` asset contract. Replace `v1.2.2` with the release tag you are installing.

Available release assets:

- Ubuntu / WSL x64: `distill-v1.2.2-linux-x64`
- macOS Intel: `distill-v1.2.2-macos-x64.zip`
- macOS Apple Silicon: `distill-v1.2.2-macos-arm64.zip`
- Windows x64: `distill-v1.2.2-windows-x64.exe`

## Quick Start (Pre-Built Binary)

Once you've downloaded the appropriate asset for your platform:

1.  Verify the checksum (see `SHA256SUMS.txt` in the release assets).
2.  Make the binary executable (macOS/Linux): `chmod +x distill-v1.2.2-macos-arm64` (example).
3.  Run the CLI: `./distill-v1.2.2-macos-arm64 spec.pdf`

Every binary includes a `--self-test` flag that runs a subset of the integration tests using embedded fixtures to ensure the extraction engine is healthy on the current host.

```bash
./distill-v1.2.2-macos-arm64 --self-test
```

## Developer / Source Installation

If you prefer to run from source or contribute:

```bash
# Clone the repository
git clone https://github.com/raymondvaldes/SpecForge-Distill.git
cd SpecForge-Distill

# Set up a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies and the package in editable mode
pip install -e .
```

Usage from source:

```bash
python -m specforge_distill.cli path/to/your/spec.pdf
```

## Features

- **Provenance-Linked Extraction:** Every extracted requirement maintains a link back to its source page and context in the PDF.
- **Strict Modal Capture:** Focuses strictly on `shall`, `must`, and `should` obligations to minimize noise.
- **Automatic Note Merging:** Contextual `Note:` blocks are automatically appended to their parent requirements.
- **Structured Output:** Generates both Markdown for human review and JSON for machine interop.
- **No-Runtime CLI:** Single-file binaries available for all major platforms.

## Documentation & Support

- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common failure modes and fixes.
- [Build Instructions](docs/BUILD.md) - How to build the project from source and produce binaries.
- [Release Notes](docs/RELEASE_NOTES_v1.2.2.md) - What's new in the latest version.
- [Engineering Standards](docs/ENGINEERING_STANDARDS.md) - Project architectural and style mandates.
