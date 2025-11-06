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

