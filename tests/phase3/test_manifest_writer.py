import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from specforge_distill.models.artifacts import ArtifactBlock
from specforge_distill.models.requirement import Requirement
from specforge_distill.pipeline import PipelineResult
from specforge_distill.render.manifest import ManifestWriter, ManifestEntity


@pytest.fixture
def mock_pipeline_result():
    return PipelineResult(
        warnings=[],
        candidates=[],
        requirements=[
            Requirement(
                id="REQ-001",
                text="The system shall be fast.",
                page=1,
                source_type="narrative",
                obligation="shall",
            )
        ],
        artifacts=[
            ArtifactBlock(
                id="ART-001",
                section="Introduction",
                content="The system is a car.",
                page=1,
                source_type="architecture_block",
            )
        ],
        metadata={"source_pdf": "spec.pdf", "taxonomy_version": "1.0"},
    )


def test_manifest_generation(mock_pipeline_result):
    file_mapping = {
        "requirements": "reqs.md",
        "architecture": "arch.md",
        "consolidated": "full.md",
    }

    writer = ManifestWriter(mock_pipeline_result, file_mapping)
    manifest = writer.generate()

    assert manifest.manifest_version == "1.0.0"
    assert manifest.source_pdf == "spec.pdf"
    assert manifest.generated_files == file_mapping

    assert len(manifest.entities) == 2

    req_entity = next(e for e in manifest.entities if e.type == "requirement")
    assert req_entity.id == "REQ-001"
    assert req_entity.target_file == "reqs.md"

    art_entity = next(e for e in manifest.entities if e.type == "artifact")
    assert art_entity.id == "ART-001"
    assert art_entity.target_file == "arch.md"


def test_manifest_json_serialization(mock_pipeline_result, tmp_path):
    output_file = tmp_path / "manifest.json"
    file_mapping = {"requirements": "reqs.md"}

    writer = ManifestWriter(mock_pipeline_result, file_mapping)
    writer.write(output_file)

    assert output_file.exists()

    content = json.loads(output_file.read_text())
    assert content["manifest_version"] == "1.0.0"
    assert len(content["entities"]) == 2


def test_manifest_entity_validation():
    # Valid
    entity = ManifestEntity(
        id="REQ-001", type="requirement", page=1, text="text", target_file="file.md"
    )
    assert entity.id == "REQ-001"

    # Missing required field
    with pytest.raises(ValidationError):
        ManifestEntity(id="REQ-001")
