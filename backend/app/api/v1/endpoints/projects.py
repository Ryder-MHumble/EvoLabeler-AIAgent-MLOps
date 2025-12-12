"""
Project API endpoints.

This module provides RESTful API endpoints for project management:
- POST /projects/ : Create a new project
- GET /projects/ : List all projects with pagination
- GET /projects/{project_id} : Get project details
- PUT /projects/{project_id} : Update project
- DELETE /projects/{project_id} : Delete project
- GET /projects/stats : Get project statistics
"""

from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.api.v1.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStatsResponse,
    ErrorResponse,
)
from app.tools.supabase_client import SupabaseClient
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Create a new EvoLabeler project with metadata",
    responses={
        201: {"description": "Project created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        409: {"model": ErrorResponse, "description": "Project ID already exists"},
    }
)
async def create_project(project: ProjectCreate) -> ProjectResponse:
    """
    Create a new project.
    
    Args:
        project: Project creation data
        
    Returns:
        Created project details
        
    Raises:
        HTTPException: If project_id already exists or validation fails
    """
    try:
        supabase_client = SupabaseClient()
        
        # Check if project_id already exists
        try:
            existing = await supabase_client.get_project_by_id(project.project_id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Project with ID '{project.project_id}' already exists"
                )
        except ValueError:
            # Project doesn't exist, which is what we want
            pass
        
        # Create project record
        project_data = {
            "project_id": project.project_id,
            "name": project.name,
            "description": project.description,
            "thumbnail_url": project.thumbnail_url,
            "status": "idle",
            "image_count": 0,
            "metadata": project.metadata,
        }
        
        created_project = await supabase_client.create_project(project_data)
        
        logger.info(
            f"Created project: {project.project_id}",
            extra={"project_id": project.project_id}
        )
        
        return ProjectResponse(**created_project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create project: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get(
    "/",
    response_model=ProjectListResponse,
    summary="List all projects",
    description="Retrieve a paginated list of all projects",
    responses={
        200: {"description": "Projects retrieved successfully"},
    }
)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order")
) -> ProjectListResponse:
    """
    List all projects with pagination and filtering.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        status_filter: Optional status filter
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        
    Returns:
        Paginated list of projects
    """
    try:
        supabase_client = SupabaseClient()
        
        # Get projects with pagination
        result = await supabase_client.list_projects(
            page=page,
            page_size=page_size,
            status_filter=status_filter,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        projects = [ProjectResponse(**p) for p in result["projects"]]
        
        return ProjectListResponse(
            projects=projects,
            total=result["total"],
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Failed to list projects: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project details",
    description="Retrieve detailed information about a specific project",
    responses={
        200: {"description": "Project details retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Project not found"},
    }
)
async def get_project(project_id: str) -> ProjectResponse:
    """
    Get detailed information about a specific project.
    
    Args:
        project_id: Project identifier
        
    Returns:
        Project details
        
    Raises:
        HTTPException: If project not found
    """
    try:
        supabase_client = SupabaseClient()
        project = await supabase_client.get_project_by_id(project_id)
        
        return ProjectResponse(**project)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )
    except Exception as e:
        logger.error(f"Failed to get project: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project: {str(e)}"
        )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Update an existing project's information",
    responses={
        200: {"description": "Project updated successfully"},
        404: {"model": ErrorResponse, "description": "Project not found"},
    }
)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate
) -> ProjectResponse:
    """
    Update an existing project.
    
    Args:
        project_id: Project identifier
        project_update: Fields to update
        
    Returns:
        Updated project details
        
    Raises:
        HTTPException: If project not found or update fails
    """
    try:
        supabase_client = SupabaseClient()
        
        # Build update data (only include non-None fields)
        update_data = {
            k: v for k, v in project_update.model_dump().items() 
            if v is not None
        }
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        updated_project = await supabase_client.update_project(
            project_id=project_id,
            update_data=update_data
        )
        
        logger.info(
            f"Updated project: {project_id}",
            extra={"project_id": project_id, "fields": list(update_data.keys())}
        )
        
        return ProjectResponse(**updated_project)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Delete a project and all associated data",
    responses={
        204: {"description": "Project deleted successfully"},
        404: {"model": ErrorResponse, "description": "Project not found"},
    }
)
async def delete_project(project_id: str) -> None:
    """
    Delete a project.
    
    Args:
        project_id: Project identifier
        
    Raises:
        HTTPException: If project not found or deletion fails
    """
    try:
        supabase_client = SupabaseClient()
        await supabase_client.delete_project(project_id)
        
        logger.info(
            f"Deleted project: {project_id}",
            extra={"project_id": project_id}
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )
    except Exception as e:
        logger.error(f"Failed to delete project: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )


@router.get(
    "/stats/summary",
    response_model=ProjectStatsResponse,
    summary="Get project statistics",
    description="Get aggregate statistics across all projects",
    responses={
        200: {"description": "Statistics retrieved successfully"},
    }
)
async def get_project_stats() -> ProjectStatsResponse:
    """
    Get aggregate statistics for all projects.
    
    Returns:
        Project statistics
    """
    try:
        supabase_client = SupabaseClient()
        stats = await supabase_client.get_project_stats()
        
        return ProjectStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get project stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project statistics: {str(e)}"
        )





