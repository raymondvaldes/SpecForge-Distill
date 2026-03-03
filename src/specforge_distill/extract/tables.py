"""Table cell extraction for requirement-like candidates."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Iterable, List, Set

from specforge_distill.models.candidates import Candidate, stable_candidate_id

_REQUIREMENT_HINTS = {
    "shall",
    "must",
    "required",
    "system",
    "interface",
    "component",
    "provide",
    "support",
}

_UNKNOWN_OBLIGATION_VERBS = {"should", "will", "ought", "expected"}


def _tokenize(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[A-Za-z']+", text)}


def _candidate_like(text: str, obligation_verbs: set[str]) -> tuple[bool, bool]:
    words = _tokenize(text)
    has_modal = bool(words & obligation_verbs)
    adjacent = bool(words & _REQUIREMENT_HINTS)
    return has_modal, has_modal or adjacent


def _unknown_flag(text: str, obligation_verbs: set[str]) -> bool:
    words = _tokenize(text)
    return bool((words & _UNKNOWN_OBLIGATION_VERBS) - obligation_verbs)


def _is_vcrm_header(row: Iterable[str]) -> bool:
    """Detect if a row looks like a VCRM/Requirement table header."""
    row_text = " ".join(str(c).lower() for f in row for c in [f] if f)
    indicators = {"req id", "requirement id", "verification method", "rationale"}
    return any(ind in row_text for ind in indicators)


class TableProcessor(ABC):
    """Abstract base for specialized table data processors."""

    @abstractmethod
    def process_row(
        self,
        row: Iterable[str],
        row_index: int,
        page_number: int,
        table_id: str,
        obligation_verbs: Set[str],
        running_index: int,
    ) -> List[Candidate]:
        """Convert a row into one or more candidates."""
        pass


class StandardTableProcessor(TableProcessor):
    """Processes each cell individually searching for requirement language."""

    def process_row(
        self,
        row: Iterable[str],
        row_index: int,
        page_number: int,
        table_id: str,
        obligation_verbs: Set[str],
        running_index: int,
    ) -> List[Candidate]:
        candidates = []
        for col_index, raw_cell in enumerate(row, start=1):
            cell_text = (raw_cell or "").strip()
            if not cell_text:
                continue

            # Only emit if it contains a modal verb (obligation)
            has_modal, _ = _candidate_like(cell_text, obligation_verbs)
            if not has_modal:
                continue

            running_index += 1
            flags: list[str] = []
            if _unknown_flag(cell_text, obligation_verbs):
                flags.append("unknown_obligation_verb")

            candidates.append(
                Candidate(
                    id=stable_candidate_id("table_cell", page_number, running_index, cell_text),
                    text=cell_text,
                    source_type="table_cell",
                    page=page_number,
                    classification="obligation",
                    source_location={
                        "table_id": table_id,
                        "cell_ref": f"R{row_index}C{col_index}",
                    },
                    flags=flags,
                    context_window=cell_text[:260],
                )
            )
        return candidates


class VCRMTableProcessor(TableProcessor):
    """Merges row content for tables identified as Verification Matrices."""

    def process_row(
        self,
        row: Iterable[str],
        row_index: int,
        page_number: int,
        table_id: str,
        obligation_verbs: Set[str],
        running_index: int,
    ) -> List[Candidate]:
        merged_text = " | ".join(str(c).strip() for c in row if c and str(c).strip())
        if not merged_text:
            return []

        running_index += 1
        return [
            Candidate(
                id=stable_candidate_id("table_row", page_number, running_index, merged_text),
                text=merged_text,
                source_type="table_cell",
                page=page_number,
                classification="neutral",
                source_location={
                    "table_id": table_id,
                    "row_ref": f"R{row_index}",
                },
                flags=["vcrm_context"],
                context_window=merged_text[:260],
            )
        ]


def extract_table_candidates_from_rows(
    *,
    page_number: int,
    table_id: str,
    rows: Iterable[Iterable[str]],
    obligation_verbs: set[str],
) -> list[Candidate]:
    """Extract candidates using specialized table processors."""

    obligation_verbs = {verb.lower() for verb in obligation_verbs}
    candidates: list[Candidate] = []
    processor: TableProcessor = StandardTableProcessor()
    
    # We need to track the global index for ID stability
    running_index = 0

    for row_index, row in enumerate(rows, start=1):
        if isinstance(processor, StandardTableProcessor) and _is_vcrm_header(row):
            processor = VCRMTableProcessor()
            continue

        row_candidates = processor.process_row(
            row, row_index, page_number, table_id, obligation_verbs, running_index
        )
        candidates.extend(row_candidates)
        running_index += len(row_candidates)

    return candidates


def extract_table_candidates(
    pdf_path: str,
    obligation_verbs: set[str],
    *,
    table_rows_by_page: dict[int, list[list[str]]] | None = None,
) -> list[Candidate]:
    """Extract table-cell candidates using injected rows or pdfplumber."""

    results: list[Candidate] = []

    if table_rows_by_page is not None:
        for page_number in sorted(table_rows_by_page):
            rows = table_rows_by_page[page_number]
            table_id = f"p{page_number}_t1"
            results.extend(
                extract_table_candidates_from_rows(
                    page_number=page_number,
                    table_id=table_id,
                    rows=rows,
                    obligation_verbs=obligation_verbs,
                )
            )
        return results

    try:
        import pdfplumber
    except ImportError:
        return results

    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            for table_index, table in enumerate(page.extract_tables() or [], start=1):
                if not table:
                    continue
                table_id = f"p{page_index}_t{table_index}"
                results.extend(
                    extract_table_candidates_from_rows(
                        page_number=page_index,
                        table_id=table_id,
                        rows=table,
                        obligation_verbs=obligation_verbs,
                    )
                )

    return results
