"""
Database models for reference.

Since we're using Supabase, these are reference models showing
the expected database schema. The actual tables should be created
in Supabase directly.
"""

from typing import Any, Optional
from datetime import datetime


# Reference: Job table schema in Supabase
"""
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    progress_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_jobs_job_id ON jobs(job_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
"""


# Reference: Inference results table schema
"""
CREATE TABLE inference_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id TEXT NOT NULL,
    image_path TEXT NOT NULL,
    predictions JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

CREATE INDEX idx_inference_results_job_id ON inference_results(job_id);
"""


# Reference: Storage buckets
"""
-- Images bucket for storing uploaded and crawled images
CREATE BUCKET IF NOT EXISTS images WITH (
    public = true,
    file_size_limit = 10485760  -- 10MB
);

-- Models bucket for storing trained models
CREATE BUCKET IF NOT EXISTS models WITH (
    public = false,
    file_size_limit = 524288000  -- 500MB
);
"""


class JobStatus:
    """Job status constants."""
    
    UPLOAD = "UPLOAD"
    INFERENCE = "INFERENCE"
    ANALYSIS = "ANALYSIS"
    ACQUISITION = "ACQUISITION"
    PSEUDO_LABELING = "PSEUDO_LABELING"
    TRAINING = "TRAINING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    
    @classmethod
    def all_statuses(cls) -> list[str]:
        """Get all valid statuses."""
        return [
            cls.UPLOAD,
            cls.INFERENCE,
            cls.ANALYSIS,
            cls.ACQUISITION,
            cls.PSEUDO_LABELING,
            cls.TRAINING,
            cls.COMPLETE,
            cls.FAILED,
        ]

