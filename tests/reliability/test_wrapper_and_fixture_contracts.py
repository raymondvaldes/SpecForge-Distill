from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import textwrap
from pathlib import Path

from specforge_distill.pipeline import run_distill_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _write_executable(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _create_wrapper_test_repo(tmp_path: Path, *, include_minimal_cli: bool) -> Path:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    distill_script = PROJECT_ROOT / "distill"
    target_script = repo_root / "distill"
    target_script.write_text(distill_script.read_text(encoding="utf-8"), encoding="utf-8")
    target_script.chmod(distill_script.stat().st_mode | stat.S_IXUSR)

    if include_minimal_cli:
        package_dir = repo_root / "src" / "specforge_distill"
        package_dir.mkdir(parents=True)
        (package_dir / "__init__.py").write_text("", encoding="utf-8")
        (package_dir / "cli.py").write_text(
            textwrap.dedent(
                """
                import json
                import os
                import sys

                if __name__ == "__main__":
                    print(
                        json.dumps(
                            {
                                "selected_python": os.environ.get("DISTILL_SELECTED_PYTHON"),
                                "argv": sys.argv[1:],
                            }
                        )
                    )
                """
            ),
            encoding="utf-8",
        )

    return repo_root


def test_distill_wrapper_prefers_repo_venv(tmp_path: Path) -> None:
    repo_root = _create_wrapper_test_repo(tmp_path, include_minimal_cli=True)
    real_python = Path(sys.executable)

    _write_executable(
        repo_root / ".venv" / "bin" / "python",
        f"""#!/bin/sh
        export DISTILL_SELECTED_PYTHON=venv
        exec "{real_python}" "$@"
        """,
    )
    _write_executable(
        repo_root / "fake-bin" / "python3",
        """#!/bin/sh
        exit 99
        """,
    )

    env = dict(os.environ)
    env["PATH"] = f"{repo_root / 'fake-bin'}:{env['PATH']}"

    result = subprocess.run(
        [str(repo_root / "distill"), "sample.pdf"],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["selected_python"] == "venv"
    assert payload["argv"] == ["sample.pdf"]


def test_distill_wrapper_fails_cleanly_when_dependencies_are_missing(tmp_path: Path) -> None:
    repo_root = _create_wrapper_test_repo(tmp_path, include_minimal_cli=False)
    _write_executable(
        repo_root / "fake-bin" / "python3",
        """#!/bin/sh
        exit 1
        """,
    )

    env = dict(os.environ)
    env["PATH"] = f"{repo_root / 'fake-bin'}:{env['PATH']}"

    result = subprocess.run(
        [str(repo_root / "distill"), "sample.pdf"],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "missing Python dependencies for the development runner" in result.stderr
    assert 'pip install -e ".[dev]"' in result.stderr


def test_sample_digital_fixture_is_parseable_and_extracts_requirements() -> None:
    result = run_distill_pipeline(PROJECT_ROOT / "fixtures" / "specs" / "sample-digital.pdf")

    assert len(result.requirements) >= 1
    assert result.requirements[0].obligation == "shall"
