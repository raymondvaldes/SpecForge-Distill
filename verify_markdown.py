from __future__ import annotations

import sys
from pathlib import Path


def _validate_markdown(path: Path) -> list[str]:
    errors: list[str] = []

    if not path.exists():
        return [f"{path}: file not found"]

    if path.suffix.lower() != ".md":
        errors.append(f"{path}: expected a .md file")

    text = path.read_text(encoding="utf-8")
    fence_count = sum(1 for line in text.splitlines() if line.strip().startswith("```"))
    if fence_count % 2 != 0:
        errors.append(f"{path}: unbalanced fenced code blocks")

    if not text.lstrip().startswith("#"):
        errors.append(f"{path}: expected the document to start with a markdown heading")

    return errors


def main(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    if not args:
        print("usage: python3 verify_markdown.py <file> [<file> ...]", file=sys.stderr)
        return 2

    all_errors: list[str] = []
    for file_name in args:
        file_path = Path(file_name)
        errors = _validate_markdown(file_path)
        if errors:
            all_errors.extend(errors)
            continue
        print(f"ok: {file_path}")

    if all_errors:
        for error in all_errors:
            print(error, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
