# app/dashboard/app.py
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------------------------------------------------------
# 🏢 PREMIUM THEMING & EXPLICIT VISUAL ACCENTS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="QualiGenAI Intel Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Deep obsidian inject matrix to clean away ugly default margins
st.markdown("""
    <style>
        /* Base application background force */
        .stApp { background-color: #060814; color: #E2E8F0; }
        header { visibility: hidden; }
        .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }

        /* Premium custom KPI card design grid */
        .kpi-card {
            background: linear-gradient(145deg, #0f132a, #090b18);
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }
        .kpi-val-green { color: #10B981; font-size: 2.2rem; font-weight: 800; font-family: monospace; }
        .kpi-val-blue { color: #3B82F6; font-size: 2.2rem; font-weight: 800; font-family: monospace; }
        .kpi-val-orange { color: #F59E0B; font-size: 2.2rem; font-weight: 800; font-family: monospace; }
        .kpi-val-red { color: #EF4444; font-size: 2.2rem; font-weight: 800; font-family: monospace; }
        .kpi-label { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1.2px; color: #94A3B8; margin-top: 0.5rem; }

        /* Header typography settings */
        .title-container {
            border-bottom: 1px solid #1e293b;
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }
        .brand-title { font-size: 2.4rem; font-weight: 900; letter-spacing: -1px; color: #FFFFFF; }
        .brand-badge { background: #1e1b4b; color: #818cf8; border: 1px solid #3730a3; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.8rem; font-weight: 600; margin-left: 10px; vertical-align: middle; }
        .brand-sub { font-size: 0.95rem; color: #64748B; margin-top: 0.3rem; }

        /* REFINED DATAFRAME MOUNT: Wraps container borders cleanly */
        div[data-testid="stDataFrame"] {
            border: 1px solid #1e293b !important;
            border-radius: 8px !important;
            background-color: #090b18 !important;
        }
    </style>
""", unsafe_allow_html=True)

# CRITICAL FIX: Defined globally here so load_live_metrics can access it instantly
DB_PATH = Path(__file__).resolve().parent.parent.parent / "observability_vault.duckdb"


def load_live_metrics() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        df = conn.execute("SELECT * FROM traces ORDER BY timestamp DESC;").fetchdf()
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()


# -----------------------------------------------------------------------------
# 🎛️ RENDER LOGIC
# -----------------------------------------------------------------------------
st.markdown("""
    <div class='title-container'>
        <span class='brand-title'>QualiGenAI <span style='color:#6366f1'>Observability</span></span>
        <span class='brand-badge'>ENTERPRISE CORE v1.0</span>
        <div class='brand-sub'>Unified time-series telemetry hub tracking pre-production evaluations and production safety drift lines</div>
    </div>
""", unsafe_allow_html=True)

df_traces = load_live_metrics()

if df_traces.empty:
    st.info("💡 Synchronizing initial pipeline metrics... Fire traffic patterns to activate data maps.")
else:
    # -----------------------------------------------------------------------------
    # 🧮 STEP 1: CALCULATE COMPONENT METRICS & CUSTOM KPI CARDS
    # -----------------------------------------------------------------------------
    total_calls = len(df_traces)
    total_tokens = int(df_traces["prompt_tokens"].sum() + df_traces["completion_tokens"].sum())
    avg_latency = float(df_traces["latency_ms"].mean())
    security_alerts = int(df_traces["policy_violated"].sum())

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-val-blue'>{total_calls:,}</div><div class='kpi-label'>API Requests Ingested</div></div>",
            unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-val-green'>{total_tokens:,}</div><div class='kpi-label'>Consolidated Tokens</div></div>",
            unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-val-orange'>{avg_latency:.1f}ms</div><div class='kpi-label'>Average Engine Latency</div></div>",
            unsafe_allow_html=True)
    with kpi_col4:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-val-red'>{security_alerts}</div><div class='kpi-label'>Security Incidents</div></div>",
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # 📈 STEP 2: GENERATE PREMIUM INTERACTIVE PLOTLY GRAPHIC LAYOUTS
    # -----------------------------------------------------------------------------
    chart_col1, chart_col2 = st.columns([2, 1])

    with chart_col1:
        st.markdown(
            "<div style='font-size:1.1rem; font-weight:700; margin-bottom:1rem; color:#F8FAFC;'>📉 Trailing Execution Latency Lifecycle Trends</div>",
            unsafe_allow_html=True)
        df_sorted = df_traces.sort_values("timestamp")

        fig_timeline = px.line(
            df_sorted,
            x="timestamp",
            y="latency_ms",
            color="model_name",
            color_discrete_sequence=["#6366f1", "#10b981", "#f59e0b"],
            template="plotly_dark"
        )
        fig_timeline.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, title="Timeline Chronology"),
            yaxis=dict(showgrid=True, gridcolor='#1e293b', title="Latency Duration (ms)"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
       # st.plotly_chart(fig_timeline, use_container_width=True, config={'displayModeBar': False})
        # Change use_container_width=True to width="stretch"
        st.plotly_chart(fig_timeline, width="stretch", config={'displayModeBar': False})

    with chart_col2:
        st.markdown(
            "<div style='font-size:1.1rem; font-weight:700; margin-bottom:1rem; color:#F8FAFC;'>🤖 Computational Workload Distribution</div>",
            unsafe_allow_html=True)

        fig_pie = px.pie(
            df_traces,
            names="model_name",
            values="prompt_tokens",
            hole=0.6,
            color_discrete_sequence=["#6366f1", "#10b981", "#f59e0b"],
            template="plotly_dark"
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )
        fig_pie.update_traces(textinfo='percent+label', pull=[0.05, 0, 0])
        # st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
        # Change use_container_width=True to width="stretch"
        st.plotly_chart(fig_pie, width="stretch", config={'displayModeBar': False})


    # -----------------------------------------------------------------------------
    # 📋 STEP 3: EXECUTING HIGH-END DATAFRAME RENDER
    # -----------------------------------------------------------------------------
    st.markdown(
        "<br><div style='font-size:1.2rem; font-weight:700; margin-bottom:1rem; color:#F8FAFC;'>📋 Real-Time Distributed Telemetry Stream Log</div>",
        unsafe_allow_html=True)

    visible_columns = [
        "trace_id", "timestamp", "model_name", "latency_ms",
        "prompt_tokens", "completion_tokens", "policy_violated", "hallucination_score"
    ]

    df_display = df_traces[visible_columns].copy()
    df_display['timestamp'] = df_display['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df_display['latency_ms'] = df_display['latency_ms'].round(1)

    st.dataframe(
        df_display,
        width="stretch",  # <-- FIXED: Replaced use_container_width=True with width="stretch"
        hide_index=True,
        column_config={
            "trace_id": st.column_config.TextColumn("Trace ID Unique Identifier"),
            "timestamp": st.column_config.TextColumn("UTC Ingestion Timestamp"),
            "model_name": st.column_config.TextColumn("Target Model"),
            "latency_ms": st.column_config.NumberColumn("Latency (ms)", format="%.1f ms"),
            "prompt_tokens": st.column_config.NumberColumn("In Tokens"),
            "completion_tokens": st.column_config.NumberColumn("Out Tokens"),
            "policy_violated": st.column_config.CheckboxColumn("Guardrail Tripped 🛡️"),
            "hallucination_score": st.column_config.ProgressColumn("Hallucination Score Index", min_value=0.0,
                                                                   max_value=1.0, format="%.2f")
        }
    )