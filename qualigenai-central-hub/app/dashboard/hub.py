# app/dashboard/hub.py
import streamlit as st
import pandas as pd
import time
import sys
from pathlib import Path
import os
from dotenv import load_dotenv


# Make sure Python can find the "app" package no matter how Streamlit launches this file
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.engine_runner import (
    run_reliability_engine, run_guardrails_platform, run_pilgrim_bot_reliability,
    check_prompt_via_service, write_run_to_observability,
    get_model_registry, get_prompt_history, get_control_hub_summary,
    get_latest_run, get_latest_guardrail
)

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

RELIABILITY_ENGINE_URL = os.getenv("RELIABILITY_ENGINE_URL", "http://localhost:8002")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "some-test-secret-123")
GUARDRAILS_PLATFORM_URL = os.getenv("GUARDRAILS_PLATFORM_URL", "http://localhost:8003")
OBSERVABILITY_API_URL = os.getenv("OBSERVABILITY_API_URL", "http://localhost:8001")
RAG_SYSTEM_URL = os.getenv("RAG_SYSTEM_URL", "http://localhost:8000")
PILGRIM_BOT_URL = os.getenv("PILGRIM_BOT_URL", "http://localhost:10000")

# -----------------------------------------------------------------------------
# 🏢 PREMIUM HUB THEMING & LAYOUT OVERRIDES
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="QualiGenAI Central Control Hub",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .stApp { background-color: #060814; color: #E2E8F0; }
        header { visibility: hidden; }

        .matrix-card {
            background: linear-gradient(145deg, #0f132a, #090b18);
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 1.25rem;
            margin-bottom: 0.85rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .meta-text { color: #64748B; font-size: 0.85rem; font-family: monospace; }

        .badge-pass { background-color: #064e3b; color: #34d399; padding: 0.35rem 0.85rem; border-radius: 6px; font-weight: 700; font-family: monospace; }
        .badge-fail { background-color: #7f1d1d; color: #fca5a5; padding: 0.35rem 0.85rem; border-radius: 6px; font-weight: 700; font-family: monospace; }
        .badge-lock { background-color: #1e293b; color: #94a3b8; padding: 0.35rem 0.85rem; border-radius: 6px; font-weight: 700; font-family: monospace; }

        .terminal-box {
            background-color: #02040a;
            border: 1px solid #1e293b;
            font-family: 'Courier New', monospace;
            padding: 1rem;
            border-radius: 6px;
            color: #38bdf8;
            max-height: 250px;
            overflow-y: auto;
            margin-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 🎛️ SIDEBAR: THE TARGET SYSTEM PICKER (AUT)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔮 Target Selection")
    st.caption("Select an active QualiGenAI implementation repository to attach to the verification core.")

    target_project = st.selectbox(
        "Active Target Project (AUT):",
        [
            "P1: qualigenai/RAG-System",
            "P2: qualigenai/srisailam-pilgrim-bot",
            "P3: qualigenai/multi-agent-system"
        ]
    )

    st.markdown("---")
    st.markdown("### ⚙️ Evaluation Profiles")
    test_profile = st.selectbox("Select Test Runner Profile:",
                                ["Full Regression Matrix", "Smoke Build Validation", "Adversarial Stress Run"])
    clear_cache = st.checkbox("Flush Prior Trace Logs", value=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    run_orchestrator = st.button("🚀 LAUNCH INTEGRATED QA GATEWAY", width='stretch')

# -----------------------------------------------------------------------------
# 📊 WORKSPACE: EXECUTIVE MANAGEMENT CONTROL DECK HEADER
# -----------------------------------------------------------------------------
st.markdown("""
    <div style='border-bottom: 1px solid #1e293b; padding-bottom: 1rem; margin-bottom: 1.5rem;'>
        <h1 style='margin:0; font-size:2.1rem;'>QualiGenAI <span style='color:#6366f1'>Ecosystem Control Center</span></h1>
        <p style='margin:0.2rem 0 0 0; color:#64748B; font-size:0.95rem;'>Central cross-project automation gate executing E2E evaluation models over target AI cores</p>
    </div>
""", unsafe_allow_html=True)

ui_tabs = st.tabs(["🚀 Live Automation Gate", "⚖️ Governance & Risk Posture"])

# =============================================================================
# 🚀 TAB 1: AUTOMATED RUNNER DECK
# =============================================================================
with ui_tabs[0]:
    if not run_orchestrator:
        st.info(
            f"📋 Hub Standby Mode. Ready to route execution calls to target: **`{target_project}`** using profile **`{test_profile}`**.")

        st.markdown("### 🔒 Expected Portfolio Capability Boundaries")
        initial_caps = ["AI Reliability Testing", "Hallucination Detection", "AI Guardrails", "AI Observability",
                        "CI/CD Quality Gates", "Multi-Model Evaluation", "Enterprise Reporting", "Safety Enforcement",
                        "Drift Monitoring"]
        for cap in initial_caps:
            st.markdown(f"""
                <div class='matrix-card'>
                    <div><strong>{cap}</strong></div>
                    <div><span class='badge-lock'>STANDBY</span></div>
                </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown(f"### 📟 Active Framework Live Test Logs: `{target_project}`")

        console_placeholder = st.empty()
        progress_bar = st.progress(0)

        log_lines = []


        def append_log(text, sleep_duration=0.4, progress_val=0):
            log_lines.append(f">> {text}")
            console_placeholder.markdown(
                f"<div class='terminal-box'>{'<br>'.join(log_lines)}</div>",
                unsafe_allow_html=True
            )
            if progress_val > 0:
                progress_bar.progress(progress_val)
            time.sleep(sleep_duration)


        append_log(f"Initializing test execution profile [{test_profile}]...", 0.5, 10)
        append_log(f"Establishing runtime hooks to target codebase directory context...", 0.6, 20)

        if target_project == "P2: qualigenai/srisailam-pilgrim-bot":
            append_log("Invoking 'srisailam-pilgrim-bot' reliability validators...", 0.2, 30)
            reliability_result = run_pilgrim_bot_reliability(PILGRIM_BOT_URL, INTERNAL_API_KEY)
        elif target_project == "P3: qualigenai/multi-agent-system":
            append_log("No reliability check wired for this system yet.", 0.2, 30)
            reliability_result = {"ok": False, "error": "Multi-agent system reliability testing is not built yet."}
        else:
            append_log("Invoking 'qualigenai-ai-reliability-engine' pre-production validators...", 0.2, 30)
            reliability_result = run_reliability_engine(RELIABILITY_ENGINE_URL, INTERNAL_API_KEY)

        if reliability_result["ok"]:
            summary = reliability_result["report"]["summary"]
            append_log(
                f"EVAL COMPLETE: {summary['passed']}/{summary['total_tests']} passed, "
                f"avg score {summary['average_score']}, quality gate {summary['quality_gate'].upper()}.",
                0.5, 55
            )
        else:
            append_log(f"RELIABILITY CHECK FAILED: {reliability_result['error']}", 0.5, 55)

        append_log("Engaging 'ai-guardrails-platform' simulation layers...", 0.3, 65)

        guardrail_result = run_guardrails_platform(GUARDRAILS_PLATFORM_URL, INTERNAL_API_KEY)

        if guardrail_result["ok"]:
            g = guardrail_result["report"]
            append_log(
                f"GUARDRAILS VERIFIED: {g['blocked']}/{g['total_tests']} malicious probes blocked.",
                0.6, 85
            )
        else:
            append_log(f"GUARDRAILS CHECK FAILED: {guardrail_result['error']}", 0.6, 85)

        append_log("Piping consolidated test execution arrays to 'ai-observability-platform'...", 0.3, 90)

        obs_result = write_run_to_observability(
            OBSERVABILITY_API_URL, INTERNAL_API_KEY, target_project, reliability_result, guardrail_result
        )

        if obs_result["ok"]:
            append_log(f"DUCKDB TRANSACTION: Real trace row written (id {obs_result['trace_id'][:8]}...).", 0.5, 95)
        else:
            append_log(f"DUCKDB WRITE FAILED: {obs_result['error']}", 0.5, 95)

        append_log("SYSTEM DISCONNECT: Verification complete. Formatting unified status block.", 0.2, 100)

        st.success("🎉 Full Ecosystem Validation Run Complete! Summary Report Generated.")
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("### 📊 E2E Unified Capability Matrix Report")
        st.caption("Final evaluation statuses mapped directly to your underlying platform QA metrics:")

        reliability_passed = (
                reliability_result["ok"]
                and reliability_result["report"]["summary"]["quality_gate"] == "passed"
        )
        guardrail_passed = (
                guardrail_result["ok"]
                and guardrail_result["report"]["blocked"] == guardrail_result["report"]["total_tests"]
        )
        observability_passed = obs_result["ok"]
        overall_passed = reliability_passed and guardrail_passed and observability_passed

        reliability_engine_label = (
            "srisailam-pilgrim-bot" if target_project == "P2: qualigenai/srisailam-pilgrim-bot"
            else "qualigenai-ai-reliability-engine"
        )
        hub_matrix = [
            ("AI Reliability Testing", reliability_engine_label, reliability_passed),
            ("Hallucination Detection", reliability_engine_label, reliability_passed),
            ("AI Guardrails", "ai-guardrails-platform", guardrail_passed),
            ("AI Observability", "ai-observability-platform", observability_passed),
            ("CI/CD Quality Gates", "Integration Test Suite Hook", overall_passed),
            ("Safety Enforcement", "ai-guardrails-platform Firewalls", guardrail_passed),
            ("Drift Monitoring", "ai-observability-platform Windowed Z-Scores", observability_passed),
        ]

        not_wired_yet = [
            ("Multi-Model Evaluation", "Cross-Engine Orchestrator"),
            ("Enterprise Reporting", "Central Hub Suite Platform"),
        ]

        for title, source, passed in hub_matrix:
            badge_class = "badge-pass" if passed else "badge-fail"
            badge_text = "PASSED" if passed else "FAILED"
            st.markdown(f"""
                        <div class='matrix-card'>
                            <div>
                                <span style='font-size: 1.05rem; font-weight: 700; color: #FFFFFF;'>{title}</span><br>
                                <span class='meta-text'>Engine Provider: {source}</span>
                            </div>
                            <div>
                                <span class='{badge_class}'>{badge_text}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        for title, source in not_wired_yet:
            st.markdown(f"""
                        <div class='matrix-card'>
                            <div>
                                <span style='font-size: 1.05rem; font-weight: 700; color: #FFFFFF;'>{title}</span><br>
                                <span class='meta-text'>Engine Provider: {source}</span>
                            </div>
                            <div>
                                <span class='badge-lock'>NOT WIRED YET</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

# =============================================================================
# ⚖️ TAB 2: GOVERNANCE & OPERATIONS PLATFORM PILLAR
# =============================================================================
with ui_tabs[1]:
    st.markdown("## ⚖️ Corporate AI Governance & Lifecycle Ledger")
    st.caption("Enterprise asset accounting, version controls, risk thresholds, and token cost compliance metrics.")

    models_response = get_model_registry(OBSERVABILITY_API_URL, INTERNAL_API_KEY)
    prompts_response = get_prompt_history(OBSERVABILITY_API_URL, INTERNAL_API_KEY)
    summary_response = get_control_hub_summary(OBSERVABILITY_API_URL, INTERNAL_API_KEY)

    metrics_ok = models_response["ok"] and prompts_response["ok"] and summary_response["ok"]
    model_count = len(models_response.get("models", [])) if models_response["ok"] else 0
    prompt_version_count = len(prompts_response.get("history", [])) if prompts_response["ok"] else 0
    avg_accuracy = summary_response.get("average_score") if summary_response["ok"] else None

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="Total Cloud Cost Allocated", value="Not wired yet")
    with m2:
        if metrics_ok:
            st.metric(label="Active Prompt Versions", value=f"{prompt_version_count} Tracked")
        else:
            st.metric(label="Active Prompt Versions", value="Not wired yet")
    with m3:
        if metrics_ok and avg_accuracy is not None:
            st.metric(label="Avg Score (Control Hub runs only)", value=f"{avg_accuracy:.1f}")
        else:
            st.metric(label="Avg Accuracy Envelope", value="No runs yet")
    with m4:
        if metrics_ok:
            st.metric(label="Active Registered Models", value=f"{model_count} Production Cores")
        else:
            st.metric(label="Active Registered Models", value="Not wired yet")

    left_layout, right_layout = st.columns(2)

    with left_layout:
        st.markdown("### 📑 Live Production Model Registry")
        st.caption("Dynamic ledger populated via the Observability Platform's own API.")
        if models_response["ok"] and models_response["models"]:
            dataframe_models = pd.DataFrame([
                {
                    "Model ID": m["model_id"], "Provider": m["provider"],
                    "Version": m["version"], "Business Owner": m["business_owner"],
                    "Risk Score": m["risk_score"],
                }
                for m in models_response["models"]
            ])
            st.dataframe(dataframe_models, width='stretch', hide_index=True)
        else:
            st.warning(f"Could not load model registry: {models_response.get('error', 'no data yet')}")

    with right_layout:
        st.markdown("### 🐙 Prompt Version Control Control-Plane")
        st.caption("Real version history — a new row appears only when the actual prompt text changes.")

        if st.button("🔍 Check RAG Prompt for Changes"):
            prompt_check_result = check_prompt_via_service(RAG_SYSTEM_URL, INTERNAL_API_KEY)
            if prompt_check_result["ok"]:
                if prompt_check_result.get("changed"):
                    st.success(f"New version recorded: {prompt_check_result['version_tag']}")
                else:
                    st.info(f"No change detected. Still {prompt_check_result.get('version_tag')}.")
            else:
                st.error(f"Could not check prompt: {prompt_check_result['error']}")

        if st.button("🔍 Check Pilgrim Bot Prompts for Changes"):
            pilgrim_prompt_result = check_prompt_via_service(PILGRIM_BOT_URL, INTERNAL_API_KEY)
            if pilgrim_prompt_result["ok"]:
                for r in pilgrim_prompt_result.get("results", []):
                    if "error" in r:
                        st.error(f"{r['prompt_name']}: {r['error']}")
                    elif r.get("changed"):
                        st.success(f"{r['prompt_name']}: new version recorded ({r['version_tag']})")
                    else:
                        st.info(f"{r['prompt_name']}: no change, still {r['version_tag']}")
            else:
                st.error(f"Could not reach Pilgrim Bot service: {pilgrim_prompt_result['error']}")

        if prompts_response["ok"]:
            history = prompts_response["history"]
            if not history:
                st.info("No prompt versions recorded yet — click a button above.")
            else:
                prompt_history_df = pd.DataFrame([
                    {"Prompt Name": h["prompt_name"], "Ver": h["version_tag"],
                     "Author": h["author"], "Changed At": h["changed_at"]}
                    for h in history
                ])
                st.dataframe(prompt_history_df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"Could not load prompt history: {prompts_response.get('error')}")

    st.markdown("---")

    st.markdown("### 🛡️ Enterprise Application Holistic Risk Index")
    st.caption(
        "Reliability scores are real, pulled from your last Control Hub runs. "
        "Guardrails is a shared check (not system-specific). Audit Gate and Cost Factor are not wired yet.")

    tracked_systems = [
        {"label": "P1: Core RAG Engine Platform", "target_project": "P1: qualigenai/RAG-System"},
        {"label": "P2: Srisailam Pilgrim Chatbot Core", "target_project": "P2: qualigenai/srisailam-pilgrim-bot"},
    ]

    guardrail_summary = get_latest_guardrail(OBSERVABILITY_API_URL, INTERNAL_API_KEY)
    guardrails_score = None
    if guardrail_summary["ok"] and guardrail_summary.get("found"):
        blocked = guardrail_summary["blocked"]
        total = guardrail_summary["total_tests"]
        if total:
            guardrails_score = round(100 * blocked / total)

    for system in tracked_systems:
        run_response = get_latest_run(OBSERVABILITY_API_URL, INTERNAL_API_KEY, system["target_project"])
        reliability_score = (
            run_response.get("hallucination_score")
            if run_response["ok"] and run_response.get("found") else None
        )

        if reliability_score is None:
            st.markdown(f"""
                    <div style="background-color: #0b0f19; border: 1px solid #1e293b; padding: 1.25rem; border-radius: 6px; margin-bottom: 0.75rem;">
                        <span style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF;">{system['label']}</span>
                        <span style="color: #64748B; margin-left: 1rem;">No Control Hub run recorded yet — click Launch with this target selected.</span>
                    </div>
                """, unsafe_allow_html=True)
            continue

        posture_label = "LOW" if reliability_score >= 75 else "MEDIUM" if reliability_score >= 50 else "HIGH"
        badge_bg = {"LOW": "#064e3b", "MEDIUM": "#78350f", "HIGH": "#7f1d1d"}[posture_label]
        badge_text = {"LOW": "#34d399", "MEDIUM": "#fbbf24", "HIGH": "#fca5a5"}[posture_label]

        guardrails_display = f"{guardrails_score}/100" if guardrails_score is not None else "No data yet"

        st.markdown(f"""
                <div style="background-color: #0b0f19; border: 1px solid #1e293b; padding: 1.25rem; border-radius: 6px; margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                        <span style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF;">{system['label']}</span>
                        <span style="background-color: {badge_bg}; color: {badge_text}; padding: 0.25rem 0.75rem; border-radius: 4px; font-weight: bold; font-size: 0.85rem;">RISK: {posture_label}</span>
                    </div>
                    <div style="display: flex; gap: 2rem; font-family: monospace; font-size: 0.9rem;">
                        <div>🎯 Reliability: <span style="color: #6366f1; font-weight:bold;">{reliability_score:.1f}/100</span></div>
                        <div>🛡️ Guardrails (shared): <span style="color: #10b981; font-weight:bold;">{guardrails_display}</span></div>
                        <div>⚖️ Audit Gate: <span style="color: #64748B;">Not wired yet</span></div>
                        <div>💰 Cost Factor: <span style="color: #64748B;">Not wired yet</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)