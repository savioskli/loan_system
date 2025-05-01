-- Add status column to case_history table
ALTER TABLE case_history
ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'Active';

-- Add check constraint to ensure valid status values
ALTER TABLE case_history
ADD CONSTRAINT valid_status CHECK (status IN ('Active', 'Pending', 'Closed'));
