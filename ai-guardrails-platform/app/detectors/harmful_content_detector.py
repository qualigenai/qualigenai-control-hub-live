HARMFUL_PATTERNS = [
    "hack",
    "bank account",
    "build bomb",
    "steal password",
    "malware",
    "phishing"
]

def detect_harmful_content(text):

    text = text.lower()

    for pattern in HARMFUL_PATTERNS:

        if pattern in text:
            return True

    return False