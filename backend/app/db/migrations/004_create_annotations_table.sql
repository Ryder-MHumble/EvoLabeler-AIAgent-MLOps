-- ============================================
-- Annotations Table Migration
-- ============================================
-- Purpose: Store annotation data (bounding boxes) for images in EvoLabeler
-- Version: 004
-- Created: 2025-12-04

-- ============================================
-- 1. Create annotations table
-- ============================================

CREATE TABLE IF NOT EXISTS public.annotations (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    project_id TEXT NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,

    -- Image Reference
    image_id TEXT NOT NULL,

    -- User Reference (optional for multi-user tracking)
    user_id TEXT,

    -- Annotation Data
    bboxes JSONB NOT NULL,  -- Array of bounding boxes with labels

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 2. Create indexes for performance
-- ============================================

-- Project lookup index
CREATE INDEX IF NOT EXISTS idx_annotations_project_id
    ON public.annotations(project_id);

-- Image lookup index
CREATE INDEX IF NOT EXISTS idx_annotations_image_id
    ON public.annotations(image_id);

-- Composite index for project + image queries
CREATE INDEX IF NOT EXISTS idx_annotations_project_image
    ON public.annotations(project_id, image_id);

-- Time series index (most recent first)
CREATE INDEX IF NOT EXISTS idx_annotations_created_at
    ON public.annotations(created_at DESC);

-- ============================================
-- 3. Create trigger for auto-updating updated_at
-- ============================================

-- Reuse the existing function or create if not exists
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_annotations_updated_at
    BEFORE UPDATE ON public.annotations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 4. Enable Row Level Security (optional)
-- ============================================

-- Uncomment if you want to enable RLS
-- ALTER TABLE public.annotations ENABLE ROW LEVEL SECURITY;

-- Example policy: Allow all authenticated users to read
-- CREATE POLICY "Allow authenticated users to read annotations"
--     ON public.annotations FOR SELECT
--     TO authenticated
--     USING (true);

-- Example policy: Allow service role full access
-- CREATE POLICY "Allow service role full access to annotations"
--     ON public.annotations
--     TO service_role
--     USING (true)
--     WITH CHECK (true);

-- ============================================
-- Comments for documentation
-- ============================================

COMMENT ON TABLE public.annotations IS
    'Stores bounding box annotations for images in EvoLabeler projects';

COMMENT ON COLUMN public.annotations.project_id IS
    'Reference to parent project';

COMMENT ON COLUMN public.annotations.image_id IS
    'Identifier of the annotated image';

COMMENT ON COLUMN public.annotations.bboxes IS
    'JSONB array of bounding boxes with labels, coordinates, and confidence scores';

COMMENT ON COLUMN public.annotations.metadata IS
    'Flexible JSONB field for storing additional annotation metadata';
