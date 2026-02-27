from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from specforge_distill.pipeline import PipelineResult
    from specforge_distill.models.requirement import Requirement
    from specforge_distill.models.artifacts import ArtifactBlock


class MarkdownRenderer:
    """Renders pipeline results into human-readable Markdown documentation."""

    def __init__(self, result: PipelineResult):
        self.result = result

    def render_full(self) -> str:
        """Consolidated view with title, warnings, architecture, and requirements."""
        lines = []
        source_pdf = self.result.metadata.get("source_pdf", "Unknown Source")
        lines.append(f"# SpecForge Distill: {source_pdf}")
        lines.append("")

        if self.result.warnings:
            lines.append("## Quality Warnings")
            for warning in self.result.warnings:
                lines.append(f"- **Page {warning.page}**: {warning.message} (code: {warning.code})")
            lines.append("")

        lines.append("## Architecture & Context")
        lines.append("")
        lines.append(self.render_architecture())
        lines.append("")

        lines.append("## Requirements")
        lines.append("")
        lines.append(self.render_requirements())

        return "\n".join(lines)

    def render_requirements(self) -> str:
        """Specialized view with only requirement blocks."""
        if not self.result.requirements:
            return "_No requirements found._"

        blocks = []
        for req in self.result.requirements:
            block = self._format_requirement(req)
            blocks.append(block)

        return "\n\n".join(blocks)

    def render_architecture(self) -> str:
        """Specialized view with only architecture artifacts."""
        if not self.result.artifacts:
            return "_No architecture artifacts found._"

        blocks = []
        for artifact in self.result.artifacts:
            block = self._format_artifact(artifact)
            blocks.append(block)

        return "\n\n".join(blocks)

    def _format_requirement(self, req: Requirement) -> str:
        """Format a single requirement into a markdown block."""
        header = f"### Requirement {req.id}"
        meta = f"**Obligation:** `{req.obligation.upper()}`"
        if req.is_ambiguous:
            meta += " ⚠️ **Ambiguous**"

        citation = f"(p. {req.page})"

        lines = [
            header,
            "",
            f"{req.text} {citation}",
            "",
            meta
        ]

        if req.ambiguity_reasons:
            lines.append(f"**Ambiguity Reasons:** {', '.join(req.ambiguity_reasons)}")

        # VCRM check - handle pydantic model
        vcrm_data = req.vcrm.model_dump() if hasattr(req.vcrm, "model_dump") else {}
        if any(v for v in vcrm_data.values()):
            lines.append("")
            lines.append("**VCRM Attributes:**")
            if vcrm_data.get("method"):
                lines.append(f"- Method: {vcrm_data['method']}")
            if vcrm_data.get("allocation"):
                lines.append(f"- Allocation: {vcrm_data['allocation']}")
            if vcrm_data.get("rationale"):
                lines.append(f"- Rationale: {vcrm_data['rationale']}")
            if vcrm_data.get("success_criteria"):
                lines.append(f"- Success Criteria: {vcrm_data['success_criteria']}")

        return "\n".join(lines)

    def _format_artifact(self, artifact: ArtifactBlock) -> str:
        """Format a single architecture artifact into a markdown block."""
        header = f"### {artifact.section}"
        citation = f"(p. {artifact.page})"

        lines = [
            header,
            f"**ID:** `{artifact.id}`",
            "",
            f"{artifact.content} {citation}"
        ]

        return "\n".join(lines)
