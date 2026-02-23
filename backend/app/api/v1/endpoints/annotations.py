"""
Annotation API endpoints.

This module provides RESTful API endpoints for annotation management:
- POST /annotations/ : Create a new annotation
- GET /annotations/{project_id} : List annotations for a project
- GET /annotations/detail/{annotation_id} : Get annotation details
- PUT /annotations/{annotation_id} : Update annotation
- DELETE /annotations/{annotation_id} : Delete annotation
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status

from app.api.v1.schemas.annotation import (
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationResponse,
    AnnotationListResponse,
)
from app.tools.supabase_client import SupabaseClient
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/annotations", tags=["annotations"])


@router.post(
    "/",
    response_model=AnnotationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new annotation",
    description="Create a new annotation with bounding boxes for an image",
    responses={
        201: {"description": "Annotation created successfully"},
        400: {"description": "Invalid request data"},
    }
)
async def create_annotation(annotation: AnnotationCreate) -> AnnotationResponse:
    """
    Create a new annotation.

    Args:
        annotation: Annotation creation data

    Returns:
        Created annotation details

    Raises:
        HTTPException: If validation fails or creation error occurs
    """
    try:
        supabase_client = SupabaseClient()

        # Build annotation data
        now = datetime.utcnow().isoformat()
        annotation_data = {
            "project_id": annotation.project_id,
            "image_id": annotation.image_id,
            "user_id": None,  # No auth yet
            "bboxes": [bbox.model_dump() for bbox in annotation.bboxes],
            "metadata": annotation.metadata or {},
            "created_at": now,
            "updated_at": now,
        }

        created_annotation = await supabase_client.create_annotation(annotation_data)

        logger.info(
            f"Created annotation for project: {annotation.project_id}, image: {annotation.image_id}",
            extra={
                "project_id": annotation.project_id,
                "image_id": annotation.image_id,
            }
        )

        return AnnotationResponse(**created_annotation)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create annotation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create annotation: {str(e)}"
        )


@router.get(
    "/{project_id}",
    response_model=AnnotationListResponse,
    summary="List annotations for a project",
    description="Retrieve all annotations for a specific project, optionally filtered by image",
    responses={
        200: {"description": "Annotations retrieved successfully"},
    }
)
async def list_annotations(
    project_id: str,
    image_id: Optional[str] = Query(None, description="Filter by image ID"),
) -> AnnotationListResponse:
    """
    List annotations for a project.

    Args:
        project_id: Project identifier
        image_id: Optional image identifier to filter by

    Returns:
        List of annotations with total count
    """
    try:
        supabase_client = SupabaseClient()

        result = await supabase_client.get_annotations_by_project(
            project_id=project_id,
            image_id=image_id,
        )

        annotations = [AnnotationResponse(**a) for a in result["annotations"]]

        return AnnotationListResponse(
            annotations=annotations,
            total=result["total"],
        )

    except Exception as e:
        logger.error(
            f"Failed to list annotations: {e}",
            exc_info=True,
            extra={"project_id": project_id, "image_id": image_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list annotations: {str(e)}"
        )


@router.get(
    "/detail/{annotation_id}",
    response_model=AnnotationResponse,
    summary="Get annotation details",
    description="Retrieve detailed information about a specific annotation",
    responses={
        200: {"description": "Annotation details retrieved successfully"},
        404: {"description": "Annotation not found"},
    }
)
async def get_annotation(annotation_id: str) -> AnnotationResponse:
    """
    Get detailed information about a specific annotation.

    Args:
        annotation_id: Annotation UUID

    Returns:
        Annotation details

    Raises:
        HTTPException: If annotation not found
    """
    try:
        supabase_client = SupabaseClient()
        annotation = await supabase_client.get_annotation_by_id(annotation_id)

        return AnnotationResponse(**annotation)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Annotation not found: {annotation_id}"
        )
    except Exception as e:
        logger.error(f"Failed to get annotation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get annotation: {str(e)}"
        )


@router.put(
    "/{annotation_id}",
    response_model=AnnotationResponse,
    summary="Update annotation",
    description="Update an existing annotation's bounding boxes or metadata",
    responses={
        200: {"description": "Annotation updated successfully"},
        404: {"description": "Annotation not found"},
    }
)
async def update_annotation(
    annotation_id: str,
    annotation_update: AnnotationUpdate,
) -> AnnotationResponse:
    """
    Update an existing annotation.

    Args:
        annotation_id: Annotation UUID
        annotation_update: Fields to update

    Returns:
        Updated annotation details

    Raises:
        HTTPException: If annotation not found or update fails
    """
    try:
        supabase_client = SupabaseClient()

        # Build update data (only include non-None fields)
        update_data = {}
        if annotation_update.bboxes is not None:
            update_data["bboxes"] = [bbox.model_dump() for bbox in annotation_update.bboxes]
        if annotation_update.metadata is not None:
            update_data["metadata"] = annotation_update.metadata

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        updated_annotation = await supabase_client.update_annotation(
            annotation_id=annotation_id,
            update_data=update_data,
        )

        logger.info(
            f"Updated annotation: {annotation_id}",
            extra={"annotation_id": annotation_id, "fields": list(update_data.keys())}
        )

        return AnnotationResponse(**updated_annotation)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Annotation not found: {annotation_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update annotation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update annotation: {str(e)}"
        )


@router.delete(
    "/{annotation_id}",
    summary="Delete annotation",
    description="Delete an annotation record",
    responses={
        200: {"description": "Annotation deleted successfully"},
        404: {"description": "Annotation not found"},
    }
)
async def delete_annotation(annotation_id: str) -> dict[str, str]:
    """
    Delete an annotation.

    Args:
        annotation_id: Annotation UUID

    Returns:
        Deletion confirmation message

    Raises:
        HTTPException: If annotation not found or deletion fails
    """
    try:
        supabase_client = SupabaseClient()
        await supabase_client.delete_annotation(annotation_id)

        logger.info(
            f"Deleted annotation: {annotation_id}",
            extra={"annotation_id": annotation_id}
        )

        return {"message": "Annotation deleted successfully"}

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Annotation not found: {annotation_id}"
        )
    except Exception as e:
        logger.error(f"Failed to delete annotation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete annotation: {str(e)}"
        )
