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
./distill-v1.2.1-linux-x64 --version
./distill-v1.2.1-linux-x64 --self-test
./distill-v1.2.1-linux-x64 /path/to/spec.pdf --dry-run
```

macOS:

```bash
./distill-v1.2.1-macos-arm64 --version
./distill-v1.2.1-macos-arm64 --self-test
./distill-v1.2.1-macos-arm64 /path/to/spec.pdf --dry-run
```

Windows PowerShell 7:

```powershell
.\distill-v1.2.1-windows-x64.exe --version
.\distill-v1.2.1-windows-x64.exe --self-test
.\distill-v1.2.1-windows-x64.exe C:\path\to\spec.pdf --dry-run
```

## Common Failure Modes

### Invalid Invocation

Symptoms:

- `error: missing PDF path`
- `error: --self-test cannot be combined with a PDF path or --dry-run`
- `error: --describe-output cannot be combined with PDF processing flags`

What it means:

- The command line mixed two different CLI modes together.

### Permission Denied

Symptoms:

- `Permission Denied` (when running the binary)
- `chmod: distill-v1.2.1-macos-arm64: No such file or directory`

What it means:

- On macOS and Linux, binaries must be made executable after download.
- Fix: `chmod +x distill-v1.2.1-macos-arm64`

### Corrupt Download

Symptoms:

- `distill-v1.2.1-linux-x64: FAILED` (when running sha256sum)
- `error: invalid zip file`
- `Segmentation fault` or `Execution failed` immediately after start.

What it means:

- The file was truncated or corrupted during download.
- Fix: Delete the file and download it again from the official release page.

### Resource Exhaustion

Symptoms:

- `MemoryError`
- `OSError: [Errno 12] Cannot allocate memory`
- Very slow performance on large (>500 page) specs.

What it means:

- The extraction engine needs approximately 4x the PDF file size in available RAM.
- Fix: Close other applications or use a machine with more memory.

## Resolution Workflow

If you encounter an error not listed above:

1. Copy the full error message and stack trace if available.
2. Check the [issue tracker](https://github.com/raymondvaldes/SpecForge-Distill/issues).
3. Ensure you are using the latest stable release (`v1.2.1`).
4. Run `--self-test`.
5. Then rerun a known-good `--dry-run` check before using the new binary in normal work.
