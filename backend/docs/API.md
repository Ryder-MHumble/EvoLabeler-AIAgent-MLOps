# API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### System Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "app": "EvoLabeler-Backend",
  "version": "0.1.0"
}
```

#### Root
```http
GET /
```

**Response:**
```json
{
  "app": "EvoLabeler-Backend",
  "version": "0.1.0",
  "description": "EvoLabeler-Backend: A Multi-Agent Driven MLOps Engine",
  "docs": "/docs"
}
```

### Project Endpoints

#### Create Project

Create a new EvoLabeler project with metadata.

```http
POST /api/v1/projects/
Content-Type: application/json
```

**Request Body:**
```json
{
  "project_id": "proj_wildlife_001",
  "name": "野生动物分类识别",
  "description": "野生动物物种识别的自动化标注项目",
  "thumbnail_url": "https://example.com/image.jpg",
  "metadata": {
    "model_type": "yolov5m",
    "classes": ["deer", "bear", "wolf"]
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "proj_wildlife_001",
  "name": "野生动物分类识别",
  "description": "野生动物物种识别的自动化标注项目",
  "status": "idle",
  "image_count": 0,
  "accuracy": null,
  "thumbnail_url": "https://example.com/image.jpg",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00.000Z",
  "updated_at": "2024-01-01T00:00:00.000Z"
}
```

**Status Codes:**
- `201`: Project created successfully
- `400`: Invalid request data
- `409`: Project ID already exists
- `500`: Internal server error

#### List Projects

Retrieve a paginated list of all projects with optional filtering.

```http
GET /api/v1/projects/?page=1&page_size=20&status_filter=training&sort_by=created_at&sort_order=desc
```

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 20, max: 100)
- `status_filter` (string, optional): Filter by status (idle|training|labeling|completed)
- `sort_by` (string, optional): Sort field (default: created_at)
- `sort_order` (string, optional): Sort order (asc|desc, default: desc)

**Response:**
```json
{
  "projects": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "project_id": "proj_wildlife_001",
      "name": "野生动物分类识别",
      "description": "野生动物物种识别的自动化标注项目",
      "status": "completed",
      "image_count": 1250,
      "accuracy": 94.5,
      "thumbnail_url": "https://example.com/image.jpg",
      "metadata": {},
      "created_at": "2024-01-01T00:00:00.000Z",
      "updated_at": "2024-01-01T00:05:00.000Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

#### Get Project Details

Retrieve detailed information about a specific project.

```http
GET /api/v1/projects/{project_id}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "proj_wildlife_001",
  "name": "野生动物分类识别",
  "description": "野生动物物种识别的自动化标注项目",
  "status": "completed",
  "image_count": 1250,
  "accuracy": 94.5,
  "thumbnail_url": "https://example.com/image.jpg",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00.000Z",
  "updated_at": "2024-01-01T00:05:00.000Z"
}
```

**Status Codes:**
- `200`: Success
- `404`: Project not found
- `500`: Internal server error

#### Update Project

Update an existing project's information.

```http
PUT /api/v1/projects/{project_id}
Content-Type: application/json
```

**Request Body** (all fields optional):
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "status": "training",
  "image_count": 1500,
  "accuracy": 95.2,
  "thumbnail_url": "https://example.com/new-image.jpg",
  "metadata": {
    "additional_info": "value"
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "proj_wildlife_001",
  "name": "Updated Project Name",
  "description": "Updated description",
  "status": "training",
  "image_count": 1500,
  "accuracy": 95.2,
  "thumbnail_url": "https://example.com/new-image.jpg",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00.000Z",
  "updated_at": "2024-01-01T00:10:00.000Z"
}
```

**Status Codes:**
- `200`: Success
- `400`: No fields to update
- `404`: Project not found
- `500`: Internal server error

#### Delete Project

Delete a project and all associated data.

```http
DELETE /api/v1/projects/{project_id}
```

**Response:**
- Status Code: `204 No Content`

**Status Codes:**
- `204`: Project deleted successfully
- `404`: Project not found
- `500`: Internal server error

#### Get Project Statistics

Get aggregate statistics across all projects.

```http
GET /api/v1/projects/stats/summary
```

**Response:**
```json
{
  "total_projects": 8,
  "active_projects": 3,
  "completed_projects": 3,
  "total_images": 43752,
  "average_accuracy": 91.875
}
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

### Job Endpoints

#### Create Job

Upload a ZIP file containing images and start the IDEATE workflow.

```http
POST /api/v1/jobs/
Content-Type: multipart/form-data
```

**Request:**
- `file`: ZIP file containing images (max 100MB by default)

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "UPLOAD",
  "created_at": "2024-01-01T00:00:00.000Z",
  "message": "Job created and workflow started"
}
```

**Status Codes:**
- `201`: Job created successfully
- `400`: Invalid file format or ZIP file
- `413`: File size exceeds limit
- `500`: Internal server error

#### Get Job Status

Retrieve the current status of a job.

```http
GET /api/v1/jobs/{job_id}/status
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "TRAINING",
  "progress_message": "Training model with acquired data",
  "created_at": "2024-01-01T00:00:00.000Z",
  "updated_at": "2024-01-01T00:05:00.000Z",
  "metadata": {
    "filename": "images.zip",
    "file_size_mb": 25.5,
    "upload_dir": "/tmp/uploads/550e8400..."
  }
}
```

**Status Codes:**
- `200`: Success
- `404`: Job not found
- `500`: Internal server error

## Job Status Flow

```
UPLOAD → INFERENCE → ANALYSIS → ACQUISITION → PSEUDO_LABELING → TRAINING → COMPLETE
```

Or in case of failure:
```
ANY_STATUS → FAILED
```

### Status Descriptions

- **UPLOAD**: Initial status when job is created
- **INFERENCE**: Running YOLO inference on uploaded images
- **ANALYSIS**: Analyzing images with VLM and generating search strategy
- **ACQUISITION**: Crawling web for similar images
- **PSEUDO_LABELING**: Generating pseudo labels for acquired images (integrated with ACQUISITION)
- **TRAINING**: Training YOLO model with combined dataset
- **COMPLETE**: Workflow completed successfully
- **FAILED**: Workflow failed at some stage

## Example Usage

### Using cURL

```bash
# Create a job
curl -X POST "http://localhost:8000/api/v1/jobs/" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@images.zip"

# Get job status
curl "http://localhost:8000/api/v1/jobs/{job_id}/status"
```

### Using Python

```python
import requests

# Create a job
with open("images.zip", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/jobs/",
        files={"file": f}
    )
    job_data = response.json()
    job_id = job_data["job_id"]

# Poll job status
import time

while True:
    response = requests.get(
        f"http://localhost:8000/api/v1/jobs/{job_id}/status"
    )
    status_data = response.json()
    
    print(f"Status: {status_data['status']}")
    print(f"Message: {status_data.get('progress_message', '')}")
    
    if status_data["status"] in ["COMPLETE", "FAILED"]:
        break
    
    time.sleep(5)
```

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "details": {} // Optional, only in debug mode
}
```

## Interactive API Documentation

When running in debug mode, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

