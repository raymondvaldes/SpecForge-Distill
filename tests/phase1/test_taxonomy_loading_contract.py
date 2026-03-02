from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


pytestmark = pytest.mark.fast_ivv


def test_load_obligation_taxonomy_completes_in_clean_subprocess() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    env = {
        "HOME": os.environ.get("HOME", str(Path.home())),
        "PATH": os.environ["PATH"],
        "PYTHONPATH": "src",
    }

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json, time; "
                "from specforge_distill.pipeline import load_obligation_taxonomy; "
                "start = time.perf_counter(); "
                "taxonomy = load_obligation_taxonomy(); "
                "print(json.dumps({"
                "'version': taxonomy.version, "
                "'verbs': taxonomy.verbs, "
                "'elapsed_s': round(time.perf_counter() - start, 3)"
                "}))"
            ),
        ],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["version"] == "2026.02"
    assert payload["verbs"] == [
        "may",
        "must",
        "optional",
        "recommended",
        "required",
        "shall",
        "should",
    ]
    assert payload["elapsed_s"] < 5.0
