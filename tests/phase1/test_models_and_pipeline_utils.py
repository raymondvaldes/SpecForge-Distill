from __future__ import annotations

from pathlib import Path

from specforge_distill.models.artifacts import ArtifactBlock, stable_artifact_id
from specforge_distill.models.candidates import Candidate, normalize_text, stable_candidate_id
from specforge_distill.pipeline import PipelineResult, load_obligation_taxonomy, run_phase1_pipeline
from specforge_distill.provenance.models import Citation


def test_normalize_text_and_candidate_id_are_deterministic() -> None:
    a = stable_candidate_id("narrative", 1, 1, "The System SHALL   log faults!")
    b = stable_candidate_id("narrative", 1, 1, "the system shall log faults")

    assert normalize_text("  The   system, SHALL log faults!! ") == "the system shall log faults"
    assert a == b


def test_stable_artifact_id_is_deterministic() -> None:
    section = "2 System Architecture"
    content = "Control and data planes are segmented."

    assert stable_artifact_id(section, 2, content) == stable_artifact_id(section, 2, content)


def test_candidate_and_artifact_to_dict_serialize_citation_objects() -> None:
    citation = Citation(page=2, source_path="spec.pdf", anchor="p2:narrative")
    candidate = Candidate(
        id="cand-1",
        text="The interface shall reject invalid packets.",
        source_type="narrative",
        page=2,
        provenance=citation,
    )
    artifact = ArtifactBlock(
        id="art-1",
        section="System Architecture",
        content="Packet validator at trust boundary.",
        page=2,
        provenance=citation,
    )

    candidate_payload = candidate.to_dict()
    artifact_payload = artifact.to_dict()

    assert candidate_payload["provenance"]["anchor"] == "p2:narrative"
    assert artifact_payload["provenance"]["anchor"] == "p2:narrative"


def test_pipeline_result_to_dict_preserves_metadata_and_counts() -> None:
    result = PipelineResult(
        warnings=[],
        candidates=[
            Candidate(
                id="cand-1",
                text="The interface shall reject invalid packets.",
                source_type="narrative",
                page=2,
            )
        ],
        requirements=[],
        artifacts=[
            ArtifactBlock(
                id="art-1",
                section="System Architecture",
                content="Packet validator at trust boundary.",
                page=2,
            )
        ],
        metadata={"taxonomy_version": "2026.02"},
    )

    payload = result.to_dict()
    assert payload["metadata"]["taxonomy_version"] == "2026.02"
    assert len(payload["candidates"]) == 1
    assert "requirements" in payload
    assert len(payload["artifacts"]) == 1


def test_load_obligation_taxonomy_from_custom_path(tmp_path: Path) -> None:
    config = tmp_path / "verbs.yml"
    config.write_text(
        "\n".join(
            [
                "version: custom-v3",
                "obligation_verbs:",
                "  - SHALL",
                "  - verify",
            ]
        ),
        encoding="utf-8",
    )

    taxonomy = load_obligation_taxonomy(config)
    assert taxonomy.version == "custom-v3"
    assert taxonomy.verbs == ("shall", "verify")


def test_pipeline_dry_run_uses_taxonomy_without_loading_pdf(tmp_path: Path) -> None:
    fake_pdf = tmp_path / "dry-run.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%placeholder\n")

    taxonomy_path = tmp_path / "verbs.yml"
    taxonomy_path.write_text(
        "\n".join(
            [
                "version: dry-run-v1",
                "obligation_verbs:",
                "  - shall",
                "  - must",
            ]
        ),
        encoding="utf-8",
    )

    result = run_phase1_pipeline(fake_pdf, taxonomy_path=taxonomy_path, dry_run=True)
    assert result.metadata["taxonomy_version"] == "dry-run-v1"
    assert result.metadata["obligation_verbs"] == ["must", "shall"]
    assert result.candidates == []
    assert result.artifacts == []
