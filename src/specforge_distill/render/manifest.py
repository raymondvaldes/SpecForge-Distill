from __future__ import annotations

import os
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

    def __init__(self, result: PipelineResult, file_mapping: Dict[str, str], output_dir: str | Path | None = None):
        self.result = result
        self.file_mapping = file_mapping
        self.output_dir = Path(output_dir) if output_dir else None

    def _make_relative(self, path_str: str) -> str:
        """Convert an absolute path to relative if output_dir is set."""
        if not self.output_dir:
            return path_str
            
        try:
            p = Path(path_str)
            if p.is_absolute():
                # We want the path relative to the output directory
                # If they are on different drives (Windows) or no common ancestor, relpath handles it
                return os.path.relpath(p, self.output_dir)
            return path_str
        except Exception:
            return path_str

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
                    interop=art.interop.model_dump(),
                )
            )

        source_pdf = str(self.result.metadata.get("source_pdf", "unknown"))
        if source_pdf != "unknown":
            source_pdf = self._make_relative(source_pdf)

        return Manifest(
            source_pdf=source_pdf,
            model_interop_target="sysmlv2-future",
            generated_files=self.file_mapping,
            entities=entities,
            metadata=self.result.metadata,
        )

    def write(self, output_path: str | Path) -> Path:
        """Generate and save the manifest to disk."""
        path = Path(output_path)
        # Automatically set output_dir to the parent of the manifest file if not explicitly set
        if not self.output_dir:
            self.output_dir = path.parent
            
        manifest = self.generate()
        path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        return path
