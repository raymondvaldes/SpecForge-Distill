from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from specforge_distill.cli import main as cli_main
from specforge_distill.models.artifacts import ArtifactBlock
from specforge_distill.models.requirement import Requirement
from specforge_distill.pipeline import PipelineResult


def create_mock_result(*, source_pdf: str = "sample-digital.pdf") -> PipelineResult:
    """Create a deterministic PipelineResult for testing orchestration."""
    req = Requirement(
        id="req-1",
        text="The system shall do X.",
        page=1,
        source_type="narrative",
        obligation="shall",
    )
    art = ArtifactBlock(
        id="art-1",
        section="Overview",
        content="Architecture description.",
        page=1,
    )
    return PipelineResult(
        warnings=[],
        candidates=[],
        requirements=[req],
        artifacts=[art],
        metadata={
            "source_pdf": source_pdf,
            "taxonomy_version": "2026.02",
        },
    )


def test_pipeline_determinism(tmp_path: Path) -> None:
    """
    Verify that running the pipeline twice on the same input produces
    identical manifest.json and markdown content.
    """
    source_pdf = tmp_path / "sample-digital.pdf"
    source_pdf.write_bytes(b"%PDF-1.4\n")

    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"

    mock_result = create_mock_result(source_pdf=str(source_pdf))

    with patch(
        "specforge_distill.cli.run_distill_pipeline",
        side_effect=[deepcopy(mock_result), deepcopy(mock_result)],
    ):
        exit_code1 = cli_main(["distill", str(source_pdf), "-o", str(out1)])
        exit_code2 = cli_main(["distill", str(source_pdf), "-o", str(out2)])

    assert exit_code1 == 0
    assert exit_code2 == 0

    manifest1_path = out1 / "manifest.json"
    manifest2_path = out2 / "manifest.json"

    assert manifest1_path.read_text() == manifest2_path.read_text()

    for md_file in ["full.md", "requirements.md", "architecture.md"]:
        assert (out1 / md_file).read_text() == (out2 / md_file).read_text()


def test_manifest_paths_are_relative(tmp_path: Path) -> None:
    """
    Verify that manifest.json contains relative paths, not absolute ones.
    """
    source_pdf = tmp_path / "abs_source.pdf"
    source_pdf.write_bytes(b"%PDF-1.4\n")

    out_dir = tmp_path / "out"

    mock_result = create_mock_result()
    mock_result.metadata["source_pdf"] = str(source_pdf.absolute())

    with patch("specforge_distill.cli.run_distill_pipeline", return_value=mock_result):
        exit_code = cli_main(["distill", str(source_pdf), "-o", str(out_dir)])

    assert exit_code == 0

    manifest = json.loads((out_dir / "manifest.json").read_text())

    manifest_source_pdf = manifest["source_pdf"]
    assert not Path(manifest_source_pdf).is_absolute()
    assert manifest_source_pdf == "../abs_source.pdf"
