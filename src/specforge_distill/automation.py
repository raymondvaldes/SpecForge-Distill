"""Machine-readable CLI support for AI and automation consumers."""

from __future__ import annotations

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


FILE_MAPPING = {
    "full": "full.md",
    "requirements": "requirements.md",
    "architecture": "architecture.md",
    "manifest": "manifest.json",
}

EXIT_CODES = {
    "0": "success",
    "2": "invalid invocation or missing input file",
    "3": "pdf processing or output generation failure",
    "4": "self-test validation failure",
}

DRY_RUN_SCHEMA = {
    "type": "object",
    "required": [
        "source",
        "warnings",
        "candidate_count",
        "artifact_count",
        "taxonomy_version",
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
        "description": "Path to the source digital-text PDF for a normal distillation run.",
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
        "description": "Output target for normal distillation, or fallback preserve directory for example/self-test modes.",
    },
    "--dry-run": {
        "kind": "flag",
        "supported_in_modes": ["distill"],
        "stdout_format": "json",
        "stdout_schema": "dry-run",
        "conflicts_with": [
            "--describe-output",
            "--emit-example-output",
            "--self-test",
        ],
        "description": "Run extraction without writing output files and emit a dry-run JSON summary.",
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
        "requires": ["pdf_path"],
        "optional_flags": [
            "--output-dir",
            "--dry-run",
            "--min-chars-per-page",
            "--allow-external-ai",
            "--report",
        ],
        "stdout_modes": ["text", "dry-run"],
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

FAILURE_CLASSES = {
    "invalid_invocation": {
        "exit_code": 2,
        "stderr_format": "plain-text",
        "typical_stderr_prefix": "error:",
        "when_it_happens": [
            "A required PDF path is missing for a normal distillation run.",
            "A special mode is combined with incompatible PDF-processing flags.",
        ],
        "recovery": "Adjust flags to match one invocation mode.",
    },
    "missing_input_file": {
        "exit_code": 2,
        "stderr_format": "plain-text",
        "typical_stderr_prefix": "error: file not found:",
        "when_it_happens": [
            "The provided pdf_path does not exist on disk.",
        ],
        "recovery": "Resolve the path before retrying.",
    },
    "pdf_processing_failure": {
        "exit_code": 3,
        "stderr_format": "plain-text",
        "typical_stderr_prefix": "error: Failed to process PDF.",
        "when_it_happens": [
            "The PDF is corrupted, encrypted, malformed, or otherwise unsupported by the extractor.",
            "Output generation fails after the pipeline starts.",
        ],
        "recovery": "Inspect stderr details and retry with a known-good digital-text PDF.",
    },
    "self_test_validation_failure": {
        "exit_code": 4,
        "stderr_format": "json",
        "stderr_shape": {
            "status": "failed",
            "mode": "self-test",
            "version": "<tool version>",
            "detail": "<validation error>",
        },
        "when_it_happens": [
            "The built-in deterministic self-test cannot write or validate the canonical output package.",
        ],
        "recovery": "Treat the installation or runtime environment as unhealthy until the self-test passes.",
    },
}


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
            "candidates": len(result.candidates),
            "requirements": len(result.requirements),
            "artifacts": len(result.artifacts),
        },
        "warning_count": len(result.warnings),
        "source_pdf": str(result.metadata.get("source_pdf", "unknown")),
    }


def describe_output_contract() -> dict[str, Any]:
    """Return a machine-readable output contract for automation clients."""

    return {
        "tool": "specforge-distill",
        "version": __version__,
        "input_contract": {
            "primary_input": "digital-text PDF path",
            "default_output_directory_pattern": "<source-stem>_distilled",
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
                "example-output": EXAMPLE_OUTPUT_SCHEMA,
                "self-test": SELF_TEST_SCHEMA,
            },
        },
        "output_contract": {
            "generated_files": dict(FILE_MAPPING),
            "markdown_files": {
                "full.md": "Consolidated document view with warnings, architecture, and requirements.",
                "requirements.md": "Requirement-only Markdown with IDs, obligation, and page citations.",
                "architecture.md": "Architecture/context Markdown blocks with deterministic artifact IDs.",
                "manifest.json": "Machine-readable index of generated files and extracted entities.",
            },
            "manifest_version": Manifest.model_fields["manifest_version"].default,
            "manifest_schema": Manifest.model_json_schema(),
            "dry_run_schema": DRY_RUN_SCHEMA,
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
