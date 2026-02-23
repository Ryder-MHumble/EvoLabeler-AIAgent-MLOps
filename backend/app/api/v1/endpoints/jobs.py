"""
Job API endpoints.

This module provides RESTful API endpoints for job management:
- POST /jobs/ : Create a new job and start workflow
- GET /jobs/{job_id}/status : Get job status
"""

import uuid
import zipfile
import shutil
from pathlib import Path
from typing import Any

import aiofiles

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse

from app.api.v1.schemas.job import (
    JobResponse,
    JobStatusResponse,
    ErrorResponse,
)
from app.services.orchestrator import JobOrchestrator
from app.tools.supabase_client import SupabaseClient
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job",
    description="Upload a ZIP file containing images and start the IDEATE workflow"
)
async def create_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="ZIP file containing images")
) -> JobResponse:
    """
    Create a new job and start the workflow.

    This endpoint:
    1. Validates the uploaded file
    2. Streams file to disk in chunks (10MB at a time)
    3. Extracts images from ZIP
    4. Creates a job record in database
    5. Starts the workflow in background
    6. Returns job_id immediately

    Args:
        background_tasks: FastAPI background tasks
        file: Uploaded ZIP file

    Returns:
        JobResponse with job_id and status
    """
    job_id = None
    temp_dir = None

    try:
        # Validate file type
        if not file.filename or not file.filename.endswith('.zip'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only ZIP files are accepted"
            )

        # Generate unique job ID
        job_id = str(uuid.uuid4())

        # Create temporary directory
        temp_dir = Path(f"/tmp/uploads/{job_id}")
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Stream upload to disk with chunked processing
        zip_path = temp_dir / "upload.zip"
        file_size_bytes = await _stream_upload_to_disk(file, zip_path)
        file_size_mb = file_size_bytes / (1024 * 1024)

        # Check file size after streaming
        if file_size_mb > settings.max_upload_size_mb:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {settings.max_upload_size_mb}MB limit"
            )

        # Validate ZIP file integrity
        if not zipfile.is_zipfile(zip_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is corrupted or not a valid ZIP file"
            )

        logger.info(
            f"Creating new job: {job_id}",
            extra={"job_id": job_id, "file_size_mb": file_size_mb}
        )

        # Extract and process uploaded file
        upload_dir = await _process_upload(job_id, zip_path)

        # Create job record in database
        supabase_client = SupabaseClient()
        job_record = await supabase_client.create_job_record(
            job_id=job_id,
            status="UPLOAD",
            metadata={
                "filename": file.filename,
                "file_size_mb": file_size_mb,
                "upload_dir": upload_dir,
            }
        )

        # Start workflow in background
        background_tasks.add_task(_run_workflow, job_id, upload_dir)

        logger.info(f"Job created successfully: {job_id}")

        return JobResponse(
            job_id=job_id,
            status="UPLOAD",
            created_at=job_record.get("created_at", ""),
            message="Job created and workflow started"
        )

    except HTTPException:
        # Clean up on validation errors
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    except Exception as e:
        # Clean up on unexpected errors
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        logger.error(f"Failed to create job: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )


@router.get(
    "/{job_id}/status",
    response_model=JobStatusResponse,
    summary="Get job status",
    description="Retrieve the current status of a job"
)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get the current status of a job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        JobStatusResponse with current status and progress
    """
    try:
        supabase_client = SupabaseClient()
        job = await supabase_client.get_job_by_id(job_id)
        
        return JobStatusResponse(
            job_id=job["job_id"],
            status=job["status"],
            progress_message=job.get("progress_message"),
            created_at=job["created_at"],
            updated_at=job["updated_at"],
            metadata=job.get("metadata", {})
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}"
        )
    except Exception as e:
        logger.error(f"Failed to get job status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )


# Helper functions

async def _stream_upload_to_disk(file: UploadFile, destination: Path) -> int:
    """
    Stream uploaded file to disk using chunked processing.

    This prevents loading the entire file into memory by writing it in
    10MB chunks, enabling support for large files (500MB+) without OOM errors.

    Args:
        file: FastAPI UploadFile object
        destination: Path where the file should be saved

    Returns:
        Total number of bytes written

    Raises:
        HTTPException: If file write fails
    """
    chunk_size = 10 * 1024 * 1024  # 10MB chunks
    total_bytes = 0

    try:
        async with aiofiles.open(destination, 'wb') as f:
            while chunk := await file.read(chunk_size):
                await f.write(chunk)
                total_bytes += len(chunk)

        logger.info(
            f"Streamed upload complete: {total_bytes / (1024 * 1024):.2f}MB written",
            extra={"bytes": total_bytes, "destination": str(destination)}
        )

        return total_bytes

    except Exception as e:
        # Clean up partial file on error
        if destination.exists():
            destination.unlink()
        logger.error(f"Failed to stream upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}"
        )


async def _process_upload(job_id: str, zip_path: Path) -> str:
    """
    Process uploaded ZIP file.

    Extracts the ZIP file and returns the path to extracted images.

    Args:
        job_id: Job identifier
        zip_path: Path to the ZIP file on disk

    Returns:
        Path to directory containing extracted images

    Raises:
        HTTPException: If ZIP extraction fails
    """
    upload_dir = zip_path.parent

    # Extract ZIP
    extract_dir = upload_dir / "images"
    extract_dir.mkdir(exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Validate ZIP integrity before extraction
            if zip_ref.testzip() is not None:
                raise zipfile.BadZipFile("ZIP file contains corrupted data")

            zip_ref.extractall(extract_dir)

        # Count extracted images
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}
        image_files = [
            f for f in extract_dir.rglob('*')
            if f.suffix.lower() in image_extensions
        ]

        logger.info(f"Extracted {len(image_files)} images from ZIP")

        # Remove ZIP file to save space
        zip_path.unlink()

        return str(extract_dir)

    except zipfile.BadZipFile as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or corrupted ZIP file: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to extract ZIP: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract ZIP file: {str(e)}"
        )


async def _run_workflow(job_id: str, upload_dir: str) -> None:
    """
    Run the complete IDEATE workflow.
    
    This is executed as a background task.
    
    Args:
        job_id: Job identifier
        upload_dir: Path to uploaded images
    """
    try:
        logger.info(f"Starting workflow for job: {job_id}")
        
        # Get list of uploaded images
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}
        image_files = [
            str(f) for f in Path(upload_dir).rglob('*')
            if f.suffix.lower() in image_extensions
        ]
        
        # Create orchestrator
        orchestrator = JobOrchestrator(job_id)
        
        # Set initial context
        orchestrator.context.update({
            "uploaded_images": image_files,
            "upload_dir": upload_dir,
            "model_path": "yolov5s.pt",  # Default model
        })
        
        # Run workflow
        result = await orchestrator.run()
        
        logger.info(f"Workflow completed for job: {job_id}", extra=result)
        
    except Exception as e:
        logger.error(
            f"Workflow failed for job: {job_id}",
            exc_info=True,
            extra={"job_id": job_id}
        )
        # Error is already handled in orchestrator


