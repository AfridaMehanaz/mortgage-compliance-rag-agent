INJECTION_PATTERNS = (
    "ignore previous instructions",
    "disregard the policy",
    "reveal system prompt",
    "override compliance",
    "act as if the rules do not apply",
)


def scan_question(question: str) -> list[str]:
    lowered = question.lower()
    flags = [pattern for pattern in INJECTION_PATTERNS if pattern in lowered]

    if len(question) > 800:
        flags.append("question_too_long")

    return flags

