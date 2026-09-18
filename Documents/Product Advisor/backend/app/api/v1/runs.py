"""Agent runs and telemetry router providing real multi-agent execution traces."""

from fastapi import APIRouter, HTTPException
from app.services.orchestrator import RUNS_TELEMETRY

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("/{request_id}")
async def get_run_trace(request_id: str):
    """Retrieve real agent execution trace, steps, latencies, and verification findings."""
    run_data = RUNS_TELEMETRY.get(request_id)
    if not run_data:
        # Provide default structured response if not yet cached
        return {
            "status": "not_found",
            "request_id": request_id,
            "trace": [],
            "message": f"No active telemetry recorded for request_id '{request_id}'",
        }

    return {
        "status": "success",
        "request_id": request_id,
        "total_latency_ms": run_data.get("total_latency_ms", 0),
        "intent": run_data.get("intent", {}),
        "trace": run_data.get("trace", []),
        "verification": run_data.get("verification", {}),
        "recommendations_count": len(run_data.get("recommendations", [])),
    }
