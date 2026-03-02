# Build and Release Strategy

`main` is currently preparing `v1.2.2-dev`. The latest stable release tag is `v1.2.1`.

This document describes how to produce the single-file binaries available in the official GitHub Releases.

## Reproducible Environment

The CI uses a locked environment defined in the `Dockerfile`. To reproduce the exact build environment locally:

```bash
docker build -t specforge-distill-builder .
```

## Creating Release Assets

Official downloads are GitHub Releases assets only. 

The examples below use the current `v1.2.1` asset contract. Replace `v1.2.1` with the release tag you are building or verifying.

Available release assets:

- Ubuntu / WSL x64: `distill-v1.2.1-linux-x64`
- macOS Intel: `distill-v1.2.1-macos-x64.zip`
- macOS Apple Silicon: `distill-v1.2.1-macos-arm64.zip`
- Windows x64: `distill-v1.2.1-windows-x64.exe`

### Linux Build

```bash
VERSION=v1.2.1
docker run --rm -v $(pwd):/app specforge-distill-builder \
    pyinstaller --onefile --name distill-${VERSION}-linux-x64 src/specforge_distill/cli.py
```

### macOS Build

Requires a macOS runner (Apple Silicon or Intel).

```bash
VERSION=v1.2.1
pip install .
pyinstaller --onefile --name distill-${VERSION}-macos-arm64 src/specforge_distill/cli.py
zip distill-${VERSION}-macos-arm64.zip distill-${VERSION}-macos-arm64
```

### Windows Build

Requires PowerShell 7.

```powershell
$version = "v1.2.1"
pip install .
pyinstaller --onefile --name distill-${version}-windows-x64 src/specforge_distill/cli.py
```

## Checksum Verification

Every release includes a `SHA256SUMS.txt` file. Before running a downloaded binary, verify its integrity:

```bash
sha256sum -c SHA256SUMS.txt
```

## Self-Test

Every binary includes a `--self-test` flag that runs a subset of the integration tests using embedded fixtures to ensure the extraction engine is healthy on the current host.

```bash
./distill --self-test
```
