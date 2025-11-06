# Architecture Documentation

## System Overview

EvoLabeler-Backend is a Multi-Agent driven MLOps engine implementing the **IDEATE (Iterative Data Engine via Agentic Task Execution)** framework for remote sensing image object detection.

## Core Concepts

### IDEATE Framework

The system embodies three key principles:

1. **Modular Design**: Each component (Agent, Tool) has a single, well-defined responsibility
2. **Automated Workflow**: End-to-end automation from data upload to model training
3. **Intelligent Adaptation**: LLM-driven decision making for data acquisition

### Academic Foundations

- **Multi-Agent Architecture**: Orchestrator + Role-Playing Agents
- **LLM in Agentic Systems**: AnalysisAgent as strategy planner
- **Active Learning**: InferenceAgent's uncertainty evaluation
- **Semi-Supervised Learning**: High-quality pseudo-labeling
- **Learning with Noisy Labels**: Quality control mechanisms (extensible)

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
│  FastAPI Endpoints │ Pydantic Schemas │ Request Validation  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                            │
│              JobOrchestrator (Workflow Manager)              │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Agent Layer                              │
│  InferenceAgent │ AnalysisAgent │ AcquisitionAgent │        │
│  TrainingAgent                                               │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Tool Layer                              │
│  SupabaseClient │ QwenAPIWrapper │ WebCrawler │             │
│  SubprocessExecutor                                          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  External Services                           │
│  Supabase │ 硅基流动 API │ Web Sources │ YOLO Scripts       │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Layer

**Location**: `app/api/v1/`

**Responsibility**: Handle HTTP requests and responses

**Components**:
- `endpoints/jobs.py`: REST API endpoints
- `schemas/job.py`: Request/response models

**Key Features**:
- RESTful design
- Request validation via Pydantic
- Background task execution
- Error handling

### 2. Service Layer

**Location**: `app/services/`

**Responsibility**: Business logic and workflow orchestration

**Components**:
- `orchestrator.py`: JobOrchestrator class

**Key Features**:
- Sequential workflow execution
- Context passing between agents
- Status management
- Error recovery

### 3. Agent Layer

**Location**: `app/agents/`

**Responsibility**: Execute specific tasks in the workflow

**Agents**:

#### InferenceAgent
- Runs YOLO inference on uploaded images
- Evaluates prediction uncertainty
- Implements active learning signals

#### AnalysisAgent
- Uses VLM to analyze images
- Generates semantic descriptions
- Creates search strategies via LLM
- Acts as "strategy planner"

#### AcquisitionAgent
- Crawls web for similar images
- Runs pseudo-labeling on acquired data
- Filters high-quality labels
- Implements semi-supervised learning

#### TrainingAgent
- Prepares training dataset
- Generates YOLO configuration
- Triggers remote training
- Monitors training progress

**Design Pattern**: Dependency Injection
- Each agent receives required tools via constructor
- Promotes testability and loose coupling

### 4. Tool Layer

**Location**: `app/tools/`

**Responsibility**: Interact with external services

**Tools**:

#### SupabaseClient
- Database operations (CRUD)
- File storage (upload/download)
- Singleton pattern for connection management

#### QwenAPIWrapper
- Vision-Language Model (VLM) API
- Text generation API
- Async HTTP client

#### WebCrawler
- Playwright-based browser automation
- Image search and download
- Rate limiting and error handling

#### SubprocessExecutor
- External script execution
- YOLO training/prediction
- Process management and monitoring

### 5. Core Layer

**Location**: `app/core/`

**Responsibility**: Configuration and utilities

**Components**:
- `config.py`: Pydantic Settings management
- `logging_config.py`: Structured logging

## Workflow Execution

### Stage-by-Stage Flow

```
1. UPLOAD
   ├─ User uploads ZIP file
   ├─ File extraction and validation
   └─ Job record creation

2. INFERENCE (InferenceAgent)
   ├─ Run YOLO on uploaded images
   ├─ Parse predictions
   └─ Calculate uncertainty metrics

3. ANALYSIS (AnalysisAgent)
   ├─ Analyze images with VLM
   ├─ Generate descriptions
   └─ Create search strategy with LLM

4. ACQUISITION (AcquisitionAgent)
   ├─ Crawl web for similar images
   ├─ Run pseudo-labeling
   └─ Filter high-quality labels

5. TRAINING (TrainingAgent)
   ├─ Prepare dataset (original + acquired)
   ├─ Generate data.yaml
   └─ Trigger YOLO training

6. COMPLETE
   └─ Workflow summary and cleanup
```

### Context Passing

The Orchestrator maintains a `context` dictionary that accumulates data as it flows through agents:

```python
context = {
    "job_id": "...",
    "uploaded_images": [...],      # From upload
    "predictions": [...],           # From InferenceAgent
    "uncertainty_metrics": {...},  # From InferenceAgent
    "image_descriptions": [...],   # From AnalysisAgent
    "search_queries": [...],        # From AnalysisAgent
    "acquired_images": [...],       # From AcquisitionAgent
    "pseudo_labels": [...],         # From AcquisitionAgent
    "training_result": {...},       # From TrainingAgent
}
```

## Design Patterns

### 1. Dependency Injection

Agents receive dependencies via constructor:

```python
inference_agent = InferenceAgent(
    subprocess_executor=executor,
    supabase_client=client
)
```

**Benefits**:
- Easy testing (mock dependencies)
- Loose coupling
- Clear dependencies

### 2. Singleton Pattern

Used for:
- Supabase client (connection pooling)
- Configuration (global settings)

### 3. Strategy Pattern

Each agent implements the `execute(context)` interface:

```python
class BaseAgent(ABC):
    @abstractmethod
    async def execute(self, context: dict) -> dict:
        pass
```

### 4. Template Method

Agents use inherited logging methods:
- `_log_execution_start()`
- `_log_execution_end()`
- `_log_error()`

## Data Flow

```
User Upload (ZIP)
    │
    ├─> Extract Images ──────────────────┐
    │                                     │
    └─> Store in /tmp/uploads/{job_id}   │
                                          │
    ┌─────────────────────────────────────┘
    │
    ├─> YOLO Inference ──> Predictions + Uncertainty
    │
    ├─> VLM Analysis ──> Descriptions
    │
    ├─> LLM Strategy ──> Search Queries
    │
    ├─> Web Crawling ──> New Images
    │
    ├─> Pseudo-Labeling ──> Labels for New Images
    │
    ├─> Dataset Preparation ──> YOLO Format
    │
    └─> YOLO Training ──> New Model
```

## Database Schema

### Jobs Table

```sql
jobs
├─ id (UUID, PK)
├─ job_id (TEXT, UNIQUE)
├─ status (TEXT)
├─ progress_message (TEXT)
├─ metadata (JSONB)
├─ created_at (TIMESTAMP)
└─ updated_at (TIMESTAMP)
```

### Inference Results Table

```sql
inference_results
├─ id (UUID, PK)
├─ job_id (TEXT, FK)
├─ image_path (TEXT)
├─ predictions (JSONB)
└─ created_at (TIMESTAMP)
```

### Storage Buckets

- `images`: Uploaded and crawled images (public)
- `models`: Trained model weights (private)

## Error Handling

### Error Propagation

```
Agent Error
    │
    └─> Log + Raise Exception
            │
            └─> Orchestrator Catches
                    │
                    ├─> Update Status to FAILED
                    ├─> Log Error Details
                    └─> Return Error Response
```

### Retry Strategy

Currently not implemented but can be added:
- Exponential backoff for API calls
- Retry failed crawls
- Resume from last successful stage

## Scalability Considerations

### Current Design

- Single-server deployment
- Background tasks via FastAPI
- Sequential workflow execution

### Future Enhancements

1. **Horizontal Scaling**
   - Distributed task queue (Celery, RQ)
   - Load balancer for API servers
   - Separate worker nodes for agents

2. **Workflow Parallelization**
   - Parallel image processing
   - Concurrent web crawling
   - Distributed training

3. **Caching**
   - Redis for job status
   - LLM response caching
   - Prediction result caching

## Security Considerations

### Current Implementation

- Environment variable configuration
- Input validation via Pydantic
- File type and size validation
- Private storage for models

### Recommended Additions

- API authentication (JWT tokens)
- Rate limiting
- Input sanitization for file paths
- Supabase Row Level Security (RLS)
- HTTPS in production
- Secrets management (HashiCorp Vault)

## Testing Strategy

### Unit Tests

Test individual components:
- Agent execute methods
- Tool operations
- Utility functions

### Integration Tests

Test component interactions:
- Orchestrator workflow
- API endpoints
- Database operations

### End-to-End Tests

Test complete workflows:
- Full job execution
- Error scenarios
- Edge cases

## Monitoring and Observability

### Logging

- Structured JSON logs in production
- Color-coded logs in development
- Log levels: DEBUG, INFO, WARNING, ERROR
- Context enrichment (job_id, agent, etc.)

### Metrics (Recommended)

- Job completion rate
- Workflow duration by stage
- API response times
- Error rates by component

### Tracing (Recommended)

- OpenTelemetry integration
- Distributed tracing across agents
- Performance profiling

## Deployment Architecture

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐  ┌────▼─────┐  ┌────▼─────┐
        │ FastAPI   │  │ FastAPI  │  │ FastAPI  │
        │ Instance 1│  │Instance 2│  │Instance 3│
        └─────┬─────┘  └────┬─────┘  └────┬─────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
        ┌─────▼─────┐                ┌─────▼──────┐
        │  Supabase │                │  External  │
        │  Database │                │  Services  │
        │  Storage  │                │  (LLM API) │
        └───────────┘                └────────────┘
```

