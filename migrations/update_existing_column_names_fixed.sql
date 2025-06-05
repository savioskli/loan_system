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

-- Create an index for faster lookups (using DROP IF EXISTS for compatibility)
-- First check if the index already exists
SELECT COUNT(*) INTO @index_exists 
FROM information_schema.statistics 
WHERE table_schema = DATABASE() 
AND table_name = 'form_fields' 
AND index_name = 'idx_form_fields_column_name';

-- Create the index only if it doesn't exist
SET @create_index = CONCAT(
    "CREATE INDEX idx_form_fields_column_name ON form_fields(column_name)"
);

SET @drop_index = CONCAT(
    "DROP INDEX idx_form_fields_column_name ON form_fields"
);

-- Execute the appropriate statement
SET @sql = IF(@index_exists > 0, 
    "SELECT 'Index already exists' AS message", 
    @create_index
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
