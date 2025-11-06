"""
Pydantic schemas for Job API.

These models define the request and response structures
for the Job endpoints.
"""

from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class JobCreate(BaseModel):
    """Request model for creating a new job."""
    
    # File will be uploaded via multipart/form-data
    # This schema is for reference only
    pass


class JobResponse(BaseModel):
    """Response model for job creation."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Current job status")
    created_at: str = Field(..., description="Job creation timestamp")
    message: str = Field(default="Job created successfully", description="Response message")
    
    model_config = {"from_attributes": True}


class JobStatusResponse(BaseModel):
    """Response model for job status query."""
    
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Current job status")
    progress_message: Optional[str] = Field(None, description="Current progress message")
    created_at: str = Field(..., description="Job creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Job metadata")
    
    model_config = {"from_attributes": True}


class JobSummaryResponse(BaseModel):
    """Response model for completed job summary."""
    
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Final job status")
    start_time: Optional[str] = Field(None, description="Workflow start time")
    end_time: Optional[str] = Field(None, description="Workflow end time")
    duration_seconds: Optional[float] = Field(None, description="Total duration in seconds")
    training_skipped: bool = Field(default=False, description="Whether training was skipped")
    summary: dict[str, Any] = Field(default_factory=dict, description="Workflow summary")
    
    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict[str, Any]] = Field(None, description="Additional error details")

