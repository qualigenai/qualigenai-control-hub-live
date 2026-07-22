import json
import requests

def run_reliability_engine(service_url: str, internal_key: str) -> dict:
    """
    Calls the Reliability Engine's own HTTP service (POST /run) instead of
    launching it as a subprocess. Same return shape as before, so callers
    don't need to change.
    """
    try:
        response = requests.post(
            f"{service_url}/run",
            headers={"X-Internal-Key": internal_key},
            timeout=300,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"ok": False, "error": f"Could not reach reliability engine service: {e}"}

def run_guardrails_platform(service_url: str, internal_key: str) -> dict:
    """
    Calls the Guardrails Platform's own HTTP service (POST /run) instead of
    launching it as a subprocess.
    """
    try:
        response = requests.post(
            f"{service_url}/run",
            headers={"X-Internal-Key": internal_key},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"ok": False, "error": f"Could not reach guardrails platform service: {e}"}

def run_pilgrim_bot_reliability(service_url: str, internal_key: str) -> dict:
    """
    Calls the Pilgrim Bot's own /internal/reliability-check endpoint.
    This one's slow (real LLM calls with rate-limit pauses), so the
    timeout is generous.
    """
    try:
        response = requests.post(
            f"{service_url}/internal/reliability-check",
            headers={"X-Internal-Key": internal_key},
            timeout=180,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"ok": False, "error": f"Could not reach Pilgrim Bot service: {e}"}


def check_prompt_via_service(service_url: str, internal_key: str) -> dict:
    """
    Calls a service's own /internal/prompt-check endpoint. Works for both
    RAG (single prompt) and Pilgrim Bot (three prompts) — each service
    reports its own result shape, we just relay whatever comes back.
    """
    try:
        response = requests.post(
            f"{service_url}/internal/prompt-check",
            headers={"X-Internal-Key": internal_key},
            timeout=30,
        )
        response.raise_for_status()
        return {"ok": True, **response.json()}
    except requests.RequestException as e:
        return {"ok": False, "error": f"Could not reach service: {e}"}


def write_run_to_observability(service_url: str, internal_key: str, target_project: str,
                                 reliability_result: dict, guardrail_result: dict) -> dict:
    """
    Reports one real Control Hub run to the Observability Platform's own
    /telemetry/trace endpoint, instead of writing to DuckDB directly.
    """
    reliability_summary = (
        reliability_result.get("report", {}).get("summary", {})
        if reliability_result.get("ok") else {}
    )
    guardrail_report = guardrail_result.get("report", {}) if guardrail_result.get("ok") else {}

    avg_score = reliability_summary.get("average_score")
    total_guard = guardrail_report.get("total_tests", 0)
    blocked_guard = guardrail_report.get("blocked", 0)
    policy_violated = guardrail_result.get("ok", False) and (blocked_guard < total_guard)

    payload = {
        "model_name": "control-hub-run",
        "prompt_text": f"Control Hub launch for {target_project}",
        "response_text": "see metadata field for full result",
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "latency_ms": 0.0,
        "guardrails": {
            "policy_violated": policy_violated,
            "violation_type": None if total_guard == 0 else f"{blocked_guard}/{total_guard} blocked",
            "action_taken": "logged",
        },
        "reliability": {
            "hallucination_score": avg_score,
            "groundedness_score": None,
            "retrieval_precision": None,
        },
        "metadata": {
            "target_project": target_project,
            "reliability": reliability_result,
            "guardrails": guardrail_result,
        },
    }

    try:
        response = requests.post(
            f"{service_url}/api/v1/telemetry/trace",
            headers={"X-Internal-Key": internal_key},
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return {"ok": True, "trace_id": data.get("trace_id")}
    except requests.RequestException as e:
        return {"ok": False, "error": f"Could not reach observability service: {e}"}


def get_model_registry(service_url: str, internal_key: str) -> dict:
    try:
        response = requests.get(
            f"{service_url}/api/v1/analytics/registry/models",
            headers={"X-Internal-Key": internal_key},
            timeout=15,
        )
        response.raise_for_status()
        return {"ok": True, "models": response.json().get("models", [])}
    except requests.RequestException as e:
        return {"ok": False, "error": str(e)}


def get_prompt_history(service_url: str, internal_key: str) -> dict:
    try:
        response = requests.get(
            f"{service_url}/api/v1/prompts/history",
            headers={"X-Internal-Key": internal_key},
            timeout=15,
        )
        response.raise_for_status()
        return {"ok": True, "history": response.json().get("history", [])}
    except requests.RequestException as e:
        return {"ok": False, "error": str(e)}


def get_control_hub_summary(service_url: str, internal_key: str) -> dict:
    try:
        response = requests.get(
            f"{service_url}/api/v1/analytics/control-hub-summary",
            headers={"X-Internal-Key": internal_key},
            timeout=15,
        )
        response.raise_for_status()
        return {"ok": True, **response.json()}
    except requests.RequestException as e:
        return {"ok": False, "error": str(e)}


def get_latest_run(service_url: str, internal_key: str, target_project: str) -> dict:
    try:
        response = requests.get(
            f"{service_url}/api/v1/analytics/latest-run",
            headers={"X-Internal-Key": internal_key},
            params={"target_project": target_project},
            timeout=15,
        )
        response.raise_for_status()
        return {"ok": True, **response.json()}
    except requests.RequestException as e:
        return {"ok": False, "error": str(e)}


def get_latest_guardrail(service_url: str, internal_key: str) -> dict:
    try:
        response = requests.get(
            f"{service_url}/api/v1/analytics/latest-guardrail",
            headers={"X-Internal-Key": internal_key},
            timeout=15,
        )
        response.raise_for_status()
        return {"ok": True, **response.json()}
    except requests.RequestException as e:
        return {"ok": False, "error": str(e)}