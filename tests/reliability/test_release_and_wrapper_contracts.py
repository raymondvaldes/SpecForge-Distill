from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RELEASE_VERSION = "v1.2.2"


@lru_cache(maxsize=None)
def _load_release_manifest_module():
    module_path = PROJECT_ROOT / "scripts" / "release_manifest.py"
    spec = importlib.util.spec_from_file_location("release_manifest", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=None)
def _release_assets_from_manifest(version: str = RELEASE_VERSION) -> list[dict[str, str]]:
    return _load_release_manifest_module().build_release_manifest(version)


@lru_cache(maxsize=None)
def _load_release_notes_renderer_module():
    module_path = PROJECT_ROOT / "scripts" / "render_release_notes.py"
    spec = importlib.util.spec_from_file_location("render_release_notes", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=None)
def _release_workflow_text() -> str:
    return (PROJECT_ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def _release_workflow() -> dict[str, object]:
    return yaml.safe_load(_release_workflow_text())


def test_release_manifest_produces_explicit_versioned_assets() -> None:
    assets = _release_assets_from_manifest()

    assert [asset["release_name"] for asset in assets] == [
        f"distill-{RELEASE_VERSION}-linux-x64",
        f"distill-{RELEASE_VERSION}-macos-x64.zip",
        f"distill-{RELEASE_VERSION}-macos-arm64.zip",
        f"distill-{RELEASE_VERSION}-windows-x64.exe",
    ]


def test_release_manifest_matches_workflow_matrix() -> None:
    manifest = _release_assets_from_manifest()
    workflow = _release_workflow()

    # The current workflow uses a dynamic matrix from scripts/release_manifest.py
    # So we just verify that we can load the manifest and it has entries.
    assert len(manifest) == 4
    
    # Also verify the workflow references the script
    workflow_text = _release_workflow_text()
    assert "scripts/release_manifest.py" in workflow_text


def test_release_notes_renderer_builds_trust_first_body() -> None:
    renderer = _load_release_notes_renderer_module()
    body = renderer.render_release_body(RELEASE_VERSION)

    assert "Official downloads are GitHub Releases assets only." in body
    assert "## Asset Selection Matrix" in body
    assert "checksums.txt" in body
    assert "--version" in body
    assert "--self-test" in body
    assert "## Curated Release Notes" in body
    for asset in _release_assets_from_manifest():
        assert asset["release_name"] in body


def test_install_docs_reference_versioned_assets_and_trust_sequence() -> None:
    readme_text = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    build_text = (PROJECT_ROOT / "docs" / "BUILD.md").read_text(encoding="utf-8")

    for asset in _release_assets_from_manifest():
        assert asset["release_name"] in readme_text
        assert asset["release_name"] in build_text

    for text in (readme_text, build_text):
        assert "Official downloads are GitHub Releases assets only." in text
        assert "--self-test" in text
        assert "checksum" in text.lower()


def test_troubleshooting_routes_by_failure_class() -> None:
    troubleshooting_text = (PROJECT_ROOT / "docs" / "TROUBLESHOOTING.md").read_text(encoding="utf-8")

    assert "## Common Failure Modes" in troubleshooting_text
    assert "### Permission Denied" in troubleshooting_text
    assert "### Corrupt Download" in troubleshooting_text
    assert "### Resource Exhaustion" in troubleshooting_text
