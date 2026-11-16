import re
import unicodedata


REFUSAL = (
    "I can't help with that topic. "
    "I can help you explore Ottawa attractions, weather, and day plans."
)

RESTRICTED_PATTERNS = [
    r"\b(?:cats?|dogs?|kittens?|pupp(?:y|ies))\b",
    r"\bhoroscopes?\b",
    r"\bzodiac\b",
    r"\bastrology\b",
    r"\btaylor\s+swift\b",
]


def contains_restricted_topic(text: str) -> bool:
    """Check for explicit mentions of the assignment's restricted topics."""
    normalized = unicodedata.normalize("NFKC", text).casefold()

    return any(
        re.search(pattern, normalized)
        for pattern in RESTRICTED_PATTERNS
    )


INSTRUCTION_PATTERNS = [
    # Requests referring to hidden or system instructions.
    r"\b(?:system|developer|hidden|internal)\s+"
    r"(?:prompt|message|instructions?|rules?)\b",

    # Common attempts to override earlier instructions.
    r"\b(?:ignore|disregard|forget|override)\b.{0,80}"
    r"\b(?:instructions?|rules?|prompts?)\b",

    # Requests to disclose or replace the assistant's instructions.
    r"\b(?:show|reveal|print|repeat|display|replace|rewrite|change)\b"
    r".{0,80}\byour\s+(?:instructions?|rules?|prompts?)\b",
]


def is_instruction_attack(text: str) -> bool:
    """Detect common requests to expose or override system instructions."""
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = " ".join(normalized.split())

    return any(
        re.search(pattern, normalized)
        for pattern in INSTRUCTION_PATTERNS
    )


def is_blocked_input(text: str) -> bool:
    """Combine our input checks in one place."""
    return (
        contains_restricted_topic(text)
        or is_instruction_attack(text)
    )