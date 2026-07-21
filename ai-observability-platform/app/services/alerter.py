# app/services/alerter.py
import httpx
import os
import asyncio
from typing import Dict, Any, Optional


class AlerterService:
    # Threshold Configuration Boundaries
    LATENCY_SLA_MS: float = 2500.0
    HALLUCINATION_MAX_THRESHOLD: float = 0.50

    # Secure acquisition of your target channel routing webhook URL from environment parameters
    # Uses a placeholder string if no active .env parameter is initialized
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/mock/placeholder/url")

    @classmethod
    def evaluate_trace_thresholds(cls, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluates a single telemetry trace against enterprise operational SLA bounds.
        Triggers internal and external alert dispatch flows if anomalies are present.
        """
        latency = payload.get("latency_ms", 0.0)
        model_name = payload.get("model_name", "unknown")
        trace_id = payload.get("trace_id", "unknown")

        guardrails = payload.get("guardrails") or {}
        reliability = payload.get("reliability") or {}

        policy_violated = guardrails.get("policy_violated", False)
        hallucination_score = reliability.get("hallucination_score")

        alert_triggered = False
        breach_reasons = []

        if latency > cls.LATENCY_SLA_MS:
            alert_triggered = True
            breach_reasons.append(f"Latency Violation: Execution took {latency}ms (SLA Max: {cls.LATENCY_SLA_MS}ms)")

        if policy_violated:
            alert_triggered = True
            v_type = guardrails.get("violation_type", "Unspecified Policy")
            action = guardrails.get("action_taken", "flagged")
            breach_reasons.append(f"Security Policy Breach: [{v_type}] encountered. Request was [{action}].")

        if hallucination_score is not None and hallucination_score > cls.HALLUCINATION_MAX_THRESHOLD:
            alert_triggered = True
            breach_reasons.append(
                f"Reliability Degradation: Hallucination score hit {hallucination_score} (Max Allowable: {cls.HALLUCINATION_MAX_THRESHOLD})")

        if alert_triggered:
            incident_report = {
                "incident_id": f"INC-{trace_id[:8].upper()}",
                "trace_id": trace_id,
                "target_model": model_name,
                "severity": "CRITICAL" if policy_violated else "WARNING",
                "violations": breach_reasons
            }

            # 1. Output clean context logs onto local console terminal thread
            cls.dispatch_local_log_alert(incident_report)

            # 2. Fire and forget an external webhook request payload asynchronously
            # safely handling event loop background tasks execution
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(cls.dispatch_external_webhook(incident_report))
                else:
                    asyncio.run(cls.dispatch_external_webhook(incident_report))
            except Exception as e:
                print(f"⚠️ Failed to initialize background alert dispatcher pipeline task: {str(e)}")

            return incident_report

        return None

    @staticmethod
    def dispatch_local_log_alert(incident: Dict[str, Any]):
        print(f"\n🚨 [ALERT TRIGGERED] Operational SLA Breach Detected! ({incident['incident_id']})")
        print(f"   Severity Level : {incident['severity']} | Model: {incident['target_model']}")
        print("-" * 65)

    @classmethod
    async def dispatch_external_webhook(cls, incident: Dict[str, Any]):
        """
        Asynchronously ships structured message payloads to enterprise slack webhook channels.
        Uses rich block formatting parameters to maximize readability.
        """
        # If the parameter remains standard fallback mock url string, skip actual network execution
        if "placeholder/url" in cls.SLACK_WEBHOOK_URL:
            print(f"ℹ️ External webhook dispatch bypassed: SLACK_WEBHOOK_URL is not configured.")
            return

        # Structured enterprise Slack blocks formatting payload blueprint
        slack_payload = {
            "text": f"🚨 {incident['severity']} Incident: Operational SLA Breach Detected",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text",
                             "text": f"🚨 Observability Incident Triggered ({incident['incident_id']})"}
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Severity Level:*\n`{incident['severity']}`"},
                        {"type": "mrkdwn", "text": f"*Target Engine Model:*\n`{incident['target_model']}`"}
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Breach Details Matrix:* \n" + "\n".join([f"• {v}" for v in incident["violations"]])
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {"type": "plain_text", "text": f"System Context Trace ID Link: {incident['trace_id']}"}]
                }
            ]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(cls.SLACK_WEBHOOK_URL, json=slack_payload, timeout=3.0)
                if response.status_code == 200:
                    print(
                        f"📬 Webhook successfully dispatched to enterprise server channel for {incident['incident_id']}.")
                else:
                    print(f"⚠️ Webhook channel rejected alert data. Error Code: {response.status_code}")
        except Exception as e:
            print(f"💥 Failed to route external HTTP request payload alert context: {str(e)}")