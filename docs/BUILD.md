# Build Guide

This guide is for contributors and release maintainers. End users should normally download a prebuilt binary from the [GitHub Releases](https://github.com/raymondvaldes/SpecForge-Distill/releases) page instead of building from source.

`main` is currently preparing `v1.1.0.dev0`. The latest stable release tag is `v1.0.1`.

## Release Targets

The release workflow produces one-file executables for:

- Ubuntu / WSL x64: `distill-linux-x64`
- macOS Intel: `distill-macos-x64.zip`
- macOS Apple Silicon: `distill-macos-arm64.zip`
- Windows x64: `distill-windows-x64.exe`

## Prerequisites

- Python 3.11 recommended for local builds
- `pip`
- `pyinstaller`
- `pytest` for local verification
- Docker only if you want to validate the container workflow

## Build On Ubuntu, WSL, Or macOS

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Build a Linux binary:

```bash
python -m PyInstaller --noconfirm --clean --onefile --name distill-linux-x64 --collect-data specforge_distill src/specforge_distill/cli.py
./dist/distill-linux-x64 --version
./dist/distill-linux-x64 --help
```

Build a macOS Intel binary:

```bash
python -m PyInstaller --noconfirm --clean --onefile --name distill-macos-x64 --collect-data specforge_distill src/specforge_distill/cli.py
./dist/distill-macos-x64 --version
./dist/distill-macos-x64 --help
ditto -c -k --keepParent ./dist/distill-macos-x64 ./dist/distill-macos-x64.zip
```

Build a macOS Apple Silicon binary:

```bash
python -m PyInstaller --noconfirm --clean --onefile --name distill-macos-arm64 --collect-data specforge_distill src/specforge_distill/cli.py
./dist/distill-macos-arm64 --version
./dist/distill-macos-arm64 --help
ditto -c -k --keepParent ./dist/distill-macos-arm64 ./dist/distill-macos-arm64.zip
```

Notes:

- Build the macOS Intel binary on an Intel macOS runner or machine.
- Build the macOS Apple Silicon binary on an Apple Silicon macOS runner or machine.
- The release workflow already does this split in GitHub Actions.

## Build On Windows PowerShell 7

Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the test suite:

```powershell
pytest
```

Build the Windows executable:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --name distill-windows-x64 --collect-data specforge_distill src/specforge_distill/cli.py
.\dist\distill-windows-x64.exe --version
.\dist\distill-windows-x64.exe --help
```

If the `py` launcher is unavailable, use your installed Python executable directly.

## Verify A Downloaded Binary

Use the smallest smoke test possible before handing a binary to users:

```text
<binary> --version
<binary> --help
<binary> --describe-output json
<binary> --self-test
<binary> path/to/spec.pdf --dry-run
```

Use the actual filename for the target platform, for example `./distill-linux-x64` or `.\distill-windows-x64.exe`.

For macOS release assets, unzip the downloaded archive first and then run the extracted binary.

## Docker Build

POSIX shells:

```bash
docker build -t distill .
docker run --rm -v "$(pwd):/data" distill /data/your-spec.pdf --report
```

PowerShell 7:

```powershell
docker build -t distill .
docker run --rm -v "${PWD}:/data" distill /data/your-spec.pdf --report
```

## GitHub Actions Release Flow

The release workflow is defined in `.github/workflows/release.yml`.

Behavior:

1. `workflow_dispatch` builds the platform executables and uploads them as workflow artifacts.
2. Pushing a tag that matches `v*` builds the same executables and uploads them to the GitHub Release for that tag.
3. Each built executable is smoke-tested with `--version`, `--help`, a machine-readable output-contract check, and a real fixture PDF run before upload.
4. If signing secrets are configured, Windows executables are code-signed and macOS binaries are code-signed and notarized before release upload.

## Release Signing And Notarization

The workflow supports optional signing to reduce Gatekeeper and SmartScreen friction on official releases.

macOS secrets:

- `APPLE_DEVELOPER_ID_P12_BASE64`
- `APPLE_DEVELOPER_ID_P12_PASSWORD`
- `APPLE_DEVELOPER_ID_APPLICATION`
- `APPLE_NOTARY_API_KEY_ID`
- `APPLE_NOTARY_API_ISSUER_ID`
- `APPLE_NOTARY_API_PRIVATE_KEY_BASE64`

Windows secrets:

- `WINDOWS_CERTIFICATE_PFX_BASE64`
- `WINDOWS_CERTIFICATE_PASSWORD`

Behavior:

1. If the macOS certificate secrets are present, the CLI binary is signed with `codesign`.
2. If the macOS notary secrets are also present, the zipped artifact is submitted with `notarytool`.
3. If the Windows certificate secrets are present, the `.exe` is signed with `signtool` and timestamped.

If these secrets are absent, the workflow still builds usable unsigned binaries.

Example tag flow:

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```
