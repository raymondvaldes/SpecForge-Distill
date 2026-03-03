"""Narrative requirement-candidate extraction."""

from __future__ import annotations

import re
from typing import Iterable

from specforge_distill.ingest.pdf_loader import PageTextRecord
from specforge_distill.models.candidates import Candidate, stable_candidate_id

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")
_TOC_MARKER = re.compile(r"(\.{3,}|_{3,})\s*\d+$")

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


def is_toc_line(text: str) -> bool:
    """Detect if a line looks like a Table of Contents entry."""
    return bool(_TOC_MARKER.search(text.strip()))


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
        # Split on double newlines for true paragraphs, but also handle 
        # single newline splits if the lines look like independent blocks (e.g. headers)
        raw_paragraphs = [p.strip() for p in re.split(r"\n\s*\n", page.text) if p.strip()]
        paragraphs: list[str] = []
        for p in raw_paragraphs:
            if "\n" in p and len(p.splitlines()[0]) < 60:
                # If first line is short, it might be a header. Split it.
                paragraphs.extend([line.strip() for line in p.splitlines() if line.strip()])
            else:
                paragraphs.append(p)
        
        running_index = 0

        for paragraph_index, paragraph in enumerate(paragraphs, start=1):
            if is_toc_line(paragraph):
                continue
                
            has_modal = contains_modal_verb(paragraph, obligation_verbs)
            if has_modal:
                segments = split_sentences(paragraph)
            else:
                # If no modal in whole paragraph, only keep if it looks like a requirement
                if not _looks_requirement_adjacent(paragraph):
                    continue
                # If it's short and no modal, it's probably a header, skip it
                if len(paragraph) < 30:
                    continue
                segments = [paragraph]

            for segment_index, segment in enumerate(segments, start=1):
                text = segment.strip()
                if not text or is_toc_line(text):
                    continue

                # Filter out extremely short segments (likely noise)
                if len(text) < 10:
                    continue

                segment_has_modal = contains_modal_verb(text, obligation_verbs)
                # If we are in a modal paragraph, we only want the segments 
                # that actually contain the meat of the requirement.
                if not segment_has_modal:
                    if not _looks_requirement_adjacent(text):
                        continue
                    # Neutral candidates (hints) must be longer to avoid headers
                    if len(text) < 30:
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
