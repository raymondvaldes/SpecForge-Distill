from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import textwrap
from pathlib import Path

from specforge_distill.pipeline import run_distill_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _clean_subprocess_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env.pop("PYTEST_CURRENT_TEST", None)
    if extra:
        env.update(extra)
    return env


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

    distill_ps1 = PROJECT_ROOT / "distill.ps1"
    (repo_root / "distill.ps1").write_text(distill_ps1.read_text(encoding="utf-8"), encoding="utf-8")

    scripts_dir = repo_root / "scripts"
    scripts_dir.mkdir()
    shared_runner = PROJECT_ROOT / "scripts" / "run_local_dev.py"
    (scripts_dir / "run_local_dev.py").write_text(
        shared_runner.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

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

                def main(argv=None):
                    argv = list(argv if argv is not None else sys.argv[1:])
                    print(
                        json.dumps(
                            {
                                "selected_python": os.environ.get("DISTILL_SELECTED_PYTHON"),
                                "argv": argv,
                            }
                        )
                    )
                    return 0

                if __name__ == "__main__":
                    raise SystemExit(main())
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

    env = _clean_subprocess_env({"PATH": f"{repo_root / 'fake-bin'}:{os.environ['PATH']}"})

    result = subprocess.run(
        ["/bin/sh", str(repo_root / "distill"), "sample.pdf"],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["selected_python"] == "venv"
    assert payload["argv"] == ["sample.pdf"]


def test_distill_wrapper_forwards_batch_arguments(tmp_path: Path) -> None:
    repo_root = _create_wrapper_test_repo(tmp_path, include_minimal_cli=True)
    real_python = Path(sys.executable)

    _write_executable(
        repo_root / ".venv" / "bin" / "python",
        f"""#!/bin/sh
        export DISTILL_SELECTED_PYTHON=venv
        exec "{real_python}" "$@"
        """,
    )

    result = subprocess.run(
        [
            "/bin/sh",
            str(repo_root / "distill"),
            "--input-dir",
            "fixtures/specs",
            "-o",
            "batch-out",
            "--report",
        ],
        cwd=repo_root,
        env=_clean_subprocess_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["selected_python"] == "venv"
    assert payload["argv"] == ["--input-dir", "fixtures/specs", "-o", "batch-out", "--report"]


def test_distill_wrapper_fails_cleanly_when_dependencies_are_missing(tmp_path: Path) -> None:
    repo_root = _create_wrapper_test_repo(tmp_path, include_minimal_cli=False)
    real_python = Path(sys.executable)
    _write_executable(
        repo_root / ".venv" / "bin" / "python",
        f"""#!/bin/sh
        export DISTILL_SELECTED_PYTHON=venv-no-site
        exec "{real_python}" -S "$@"
        """,
    )

    result = subprocess.run(
        ["/bin/sh", str(repo_root / "distill"), "sample.pdf"],
        cwd=repo_root,
        env=_clean_subprocess_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 1
    assert "missing Python dependencies for the development runner" in result.stderr
    assert 'pip install -e ".[dev]"' in result.stderr


def test_powershell_wrapper_tracks_same_shared_runner_contract() -> None:
    wrapper_text = (PROJECT_ROOT / "distill.ps1").read_text(encoding="utf-8")

    assert ".venv\\Scripts\\python.exe" in wrapper_text
    assert "run_local_dev.py" in wrapper_text
    assert "DISTILL_SELECTED_PYTHON" in wrapper_text


def test_powershell_wrapper_executes_shared_runner_when_pwsh_is_available(tmp_path: Path) -> None:
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        return

    repo_root = _create_wrapper_test_repo(tmp_path, include_minimal_cli=True)
    env = _clean_subprocess_env({"PATH": f"{repo_root / '.venv' / 'Scripts'}:{os.environ['PATH']}"})

    real_python = Path(sys.executable)
    scripts_dir = repo_root / ".venv" / "Scripts"
    scripts_dir.mkdir(parents=True)
    _write_executable(
        scripts_dir / "python.exe",
        f"""#!/bin/sh
        export DISTILL_SELECTED_PYTHON=venv-pwsh
        exec "{real_python}" "$@"
        """,
    )

    result = subprocess.run(
        [pwsh, "-NoProfile", "-File", str(repo_root / "distill.ps1"), "sample.pdf"],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["selected_python"] == "venv-pwsh"
    assert payload["argv"] == ["sample.pdf"]


def test_sample_digital_fixture_is_parseable_and_extracts_requirements() -> None:
    result = run_distill_pipeline(PROJECT_ROOT / "fixtures" / "specs" / "sample-digital.pdf")

    assert len(result.requirements) >= 1
    assert result.requirements[0].obligation == "shall"
