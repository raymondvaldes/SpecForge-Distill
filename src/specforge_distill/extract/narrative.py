"""Narrative requirement-candidate extraction."""

from __future__ import annotations

import re
from typing import Iterable

from specforge_distill.ingest.pdf_loader import PageTextRecord
from specforge_distill.models.candidates import Candidate, stable_candidate_id

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")

_REQUIREMENT_ADJACENT_HINTS = {
    "system",
    "module",
    "interface",
    "component",
    "shall",
    "must",
    "required",
    "needs",
    "provide",
    "support",
    "maintain",
    "perform",
    "constraint",
    "capability",
}

_UNKNOWN_OBLIGATION_VERBS = {"should", "will", "ought", "expected"}


def _tokenize_words(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[A-Za-z']+", text)}


def contains_modal_verb(text: str, obligation_verbs: set[str]) -> bool:
    return bool(_tokenize_words(text) & obligation_verbs)


def contains_unknown_obligation_verb(text: str, obligation_verbs: set[str]) -> bool:
    words = _tokenize_words(text)
    return bool((words & _UNKNOWN_OBLIGATION_VERBS) - obligation_verbs)


def split_sentences(paragraph: str) -> list[str]:
    sentences = [segment.strip() for segment in _SENTENCE_BOUNDARY.split(paragraph.strip())]
    return [sentence for sentence in sentences if sentence]


def _looks_requirement_adjacent(text: str) -> bool:
    words = _tokenize_words(text)
    return bool(words & _REQUIREMENT_ADJACENT_HINTS)


def extract_narrative_candidates(
    page_records: Iterable[PageTextRecord],
    obligation_verbs: set[str],
    *,
    context_chars: int = 260,
) -> list[Candidate]:
    """Capture broad narrative candidates with modal-triggered sentence splitting."""

    candidates: list[Candidate] = []
    obligation_verbs = {verb.lower() for verb in obligation_verbs}

    for page in page_records:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", page.text) if p.strip()]
        running_index = 0

        for paragraph_index, paragraph in enumerate(paragraphs, start=1):
            has_modal = contains_modal_verb(paragraph, obligation_verbs)
            segments = split_sentences(paragraph) if has_modal else [paragraph]

            for segment_index, segment in enumerate(segments, start=1):
                text = segment.strip()
                if not text:
                    continue

                segment_has_modal = contains_modal_verb(text, obligation_verbs)
                if not segment_has_modal and not _looks_requirement_adjacent(text):
                    continue

                running_index += 1
                flags: list[str] = []
                if contains_unknown_obligation_verb(text, obligation_verbs):
                    flags.append("unknown_obligation_verb")

                candidate = Candidate(
                    id=stable_candidate_id("narrative", page.page_number, running_index, text),
                    text=text,
                    source_type="narrative",
                    page=page.page_number,
                    classification="obligation" if segment_has_modal else "neutral",
                    source_location={
                        "paragraph_index": paragraph_index,
                        "segment_index": segment_index,
                    },
                    flags=flags,
                    context_window=paragraph[:context_chars],
                )
                candidates.append(candidate)

    return candidates
