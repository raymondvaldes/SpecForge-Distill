"""Narrative requirement-candidate extraction."""

from __future__ import annotations

import re
from typing import Iterable

from specforge_distill.ingest.pdf_loader import PageTextRecord
from specforge_distill.models.candidates import Candidate, stable_candidate_id

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")
_TOC_MARKER = re.compile(r"(\.{3,}|_{3,})\s*\d+$")
_NOTE_PREFIX = re.compile(r"^(note|notes)[:\s]", re.IGNORECASE)

_UNKNOWN_OBLIGATION_VERBS = {"ought", "expected"}


def _tokenize_words(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[A-Za-z']+", text)}


def contains_modal_verb(text: str, obligation_verbs: set[str]) -> bool:
    return bool(_tokenize_words(text) & obligation_verbs)


def contains_unknown_obligation_verb(text: str, obligation_verbs: set[str]) -> bool:
    words = _tokenize_words(text)
    return bool((words & _UNKNOWN_OBLIGATION_VERBS) - obligation_verbs)


def split_sentences(paragraph: str) -> list[str]:
    """Split paragraph into segments."""
    # Split by standard sentence boundaries
    segments = re.split(r"(?<=[.!?])\s+", paragraph)
    return [s.strip() for s in segments if s.strip()]


def is_toc_line(text: str) -> bool:
    """Detect if a line looks like a Table of Contents entry."""
    return bool(_TOC_MARKER.search(text.strip()))


def extract_narrative_candidates(
    page_records: Iterable[PageTextRecord],
    obligation_verbs: set[str],
    *,
    context_chars: int = 260,
) -> list[Candidate]:
    """Capture strong narrative candidates, including trailing 'Note:' blocks."""

    candidates: list[Candidate] = []
    obligation_verbs = {verb.lower() for verb in obligation_verbs}

    for page in page_records:
        # Step 1: Split into paragraphs and merge 'Note:' paragraphs with PRECEDING requirement-containing ones
        raw_paragraphs = [p.strip() for p in re.split(r"\n\s*\n", page.text) if p.strip()]
        
        merged_paragraphs: list[str] = []
        for p in raw_paragraphs:
            # Only merge if current is a Note AND the previous one had a modal
            if _NOTE_PREFIX.match(p) and merged_paragraphs:
                # IMPORTANT: Check if the LAST SENTENCE of the previous paragraph has a modal
                # to avoid merging a Note with a long paragraph that just happens to have a modal somewhere
                last_segments = split_sentences(merged_paragraphs[-1])
                if last_segments and contains_modal_verb(last_segments[-1], obligation_verbs):
                    merged_paragraphs[-1] = f"{merged_paragraphs[-1]} {p}"
                else:
                    merged_paragraphs.append(p)
            else:
                merged_paragraphs.append(p)

        running_index = 0

        for paragraph_index, paragraph in enumerate(merged_paragraphs, start=1):
            if is_toc_line(paragraph):
                continue
            
            # Step 2: Split into segments (sentences)
            raw_segments = split_sentences(paragraph)
            
            # Step 3: Within the paragraph, merge 'Note:' segments with the preceding sentence
            segments: list[str] = []
            for seg in raw_segments:
                if _NOTE_PREFIX.match(seg) and segments:
                    # Merge only if preceding segment had a modal
                    if contains_modal_verb(segments[-1], obligation_verbs):
                        segments[-1] = f"{segments[-1]} {seg}"
                    else:
                        segments.append(seg)
                else:
                    segments.append(seg)

            for segment_index, segment in enumerate(segments, start=1):
                text = segment.strip()
                if not text or is_toc_line(text):
                    continue

                if len(text) < 10:
                    continue

                # STRICT RULE: Only capture if it contains a modal verb.
                segment_has_modal = contains_modal_verb(text, obligation_verbs)
                if not segment_has_modal:
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
                    classification="obligation",
                    source_location={
                        "paragraph_index": paragraph_index,
                        "segment_index": segment_index,
                    },
                    flags=flags,
                    context_window=paragraph[:context_chars],
                )
                candidates.append(candidate)

    return candidates
