from __future__ import annotations

from functools import lru_cache
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from specforge_distill.models.candidates import Candidate
    from specforge_distill.models.requirement import Requirement


@dataclass(frozen=True)
class ObligationTaxonomy:
    """Runtime obligation taxonomy loaded from external config."""

    version: str
    verbs: tuple[str, ...]
    taxonomy_dict: Dict[str, list[str]]


DEFAULT_TAXONOMY_PATH = Path(__file__).resolve().parent / "config" / "obligation_verbs.yml"
DEFAULT_TAXONOMY_RESOURCE = "obligation_verbs.yml"


def _parse_basic_yaml(text: str) -> dict[str, Any]:
    """Simple parser for the small taxonomy format used by this project."""

    data: dict[str, Any] = {}
    current_list_key: str | None = None
    current_section: str | None = None

    for raw_line in text.splitlines():
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("-"):
            if current_list_key is None:
                continue
            item = line[1:].strip().strip('"').strip("'")
            if current_section is not None:
                section = data.setdefault(current_section, {})
                assert isinstance(section, dict)
                section.setdefault(current_list_key, []).append(item)
            else:
                data.setdefault(current_list_key, []).append(item)
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", maxsplit=1)
        key = key.strip()
        value = value.strip()

        if value:
            if indent and current_section is not None:
                section = data.setdefault(current_section, {})
                assert isinstance(section, dict)
                section[key] = value.strip('"').strip("'")
            else:
                data[key] = value.strip('"').strip("'")
                current_section = None
            current_list_key = None
        else:
            if indent == 0:
                if key == "taxonomy":
                    data[key] = {}
                    current_section = key
                    current_list_key = None
                else:
                    data[key] = []
                    current_section = None
                    current_list_key = key
            else:
                if current_section is None:
                    data[key] = []
                else:
                    section = data.setdefault(current_section, {})
                    assert isinstance(section, dict)
                    section[key] = []
                current_list_key = key

    return data


def _read_taxonomy_payload(taxonomy_path: str | Path | None = None) -> str:
    """Load taxonomy text from an explicit path or bundled package data."""

    if taxonomy_path is not None:
        return Path(taxonomy_path).read_text(encoding="utf-8")

    try:
        return (
            resources.files("specforge_distill.config")
            .joinpath(DEFAULT_TAXONOMY_RESOURCE)
            .read_text(encoding="utf-8")
        )
    except Exception:
        # Fall back to a filesystem path for editable installs and unusual runtimes.
        return DEFAULT_TAXONOMY_PATH.read_text(encoding="utf-8")


def _normalize_taxonomy_path(taxonomy_path: str | Path | None) -> str | None:
    if taxonomy_path is None:
        return None
    return str(Path(taxonomy_path).resolve())


@lru_cache(maxsize=8)
def _load_obligation_taxonomy_cached(normalized_path: str | None) -> ObligationTaxonomy:
    payload = _read_taxonomy_payload(normalized_path)
    parsed: dict[str, Any]
    parsed = _parse_basic_yaml(payload)

    version = str(parsed.get("version", "unknown"))

    taxonomy_dict: Dict[str, list[str]] = {
        "shall": ["shall", "must", "required"],
        "should": ["should", "recommended"],
        "may": ["may", "optional"],
    }

    verbs_list = []
    if "taxonomy" in parsed and isinstance(parsed["taxonomy"], dict):
        # Merge YAML taxonomy over defaults
        for level, verbs in parsed["taxonomy"].items():
            if isinstance(verbs, list):
                taxonomy_dict[level] = sorted(list(set(verbs)))
                verbs_list.extend(verbs)
    elif "obligation_verbs" in parsed and isinstance(parsed["obligation_verbs"], list):
        verbs_list = parsed["obligation_verbs"]
        taxonomy_dict["shall"] = sorted(list(set(taxonomy_dict["shall"] + verbs_list)))

    canonical_verbs = tuple(sorted({str(verb).strip().lower() for verb in verbs_list if str(verb).strip()}))
    return ObligationTaxonomy(version=version, verbs=canonical_verbs, taxonomy_dict=taxonomy_dict)


def load_obligation_taxonomy(taxonomy_path: str | Path | None = None) -> ObligationTaxonomy:
    """Load obligation verbs from external config with version metadata."""

    return _load_obligation_taxonomy_cached(_normalize_taxonomy_path(taxonomy_path))


def normalize_requirements(
    candidates: list["Candidate"],
    taxonomy_dict: Dict[str, list[str]],
) -> list["Requirement"]:
    """Transform extraction candidates into formal normalized Requirement records."""
    from specforge_distill.extract.classifier import enrich_requirement
    from specforge_distill.extract.id_resolver import resolve_requirement_id
    from specforge_distill.models.requirement import Requirement

    requirements = []
    processed_texts = set()
    from specforge_distill.models.candidates import normalize_text

    for cand in candidates:
        # Deduplication: skip if we've already processed this semantic content
        norm_text = normalize_text(cand.text)
        if norm_text in processed_texts:
            continue
        
        # 1. Create Requirement model
        req = Requirement.from_candidate(cand)
        
        # 2. Resolve ID (preserving source or generating stable hash)
        req_id, is_source_id = resolve_requirement_id(cand.text, cand.page, cand.source_type)
        req.id = req_id
        req.is_generated_id = not is_source_id
        
        # Parse VCRM matrix attributes if context flag is present
        if "vcrm_context" in cand.flags:
            parts = [p.strip() for p in cand.text.split("|")]
            if len(parts) > 0:
                req.text = parts[0]
            if len(parts) > 1:
                req.vcrm.method = parts[1]
            if len(parts) > 2:
                req.vcrm.rationale = parts[2]
        
        # 3. Classify obligation and detect ambiguity
        enrich_requirement(req, taxonomy_dict)
        
        requirements.append(req)
        processed_texts.add(norm_text)
        
    return requirements
