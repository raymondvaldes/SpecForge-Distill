from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from specforge_distill.pipeline import PipelineResult


class ManifestEntity(BaseModel):
    """Machine-readable reference to an extracted entity."""

    id: str
    type: str  # 'requirement' or 'artifact'
    page: int
    text: str
    target_file: str
    interop: Dict[str, Any] = Field(default_factory=dict)


class Manifest(BaseModel):
    """The root manifest indexing all distillation results."""

    manifest_version: str = "1.0.0"
    source_pdf: str
    model_interop_target: str = "sysmlv2-future"
    generated_files: Dict[str, str] = Field(default_factory=dict)
    entities: List[ManifestEntity] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ManifestWriter:
    """Generates a manifest.json from a PipelineResult."""

    def __init__(self, result: PipelineResult, file_mapping: Dict[str, str]):
        self.result = result
        self.file_mapping = file_mapping

    def generate(self) -> Manifest:
        """Construct the manifest object from results and file mappings."""
        entities: List[ManifestEntity] = []

        # Add requirements
        req_file = self.file_mapping.get("requirements", "requirements.md")
        for req in self.result.requirements:
            entities.append(
                ManifestEntity(
                    id=req.id,
                    type="requirement",
                    page=req.page,
                    text=req.text,
                    target_file=req_file,
                    interop=req.interop.model_dump(),
                )
            )

        # Add artifacts
        art_file = self.file_mapping.get("architecture", "architecture.md")
        for art in self.result.artifacts:
            entities.append(
                ManifestEntity(
                    id=art.id,
                    type="artifact",
                    page=art.page,
                    text=art.content,
                    target_file=art_file,
                    interop=art.interop.to_dict(),
                )
            )

        return Manifest(
            source_pdf=str(self.result.metadata.get("source_pdf", "unknown")),
            model_interop_target="sysmlv2-future",
            generated_files=self.file_mapping,
            entities=entities,
            metadata=self.result.metadata,
        )

    def write(self, output_path: str | Path) -> Path:
        """Generate and save the manifest to disk."""
        manifest = self.generate()
        path = Path(output_path)
        path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        return path
