# SpecForge Distill v1.0.1

Transform digital-text specification PDFs into structured, provenance-linked Markdown and JSON.

SpecForge Distill is designed to be usable without a Python setup. For most users, the fastest path is to download a single CLI binary for your platform and run it locally.

## Download And Run

Prebuilt binaries are published on the [GitHub Releases](https://github.com/raymondvaldes/SpecForge-Distill/releases) page.

Available release assets:

- Ubuntu / WSL x64: `distill-linux-x64`
- macOS Intel: `distill-macos-x64.zip`
- macOS Apple Silicon: `distill-macos-arm64.zip`
- Windows PowerShell 7 x64: `distill-windows-x64.exe`

### Ubuntu Or WSL

```bash
curl -LO https://github.com/raymondvaldes/SpecForge-Distill/releases/latest/download/distill-linux-x64
chmod +x distill-linux-x64
./distill-linux-x64 --version
./distill-linux-x64 /path/to/spec.pdf --report
```

### macOS

Use `distill-macos-arm64.zip` on Apple Silicon and `distill-macos-x64.zip` on Intel Macs.

```bash
ASSET=distill-macos-arm64.zip
curl -LO "https://github.com/raymondvaldes/SpecForge-Distill/releases/latest/download/${ASSET}"
unzip -j "${ASSET}"
chmod +x distill-macos-arm64
./distill-macos-arm64 --version
./distill-macos-arm64 /path/to/spec.pdf --report
```

### Windows PowerShell 7

```powershell
$asset = "distill-windows-x64.exe"
Invoke-WebRequest -Uri "https://github.com/raymondvaldes/SpecForge-Distill/releases/latest/download/$asset" -OutFile "distill.exe"
.\distill.exe --version
.\distill.exe C:\path\to\spec.pdf --report
```

## What The CLI Produces

Running the CLI writes a sibling output directory named `<source>_distilled/` unless `-o` is provided.

Generated files:

- `manifest.json`: machine-readable index of requirements, artifacts, and output files
- `full.md`: consolidated Markdown view of the entire document
- `requirements.md`: extracted and normalized requirements only
- `architecture.md`: architecture and supporting narrative blocks

## Common Commands

In the examples below, replace `<binary>` with the file you downloaded, such as `./distill-linux-x64`, `./distill-macos-arm64`, or `.\distill.exe`.

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

## Limitations

- Input must be a digital-text PDF. Scanned PDFs and OCR-only image PDFs are not supported in `v1.0.1`.
- Complex diagrams are not converted into structured graphics formats.
- `v1.0.1` is focused on reliable single-document processing, not large multi-file batch orchestration.

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

## Troubleshooting

- `Permission denied` on Linux, WSL, or macOS usually means the file needs `chmod +x`.
- macOS release assets are zipped so they can be signed and notarized cleanly. If Gatekeeper still blocks a binary, verify that you downloaded an official release asset and remove the quarantine attribute only as a fallback.
- Windows may show a SmartScreen warning for an unsigned executable. Use `More info` then `Run anyway` if you trust the release source.
- If extraction produces little or no content, verify that the PDF contains a real text layer and is not a scan.
- If the output path has spaces, wrap the PDF path in quotes.

## Project Notes

- The package version is `1.0.1`.
- The manifest schema version remains `1.0.0`.
- The tool runs locally by default and does not require external AI services.
