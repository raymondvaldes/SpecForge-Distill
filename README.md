# SpecForge Distill

`main` is preparing `v1.2.2-dev`. The latest stable release is `v1.2.1`.

Transform digital-text specification PDFs into structured, provenance-linked Markdown and JSON.

SpecForge Distill is designed to be usable without a Python setup. For most users, the fastest path is to download a single CLI binary for your platform and run it locally.

## Trusted Download And Run

Official downloads are GitHub Releases assets only. If a binary, checksum file, or copied mirror did not come from that page, discard it and start again from the official release.

The examples below use the current `v1.2.1` asset contract. Replace `v1.2.1` with the release tag you are installing.

Available release assets:

- Ubuntu / WSL x64: `distill-v1.2.1-linux-x64`
- macOS Intel: `distill-v1.2.1-macos-x64.zip`
- macOS Apple Silicon: `distill-v1.2.1-macos-arm64.zip`
- Windows PowerShell 7 x64: `distill-v1.2.1-windows-x64.exe`

## Quick Start (Pre-Built Binary)

Once you've downloaded the appropriate asset for your platform:

1.  Verify the checksum (see `SHA256SUMS.txt` in the release assets).
2.  Make the binary executable (macOS/Linux): `chmod +x distill-v1.2.1-macos-arm64` (example).
3.  Run the CLI: `./distill-v1.2.1-macos-arm64 spec.pdf`

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
- **Structured Output:** Generates both Markdown for human review and JSON for machine interop.
- **Digital-Text Only:** Optimized for searchable PDF specifications (not scanned images).
- **No-Runtime CLI:** Single-file binaries available for all major platforms.
