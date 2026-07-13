import re

def detect_pii(text):

    ssn_pattern = r"\d{3}-\d{2}-\d{4}"

    if re.search(ssn_pattern, text):
        return True

    return False