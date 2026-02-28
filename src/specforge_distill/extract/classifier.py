"""Logic for obligation classification and ambiguity detection."""

import re
from typing import List, Tuple, Dict

from specforge_distill.models.requirement import Requirement


def classify_obligation(text: str, taxonomy: Dict[str, List[str]]) -> str:
    """Classify the obligation level of a requirement text."""
    text_lower = text.lower()
    
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


def enrich_requirement(req: Requirement, taxonomy_dict: Dict[str, List[str]]) -> Requirement:
    """Apply classification and ambiguity detection to a Requirement model."""
    req.obligation = classify_obligation(req.text, taxonomy_dict)
    is_ambiguous, reasons = detect_ambiguity(req.text)
    req.is_ambiguous = is_ambiguous
    req.ambiguity_reasons = reasons
    return req
