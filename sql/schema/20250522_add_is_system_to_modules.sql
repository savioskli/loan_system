BEGIN;

-- Add is_system column to modules table
ALTER TABLE modules 
ADD COLUMN is_system BOOLEAN NOT NULL DEFAULT FALSE;

-- Update existing Client Management and Loan Management modules to be system modules
UPDATE modules 
SET is_system = TRUE 
WHERE code IN ('CLT_MGT', 'LN_MGT');

COMMIT;
