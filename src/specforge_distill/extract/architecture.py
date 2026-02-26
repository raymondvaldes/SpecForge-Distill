"""Architecture section extraction."""

from __future__ import annotations

import re
from typing import Iterable

from specforge_distill.ingest.pdf_loader import PageTextRecord
from specforge_distill.models.artifacts import ArtifactBlock, stable_artifact_id

_ARCHITECTURE_HEADING = re.compile(
    r"^(?:\d+(?:\.\d+)*)?\s*(?:system\s+architecture|architecture|logical\s+architecture|physical\s+architecture)\b",
    re.IGNORECASE,
)


def _flush_block(
    page_number: int,
    heading: str | None,
    body_lines: list[str],
    start_line: int,
    results: list[ArtifactBlock],
) -> None:
    if not heading:
        return
    body = "\n".join(line.strip() for line in body_lines if line.strip()).strip()
    if not body:
        return

    section = heading.strip()
    artifact = ArtifactBlock(
        id=stable_artifact_id(section, page_number, body),
        section=section,
        content=body,
        page=page_number,
        source_location={"line": start_line},
    )
    results.append(artifact)


def extract_architecture_blocks(page_records: Iterable[PageTextRecord]) -> list[ArtifactBlock]:
    """Extract architecture sections into structured blocks."""

    blocks: list[ArtifactBlock] = []

    for page in page_records:
        lines = [line.rstrip() for line in page.text.splitlines()]
        heading: str | None = None
        body_lines: list[str] = []
        start_line = 1

        for line_number, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line:
                if heading:
                    body_lines.append("")
                continue

            if _ARCHITECTURE_HEADING.match(line):
                _flush_block(page.page_number, heading, body_lines, start_line, blocks)
                heading = line
                body_lines = []
                start_line = line_number
                continue

            if heading:
                body_lines.append(line)

        _flush_block(page.page_number, heading, body_lines, start_line, blocks)

    return blocks
