-- ============================================
-- Projects Table Migration
-- ============================================
-- Purpose: Store project metadata for EvoLabeler MLOps workflows
-- Version: 002
-- Created: 2025-12-04

-- ============================================
-- 1. Create projects table
-- ============================================

CREATE TABLE IF NOT EXISTS public.projects (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Project Basic Info
    project_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    
    -- Project Status
    status TEXT NOT NULL CHECK (status IN (
        'idle',        -- Project created but not started
        'training',    -- Model training in progress
        'labeling',    -- Active learning / labeling in progress
        'completed'    -- Project completed successfully
    )) DEFAULT 'idle',
    
    -- Project Metrics
    image_count INTEGER DEFAULT 0 CHECK (image_count >= 0),
    accuracy NUMERIC(5, 2) CHECK (accuracy >= 0 AND accuracy <= 100),
    
    -- Visual Assets
    thumbnail_url TEXT,  -- Project cover image URL
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 2. Create indexes for performance
-- ============================================

-- Primary query index
CREATE INDEX IF NOT EXISTS idx_projects_project_id 
    ON public.projects(project_id);

-- Status filtering index
CREATE INDEX IF NOT EXISTS idx_projects_status 
    ON public.projects(status);

-- Time series index (most recent first)
CREATE INDEX IF NOT EXISTS idx_projects_created_at 
    ON public.projects(created_at DESC);

-- Updated time index (for sorting by last update)
CREATE INDEX IF NOT EXISTS idx_projects_updated_at 
    ON public.projects(updated_at DESC);

-- ============================================
-- 3. Create trigger for auto-updating updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_projects_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_projects_updated_at
    BEFORE UPDATE ON public.projects
    FOR EACH ROW
    EXECUTE FUNCTION update_projects_updated_at();

-- ============================================
-- 4. Enable Row Level Security (optional)
-- ============================================

-- Uncomment if you want to enable RLS
-- ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

-- Example policy: Allow all authenticated users to read
-- CREATE POLICY "Allow authenticated users to read projects"
--     ON public.projects FOR SELECT
--     TO authenticated
--     USING (true);

-- Example policy: Allow service role full access
-- CREATE POLICY "Allow service role full access to projects"
--     ON public.projects
--     TO service_role
--     USING (true)
--     WITH CHECK (true);

-- ============================================
-- 5. Create project_jobs relationship table (optional)
-- ============================================

-- This table links projects with jobs for tracking purposes
CREATE TABLE IF NOT EXISTS public.project_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id TEXT NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    job_id TEXT NOT NULL REFERENCES public.jobs(job_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, job_id)
);

CREATE INDEX IF NOT EXISTS idx_project_jobs_project_id 
    ON public.project_jobs(project_id);
    
CREATE INDEX IF NOT EXISTS idx_project_jobs_job_id 
    ON public.project_jobs(job_id);

-- ============================================
-- Comments for documentation
-- ============================================

COMMENT ON TABLE public.projects IS 
    'Stores metadata and status for EvoLabeler projects';

COMMENT ON COLUMN public.projects.project_id IS 
    'Human-readable unique project identifier';

COMMENT ON COLUMN public.projects.thumbnail_url IS 
    'URL to project cover image (stored in Supabase storage)';

COMMENT ON COLUMN public.projects.metadata IS 
    'Flexible JSONB field for storing additional project configuration and statistics';

COMMENT ON TABLE public.project_jobs IS 
    'Links projects with their associated jobs for tracking workflow progress';





