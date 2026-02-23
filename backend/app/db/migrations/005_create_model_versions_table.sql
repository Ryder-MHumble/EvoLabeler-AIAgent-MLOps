-- ============================================
-- Model Versions Table Migration
-- ============================================
-- Purpose: Tracks every trained model checkpoint with metrics for anti-degradation comparison
-- Version: 005
-- Created: 2026-02-22

-- ============================================
-- 1. Create model_versions table
-- ============================================

CREATE TABLE IF NOT EXISTS public.model_versions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys / References
    project_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    round_number INTEGER NOT NULL DEFAULT 1,

    -- Model artifact
    model_path TEXT NOT NULL,
    model_size_bytes BIGINT,

    -- Performance metrics (core of anti-degradation)
    metrics JSONB NOT NULL DEFAULT '{}',
    -- Expected structure:
    -- {
    --   "mAP50": float,
    --   "mAP50_95": float,
    --   "precision": float,
    --   "recall": float,
    --   "val_loss": float,
    --   "train_loss": float,
    --   "per_class": { "class_name": {"ap": float, "precision": float, "recall": float} }
    -- }

    -- Validation set tracking (ensures consistency across rounds)
    validation_set_hash TEXT,
    validation_set_size INTEGER,

    -- Confidence calibration metrics
    calibration_ece NUMERIC(6,4),  -- Expected Calibration Error
    calibration_mce NUMERIC(6,4),  -- Maximum Calibration Error

    -- Status flags
    is_best BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,

    -- Training metadata
    training_config JSONB DEFAULT '{}',
    training_duration_seconds INTEGER,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 2. Create indexes for performance
-- ============================================

-- Project lookup index
CREATE INDEX IF NOT EXISTS idx_model_versions_project
    ON public.model_versions(project_id);

-- Job lookup index
CREATE INDEX IF NOT EXISTS idx_model_versions_job
    ON public.model_versions(job_id);

-- Best model partial index (for quick best-model lookup)
CREATE INDEX IF NOT EXISTS idx_model_versions_best
    ON public.model_versions(project_id, is_best)
    WHERE is_best = TRUE;

-- Active model partial index (for quick active-model lookup)
CREATE INDEX IF NOT EXISTS idx_model_versions_active
    ON public.model_versions(project_id, is_active)
    WHERE is_active = TRUE;

-- Time series index (most recent first)
CREATE INDEX IF NOT EXISTS idx_model_versions_created
    ON public.model_versions(created_at DESC);

-- ============================================
-- 3. Enable Row Level Security (optional)
-- ============================================

-- Uncomment if you want to enable RLS
-- ALTER TABLE public.model_versions ENABLE ROW LEVEL SECURITY;

-- Example policy: Allow all authenticated users to read
-- CREATE POLICY "Allow authenticated users to read model_versions"
--     ON public.model_versions FOR SELECT
--     TO authenticated
--     USING (true);

-- Example policy: Allow service role full access
-- CREATE POLICY "Allow service role full access to model_versions"
--     ON public.model_versions
--     TO service_role
--     USING (true)
--     WITH CHECK (true);

-- ============================================
-- 4. Comments for documentation
-- ============================================

COMMENT ON TABLE public.model_versions IS
    'Tracks model checkpoints with performance metrics for anti-degradation comparison';

COMMENT ON COLUMN public.model_versions.metrics IS
    'JSONB storing mAP50, mAP50_95, precision, recall, val_loss, train_loss, per_class metrics';

COMMENT ON COLUMN public.model_versions.validation_set_hash IS
    'SHA256 hash of validation image list to ensure consistency across rounds';

COMMENT ON COLUMN public.model_versions.calibration_ece IS
    'Expected Calibration Error - measures model confidence calibration quality';
