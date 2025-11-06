# Setup Guide

## Prerequisites

- Python 3.13+
- Poetry (recommended) or pip
- Supabase account and project
- 硅基流动 (SiliconFlow) API key
- YOLO project setup (for training)

## Installation Steps

### 1. Clone the Repository

```bash
cd EvoLabeler-Backend
```

### 2. Install Dependencies

Using Poetry (recommended):

```bash
poetry install
```

Or using pip:

```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers

```bash
poetry run playwright install
# Or without poetry:
# playwright install
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your configuration:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# Qwen API Configuration
QWEN_API_KEY=your-qwen-api-key
QWEN_API_BASE_URL=https://api.siliconflow.cn/v1

# Remote YOLO Project
REMOTE_YOLO_PROJECT_PATH=/path/to/yolo/project
```

### 5. Setup Supabase Database

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run the setup script from `scripts/setup_supabase.sql`

Alternatively, create the tables manually:

```sql
-- See scripts/setup_supabase.sql for complete schema
```

### 6. Create Storage Buckets

In Supabase Dashboard:

1. Go to Storage
2. Create bucket `images` (public, 10MB limit)
3. Create bucket `models` (private, 500MB limit)

### 7. Setup YOLO Project

Ensure your YOLO project has the following structure:

```
/path/to/yolo/project/
├── train.py
├── predict.py
└── ... (other YOLO files)
```

## Running the Application

### Development Mode

```bash
poetry run python run.py
```

Or:

```bash
poetry run uvicorn app.main:app --reload
```

### Production Mode

```bash
# Set DEBUG=false in .env
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Verification

### 1. Check Health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "app": "EvoLabeler-Backend",
  "version": "0.1.0"
}
```

### 2. Access API Documentation

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Test Job Creation

```bash
# Create a test ZIP file with some images
zip test_images.zip image1.jpg image2.jpg

# Upload via API
curl -X POST "http://localhost:8000/api/v1/jobs/" \
  -F "file=@test_images.zip"
```

## Troubleshooting

### Import Errors

If you see import errors, ensure you're running from the project root:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Supabase Connection Errors

- Verify your `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check if your Supabase project is active
- Ensure the tables are created correctly

### Playwright Errors

If browser downloads fail:

```bash
poetry run playwright install --with-deps
```

### YOLO Script Errors

- Verify `REMOTE_YOLO_PROJECT_PATH` points to correct directory
- Ensure `train.py` and `predict.py` exist
- Check Python environment has required YOLO dependencies

## Configuration Options

See `.env.example` for all available configuration options:

- File upload limits
- Job timeout settings
- Pseudo-label confidence thresholds
- Model configurations
- Logging levels

## Development Tips

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black app/
poetry run ruff check app/
```

### Type Checking

```bash
poetry run mypy app/
```

## Next Steps

- Review API documentation in `docs/API.md`
- Understand the Multi-Agent architecture in `docs/ARCHITECTURE.md`
- Customize agent behavior for your use case

