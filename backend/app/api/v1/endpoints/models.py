"""
Model Health API endpoints.

Provides endpoints for:
- Listing model versions with metrics
- Getting model health reports
- Viewing metrics history over time
- Manual model rollback
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.tools.supabase_client import SupabaseClient
from app.services.model_guardian import ModelGuardian
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/{project_id}/versions")
async def list_model_versions(project_id: str):
    """List all model versions for a project with their metrics."""
    try:
        client = SupabaseClient()
        versions = await client.get_model_versions(project_id)
        return {
            "project_id": project_id,
            "versions": versions,
            "total": len(versions),
        }
    except Exception as e:
        logger.error(f"Failed to list model versions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/health")
async def get_model_health(project_id: str):
    """
    Get comprehensive model health report.
    Compares the active model against the best model.
    """
    try:
        client = SupabaseClient()
        guardian = ModelGuardian(client)

        # Get active and best versions
        active = await client.get_active_model_version(project_id)
        best = await client.get_best_model_version(project_id)

        if not active:
            return {
                "project_id": project_id,
                "status": "no_model",
                "message": "No active model found for this project",
            }

        active_metrics = active.get("metrics", {})
        best_metrics = best.get("metrics", {}) if best else {}

        report = await guardian.check_model_health(
            current_metrics=active_metrics,
            best_metrics=best_metrics,
        )

        return {
            "project_id": project_id,
            "active_version": active.get("version"),
            "best_version": best.get("version") if best else None,
            "health_report": report.to_dict(),
        }

    except Exception as e:
        logger.error(f"Failed to get model health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/history")
async def get_metrics_history(
    project_id: str,
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Get metrics history over time (model versions ordered by creation).
    Used for frontend charts showing mAP/loss trends.
    """
    try:
        client = SupabaseClient()
        versions = await client.get_model_versions(project_id)

        # Build time series data
        history = []
        for v in reversed(versions[:limit]):  # Oldest first for charts
            metrics = v.get("metrics", {})
            history.append({
                "version": v.get("version"),
                "round_number": v.get("round_number"),
                "mAP50": metrics.get("mAP50"),
                "mAP50_95": metrics.get("mAP50_95"),
                "precision": metrics.get("precision"),
                "recall": metrics.get("recall"),
                "val_loss": metrics.get("val_loss"),
                "train_loss": metrics.get("train_loss"),
                "calibration_ece": v.get("calibration_ece"),
                "is_best": v.get("is_best"),
                "created_at": v.get("created_at"),
            })

        return {
            "project_id": project_id,
            "history": history,
            "total": len(history),
        }

    except Exception as e:
        logger.error(f"Failed to get metrics history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/rollback/{version_id}")
async def rollback_model(project_id: str, version_id: str):
    """
    Manually rollback to a specific model version.
    """
    try:
        client = SupabaseClient()
        guardian = ModelGuardian(client)

        # Get current active version
        active = await client.get_active_model_version(project_id)
        current_id = active.get("id") if active else None

        # Perform rollback
        result = await guardian.rollback_to_best(
            project_id=project_id,
            current_version_id=current_id
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("reason", "Rollback failed")
            )

        return {
            "message": "Model rolled back successfully",
            "project_id": project_id,
            **result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to rollback model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/rounds")
async def list_evo_rounds(
    project_id: str,
    job_id: Optional[str] = Query(default=None),
):
    """List EvoLoop rounds for a project."""
    try:
        client = SupabaseClient()
        rounds = await client.get_evo_rounds(project_id, job_id)
        return {
            "project_id": project_id,
            "rounds": rounds,
            "total": len(rounds),
        }
    except Exception as e:
        logger.error(f"Failed to list evo rounds: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
