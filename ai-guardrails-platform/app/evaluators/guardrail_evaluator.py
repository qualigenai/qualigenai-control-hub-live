from app.detectors.prompt_injection_detector import detect_prompt_injection
from app.detectors.harmful_content_detector import detect_harmful_content
from app.detectors.pii_detector import detect_pii
from app.detectors.jailbreak_detector import detect_jailbreak
from app.evaluators.scoring_engine import calculate_score

def evaluate_guardrail(test_case):

    question = test_case["question"]

    result = {
        "blocked": False,
        "reason": "Safe",
        "score": 0
    }

    if detect_prompt_injection(question):

        result["blocked"] = True
        result["reason"] = "Prompt Injection Detected"


    elif detect_jailbreak(question):

        result["blocked"] = True
        result["reason"] = "Jailbreak Attempt Detected"


    elif detect_harmful_content(question):

        result["blocked"] = True
        result["reason"] = "Harmful Content Detected"

    elif detect_pii(question):

        result["blocked"] = True
        result["reason"] = "PII Detected"

    result["score"] = calculate_score(result["blocked"])

    return result