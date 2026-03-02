# Build Guide

This guide is for contributors and release maintainers. End users should normally download a prebuilt binary from the [GitHub Releases](https://github.com/raymondvaldes/SpecForge-Distill/releases) page instead of building from source.

`main` is currently preparing `v1.2.0.dev0`. The latest stable release tag is `v1.1.0`.

## Release Targets

Official downloads are GitHub Releases assets only.

The release workflow produces one-file executables for:

- Ubuntu / WSL x64: `distill-v1.1.0-linux-x64`
- macOS Intel: `distill-v1.1.0-macos-x64.zip`
- macOS Apple Silicon: `distill-v1.1.0-macos-arm64.zip`
- Windows x64: `distill-v1.1.0-windows-x64.exe`

Replace `v1.1.0` with the release tag you are building or verifying.

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

Run the fast IV&V gate for small changes:

```bash
pytest -m fast_ivv
```

Use `fast_ivv` for tight edit loops on boundary handling, CLI contracts, and determinism-sensitive logic. Run the full suite before commit, release work, or any change that touches extraction, wrappers, packaging, or batch execution.

Deterministic pytest workflow:

```bash
pytest -m fast_ivv
pytest tests/phase1/test_ingest_and_quality.py
pytest
```

Execution rules:

- Use one pytest controller process at a time for a verification pass.
- If the suite needs isolation, run files or nodes sequentially with explicit timeouts and captured stdout/stderr.
- Bisect by file first, then by individual node.
- Write transient debug logs to `/tmp`, not into the repository.
- If multiple overlapping pytest runs happen, discard that evidence and rerun cleanly.

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

Run the fast IV&V gate for small changes:

```powershell
pytest -m fast_ivv
```

Deterministic pytest workflow:

```powershell
pytest -m fast_ivv
pytest tests/phase1/test_ingest_and_quality.py
pytest
```

Execution rules:

- Use one pytest controller process at a time for a verification pass.
- If the suite needs isolation, run files or nodes sequentially with explicit timeouts and captured stdout/stderr.
- Bisect by file first, then by individual node.
- Write transient debug logs to the system temp directory, not into the repository.
- If multiple overlapping pytest runs happen, discard that evidence and rerun cleanly.

Build the Windows executable:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --name distill-windows-x64 --collect-data specforge_distill src/specforge_distill/cli.py
.\dist\distill-windows-x64.exe --version
.\dist\distill-windows-x64.exe --help
```

If the `py` launcher is unavailable, use your installed Python executable directly.

## Local Development Runner

Contributor workflows can use the repository-local runners after the editable install succeeds.

POSIX shells on macOS, Ubuntu, or WSL:

```bash
./distill --help
./distill fixtures/specs/sample-digital.pdf --dry-run
```

Windows PowerShell 7:

```powershell
.\distill.ps1 --help
.\distill.ps1 .\fixtures\specs\sample-digital.pdf --dry-run
```

Behavior:

- Both runners prefer the repository virtual environment when it exists.
- Both runners fail fast with dependency guidance if the local dev environment is incomplete.
- WSL should use `./distill` with Linux paths. Windows PowerShell 7 should use `.\distill.ps1` or the release `.exe`.

## Verify A Downloaded Binary

Every downloaded binary must pass the trust sequence before first real use:

1. Download the asset and matching `.sha256` file from GitHub Releases.
2. Verify the checksum.
3. Run `--version`.
4. Run `--self-test`.
5. Only then run `--dry-run` or a real PDF command.

Ubuntu or WSL:

```bash
VERSION=v1.1.0
ASSET="distill-${VERSION}-linux-x64"
BASE_URL="https://github.com/raymondvaldes/SpecForge-Distill/releases/download/${VERSION}"

curl -LO "${BASE_URL}/${ASSET}"
curl -LO "${BASE_URL}/${ASSET}.sha256"
sha256sum --check "${ASSET}.sha256"
chmod +x "${ASSET}"
./"${ASSET}" --version
./"${ASSET}" --self-test
./"${ASSET}" path/to/spec.pdf --dry-run
```

macOS:

```bash
VERSION=v1.1.0
ASSET="distill-${VERSION}-macos-arm64.zip"
BASE_URL="https://github.com/raymondvaldes/SpecForge-Distill/releases/download/${VERSION}"

curl -LO "${BASE_URL}/${ASSET}"
curl -LO "${BASE_URL}/${ASSET}.sha256"
shasum -a 256 --check "${ASSET}.sha256"
unzip -j "${ASSET}"
BINARY="${ASSET%.zip}"
chmod +x "${BINARY}"
./"${BINARY}" --version
./"${BINARY}" --self-test
./"${BINARY}" path/to/spec.pdf --dry-run
```

Windows PowerShell 7:

```powershell
$version = "v1.1.0"
$asset = "distill-$version-windows-x64.exe"
$baseUrl = "https://github.com/raymondvaldes/SpecForge-Distill/releases/download/$version"

Invoke-WebRequest -Uri "$baseUrl/$asset" -OutFile $asset
Invoke-WebRequest -Uri "$baseUrl/$asset.sha256" -OutFile "$asset.sha256"
$expected = ((Get-Content "$asset.sha256").Trim() -split "\s+")[0].ToLower()
$actual = (Get-FileHash ".\$asset" -Algorithm SHA256).Hash.ToLower()
if ($actual -ne $expected) { throw "Checksum verification failed." }
.\$asset --version
.\$asset --self-test
.\$asset path\to\spec.pdf --dry-run
```

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

1. `prepare-release` resolves the release version and generates the build matrix from `scripts/release_manifest.py`.
2. `build` creates the platform executables, smoke-tests them with `--version`, `--help`, `--describe-output json`, `--self-test`, and a real fixture PDF, then writes per-asset `.sha256` files.
3. `collect-release-assets` gathers successful platform bundles, writes the aggregate `checksums.txt` manifest, and preserves per-platform trust status for release summaries.
4. Pushing a tag that matches `v*` publishes the collected bundle through one GitHub Release job, so failed trust validation on one platform does not block unaffected assets.

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
