from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RELEASE_VERSION = "v1.1.0"


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
        "distill-v1.1.0-linux-x64",
        "distill-v1.1.0-macos-x64.zip",
        "distill-v1.1.0-macos-arm64.zip",
        "distill-v1.1.0-windows-x64.exe",
    ]
    assert {asset["artifact_name"] for asset in assets} == {
        "release-bundle-linux-x64",
        "release-bundle-macos-x64",
        "release-bundle-macos-arm64",
        "release-bundle-windows-x64",
    }


def test_ci_binary_smoke_workflow_uses_real_fixture_pdf() -> None:
    workflow_text = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "fixtures/specs/sample-digital.pdf" in workflow_text
    assert "distill-linux-x64" in workflow_text
    assert "--describe-output json" in workflow_text
    assert "--self-test" in workflow_text


def test_release_workflow_uses_contract_and_self_test_smoke_checks() -> None:
    workflow_text = _release_workflow_text()
    assert "--describe-output json" in workflow_text
    assert "--self-test" in workflow_text
    assert "scripts/release_manifest.py" in workflow_text
    assert "scripts/render_release_notes.py" in workflow_text
    assert "--write-checksums-manifest release-artifacts" in workflow_text
    assert "release-bundle-" in workflow_text
    assert "release-status-" in workflow_text


def test_release_workflow_collects_checksums_and_publishes_once() -> None:
    workflow = _release_workflow()

    assert "prepare-release" in workflow["jobs"]
    assert "collect-release-assets" in workflow["jobs"]
    assert "publish-release" in workflow["jobs"]
    assert workflow["jobs"]["build"]["strategy"]["fail-fast"] is False
    assert workflow["jobs"]["build"]["strategy"]["matrix"]["include"] == "${{ fromJson(needs.prepare-release.outputs.release_matrix) }}"
    assert workflow["jobs"]["publish-release"]["steps"][-1]["with"]["body_path"] == "release-metadata/release-body.md"
    assert workflow["jobs"]["publish-release"]["steps"][-1]["uses"] == "softprops/action-gh-release@v2"


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

    assert "Failure Class: Invalid Invocation" in troubleshooting_text
    assert "Failure Class: Missing Input File" in troubleshooting_text
    assert "Failure Class: Checksum Mismatch" in troubleshooting_text
    assert "Failure Class: Self-Test Validation Failure" in troubleshooting_text
    assert "Failure Class: Output Write Failure" in troubleshooting_text
    assert "Failure Class: PDF Processing Failure" in troubleshooting_text
    assert "Result Class: Low-Text Or Likely Image-Only Extraction" in troubleshooting_text
    assert "Official downloads are GitHub Releases assets only." in troubleshooting_text
