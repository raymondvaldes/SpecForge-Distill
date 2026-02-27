"""Cross-source candidate linking."""

from __future__ import annotations

from collections import defaultdict

from specforge_distill.models.candidates import Candidate, CandidateLink, normalize_text


def link_equivalent_candidates(candidates: list[Candidate]) -> None:
    """Link equivalent text across source types without deduplicating entries."""

    groups: dict[str, list[Candidate]] = defaultdict(list)
    for candidate in candidates:
        key = normalize_text(candidate.text)
        if not key:
            continue
        groups[key].append(candidate)

    # Sort items for deterministic processing order
    for _, group in sorted(groups.items()):
        if len(group) < 2:
            continue

        # Sort candidates within group by ID to ensure stable peer linking
        sorted_group = sorted(group, key=lambda c: c.id)

        for candidate in sorted_group:
            existing = {link.target_id for link in candidate.links}
            for peer in sorted_group:
                if peer.id == candidate.id:
                    continue
                if peer.source_type == candidate.source_type:
                    continue
                if peer.id in existing:
                    continue
                candidate.links.append(
                    CandidateLink(
                        relation="semantic_duplicate",
                        target_id=peer.id,
                        confidence=1.0,
                    )
                )
