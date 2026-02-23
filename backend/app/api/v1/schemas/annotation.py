"""
Annotation API schemas.

This module defines Pydantic models for annotation-related API requests and responses.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BBox(BaseModel):
    """Bounding box schema."""

    x: float = Field(..., ge=0, le=1, description="Normalized x coordinate (0-1)")
    y: float = Field(..., ge=0, le=1, description="Normalized y coordinate (0-1)")
    width: float = Field(..., ge=0, le=1, description="Normalized width (0-1)")
    height: float = Field(..., ge=0, le=1, description="Normalized height (0-1)")
    label: str = Field(..., min_length=1, max_length=100, description="Object label")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score (0-1)")


class AnnotationCreate(BaseModel):
    """Schema for creating a new annotation."""

    project_id: str = Field(..., min_length=1, max_length=100, description="Project identifier")
    image_id: str = Field(..., min_length=1, max_length=200, description="Image identifier")
    bboxes: List[BBox] = Field(..., description="List of bounding boxes")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")


class AnnotationUpdate(BaseModel):
    """Schema for updating an existing annotation."""

    bboxes: Optional[List[BBox]] = Field(None, description="Updated bounding boxes")
    metadata: Optional[dict] = Field(None, description="Updated metadata")


class AnnotationResponse(BaseModel):
    """Schema for annotation response."""

    id: str = Field(..., description="Annotation UUID")
    project_id: str = Field(..., description="Project identifier")
    image_id: str = Field(..., description="Image identifier")
    user_id: Optional[str] = Field(None, description="User who created the annotation")
    bboxes: List[BBox] = Field(..., description="List of bounding boxes")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class AnnotationListResponse(BaseModel):
    """Schema for annotation list response."""

    annotations: List[AnnotationResponse]
    total: int = Field(..., description="Total number of annotations")
