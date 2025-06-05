-- Update column_name for all existing form fields
-- This sets the column_name to the snake_case version of field_name
-- For example, "First Name" becomes "first_name"

-- Skip backup creation if it already exists
SELECT COUNT(*) INTO @backup_exists FROM information_schema.tables 
WHERE table_schema = DATABASE() AND table_name = 'form_fields_backup';

SET @create_backup = IF(@backup_exists > 0, 
    "SELECT 'Backup table already exists' AS message", 
    "CREATE TABLE form_fields_backup LIKE form_fields; INSERT INTO form_fields_backup SELECT * FROM form_fields;"
);

PREPARE stmt FROM @create_backup;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Update all records where column_name is NULL or empty
UPDATE form_fields 
SET column_name = LOWER(REPLACE(field_name, ' ', '_'))
WHERE column_name IS NULL OR column_name = '';

-- Print a summary of the changes
SELECT 
    id,
    field_name, 
    field_label, 
    column_name,
    LOWER(REPLACE(field_name, ' ', '_')) AS expected_column_name
FROM form_fields
ORDER BY id;

-- Check if the index already exists
SELECT COUNT(*) INTO @index_exists 
FROM information_schema.statistics 
WHERE table_schema = DATABASE() 
AND table_name = 'form_fields' 
AND index_name = 'idx_form_fields_column_name';

-- Create the index only if it doesn't exist
SET @sql = IF(@index_exists > 0, 
    "SELECT 'Index already exists' AS message", 
    "CREATE INDEX idx_form_fields_column_name ON form_fields(column_name)"
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
