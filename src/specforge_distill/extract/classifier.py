"""Logic for obligation classification and ambiguity detection."""

import re
import yaml
from pathlib import Path
from typing import List, Tuple, Dict, Any

from specforge_distill.models.requirement import Requirement


def load_verbs() -> Dict[str, List[str]]:
    """Load obligation verb taxonomy from config."""
    config_path = Path(__file__).parent.parent / "config" / "obligation_verbs.yml"
    try:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
            # Default taxonomy structure
            taxonomy = {
                "shall": ["shall", "must", "required"],
                "should": ["should", "recommended"],
                "may": ["may", "optional"]
            }
            
            # Use data from YAML if available to override/augment
            if data and "obligation_verbs" in data:
                # For v1, we map everything in the list to 'shall' if not specified otherwise
                # Future versions could have a more complex YAML structure
                taxonomy["shall"] = list(set(taxonomy["shall"] + data["obligation_verbs"]))
                
            return taxonomy
    except Exception:
        # Fallback to hardcoded defaults if file missing or broken
        return {
            "shall": ["shall", "must", "required"],
            "should": ["should", "recommended"],
            "may": ["may", "optional"]
        }


def classify_obligation(text: str) -> str:
    """Classify the obligation level of a requirement text."""
    text_lower = text.lower()
    taxonomy = load_verbs()
    
    for level, verbs in taxonomy.items():
        for verb in verbs:
            # Use word boundaries to avoid matching within other words
            if re.search(rf"\b{re.escape(verb)}\b", text_lower):
                return level
                
    return "neutral"


def detect_ambiguity(text: str) -> Tuple[bool, List[str]]:
    """Detect common requirement ambiguity patterns."""
    reasons = []
    text_lower = text.lower()
    
    # 1. Passive voice patterns (basic)
    passive_patterns = [
        r"\bbe done\b",
        r"\bwill be\b",
        r"\bis to be\b",
        r"\bshall be\b (?!\w+ed\b)", # shall be + not-past-participle (oversimplified)
    ]
    if any(re.search(p, text_lower) for p in passive_patterns):
        reasons.append("passive_voice")
        
    # 2. Vague quantifiers
    vague_words = [
        "fast", "easy", "efficient", "user-friendly", "flexible", 
        "minimize", "maximize", "optimize", "adequate", "appropriate",
        "etc", "including but not limited to"
    ]
    for word in vague_words:
        if re.search(rf"\b{re.escape(word)}\b", text_lower):
            reasons.append(f"vague_word:{word}")
            
    # 3. TBD/Low confidence markers
    confidence_markers = ["tbd", "tbr", "tbc", "to be determined", "to be confirmed"]
    for marker in confidence_markers:
        if re.search(rf"\b{re.escape(marker)}\b", text_lower):
            reasons.append(f"low_confidence:{marker}")
            
    return len(reasons) > 0, reasons


def enrich_requirement(req: Requirement) -> Requirement:
    """Apply classification and ambiguity detection to a Requirement model."""
    req.obligation = classify_obligation(req.text)
    is_ambiguous, reasons = detect_ambiguity(req.text)
    req.is_ambiguous = is_ambiguous
    req.ambiguity_reasons = reasons
    return req
