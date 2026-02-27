from specforge_distill.pipeline import PipelineResult
from specforge_distill.models.requirement import Requirement, VCRMAttributes
from specforge_distill.models.artifacts import ArtifactBlock
from specforge_distill.ingest.text_quality import QualityWarning
from specforge_distill.render.markdown import MarkdownRenderer

def verify_render():
    warnings = [QualityWarning(page=1, message="Low text density", score=0.1)]
    
    req = Requirement(
        id="REQ-001",
        text="The system shall do something.",
        obligation="shall",
        page=2,
        source_type="narrative",
        vcrm=VCRMAttributes(method="Test", rationale="Safety critical")
    )
    
    art = ArtifactBlock(
        id="art-001",
        section="System Overview",
        content="This is the system architecture description.",
        page=1
    )
    
    result = PipelineResult(
        warnings=warnings,
        candidates=[],
        requirements=[req],
        artifacts=[art],
        metadata={"source_pdf": "test.pdf"}
    )
    
    renderer = MarkdownRenderer(result)
    
    print("--- FULL RENDER ---")
    print(renderer.render_full())
    print("\n--- REQUIREMENTS ONLY ---")
    print(renderer.render_requirements())
    print("\n--- ARCHITECTURE ONLY ---")
    print(renderer.render_architecture())

if __name__ == "__main__":
    verify_render()
