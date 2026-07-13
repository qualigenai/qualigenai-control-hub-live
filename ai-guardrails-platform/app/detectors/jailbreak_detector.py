JAILBREAK_PATTERNS = [
    "unrestricted ai",
    "bypass safety",
    "ignore safeguards",
    "developer mode"
]

def detect_jailbreak(text):

    text = text.lower()

    for pattern in JAILBREAK_PATTERNS:

        if pattern in text:
            return True

    return False