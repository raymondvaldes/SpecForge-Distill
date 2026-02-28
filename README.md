# SpecForge Distill

`main` is preparing `v1.1.0`. The latest stable release is `v1.0.1`.

Transform digital-text specification PDFs into structured, provenance-linked Markdown and JSON.

SpecForge Distill is designed to be usable without a Python setup. For most users, the fastest path is to download a single CLI binary for your platform and run it locally.

## Trusted Download And Run

Official downloads are GitHub Releases assets only. If a binary, checksum file, or copied mirror did not come from that page, discard it and start again from the official release.

The examples below use the current `v1.1.0` asset contract. Replace `v1.1.0` with the release tag you are installing.

Available release assets:

- Ubuntu / WSL x64: `distill-v1.1.0-linux-x64`
- macOS Intel: `distill-v1.1.0-macos-x64.zip`
- macOS Apple Silicon: `distill-v1.1.0-macos-arm64.zip`
- Windows PowerShell 7 x64: `distill-v1.1.0-windows-x64.exe`

Each release also publishes per-asset `.sha256` files and one aggregate `checksums.txt` manifest.

Every binary install path must follow the same trust sequence:

1. Download the asset and matching checksum from GitHub Releases.
2. Verify the checksum before first execution.
3. Run `--version`.
4. Run `--self-test`.
5. Only then run against a real PDF.

### Ubuntu Or WSL

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
./"${ASSET}" /path/to/spec.pdf --report
```

### macOS

Use `distill-v1.1.0-macos-arm64.zip` on Apple Silicon and `distill-v1.1.0-macos-x64.zip` on Intel Macs.

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
./"${BINARY}" /path/to/spec.pdf --report
```

### Windows PowerShell 7

```powershell
$version = "v1.1.0"
$asset = "distill-$version-windows-x64.exe"
$baseUrl = "https://github.com/raymondvaldes/SpecForge-Distill/releases/download/$version"

Invoke-WebRequest -Uri "$baseUrl/$asset" -OutFile $asset
Invoke-WebRequest -Uri "$baseUrl/$asset.sha256" -OutFile "$asset.sha256"
$expected = ((Get-Content "$asset.sha256").Trim() -split "\s+")[0].ToLower()
$actual = (Get-FileHash ".\$asset" -Algorithm SHA256).Hash.ToLower()
if ($actual -ne $expected) { throw "Checksum verification failed. See docs/TROUBLESHOOTING.md#failure-class-checksum-mismatch" }
.\$asset --version
.\$asset --self-test
.\$asset C:\path\to\spec.pdf --report
```

## What The CLI Produces

Running the CLI writes a sibling output directory named `<source>_distilled/` unless `-o` is provided.

Generated files:

- `manifest.json`: machine-readable index of requirements, artifacts, and output files
- `full.md`: consolidated Markdown view of the entire document
- `requirements.md`: extracted and normalized requirements only
- `architecture.md`: architecture and supporting narrative blocks

## Common Commands

In the examples below, replace `<binary>` with the verified file you downloaded, such as `./distill-v1.1.0-linux-x64`, `./distill-v1.1.0-macos-arm64`, or `.\distill-v1.1.0-windows-x64.exe`.

Show help:

```text
<binary> --help
```

Dry run without writing output:

```text
<binary> path/to/spec.pdf --dry-run
```

Write output to a specific directory:

```text
<binary> path/to/spec.pdf -o path/to/output --report
```

## Automation And AI Use

The CLI exposes deterministic machine-oriented modes so tools can inspect or verify the contract without guessing:

Describe the output contract:

```text
<binary> --describe-output json
```

Emit a canonical example package:

```text
<binary> --emit-example-output path/to/example-output
```

Run a built-in self-test:

```text
<binary> --self-test
```

Use these modes when integrating the repo or binary with AI agents, CI checks, wrappers, or other automation that needs to understand the output format before processing real PDFs. The `--describe-output json` contract includes generated-file schemas, CLI flag applicability, invocation modes, and failure classes so tools do not have to infer behavior from help text.

## Limitations

- Input must be a digital-text PDF. Scanned PDFs and OCR-only image PDFs are not supported in the latest stable release (`v1.0.1`).
- Complex diagrams are not converted into structured graphics formats.
- The latest stable release focuses on reliable single-document processing, not large multi-file batch orchestration.

## Docker

If you prefer a containerized run instead of a local binary:

```bash
docker build -t distill .
docker run --rm -v "$(pwd):/data" distill /data/your-spec.pdf --report
```

PowerShell 7:

```powershell
docker build -t distill .
docker run --rm -v "${PWD}:/data" distill /data/your-spec.pdf --report
```

## Build From Source

End users should prefer the release binaries above. Contributor and packaging instructions live in [docs/BUILD.md](docs/BUILD.md).

## Local Development Runner

For contributor workflows inside this repository, use the checked-in development runners instead of a release binary:

- POSIX shells on macOS, Ubuntu, or WSL: `./distill`
- Windows PowerShell 7: `.\distill.ps1`

Examples:

```bash
./distill --help
./distill fixtures/specs/sample-digital.pdf --dry-run
```

```powershell
.\distill.ps1 --help
.\distill.ps1 .\fixtures\specs\sample-digital.pdf --dry-run
```

WSL note: use Linux paths with `./distill` inside WSL. Use the Windows release `.exe` only from Windows PowerShell 7, not from the WSL shell.

For the repository's test integration Verification and Validation vision, see [docs/TEST_IVV_VISION.md](docs/TEST_IVV_VISION.md). The detailed test-to-requirement mapping lives in [docs/TEST_SPEC.md](docs/TEST_SPEC.md).

## Troubleshooting

See the dedicated [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for:

- checksum mismatch recovery and wrong-asset diagnosis
- failure-class-first guidance for `--self-test`, PDF processing, and CLI invocation issues
- Gatekeeper, SmartScreen, WSL, Ubuntu, macOS, and PowerShell 7 recovery after verification succeeds
- Docker troubleshooting, local build recovery, and upgrade-path guidance

## Project Notes

- The `main` branch package version is `1.1.0.dev0`.
- The latest stable release is `1.0.1`.
- The manifest schema version remains `1.0.0`.
- The tool runs locally by default and does not require external AI services.
- The in-progress maintainer release-note draft lives in [docs/RELEASE_NOTES_v1.1.0.md](docs/RELEASE_NOTES_v1.1.0.md).
