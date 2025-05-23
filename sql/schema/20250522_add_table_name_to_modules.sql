-- Add table_name column to modules table
BEGIN;

-- Add new column if it doesn't exist
SET @dbname = DATABASE();
SET @tablename = "modules";
SET @columnname = "table_name";
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*)
   FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname
     AND TABLE_NAME = @tablename
     AND COLUMN_NAME = @columnname) > 0,
  "SELECT 1",
  "ALTER TABLE modules ADD COLUMN table_name VARCHAR(100) DEFAULT NULL"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Create temporary table for the update
CREATE TEMPORARY TABLE module_tables AS
SELECT m.id, CONCAT(LOWER(REPLACE(REPLACE(m.name, ' ', '_'), '-', '_')), '_data') as table_name
FROM modules m
WHERE m.is_system = FALSE
AND EXISTS (
    SELECT 1
    FROM information_schema.tables t
    WHERE t.table_name = CONCAT(LOWER(REPLACE(REPLACE(m.name, ' ', '_'), '-', '_')), '_data')
    AND t.table_schema = DATABASE()
);

-- Update modules using the temporary table
UPDATE modules m
INNER JOIN module_tables mt ON m.id = mt.id
SET m.table_name = mt.table_name;

-- Drop temporary table
DROP TEMPORARY TABLE module_tables;

COMMIT;

-- Rollback in case of failure
-- BEGIN;
-- ALTER TABLE modules DROP COLUMN table_name;
-- COMMIT;
