from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from release_manifest import build_release_manifest, normalize_version


PROJECT_ROOT = SCRIPT_DIR.parent


def _draft_path_for_version(version: str) -> Path:
    normalized = normalize_version(version)
    return PROJECT_ROOT / "docs" / f"RELEASE_NOTES_{normalized}.md"


def _load_status_map(status_dir: Path | None) -> dict[str, dict[str, object]]:
    if status_dir is None or not status_dir.exists():
        return {}

    status_map: dict[str, dict[str, object]] = {}
    for status_file in sorted(status_dir.glob("*.json")):
        payload = json.loads(status_file.read_text(encoding="utf-8"))
        status_map[str(payload["release_name"])] = payload
    return status_map


def _status_label(payload: dict[str, object]) -> str:
    if not payload["publishable"]:
        return f"Held back: {payload['status_message']}"

    trust_state = str(payload["trust_state"])
    if trust_state == "notarized":
        return "Notarized"
    if trust_state == "signed":
        return "Signed"
    return "Unsigned"


def _load_curated_sections(draft_path: Path) -> str:
    draft_text = draft_path.read_text(encoding="utf-8").strip()
    marker = "## Highlights"
    if marker not in draft_text:
        return draft_text
    return draft_text[draft_text.index(marker) :].strip()


def render_release_body(version: str, *, draft_path: Path | None = None, status_dir: Path | None = None) -> str:
    normalized = normalize_version(version)
    manifest = build_release_manifest(normalized)
    statuses = _load_status_map(status_dir)
    draft = _load_curated_sections(draft_path or _draft_path_for_version(normalized))

    matrix_lines = [
        "| Platform | CPU | Asset | Status |",
        "|----------|-----|-------|--------|",
    ]
    held_back_lines: list[str] = []

    for asset in manifest:
        status = statuses.get(
            asset["release_name"],
            {
                "release_name": asset["release_name"],
                "publishable": True,
                "trust_state": "unsigned",
                "status_message": "Publishable release asset.",
            },
        )
        matrix_lines.append(
            f"| {asset['platform_label']} | {asset['arch_label']} | `{asset['release_name']}` | {_status_label(status)} |"
        )
        if not bool(status["publishable"]):
            held_back_lines.append(f"- `{asset['release_name']}` — {status['status_message']}")

    sections = [
        f"# SpecForge Distill {normalized}",
        "",
        "Official downloads are GitHub Releases assets only.",
        "",
        "## Asset Selection Matrix",
        "",
        *matrix_lines,
        "",
        "## Verify Before First Real Use",
        "",
        "1. Download the platform asset from GitHub Releases.",
        "2. Verify the matching `.sha256` file or the aggregate `checksums.txt` manifest.",
        "3. Run `--version`.",
        "4. Run `--self-test`.",
        "5. Only then process a real PDF.",
        "",
    ]

    if held_back_lines:
        sections.extend(
            [
                "## Held-Back Platforms",
                "",
                *held_back_lines,
                "",
            ]
        )

    sections.extend(
        [
            "## Curated Release Notes",
            "",
            draft,
            "",
        ]
    )

    return "\n".join(sections).strip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a trust-first GitHub release body.")
    parser.add_argument("--version", required=True, help="Release tag, for example v1.1.0.")
    parser.add_argument("--draft", type=Path, default=None, help="Override the curated release-notes draft path.")
    parser.add_argument("--status-dir", type=Path, default=None, help="Optional directory of per-platform release status JSON files.")
    parser.add_argument("--output", type=Path, default=None, help="Write the rendered body to this path instead of stdout.")
    parser.add_argument("--check", action="store_true", help="Validate that the rendered body includes trust-first markers.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    body = render_release_body(args.version, draft_path=args.draft, status_dir=args.status_dir)

    if args.check:
        required_markers = [
            "Official downloads are GitHub Releases assets only.",
            "## Asset Selection Matrix",
            "checksums.txt",
            "--version",
            "--self-test",
            "## Curated Release Notes",
        ]
        for marker in required_markers:
            if marker not in body:
                raise ValueError(f"Rendered release body is missing required marker: {marker}")
        print(f"ok: release body for {normalize_version(args.version)}")
        return 0

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8")
        print(str(args.output))
        return 0

    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
