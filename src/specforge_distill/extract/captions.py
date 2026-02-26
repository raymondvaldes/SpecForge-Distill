"""Caption and figure-context extraction."""

from __future__ import annotations

import re
from typing import Iterable

from specforge_distill.ingest.pdf_loader import PageTextRecord
from specforge_distill.models.candidates import Candidate, stable_candidate_id

_CAPTION_PREFIX = re.compile(r"^(figure|fig\.|table|caption)\s*\d*[:.-]?", re.IGNORECASE)
_UNKNOWN_OBLIGATION_VERBS = {"should", "will", "ought", "expected"}
_REQUIREMENT_HINTS = {"system", "interface", "component", "module", "shall", "must", "required"}


def _tokenize(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[A-Za-z']+", text)}


def extract_caption_candidates(
    page_records: Iterable[PageTextRecord],
    obligation_verbs: set[str],
    *,
    context_window_lines: int = 1,
) -> list[Candidate]:
    """Extract requirement-adjacent statements near caption markers."""

    obligation_verbs = {verb.lower() for verb in obligation_verbs}
    candidates: list[Candidate] = []

    for page in page_records:
        lines = [line.strip() for line in page.text.splitlines() if line.strip()]
        running_index = 0

        for index, line in enumerate(lines):
            if not _CAPTION_PREFIX.match(line):
                continue

            context_lines = [line]
            for offset in range(1, context_window_lines + 1):
                if index + offset < len(lines):
                    context_lines.append(lines[index + offset])

            context_text = " ".join(context_lines).strip()
            words = _tokenize(context_text)
            has_modal = bool(words & obligation_verbs)
            has_unknown_obligation = bool((words & _UNKNOWN_OBLIGATION_VERBS) - obligation_verbs)
            requirement_adjacent = has_modal or bool(words & _REQUIREMENT_HINTS) or has_unknown_obligation
            if not requirement_adjacent:
                continue

            running_index += 1
            flags: list[str] = []
            if has_unknown_obligation:
                flags.append("unknown_obligation_verb")

            candidates.append(
                Candidate(
                    id=stable_candidate_id("caption_context", page.page_number, running_index, context_text),
                    text=context_text,
                    source_type="caption_context",
                    page=page.page_number,
                    classification="obligation" if has_modal else "neutral",
                    source_location={
                        "line_index": index + 1,
                        "caption_ref": line.split(":", maxsplit=1)[0],
                    },
                    flags=flags,
                    context_window=context_text[:260],
                )
            )

    return candidates
