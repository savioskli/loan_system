-- Add column_name field to form_fields table
ALTER TABLE form_fields ADD COLUMN column_name VARCHAR(100) NULL COMMENT 'Database column name this field maps to';

-- Update existing records with inferred column names based on field_name
-- Convert field_name to snake_case for existing records
UPDATE form_fields 
SET column_name = LOWER(REPLACE(field_name, ' ', '_'))
WHERE column_name IS NULL;

-- Create an index for faster lookups
CREATE INDEX idx_form_fields_column_name ON form_fields(column_name);

-- Add a comment explaining the purpose of this field
ALTER TABLE form_fields 
MODIFY COLUMN column_name VARCHAR(100) NULL 
COMMENT 'Database column name this field maps to (used for dynamic form processing)';
