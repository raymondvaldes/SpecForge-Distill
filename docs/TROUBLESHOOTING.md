# Troubleshooting Guide

This guide is for end users running the published CLI binaries and for contributors running the project locally from source.

If you only need the shortest possible sanity check, start here:

## Quick Checks

1. Confirm you downloaded the correct asset for your platform.
2. Run `--version`.
3. Run `--help`.
4. Run `--self-test`.
5. Run `--dry-run` against a known digital-text PDF.
6. Verify the input PDF actually has a selectable text layer.

Examples:

Ubuntu or WSL:

```bash
./distill-linux-x64 --version
./distill-linux-x64 --help
./distill-linux-x64 --self-test
./distill-linux-x64 /path/to/spec.pdf --dry-run
```

macOS:

```bash
./distill-macos-arm64 --version
./distill-macos-arm64 --help
./distill-macos-arm64 --self-test
./distill-macos-arm64 /path/to/spec.pdf --dry-run
```

Windows PowerShell 7:

```powershell
.\distill.exe --version
.\distill.exe --help
.\distill.exe --self-test
.\distill.exe C:\path\to\spec.pdf --dry-run
```

## Pick The Right Download

Latest stable release assets:

- Ubuntu or WSL x64: `distill-linux-x64`
- macOS Intel: `distill-macos-x64.zip`
- macOS Apple Silicon: `distill-macos-arm64.zip`
- Windows PowerShell 7 x64: `distill-windows-x64.exe`

Common symptoms of the wrong asset:

- `cannot execute binary file`
- `Exec format error`
- `bad CPU type in executable`
- the binary exits immediately without doing useful work

If that happens, confirm both your OS and CPU architecture before retrying the download.

## Verify The Download Before Running It

Each release asset includes a matching `.sha256` file.

Ubuntu, WSL, or most Linux systems:

```bash
sha256sum distill-linux-x64
cat distill-linux-x64.sha256
```

macOS:

```bash
shasum -a 256 distill-macos-arm64.zip
cat distill-macos-arm64.zip.sha256
```

Windows PowerShell 7:

```powershell
Get-FileHash .\distill.exe -Algorithm SHA256
Get-Content .\distill-windows-x64.exe.sha256
```

The computed hash should match the value in the checksum file.

## Upgrade Path

For most binary users, upgrading should be a replace-and-verify workflow rather than an in-place install.

### Upgrading From One Binary Release To Another

1. Check the version you are currently running.
2. Download the new asset for the same platform and CPU.
3. Verify its checksum.
4. Replace the old binary with the new one.
5. Rerun `--version`, `--help`, and a small `--dry-run` check.

Ubuntu, WSL, or macOS:

```bash
./distill-linux-x64 --version
mv distill-linux-x64 distill-linux-x64.old
curl -LO https://github.com/raymondvaldes/SpecForge-Distill/releases/latest/download/distill-linux-x64
chmod +x distill-linux-x64
./distill-linux-x64 --version
./distill-linux-x64 /path/to/spec.pdf --dry-run
```

Windows PowerShell 7:

```powershell
.\distill.exe --version
Move-Item .\distill.exe .\distill-old.exe
Invoke-WebRequest -Uri "https://github.com/raymondvaldes/SpecForge-Distill/releases/latest/download/distill-windows-x64.exe" -OutFile "distill.exe"
.\distill.exe --version
.\distill.exe C:\path\to\spec.pdf --dry-run
```

### Upgrading macOS Release Assets

Because macOS assets are distributed as zip files:

1. Download the correct Intel or Apple Silicon zip.
2. Verify the zip checksum.
3. Unzip the new binary.
4. Replace the old executable.
5. Rerun `--version`.

If Gatekeeper re-prompts after an upgrade, treat it as a new binary and repeat the same verification checks you used for the previous release.

### Upgrading If You Script Against Outputs

Before upgrading a production script or automation:

1. Read the current draft or final release notes.
2. Check whether CLI flags changed.
3. Check whether output file names changed.
4. Check whether `manifest.json` fields or semantics changed.
5. Run the new binary on a known-good fixture and compare outputs before rolling it into automation.

### Upgrading From Source Install To Binary Use

If you previously ran the project from a Python environment and want the simpler binary path:

1. Download the correct release asset.
2. Verify the checksum.
3. Run the binary directly instead of the local wrapper or `python -m ...`.
4. Keep the source checkout only if you still need development workflows.

This is usually the simplest path for non-developer users.

### Upgrading A Source Checkout

If you are staying on source instead of moving to the release binary:

Ubuntu, WSL, or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m specforge_distill.cli --version
```

Windows PowerShell 7:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m specforge_distill.cli --version
```

If an upgrade changes packaging or dependencies, rebuilding the local virtual environment is often faster than debugging a stale one.

## Binary Will Not Start

### Linux, WSL, Or macOS: `Permission denied`

Mark the file executable:

```bash
chmod +x ./distill-linux-x64
```

or:

```bash
chmod +x ./distill-macos-arm64
```

Then rerun:

```bash
./distill-linux-x64 --version
```

### macOS: `bad CPU type in executable`

You downloaded the wrong macOS build.

Use:

- `distill-macos-arm64.zip` for Apple Silicon
- `distill-macos-x64.zip` for Intel Macs

### macOS: Gatekeeper Blocks The Binary

Official macOS release assets are zipped because the release flow can sign and notarize them cleanly. If macOS still blocks the file:

1. Confirm you downloaded it from the official GitHub release page.
2. Confirm you unzipped the correct asset for your CPU.
3. Retry from Terminal:

```bash
./distill-macos-arm64 --version
```

If Gatekeeper still blocks it and you trust the source, remove the quarantine attribute as a fallback:

```bash
xattr -d com.apple.quarantine ./distill-macos-arm64
```

Then rerun the version check.

### Windows: SmartScreen Warning

If Windows shows a SmartScreen warning:

1. Confirm the file came from the official GitHub release page.
2. Compare its SHA256 hash with the published checksum.
3. Use `More info` and then `Run anyway` only if the file matches the official release.

You can also remove the download block marker in PowerShell:

```powershell
Unblock-File .\distill.exe
```

### Windows: PowerShell Says Scripts Or Files Cannot Run

The release binary is an `.exe`, not a PowerShell script, so you should run it directly:

```powershell
.\distill.exe --version
```

If the current directory is not being searched automatically, always prefix with `.\`.

### WSL: Windows Path Confusion

If you are inside WSL, use Linux-style paths when invoking the Linux binary.

Good:

```bash
./distill-linux-x64 /mnt/c/Users/you/Documents/spec.pdf --report
```

Bad:

```text
./distill-linux-x64 C:\Users\you\Documents\spec.pdf --report
```

## Binary Starts But The PDF Fails

### `error: file not found`

The path is wrong from the current working directory, or it contains spaces and is not quoted.

Ubuntu, WSL, or macOS:

```bash
./distill-linux-x64 "/path/with spaces/spec.pdf" --report
```

Windows PowerShell 7:

```powershell
.\distill.exe "C:\path with spaces\spec.pdf" --report
```

### `error: Failed to process PDF`

This usually means one of these:

- the PDF is malformed or truncated
- the PDF is encrypted or restricted
- the file is not actually a valid PDF
- the PDF parser hit structure it could not recover from

Try these checks:

1. Open the file in a normal PDF viewer first.
2. Confirm it really ends in `.pdf` because it is a PDF, not because it was renamed.
3. Retry with `--dry-run` first to avoid mixing parser failure with output-writing issues.
4. Try a known-good digital-text PDF to confirm the binary itself is healthy.

### Output Is Empty Or Nearly Empty

The most common cause is that the input is a scan or image-only PDF.

Quick test:

1. Open the PDF in a viewer.
2. Try to select and copy a sentence.
3. Paste it into a text editor.

If copy/paste does not work, the PDF probably does not contain a real text layer. The stable release is optimized for digital-text PDFs, not OCR-only scans.

### Low Text-Layer Warning

If the CLI warns about low text-layer quality on some pages, it detected too little extractable text on those pages. That does not always mean total failure, but it does mean:

- some pages may be image-only
- the PDF may mix real text with scanned pages
- tables or captions may be incomplete

Use `--dry-run` first to see warnings without writing full output:

Ubuntu, WSL, or macOS:

```bash
./distill-linux-x64 /path/to/spec.pdf --dry-run
```

Windows PowerShell 7:

```powershell
.\distill.exe C:\path\to\spec.pdf --dry-run
```

### Requirements Or Architecture Content Looks Incomplete

Check these conditions before treating it as a product bug:

1. The PDF is digital text, not a scan.
2. The document language uses recognizable obligation words such as `shall`, `must`, or `required`.
3. The PDF is not a heavily graphical export with most content flattened into images.
4. The requirement text is not only embedded inside unusual diagrams or unsupported visual layouts.

If the problem is repeatable on a digital-text PDF, save the failing input and compare the generated `requirements.md`, `architecture.md`, and `manifest.json`.

## Output Directory Problems

### I Cannot Find The Output

By default the CLI writes next to the source PDF and uses this naming pattern:

```text
<source-stem>_distilled/
```

Example:

```text
system_spec.pdf
system_spec_distilled/
```

If you used `-o`, output goes exactly where you told it to go.

### Output Path Contains Spaces

Quote the path.

Ubuntu, WSL, or macOS:

```bash
./distill-linux-x64 "/path/to/spec.pdf" -o "/path/to/output folder" --report
```

Windows PowerShell 7:

```powershell
.\distill.exe "C:\path\to\spec.pdf" -o "C:\path\to\output folder" --report
```

### Permission Denied While Writing Output

You may be trying to write into a protected location.

Try one of these:

- run in your home directory or Documents folder
- choose a writable `-o` path explicitly
- avoid system directories such as `/usr`, `/System`, or protected Windows folders

## Docker Troubleshooting

### Docker Build Works But The Container Cannot See My PDF

The problem is usually the bind mount path.

POSIX shells:

```bash
docker run --rm -v "$(pwd):/data" distill /data/your-spec.pdf --report
```

PowerShell 7:

```powershell
docker run --rm -v "${PWD}:/data" distill /data/your-spec.pdf --report
```

Make sure the PDF path you pass to the container matches the mounted container path, not your host path.

### Docker Runs But The Output Is Not On My Host

Write output somewhere inside the mounted directory:

```bash
docker run --rm -v "$(pwd):/data" distill /data/your-spec.pdf -o /data/output --report
```

## Source Build Troubleshooting

If you are building from source instead of using a release binary, also see [BUILD.md](BUILD.md).

### `pytest` Or `pyinstaller` Is Missing

Install the dev dependencies:

Ubuntu, WSL, or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Windows PowerShell 7:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### The Wrong Python Environment Is Being Used

Check which Python is active.

Ubuntu, WSL, or macOS:

```bash
which python
python --version
```

Windows PowerShell 7:

```powershell
Get-Command python
python --version
```

The project expects the local virtual environment when working from source.

### The Local `distill` Wrapper Fails

The root `distill` script is a development convenience wrapper. It is not the official end-user install path.

If it fails locally:

1. Create the repo virtual environment.
2. Install the dev dependencies.
3. Retry with the module form if needed:

Ubuntu, WSL, or macOS:

```bash
PYTHONPATH=src .venv/bin/python -m specforge_distill.cli --help
```

Windows PowerShell 7:

```powershell
python -m specforge_distill.cli --help
```

## Platform-Specific Notes

### Ubuntu And Native Linux

- Mark the binary executable with `chmod +x`.
- Prefer a local directory you control for both the binary and the output.
- If the binary came from a network share, copy it locally first before troubleshooting execution.

### WSL

- Use the Linux binary, not the Windows `.exe`, unless you intentionally want to run the Windows build from Windows itself.
- Prefer `/mnt/c/...` paths when targeting Windows-hosted files from WSL.
- Quote paths with spaces.

### macOS

- Choose the correct Intel vs Apple Silicon asset.
- Unzip the release archive before running the binary.
- If blocked, verify download source and checksum before using `xattr -d com.apple.quarantine`.

### Windows PowerShell 7

- Use `.\distill.exe`, not just `distill.exe`, when running from the current directory.
- Use `Get-FileHash` to compare with the published `.sha256` file.
- If downloaded from a browser, `Unblock-File` can help after you verify the file is official.

## Before Reporting A Bug Or Upgrade Regression

Collect this first:

1. Platform and version, for example Ubuntu 22.04, macOS 15 Intel, or Windows 11 PowerShell 7.
2. Exact binary name you downloaded.
3. Exact command you ran.
4. Whether `--version` and `--help` work.
5. Whether `--dry-run` works on the failing PDF.
6. Whether the PDF is digital text or a scan.
7. The exact error message.
8. If this was an upgrade, the last version that worked and what changed during the upgrade.

That usually separates:

- bad download
- wrong platform asset
- filesystem/permission problem
- malformed PDF
- scan/OCR limitation
- upgrade-path regression
- actual product bug
