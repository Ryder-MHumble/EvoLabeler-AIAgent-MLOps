"""
Project API schemas.

This module defines Pydantic models for project-related API requests and responses.
"""

from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    thumbnail_url: Optional[str] = Field(None, description="URL to project cover image")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    
    project_id: str = Field(..., min_length=1, max_length=100, description="Unique project identifier")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="Additional project metadata")
    
    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        """Validate project_id format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('project_id must contain only alphanumeric characters, hyphens, and underscores')
        return v


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None, pattern='^(idle|training|labeling|completed)$')
    image_count: Optional[int] = Field(None, ge=0)
    accuracy: Optional[float] = Field(None, ge=0, le=100)
    thumbnail_url: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    
    id: str = Field(..., description="Internal UUID")
    project_id: str = Field(..., description="Unique project identifier")
    status: str = Field(..., description="Project status")
    image_count: int = Field(default=0, description="Number of images in project")
    accuracy: Optional[float] = Field(None, description="Model accuracy percentage")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(..., description="Project creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for project list response."""
    
    projects: list[ProjectResponse]
    total: int = Field(..., description="Total number of projects")
    page: int = Field(default=1, ge=1, description="Current page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class ProjectStatsResponse(BaseModel):
    """Schema for project statistics response."""
    
    total_projects: int
    active_projects: int
    completed_projects: int
    total_images: int
    average_accuracy: Optional[float]


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    detail: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


