from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from specforge_distill.extract.classifier import enrich_requirement
from specforge_distill.extract.id_resolver import resolve_requirement_id
from specforge_distill.models.candidates import Candidate
from specforge_distill.models.requirement import Requirement


@dataclass(frozen=True)
class ObligationTaxonomy:
    """Runtime obligation taxonomy loaded from external config."""

    version: str
    verbs: tuple[str, ...]
    taxonomy_dict: Dict[str, list[str]]


DEFAULT_TAXONOMY_PATH = Path(__file__).resolve().parent / "config" / "obligation_verbs.yml"


def _parse_basic_yaml(text: str) -> dict[str, Any]:
    """Simple parser for the small taxonomy format used by this project."""

    data: dict[str, Any] = {}
    current_list_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("-"):
            if current_list_key is None:
                continue
            item = line[1:].strip().strip('"').strip("'")
            data.setdefault(current_list_key, []).append(item)
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", maxsplit=1)
        key = key.strip()
        value = value.strip()

        if value:
            data[key] = value.strip('"').strip("'")
            current_list_key = None
        else:
            data[key] = []
            current_list_key = key

    return data


def load_obligation_taxonomy(taxonomy_path: str | Path | None = None) -> ObligationTaxonomy:
    """Load obligation verbs from external config with version metadata."""

    path = Path(taxonomy_path or DEFAULT_TAXONOMY_PATH)
    payload = path.read_text(encoding="utf-8")

    parsed: dict[str, Any]
    try:
        import yaml  # type: ignore

        maybe = yaml.safe_load(payload)
        parsed = maybe if isinstance(maybe, dict) else {}
    except Exception:
        parsed = _parse_basic_yaml(payload)

    version = str(parsed.get("version", "unknown"))
    
    taxonomy_dict: Dict[str, list[str]] = {
        "shall": ["shall", "must", "required"],
        "should": ["should", "recommended"],
        "may": ["may", "optional"]
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


def normalize_requirements(candidates: list[Candidate], taxonomy_dict: Dict[str, list[str]]) -> list[Requirement]:
    """Transform extraction candidates into formal normalized Requirement records."""
    requirements = []
    for cand in candidates:
        # 1. Create Requirement model
        req = Requirement.from_candidate(cand)
        
        # 2. Resolve ID (preserving source or generating stable hash)
        req.id = resolve_requirement_id(cand.text, cand.page, cand.source_type)
        
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
        
    return requirements
