"""Requirement validation and quality diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from specforge_distill.pipeline import PipelineResult


@dataclass(frozen=True)
class ValidationIssue:
    """A single validation finding for a requirement or artifact."""

    code: str
    severity: str  # error, warning, info
    message: str
    page: int
    entity_id: str

    def to_dict(self) -> dict[str, str | int]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "page": self.page,
            "entity_id": self.entity_id,
        }


@dataclass(frozen=True)
class ValidationSummary:
    """Aggregate validation report."""

    issues: list[ValidationIssue]

    def to_dict(self) -> dict[str, Any]:
        return {
            "issues": [issue.to_dict() for issue in self.issues],
            "totals": {
                "errors": sum(1 for i in self.issues if i.severity == "error"),
                "warnings": sum(1 for i in self.issues if i.severity == "warning"),
                "info": sum(1 for i in self.issues if i.severity == "info"),
            },
        }


def validate_requirements(result: PipelineResult) -> ValidationSummary:
    """Run quality and consistency checks on extracted requirements."""

    issues: list[ValidationIssue] = []
    seen_ids: dict[str, int] = {}

    for req in result.requirements:
        # 1. Duplicate ID check
        if req.id in seen_ids:
            issues.append(
                ValidationIssue(
                    code="duplicate_id",
                    severity="error",
                    message=f"Duplicate requirement ID detected: {req.id}",
                    page=req.page,
                    entity_id=req.id,
                )
            )
        seen_ids[req.id] = seen_ids.get(req.id, 0) + 1

        # 2. Generated ID warning
        if req.is_generated_id:
            issues.append(
                ValidationIssue(
                    code="generated_id",
                    severity="info",
                    message="Requirement has no source-provided ID; a stable hash was generated.",
                    page=req.page,
                    entity_id=req.id,
                )
            )

        # 3. Ambiguity warning
        if req.is_ambiguous:
            reasons = ", ".join(req.ambiguity_reasons)
            issues.append(
                ValidationIssue(
                    code="ambiguous_requirement",
                    severity="warning",
                    message=f"Requirement language is ambiguous. Reasons: {reasons}",
                    page=req.page,
                    entity_id=req.id,
                )
            )

        # 4. Missing obligation check (if classifier couldn't determine it)
        if req.obligation == "unknown":
             issues.append(
                ValidationIssue(
                    code="unknown_obligation",
                    severity="warning",
                    message="Extraction found a candidate but couldn't classify a clear obligation verb.",
                    page=req.page,
                    entity_id=req.id,
                )
            )

    return ValidationSummary(issues=issues)
