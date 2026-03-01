"""Machine-readable CLI support for AI and automation consumers."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from specforge_distill import __version__
from specforge_distill.ingest.text_quality import QualityWarning
from specforge_distill.models.artifacts import ArtifactBlock
from specforge_distill.models.candidates import Candidate
from specforge_distill.models.common import InteropMetadata
from specforge_distill.models.requirement import Requirement
from specforge_distill.pipeline import PipelineResult
from specforge_distill.render.manifest import Manifest, ManifestWriter
from specforge_distill.render.markdown import MarkdownRenderer


TROUBLESHOOTING_GUIDE = "docs/TROUBLESHOOTING.md"

FILE_MAPPING = {
    "full": "full.md",
    "requirements": "requirements.md",
    "architecture": "architecture.md",
    "manifest": "manifest.json",
}
BATCH_SUMMARY_FILE = "batch-summary.json"

EXIT_CODES = {
    "0": "success",
    "2": "invalid invocation or missing input file",
    "3": "pdf processing or output generation failure",
    "4": "self-test validation failure",
    "5": "batch completed with one or more item failures",
}

DRY_RUN_SCHEMA = {
    "type": "object",
    "required": [
        "source",
        "warnings",
        "candidate_count",
        "artifact_count",
        "taxonomy_version",
        "extraction_assessment",
    ],
    "properties": {
        "source": {"type": "string"},
        "warnings": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["code", "page", "chars", "message"],
                "properties": {
                    "code": {"type": "string"},
                    "page": {"type": "integer"},
                    "chars": {"type": "integer"},
                    "message": {"type": "string"},
                },
            },
        },
        "candidate_count": {"type": "integer"},
        "artifact_count": {"type": "integer"},
        "taxonomy_version": {"type": "string"},
        "extraction_assessment": {
            "type": "string",
            "enum": [
                "content_extracted",
                "content_extracted_with_low_text_warnings",
                "likely_text_layer_issue",
                "no_structured_content",
            ],
        },
    },
}

BATCH_ITEM_SCHEMA = {
    "type": "object",
    "required": [
        "source",
        "planned_output_dir",
        "status",
        "output_dir",
        "generated_files",
        "manifest_path",
        "manifest_version",
        "warning_count",
        "entity_counts",
        "extraction_assessment",
        "failure_class",
        "detail",
    ],
    "properties": {
        "source": {"type": "string"},
        "planned_output_dir": {"type": "string"},
        "status": {"type": "string", "enum": ["ok", "failed"]},
        "output_dir": {"type": ["string", "null"]},
        "generated_files": {
            "type": ["object", "null"],
            "properties": {key: {"type": "string"} for key in FILE_MAPPING},
        },
        "manifest_path": {"type": ["string", "null"]},
        "manifest_version": {"type": ["string", "null"]},
        "warning_count": {"type": "integer"},
        "entity_counts": {
            "type": "object",
            "required": ["candidates", "requirements", "artifacts"],
            "properties": {
                "candidates": {"type": "integer"},
                "requirements": {"type": "integer"},
                "artifacts": {"type": "integer"},
            },
        },
        "extraction_assessment": {
            "type": ["string", "null"],
            "enum": [
                "content_extracted",
                "content_extracted_with_low_text_warnings",
                "likely_text_layer_issue",
                "no_structured_content",
                None,
            ],
        },
        "failure_class": {"type": ["string", "null"]},
        "detail": {"type": ["string", "null"]},
    },
}

BATCH_SUMMARY_SCHEMA = {
    "type": "object",
    "required": [
        "status",
        "mode",
        "version",
        "dry_run",
        "batch_root",
        "summary_path",
        "batch_summary_file",
        "items",
        "totals",
    ],
    "properties": {
        "status": {"type": "string", "enum": ["ok", "partial_failure"]},
        "mode": {"type": "string", "enum": ["batch", "batch-dry-run"]},
        "version": {"type": "string"},
        "dry_run": {"type": "boolean"},
        "batch_root": {"type": "string"},
        "summary_path": {"type": ["string", "null"]},
        "batch_summary_file": {"type": "string"},
        "items": {"type": "array", "items": BATCH_ITEM_SCHEMA},
        "totals": {
            "type": "object",
            "required": [
                "sources",
                "succeeded",
                "failed",
                "warnings",
                "candidates",
                "requirements",
                "artifacts",
            ],
            "properties": {
                "sources": {"type": "integer"},
                "succeeded": {"type": "integer"},
                "failed": {"type": "integer"},
                "warnings": {"type": "integer"},
                "candidates": {"type": "integer"},
                "requirements": {"type": "integer"},
                "artifacts": {"type": "integer"},
            },
        },
    },
}

EXAMPLE_OUTPUT_SCHEMA = {
    "type": "object",
    "required": [
        "status",
        "mode",
        "version",
        "output_dir",
        "generated_files",
        "file_names",
        "manifest_path",
        "manifest_version",
        "entity_counts",
        "warning_count",
        "source_pdf",
    ],
    "properties": {
        "status": {"type": "string", "enum": ["ok"]},
        "mode": {"type": "string", "enum": ["example-output"]},
        "version": {"type": "string"},
        "output_dir": {"type": "string"},
        "generated_files": {
            "type": "object",
            "required": list(FILE_MAPPING.keys()),
            "properties": {key: {"type": "string"} for key in FILE_MAPPING},
        },
        "file_names": {
            "type": "object",
            "required": list(FILE_MAPPING.keys()),
            "properties": {key: {"type": "string"} for key in FILE_MAPPING},
        },
        "manifest_path": {"type": "string"},
        "manifest_version": {"type": "string"},
        "entity_counts": {
            "type": "object",
            "required": ["candidates", "requirements", "artifacts"],
            "properties": {
                "candidates": {"type": "integer"},
                "requirements": {"type": "integer"},
                "artifacts": {"type": "integer"},
            },
        },
        "warning_count": {"type": "integer"},
        "source_pdf": {"type": "string"},
    },
}

SELF_TEST_SCHEMA = {
    "type": "object",
    "required": [
        "status",
        "mode",
        "version",
        "checks",
        "preserved_output",
        "preserved_output_dir",
        "output_dir",
        "generated_files",
        "file_names",
        "manifest_path",
        "manifest_version",
        "entity_counts",
        "warning_count",
        "source_pdf",
    ],
    "properties": {
        "status": {"type": "string", "enum": ["ok"]},
        "mode": {"type": "string", "enum": ["self-test"]},
        "version": {"type": "string"},
        "checks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "status", "detail"],
                "properties": {
                    "name": {"type": "string"},
                    "status": {"type": "string", "enum": ["ok", "failed"]},
                    "detail": {"type": "string"},
                },
            },
        },
        "preserved_output": {"type": "boolean"},
        "preserved_output_dir": {"type": ["string", "null"]},
        "output_dir": {"type": "string"},
        "generated_files": {
            "type": "object",
            "required": list(FILE_MAPPING.keys()),
            "properties": {key: {"type": "string"} for key in FILE_MAPPING},
        },
        "file_names": {
            "type": "object",
            "required": list(FILE_MAPPING.keys()),
            "properties": {key: {"type": "string"} for key in FILE_MAPPING},
        },
        "manifest_path": {"type": "string"},
        "manifest_version": {"type": "string"},
        "entity_counts": {
            "type": "object",
            "required": ["candidates", "requirements", "artifacts"],
            "properties": {
                "candidates": {"type": "integer"},
                "requirements": {"type": "integer"},
                "artifacts": {"type": "integer"},
            },
        },
        "warning_count": {"type": "integer"},
        "source_pdf": {"type": "string"},
    },
}

CLI_FLAGS = {
    "pdf_path": {
        "kind": "positional",
        "value_type": "path",
        "required_in_modes": ["distill"],
        "supported_in_modes": ["distill"],
        "conflicts_with": [
            "--describe-output",
            "--emit-example-output",
            "--self-test",
        ],
        "repeatable": True,
        "batch_behavior": "One PDF keeps single-file mode; multiple PDFs enter explicit batch mode.",
        "description": "One or more source digital-text PDF paths for normal distillation.",
    },
    "--input-dir": {
        "kind": "option",
        "value_type": "path",
        "supported_in_modes": ["distill"],
        "conflicts_with": ["pdf_path", "--describe-output", "--emit-example-output", "--self-test"],
        "description": "Resolve direct child PDFs from one directory and process them as a batch.",
    },
    "--version": {
        "kind": "flag",
        "supported_in_modes": ["global"],
        "exits_immediately": True,
        "stdout_format": "text",
        "description": "Print the CLI version and exit through argparse.",
    },
    "--describe-output": {
        "kind": "mode",
        "value_type": "enum",
        "choices": ["json"],
        "supported_in_modes": ["describe-output"],
        "stdout_format": "json",
        "stdout_schema": "describe-output",
        "conflicts_with": ["pdf_path", "--output-dir", "--dry-run", "--report"],
        "description": "Print the machine-readable CLI and output contract.",
    },
    "--emit-example-output": {
        "kind": "mode",
        "value_type": "optional_path",
        "supported_in_modes": ["emit-example-output"],
        "stdout_format": "json",
        "stdout_schema": "example-output",
        "default_output_dir": "specforge_distill_example_output",
        "fallback_option": "--output-dir",
        "argument_precedence": "Explicit DIR passed to --emit-example-output wins over --output-dir.",
        "conflicts_with": ["pdf_path", "--dry-run"],
        "description": "Write a canonical output package without needing a source PDF.",
    },
    "--self-test": {
        "kind": "mode",
        "value_type": "optional_path",
        "supported_in_modes": ["self-test"],
        "stdout_format": "json",
        "stdout_schema": "self-test",
        "fallback_option": "--output-dir",
        "argument_precedence": "Explicit DIR passed to --self-test wins over --output-dir.",
        "preserve_behavior": "Without DIR or --output-dir, output is written to a temporary directory and removed.",
        "conflicts_with": ["pdf_path", "--dry-run"],
        "description": "Run deterministic verification using the same output writer used by normal distillation.",
    },
    "--output-dir": {
        "kind": "option",
        "value_type": "path",
        "default": None,
        "supported_in_modes": ["distill", "emit-example-output", "self-test"],
        "description": "Output target for single-file distillation, batch root for batch mode, or fallback preserve directory for example/self-test modes.",
    },
    "--dry-run": {
        "kind": "flag",
        "supported_in_modes": ["distill"],
        "stdout_format": "json",
        "stdout_schema": "dry-run",
        "batch_stdout_schema": "batch-summary",
        "conflicts_with": [
            "--describe-output",
            "--emit-example-output",
            "--self-test",
        ],
        "description": "Run extraction without writing output files and emit a dry-run JSON summary for single-file or batch mode.",
    },
    "--min-chars-per-page": {
        "kind": "option",
        "value_type": "integer",
        "default": 40,
        "supported_in_modes": ["distill"],
        "description": "Low-text warning threshold applied during PDF processing.",
    },
    "--allow-external-ai": {
        "kind": "flag",
        "supported_in_modes": ["distill"],
        "current_behavior": "accepted but currently no-op",
        "description": "Reserved for future enrichment workflows.",
    },
    "--report": {
        "kind": "flag",
        "supported_in_modes": ["distill"],
        "stdout_format": "text",
        "description": "Print a generated-file report after a successful normal distillation run.",
    },
}

INVOCATION_MODES = {
    "distill": {
        "requires_one_of": ["pdf_path", "--input-dir"],
        "optional_flags": [
            "--input-dir",
            "--output-dir",
            "--dry-run",
            "--min-chars-per-page",
            "--allow-external-ai",
            "--report",
        ],
        "stdout_modes": ["text", "dry-run", "batch-summary"],
        "stderr_modes": ["plain-text warnings", "plain-text errors"],
    },
    "describe-output": {
        "requires": ["--describe-output json"],
        "optional_flags": [],
        "stdout_modes": ["describe-output"],
        "stderr_modes": ["plain-text errors"],
    },
    "emit-example-output": {
        "requires": ["--emit-example-output [DIR]"],
        "optional_flags": ["--output-dir"],
        "stdout_modes": ["example-output"],
        "stderr_modes": ["plain-text errors"],
    },
    "self-test": {
        "requires": ["--self-test [DIR]"],
        "optional_flags": ["--output-dir"],
        "stdout_modes": ["self-test"],
        "stderr_modes": ["json errors"],
    },
}

def _troubleshooting_pointer(anchor: str) -> dict[str, str]:
    return {
        "guide": TROUBLESHOOTING_GUIDE,
        "anchor": anchor,
        "pointer": f"{TROUBLESHOOTING_GUIDE}{anchor}",
    }


FAILURE_CLASSES = {
    "invalid_invocation": {
        "failure_class": "invalid_invocation",
        "exit_code": 2,
        "stderr_format": "plain-text",
        "typical_stderr_prefix": "error:",
        "when_it_happens": [
            "A required PDF path is missing for a normal distillation run.",
            "A special mode is combined with incompatible PDF-processing flags.",
        ],
        "recovery_hint": "Adjust flags so the command uses one supported invocation mode.",
        "recovery": "Adjust flags to match one invocation mode.",
        "troubleshooting": _troubleshooting_pointer("#failure-class-invalid-invocation"),
    },
    "missing_input_file": {
        "failure_class": "missing_input_file",
        "exit_code": 2,
        "stderr_format": "plain-text",
        "typical_stderr_prefix": "error: file not found:",
        "when_it_happens": [
            "The provided pdf_path does not exist on disk.",
        ],
        "recovery_hint": "Fix the PDF path, then rerun the command before attempting any real processing.",
        "recovery": "Resolve the path before retrying.",
        "troubleshooting": _troubleshooting_pointer("#failure-class-missing-input-file"),
    },
    "pdf_processing_failure": {
        "failure_class": "pdf_processing_failure",
        "exit_code": 3,
        "stderr_format": "plain-text",
        "typical_stderr_prefix": "error: Failed to process PDF.",
        "when_it_happens": [
            "The PDF is corrupted, encrypted, malformed, or otherwise unsupported by the extractor.",
            "Output generation fails after the pipeline starts.",
        ],
        "recovery_hint": "Retry with a known-good digital-text PDF after reading the matching troubleshooting section.",
        "recovery": "Inspect stderr details and retry with a known-good digital-text PDF.",
        "troubleshooting": _troubleshooting_pointer("#failure-class-pdf-processing-failure"),
    },
    "output_write_failure": {
        "failure_class": "output_write_failure",
        "exit_code": 3,
        "stderr_format": "plain-text",
        "typical_stderr_prefix": "error: failed to write output package",
        "when_it_happens": [
            "The output directory is unwritable or the destination path cannot be created.",
            "A filesystem error prevents manifest or markdown generation from being written.",
        ],
        "recovery_hint": "Retry with a writable output path after checking shell path and permission assumptions for the current platform.",
        "recovery": "Pick a writable output directory and retry the command.",
        "troubleshooting": _troubleshooting_pointer("#failure-class-output-write-failure"),
    },
    "self_test_validation_failure": {
        "failure_class": "self_test_validation_failure",
        "exit_code": 4,
        "stderr_format": "json",
        "stderr_shape": {
            "status": "failed",
            "mode": "self-test",
            "version": "<tool version>",
            "failure_class": "self_test_validation_failure",
            "recovery_hint": "<short recovery step>",
            "troubleshooting": {
                "guide": TROUBLESHOOTING_GUIDE,
                "anchor": "#failure-class-self-test-validation-failure",
                "pointer": f"{TROUBLESHOOTING_GUIDE}#failure-class-self-test-validation-failure",
            },
            "detail": "<validation error>",
        },
        "when_it_happens": [
            "The built-in deterministic self-test cannot write or validate the canonical output package.",
        ],
        "recovery_hint": "Do not process a real PDF until distill --self-test passes cleanly on the downloaded binary.",
        "recovery": "Treat the installation or runtime environment as unhealthy until the self-test passes.",
        "troubleshooting": _troubleshooting_pointer("#failure-class-self-test-validation-failure"),
    },
    "batch_partial_failure": {
        "failure_class": "batch_partial_failure",
        "exit_code": 5,
        "stderr_format": "plain-text",
        "typical_stderr_prefix": "batch finished with failures:",
        "when_it_happens": [
            "At least one input in a batch fails after batch resolution begins.",
        ],
        "recovery_hint": "Inspect batch-summary.json to see which inputs failed and rerun only the failed items after fixing them.",
        "recovery": "Use batch-summary.json to target the failed inputs.",
        "troubleshooting": _troubleshooting_pointer("#failure-class-batch-partial-failure"),
    },
}


def build_failure_payload(failure_class: str, *, mode: str, detail: str) -> dict[str, Any]:
    """Return a machine-readable failure payload aligned with the output contract."""

    contract = FAILURE_CLASSES[failure_class]
    return {
        "status": "failed",
        "mode": mode,
        "version": __version__,
        "failure_class": failure_class,
        "recovery_hint": contract["recovery_hint"],
        "troubleshooting": dict(contract["troubleshooting"]),
        "detail": detail,
    }


def _result_list(result: Any, attr_name: str) -> list[Any]:
    value = getattr(result, attr_name, [])
    return list(value or [])


def result_entity_counts(result: Any) -> dict[str, int]:
    """Return deterministic entity counts from a pipeline-style result object."""

    return {
        "candidates": len(_result_list(result, "candidates")),
        "requirements": len(_result_list(result, "requirements")),
        "artifacts": len(_result_list(result, "artifacts")),
    }


def classify_extraction_assessment(result: Any) -> str:
    """Classify the extraction outcome using the stable runtime vocabulary."""

    counts = result_entity_counts(result)
    has_structured_output = any(counts.values())
    has_low_text_warnings = bool(_result_list(result, "warnings"))

    if has_structured_output and has_low_text_warnings:
        return "content_extracted_with_low_text_warnings"
    if has_structured_output:
        return "content_extracted"
    if has_low_text_warnings:
        return "likely_text_layer_issue"
    return "no_structured_content"


def build_dry_run_payload(result: Any, source_pdf: str | Path) -> dict[str, Any]:
    """Return the machine-readable dry-run payload for one source PDF."""

    return {
        "source": str(source_pdf),
        "warnings": [warning.to_dict() for warning in _result_list(result, "warnings")],
        "candidate_count": len(_result_list(result, "candidates")),
        "artifact_count": len(_result_list(result, "artifacts")),
        "taxonomy_version": getattr(result, "metadata", {}).get("taxonomy_version", "unknown"),
        "extraction_assessment": classify_extraction_assessment(result),
    }


def build_batch_success_item(
    source_pdf: str | Path,
    result: Any,
    *,
    planned_output_dir: str | Path,
    package_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the success item payload for one batch entry."""

    item = {
        "source": str(source_pdf),
        "planned_output_dir": str(Path(planned_output_dir).absolute()),
        "status": "ok",
        "output_dir": None,
        "generated_files": None,
        "manifest_path": None,
        "manifest_version": None,
        "warning_count": len(_result_list(result, "warnings")),
        "entity_counts": result_entity_counts(result),
        "extraction_assessment": classify_extraction_assessment(result),
        "failure_class": None,
        "detail": None,
    }
    if package_summary is not None:
        item.update(
            {
                "output_dir": package_summary["output_dir"],
                "generated_files": package_summary["generated_files"],
                "manifest_path": package_summary["manifest_path"],
                "manifest_version": package_summary["manifest_version"],
            }
        )
    return item


def build_batch_failure_item(
    source_pdf: str | Path,
    planned_output_dir: str | Path,
    *,
    failure_class: str,
    detail: str,
) -> dict[str, Any]:
    """Return the failure item payload for one batch entry."""

    return {
        "source": str(source_pdf),
        "planned_output_dir": str(Path(planned_output_dir).absolute()),
        "status": "failed",
        "output_dir": None,
        "generated_files": None,
        "manifest_path": None,
        "manifest_version": None,
        "warning_count": 0,
        "entity_counts": {"candidates": 0, "requirements": 0, "artifacts": 0},
        "extraction_assessment": None,
        "failure_class": failure_class,
        "detail": detail,
    }


def summarize_batch_items(
    items: list[dict[str, Any]],
    *,
    batch_root: str | Path,
    dry_run: bool,
) -> dict[str, Any]:
    """Build the aggregate batch summary payload."""

    succeeded = sum(1 for item in items if item["status"] == "ok")
    failed = sum(1 for item in items if item["status"] == "failed")

    return {
        "status": "ok" if failed == 0 else "partial_failure",
        "mode": "batch-dry-run" if dry_run else "batch",
        "version": __version__,
        "dry_run": dry_run,
        "batch_root": str(Path(batch_root).absolute()),
        "summary_path": None,
        "batch_summary_file": BATCH_SUMMARY_FILE,
        "items": items,
        "totals": {
            "sources": len(items),
            "succeeded": succeeded,
            "failed": failed,
            "warnings": sum(item["warning_count"] for item in items),
            "candidates": sum(item["entity_counts"]["candidates"] for item in items),
            "requirements": sum(item["entity_counts"]["requirements"] for item in items),
            "artifacts": sum(item["entity_counts"]["artifacts"] for item in items),
        },
    }


def write_batch_summary(summary: dict[str, Any], batch_root: str | Path) -> Path:
    """Write batch-summary.json in the batch root and return the created path."""

    batch_root_path = Path(batch_root)
    batch_root_path.mkdir(parents=True, exist_ok=True)
    summary_path = batch_root_path / BATCH_SUMMARY_FILE
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary_path


def build_example_result() -> PipelineResult:
    """Construct a deterministic example result for automation and docs."""

    warnings = [
        QualityWarning(
            code="low_text_quality",
            page=3,
            chars=12,
            message="Low text-layer quality detected; extraction continues but output may be incomplete.",
        )
    ]
    candidates = [
        Candidate(
            id="cand-narrative-001-001-example",
            text="The Flight Software shall publish health telemetry once per second.",
            source_type="narrative_text",
            page=2,
            classification="requirement",
        ),
        Candidate(
            id="cand-caption-003-001-example",
            text="A scanned appendix may require manual review.",
            source_type="caption_context",
            page=3,
            classification="neutral",
            flags=["review"],
        ),
    ]
    requirements = [
        Requirement(
            id="EX-REQ-001",
            text="The Flight Software shall publish health telemetry once per second.",
            obligation="shall",
            page=2,
            source_type="narrative_text",
            interop=InteropMetadata(candidate_concept="HealthTelemetry"),
        )
    ]
    artifacts = [
        ArtifactBlock(
            id="art-001-example",
            section="System Overview",
            content="The system includes flight software, a telemetry bus, and an operator console.",
            page=1,
            interop=InteropMetadata(candidate_concept="SystemOverview"),
        )
    ]
    metadata = {
        "source_pdf": "example-spec.pdf",
        "taxonomy_version": "2026.02",
        "obligation_verbs": [
            "may",
            "must",
            "optional",
            "recommended",
            "required",
            "shall",
            "should",
        ],
        "mode": "example-output",
    }

    return PipelineResult(
        warnings=warnings,
        candidates=candidates,
        requirements=requirements,
        artifacts=artifacts,
        metadata=metadata,
    )


def write_output_package(result: PipelineResult, output_dir: str | Path) -> dict[str, Any]:
    """Write the standard output package and return a machine-readable summary."""

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    renderer = MarkdownRenderer(result)
    (target_dir / FILE_MAPPING["full"]).write_text(renderer.render_full(), encoding="utf-8")
    (target_dir / FILE_MAPPING["requirements"]).write_text(
        renderer.render_requirements(),
        encoding="utf-8",
    )
    (target_dir / FILE_MAPPING["architecture"]).write_text(
        renderer.render_architecture(),
        encoding="utf-8",
    )

    manifest_writer = ManifestWriter(result, dict(FILE_MAPPING))
    manifest_path = manifest_writer.write(target_dir / FILE_MAPPING["manifest"])

    return {
        "output_dir": str(target_dir.absolute()),
        "generated_files": {
            key: str((target_dir / filename).absolute())
            for key, filename in FILE_MAPPING.items()
        },
        "file_names": dict(FILE_MAPPING),
        "manifest_path": str(manifest_path.absolute()),
        "manifest_version": Manifest.model_fields["manifest_version"].default,
        "entity_counts": {
            **result_entity_counts(result),
        },
        "warning_count": len(_result_list(result, "warnings")),
        "source_pdf": str(result.metadata.get("source_pdf", "unknown")),
    }


def describe_output_contract() -> dict[str, Any]:
    """Return a machine-readable output contract for automation clients."""

    return {
        "tool": "specforge-distill",
        "version": __version__,
        "input_contract": {
            "primary_input": "one or more digital-text PDF paths",
            "default_output_directory_pattern": "<source-stem>_distilled",
            "batch_default_output_root_pattern": "specforge_distill_batch_output/",
            "batch_summary_file": BATCH_SUMMARY_FILE,
            "special_modes": [
                "--describe-output json",
                "--emit-example-output <dir>",
                "--self-test",
            ],
        },
        "cli_contract": {
            "flags": CLI_FLAGS,
            "invocation_modes": INVOCATION_MODES,
            "response_schemas": {
                "dry-run": DRY_RUN_SCHEMA,
                "batch-summary": BATCH_SUMMARY_SCHEMA,
                "example-output": EXAMPLE_OUTPUT_SCHEMA,
                "self-test": SELF_TEST_SCHEMA,
            },
        },
        "output_contract": {
            "generated_files": dict(FILE_MAPPING),
            "batch_summary_file": BATCH_SUMMARY_FILE,
            "markdown_files": {
                "full.md": "Consolidated document view with warnings, architecture, and requirements.",
                "requirements.md": "Requirement-only Markdown with IDs, obligation, and page citations.",
                "architecture.md": "Architecture/context Markdown blocks with deterministic artifact IDs.",
                "manifest.json": "Machine-readable index of generated files and extracted entities.",
            },
            "manifest_version": Manifest.model_fields["manifest_version"].default,
            "manifest_schema": Manifest.model_json_schema(),
            "dry_run_schema": DRY_RUN_SCHEMA,
            "batch_summary_schema": BATCH_SUMMARY_SCHEMA,
            "entity_types": ["requirement", "artifact"],
        },
        "failure_classes": FAILURE_CLASSES,
        "exit_codes": EXIT_CODES,
    }


def emit_example_output(output_dir: str | Path) -> dict[str, Any]:
    """Write a canonical example output package for clients to inspect."""

    summary = write_output_package(build_example_result(), output_dir)
    return {
        "status": "ok",
        "mode": "example-output",
        "version": __version__,
        **summary,
    }


def _validate_check(checks: list[dict[str, str]], *, name: str, ok: bool, detail: str) -> None:
    checks.append({"name": name, "status": "ok" if ok else "failed", "detail": detail})
    if not ok:
        raise RuntimeError(detail)


def _run_self_test_in_dir(output_dir: Path, *, preserved_output: bool) -> dict[str, Any]:
    example = build_example_result()
    summary = write_output_package(example, output_dir)

    manifest_path = Path(summary["manifest_path"])
    manifest = Manifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    requirements_md = Path(summary["generated_files"]["requirements"]).read_text(encoding="utf-8")
    architecture_md = Path(summary["generated_files"]["architecture"]).read_text(encoding="utf-8")

    checks: list[dict[str, str]] = []
    _validate_check(
        checks,
        name="output_files_exist",
        ok=all(Path(path).exists() for path in summary["generated_files"].values()),
        detail="Expected output files were written.",
    )
    _validate_check(
        checks,
        name="manifest_validates",
        ok=manifest.manifest_version == Manifest.model_fields["manifest_version"].default,
        detail="manifest.json validates against the bundled Pydantic schema.",
    )
    _validate_check(
        checks,
        name="requirements_markdown_contains_example_id",
        ok="EX-REQ-001" in requirements_md,
        detail="requirements.md contains the canonical example requirement.",
    )
    _validate_check(
        checks,
        name="architecture_markdown_contains_example_artifact",
        ok="art-001-example" in architecture_md,
        detail="architecture.md contains the canonical example artifact.",
    )

    return {
        "status": "ok",
        "mode": "self-test",
        "version": __version__,
        "preserved_output": preserved_output,
        "output_dir": summary["output_dir"] if preserved_output else None,
        "manifest_version": manifest.manifest_version,
        "entity_counts": summary["entity_counts"],
        "checks": checks,
    }


def run_self_test(output_dir: str | Path | None = None) -> dict[str, Any]:
    """Run a built-in deterministic verification of output generation."""

    if output_dir is not None:
        return _run_self_test_in_dir(Path(output_dir), preserved_output=True)

    with TemporaryDirectory(prefix="specforge-distill-self-test-") as temp_dir:
        return _run_self_test_in_dir(Path(temp_dir), preserved_output=False)
