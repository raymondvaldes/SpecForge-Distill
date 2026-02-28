# Troubleshooting Guide

Official downloads are GitHub Releases assets only. If the binary or checksum file did not come from that page, discard it and start over with the official release.

Use this guide in the same order the binary install flow is supposed to run:

1. Download the correct asset and matching `.sha256` file.
2. Verify the checksum.
3. Run `--version`.
4. Run `--self-test`.
5. Only then run `--dry-run` or a real PDF command.

## Quick Verification Commands

Ubuntu or WSL:

```bash
./distill-v1.1.0-linux-x64 --version
./distill-v1.1.0-linux-x64 --self-test
./distill-v1.1.0-linux-x64 /path/to/spec.pdf --dry-run
```

macOS:

```bash
./distill-v1.1.0-macos-arm64 --version
./distill-v1.1.0-macos-arm64 --self-test
./distill-v1.1.0-macos-arm64 /path/to/spec.pdf --dry-run
```

Windows PowerShell 7:

```powershell
.\distill-v1.1.0-windows-x64.exe --version
.\distill-v1.1.0-windows-x64.exe --self-test
.\distill-v1.1.0-windows-x64.exe C:\path\to\spec.pdf --dry-run
```

## Failure Class: Invalid Invocation

Symptoms:

- `error: missing PDF path`
- `error: --self-test cannot be combined with a PDF path or --dry-run`
- `error: --describe-output cannot be combined with PDF processing flags`

What it means:

- The command line mixed two different CLI modes together.

Recovery:

1. Decide whether you are running a normal PDF command, `--describe-output json`, `--emit-example-output`, or `--self-test`.
2. Remove the flags that belong to the other modes.
3. Retry the simplest successful form first, such as `distill --self-test` or `distill path/to/spec.pdf --dry-run`.

## Failure Class: Missing Input File

Symptoms:

- `error: file not found: ...`

What it means:

- The PDF path does not exist where the command expects it.

Recovery:

1. Confirm the file path before retrying.
2. On WSL, use Linux paths with the Linux binary.
3. On PowerShell, prefer an explicit path like `C:\work\spec.pdf`.

## Failure Class: Checksum Mismatch

Symptoms:

- `sha256sum --check` fails.
- `shasum -a 256 --check` fails.
- Your computed hash does not match the `.sha256` file.

What it means:

- The file is incomplete, corrupted, or not the same binary that the official release published.

Recovery:

1. Do not run the binary.
2. Delete the downloaded file and checksum file.
3. Download both files again from the official GitHub Release.
4. Retry checksum verification before any `--version` or `--self-test` command.

Ubuntu or WSL:

```bash
sha256sum --check distill-v1.1.0-linux-x64.sha256
```

macOS:

```bash
shasum -a 256 --check distill-v1.1.0-macos-arm64.zip.sha256
```

Windows PowerShell 7:

```powershell
$expected = ((Get-Content ".\distill-v1.1.0-windows-x64.exe.sha256").Trim() -split "\s+")[0].ToLower()
$actual = (Get-FileHash ".\distill-v1.1.0-windows-x64.exe" -Algorithm SHA256).Hash.ToLower()
if ($actual -ne $expected) { throw "Checksum verification failed." }
```

## Failure Class: Wrong Asset Or Platform Trust Prompt

Symptoms:

- `cannot execute binary file`
- `Exec format error`
- `bad CPU type in executable`
- macOS Gatekeeper blocks launch
- Windows SmartScreen warns before first run

What it means:

- You may have downloaded the wrong asset for the machine, or the platform is asking you to confirm the trust path after download.

Recovery:

1. Verify you chose the correct asset first.
2. Verify the checksum second.
3. Only after both pass should you respond to Gatekeeper or SmartScreen prompts.

Correct assets:

- Ubuntu / WSL x64: `distill-v1.1.0-linux-x64`
- macOS Intel: `distill-v1.1.0-macos-x64.zip`
- macOS Apple Silicon: `distill-v1.1.0-macos-arm64.zip`
- Windows PowerShell 7 x64: `distill-v1.1.0-windows-x64.exe`

macOS Gatekeeper:

1. Confirm the zip came from GitHub Releases.
2. Confirm the zip checksum matches.
3. Unzip the correct Intel or Apple Silicon build.
4. Retry `./distill-v1.1.0-macos-arm64 --version`.
5. If Gatekeeper still blocks a checksum-verified file that you trust, remove the quarantine attribute:

```bash
xattr -d com.apple.quarantine ./distill-v1.1.0-macos-arm64
```

Windows SmartScreen:

1. Confirm the `.exe` came from GitHub Releases.
2. Confirm its SHA256 checksum matches.
3. Run `.\distill-v1.1.0-windows-x64.exe --version`.
4. If SmartScreen still warns on the verified binary, use `More info` only after the checksum succeeds.
5. If Windows keeps the file blocked, remove the download marker:

```powershell
Unblock-File .\distill-v1.1.0-windows-x64.exe
```

## Failure Class: Self-Test Validation Failure

Symptoms:

- `distill --self-test` exits with code `4`
- stderr is JSON with `failure_class: "self_test_validation_failure"`

What it means:

- The installation or runtime environment cannot complete the deterministic output-package verification path.

The CLI returns a stable JSON payload on stderr:

```json
{
  "status": "failed",
  "mode": "self-test",
  "failure_class": "self_test_validation_failure",
  "recovery_hint": "Do not process a real PDF until distill --self-test passes cleanly on the downloaded binary.",
  "troubleshooting": {
    "guide": "docs/TROUBLESHOOTING.md",
    "anchor": "#failure-class-self-test-validation-failure"
  }
}
```

Recovery:

1. Stop before processing a real PDF.
2. Rerun the binary from a writable directory.
3. Redownload the asset and checksum from GitHub Releases if you have any doubt about the binary.
4. If the failure persists on the release binary, try a clean local source install to determine whether the issue is machine-specific.

Platform notes:

- Ubuntu / WSL: confirm the file is executable with `chmod +x`.
- macOS: confirm you unzipped the correct Intel or Apple Silicon asset before running `--self-test`.
- Windows: run the `.exe` directly from PowerShell 7 and keep the current directory writable.

## Failure Class: PDF Processing Failure

Symptoms:

- `error: Failed to process PDF.`
- `--self-test` passes, but a real PDF command fails.
- Output is empty or obviously incomplete.

What it means:

- The PDF is malformed, encrypted, image-only, or otherwise unsupported by the extractor.

Recovery:

1. Retry with `--dry-run` first.
2. Confirm the PDF has selectable text.
3. Retry with a known-good digital-text PDF to separate the input problem from the installation problem.
4. If only one PDF fails, treat that input as unsupported or damaged rather than trusting the binary less.

## Failure Class: Source Environment Drift

Symptoms:

- Contributor install works once and later breaks after dependency or packaging changes.
- Wrapper scripts complain about missing Python dependencies.

What it means:

- The local development environment drifted away from the repo's expected dependency set.

Recovery:

Ubuntu, WSL, or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m specforge_distill.cli --version
./distill --help
```

Windows PowerShell 7:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m specforge_distill.cli --version
.\distill.ps1 --help
```

Notes:

- Use `./distill` inside WSL or other POSIX shells.
- Use `.\distill.ps1` from Windows PowerShell 7 for the repository-local development runner.
- Use the release `.exe` only for the downloaded binary workflow, not for editable source development.

## Upgrade Path

Upgrade by repeating the same trust sequence:

1. Download the new platform asset from GitHub Releases.
2. Verify the checksum.
3. Run `--version`.
4. Run `--self-test`.
5. Then rerun a known-good `--dry-run` check before using the new binary in normal work.
