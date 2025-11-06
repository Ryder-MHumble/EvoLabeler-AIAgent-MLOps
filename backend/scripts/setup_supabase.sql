-- Supabase Database Setup Script
-- Run this script in your Supabase SQL editor to create the required tables and storage

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL CHECK (status IN (
        'UPLOAD', 'INFERENCE', 'ANALYSIS', 'ACQUISITION', 
        'PSEUDO_LABELING', 'TRAINING', 'COMPLETE', 'FAILED'
    )),
    progress_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for jobs table
CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);

-- Create inference_results table
CREATE TABLE IF NOT EXISTS inference_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id TEXT NOT NULL,
    image_path TEXT NOT NULL,
    predictions JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for inference_results
CREATE INDEX IF NOT EXISTS idx_inference_results_job_id ON inference_results(job_id);

-- Add foreign key constraint (optional, for referential integrity)
-- ALTER TABLE inference_results 
-- ADD CONSTRAINT fk_inference_results_job 
-- FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE;

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic timestamp update
DROP TRIGGER IF EXISTS update_jobs_updated_at ON jobs;
CREATE TRIGGER update_jobs_updated_at
    BEFORE UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Storage Buckets
-- Note: These need to be created via Supabase Dashboard or API
-- The following is reference SQL for documentation purposes

/*
-- Create images bucket (for uploaded and crawled images)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'images',
    'images',
    true,
    10485760,  -- 10MB
    ARRAY['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/tiff']
);

-- Create models bucket (for trained model weights)
INSERT INTO storage.buckets (id, name, public, file_size_limit)
VALUES (
    'models',
    'models',
    false,
    524288000  -- 500MB
);
*/

-- Grant necessary permissions
-- Adjust these based on your security requirements

-- Public read access to jobs status (adjust as needed)
-- ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

-- Example RLS policy (customize for your needs)
/*
CREATE POLICY "Allow public to read job status"
    ON jobs FOR SELECT
    USING (true);

CREATE POLICY "Allow authenticated users to insert jobs"
    ON jobs FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to update jobs"
    ON jobs FOR UPDATE
    USING (auth.role() = 'authenticated');
*/

-- Success message
SELECT 'Database setup completed successfully!' AS status;

