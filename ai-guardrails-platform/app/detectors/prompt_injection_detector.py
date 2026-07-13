INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "reveal system prompt",
    "bypass safety",
    "pretend to be unrestricted"
]

def detect_prompt_injection(text):

    text = text.lower()

    for pattern in INJECTION_PATTERNS:

        if pattern in text:
            return True

    return False