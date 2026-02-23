-- ============================================
-- EvoLoop Rounds Table Migration
-- ============================================
-- Purpose: Records each iteration round of the self-improvement loop with decision logs
-- Version: 006
-- Created: 2026-02-22

-- ============================================
-- 1. Create evo_rounds table
-- ============================================

CREATE TABLE IF NOT EXISTS public.evo_rounds (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys / References
    project_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    round_number INTEGER NOT NULL,

    -- Round input state
    input_image_count INTEGER,
    input_model_version_id UUID,

    -- Round output state
    acquired_image_count INTEGER DEFAULT 0,
    pseudo_label_count INTEGER DEFAULT 0,
    accepted_label_count INTEGER DEFAULT 0,
    avg_quality_score NUMERIC(6,4),

    -- Decision log
    should_continue BOOLEAN,
    continue_reason TEXT,

    -- Metrics delta (before/after comparison)
    metrics_before JSONB DEFAULT '{}',
    metrics_after JSONB DEFAULT '{}',
    metrics_delta JSONB DEFAULT '{}',

    -- Data quality gate results
    data_quality_gate_passed BOOLEAN,
    data_quality_gate_details JSONB DEFAULT '{}',

    -- Anti-degradation results
    model_health_report JSONB DEFAULT '{}',
    was_rolled_back BOOLEAN DEFAULT FALSE,

    -- Status
    status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'rolled_back', 'skipped')),

    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================
-- 2. Create indexes for performance
-- ============================================

-- Project lookup index
CREATE INDEX IF NOT EXISTS idx_evo_rounds_project
    ON public.evo_rounds(project_id);

-- Job lookup index
CREATE INDEX IF NOT EXISTS idx_evo_rounds_job
    ON public.evo_rounds(job_id);

-- Composite index for project + round queries
CREATE INDEX IF NOT EXISTS idx_evo_rounds_project_round
    ON public.evo_rounds(project_id, round_number);

-- Time series index (most recent first)
CREATE INDEX IF NOT EXISTS idx_evo_rounds_started
    ON public.evo_rounds(started_at DESC);

-- ============================================
-- 3. Enable Row Level Security (optional)
-- ============================================

-- Uncomment if you want to enable RLS
-- ALTER TABLE public.evo_rounds ENABLE ROW LEVEL SECURITY;

-- Example policy: Allow all authenticated users to read
-- CREATE POLICY "Allow authenticated users to read evo_rounds"
--     ON public.evo_rounds FOR SELECT
--     TO authenticated
--     USING (true);

-- Example policy: Allow service role full access
-- CREATE POLICY "Allow service role full access to evo_rounds"
--     ON public.evo_rounds
--     TO service_role
--     USING (true)
--     WITH CHECK (true);

-- ============================================
-- 4. Comments for documentation
-- ============================================

COMMENT ON TABLE public.evo_rounds IS
    'Records each EvoLoop iteration round with decision logs and anti-degradation results';

COMMENT ON COLUMN public.evo_rounds.metrics_delta IS
    'Difference between metrics_after and metrics_before for quick comparison';

COMMENT ON COLUMN public.evo_rounds.was_rolled_back IS
    'Whether the model was rolled back due to degradation in this round';
