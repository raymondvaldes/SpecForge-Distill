import pytest
from specforge_distill.render.markdown import MarkdownRenderer
from specforge_distill.pipeline import PipelineResult
from specforge_distill.models.requirement import Requirement, VCRMAttributes
from specforge_distill.models.artifacts import ArtifactBlock
from specforge_distill.ingest.text_quality import QualityWarning

@pytest.fixture
def mock_pipeline_result():
    warnings = [
        QualityWarning(
            code="low_text_density",
            page=1,
            chars=10,
            message="Low text density"
        )
    ]
    
    requirements = [
        Requirement(
            id="REQ-001",
            text="The system shall process data.",
            obligation="shall",
            page=1,
            source_type="narrative",
            vcrm=VCRMAttributes(method="Test", rationale="Essential function")
        ),
        Requirement(
            id="REQ-002",
            text="The UI may be blue.",
            obligation="may",
            page=2,
            source_type="narrative",
            is_ambiguous=True,
            ambiguity_reasons=["Subjective color"]
        )
    ]
    
    artifacts = [
        ArtifactBlock(
            id="art-001",
            section="System Overview",
            content="The system consists of three modules.",
            page=1,
            source_type="architecture_block"
        )
    ]
    
    metadata = {"source_pdf": "test.pdf"}
    
    return PipelineResult(
        warnings=warnings,
        candidates=[], # Not used by renderer
        requirements=requirements,
        artifacts=artifacts,
        metadata=metadata
    )

def test_render_full(mock_pipeline_result):
    renderer = MarkdownRenderer(mock_pipeline_result)
    output = renderer.render_full()
    
    assert "# SpecForge Distill: test.pdf" in output
    assert "## Quality Warnings" in output
    assert "Low text density" in output
    assert "## Architecture & Context" in output
    assert "### System Overview" in output
    assert "## Requirements" in output
    assert "### Requirement REQ-001" in output
    assert "The system shall process data." in output
    assert "(p. 1)" in output

def test_render_requirements(mock_pipeline_result):
    renderer = MarkdownRenderer(mock_pipeline_result)
    output = renderer.render_requirements()
    
    assert "### Requirement REQ-001" in output
    assert "**Obligation:** `SHALL`" in output
    assert "- Method: Test" in output
    assert "- Rationale: Essential function" in output
    
    assert "### Requirement REQ-002" in output
    assert "⚠️ **Ambiguous**" in output
    assert "**Ambiguity Reasons:** Subjective color" in output

def test_render_architecture(mock_pipeline_result):
    renderer = MarkdownRenderer(mock_pipeline_result)
    output = renderer.render_architecture()
    
    assert "### System Overview" in output
    assert "**ID:** `art-001`" in output
    assert "The system consists of three modules. (p. 1)" in output

def test_render_edge_cases():
    """Test renderer with problematic or minimal data."""
    req_minimal = Requirement(
        id="MIN-001",
        text="Minimal req.",
        obligation="unknown",
        page=0,
        source_type="text"
    )
    req_special_chars = Requirement(
        id="SPEC-001",
        text="Text with *markdown* and [links] and \n newlines.",
        obligation="shall",
        page=1,
        source_type="text"
    )
    
    result = PipelineResult(
        warnings=[],
        candidates=[],
        requirements=[req_minimal, req_special_chars],
        artifacts=[],
        metadata={"source_pdf": "edge.pdf"}
    )
    
    renderer = MarkdownRenderer(result)
    output = renderer.render_requirements()
    
    assert "### Requirement MIN-001" in output
    assert "**Obligation:** `UNKNOWN`" in output
    assert "### Requirement SPEC-001" in output
    assert "*markdown*" in output
    assert "[links]" in output


def test_render_empty():
    empty_result = PipelineResult(
        warnings=[],
        candidates=[],
        requirements=[],
        artifacts=[],
        metadata={"source_pdf": "empty.pdf"}
    )
    renderer = MarkdownRenderer(empty_result)
    
    req_output = renderer.render_requirements()
    assert "_No requirements found._" in req_output
    
    arch_output = renderer.render_architecture()
    assert "_No architecture artifacts found._" in arch_output
