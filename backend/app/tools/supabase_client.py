"""
Supabase client wrapper for common operations.

This module provides a SupabaseClient class that encapsulates
common Supabase operations such as file uploads, job management, etc.
"""

from typing import Any, Optional
from datetime import datetime
import io

from supabase import Client

from app.db.supabase_init import get_supabase_client
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class SupabaseClient:
    """
    Wrapper class for Supabase operations.
    
    This class provides a clean interface for interacting with Supabase,
    including job management, file uploads, and data storage.
    """

    def __init__(self, client: Optional[Client] = None) -> None:
        """
        Initialize the Supabase client wrapper.
        
        Args:
            client: Optional Supabase client instance. If None, uses global instance.
        """
        self.client = client or get_supabase_client()
        logger.info("SupabaseClient initialized")

    async def create_job_record(
        self, 
        job_id: str,
        status: str = "UPLOAD",
        metadata: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Create a new job record in the database.
        
        Args:
            job_id: Unique job identifier
            status: Initial job status
            metadata: Optional metadata dictionary
            
        Returns:
            Created job record
        """
        try:
            data = {
                "job_id": job_id,
                "status": status,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }
            
            response = self.client.table("jobs").insert(data).execute()
            logger.info(f"Created job record: {job_id}", extra={"job_id": job_id})
            return response.data[0] if response.data else data
            
        except Exception as e:
            logger.error(f"Failed to create job record: {e}", extra={"job_id": job_id})
            raise

    async def update_job_status(
        self,
        job_id: str,
        status: str,
        progress_message: Optional[str] = None,
        metadata_update: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Update job status and optionally progress message.
        
        Args:
            job_id: Job identifier
            status: New status
            progress_message: Optional progress message
            metadata_update: Optional metadata to merge with existing
            
        Returns:
            Updated job record
        """
        try:
            update_data: dict[str, Any] = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            if progress_message:
                update_data["progress_message"] = progress_message
                
            if metadata_update:
                # Get existing metadata and merge
                job = await self.get_job_by_id(job_id)
                existing_metadata = job.get("metadata", {})
                existing_metadata.update(metadata_update)
                update_data["metadata"] = existing_metadata
            
            response = (
                self.client.table("jobs")
                .update(update_data)
                .eq("job_id", job_id)
                .execute()
            )
            
            logger.info(
                f"Updated job status: {job_id} -> {status}",
                extra={"job_id": job_id, "status": status}
            )
            return response.data[0] if response.data else update_data
            
        except Exception as e:
            logger.error(
                f"Failed to update job status: {e}",
                extra={"job_id": job_id, "status": status}
            )
            raise

    async def get_job_by_id(self, job_id: str) -> dict[str, Any]:
        """
        Retrieve job record by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job record
        """
        try:
            response = (
                self.client.table("jobs")
                .select("*")
                .eq("job_id", job_id)
                .execute()
            )
            
            if not response.data:
                raise ValueError(f"Job not found: {job_id}")
                
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Failed to get job: {e}", extra={"job_id": job_id})
            raise

    async def upload_file(
        self,
        bucket: str,
        file_path: str,
        file_data: bytes,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Upload a file to Supabase storage.
        
        Args:
            bucket: Storage bucket name
            file_path: Path within the bucket
            file_data: File content as bytes
            content_type: MIME type of the file
            
        Returns:
            Public URL of the uploaded file
        """
        try:
            # Upload file
            self.client.storage.from_(bucket).upload(
                path=file_path,
                file=file_data,
                file_options={"content-type": content_type}
            )
            
            # Get public URL
            public_url = self.client.storage.from_(bucket).get_public_url(file_path)
            
            logger.info(
                f"Uploaded file to storage: {file_path}",
                extra={"bucket": bucket, "path": file_path}
            )
            return public_url
            
        except Exception as e:
            logger.error(
                f"Failed to upload file: {e}",
                extra={"bucket": bucket, "path": file_path}
            )
            raise

    async def download_file(self, bucket: str, file_path: str) -> bytes:
        """
        Download a file from Supabase storage.
        
        Args:
            bucket: Storage bucket name
            file_path: Path within the bucket
            
        Returns:
            File content as bytes
        """
        try:
            response = self.client.storage.from_(bucket).download(file_path)
            logger.info(
                f"Downloaded file from storage: {file_path}",
                extra={"bucket": bucket, "path": file_path}
            )
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to download file: {e}",
                extra={"bucket": bucket, "path": file_path}
            )
            raise

    async def store_inference_results(
        self,
        job_id: str,
        image_path: str,
        predictions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Store inference results in the database.
        
        Args:
            job_id: Job identifier
            image_path: Path to the image
            predictions: List of prediction dictionaries
            
        Returns:
            Created record
        """
        try:
            data = {
                "job_id": job_id,
                "image_path": image_path,
                "predictions": predictions,
                "created_at": datetime.utcnow().isoformat(),
            }
            
            response = self.client.table("inference_results").insert(data).execute()
            logger.info(
                f"Stored inference results for job: {job_id}",
                extra={"job_id": job_id, "image": image_path}
            )
            return response.data[0] if response.data else data
            
        except Exception as e:
            logger.error(
                f"Failed to store inference results: {e}",
                extra={"job_id": job_id}
            )
            raise

    # ============================================
    # Project Management Methods
    # ============================================

    async def create_project(self, project_data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new project record.
        
        Args:
            project_data: Project data dictionary
            
        Returns:
            Created project record
        """
        try:
            response = self.client.table("projects").insert(project_data).execute()
            logger.info(
                f"Created project: {project_data.get('project_id')}",
                extra={"project_id": project_data.get("project_id")}
            )
            return response.data[0] if response.data else project_data
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise

    async def get_project_by_id(self, project_id: str) -> dict[str, Any]:
        """
        Retrieve project by ID.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Project record
            
        Raises:
            ValueError: If project not found
        """
        try:
            response = (
                self.client.table("projects")
                .select("*")
                .eq("project_id", project_id)
                .execute()
            )
            
            if not response.data:
                raise ValueError(f"Project not found: {project_id}")
                
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Failed to get project: {e}", extra={"project_id": project_id})
            raise

    async def list_projects(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> dict[str, Any]:
        """
        List projects with pagination and filtering.
        
        Args:
            page: Page number (1-indexed)
            page_size: Items per page
            status_filter: Optional status filter
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)
            
        Returns:
            Dictionary with 'projects' list and 'total' count
        """
        try:
            # Build query
            query = self.client.table("projects").select("*", count="exact")
            
            # Apply status filter if provided
            if status_filter:
                query = query.eq("status", status_filter)
            
            # Apply sorting
            ascending = sort_order.lower() == "asc"
            query = query.order(sort_by, desc=not ascending)
            
            # Apply pagination
            start = (page - 1) * page_size
            end = start + page_size - 1
            query = query.range(start, end)
            
            # Execute query
            response = query.execute()
            
            return {
                "projects": response.data,
                "total": response.count if hasattr(response, 'count') else len(response.data)
            }
            
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            raise

    async def update_project(
        self,
        project_id: str,
        update_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update project record.
        
        Args:
            project_id: Project identifier
            update_data: Fields to update
            
        Returns:
            Updated project record
            
        Raises:
            ValueError: If project not found
        """
        try:
            response = (
                self.client.table("projects")
                .update(update_data)
                .eq("project_id", project_id)
                .execute()
            )
            
            if not response.data:
                raise ValueError(f"Project not found: {project_id}")
            
            logger.info(
                f"Updated project: {project_id}",
                extra={"project_id": project_id}
            )
            return response.data[0]
            
        except Exception as e:
            logger.error(
                f"Failed to update project: {e}",
                extra={"project_id": project_id}
            )
            raise

    async def delete_project(self, project_id: str) -> None:
        """
        Delete project record.
        
        Args:
            project_id: Project identifier
            
        Raises:
            ValueError: If project not found
        """
        try:
            # First check if project exists
            await self.get_project_by_id(project_id)
            
            # Delete project
            response = (
                self.client.table("projects")
                .delete()
                .eq("project_id", project_id)
                .execute()
            )
            
            logger.info(
                f"Deleted project: {project_id}",
                extra={"project_id": project_id}
            )
            
        except Exception as e:
            logger.error(
                f"Failed to delete project: {e}",
                extra={"project_id": project_id}
            )
            raise

    async def get_project_stats(self) -> dict[str, Any]:
        """
        Get aggregate statistics for all projects.
        
        Returns:
            Dictionary with project statistics
        """
        try:
            # Get all projects
            response = self.client.table("projects").select("*").execute()
            projects = response.data
            
            total_projects = len(projects)
            active_projects = sum(
                1 for p in projects 
                if p.get("status") in ["training", "labeling"]
            )
            completed_projects = sum(
                1 for p in projects 
                if p.get("status") == "completed"
            )
            total_images = sum(p.get("image_count", 0) for p in projects)
            
            # Calculate average accuracy (only for projects with accuracy)
            accuracies = [
                p.get("accuracy") for p in projects 
                if p.get("accuracy") is not None
            ]
            average_accuracy = (
                sum(accuracies) / len(accuracies) 
                if accuracies else None
            )
            
            return {
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": completed_projects,
                "total_images": total_images,
                "average_accuracy": average_accuracy
            }
            
        except Exception as e:
            logger.error(f"Failed to get project stats: {e}")
            raise


