#!/usr/bin/env python3
"""Shared local development runner for POSIX and PowerShell entrypoints."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


REQUIRED_MODULES = ("pydantic", "pypdf", "pdfplumber", "yaml")


def _check_dependencies() -> bool:
    for module_name in REQUIRED_MODULES:
        if importlib.util.find_spec(module_name) is None:
            return False
    return True


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "src"))

    if not _check_dependencies():
        selected_python = os.environ.get("DISTILL_SELECTED_PYTHON", sys.executable)
        print("error: missing Python dependencies for the development runner.", file=sys.stderr)
        print(f'Install them with: {selected_python} -m pip install -e ".[dev]"', file=sys.stderr)
        print(
            "Or use a standalone release binary if you do not want a Python setup.",
            file=sys.stderr,
        )
        return 1

    from specforge_distill.cli import main as cli_main

    return int(cli_main(list(argv if argv is not None else sys.argv[1:])))


if __name__ == "__main__":
    raise SystemExit(main())
