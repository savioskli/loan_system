-- Update column_name for all existing form fields
-- This sets the column_name to the snake_case version of field_name
-- For example, "First Name" becomes "first_name"

-- First, make sure we have a backup of the current data
CREATE TABLE IF NOT EXISTS form_fields_backup LIKE form_fields;
INSERT INTO form_fields_backup SELECT * FROM form_fields;

-- Update all records where column_name is NULL or empty
UPDATE form_fields 
SET column_name = LOWER(REPLACE(field_name, ' ', '_'))
WHERE column_name IS NULL OR column_name = '';

-- Print a summary of the changes
SELECT 
    field_name, 
    field_label, 
    column_name,
    LOWER(REPLACE(field_name, ' ', '_')) AS expected_column_name
FROM form_fields
ORDER BY id;

-- Create an index for faster lookups if it doesn't exist
CREATE INDEX IF NOT EXISTS idx_form_fields_column_name ON form_fields(column_name);
