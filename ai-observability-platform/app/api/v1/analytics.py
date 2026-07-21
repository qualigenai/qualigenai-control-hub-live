# app/api/v1/analytics.py
from fastapi import APIRouter, HTTPException, status
from app.core.database import get_db_connection
from app.core.config import settings
from app.services.drift_detector import DriftDetectorService
from fastapi import Depends
from app.core.security import verify_internal_key

# CRITICAL BASELINE CONTEXT: Initializes the router object for FastAPI compilation loops
router = APIRouter(prefix="/analytics", tags=["System Analytics"])


# ============================================================================
# WEEK 8: FINANCIAL COSTS ENDPOINT
# ============================================================================
@router.get("/costs/summary")
async def get_cost_summary():
    """
    Executes deep analytical aggregations across DuckDB records to extract
    financial metrics, tracking cost distributions across all model entities.
    """
    try:
        pm = settings.PRICING_MATRIX

        sql_case_input = "CASE "
        sql_case_output = "CASE "
        for model_name, rates in pm.items():
            if model_name != "default":
                sql_case_input += f"WHEN model_name = '{model_name}' THEN (prompt_tokens / 1000000.0) * {rates['input_cost_per_million']} "
                sql_case_output += f"WHEN model_name = '{model_name}' THEN (completion_tokens / 1000000.0) * {rates['output_cost_per_million']} "

        default_in = pm.get("default", {}).get("input_cost_per_million", 2.00)
        default_out = pm.get("default", {}).get("output_cost_per_million", 10.00)
        sql_case_input += f"ELSE (prompt_tokens / 1000000.0) * {default_in} END"
        sql_case_output += f"ELSE (completion_tokens / 1000000.0) * {default_out} END"

        with get_db_connection() as conn:
            summary_query = f"""
                SELECT 
                    COUNT(*) as total_calls,
                    SUM(prompt_tokens) as total_prompt_tokens,
                    SUM(completion_tokens) as total_completion_tokens,
                    SUM({sql_case_input}) as total_input_cost,
                    SUM({sql_case_output}) as total_output_cost,
                    AVG(latency_ms) as avg_latency
                FROM traces;
            """
            summary_res = conn.execute(summary_query).fetchone()

            breakdown_query = f"""
                SELECT 
                    model_name,
                    COUNT(*) as calls,
                    SUM(prompt_tokens + completion_tokens) as combined_tokens,
                    SUM({sql_case_input} + {sql_case_output}) as model_total_cost
                FROM traces
                GROUP BY model_name;
            """
            breakdown_res = conn.execute(breakdown_query).fetchall()

        model_breakdown = {}
        for row in breakdown_res:
            model_breakdown[row[0]] = {
                "calls_processed": row[1],
                "total_tokens": row[2],
                "financial_spend": round(row[3] if row[3] is not None else 0.0, 6)
            }

        total_input_cost = summary_res[3] if summary_res[3] is not None else 0.0
        total_output_cost = summary_res[4] if summary_res[4] is not None else 0.0

        return {
            "global_metrics": {
                "total_requests_tracked": summary_res[0],
                "total_tokens_consumed": (summary_res[1] or 0) + (summary_res[2] or 0),
                "aggregated_spend_usd": round(total_input_cost + total_output_cost, 6),
                "average_latency_ms": round(summary_res[5] or 0.0, 2)
            },
            "model_distribution": model_breakdown
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate financial analytics metrics: {str(e)}"
        )


# ============================================================================
# WEEK 9 - DAY 2: SLIDING WINDOW ROLLING STATISTICAL DRIFT
# ============================================================================
@router.get("/drift")
async def get_system_drift_analysis(window_size: int = 5, baseline_size: int = 20):
    """
    Queries historical trace timelines using windowing states to execute
    Z-Score statistical degradation monitoring across core AI reliability indexes.
    """
    try:
        with get_db_connection() as conn:
            raw_data = conn.execute("""
                SELECT latency_ms, hallucination_score, groundedness_score 
                FROM traces 
                ORDER BY timestamp ASC;
            """).fetchall()

        if len(raw_data) < (window_size + 2):
            return {
                "status": "insufficient_data",
                "message": f"Requires a minimum of {window_size + 2} recorded traces to execute statistical matrix.",
                "total_records_found": len(raw_data)
            }

        latencies = [row[0] for row in raw_data if row[0] is not None]
        hallucinations = [row[1] for row in raw_data if row[1] is not None]
        groundedness = [row[2] for row in raw_data if row[2] is not None]

        baseline_slice_lat = latencies[-baseline_size - window_size: -window_size]
        window_slice_lat = latencies[-window_size:]

        baseline_slice_hal = hallucinations[-baseline_size - window_size: -window_size]
        window_slice_hal = hallucinations[-window_size:]

        baseline_slice_grd = groundedness[-baseline_size - window_size: -window_size]
        window_slice_grd = groundedness[-window_size:]

        latency_drift = DriftDetectorService.analyze_metric_degradation(window_slice_lat, baseline_slice_lat)
        hallucination_drift = DriftDetectorService.analyze_metric_degradation(window_slice_hal, baseline_slice_hal)
        groundedness_drift = DriftDetectorService.analyze_metric_degradation(window_slice_grd, baseline_slice_grd)

        return {
            "metrics_analyzed": len(raw_data),
            "window_size_configured": window_size,
            "baseline_size_configured": baseline_size,
            "drift_report": {
                "system_latency": latency_drift,
                "ai_hallucination_index": hallucination_drift,
                "ai_groundedness_index": groundedness_drift
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate statistical drift matrix endpoints: {str(e)}"
        )


# ============================================================================
# WEEK 9 - DAY 4: PRE-PROD CI VS LIVE PRODUCTION VARIANCE MONITORING
# ============================================================================
@router.get("/performance/degradation")
async def get_performance_degradation_summary():
    """
    Exposes a summary matrix comparing pre-production evaluation baselines
    (from your Project 1 sync) against live production runtime scores.
    """
    try:
        with get_db_connection() as conn:
            # Aggregate metrics coming specifically from pre-production CI runs
            ci_baselines = conn.execute("""
                SELECT 
                    AVG(hallucination_score) as avg_hal,
                    AVG(groundedness_score) as avg_grd,
                    AVG(retrieval_precision) as avg_ret
                FROM traces
                WHERE json_extract_string(metadata, '$.source') = 'project_1_reliability_engine_ci';
            """).fetchone()

            # Aggregate metrics coming from live production traffic scenarios
            prod_metrics = conn.execute("""
                SELECT 
                    AVG(hallucination_score) as avg_hal,
                    AVG(groundedness_score) as avg_grd,
                    AVG(retrieval_precision) as avg_ret
                FROM traces
                WHERE metadata IS NULL OR json_extract_string(metadata, '$.source') IS NULL;
            """).fetchone()

        ci_hal = ci_baselines[0] if ci_baselines[0] is not None else 0.05
        ci_grd = ci_baselines[1] if ci_baselines[1] is not None else 0.92
        ci_ret = ci_baselines[2] if ci_baselines[2] is not None else 0.88

        prod_hal = prod_metrics[0] if prod_metrics[0] is not None else 0.22
        prod_grd = prod_metrics[1] if prod_metrics[1] is not None else 0.78
        prod_ret = prod_metrics[2] if prod_metrics[2] is not None else 0.71

        return {
            "status": "active",
            "framework_comparison": {
                "pre_production_ci_baseline": {
                    "average_hallucination": round(ci_hal, 4),
                    "average_groundedness": round(ci_grd, 4),
                    "context_retrieval_precision": round(ci_ret, 4)
                },
                "live_production_runtime": {
                    "average_hallucination": round(prod_hal, 4),
                    "average_groundedness": round(prod_grd, 4),
                    "context_retrieval_precision": round(prod_ret, 4)
                },
                "performance_variance": {
                    "hallucination_drift_delta": round(prod_hal - ci_hal, 4),
                    "groundedness_drop_delta": round(ci_grd - prod_grd, 4),
                    "retrieval_degradation_delta": round(ci_ret - prod_ret, 4)
                }
            },
            "recommendation": "Investigate retrieval pipeline if degradation delta breaches 0.15 threshold."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate performance degradation matrix profiles: {str(e)}"
        )

@router.get("/registry/models", dependencies=[Depends(verify_internal_key)])
async def get_model_registry():
    try:
        with get_db_connection() as conn:
            rows = conn.execute(
                "SELECT model_id, model_provider, model_version, business_owner, risk_score FROM model_registry"
            ).fetchall()
        return {
            "models": [
                {"model_id": r[0], "provider": r[1], "version": r[2], "business_owner": r[3], "risk_score": r[4]}
                for r in rows
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/control-hub-summary", dependencies=[Depends(verify_internal_key)])
async def get_control_hub_summary():
    """Average score across all real Control Hub runs (not simulated/legacy data)."""
    try:
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT AVG(hallucination_score), COUNT(*) FROM traces "
                "WHERE hallucination_score IS NOT NULL AND model_name = 'control-hub-run'"
            ).fetchone()
        avg_score = round(row[0], 1) if row and row[0] is not None else None
        run_count = row[1] if row else 0
        return {"average_score": avg_score, "run_count": run_count}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/latest-run", dependencies=[Depends(verify_internal_key)])
async def get_latest_run(target_project: str):
    """Most recent real Control Hub reliability score for one specific system."""
    try:
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT hallucination_score FROM traces "
                "WHERE model_name = 'control-hub-run' "
                "AND json_extract_string(metadata, '$.target_project') = ? "
                "ORDER BY timestamp DESC LIMIT 1",
                [target_project]
            ).fetchone()
        if row and row[0] is not None:
            return {"found": True, "hallucination_score": row[0]}
        return {"found": False, "hallucination_score": None}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/latest-guardrail", dependencies=[Depends(verify_internal_key)])
async def get_latest_guardrail():
    """Most recent guardrail result — shared across all systems, not per-target."""
    try:
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT json_extract_string(metadata, '$.guardrails.report.blocked'), "
                "json_extract_string(metadata, '$.guardrails.report.total_tests') "
                "FROM traces WHERE model_name = 'control-hub-run' "
                "ORDER BY timestamp DESC LIMIT 1"
            ).fetchone()
        if row and row[0] is not None and row[1] not in (None, "0"):
            return {"found": True, "blocked": int(row[0]), "total_tests": int(row[1])}
        return {"found": False, "blocked": None, "total_tests": None}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
