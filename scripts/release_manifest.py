from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


VERSION_PATTERN = re.compile(r"^v[0-9][0-9A-Za-z.+-]*$")


@dataclass(frozen=True)
class ReleaseAsset:
    os: str
    platform: str
    platform_label: str
    arch: str
    arch_label: str
    binary_name: str
    release_name: str
    upload_path: str
    artifact_name: str
    status_artifact_name: str


def normalize_version(version: str) -> str:
    normalized = version if version.startswith("v") else f"v{version}"
    if not VERSION_PATTERN.match(normalized):
        raise ValueError(f"Unsupported release version: {version}")
    return normalized


def build_release_manifest(version: str) -> list[dict[str, str]]:
    normalized = normalize_version(version)
    release_stem = {
        ("linux", "x64"): f"distill-{normalized}-linux-x64",
        ("macos", "x64"): f"distill-{normalized}-macos-x64",
        ("macos", "arm64"): f"distill-{normalized}-macos-arm64",
        ("windows", "x64"): f"distill-{normalized}-windows-x64",
    }

    assets = [
        ReleaseAsset(
            os="ubuntu-22.04",
            platform="linux",
            platform_label="Ubuntu / WSL",
            arch="x64",
            arch_label="x64",
            binary_name="distill-linux-x64",
            release_name=release_stem[("linux", "x64")],
            upload_path=f"dist/{release_stem[('linux', 'x64')]}",
            artifact_name="release-bundle-linux-x64",
            status_artifact_name="release-status-linux-x64",
        ),
        ReleaseAsset(
            os="macos-15-intel",
            platform="macos",
            platform_label="macOS",
            arch="x64",
            arch_label="Intel",
            binary_name="distill-macos-x64",
            release_name=f"{release_stem[('macos', 'x64')]}.zip",
            upload_path=f"dist/{release_stem[('macos', 'x64')]}.zip",
            artifact_name="release-bundle-macos-x64",
            status_artifact_name="release-status-macos-x64",
        ),
        ReleaseAsset(
            os="macos-14",
            platform="macos",
            platform_label="macOS",
            arch="arm64",
            arch_label="Apple Silicon",
            binary_name="distill-macos-arm64",
            release_name=f"{release_stem[('macos', 'arm64')]}.zip",
            upload_path=f"dist/{release_stem[('macos', 'arm64')]}.zip",
            artifact_name="release-bundle-macos-arm64",
            status_artifact_name="release-status-macos-arm64",
        ),
        ReleaseAsset(
            os="windows-2022",
            platform="windows",
            platform_label="Windows PowerShell 7",
            arch="x64",
            arch_label="x64",
            binary_name="distill-windows-x64.exe",
            release_name=f"{release_stem[('windows', 'x64')]}.exe",
            upload_path=f"dist/{release_stem[('windows', 'x64')]}.exe",
            artifact_name="release-bundle-windows-x64",
            status_artifact_name="release-status-windows-x64",
        ),
    ]
    return [asdict(asset) for asset in assets]


def validate_release_manifest(version: str) -> list[dict[str, str]]:
    manifest = build_release_manifest(version)
    normalized = normalize_version(version)

    for asset in manifest:
        expected_prefix = f"distill-{normalized}-{asset['platform']}-{asset['arch']}"
        if not asset["release_name"].startswith(expected_prefix):
            raise ValueError(f"Unexpected release name: {asset['release_name']}")
        if Path(asset["upload_path"]).name != asset["release_name"]:
            raise ValueError(f"Upload path does not end with release name: {asset['upload_path']}")
        if asset["platform"] == "linux" and asset["release_name"].endswith((".zip", ".exe")):
            raise ValueError(f"Linux release asset should be a raw executable: {asset['release_name']}")
        if asset["platform"] == "macos" and not asset["release_name"].endswith(".zip"):
            raise ValueError(f"macOS release asset should be zipped: {asset['release_name']}")
        if asset["platform"] == "windows" and not asset["release_name"].endswith(".exe"):
            raise ValueError(f"Windows release asset should be an .exe: {asset['release_name']}")

    return manifest


def write_checksums_manifest(version: str, release_dir: Path) -> Path:
    manifest = validate_release_manifest(version)
    lines: list[str] = []

    for asset in manifest:
        checksum_path = release_dir / f"{asset['release_name']}.sha256"
        if not checksum_path.exists():
            continue

        entries = [line.strip() for line in checksum_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(entries) != 1:
            raise ValueError(f"Expected exactly one checksum entry in {checksum_path}")

        checksum, separator, file_name = entries[0].partition("  ")
        if not separator or not checksum or file_name != asset["release_name"]:
            raise ValueError(f"Malformed checksum entry in {checksum_path}: {entries[0]}")

        asset_path = release_dir / asset["release_name"]
        if not asset_path.exists():
            raise ValueError(f"Checksum exists without release asset: {asset_path}")

        lines.append(f"{checksum}  {file_name}")

    if not lines:
        raise ValueError(f"No checksum files found in {release_dir}")

    output_path = release_dir / "checksums.txt"
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the SpecForge Distill release asset contract.",
    )
    parser.add_argument("--version", required=True, help="Release tag or version, for example v1.1.0.")
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--matrix-json", action="store_true", help="Print release matrix JSON.")
    actions.add_argument("--check", action="store_true", help="Validate the release naming contract.")
    actions.add_argument(
        "--write-checksums-manifest",
        metavar="DIR",
        help="Write an aggregate checksums.txt manifest for release assets in DIR.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.matrix_json:
        print(json.dumps(build_release_manifest(args.version), separators=(",", ":")))
        return 0

    if args.check:
        manifest = validate_release_manifest(args.version)
        print(json.dumps({"version": normalize_version(args.version), "asset_count": len(manifest)}, indent=2))
        return 0

    output_path = write_checksums_manifest(args.version, Path(args.write_checksums_manifest))
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
